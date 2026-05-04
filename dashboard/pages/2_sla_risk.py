import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import pickle

import numpy as np
import pandas as pd
import streamlit as st

from dashboard.components.charts import sla_gauge
from src.data.feature_engineer import build_sla_features


st.set_page_config(page_title="SLA Risk Monitor", layout="wide")

DATA_PATH = Path("data/processed/tickets_clean.parquet")
DEMO_MODE = not DATA_PATH.exists()


def _synthetic_tickets(rows: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    categories = ["billing", "technical", "account", "shipping", "refund", "security"]
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "pending", "closed"]
    channels = ["email", "chat", "phone", "web"]
    created_at = pd.Timestamp.today().normalize() - pd.to_timedelta(
        rng.integers(0, 90, rows), unit="D"
    )
    priority = rng.choice(priorities, rows, p=[0.35, 0.40, 0.20, 0.05])
    status = rng.choice(statuses, rows, p=[0.25, 0.20, 0.55])
    resolution_hours = rng.gamma(shape=2.2, scale=8.0, size=rows).round(1)
    resolution_hours = np.where(status == "closed", resolution_hours, np.nan)
    sla_thresholds = {"critical": 4, "high": 8, "medium": 24, "low": 72}

    df = pd.DataFrame(
        {
            "ticket_id": [f"TKT-{i:05d}" for i in range(1, rows + 1)],
            "created_at": created_at,
            "category": rng.choice(categories, rows),
            "priority": priority,
            "status": status,
            "resolution_hours": resolution_hours,
            "channel": rng.choice(channels, rows),
            "customer_satisfaction": rng.uniform(2.8, 5.0, rows).round(1),
        }
    )
    df["text"] = (
        "Customer needs help with "
        + df["category"].astype(str)
        + " issue at "
        + df["priority"].astype(str)
        + " priority."
    )
    df["hour_created"] = rng.integers(0, 24, rows)
    df["day_of_week"] = pd.to_datetime(df["created_at"]).dt.dayofweek
    df["is_weekend"] = df["day_of_week"] >= 5
    df["sla_breached"] = [
        bool(hours > sla_thresholds[prio]) if not pd.isna(hours) else False
        for hours, prio in zip(df["resolution_hours"], df["priority"])
    ]
    return df


def _prepare_tickets(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    now = pd.Timestamp.now()
    if "ticket_id" not in data.columns:
        data["ticket_id"] = [f"TKT-{i:05d}" for i in range(1, len(data) + 1)]
    if "text" not in data.columns:
        data["text"] = ""
    if "hour_created" not in data.columns:
        data["hour_created"] = data["created_at"].dt.hour.fillna(9).astype(int)
    if "day_of_week" not in data.columns:
        data["day_of_week"] = data["created_at"].dt.dayofweek.fillna(1).astype(int)
    if "is_weekend" not in data.columns:
        data["is_weekend"] = data["day_of_week"] >= 5
    data["age_hours"] = ((now - data["created_at"]).dt.total_seconds() / 3600).fillna(0)
    return data


@st.cache_data
def load_tickets() -> pd.DataFrame:
    if DATA_PATH.exists():
        return _prepare_tickets(pd.read_parquet(DATA_PATH))
    return _prepare_tickets(_synthetic_tickets())


def _predict_open_ticket_risk(open_tickets: pd.DataFrame, threshold: float) -> pd.DataFrame:
    with open("models/sla_predictor.pkl", "rb") as f:
        artifacts = pickle.load(f)

    clf = artifacts["classifier"]
    feature_names = artifacts["feature_names"]
    features = build_sla_features(open_tickets)
    for column in feature_names:
        if column not in features.columns:
            features[column] = 0
    features = features[feature_names]

    probabilities = clf.predict_proba(features.values)[:, 1]
    risk = open_tickets[["ticket_id", "category", "priority", "age_hours"]].copy()
    risk["breach_probability"] = probabilities
    risk["risk_level"] = np.where(
        risk["breach_probability"] >= threshold,
        "high",
        np.where(risk["breach_probability"] >= 0.30, "medium", "low"),
    )
    return risk.sort_values("breach_probability", ascending=False)


def _risk_row_style(row):
    colors = {
        "low": "background-color: #dcfce7",
        "medium": "background-color: #fef3c7",
        "high": "background-color: #fee2e2",
    }
    return [colors.get(row["risk_level"], "")] * len(row)


df = load_tickets()
if DEMO_MODE or not DATA_PATH.exists():
    st.warning("Demo Mode: Showing synthetic data. Download datasets and run preprocessing to load real data.")

st.title("SLA Risk Monitor")
threshold = st.slider("Risk threshold", min_value=0.0, max_value=1.0, value=0.5)
breach_rate = float(df.get("sla_breached", pd.Series(dtype=float)).mean() or 0)
st.plotly_chart(sla_gauge(breach_rate), use_container_width=True)

model_path = Path("models/sla_predictor.pkl")
if model_path.exists():
    open_tickets = df[df.get("status", pd.Series(dtype=str)) != "closed"].copy()
    if open_tickets.empty:
        st.info("No open tickets to score.")
    else:
        try:
            risk_df = _predict_open_ticket_risk(open_tickets, threshold)
            styled = risk_df.style.apply(_risk_row_style, axis=1).format(
                {"age_hours": "{:.1f}", "breach_probability": "{:.1%}"}
            )
            st.dataframe(styled, use_container_width=True)
        except Exception as exc:
            st.error(f"Unable to score SLA risk: {exc}")
else:
    st.info("Train models first: python src/models/sla_predictor.py")

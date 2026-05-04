import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.charts import agent_load_heatmap


st.set_page_config(page_title="Auto-Routing", layout="wide")

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

    df = pd.DataFrame(
        {
            "ticket_id": [f"TKT-{i:05d}" for i in range(1, rows + 1)],
            "created_at": created_at,
            "category": rng.choice(categories, rows),
            "priority": rng.choice(priorities, rows, p=[0.35, 0.40, 0.20, 0.05]),
            "status": rng.choice(statuses, rows, p=[0.25, 0.20, 0.55]),
            "channel": rng.choice(channels, rows),
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
    df["agent_group"] = _derive_agent_group(df)
    return df


def _derive_agent_group(df: pd.DataFrame):
    return np.select(
        [
            df["priority"].eq("critical"),
            df["category"].isin(["technical", "security"]),
            df["category"].isin(["billing", "refund"]),
        ],
        ["escalation", "tier2", "billing"],
        default="tier1",
    )


def _prepare_tickets(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    if "hour_created" not in data.columns:
        data["hour_created"] = data["created_at"].dt.hour.fillna(9).astype(int)
    if "day_of_week" not in data.columns:
        data["day_of_week"] = data["created_at"].dt.dayofweek.fillna(1).astype(int)
    if "agent_group" not in data.columns:
        data["agent_group"] = _derive_agent_group(data)
    return data


@st.cache_data
def load_tickets() -> pd.DataFrame:
    if DATA_PATH.exists():
        return _prepare_tickets(pd.read_parquet(DATA_PATH))
    return _synthetic_tickets()


def _routing_distribution(df: pd.DataFrame):
    counts = (
        df["agent_group"]
        .value_counts()
        .rename_axis("agent_group")
        .reset_index(name="ticket_count")
    )
    return px.bar(
        counts,
        x="agent_group",
        y="ticket_count",
        title="Routing Distribution",
    )


def demo_route(text: str, priority: str) -> dict:
    text_lower = text.lower()
    if any(
        word in text_lower
        for word in ["payment", "billing", "charge", "invoice", "refund", "subscription"]
    ):
        category, group = "billing", "Billing Team"
    elif any(
        word in text_lower
        for word in [
            "crash",
            "error",
            "bug",
            "broken",
            "not working",
            "down",
            "outage",
            "login",
            "password",
            "access",
        ]
    ):
        category, group = "technical", "Tier 2 — Technical"
    elif any(
        word in text_lower
        for word in ["ship", "deliver", "tracking", "order", "package", "return"]
    ):
        category, group = "shipping", "Fulfillment Team"
    elif priority == "critical":
        category, group = "general", "Escalation Queue"
    else:
        category, group = "general", "Tier 1 — General Support"

    sla_risk = {"critical": 0.88, "high": 0.62, "medium": 0.31, "low": 0.12}[priority]
    return {
        "agent_group": group,
        "category": category,
        "breach_probability": sla_risk,
        "risk_level": "high" if sla_risk > 0.6 else "medium" if sla_risk > 0.3 else "low",
    }


def _show_recommendation(result: dict):
    group = result["agent_group"]
    if group == "Escalation Queue":
        st.error(f"ESCALATE: {group}")
    elif group.startswith("Tier 2"):
        st.warning(f"Route to: {group}")
    else:
        st.success(f"Route to: {group}")

    metric_cols = st.columns(3)
    metric_cols[0].metric("Predicted Category", result["category"].title())
    metric_cols[1].metric("SLA Risk %", f"{result['breach_probability']:.0%}")
    metric_cols[2].metric("Risk Level", result["risk_level"].title())


df = load_tickets()
if DEMO_MODE or not DATA_PATH.exists():
    st.warning("Demo Mode: Showing synthetic data. Download datasets and run preprocessing to load real data.")

st.title("Auto-Routing")
left, right = st.columns(2)

with left:
    st.plotly_chart(_routing_distribution(df), use_container_width=True)

with right:
    st.subheader("Try Routing")
    with st.form("routing_form"):
        ticket_text = st.text_area(
            "Ticket text",
            value=(
                "My payment was charged twice this month and I still have not "
                "received a refund. This is urgent."
            ),
        )
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"], index=2)
        submitted = st.form_submit_button("Get Routing Recommendation")

    if submitted or ticket_text.strip():
        recommendation = demo_route(ticket_text, priority=priority)
        _show_recommendation(recommendation)

st.plotly_chart(agent_load_heatmap(df), use_container_width=True)

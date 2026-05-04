import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import streamlit as st

from dashboard.components.charts import (
    category_bar,
    priority_donut,
    ticket_volume_timeseries,
)
from dashboard.components.filters import (
    apply_filters,
    category_filter,
    date_range_filter,
    priority_filter,
)


st.set_page_config(page_title="Ticket Overview", layout="wide")

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
    df["agent_group"] = np.select(
        [
            df["priority"].eq("critical"),
            df["category"].isin(["technical", "security"]),
            df["category"].isin(["billing", "refund"]),
        ],
        ["escalation", "tier2", "billing"],
        default="tier1",
    )
    return df


def _prepare_tickets(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    if "hour_created" not in data.columns:
        data["hour_created"] = data["created_at"].dt.hour.fillna(9).astype(int)
    if "day_of_week" not in data.columns:
        data["day_of_week"] = data["created_at"].dt.dayofweek.fillna(1).astype(int)
    if "is_weekend" not in data.columns:
        data["is_weekend"] = data["day_of_week"] >= 5
    return data


@st.cache_data
def load_tickets() -> pd.DataFrame:
    if DATA_PATH.exists():
        return _prepare_tickets(pd.read_parquet(DATA_PATH))
    return _synthetic_tickets()


df = load_tickets()
if DEMO_MODE or not DATA_PATH.exists():
    st.warning("Demo Mode: Showing synthetic data. Download datasets and run preprocessing to load real data.")

st.title("Ticket Overview")
start, end = date_range_filter(df)
priorities = priority_filter(df)
categories = category_filter(df)
filtered = apply_filters(df, start, end, priorities, categories)

total_tickets = len(filtered)
open_tickets = int((filtered.get("status", pd.Series(dtype=str)) != "closed").sum())
avg_resolution = float(filtered.get("resolution_hours", pd.Series(dtype=float)).mean() or 0)
sla_breach_pct = float(filtered.get("sla_breached", pd.Series(dtype=float)).mean() or 0) * 100

kpi_cols = st.columns(4)
kpi_cols[0].metric("Total Tickets", f"{total_tickets:,}")
kpi_cols[1].metric("Open Tickets", f"{open_tickets:,}")
kpi_cols[2].metric("Avg Resolution (hours)", f"{avg_resolution:.1f}")
kpi_cols[3].metric("SLA Breach %", f"{sla_breach_pct:.1f}%")

chart_cols = st.columns(3)
chart_cols[0].plotly_chart(ticket_volume_timeseries(filtered), use_container_width=True)
chart_cols[1].plotly_chart(category_bar(filtered), use_container_width=True)
chart_cols[2].plotly_chart(priority_donut(filtered), use_container_width=True)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def ticket_volume_timeseries(df: pd.DataFrame):
    data = df.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    daily = (
        data.dropna(subset=["created_at"])
        .assign(date=lambda x: x["created_at"].dt.date)
        .groupby("date")
        .size()
        .reset_index(name="ticket_count")
    )
    return px.line(
        daily,
        x="date",
        y="ticket_count",
        title="Ticket Volume Over Time",
        markers=True,
    )


def category_bar(df: pd.DataFrame):
    counts = (
        df["category"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
        .rename_axis("category")
        .reset_index(name="ticket_count")
    )
    return px.bar(
        counts,
        x="category",
        y="ticket_count",
        title="Tickets by Category",
    )


def priority_donut(df: pd.DataFrame):
    counts = (
        df["priority"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("priority")
        .reset_index(name="ticket_count")
    )
    return px.pie(
        counts,
        names="priority",
        values="ticket_count",
        hole=0.4,
        title="Priority Distribution",
    )


def sla_gauge(breach_rate: float):
    return go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(breach_rate),
            number={"valueformat": ".1%"},
            title={"text": "SLA Breach Rate"},
            gauge={
                "axis": {"range": [0, 1], "tickformat": ".0%"},
                "bar": {"color": "#1f2937"},
                "steps": [
                    {"range": [0, 0.15], "color": "#bbf7d0"},
                    {"range": [0.15, 0.30], "color": "#fde68a"},
                    {"range": [0.30, 1], "color": "#fecaca"},
                ],
            },
        )
    )


def agent_load_heatmap(df: pd.DataFrame):
    return px.density_heatmap(
        df,
        x="hour_created",
        y="day_of_week",
        title="Ticket Volume Heatmap",
    )

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import streamlit as st


def date_range_filter(df: pd.DataFrame):
    dates = pd.to_datetime(df["created_at"], errors="coerce").dropna()
    if dates.empty:
        today = pd.Timestamp.today().date()
        default_range = (today, today)
    else:
        default_range = (dates.min().date(), dates.max().date())

    selected = st.sidebar.date_input("Date range", value=default_range)
    if isinstance(selected, tuple):
        if len(selected) == 2:
            return selected
        if len(selected) == 1:
            return selected[0], selected[0]
    return selected, selected


def priority_filter(df: pd.DataFrame):
    options = sorted(df["priority"].dropna().unique().tolist())
    return st.sidebar.multiselect("Priority", options=options, default=options)


def category_filter(df: pd.DataFrame):
    options = sorted(df["category"].dropna().unique().tolist())
    return st.sidebar.multiselect("Category", options=options, default=options)


def apply_filters(df: pd.DataFrame, start, end, priorities, categories):
    filtered = df.copy()

    if "created_at" in filtered.columns and start is not None and end is not None:
        created_dates = pd.to_datetime(filtered["created_at"], errors="coerce").dt.date
        filtered = filtered[(created_dates >= start) & (created_dates <= end)]

    if "priority" in filtered.columns and priorities is not None:
        filtered = filtered[filtered["priority"].isin(priorities)]

    if "category" in filtered.columns and categories is not None:
        filtered = filtered[filtered["category"].isin(categories)]

    return filtered

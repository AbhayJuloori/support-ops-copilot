"""Clean and standardize support ticket data from 200K dataset.

Expected input CSV columns (flexible — adapts to actual column names):
Ticket ID, Customer Name, Customer Email, Customer Age, Customer Gender,
Product Purchased, Date of Purchase, Ticket Type, Ticket Subject,
Ticket Description, Ticket Status, Resolution, Ticket Priority,
Ticket Channel, First Response Time, Time to Resolution, Customer Satisfaction Rating

Output: data/processed/tickets_clean.parquet
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from src.config import DATA_RAW, DATA_PROCESSED, SLA_THRESHOLDS

logger = logging.getLogger(__name__)


def load_raw_tickets() -> pd.DataFrame:
    """Load the 200K tickets CSV from data/raw/tickets_200k/."""
    csv_files = list((DATA_RAW / "tickets_200k").glob("*.csv")) if (DATA_RAW / "tickets_200k").exists() else []
    csv_files += list(DATA_RAW.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV found in {DATA_RAW}. Run loader.py first.")
    path = csv_files[0]
    logger.info(f"Loading {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df):,} rows, columns: {df.columns.tolist()}")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    return df


def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if "date" in col or ("time" in col and "resolution" not in col):
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            except Exception:
                pass
    return df


def compute_resolution_hours(df: pd.DataFrame) -> pd.DataFrame:
    res_col = next((c for c in ["resolution_time_hours", "time_to_resolution", "resolution_time", "time_to_close"] if c in df.columns), None)

    if res_col and df[res_col].dtype in ["float64", "int64"]:
        df["resolution_hours"] = df[res_col]
    elif res_col:
        try:
            df["resolution_hours"] = pd.to_timedelta(df[res_col], errors="coerce").dt.total_seconds() / 3600
        except Exception:
            df["resolution_hours"] = np.nan
    else:
        df["resolution_hours"] = np.nan

    # Synthesize missing from priority using exponential distribution
    priority_mean = {"critical": 3, "high": 10, "medium": 30, "low": 60}
    mask = df["resolution_hours"].isna()
    if mask.sum() > 0:
        logger.warning(f"{mask.sum()} rows missing resolution_hours — synthesizing from priority")
        rng = np.random.default_rng(42)
        for p, mean in priority_mean.items():
            pmask = mask & (df.get("priority", pd.Series(dtype=str)) == p)
            if pmask.sum() > 0:
                df.loc[pmask, "resolution_hours"] = rng.exponential(scale=mean, size=pmask.sum())
        # Remaining nulls (unmatched priority)
        still_null = df["resolution_hours"].isna()
        if still_null.sum() > 0:
            df.loc[still_null, "resolution_hours"] = rng.exponential(scale=24, size=still_null.sum())
    return df


def add_sla_features(df: pd.DataFrame) -> pd.DataFrame:
    df["sla_threshold_hours"] = df["priority"].map(SLA_THRESHOLDS).fillna(24)
    # Use existing sla_breached column if present (Yes/No strings), else compute
    if "sla_breached" in df.columns and df["sla_breached"].dtype == object:
        df["sla_breached"] = df["sla_breached"].str.strip().str.lower().map({"yes": True, "no": False}).fillna(False)
    else:
        df["sla_breached"] = df["resolution_hours"] > df["sla_threshold_hours"]
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    dt_col = next(
        (c for c in ["created_at", "date_of_purchase", "date_created", "ticket_date", "date"]
         if c in df.columns and pd.api.types.is_datetime64_any_dtype(df[c])),
        None
    )
    if dt_col:
        df["hour_created"] = df[dt_col].dt.hour
        df["day_of_week"] = df[dt_col].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6])
        df["created_at"] = df[dt_col]
    else:
        df["hour_created"] = 9
        df["day_of_week"] = 1
        df["is_weekend"] = False
        df["created_at"] = pd.Timestamp("2024-01-01")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    df = parse_datetimes(df)

    # Map to standard names
    col_map = {}
    for std, variants in {
        "ticket_id": ["ticket_id", "id"],
        "subject": ["ticket_subject", "subject", "title"],
        "description": ["issue_description", "ticket_description", "description", "body", "message"],
        "priority": ["ticket_priority", "priority"],
        "category": ["ticket_type", "category", "type"],
        "channel": ["ticket_channel", "channel", "source"],
        "product": ["product_purchased", "product"],
        "status": ["ticket_status", "status"],
        "customer_satisfaction": ["customer_satisfaction_rating", "csat", "satisfaction_score"],
    }.items():
        for v in variants:
            if v in df.columns and v != std:
                col_map[v] = std
                break
    df = df.rename(columns=col_map)

    for col in ["ticket_id", "subject", "description", "priority", "category"]:
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found — creating placeholder")
            df[col] = "unknown"

    # Normalize priority
    df["priority"] = df["priority"].astype(str).str.lower().str.strip()
    df["priority"] = df["priority"].replace({
        "urgent": "critical", "p1": "critical", "p2": "high",
        "p3": "medium", "p4": "low", "normal": "medium",
    })
    df["priority"] = df["priority"].where(df["priority"].isin(SLA_THRESHOLDS.keys()), other="medium")

    df["category"] = df["category"].astype(str).str.lower().str.strip()
    df["text"] = (df["subject"].fillna("") + " " + df["description"].fillna("")).str.strip()

    df = add_time_features(df)
    df = compute_resolution_hours(df)
    df = add_sla_features(df)

    keep = [c for c in [
        "ticket_id", "subject", "description", "text", "priority", "category",
        "status", "channel", "product", "created_at", "resolution_hours",
        "sla_threshold_hours", "sla_breached", "hour_created", "day_of_week",
        "is_weekend", "customer_satisfaction",
    ] if c in df.columns]
    df = df[keep].copy()
    df = df[df["text"].str.len() > 5].reset_index(drop=True)

    logger.info(f"Clean output: {len(df):,} rows, {df.shape[1]} columns")
    logger.info(f"SLA breach rate: {df['sla_breached'].mean():.1%}")
    return df


def run() -> pd.DataFrame:
    df = load_raw_tickets()
    df = clean(df)
    out = DATA_PROCESSED / "tickets_clean.parquet"
    df.to_parquet(out, index=False)
    logger.info(f"Saved to {out}")
    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = run()
    print(df.dtypes)
    print(df.head())

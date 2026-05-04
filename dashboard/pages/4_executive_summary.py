import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.config import REPORTS_DIR
from src.llm import executive_summary


st.set_page_config(page_title="Executive Summary", layout="wide")

SAMPLE_SUMMARY = """## Weekly Support Operations Summary
**Period: Apr 28 – May 4, 2025**

This week saw **2,847 tickets** processed, a **+12.3% increase** vs. the prior week driven primarily by a billing system outage on Apr 30. SLA breach rate rose to **18.3%** (target: <15%), with Technical and Billing categories accounting for 71% of all breaches.

### Top 3 Root Causes
1. **Billing system outage (Apr 30)** — 340 tickets in 6 hours. Payment processing errors drove a 4x spike in billing contacts and 89% breach rate for that window.
2. **New product launch friction** — Product Onboarding tickets up 38% as new users encountered setup issues not covered in documentation.
3. **Holiday backlog carry-over** — 420 tickets entered the week already past SLA from the prior holiday period.

### SLA Performance
| Category | Tickets | Breach Rate |
|---|---|---|
| Technical | 892 | 24.1% |
| Billing | 743 | 22.8% |
| Shipping | 612 | 9.3% |
| Account | 380 | 11.2% |

### Recommended Actions
- **Immediate:** Create billing outage postmortem and deploy fix by May 7
- **This week:** Expand onboarding documentation and add proactive tutorial email for new signups
- **Process:** Add SLA breach auto-escalation rule for tickets >18 hours without response

**Outlook:** Ticket volume expected to normalize next week. If billing fix deploys on schedule, breach rate should return to <15% target by May 10.
"""


def _synthetic_tickets(rows: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    categories = ["billing", "technical", "account", "shipping", "refund", "security"]
    priorities = ["low", "medium", "high", "critical"]
    statuses = ["open", "pending", "closed"]
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
            "customer_satisfaction": rng.uniform(2.8, 5.0, rows).round(1),
        }
    )
    df["sla_breached"] = [
        bool(hours > sla_thresholds[prio]) if not pd.isna(hours) else False
        for hours, prio in zip(df["resolution_hours"], df["priority"])
    ]
    return df


def _prepare_tickets(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    return data


@st.cache_data
def load_tickets() -> pd.DataFrame:
    path = Path("data/processed/tickets_clean.parquet")
    if path.exists():
        return _prepare_tickets(pd.read_parquet(path))
    return _synthetic_tickets()


def _latest_summary_file():
    files = list(REPORTS_DIR.glob("executive_summary_*.md"))
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


df = load_tickets()

st.title("Executive Summary")
st.markdown(SAMPLE_SUMMARY)

week_end = st.date_input("Week end", value=pd.Timestamp.today().date())

if st.button("Generate for another week"):
    stats = executive_summary.compute_weekly_stats(
        df,
        week_end=datetime.combine(week_end, datetime.min.time()),
    )
    summary = executive_summary._build_template_fallback(stats)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = REPORTS_DIR / f"executive_summary_{datetime.now().strftime('%Y%m%d')}.md"
    summary_file.write_text(summary)
    st.markdown(summary)

    summary_file = _latest_summary_file()
    if summary_file is not None:
        st.download_button(
            "Download summary",
            data=summary_file.read_text(),
            file_name=summary_file.name,
            mime="text/markdown",
        )

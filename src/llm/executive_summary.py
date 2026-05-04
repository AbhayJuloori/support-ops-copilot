"""Weekly executive summary generator. Builds stats from ticket DataFrame, calls LLM."""
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from src.config import USE_OPENAI, OPENAI_API_KEY, OPENAI_MODEL, LLM_FALLBACK_MODEL, DATA_PROCESSED, REPORTS_DIR
from src.llm.prompts import EXECUTIVE_SUMMARY_SYSTEM, EXECUTIVE_SUMMARY_USER

logger = logging.getLogger(__name__)


def compute_weekly_stats(df: pd.DataFrame, week_end: datetime | None = None) -> dict:
    """Aggregate ticket stats for the past 7 days vs prior 7 days."""
    if week_end is None:
        week_end = df["created_at"].max()
    week_start = week_end - timedelta(days=7)
    prior_start = week_start - timedelta(days=7)

    this_week = df[(df["created_at"] >= week_start) & (df["created_at"] < week_end)]
    prior_week = df[(df["created_at"] >= prior_start) & (df["created_at"] < week_start)]

    total = len(this_week)
    prior_total = max(len(prior_week), 1)
    wow_pct = (total - prior_total) / prior_total * 100

    open_tickets = (this_week.get("status", pd.Series(dtype=str)) != "closed").sum() if "status" in this_week.columns else 0
    breach_rate = this_week["sla_breached"].mean() if "sla_breached" in this_week.columns else 0.0
    avg_res = this_week["resolution_hours"].mean() if "resolution_hours" in this_week.columns else 0.0

    top_cats = this_week["category"].value_counts().nlargest(5)
    top_categories = "\n".join(f"  - {cat}: {cnt} tickets" for cat, cnt in top_cats.items())

    prior_cats = prior_week["category"].value_counts() if len(prior_week) > 0 else pd.Series(dtype=int)
    rising = []
    for cat, cnt in top_cats.items():
        prior_cnt = prior_cats.get(cat, 0)
        if prior_cnt > 0:
            pct = (cnt - prior_cnt) / prior_cnt * 100
            if pct > 10:
                rising.append(f"  - {cat}: +{pct:.0f}%")
    rising_categories = "\n".join(rising) if rising else "  - No significant increases"

    escalations = int((this_week.get("priority", pd.Series(dtype=str)) == "critical").sum()) if "priority" in this_week.columns else 0
    csat = this_week["customer_satisfaction"].mean() if "customer_satisfaction" in this_week.columns else float("nan")
    csat_str = f"{csat:.1f}/5" if not pd.isna(csat) else "N/A"

    return {
        "period": f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}",
        "total_tickets": total,
        "week_over_week_pct": wow_pct,
        "open_tickets": int(open_tickets),
        "sla_breach_rate": float(breach_rate),
        "avg_resolution_hours": float(avg_res),
        "top_categories": top_categories,
        "rising_categories": rising_categories,
        "escalations": escalations,
        "csat_score": csat_str,
    }


def _call_openai(stats: dict) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXECUTIVE_SUMMARY_SYSTEM},
            {"role": "user", "content": EXECUTIVE_SUMMARY_USER.format(**stats)},
        ],
        max_tokens=600,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def _call_hf(stats: dict) -> str:
    from transformers import pipeline
    if not hasattr(_call_hf, "_pipe"):
        _call_hf._pipe = pipeline("text2text-generation", model=LLM_FALLBACK_MODEL,
                                   max_new_tokens=400, device=-1)
    prompt = (f"Write an executive summary for support operations: "              f"{stats['total_tickets']} tickets this week ({stats['week_over_week_pct']:+.1f}% vs last week), "              f"SLA breach rate {stats['sla_breach_rate']:.1%}, avg resolution {stats['avg_resolution_hours']:.1f}h. "              f"Top categories: {stats['top_categories']}. Rising: {stats['rising_categories']}.")
    return _call_hf._pipe(prompt)[0]["generated_text"].strip()


def generate(df: pd.DataFrame | None = None, week_end: datetime | None = None,
             save: bool = True) -> str:
    """Generate weekly executive summary. Returns Markdown string."""
    if df is None:
        df = pd.read_parquet(DATA_PROCESSED / "tickets_clean.parquet")

    stats = compute_weekly_stats(df, week_end=week_end)
    logger.info(f"Generating executive summary for {stats['period']}")

    try:
        summary = _call_openai(stats) if USE_OPENAI else _call_hf(stats)
    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
        summary = _build_template_fallback(stats)

    if save:
        path = REPORTS_DIR / f"executive_summary_{datetime.now().strftime('%Y%m%d')}.md"
        path.write_text(summary)
        logger.info(f"Saved to {path}")

    return summary


def _build_template_fallback(stats: dict) -> str:
    """Rule-based fallback when LLM is unavailable."""
    return f"""# Weekly Support Operations Summary
**Period:** {stats['period']}

## Overview
{stats['total_tickets']} tickets processed this week ({stats['week_over_week_pct']:+.1f}% vs prior week).
SLA breach rate: **{stats['sla_breach_rate']:.1%}**. Avg resolution: {stats['avg_resolution_hours']:.1f}h.

## Top Categories
{stats['top_categories']}

## Rising Categories
{stats['rising_categories']}

## Recommended Actions
- Review SLA breach rate — target < 15%
- Address rising ticket categories with targeted resources
- Escalation tickets ({stats['escalations']}): ensure tier-2 coverage
"""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    summary = generate()
    print(summary)

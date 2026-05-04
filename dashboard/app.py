import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st


st.set_page_config(page_title="Support Ops Copilot", page_icon="🎧", layout="wide")

DATA_PATH = Path("data/processed/tickets_clean.parquet")
DEMO_MODE = not DATA_PATH.exists()

st.sidebar.title("🎧 Support Ops Copilot")
st.sidebar.markdown(
    "AI dashboard for ticket trends, SLA risk, auto-routing, and executive summaries."
)

st.title("🎧 AI Support Operations Copilot")

col1, col2, col3 = st.columns(3)
col1.metric("200K+ Tickets Analyzed", "ML-ready")
col2.metric("5 AI Components", "Classifier + SLA + Routing + LLM")
col3.metric("4 Live Dashboard Views", "Operations cockpit")

st.info("Use the sidebar to explore Ticket Overview, SLA Risk Monitor, Auto-Routing, and Executive Summary.")

if DEMO_MODE or not DATA_PATH.exists():
    st.success("Live Demo Running — all pages use realistic synthetic data. No setup required.")

overview, risk, reporting = st.columns(3)
overview.subheader("Ticket Operations")
overview.markdown("Track support volume, category mix, priority distribution, and core KPIs.")

risk.subheader("SLA and Routing")
risk.markdown("Monitor breach risk, inspect high-risk open tickets, and test routing recommendations.")

reporting.subheader("Executive Reporting")
reporting.markdown("Generate weekly operations summaries from the latest processed ticket data.")

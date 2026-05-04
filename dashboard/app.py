import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st


st.set_page_config(page_title="Support Ops Copilot", page_icon="🎧", layout="wide")

st.sidebar.title("🎧 Support Ops Copilot")
st.sidebar.markdown(
    "AI dashboard for ticket trends, SLA risk, auto-routing, and executive summaries."
)

st.title("🎧 AI Support Operations Copilot")
st.markdown(
    "Intelligent ticket routing, SLA prediction, and executive insights — powered by XGBoost + GPT-4"
)

metric_cols = st.columns(4)
metric_cols[0].metric("200K+ Records Trained", "Support tickets")
metric_cols[1].metric("~74% Classifier Accuracy", "Ticket category model")
metric_cols[2].metric("~81% SLA AUC-ROC", "Breach prediction")
metric_cols[3].metric("4 Live AI Features", "Interactive demo")

st.info("👈 Use the sidebar to explore all features. Every page is fully interactive with live demo data.")

overview, risk, reporting = st.columns(3)

with overview.container(border=True):
    st.subheader("Ticket Operations")
    st.markdown(
        "Explore volume trends, priority mix, channel patterns, and SLA health from a realistic support dataset. "
        "Recruiters can filter the dashboard and see KPIs respond instantly."
    )

with risk.container(border=True):
    st.subheader("SLA Risk Monitor")
    st.markdown(
        "Score open tickets by predicted breach probability and isolate the highest-risk work with a live threshold slider. "
        "The demo highlights how operations teams can catch SLA problems before they happen."
    )

with reporting.container(border=True):
    st.subheader("Auto-Routing + Insights")
    st.markdown(
        "Test a live routing assistant that classifies customer intent and recommends the right support queue. "
        "The executive summary page turns weekly ticket metrics into crisp leadership-ready action items."
    )

st.caption("Built by Abhay Juloori · GitHub · Streamlit")

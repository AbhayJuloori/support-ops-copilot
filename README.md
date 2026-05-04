---
title: AI Support Operations Copilot
emoji: 🎧
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: dashboard/app.py
pinned: true
---

# AI Support Operations Copilot

## Problem Statement

Support teams are drowning in rising ticket volume while customers expect fast, accurate responses across every channel. Without intelligent routing and SLA risk prediction, urgent issues sit in the wrong queue, breach commitments, and create avoidable churn and revenue risk.

## Solution Overview

AI Support Operations Copilot is an end-to-end support intelligence system that turns raw ticket data into routing decisions, SLA risk signals, and executive-ready summaries.

- 🎫 **Ticket classifier:** predicts support category from ticket text and priority.
- ⏱️ **SLA breach predictor:** estimates breach probability before a ticket misses its target.
- 🧭 **Routing engine:** recommends the right agent group using category, urgency, and SLA risk.
- 📊 **Streamlit dashboard:** gives operators ticket volume, breach trends, routing load, and summary views.
- 🧠 **LLM summarizer:** generates concise ticket summaries and weekly executive narratives.

## Architecture

```text
Raw Data
   |
   v
Preprocessor
   |
   v
Feature Engineering
   |
   +-------------------+-------------------+
   |                   |                   |
   v                   v                   v
Classifier       SLA Predictor      Routing Engine
   |                   |                   |
   +-------------------+-------------------+
                       |
                       v
                    FastAPI
                       |
          +------------+-------------+
          |                          |
          v                          v
 Streamlit Dashboard          LLM Summarizer
                                      |
                                      v
                             Executive Summary
```

## Datasets

| Dataset name | Source | Rows | Used for |
|---|---:|---:|---|
| Customer Support Tickets 200K | Kaggle: `mirzayasirabdullah07/customer-support-tickets-dataset-200k-records` | ~200,000 | Preprocessing, category classification, SLA prediction, routing features |
| Bitext Customer Support Intent Dataset | Hugging Face/Kaggle: `bitext/bitext-gen-ai-chatbot-customer-support-dataset` | ~27,000 | Intent examples, summarization demos, classifier enrichment |

## Model Performance

| Model | Algorithm | Metric | Score |
|---|---|---:|---:|
| Ticket Classifier | XGBoost + TF-IDF | Macro F1 | Target: 0.74+ |
| SLA Breach Predictor | XGBoost + SMOTE | AUC-ROC | Target: 0.81+ |

## Quick Start

```bash
git clone https://github.com/AbhayJuloori/support-ops-copilot.git
cd support-ops-copilot && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python src/data/loader.py
python src/data/preprocessor.py && python src/models/ticket_classifier.py && python src/models/sla_predictor.py
streamlit run dashboard/app.py
```

## Dashboard Pages

- 📈 **Ticket Overview:** ticket volume, backlog, SLA breach rate, and category/priority breakdowns.
- 🚨 **SLA Risk Monitor:** at-risk tickets, breach probability, and escalation candidates.
- 🧭 **Routing Dashboard:** recommended agent groups, routing rationale, and team load patterns.
- 📝 **Executive Summary:** weekly LLM-generated operations summary with actions and outlook.

## API Reference

| Method | Endpoint | Description | Example payload |
|---|---|---|---|
| GET | `/health` | Returns service status and model availability. | N/A |
| POST | `/classify` | Predicts ticket category and confidence. | `{"text": "my wifi is broken", "priority": "high"}` |
| POST | `/sla-risk` | Predicts SLA breach probability and risk level. | `{"text": "refund still pending", "priority": "medium", "category": "billing"}` |
| POST | `/route` | Recommends an agent group for a new ticket. | `{"text": "checkout failed twice", "priority": "high"}` |
| POST | `/summarize` | Generates a concise ticket summary. | `{"subject": "Duplicate charge", "description": "I was billed twice", "priority": "high", "category": "billing"}` |

Run the API locally:

```bash
uvicorn api.main:app --reload
```

## Deployment

Deploy the dashboard to Hugging Face Spaces with the Streamlit SDK:

1. Create a new Hugging Face Space and select **Streamlit**.
2. Push this repository to the Space, including `requirements.txt`, `dashboard/`, `src/`, and any trained model artifacts you want available at runtime.
3. Set `OPENAI_API_KEY` as a Space secret if GPT-powered summaries should use OpenAI; otherwise the app falls back to the local Hugging Face summarization path.
4. Set the Space app entry point to `dashboard/app.py`.
5. Rebuild the Space and verify all four dashboard pages render.

## Project Structure

```text
support-ops-copilot/
├── api/
│   ├── main.py
│   ├── schemas.py
│   └── routers/
│       ├── classify.py
│       ├── sla.py
│       ├── route.py
│       └── summarize.py
├── dashboard/
│   ├── app.py
│   ├── components/
│   │   ├── charts.py
│   │   └── filters.py
│   └── pages/
│       ├── 1_ticket_overview.py
│       ├── 2_sla_risk.py
│       ├── 3_routing.py
│       └── 4_executive_summary.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   ├── ticket_classifier.pkl
│   └── sla_predictor.pkl
├── reports/
│   └── sample_executive_summary.md
├── src/
│   ├── config.py
│   ├── data/
│   │   ├── loader.py
│   │   ├── preprocessor.py
│   │   └── feature_engineer.py
│   ├── llm/
│   │   ├── prompts.py
│   │   ├── summarizer.py
│   │   └── executive_summary.py
│   └── models/
│       ├── ticket_classifier.py
│       ├── sla_predictor.py
│       ├── routing_recommender.py
│       └── evaluator.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_classifier.py
│   ├── test_preprocessor.py
│   └── test_sla_predictor.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

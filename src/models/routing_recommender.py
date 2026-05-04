"""Auto-routing recommender: rule-based layer on classifier + SLA risk.

Routing matrix:
  P(breach) > 0.7  → escalation
  priority == critical → tier2
  technical/network/security category → tier2
  billing/payment → billing team
  default → tier1
"""
import logging
import pandas as pd
from src.models.ticket_classifier import predict as classify
from src.models.sla_predictor import predict_risk

logger = logging.getLogger(__name__)

_RULES = [
    (lambda c, p, s: s["breach_probability"] > 0.7, "escalation", "High SLA breach risk (>70%)"),
    (lambda c, p, s: p == "critical", "tier2", "Critical priority ticket"),
    (lambda c, p, s: any(kw in c for kw in ["technical", "network", "security", "bug", "error", "crash"]),
     "tier2", "Technical issue category"),
    (lambda c, p, s: any(kw in c for kw in ["billing", "payment", "refund", "charge", "invoice"]),
     "billing", "Billing/payment category"),
    (lambda c, p, s: True, "tier1", "Standard ticket — routed to tier1"),
]


def recommend(text: str, priority: str = "medium",
              hour_created: int = 9, day_of_week: int = 1) -> dict:
    cat_result = classify(text, priority=priority)
    category = cat_result["category"]

    sla_result = predict_risk({
        "priority": priority,
        "hour_created": hour_created,
        "day_of_week": day_of_week,
        "is_weekend": day_of_week >= 5,
        "text_length": len(text),
        "word_count": len(text.split()),
        "category": category,
    })

    for condition, group, reason in _RULES:
        if condition(category.lower(), priority.lower(), sla_result):
            return {
                "agent_group": group,
                "rationale": reason,
                "predicted_category": category,
                "category_confidence": cat_result["confidence"],
                "breach_probability": sla_result["breach_probability"],
                "risk_level": sla_result["risk_level"],
            }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(recommend("Payment was charged twice, need refund immediately", priority="high"))

import pandas as pd

from src.data.preprocessor import clean, normalize_columns


def test_normalize_columns():
    df = pd.DataFrame(columns=["Ticket ID", "Ticket Subject", "Ticket Priority"])

    normalized = normalize_columns(df)

    assert normalized.columns.tolist() == [
        "ticket_id",
        "ticket_subject",
        "ticket_priority",
    ]


def test_clean_output_columns():
    df = pd.DataFrame(
        [
            {
                "Ticket ID": "T-1",
                "Ticket Subject": "Cannot connect",
                "Ticket Description": "Customer wifi fails after router restart",
                "Ticket Priority": "High",
                "Ticket Type": "Technical",
            }
        ]
    )

    cleaned = clean(df)

    expected = [
        "ticket_id",
        "subject",
        "description",
        "text",
        "priority",
        "category",
        "sla_breached",
        "resolution_hours",
    ]
    assert all(column in cleaned.columns for column in expected)


def test_priority_normalization():
    df = pd.DataFrame(
        [
            {
                "Ticket ID": "T-1",
                "Ticket Subject": "Outage reported",
                "Ticket Description": "Customer cannot access the billing portal",
                "Ticket Priority": "Urgent",
                "Ticket Type": "Billing",
            },
            {
                "Ticket ID": "T-2",
                "Ticket Subject": "General question",
                "Ticket Description": "Customer asks for invoice details",
                "Ticket Priority": "Normal",
                "Ticket Type": "Billing",
            },
        ]
    )

    cleaned = clean(df)

    assert cleaned["priority"].tolist() == ["critical", "medium"]


def test_sla_breached_computed():
    df = pd.DataFrame(
        [
            {
                "Ticket ID": "T-1",
                "Ticket Subject": "Escalated outage",
                "Ticket Description": "Customer production system is unavailable",
                "Ticket Priority": "High",
                "Ticket Type": "Technical",
                "Time to Resolution": 9,
            }
        ]
    )

    cleaned = clean(df)

    assert cleaned.loc[0, "sla_threshold_hours"] == 8
    assert bool(cleaned.loc[0, "sla_breached"]) is True


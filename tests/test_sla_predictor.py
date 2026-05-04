import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np

sys.modules.setdefault("mlflow", types.ModuleType("mlflow"))

from src.models import sla_predictor


def test_predict_risk_structure():
    mock_clf = MagicMock()
    mock_clf.predict_proba.return_value = np.array([[0.25, 0.75]])

    artifacts = {
        "classifier": mock_clf,
        "feature_names": [
            "priority_enc",
            "hour_created",
            "day_of_week",
            "is_weekend",
            "text_length",
            "word_count",
            "cat_billing",
        ],
    }
    row = {
        "text": "Refund request for duplicate charge",
        "priority": "high",
        "hour_created": 10,
        "day_of_week": 2,
        "is_weekend": False,
        "category": "billing",
    }

    with patch.object(sla_predictor, "load_predictor", return_value=artifacts):
        result = sla_predictor.predict_risk(row)

    assert set(result.keys()) == {"breach_probability", "risk_level", "will_breach"}
    assert 0.0 <= result["breach_probability"] <= 1.0
    assert result["risk_level"] in {"low", "medium", "high"}
    assert isinstance(result["will_breach"], bool)


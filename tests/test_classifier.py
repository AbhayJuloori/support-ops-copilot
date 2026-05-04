import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np
from scipy.sparse import csr_matrix

sys.modules.setdefault("mlflow", types.ModuleType("mlflow"))

from src.models import ticket_classifier


def test_predict_returns_valid_structure():
    mock_clf = MagicMock()
    mock_clf.predict_proba.return_value = np.array([[0.15, 0.7, 0.15]])

    mock_vectorizer = MagicMock()
    mock_vectorizer.transform.return_value = csr_matrix([[0.2, 0.8]])

    mock_label_encoder = MagicMock()
    mock_label_encoder.classes_ = np.array(["billing", "technical", "shipping"])

    artifacts = {
        "classifier": mock_clf,
        "label_encoder": mock_label_encoder,
        "vectorizer": mock_vectorizer,
    }

    with patch.object(ticket_classifier, "load_classifier", return_value=artifacts):
        result = ticket_classifier.predict("test text")

    assert set(result.keys()) == {"category", "confidence", "all_probabilities"}
    assert result["category"] == "technical"
    assert 0.0 <= result["confidence"] <= 1.0
    assert set(result["all_probabilities"].keys()) == {
        "billing",
        "technical",
        "shipping",
    }


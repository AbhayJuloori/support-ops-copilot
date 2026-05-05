"""Ticket category classifier: XGBoost + TF-IDF pipeline.
Trains on ticket text + metadata features, predicts ticket category.
Saves to models/ticket_classifier.pkl + MLflow run.
"""
import json
import pickle
import logging
from datetime import datetime
from typing import Optional
import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from src.config import DATA_PROCESSED, MODELS_DIR, REPORTS_DIR
from src.data.feature_engineer import build_features_for_classification

logger = logging.getLogger(__name__)


def train(df: Optional[pd.DataFrame] = None) -> dict:
    if df is None:
        df = pd.read_parquet(DATA_PROCESSED / "tickets_clean.parquet")

    le = LabelEncoder()
    y = le.fit_transform(df["category"])
    X, vectorizer = build_features_for_classification(df, fit=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        eval_metric="mlogloss", random_state=42, n_jobs=-1, verbosity=0,
    )

    with mlflow.start_run(run_name="ticket_classifier"):
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)
        results = {
            "accuracy": float(acc),
            "macro_f1": float(macro_f1),
            "classes": le.classes_.tolist(),
            "trained_at": datetime.now().isoformat(),
        }
        with open(REPORTS_DIR / "classifier_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("macro_f1", macro_f1)
        logger.info(f"Classifier — Accuracy: {acc:.3f}, Macro F1: {macro_f1:.3f}")
        logger.info(f"\n{report}")

        artifacts = {"classifier": clf, "label_encoder": le, "vectorizer": vectorizer}
        path = MODELS_DIR / "ticket_classifier.pkl"
        with open(path, "wb") as f:
            pickle.dump(artifacts, f)
        mlflow.log_artifact(str(path))
        logger.info(f"Saved to {path}")

    return {"accuracy": acc, "macro_f1": macro_f1, "classes": le.classes_.tolist()}


def load_classifier():
    with open(MODELS_DIR / "ticket_classifier.pkl", "rb") as f:
        return pickle.load(f)


def predict(text: str, priority: str = "medium") -> dict:
    arts = load_classifier()
    clf, le, vec = arts["classifier"], arts["label_encoder"], arts["vectorizer"]
    row = pd.DataFrame([{
        "text": text, "priority": priority,
        "hour_created": 9, "day_of_week": 1, "is_weekend": False, "channel": "email",
    }])
    X, _ = build_features_for_classification(row, fit=False, vectorizer=vec)
    proba = clf.predict_proba(X)[0]
    idx = int(np.argmax(proba))
    return {
        "category": le.classes_[idx],
        "confidence": float(proba[idx]),
        "all_probabilities": dict(zip(le.classes_.tolist(), proba.tolist())),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())

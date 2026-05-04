"""SLA breach predictor: XGBoost + SMOTE for class imbalance.
Input: ticket metadata features. Output: P(breach), risk level.
"""
import json
import pickle
import logging
from datetime import datetime
import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, average_precision_score
from xgboost import XGBClassifier
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False
from src.config import DATA_PROCESSED, MODELS_DIR, REPORTS_DIR
from src.data.feature_engineer import build_sla_features

logger = logging.getLogger(__name__)

RISK_THRESHOLDS = {"low": 0.3, "medium": 0.6, "high": 1.0}


def train(df: pd.DataFrame | None = None) -> dict:
    if df is None:
        df = pd.read_parquet(DATA_PROCESSED / "tickets_clean.parquet")

    X = build_sla_features(df)
    y = df["sla_breached"].astype(int)
    feature_names = X.columns.tolist()
    X_arr = X.values

    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y, test_size=0.2, random_state=42, stratify=y
    )

    if HAS_SMOTE and y_train.mean() < 0.3:
        sm = SMOTE(random_state=42)
        X_train, y_train = sm.fit_resample(X_train, y_train)
        logger.info(f"SMOTE applied. Breach rate after: {y_train.mean():.2%}")

    clf = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
        eval_metric="logloss", random_state=42, n_jobs=-1, verbosity=0,
    )

    with mlflow.start_run(run_name="sla_predictor"):
        clf.fit(X_train, y_train)
        y_proba = clf.predict_proba(X_test)[:, 1]
        y_pred = (y_proba > 0.5).astype(int)

        auc = roc_auc_score(y_test, y_proba)
        ap = average_precision_score(y_test, y_proba)
        report = classification_report(y_test, y_pred, zero_division=0)
        results = {
            "auc_roc": float(auc),
            "avg_precision": float(ap),
            "trained_at": datetime.now().isoformat(),
        }
        with open(REPORTS_DIR / "sla_predictor_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        mlflow.log_metric("auc_roc", auc)
        mlflow.log_metric("avg_precision", ap)
        logger.info(f"SLA Predictor — AUC-ROC: {auc:.3f}, Avg Precision: {ap:.3f}")
        logger.info(f"\n{report}")

        artifacts = {"classifier": clf, "feature_names": feature_names}
        path = MODELS_DIR / "sla_predictor.pkl"
        with open(path, "wb") as f:
            pickle.dump(artifacts, f)
        mlflow.log_artifact(str(path))
        logger.info(f"Saved to {path}")

    return {"auc_roc": auc, "avg_precision": ap}


def load_predictor():
    with open(MODELS_DIR / "sla_predictor.pkl", "rb") as f:
        return pickle.load(f)


def predict_risk(row: dict) -> dict:
    """Predict SLA breach probability for a single ticket metadata row."""
    arts = load_predictor()
    clf, feature_names = arts["classifier"], arts["feature_names"]

    df_row = pd.DataFrame([row])
    X = build_sla_features(df_row)
    for col in feature_names:
        if col not in X.columns:
            X[col] = 0
    X = X[feature_names]

    proba = float(clf.predict_proba(X.values)[0, 1])
    risk_level = next((lvl for lvl, thr in RISK_THRESHOLDS.items() if proba <= thr), "high")

    return {
        "breach_probability": proba,
        "risk_level": risk_level,
        "will_breach": proba > 0.5,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())

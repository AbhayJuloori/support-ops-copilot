"""Feature engineering: TF-IDF text features, time features, sentence embeddings."""
import json
import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix
from src.config import DATA_PROCESSED, MODELS_DIR, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

TFIDF_MAX_FEATURES = 500
META_SCHEMA_PATH = MODELS_DIR / "meta_feature_schema.json"


def build_tfidf(texts: pd.Series, fit: bool = True, vectorizer=None):
    """Fit or transform TF-IDF. Returns (sparse_matrix, vectorizer)."""
    if fit:
        vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES, ngram_range=(1, 2),
            stop_words="english", sublinear_tf=True,
        )
        X = vectorizer.fit_transform(texts.fillna(""))
        path = MODELS_DIR / "tfidf_vectorizer.pkl"
        with open(path, "wb") as f:
            pickle.dump(vectorizer, f)
        logger.info(f"TF-IDF fitted: {X.shape}, saved to {path}")
    else:
        X = vectorizer.transform(texts.fillna(""))
    return X, vectorizer


def _build_meta_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Numeric metadata features with stable column names."""
    priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    feat = pd.DataFrame({
        "hour_created": df["hour_created"].fillna(9),
        "day_of_week": df["day_of_week"].fillna(1),
        "is_weekend": df["is_weekend"].astype(int),
        "priority_enc": df["priority"].map(priority_order).fillna(1),
    })
    if "channel" in df.columns:
        for ch in df["channel"].value_counts().nlargest(5).index:
            feat[f"ch_{ch}"] = (df["channel"] == ch).astype(int)
    return feat.astype(np.float32)


def save_meta_schema(df: pd.DataFrame) -> None:
    """Save metadata feature column names for inference-time alignment."""
    with open(META_SCHEMA_PATH, "w", encoding="utf-8") as f:
        json.dump(df.columns.tolist(), f, indent=2)


def load_meta_schema() -> list[str]:
    """Load metadata feature column names saved during classifier training."""
    try:
        with open(META_SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return ["hour_created", "day_of_week", "is_weekend", "priority_enc"]


def build_meta_features(df: pd.DataFrame) -> np.ndarray:
    """Numeric metadata features: hour, day, is_weekend, priority_enc, channel_enc."""
    return _build_meta_feature_frame(df).values.astype(np.float32)


def build_embeddings(texts: pd.Series, batch_size: int = 256) -> np.ndarray:
    """Sentence embeddings via all-MiniLM-L6-v2. Cached to disk."""
    cache_path = DATA_PROCESSED / "embeddings.npy"
    if cache_path.exists():
        logger.info(f"Loading cached embeddings from {cache_path}")
        return np.load(cache_path)
    logger.info(f"Computing embeddings for {len(texts):,} texts...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(
        texts.fillna("").tolist(),
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    np.save(cache_path, embeddings)
    logger.info(f"Embeddings saved: {embeddings.shape}")
    return embeddings


def build_features_for_classification(df: pd.DataFrame, fit: bool = True, vectorizer=None):
    """TF-IDF + metadata features for ticket classifier."""
    X_tfidf, vectorizer = build_tfidf(df["text"], fit=fit, vectorizer=vectorizer)
    X_meta_df = _build_meta_feature_frame(df)
    if fit:
        save_meta_schema(X_meta_df)
    else:
        schema = load_meta_schema()
        X_meta_df = X_meta_df.reindex(columns=schema, fill_value=0)
    X_meta = csr_matrix(X_meta_df.values.astype(np.float32))
    return hstack([X_tfidf, X_meta]), vectorizer


def build_sla_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tabular features for SLA predictor."""
    priority_order = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    feat = pd.DataFrame({
        "priority_enc": df["priority"].map(priority_order).fillna(1),
        "hour_created": df["hour_created"].fillna(9),
        "day_of_week": df["day_of_week"].fillna(1),
        "is_weekend": df["is_weekend"].astype(int),
        "text_length": df["text"].str.len().fillna(0),
        "word_count": df["text"].str.split().str.len().fillna(0),
    })
    for cat in df["category"].value_counts().nlargest(20).index:
        feat[f"cat_{cat.replace(' ', '_')}"] = (df["category"] == cat).astype(int)
    if "channel" in df.columns:
        for ch in df["channel"].value_counts().nlargest(5).index:
            feat[f"ch_{ch}"] = (df["channel"] == ch).astype(int)
    return feat


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = pd.read_parquet(DATA_PROCESSED / "tickets_clean.parquet")
    print(f"Loaded {len(df):,} rows")
    X, vec = build_features_for_classification(df)
    print(f"Classification features: {X.shape}")
    sla = build_sla_features(df)
    print(f"SLA features: {sla.shape}")

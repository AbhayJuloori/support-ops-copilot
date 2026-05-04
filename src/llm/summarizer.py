"""Single-ticket summarizer. Uses OpenAI gpt-4o-mini if API key set, else flan-t5-base."""
import logging
import pandas as pd
from src.config import USE_OPENAI, OPENAI_API_KEY, OPENAI_MODEL, LLM_FALLBACK_MODEL
from src.llm.prompts import SUMMARIZE_TICKET_SYSTEM, SUMMARIZE_TICKET_USER

logger = logging.getLogger(__name__)


def _summarize_openai(subject: str, description: str, priority: str, category: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SUMMARIZE_TICKET_SYSTEM},
            {"role": "user", "content": SUMMARIZE_TICKET_USER.format(
                subject=subject, description=description,
                priority=priority, category=category,
            )},
        ],
        max_tokens=200,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def _summarize_hf(subject: str, description: str, priority: str, category: str) -> str:
    from transformers import pipeline
    # Lazy load — cached after first call
    if not hasattr(_summarize_hf, "_pipe"):
        logger.info(f"Loading {LLM_FALLBACK_MODEL} pipeline (first call)...")
        _summarize_hf._pipe = pipeline("text2text-generation", model=LLM_FALLBACK_MODEL,
                                        max_new_tokens=150, device=-1)
    text = (f"Summarize this support ticket in 3 bullets (Issue, Urgency, Action): "
            f"Subject: {subject}. Description: {description[:300]}. Priority: {priority}.")
    result = _summarize_hf._pipe(text)[0]["generated_text"]
    return result.strip()


def summarize_ticket(subject: str, description: str,
                     priority: str = "medium", category: str = "unknown") -> str:
    """Summarize a single ticket. Returns 3-bullet string."""
    try:
        if USE_OPENAI:
            return _summarize_openai(subject, description, priority, category)
        return _summarize_hf(subject, description, priority, category)
    except Exception as e:
        logger.warning(f"Summarizer failed: {e}")
        return f"• Issue: {subject[:100]}\n• Urgency: {priority}\n• Recommended Action: Review ticket manually."


def summarize_batch(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Summarize top-n tickets. Returns df with 'summary' column added."""
    sample = df.head(n).copy()
    sample["summary"] = sample.apply(
        lambda r: summarize_ticket(
            str(r.get("subject", "")),
            str(r.get("description", "")),
            str(r.get("priority", "medium")),
            str(r.get("category", "unknown")),
        ),
        axis=1,
    )
    return sample


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    summary = summarize_ticket(
        subject="Payment charged twice",
        description="I was billed twice for my order #12345. Please issue a refund immediately.",
        priority="high",
        category="billing",
    )
    print(summary)

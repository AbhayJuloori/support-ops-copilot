from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
DATA_RAW = ROOT / 'data' / 'raw'
DATA_PROCESSED = ROOT / 'data' / 'processed'
MODELS_DIR = ROOT / 'models'
REPORTS_DIR = ROOT / 'reports'

for d in [DATA_RAW, DATA_PROCESSED, MODELS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_OPENAI = bool(OPENAI_API_KEY)

SLA_THRESHOLDS = {
    'critical': 4,
    'high': 8,
    'medium': 24,
    'low': 72,
}

EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
LLM_FALLBACK_MODEL = 'google/flan-t5-base'
OPENAI_MODEL = 'gpt-4o-mini'

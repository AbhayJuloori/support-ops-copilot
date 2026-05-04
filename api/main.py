import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import classify, route, sla, summarize
from api.schemas import HealthResponse
from src.config import MODELS_DIR


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Support Ops Copilot API",
    version="0.1.0",
    description="Ticket classification, SLA prediction, routing, and LLM summarization.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classify.router)
app.include_router(sla.router)
app.include_router(route.router)
app.include_router(summarize.router)


def _models_status() -> dict[str, bool]:
    return {
        "classifier": (MODELS_DIR / "ticket_classifier.pkl").exists(),
        "sla_predictor": (MODELS_DIR / "sla_predictor.pkl").exists(),
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", models_loaded=_models_status())


@app.on_event("startup")
def log_startup() -> None:
    logger.info("API started. Models status: %s", _models_status())

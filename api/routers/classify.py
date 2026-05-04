from fastapi import APIRouter, HTTPException

from api.schemas import ClassifyRequest, ClassifyResponse
from src.config import MODELS_DIR


router = APIRouter(prefix="/classify")


@router.post("", response_model=ClassifyResponse)
@router.post("/", response_model=ClassifyResponse)
def classify_ticket(request: ClassifyRequest) -> ClassifyResponse:
    if not (MODELS_DIR / "ticket_classifier.pkl").exists():
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run: python src/models/ticket_classifier.py",
        )

    from src.models.ticket_classifier import predict

    try:
        result = predict(request.text, priority=request.priority)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run: python src/models/ticket_classifier.py",
        ) from exc

    return ClassifyResponse(**result)

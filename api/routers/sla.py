from fastapi import APIRouter, HTTPException

from api.schemas import SLARiskRequest, SLARiskResponse


router = APIRouter(prefix="/sla-risk")


@router.post("/", response_model=SLARiskResponse)
def predict_sla_risk(request: SLARiskRequest) -> SLARiskResponse:
    row = {
        "text": request.text,
        "priority": request.priority,
        "hour_created": request.hour_created,
        "day_of_week": request.day_of_week,
        "is_weekend": request.day_of_week >= 5,
        "text_length": len(request.text),
        "word_count": len(request.text.split()),
        "category": request.category,
    }

    from src.models.sla_predictor import predict_risk

    try:
        result = predict_risk(row)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Model not trained yet.") from exc

    return SLARiskResponse(**result)

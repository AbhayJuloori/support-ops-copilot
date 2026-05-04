from fastapi import APIRouter, HTTPException

from api.schemas import RouteRequest, RouteResponse


router = APIRouter(prefix="/route")


@router.post("/", response_model=RouteResponse)
def route_ticket(request: RouteRequest) -> RouteResponse:
    from src.models.routing_recommender import recommend

    try:
        result = recommend(
            request.text,
            priority=request.priority,
            hour_created=request.hour_created,
            day_of_week=request.day_of_week,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Model not trained yet.") from exc

    return RouteResponse(**result)

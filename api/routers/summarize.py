from fastapi import APIRouter

from api.schemas import SummarizeRequest, SummarizeResponse
from src.llm.summarizer import summarize_ticket


router = APIRouter(prefix="/summarize")


@router.post("/", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    summary = summarize_ticket(
        request.subject,
        request.description,
        priority=request.priority,
        category=request.category,
    )
    return SummarizeResponse(summary=summary)

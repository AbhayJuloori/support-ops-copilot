from typing import Annotated

from pydantic import BaseModel, Field, field_validator


VALID_PRIORITIES = {"critical", "high", "medium", "low"}
HourCreated = Annotated[int, Field(ge=0, le=23)]
DayOfWeek = Annotated[int, Field(ge=0, le=6)]


def _strip_non_empty(value, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} must be non-empty")
    return value


class PriorityValidatedModel(BaseModel):
    priority: str = "medium"

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, value):
        if not isinstance(value, str):
            raise ValueError("priority must be a string")
        value = value.strip().lower()
        if value not in VALID_PRIORITIES:
            raise ValueError("priority must be one of: critical, high, medium, low")
        return value


class ClassifyRequest(PriorityValidatedModel):
    text: str

    @field_validator("text", mode="before")
    @classmethod
    def validate_text(cls, value):
        return _strip_non_empty(value, "text")


class ClassifyResponse(BaseModel):
    category: str
    confidence: float
    all_probabilities: dict[str, float]


class SLARiskRequest(PriorityValidatedModel):
    text: str
    hour_created: HourCreated = 9
    day_of_week: DayOfWeek = 1
    category: str = "unknown"

    @field_validator("text", mode="before")
    @classmethod
    def validate_text(cls, value):
        return _strip_non_empty(value, "text")


class SLARiskResponse(BaseModel):
    breach_probability: float
    risk_level: str
    will_breach: bool


class RouteRequest(PriorityValidatedModel):
    text: str
    hour_created: HourCreated = 9
    day_of_week: DayOfWeek = 1

    @field_validator("text", mode="before")
    @classmethod
    def validate_text(cls, value):
        return _strip_non_empty(value, "text")


class RouteResponse(BaseModel):
    agent_group: str
    rationale: str
    predicted_category: str
    category_confidence: float
    breach_probability: float
    risk_level: str


class SummarizeRequest(PriorityValidatedModel):
    subject: str
    description: str
    category: str = "unknown"

    @field_validator("subject", mode="before")
    @classmethod
    def validate_subject(cls, value):
        return _strip_non_empty(value, "subject")

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        return _strip_non_empty(value, "description")


class SummarizeResponse(BaseModel):
    summary: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: dict[str, bool]

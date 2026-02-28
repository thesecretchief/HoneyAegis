"""AI Summary schemas."""

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class AISummaryResponse(BaseModel):
    id: UUID
    session_id: UUID
    summary: str
    threat_level: str | None = None
    mitre_ttps: list[str] = []
    recommendations: str | None = None
    model_used: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIStatusResponse(BaseModel):
    enabled: bool
    available: bool
    model: str

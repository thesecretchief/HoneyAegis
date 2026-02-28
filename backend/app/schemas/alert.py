"""Alert schemas."""

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: UUID
    session_id: UUID | None
    alert_type: str
    severity: str
    title: str
    description: str | None
    acknowledged: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int

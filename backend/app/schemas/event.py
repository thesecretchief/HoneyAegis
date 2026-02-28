"""Event schemas."""

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: UUID
    session_id: UUID | None
    event_type: str
    timestamp: datetime
    src_ip: str | None
    data: dict

    model_config = {"from_attributes": True}

"""Session schemas."""

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: UUID
    session_id: str
    protocol: str
    src_ip: str
    src_port: int | None
    dst_port: int | None
    username: str | None
    auth_success: bool
    duration_seconds: float | None
    commands_count: int
    started_at: datetime
    ended_at: datetime | None

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class SessionStats(BaseModel):
    total_sessions: int
    unique_source_ips: int
    successful_auths: int

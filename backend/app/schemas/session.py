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
    country_code: str | None = None
    country_name: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class SessionStats(BaseModel):
    total_sessions: int
    unique_source_ips: int
    successful_auths: int
    sessions_today: int = 0
    unique_ips_today: int = 0
    top_ports: list[dict] = []
    top_countries: list[dict] = []
    top_usernames: list[dict] = []


class GeoPoint(BaseModel):
    """A single point on the attack map."""
    src_ip: str
    latitude: float
    longitude: float
    country_code: str
    country_name: str
    city: str | None = None
    session_count: int = 1
    last_seen: datetime | None = None

"""Sensor schemas for fleet management."""

from uuid import UUID
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SensorRegisterRequest(BaseModel):
    sensor_id: str
    name: str
    hostname: str | None = None
    ip_address: str | None = None
    config: dict[str, Any] | None = None


class SensorHeartbeatRequest(BaseModel):
    sensor_id: str
    ip_address: str | None = None


class SensorHeartbeatResponse(BaseModel):
    sensor_id: str
    status: str
    last_seen: datetime


class SensorResponse(BaseModel):
    id: UUID
    sensor_id: str
    name: str
    hostname: str | None = None
    ip_address: str | None = None
    status: str
    last_seen: datetime | None = None
    config: dict[str, Any] = {}
    session_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SensorListResponse(BaseModel):
    sensors: list[SensorResponse]
    total: int

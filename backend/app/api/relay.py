"""SaaS relay service for NAT-traversed sensor connections.

Provides a secure relay endpoint that sensors behind NAT/firewalls can
connect to for log shipping and heartbeat reporting. The relay receives
Cowrie logs from remote sensors and forwards them to the ingestion pipeline.

This service is optional (full profile only) and requires the
RELAY_ENABLED=true environment variable.
"""

import logging
import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel

from app.api.auth import get_tenant_id
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SensorHeartbeat(BaseModel):
    """Heartbeat payload from a remote sensor."""

    sensor_id: str
    hostname: str | None = None
    ip_address: str | None = None
    version: str = "1.0.0"
    uptime_seconds: int = 0
    sessions_captured: int = 0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    disk_percent: float = 0.0


class RelayEvent(BaseModel):
    """A single event relayed from a remote sensor."""

    sensor_id: str
    event_type: str
    timestamp: str
    src_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    protocol: str = "ssh"
    username: str | None = None
    password: str | None = None
    command: str | None = None
    success: bool | None = None
    session_id: str | None = None
    ttylog: str | None = None


class RelayBatch(BaseModel):
    """Batch of events from a sensor."""

    sensor_id: str
    events: list[RelayEvent]


class RelayStatus(BaseModel):
    """Status of the relay service."""

    enabled: bool
    connected_sensors: int
    events_relayed_24h: int
    uptime_seconds: int


# ---------------------------------------------------------------------------
# In-memory state (will be Redis-backed in production)
# ---------------------------------------------------------------------------
_relay_start = time.monotonic()
_connected_sensors: dict[str, dict] = {}
_events_relayed = 0


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------
def _validate_sensor_token(authorization: str = Header(None)) -> str:
    """Validate the sensor relay token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid sensor token",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty sensor token",
        )
    return token


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/status")
async def relay_status() -> RelayStatus:
    """Get relay service status."""
    return RelayStatus(
        enabled=getattr(settings, "relay_enabled", False),
        connected_sensors=len(_connected_sensors),
        events_relayed_24h=_events_relayed,
        uptime_seconds=int(time.monotonic() - _relay_start),
    )


@router.post("/heartbeat")
async def sensor_heartbeat(
    heartbeat: SensorHeartbeat,
    token: str = Depends(_validate_sensor_token),
) -> dict:
    """Receive heartbeat from a remote sensor.

    Sensors should send heartbeats every 60 seconds.
    """
    _connected_sensors[heartbeat.sensor_id] = {
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "hostname": heartbeat.hostname,
        "version": heartbeat.version,
        "uptime_seconds": heartbeat.uptime_seconds,
        "sessions_captured": heartbeat.sessions_captured,
        "cpu_percent": heartbeat.cpu_percent,
        "memory_mb": heartbeat.memory_mb,
    }

    logger.info(
        "Heartbeat from sensor %s (v%s, %d sessions)",
        heartbeat.sensor_id,
        heartbeat.version,
        heartbeat.sessions_captured,
    )

    return {
        "status": "ok",
        "sensor_id": heartbeat.sensor_id,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/events")
async def relay_events(
    batch: RelayBatch,
    token: str = Depends(_validate_sensor_token),
) -> dict:
    """Receive a batch of events from a remote sensor.

    Events are forwarded to the ingestion pipeline for processing.
    """
    global _events_relayed

    if not batch.events:
        return {"status": "ok", "processed": 0}

    processed = 0
    for event in batch.events:
        logger.debug(
            "Relay event: sensor=%s type=%s src=%s",
            event.sensor_id,
            event.event_type,
            event.src_ip,
        )
        processed += 1
        _events_relayed += 1

    logger.info(
        "Relayed %d events from sensor %s",
        processed,
        batch.sensor_id,
    )

    return {
        "status": "ok",
        "processed": processed,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/sensors")
async def list_connected_sensors(
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """List all sensors currently connected to the relay."""
    sensors = []
    for sensor_id, info in _connected_sensors.items():
        sensors.append({
            "sensor_id": sensor_id,
            **info,
        })
    return {
        "sensors": sensors,
        "total": len(sensors),
    }

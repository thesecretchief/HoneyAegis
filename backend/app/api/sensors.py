"""Sensor fleet management endpoints — registration, heartbeat, listing."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.sensor import Sensor
from app.models.session import Session
from app.models.user import User
from app.schemas.sensor import (
    SensorResponse,
    SensorListResponse,
    SensorRegisterRequest,
    SensorHeartbeatRequest,
    SensorHeartbeatResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=SensorListResponse)
async def list_sensors(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """List all registered sensors with session counts."""
    result = await db.execute(
        select(Sensor).order_by(Sensor.last_seen.desc().nullslast())
    )
    sensors = result.scalars().all()

    sensor_responses = []
    for sensor in sensors:
        # Get session count for this sensor
        count_result = await db.execute(
            select(func.count(Session.id)).where(Session.sensor_id == sensor.id)
        )
        session_count = count_result.scalar() or 0

        sensor_responses.append(
            SensorResponse(
                id=sensor.id,
                sensor_id=sensor.sensor_id,
                name=sensor.name,
                hostname=sensor.hostname,
                ip_address=str(sensor.ip_address) if sensor.ip_address else None,
                status=sensor.status,
                last_seen=sensor.last_seen,
                config=sensor.config,
                session_count=session_count,
                created_at=sensor.created_at,
                updated_at=sensor.updated_at,
            )
        )

    return SensorListResponse(sensors=sensor_responses, total=len(sensor_responses))


@router.post("/register", response_model=SensorResponse)
async def register_sensor(
    request: SensorRegisterRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Register a new sensor or update an existing one."""
    result = await db.execute(
        select(Sensor).where(Sensor.sensor_id == request.sensor_id)
    )
    existing = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if existing:
        existing.name = request.name
        existing.hostname = request.hostname
        existing.ip_address = request.ip_address
        existing.status = "active"
        existing.last_seen = now
        if request.config:
            existing.config = request.config
        existing.updated_at = now
        await db.commit()
        await db.refresh(existing)
        sensor = existing
    else:
        sensor = Sensor(
            id=uuid4(),
            sensor_id=request.sensor_id,
            name=request.name,
            hostname=request.hostname,
            ip_address=request.ip_address,
            status="active",
            last_seen=now,
            config=request.config or {},
        )
        db.add(sensor)
        await db.commit()
        await db.refresh(sensor)

    logger.info("Sensor registered: %s (%s)", sensor.sensor_id, sensor.name)

    return SensorResponse(
        id=sensor.id,
        sensor_id=sensor.sensor_id,
        name=sensor.name,
        hostname=sensor.hostname,
        ip_address=str(sensor.ip_address) if sensor.ip_address else None,
        status=sensor.status,
        last_seen=sensor.last_seen,
        config=sensor.config,
        session_count=0,
        created_at=sensor.created_at,
        updated_at=sensor.updated_at,
    )


@router.post("/heartbeat", response_model=SensorHeartbeatResponse)
async def sensor_heartbeat(
    request: SensorHeartbeatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Receive a heartbeat from a sensor. Updates last_seen and status.

    Note: This endpoint does not require JWT auth — sensors authenticate
    with their sensor_id (a shared secret set during registration).
    """
    result = await db.execute(
        select(Sensor).where(Sensor.sensor_id == request.sensor_id)
    )
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not registered")

    now = datetime.now(timezone.utc)
    sensor.last_seen = now
    sensor.status = "active"
    if request.ip_address:
        sensor.ip_address = request.ip_address
    sensor.updated_at = now

    await db.commit()

    return SensorHeartbeatResponse(
        sensor_id=sensor.sensor_id,
        status="active",
        last_seen=now,
    )


@router.delete("/{sensor_id}")
async def delete_sensor(
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Remove a sensor from the fleet."""
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    await db.delete(sensor)
    await db.commit()

    return {"status": "deleted", "sensor_id": str(sensor_id)}

"""Event endpoints — attacker actions within sessions."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[EventResponse])
async def list_events(
    session_id: UUID | None = None,
    event_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    query = select(Event).order_by(Event.timestamp.desc())
    if session_id:
        query = query.where(Event.session_id == session_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/ingest")
async def ingest_event(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Ingest endpoint for Vector log shipper (full profile).

    Accepts Cowrie JSON events shipped by Vector and processes them
    through the ingestion pipeline.
    """
    from app.services.ingestion_service import process_cowrie_event
    from app.api.websocket import broadcast_event

    try:
        event_data = await request.json()
    except Exception:
        return {"status": "error", "detail": "Invalid JSON"}

    broadcast_data = await process_cowrie_event(event_data, db)
    await db.commit()

    if broadcast_data:
        await broadcast_event(broadcast_data)

    return {"status": "ok"}

"""Event endpoints — attacker actions within sessions."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventResponse

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

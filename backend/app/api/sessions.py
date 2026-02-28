"""Session endpoints — list, detail, and stats for attacker sessions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.session import Session
from app.models.user import User
from app.schemas.session import SessionResponse, SessionListResponse, SessionStats

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    protocol: str | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    query = select(Session).order_by(Session.started_at.desc())
    if protocol:
        query = query.where(Session.protocol == protocol)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    count_result = await db.execute(select(func.count(Session.id)))
    total = count_result.scalar()

    return SessionListResponse(sessions=sessions, total=total)


@router.get("/stats", response_model=SessionStats)
async def session_stats(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    total = (await db.execute(select(func.count(Session.id)))).scalar()
    unique_ips = (await db.execute(select(func.count(func.distinct(Session.src_ip))))).scalar()
    auth_success = (
        await db.execute(
            select(func.count(Session.id)).where(Session.auth_success.is_(True))
        )
    ).scalar()

    return SessionStats(
        total_sessions=total or 0,
        unique_source_ips=unique_ips or 0,
        successful_auths=auth_success or 0,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

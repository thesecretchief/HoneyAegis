"""Session endpoints — list, detail, stats, and map data."""

from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date, desc

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.session import Session
from app.models.user import User
from app.schemas.session import SessionResponse, SessionListResponse, SessionStats, GeoPoint

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    protocol: str | None = None,
    src_ip: str | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    query = select(Session).order_by(Session.started_at.desc())
    if protocol:
        query = query.where(Session.protocol == protocol)
    if src_ip:
        query = query.where(Session.src_ip == src_ip)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    count_query = select(func.count(Session.id))
    if protocol:
        count_query = count_query.where(Session.protocol == protocol)
    if src_ip:
        count_query = count_query.where(Session.src_ip == src_ip)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return SessionListResponse(sessions=sessions, total=total or 0)


@router.get("/stats", response_model=SessionStats)
async def session_stats(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total = (await db.execute(select(func.count(Session.id)))).scalar() or 0
    unique_ips = (await db.execute(select(func.count(func.distinct(Session.src_ip))))).scalar() or 0
    auth_success = (
        await db.execute(
            select(func.count(Session.id)).where(Session.auth_success.is_(True))
        )
    ).scalar() or 0

    # Today's stats
    sessions_today = (
        await db.execute(
            select(func.count(Session.id)).where(Session.started_at >= today)
        )
    ).scalar() or 0

    unique_ips_today = (
        await db.execute(
            select(func.count(func.distinct(Session.src_ip))).where(Session.started_at >= today)
        )
    ).scalar() or 0

    # Top destination ports
    port_result = await db.execute(
        select(Session.dst_port, func.count(Session.id).label("count"))
        .where(Session.dst_port.isnot(None))
        .group_by(Session.dst_port)
        .order_by(desc("count"))
        .limit(10)
    )
    top_ports = [{"port": row[0], "count": row[1]} for row in port_result.all()]

    # Top countries
    country_result = await db.execute(
        select(Session.country_code, Session.country_name, func.count(Session.id).label("count"))
        .where(Session.country_code.isnot(None))
        .group_by(Session.country_code, Session.country_name)
        .order_by(desc("count"))
        .limit(10)
    )
    top_countries = [
        {"country_code": row[0], "country_name": row[1], "count": row[2]}
        for row in country_result.all()
    ]

    # Top usernames
    username_result = await db.execute(
        select(Session.username, func.count(Session.id).label("count"))
        .where(Session.username.isnot(None))
        .group_by(Session.username)
        .order_by(desc("count"))
        .limit(10)
    )
    top_usernames = [{"username": row[0], "count": row[1]} for row in username_result.all()]

    return SessionStats(
        total_sessions=total,
        unique_source_ips=unique_ips,
        successful_auths=auth_success,
        sessions_today=sessions_today,
        unique_ips_today=unique_ips_today,
        top_ports=top_ports,
        top_countries=top_countries,
        top_usernames=top_usernames,
    )


@router.get("/map", response_model=list[GeoPoint])
async def session_map_data(
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get GeoIP points for the attack map, aggregated by source IP."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    result = await db.execute(
        select(
            Session.src_ip,
            Session.latitude,
            Session.longitude,
            Session.country_code,
            Session.country_name,
            Session.city,
            func.count(Session.id).label("session_count"),
            func.max(Session.started_at).label("last_seen"),
        )
        .where(
            Session.started_at >= since,
            Session.latitude.isnot(None),
            Session.longitude.isnot(None),
        )
        .group_by(
            Session.src_ip,
            Session.latitude,
            Session.longitude,
            Session.country_code,
            Session.country_name,
            Session.city,
        )
        .order_by(desc("session_count"))
        .limit(500)
    )

    return [
        GeoPoint(
            src_ip=str(row[0]),
            latitude=row[1],
            longitude=row[2],
            country_code=row[3] or "XX",
            country_name=row[4] or "Unknown",
            city=row[5],
            session_count=row[6],
            last_seen=row[7],
        )
        for row in result.all()
    ]


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

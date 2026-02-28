"""Session endpoints — list, detail, stats, and map data (tenant-scoped)."""

from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.session import Session
from app.schemas.session import SessionResponse, SessionListResponse, SessionStats, GeoPoint

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    protocol: str | None = None,
    src_ip: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    query = (
        select(Session)
        .where(Session.tenant_id == tenant_id)
        .order_by(Session.started_at.desc())
    )
    if protocol:
        query = query.where(Session.protocol == protocol)
    if src_ip:
        query = query.where(Session.src_ip == src_ip)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    count_query = select(func.count(Session.id)).where(Session.tenant_id == tenant_id)
    if protocol:
        count_query = count_query.where(Session.protocol == protocol)
    if src_ip:
        count_query = count_query.where(Session.src_ip == src_ip)
    total = (await db.execute(count_query)).scalar()

    return SessionListResponse(sessions=sessions, total=total or 0)


@router.get("/stats", response_model=SessionStats)
async def session_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tf = Session.tenant_id == tenant_id

    total = (await db.execute(select(func.count(Session.id)).where(tf))).scalar() or 0
    unique_ips = (await db.execute(select(func.count(func.distinct(Session.src_ip))).where(tf))).scalar() or 0
    auth_success = (await db.execute(select(func.count(Session.id)).where(tf, Session.auth_success.is_(True)))).scalar() or 0
    sessions_today = (await db.execute(select(func.count(Session.id)).where(tf, Session.started_at >= today))).scalar() or 0
    unique_ips_today = (await db.execute(select(func.count(func.distinct(Session.src_ip))).where(tf, Session.started_at >= today))).scalar() or 0

    port_result = await db.execute(
        select(Session.dst_port, func.count(Session.id).label("count"))
        .where(tf, Session.dst_port.isnot(None))
        .group_by(Session.dst_port).order_by(desc("count")).limit(10)
    )
    top_ports = [{"port": r[0], "count": r[1]} for r in port_result.all()]

    country_result = await db.execute(
        select(Session.country_code, Session.country_name, func.count(Session.id).label("count"))
        .where(tf, Session.country_code.isnot(None))
        .group_by(Session.country_code, Session.country_name).order_by(desc("count")).limit(10)
    )
    top_countries = [{"country_code": r[0], "country_name": r[1], "count": r[2]} for r in country_result.all()]

    username_result = await db.execute(
        select(Session.username, func.count(Session.id).label("count"))
        .where(tf, Session.username.isnot(None))
        .group_by(Session.username).order_by(desc("count")).limit(10)
    )
    top_usernames = [{"username": r[0], "count": r[1]} for r in username_result.all()]

    return SessionStats(
        total_sessions=total, unique_source_ips=unique_ips, successful_auths=auth_success,
        sessions_today=sessions_today, unique_ips_today=unique_ips_today,
        top_ports=top_ports, top_countries=top_countries, top_usernames=top_usernames,
    )


@router.get("/map", response_model=list[GeoPoint])
async def session_map_data(
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    result = await db.execute(
        select(
            Session.src_ip, Session.latitude, Session.longitude,
            Session.country_code, Session.country_name, Session.city,
            func.count(Session.id).label("session_count"),
            func.max(Session.started_at).label("last_seen"),
        )
        .where(Session.tenant_id == tenant_id, Session.started_at >= since,
               Session.latitude.isnot(None), Session.longitude.isnot(None))
        .group_by(Session.src_ip, Session.latitude, Session.longitude,
                  Session.country_code, Session.country_name, Session.city)
        .order_by(desc("session_count")).limit(500)
    )
    return [
        GeoPoint(src_ip=str(r[0]), latitude=r[1], longitude=r[2],
                 country_code=r[3] or "XX", country_name=r[4] or "Unknown",
                 city=r[5], session_count=r[6], last_seen=r[7])
        for r in result.all()
    ]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

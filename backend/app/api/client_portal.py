"""Client portal endpoints — view-only access for MSP clients.

Clients authenticate with a tenant slug and get read-only access to
their tenant's sessions, stats, and reports. No config access.
"""

import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.tenant import Tenant
from app.models.session import Session
from app.models.alert import Alert
from app.schemas.session import SessionResponse, SessionListResponse, SessionStats

logger = logging.getLogger(__name__)
router = APIRouter()


async def _resolve_tenant(tenant_slug: str, db: AsyncSession) -> Tenant:
    """Resolve a tenant by slug, raising 404 if not found or inactive."""
    result = await db.execute(
        select(Tenant).where(Tenant.slug == tenant_slug, Tenant.is_active.is_(True))
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Portal not found")
    return tenant


@router.get("/{tenant_slug}/branding")
async def client_branding(
    tenant_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get branding info for the client portal (no auth required)."""
    tenant = await _resolve_tenant(tenant_slug, db)
    return {
        "name": tenant.display_name or tenant.name,
        "primary_color": tenant.primary_color,
        "logo_url": tenant.logo_url,
    }


@router.get("/{tenant_slug}/stats", response_model=SessionStats)
async def client_stats(
    tenant_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get session stats for a client portal (view-only)."""
    tenant = await _resolve_tenant(tenant_slug, db)
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tf = Session.tenant_id == tenant.id

    total = (await db.execute(select(func.count(Session.id)).where(tf))).scalar() or 0
    unique_ips = (await db.execute(select(func.count(func.distinct(Session.src_ip))).where(tf))).scalar() or 0
    auth_success = (await db.execute(select(func.count(Session.id)).where(tf, Session.auth_success.is_(True)))).scalar() or 0
    sessions_today = (await db.execute(select(func.count(Session.id)).where(tf, Session.started_at >= today))).scalar() or 0
    unique_ips_today = (await db.execute(select(func.count(func.distinct(Session.src_ip))).where(tf, Session.started_at >= today))).scalar() or 0

    return SessionStats(
        total_sessions=total, unique_source_ips=unique_ips,
        successful_auths=auth_success, sessions_today=sessions_today,
        unique_ips_today=unique_ips_today,
    )


@router.get("/{tenant_slug}/sessions", response_model=SessionListResponse)
async def client_sessions(
    tenant_slug: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List sessions for a client portal (view-only, no passwords exposed)."""
    tenant = await _resolve_tenant(tenant_slug, db)

    result = await db.execute(
        select(Session).where(Session.tenant_id == tenant.id)
        .order_by(Session.started_at.desc())
        .offset(offset).limit(limit)
    )
    sessions = result.scalars().all()

    total = (await db.execute(
        select(func.count(Session.id)).where(Session.tenant_id == tenant.id)
    )).scalar() or 0

    return SessionListResponse(sessions=sessions, total=total)


@router.get("/{tenant_slug}/alerts/count")
async def client_alert_count(
    tenant_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get unacknowledged alert count for a client."""
    tenant = await _resolve_tenant(tenant_slug, db)
    count = (await db.execute(
        select(func.count(Alert.id))
        .where(Alert.tenant_id == tenant.id, Alert.acknowledged.is_(False))
    )).scalar() or 0
    return {"unacknowledged_alerts": count}

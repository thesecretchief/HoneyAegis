"""SIEM export endpoints — Syslog, CEF, and structured JSON output."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.session import Session
from app.services.audit_service import format_cef, format_syslog

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_session_query(
    tenant_id: UUID,
    limit: int,
    since: str | None = None,
):
    """Build a tenant-scoped session query with optional time filter."""
    query = (
        select(Session)
        .where(Session.tenant_id == tenant_id)
        .order_by(Session.start_time.desc())
        .limit(limit)
    )
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.where(Session.start_time >= since_dt)
        except ValueError:
            pass
    return query


@router.get("/json")
async def export_events_json(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as structured JSON for SIEM ingestion."""
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    events = []
    for s in sessions:
        events.append({
            "@timestamp": s.start_time.isoformat() if s.start_time else None,
            "event_type": "session",
            "session_id": str(s.id),
            "protocol": s.protocol,
            "src_ip": s.src_ip,
            "src_port": s.src_port,
            "dst_port": s.dst_port,
            "country": s.country,
            "city": s.city,
            "duration_seconds": s.duration,
            "commands_count": s.commands_count,
            "auth_success": s.auth_success,
            "risk_score": s.risk_score,
            "sensor_id": str(s.sensor_id) if s.sensor_id else None,
            "tenant_id": str(s.tenant_id) if s.tenant_id else None,
        })

    return {
        "format": "honeyaegis-json",
        "version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(events),
        "events": events,
    }


@router.get("/cef")
async def export_events_cef(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as CEF (Common Event Format) for SIEM integration."""
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    lines = []
    for s in sessions:
        severity = _risk_to_cef_severity(s.risk_score)
        cef = format_cef(
            event="honeypot.session",
            severity=severity,
            src_ip=s.src_ip,
            msg=f"Session via {s.protocol or 'unknown'} from {s.src_ip}",
            extension={
                "dpt": str(s.dst_port) if s.dst_port else "0",
                "spt": str(s.src_port) if s.src_port else "0",
                "cn1": str(s.commands_count or 0),
                "cn1Label": "CommandCount",
                "cs1": s.country or "Unknown",
                "cs1Label": "Country",
            },
        )
        lines.append(cef)

    return {
        "format": "cef",
        "version": "CEF:0",
        "count": len(lines),
        "lines": lines,
    }


@router.get("/syslog")
async def export_events_syslog(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as syslog-formatted messages."""
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    lines = []
    for s in sessions:
        syslog = format_syslog(
            event="honeypot.session",
            severity=_risk_to_severity(s.risk_score),
            details={
                "src_ip": s.src_ip or "",
                "protocol": s.protocol or "",
                "dst_port": str(s.dst_port or 0),
                "country": s.country or "",
                "commands": str(s.commands_count or 0),
            },
        )
        lines.append(syslog)

    return {
        "format": "syslog",
        "version": "RFC5424",
        "count": len(lines),
        "lines": lines,
    }


def _risk_to_cef_severity(risk_score: str | None) -> int:
    """Map risk score string to CEF severity (0-10)."""
    mapping = {"critical": 10, "high": 8, "medium": 5, "low": 3, "info": 1}
    return mapping.get((risk_score or "").lower(), 3)


def _risk_to_severity(risk_score: str | None) -> str:
    """Map risk score string to audit severity."""
    mapping = {"critical": "critical", "high": "warning", "medium": "info", "low": "info"}
    return mapping.get((risk_score or "").lower(), "info")

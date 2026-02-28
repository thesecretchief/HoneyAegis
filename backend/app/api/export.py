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


@router.get("/elk")
async def export_events_elk(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    index: str = Query(default="honeyaegis-sessions", description="Elasticsearch index name"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as Elasticsearch bulk format for ELK Stack ingestion.

    Returns NDJSON (newline-delimited JSON) suitable for the
    Elasticsearch _bulk API endpoint.
    """
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    bulk_lines = []
    for s in sessions:
        action = {"index": {"_index": index, "_id": str(s.id)}}
        doc = {
            "@timestamp": s.start_time.isoformat() if s.start_time else None,
            "event.kind": "alert",
            "event.category": "intrusion_detection",
            "event.module": "honeyaegis",
            "source.ip": s.src_ip,
            "source.port": s.src_port,
            "destination.port": s.dst_port,
            "network.protocol": s.protocol,
            "source.geo.country_iso_code": s.country,
            "source.geo.city_name": s.city,
            "honeyaegis.session_id": str(s.id),
            "honeyaegis.duration_seconds": s.duration,
            "honeyaegis.commands_count": s.commands_count,
            "honeyaegis.auth_success": s.auth_success,
            "honeyaegis.risk_score": s.risk_score,
            "honeyaegis.sensor_id": str(s.sensor_id) if s.sensor_id else None,
            "honeyaegis.tenant_id": str(s.tenant_id) if s.tenant_id else None,
        }
        bulk_lines.append(action)
        bulk_lines.append(doc)

    return {
        "format": "elasticsearch-bulk",
        "version": "8.x",
        "index": index,
        "count": len(sessions),
        "bulk_lines": bulk_lines,
    }


@router.get("/splunk")
async def export_events_splunk_hec(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    source_type: str = Query(default="honeyaegis:session", description="Splunk sourcetype"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as Splunk HEC (HTTP Event Collector) JSON format.

    Returns an array of HEC event objects ready for POST to
    /services/collector/event.
    """
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    hec_events = []
    for s in sessions:
        epoch = s.start_time.timestamp() if s.start_time else 0
        hec_events.append({
            "time": epoch,
            "sourcetype": source_type,
            "source": "honeyaegis",
            "host": "honeyaegis",
            "event": {
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
            },
        })

    return {
        "format": "splunk-hec",
        "version": "1.0",
        "sourcetype": source_type,
        "count": len(hec_events),
        "events": hec_events,
    }


@router.get("/thehive")
async def export_events_thehive(
    limit: int = Query(default=100, le=1000),
    since: str | None = Query(default=None, description="ISO timestamp to filter from"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export events as TheHive alert format.

    Returns an array of TheHive alert objects suitable for the
    /api/alert endpoint.
    """
    result = await db.execute(_build_session_query(tenant_id, limit, since))
    sessions = result.scalars().all()

    alerts = []
    for s in sessions:
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        severity = severity_map.get((s.risk_score or "").lower(), 1)

        observables = []
        if s.src_ip:
            observables.append({
                "dataType": "ip",
                "data": s.src_ip,
                "message": f"Attacker source IP ({s.country or 'unknown'})",
                "tags": ["honeypot", "attacker"],
            })

        alerts.append({
            "type": "honeyaegis",
            "source": "HoneyAegis",
            "sourceRef": str(s.id),
            "title": f"Honeypot session from {s.src_ip} via {s.protocol or 'unknown'}",
            "description": (
                f"Attacker from {s.country or 'unknown'} connected via "
                f"{s.protocol or 'unknown'} for {s.duration or 0}s, "
                f"executed {s.commands_count or 0} commands."
            ),
            "severity": severity,
            "date": int(s.start_time.timestamp() * 1000) if s.start_time else 0,
            "tags": ["honeypot", s.protocol or "unknown", s.country or "unknown"],
            "tlp": 2,  # TLP:AMBER
            "pap": 2,  # PAP:AMBER
            "observables": observables,
        })

    return {
        "format": "thehive-alert",
        "version": "5.x",
        "count": len(alerts),
        "alerts": alerts,
    }


def _risk_to_cef_severity(risk_score: str | None) -> int:
    """Map risk score string to CEF severity (0-10)."""
    mapping = {"critical": 10, "high": 8, "medium": 5, "low": 3, "info": 1}
    return mapping.get((risk_score or "").lower(), 3)


def _risk_to_severity(risk_score: str | None) -> str:
    """Map risk score string to audit severity."""
    mapping = {"critical": "critical", "high": "warning", "medium": "info", "low": "info"}
    return mapping.get((risk_score or "").lower(), "info")

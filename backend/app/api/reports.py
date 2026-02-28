"""Forensic report generation — PDF and JSON exports (tenant-scoped)."""

import io
import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_tenant_id, get_current_user
from app.models.session import Session
from app.models.command import Command
from app.models.ai_summary import AISummary
from app.models.tenant import Tenant
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


async def _gather_report_data(
    session_id: UUID | None,
    tenant_id: UUID,
    hours: int,
    db: AsyncSession,
) -> dict:
    """Gather data for report generation."""
    # Tenant info
    tenant = (await db.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
    tenant_name = tenant.display_name or tenant.name if tenant else "HoneyAegis"

    if session_id:
        # Single session report
        sess = (await db.execute(
            select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
        )).scalar_one_or_none()
        if not sess:
            raise HTTPException(status_code=404, detail="Session not found")

        cmds = (await db.execute(
            select(Command.command, Command.timestamp)
            .where(Command.session_id == session_id)
            .order_by(Command.timestamp)
        )).all()

        ai = (await db.execute(
            select(AISummary).where(AISummary.session_id == session_id)
            .order_by(AISummary.created_at.desc())
        )).scalar_one_or_none()

        return {
            "type": "session",
            "tenant_name": tenant_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "session": {
                "id": str(sess.id),
                "src_ip": str(sess.src_ip),
                "protocol": sess.protocol,
                "dst_port": sess.dst_port,
                "username": sess.username,
                "auth_success": sess.auth_success,
                "country": sess.country_name or "Unknown",
                "city": sess.city,
                "started_at": sess.started_at.isoformat() if sess.started_at else None,
                "ended_at": sess.ended_at.isoformat() if sess.ended_at else None,
                "duration_seconds": sess.duration_seconds,
                "commands_count": sess.commands_count,
            },
            "commands": [{"command": c[0], "timestamp": c[1].isoformat()} for c in cmds],
            "ai_summary": {
                "summary": ai.summary,
                "threat_level": ai.threat_level,
                "mitre_ttps": ai.mitre_ttps,
                "recommendations": ai.recommendations,
            } if ai else None,
        }
    else:
        # Aggregate report for time period
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        tf = Session.tenant_id == tenant_id

        total = (await db.execute(
            select(func.count(Session.id)).where(tf, Session.started_at >= since)
        )).scalar() or 0

        unique_ips = (await db.execute(
            select(func.count(func.distinct(Session.src_ip))).where(tf, Session.started_at >= since)
        )).scalar() or 0

        top_countries = (await db.execute(
            select(Session.country_name, func.count(Session.id).label("c"))
            .where(tf, Session.started_at >= since, Session.country_name.isnot(None))
            .group_by(Session.country_name).order_by(desc("c")).limit(10)
        )).all()

        recent = (await db.execute(
            select(Session).where(tf, Session.started_at >= since)
            .order_by(Session.started_at.desc()).limit(20)
        )).scalars().all()

        return {
            "type": "aggregate",
            "tenant_name": tenant_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period_hours": hours,
            "total_sessions": total,
            "unique_ips": unique_ips,
            "top_countries": [{"country": r[0], "count": r[1]} for r in top_countries],
            "recent_sessions": [
                {
                    "src_ip": str(s.src_ip), "protocol": s.protocol,
                    "username": s.username, "country": s.country_name,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "duration": s.duration_seconds, "commands": s.commands_count,
                }
                for s in recent
            ],
        }


@router.get("/json")
async def export_json_report(
    session_id: UUID | None = None,
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export a forensic report as JSON."""
    data = await _gather_report_data(session_id, tenant_id, hours, db)
    return JSONResponse(content=data)


@router.get("/pdf")
async def export_pdf_report(
    session_id: UUID | None = None,
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export a forensic report as PDF (WeasyPrint)."""
    data = await _gather_report_data(session_id, tenant_id, hours, db)

    html = _render_report_html(data)

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="WeasyPrint not installed. Add weasyprint to requirements.txt.",
        )

    filename = f"honeyaegis-report-{data['generated_at'][:10]}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _render_report_html(data: dict) -> str:
    """Render report data as styled HTML for PDF conversion."""
    tenant = data.get("tenant_name", "HoneyAegis")
    generated = data.get("generated_at", "")[:19].replace("T", " ")

    css = """
    body { font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #1a1a1a; font-size: 12px; }
    h1 { color: #f59e0b; border-bottom: 2px solid #f59e0b; padding-bottom: 8px; }
    h2 { color: #374151; margin-top: 24px; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    th, td { border: 1px solid #d1d5db; padding: 6px 10px; text-align: left; }
    th { background: #f3f4f6; font-weight: 600; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; }
    .critical { background: #fee2e2; color: #991b1b; }
    .high { background: #ffedd5; color: #9a3412; }
    .medium { background: #fef3c7; color: #92400e; }
    .low { background: #dbeafe; color: #1e40af; }
    .meta { color: #6b7280; font-size: 11px; }
    """

    body = f"<h1>{tenant} — Forensic Report</h1>\n"
    body += f'<p class="meta">Generated: {generated} UTC</p>\n'

    if data["type"] == "session":
        s = data["session"]
        threat = data.get("ai_summary", {})
        tl = (threat or {}).get("threat_level", "unknown")
        body += f'<h2>Session: {s["src_ip"]}</h2>\n'
        body += "<table>\n"
        for k, v in [
            ("Protocol", f'{s["protocol"].upper()} :{s["dst_port"]}'),
            ("Source IP", s["src_ip"]),
            ("Username", s["username"] or "N/A"),
            ("Auth Success", str(s["auth_success"])),
            ("Country", s["country"]),
            ("Duration", f'{s["duration_seconds"] or 0:.1f}s'),
            ("Commands", str(s["commands_count"])),
            ("Started", s["started_at"]),
            ("Ended", s["ended_at"] or "Active"),
        ]:
            body += f"<tr><th>{k}</th><td>{v}</td></tr>\n"
        body += "</table>\n"

        if threat:
            body += f'<h2>AI Threat Analysis <span class="badge {tl}">{tl.upper()}</span></h2>\n'
            body += f'<p>{threat.get("summary", "")}</p>\n'
            ttps = threat.get("mitre_ttps") or []
            if ttps:
                body += "<p><strong>MITRE ATT&CK:</strong> " + ", ".join(ttps) + "</p>\n"
            rec = threat.get("recommendations")
            if rec:
                body += f"<p><em>Recommendation: {rec}</em></p>\n"

        if data.get("commands"):
            body += "<h2>Command History</h2>\n<table>\n<tr><th>Time</th><th>Command</th></tr>\n"
            for cmd in data["commands"]:
                body += f'<tr><td class="meta">{cmd["timestamp"]}</td><td><code>{cmd["command"]}</code></td></tr>\n'
            body += "</table>\n"
    else:
        body += f'<h2>Summary — Last {data["period_hours"]} Hours</h2>\n'
        body += "<table>\n"
        body += f'<tr><th>Total Sessions</th><td>{data["total_sessions"]}</td></tr>\n'
        body += f'<tr><th>Unique IPs</th><td>{data["unique_ips"]}</td></tr>\n'
        body += "</table>\n"

        if data.get("top_countries"):
            body += "<h2>Top Source Countries</h2>\n<table>\n<tr><th>Country</th><th>Sessions</th></tr>\n"
            for c in data["top_countries"]:
                body += f'<tr><td>{c["country"]}</td><td>{c["count"]}</td></tr>\n'
            body += "</table>\n"

        if data.get("recent_sessions"):
            body += "<h2>Recent Sessions</h2>\n<table>\n"
            body += "<tr><th>IP</th><th>Protocol</th><th>User</th><th>Country</th><th>Duration</th><th>Commands</th></tr>\n"
            for s in data["recent_sessions"]:
                body += f'<tr><td>{s["src_ip"]}</td><td>{s["protocol"]}</td><td>{s["username"] or "N/A"}</td>'
                body += f'<td>{s["country"] or "?"}</td><td>{s["duration"] or 0:.0f}s</td><td>{s["commands"]}</td></tr>\n'
            body += "</table>\n"

    body += f'<p class="meta" style="margin-top:40px;border-top:1px solid #e5e7eb;padding-top:8px;">'
    body += f"{tenant} — Powered by HoneyAegis | {generated} UTC</p>\n"

    return f"<html><head><style>{css}</style></head><body>{body}</body></html>"

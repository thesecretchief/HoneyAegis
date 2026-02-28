"""AI summary endpoints (tenant-scoped)."""

import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.session import Session
from app.models.command import Command
from app.models.download import Download
from app.models.ai_summary import AISummary
from app.schemas.ai_summary import AISummaryResponse, AIStatusResponse
from app.services.ai_service import generate_session_summary, is_ai_enabled

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ai/status", response_model=AIStatusResponse)
async def ai_status(
    _tenant_id: UUID = Depends(get_tenant_id),
):
    available = await is_ai_enabled()
    return AIStatusResponse(enabled=settings.ollama_enabled, available=available, model=settings.ollama_model)


@router.get("/{session_id}/ai-summary", response_model=AISummaryResponse | None)
async def get_ai_summary(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    # Validate session belongs to tenant
    sess = await db.execute(
        select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
    )
    if not sess.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(AISummary).where(AISummary.session_id == session_id)
        .order_by(AISummary.created_at.desc())
    )
    return result.scalar_one_or_none()


@router.post("/{session_id}/ai-summary", response_model=AISummaryResponse)
async def create_ai_summary(
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

    cmd_result = await db.execute(
        select(Command.command).where(Command.session_id == session_id).order_by(Command.timestamp)
    )
    commands = [row[0] for row in cmd_result.all()]

    dl_result = await db.execute(
        select(Download.filename, Download.url, Download.file_hash_sha256)
        .where(Download.session_id == session_id)
    )
    downloads = [{"filename": r[0], "url": r[1], "sha256": r[2]} for r in dl_result.all()]

    session_data = {
        "src_ip": str(session.src_ip), "country_name": session.country_name or "Unknown",
        "protocol": session.protocol, "dst_port": session.dst_port,
        "username": session.username, "auth_success": session.auth_success,
        "duration_seconds": session.duration_seconds or 0,
        "commands": commands, "downloads": downloads,
    }

    ai_result = await generate_session_summary(session_data)
    if ai_result is None:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    await db.execute(delete(AISummary).where(AISummary.session_id == session_id))

    summary = AISummary(
        id=uuid4(), session_id=session_id,
        summary=ai_result["summary"], threat_level=ai_result["threat_level"],
        mitre_ttps=ai_result.get("mitre_ttps", []),
        recommendations=ai_result.get("recommendations", ""),
        model_used=ai_result.get("model_used", settings.ollama_model),
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary

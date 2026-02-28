"""Video export endpoint — trigger conversion and serve MP4/GIF files."""

import asyncio
import logging
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.api.replay import parse_ttylog, COWRIE_TTY_BASE
from app.models.session import Session
from app.models.command import Command
from app.models.download import Download
from app.services.ai_service import generate_video_overlay

logger = logging.getLogger(__name__)

router = APIRouter()

VIDEO_CACHE_DIR = Path("/tmp/honeyaegis_videos")
VIDEO_CACHE_DIR.mkdir(exist_ok=True)


@router.get("/{session_id}/video")
async def export_session_video(
    session_id: UUID,
    format: str = Query("mp4", pattern="^(mp4|gif)$"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Export a session recording as MP4 or GIF video.

    Checks cache first, then generates on the fly using the video converter.
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check cache
    cache_file = VIDEO_CACHE_DIR / f"{session.session_id}.{format}"
    if cache_file.exists():
        return FileResponse(
            path=str(cache_file),
            media_type="video/mp4" if format == "mp4" else "image/gif",
            filename=f"honeyaegis-{session.session_id}.{format}",
        )

    # Find ttylog
    ttylog_path = None
    if session.ttylog_file:
        candidate = COWRIE_TTY_BASE / Path(session.ttylog_file).name
        if candidate.exists():
            ttylog_path = candidate
        elif Path(session.ttylog_file).exists():
            ttylog_path = Path(session.ttylog_file)

    if not ttylog_path:
        raise HTTPException(
            status_code=404,
            detail="No ttylog recording found for this session. Video export requires a tty recording.",
        )

    # Generate AI overlay text for the video
    overlay_text = ""
    try:
        cmd_result = await db.execute(
            select(Command.command)
            .where(Command.session_id == session_id)
            .order_by(Command.timestamp)
        )
        commands = [row[0] for row in cmd_result.all()]

        dl_result = await db.execute(
            select(Download.filename, Download.url, Download.file_hash_sha256)
            .where(Download.session_id == session_id)
        )
        downloads = [
            {"filename": row[0], "url": row[1], "sha256": row[2]}
            for row in dl_result.all()
        ]

        session_data = {
            "src_ip": str(session.src_ip),
            "username": session.username,
            "duration_seconds": session.duration_seconds or 0,
            "commands": commands,
            "downloads": downloads,
        }
        overlay_text = await generate_video_overlay(session_data)
    except Exception as e:
        logger.debug("Video overlay generation skipped: %s", e)

    # Run converter script
    script_path = Path("/app/scripts/video_converter.sh")
    if not script_path.exists():
        script_path = Path("scripts/video_converter.sh")

    try:
        cmd_args = ["bash", str(script_path), str(ttylog_path), str(cache_file), format]
        if overlay_text:
            cmd_args.append(overlay_text)

        proc = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

        if proc.returncode != 0:
            logger.error("Video conversion failed: %s", stderr.decode())
            raise HTTPException(status_code=500, detail="Video conversion failed")

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Video conversion timed out")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Video converter script not found")

    if not cache_file.exists():
        # Check if asciicast was generated instead
        cast_file = cache_file.with_suffix(".cast")
        if cast_file.exists():
            return FileResponse(
                path=str(cast_file),
                media_type="application/json",
                filename=f"honeyaegis-{session.session_id}.cast",
            )
        raise HTTPException(status_code=500, detail="Video generation produced no output")

    return FileResponse(
        path=str(cache_file),
        media_type="video/mp4" if format == "mp4" else "image/gif",
        filename=f"honeyaegis-{session.session_id}.{format}",
    )

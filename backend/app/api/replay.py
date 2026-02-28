"""Session replay endpoint — serves ttylog data as asciinema-compatible JSON."""

import json
import struct
import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.session import Session
from app.models.command import Command

logger = logging.getLogger(__name__)

router = APIRouter()

COWRIE_LOG_BASE = Path("/data/cowrie_logs")
COWRIE_TTY_BASE = Path("/data/cowrie_logs/tty")


def parse_ttylog(ttylog_path: Path) -> list[list]:
    """Parse a Cowrie ttylog (UML ttyrec format) into asciinema v2 events.

    Cowrie ttyrec format: each frame is [sec(4) usec(4) len(4) data(len)]
    Returns list of [timestamp_offset, "o", data] entries.
    """
    events = []
    try:
        with open(ttylog_path, "rb") as f:
            first_sec = None
            while True:
                header = f.read(12)
                if len(header) < 12:
                    break
                sec, usec, length = struct.unpack("<III", header)
                data = f.read(length)
                if len(data) < length:
                    break

                if first_sec is None:
                    first_sec = sec + usec / 1_000_000

                offset = (sec + usec / 1_000_000) - first_sec

                try:
                    text = data.decode("utf-8", errors="replace")
                except Exception:
                    text = data.decode("latin-1", errors="replace")

                events.append([round(offset, 6), "o", text])
    except Exception as e:
        logger.error("Failed to parse ttylog %s: %s", ttylog_path, e)

    return events


@router.get("/{session_id}/replay")
async def get_session_replay(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Get asciinema-compatible replay data for a session.

    Returns asciicast v2 format JSON for use with asciinema-player.
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Try to find and parse ttylog file
    tty_events = []
    if session.ttylog_file:
        ttylog_path = COWRIE_TTY_BASE / Path(session.ttylog_file).name
        if not ttylog_path.exists():
            # Try the raw path
            ttylog_path = Path(session.ttylog_file)
        if ttylog_path.exists():
            tty_events = parse_ttylog(ttylog_path)

    # If no ttylog, reconstruct from captured commands
    if not tty_events:
        cmd_result = await db.execute(
            select(Command)
            .where(Command.session_id == session.id)
            .order_by(Command.timestamp.asc())
        )
        commands = cmd_result.scalars().all()

        if not commands and not tty_events:
            raise HTTPException(status_code=404, detail="No replay data available for this session")

        offset = 0.0
        for cmd in commands:
            if session.started_at and cmd.timestamp:
                offset = (cmd.timestamp - session.started_at).total_seconds()
            tty_events.append([round(offset, 3), "o", f"$ {cmd.command}\r\n"])
            if cmd.output:
                tty_events.append([round(offset + 0.1, 3), "o", f"{cmd.output}\r\n"])
            offset += 1.0

    # Asciicast v2 header
    duration = session.duration_seconds or (
        tty_events[-1][0] if tty_events else 0
    )
    header = {
        "version": 2,
        "width": 120,
        "height": 36,
        "timestamp": int(session.started_at.timestamp()) if session.started_at else 0,
        "duration": duration,
        "title": f"HoneyAegis Session {session.session_id}",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
    }

    # Asciicast v2 is NDJSON: header line + event lines
    lines = [json.dumps(header)]
    for event in tty_events:
        lines.append(json.dumps(event))

    return JSONResponse(
        content={"asciicast": "\n".join(lines), "header": header, "event_count": len(tty_events)},
        media_type="application/json",
    )


@router.get("/{session_id}/commands")
async def get_session_commands(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Get the list of commands executed in a session."""
    result = await db.execute(
        select(Session).where(Session.id == session_id, Session.tenant_id == tenant_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cmd_result = await db.execute(
        select(Command)
        .where(Command.session_id == session.id)
        .order_by(Command.timestamp.asc())
    )
    commands = cmd_result.scalars().all()

    return [
        {
            "command": cmd.command,
            "output": cmd.output,
            "timestamp": cmd.timestamp.isoformat() if cmd.timestamp else None,
        }
        for cmd in commands
    ]

"""Cowrie log ingestion service — watches log files and persists to PostgreSQL.

In light profile: Backend watches the mounted Cowrie log volume directly.
In full profile: Vector ships logs to the /api/v1/events/ingest endpoint.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.session import Session
from app.models.event import Event
from app.models.command import Command
from app.models.download import Download
from app.services.geoip_service import lookup_ip

logger = logging.getLogger(__name__)

# Track file read position
_file_positions: dict[str, int] = {}

# In-memory session state for building sessions from events
_active_sessions: dict[str, dict] = {}


async def _persist_geoip(db: AsyncSession, ip: str) -> dict:
    """Look up and cache GeoIP data for an IP."""
    from app.models.geoip import GeoIPCache

    # Check cache first
    result = await db.execute(select(GeoIPCache).where(GeoIPCache.ip == ip))
    cached = result.scalar_one_or_none()
    if cached:
        return {
            "country_code": cached.country_code,
            "country_name": cached.country_name,
            "city": cached.city,
            "latitude": cached.latitude,
            "longitude": cached.longitude,
        }

    # Look up
    geo = await lookup_ip(ip)

    # Cache the result
    cache_entry = GeoIPCache(
        ip=ip,
        country_code=geo["country_code"],
        country_name=geo["country_name"],
        city=geo["city"],
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        asn=geo.get("asn", 0),
        org=geo.get("org", ""),
    )
    db.add(cache_entry)

    return geo


async def process_cowrie_event(event_data: dict, db: AsyncSession) -> dict | None:
    """Process a single parsed Cowrie JSON event and persist to database.

    Returns enriched event data for WebSocket broadcast, or None if filtered.
    """
    event_id = event_data.get("eventid", "")
    session_key = event_data.get("session", "")
    timestamp_str = event_data.get("timestamp", "")
    src_ip = event_data.get("src_ip", "")

    if not session_key or not event_id:
        return None

    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        ts = datetime.now(timezone.utc)

    broadcast_data = None

    # Session connect
    if event_id == "cowrie.session.connect":
        geo = await _persist_geoip(db, src_ip) if src_ip else {}

        session = Session(
            id=uuid4(),
            session_id=session_key,
            protocol=event_data.get("protocol", "ssh"),
            src_ip=src_ip,
            src_port=event_data.get("src_port"),
            dst_port=event_data.get("dst_port"),
            started_at=ts,
            country_code=geo.get("country_code"),
            country_name=geo.get("country_name"),
            city=geo.get("city"),
            latitude=geo.get("latitude"),
            longitude=geo.get("longitude"),
        )
        db.add(session)
        _active_sessions[session_key] = {"db_id": session.id, "start": ts}

        broadcast_data = {
            "type": "session.connect",
            "session_id": session_key,
            "src_ip": src_ip,
            "src_port": event_data.get("src_port"),
            "dst_port": event_data.get("dst_port"),
            "protocol": event_data.get("protocol", "ssh"),
            "timestamp": ts.isoformat(),
            "country_code": geo.get("country_code", "XX"),
            "country_name": geo.get("country_name", "Unknown"),
            "city": geo.get("city", ""),
            "latitude": geo.get("latitude", 0),
            "longitude": geo.get("longitude", 0),
        }

    # Login attempt
    elif event_id in ("cowrie.login.success", "cowrie.login.failed"):
        success = event_id == "cowrie.login.success"
        username = event_data.get("username", "")
        password = event_data.get("password", "")

        # Update session with login info
        result = await db.execute(
            select(Session).where(Session.session_id == session_key)
        )
        session = result.scalar_one_or_none()
        if session:
            session.username = username
            session.password = password
            session.auth_success = success

        broadcast_data = {
            "type": "login.attempt",
            "session_id": session_key,
            "src_ip": src_ip,
            "username": username,
            "success": success,
            "timestamp": ts.isoformat(),
        }

    # Command input
    elif event_id == "cowrie.command.input":
        cmd_text = event_data.get("input", "")

        result = await db.execute(
            select(Session).where(Session.session_id == session_key)
        )
        session = result.scalar_one_or_none()
        db_session_id = session.id if session else None

        if session:
            session.commands_count = (session.commands_count or 0) + 1

        command = Command(
            id=uuid4(),
            session_id=db_session_id,
            command=cmd_text,
            timestamp=ts,
            success=True,
        )
        db.add(command)

        broadcast_data = {
            "type": "command.input",
            "session_id": session_key,
            "src_ip": src_ip,
            "command": cmd_text,
            "timestamp": ts.isoformat(),
        }

    # File download
    elif event_id in ("cowrie.session.file_download", "cowrie.session.file_upload"):
        result = await db.execute(
            select(Session).where(Session.session_id == session_key)
        )
        session = result.scalar_one_or_none()
        db_session_id = session.id if session else None

        download = Download(
            id=uuid4(),
            session_id=db_session_id,
            url=event_data.get("url", ""),
            filename=event_data.get("filename", ""),
            file_hash_sha256=event_data.get("shasum", ""),
            file_size=event_data.get("size"),
            timestamp=ts,
        )
        db.add(download)

        broadcast_data = {
            "type": "file.download",
            "session_id": session_key,
            "src_ip": src_ip,
            "url": event_data.get("url", ""),
            "filename": event_data.get("filename", ""),
            "sha256": event_data.get("shasum", ""),
            "timestamp": ts.isoformat(),
        }

    # Session close
    elif event_id == "cowrie.session.closed":
        result = await db.execute(
            select(Session).where(Session.session_id == session_key)
        )
        session = result.scalar_one_or_none()
        if session:
            session.ended_at = ts
            if session.started_at:
                session.duration_seconds = (ts - session.started_at).total_seconds()
            # Set ttylog path if available
            ttylog = event_data.get("ttylog")
            if ttylog:
                session.ttylog_file = ttylog

            # Auto-generate AI summary on session close (non-blocking)
            try:
                await _auto_summarize_session(session, db)
            except Exception as e:
                logger.debug("Auto-summarize skipped: %s", e)

        _active_sessions.pop(session_key, None)

        broadcast_data = {
            "type": "session.closed",
            "session_id": session_key,
            "src_ip": src_ip,
            "timestamp": ts.isoformat(),
            "duration": event_data.get("duration"),
        }

    # Store raw event
    result = await db.execute(
        select(Session).where(Session.session_id == session_key)
    )
    session = result.scalar_one_or_none()
    db_session_id = session.id if session else None

    event = Event(
        id=uuid4(),
        session_id=db_session_id,
        event_type=event_id,
        timestamp=ts,
        src_ip=src_ip if src_ip else None,
        data=event_data,
    )
    db.add(event)

    return broadcast_data


async def _auto_summarize_session(session: Session, db: AsyncSession) -> None:
    """Generate an AI summary when a session closes (if Ollama is enabled)."""
    from app.services.ai_service import generate_session_summary, is_ai_enabled
    from app.models.ai_summary import AISummary
    from app.models.command import Command
    from app.models.download import Download

    if not await is_ai_enabled():
        return

    # Gather session data
    cmd_result = await db.execute(
        select(Command.command)
        .where(Command.session_id == session.id)
        .order_by(Command.timestamp)
    )
    commands = [row[0] for row in cmd_result.all()]

    dl_result = await db.execute(
        select(Download.filename, Download.url, Download.file_hash_sha256)
        .where(Download.session_id == session.id)
    )
    downloads = [
        {"filename": row[0], "url": row[1], "sha256": row[2]}
        for row in dl_result.all()
    ]

    session_data = {
        "src_ip": str(session.src_ip),
        "country_name": session.country_name or "Unknown",
        "protocol": session.protocol,
        "dst_port": session.dst_port,
        "username": session.username,
        "auth_success": session.auth_success,
        "duration_seconds": session.duration_seconds or 0,
        "commands": commands,
        "downloads": downloads,
    }

    ai_result = await generate_session_summary(session_data)
    if ai_result is None:
        return

    summary = AISummary(
        id=uuid4(),
        session_id=session.id,
        summary=ai_result["summary"],
        threat_level=ai_result["threat_level"],
        mitre_ttps=ai_result.get("mitre_ttps", []),
        recommendations=ai_result.get("recommendations", ""),
        model_used=ai_result.get("model_used", ""),
    )
    db.add(summary)
    logger.info("AI summary auto-generated for session %s", session.session_id)


async def watch_cowrie_logs(log_path: str = "/data/cowrie_logs/cowrie.json"):
    """Continuously watch and ingest Cowrie JSON log file.

    This runs as a background task during application startup.
    """
    from app.api.websocket import broadcast_event

    path = Path(log_path)
    logger.info("Starting Cowrie log watcher on %s", path)

    while True:
        try:
            if not path.exists():
                await asyncio.sleep(2)
                continue

            current_pos = _file_positions.get(str(path), 0)

            with open(path, "r") as f:
                f.seek(current_pos)
                new_lines = f.readlines()
                _file_positions[str(path)] = f.tell()

            if not new_lines:
                await asyncio.sleep(1)
                continue

            async with async_session() as db:
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event_data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    broadcast_data = await process_cowrie_event(event_data, db)
                    if broadcast_data:
                        await broadcast_event(broadcast_data)

                await db.commit()

        except Exception as e:
            logger.error("Error in log watcher: %s", e, exc_info=True)
            await asyncio.sleep(5)

        await asyncio.sleep(0.5)

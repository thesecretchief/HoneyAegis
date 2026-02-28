"""Sensor relay worker — forwards Cowrie events to a central HoneyAegis hub.

This module runs as a standalone process on sensor-only deployments
(e.g., Raspberry Pi). It:
  1. Watches the Cowrie log directory for new JSON events.
  2. Batches events and relays them to the hub via /api/v1/relay/events.
  3. Sends periodic heartbeats to /api/v1/relay/heartbeat.

Usage:
  python -m app.workers.sensor_relay

Environment variables:
  HONEYAEGIS_HUB_URL  — hub URL (default: http://localhost:8000)
  SENSOR_ID           — unique sensor identifier
  SENSOR_TOKEN        — bearer token for hub authentication
"""

import json
import logging
import os
import platform
import signal
import sys
import time
from pathlib import Path

logger = logging.getLogger("honeyaegis.sensor_relay")

HUB_URL = os.environ.get("HONEYAEGIS_HUB_URL", "http://localhost:8000")
SENSOR_ID = os.environ.get("SENSOR_ID", "sensor-01")
SENSOR_TOKEN = os.environ.get("SENSOR_TOKEN", "change-me")
LOG_DIR = Path(os.environ.get("COWRIE_LOG_PATH", "/data/cowrie_logs"))
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "60"))
BATCH_SIZE = int(os.environ.get("RELAY_BATCH_SIZE", "50"))
BATCH_INTERVAL = int(os.environ.get("RELAY_BATCH_INTERVAL", "10"))

_running = True


def _signal_handler(_sig: int, _frame: object) -> None:
    global _running
    logger.info("Shutdown signal received, stopping relay...")
    _running = False


def _get_auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {SENSOR_TOKEN}"}


def _send_heartbeat(session: object) -> bool:
    """Send heartbeat to hub with sensor health metrics."""
    import shutil

    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().used / (1024 * 1024)
        disk = psutil.disk_usage("/").percent
    except ImportError:
        cpu = 0.0
        mem = 0.0
        disk = shutil.disk_usage("/").used / shutil.disk_usage("/").total * 100

    payload = {
        "sensor_id": SENSOR_ID,
        "hostname": platform.node(),
        "ip_address": None,
        "version": "1.0.0",
        "uptime_seconds": int(time.monotonic()),
        "sessions_captured": 0,
        "cpu_percent": round(cpu, 1),
        "memory_mb": round(mem, 1),
        "disk_percent": round(disk, 1),
    }

    try:
        resp = session.post(
            f"{HUB_URL}/api/v1/relay/heartbeat",
            json=payload,
            headers=_get_auth_headers(),
            timeout=10,
        )
        if resp.status_code == 200:
            logger.debug("Heartbeat sent successfully")
            return True
        logger.warning("Heartbeat failed: %d %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.error("Heartbeat error: %s", exc)
    return False


def _relay_events(session: object, events: list[dict]) -> bool:
    """Relay a batch of events to the hub."""
    if not events:
        return True

    payload = {
        "sensor_id": SENSOR_ID,
        "events": events,
    }

    try:
        resp = session.post(
            f"{HUB_URL}/api/v1/relay/events",
            json=payload,
            headers=_get_auth_headers(),
            timeout=30,
        )
        if resp.status_code == 200:
            logger.info("Relayed %d events", len(events))
            return True
        logger.warning("Relay failed: %d %s", resp.status_code, resp.text)
    except Exception as exc:
        logger.error("Relay error: %s", exc)
    return False


def _tail_log_file(log_path: Path, position: int) -> tuple[list[dict], int]:
    """Read new lines from the Cowrie JSON log since last position."""
    events: list[dict] = []
    if not log_path.exists():
        return events, position

    try:
        with open(log_path, "r") as f:
            f.seek(position)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    events.append({
                        "sensor_id": SENSOR_ID,
                        "event_type": data.get("eventid", "unknown"),
                        "timestamp": data.get("timestamp", ""),
                        "src_ip": data.get("src_ip"),
                        "src_port": data.get("src_port"),
                        "dst_port": data.get("dst_port"),
                        "protocol": data.get("protocol", "ssh"),
                        "username": data.get("username"),
                        "password": data.get("password"),
                        "command": data.get("input"),
                        "success": data.get("success"),
                        "session_id": data.get("session"),
                    })
                except json.JSONDecodeError:
                    continue
            new_position = f.tell()
    except OSError as exc:
        logger.error("Error reading log file: %s", exc)
        return events, position

    return events, new_position


def main() -> None:
    """Main relay loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    logger.info(
        "Starting sensor relay: sensor=%s hub=%s log_dir=%s",
        SENSOR_ID, HUB_URL, LOG_DIR,
    )

    try:
        import requests
        http_session = requests.Session()
    except ImportError:
        import urllib.request
        logger.warning("requests not available, using urllib fallback")
        http_session = None

    log_file = LOG_DIR / "cowrie.json"
    file_position = log_file.stat().st_size if log_file.exists() else 0
    last_heartbeat = 0.0
    event_buffer: list[dict] = []
    last_batch_send = time.monotonic()

    while _running:
        now = time.monotonic()

        # Heartbeat
        if now - last_heartbeat >= HEARTBEAT_INTERVAL:
            if http_session:
                _send_heartbeat(http_session)
            last_heartbeat = now

        # Read new events
        new_events, file_position = _tail_log_file(log_file, file_position)
        event_buffer.extend(new_events)

        # Send batch if full or interval elapsed
        if (
            len(event_buffer) >= BATCH_SIZE
            or (event_buffer and now - last_batch_send >= BATCH_INTERVAL)
        ):
            if http_session:
                batch = event_buffer[:BATCH_SIZE]
                if _relay_events(http_session, batch):
                    event_buffer = event_buffer[BATCH_SIZE:]
                last_batch_send = now

        time.sleep(1)

    logger.info("Sensor relay stopped")


if __name__ == "__main__":
    main()

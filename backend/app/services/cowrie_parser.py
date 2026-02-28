"""Parse Cowrie JSON logs into session and event records."""

import json
from datetime import datetime
from pathlib import Path


def parse_cowrie_log_line(line: str) -> dict | None:
    """Parse a single Cowrie JSON log line into a structured dict."""
    try:
        entry = json.loads(line.strip())
    except json.JSONDecodeError:
        return None

    return {
        "event_id": entry.get("eventid"),
        "session": entry.get("session"),
        "timestamp": entry.get("timestamp"),
        "src_ip": entry.get("src_ip"),
        "src_port": entry.get("src_port"),
        "dst_ip": entry.get("dst_ip"),
        "dst_port": entry.get("dst_port"),
        "username": entry.get("username"),
        "password": entry.get("password"),
        "input": entry.get("input"),
        "message": entry.get("message"),
        "sensor": entry.get("sensor"),
        "raw": entry,
    }


def parse_cowrie_log_file(filepath: str | Path) -> list[dict]:
    """Parse an entire Cowrie JSON log file."""
    events = []
    with open(filepath, "r") as f:
        for line in f:
            parsed = parse_cowrie_log_line(line)
            if parsed:
                events.append(parsed)
    return events

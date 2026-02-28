"""Tests for session replay parsing."""

import struct
import tempfile
from pathlib import Path

from app.api.replay import parse_ttylog


def _create_test_ttylog(frames: list[tuple[int, int, bytes]]) -> Path:
    """Create a test ttylog file with the given frames (sec, usec, data)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".ttylog", delete=False)
    for sec, usec, data in frames:
        header = struct.pack("<III", sec, usec, len(data))
        tmp.write(header)
        tmp.write(data)
    tmp.close()
    return Path(tmp.name)


def test_parse_ttylog_basic():
    ttylog = _create_test_ttylog([
        (1000, 0, b"$ whoami\r\n"),
        (1001, 0, b"root\r\n"),
        (1002, 500000, b"$ ls\r\n"),
    ])

    events = parse_ttylog(ttylog)
    assert len(events) == 3

    # First event should be at offset 0
    assert events[0][0] == 0.0
    assert events[0][1] == "o"
    assert "whoami" in events[0][2]

    # Second event should be at offset ~1.0
    assert abs(events[1][0] - 1.0) < 0.01
    assert "root" in events[1][2]

    # Third event should be at offset ~2.5
    assert abs(events[2][0] - 2.5) < 0.01
    assert "ls" in events[2][2]

    # Cleanup
    ttylog.unlink()


def test_parse_ttylog_empty():
    ttylog = _create_test_ttylog([])
    events = parse_ttylog(ttylog)
    assert len(events) == 0
    ttylog.unlink()


def test_parse_ttylog_single_frame():
    ttylog = _create_test_ttylog([
        (0, 0, b"Hello World"),
    ])
    events = parse_ttylog(ttylog)
    assert len(events) == 1
    assert events[0][0] == 0.0
    assert events[0][2] == "Hello World"
    ttylog.unlink()


def test_parse_ttylog_nonexistent():
    events = parse_ttylog(Path("/nonexistent/file.ttylog"))
    assert len(events) == 0

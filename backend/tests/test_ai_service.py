"""Tests for the AI service module."""

from unittest.mock import patch, AsyncMock

import pytest

from app.services.ai_service import (
    _parse_json_response,
    _fallback_overlay,
)


def test_parse_json_response_clean():
    raw = '{"summary": "Attacker brute-forced SSH.", "threat_level": "high", "mitre_ttps": ["T1078"], "recommendations": "Block the IP."}'
    result = _parse_json_response(raw)
    assert result["summary"] == "Attacker brute-forced SSH."
    assert result["threat_level"] == "high"
    assert result["mitre_ttps"] == ["T1078"]
    assert result["recommendations"] == "Block the IP."


def test_parse_json_response_with_markdown_fences():
    raw = '```json\n{"summary": "Test", "threat_level": "low", "mitre_ttps": [], "recommendations": ""}\n```'
    result = _parse_json_response(raw)
    assert result["summary"] == "Test"
    assert result["threat_level"] == "low"


def test_parse_json_response_missing_fields():
    raw = '{"summary": "Minimal"}'
    result = _parse_json_response(raw)
    assert result["summary"] == "Minimal"
    assert result["threat_level"] == "medium"
    assert result["mitre_ttps"] == []
    assert result["recommendations"] == ""


def test_parse_json_response_invalid():
    with pytest.raises(Exception):
        _parse_json_response("not json at all")


def test_fallback_overlay():
    session_data = {
        "src_ip": "1.2.3.4",
        "username": "root",
        "commands": ["ls", "cat /etc/passwd"],
    }
    result = _fallback_overlay(session_data)
    assert "1.2.3.4" in result
    assert "root" in result
    assert "2 cmds" in result


def test_fallback_overlay_no_commands():
    session_data = {"src_ip": "5.6.7.8", "username": None, "commands": None}
    result = _fallback_overlay(session_data)
    assert "5.6.7.8" in result
    assert "0 cmds" in result

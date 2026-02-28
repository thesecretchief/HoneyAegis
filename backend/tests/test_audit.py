"""Tests for audit logging service."""

import uuid
import json
import logging

import pytest

from app.services.audit_service import (
    log_audit,
    format_cef,
    format_syslog,
    AuditEvent,
)


def test_audit_event_constants():
    """AuditEvent has all expected constants."""
    assert AuditEvent.LOGIN_SUCCESS == "auth.login.success"
    assert AuditEvent.LOGIN_FAILURE == "auth.login.failure"
    assert AuditEvent.TOKEN_CREATED == "token.created"
    assert AuditEvent.WEBHOOK_CREATED == "webhook.created"
    assert AuditEvent.HONEY_TOKEN_TRIGGERED == "honey_token.triggered"
    assert AuditEvent.CONFIG_UPDATED == "config.updated"
    assert AuditEvent.PLUGIN_RELOADED == "plugin.reloaded"


def test_log_audit_writes_structured_json(caplog):
    """log_audit writes structured JSON to the audit logger."""
    tenant_id = uuid.uuid4()
    with caplog.at_level(logging.INFO, logger="honeyaegis.audit"):
        log_audit(
            event=AuditEvent.LOGIN_SUCCESS,
            actor="admin@test.com",
            tenant_id=tenant_id,
            resource_type="user",
            ip_address="10.0.0.1",
        )

    assert "AUDIT" in caplog.text
    assert "auth.login.success" in caplog.text
    assert "admin@test.com" in caplog.text


def test_log_audit_with_details(caplog):
    """log_audit includes additional details."""
    with caplog.at_level(logging.INFO, logger="honeyaegis.audit"):
        log_audit(
            event=AuditEvent.CONFIG_UPDATED,
            actor="admin@test.com",
            details={"setting": "alert_cooldown", "old": 5, "new": 10},
        )

    assert "config.updated" in caplog.text


def test_log_audit_minimal(caplog):
    """log_audit works with minimal arguments."""
    with caplog.at_level(logging.INFO, logger="honeyaegis.audit"):
        log_audit(event="test.event")

    assert "test.event" in caplog.text


def test_format_cef_basic():
    """format_cef returns valid CEF format."""
    cef = format_cef(event="honeypot.session", severity=8, src_ip="1.2.3.4")
    assert cef.startswith("CEF:0|HoneyAegis|HoneyAegis|0.6.0|")
    assert "honeypot.session" in cef
    assert "src=1.2.3.4" in cef


def test_format_cef_with_extension():
    """format_cef includes extension fields."""
    cef = format_cef(
        event="test",
        severity=5,
        src_ip="10.0.0.1",
        dst_ip="192.168.1.1",
        msg="Test event",
        extension={"dpt": "22", "cs1": "US", "cs1Label": "Country"},
    )
    assert "src=10.0.0.1" in cef
    assert "dst=192.168.1.1" in cef
    assert "msg=Test event" in cef
    assert "dpt=22" in cef
    assert "cs1=US" in cef


def test_format_cef_severity_range():
    """format_cef handles severity range 0-10."""
    for severity in [0, 3, 5, 8, 10]:
        cef = format_cef(event="test", severity=severity)
        assert f"|{severity}|" in cef


def test_format_syslog_basic():
    """format_syslog returns RFC 5424-style output."""
    syslog = format_syslog(event="honeypot.session", severity="info")
    assert "honeyaegis" in syslog
    assert "honeypot.session" in syslog


def test_format_syslog_with_details():
    """format_syslog includes structured data."""
    syslog = format_syslog(
        event="honeypot.session",
        severity="warning",
        details={"src_ip": "1.2.3.4", "protocol": "ssh"},
    )
    assert "honeyaegis@0" in syslog
    assert 'src_ip="1.2.3.4"' in syslog
    assert 'protocol="ssh"' in syslog


def test_format_syslog_severity_mapping():
    """format_syslog maps severity to correct syslog codes."""
    for severity in ["debug", "info", "warning", "critical"]:
        syslog = format_syslog(event="test", severity=severity)
        assert syslog.startswith("<")

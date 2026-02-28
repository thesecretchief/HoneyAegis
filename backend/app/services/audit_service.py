"""Audit logging service for HoneyAegis.

Records security-relevant actions for compliance and forensics.
Supports structured JSON output for SIEM integration.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

logger = logging.getLogger("honeyaegis.audit")

# Structured audit logger — writes JSON lines to stdout/file
_audit_handler = logging.StreamHandler()
_audit_handler.setFormatter(logging.Formatter("%(message)s"))
_audit_logger = logging.getLogger("honeyaegis.audit.structured")
_audit_logger.addHandler(_audit_handler)
_audit_logger.setLevel(logging.INFO)
_audit_logger.propagate = False


class AuditEvent:
    """Represents an auditable action."""

    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    TOKEN_CREATED = "token.created"
    TOKEN_DELETED = "token.deleted"
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_DELETED = "webhook.deleted"
    WEBHOOK_TESTED = "webhook.tested"
    TENANT_CREATED = "tenant.created"
    TENANT_UPDATED = "tenant.updated"
    SENSOR_REGISTERED = "sensor.registered"
    CONFIG_UPDATED = "config.updated"
    PLUGIN_RELOADED = "plugin.reloaded"
    REPORT_GENERATED = "report.generated"
    SESSION_EXPORTED = "session.exported"
    HONEY_TOKEN_TRIGGERED = "honey_token.triggered"
    API_KEY_ROTATED = "api_key.rotated"


def _serialize(value: Any) -> Any:
    """Serialize values for JSON output."""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def log_audit(
    event: str,
    actor: str | None = None,
    tenant_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
    severity: str = "info",
) -> None:
    """Log an audit event in structured JSON format.

    Args:
        event: The audit event type (use AuditEvent constants).
        actor: Email or identifier of the user performing the action.
        tenant_id: The tenant context for the action.
        resource_type: Type of resource affected (e.g., "honey_token", "webhook").
        resource_id: ID of the affected resource.
        details: Additional context as a dict.
        ip_address: Source IP of the request.
        severity: Event severity (info, warning, critical).
    """
    record = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "severity": severity,
        "actor": actor,
        "tenant_id": _serialize(tenant_id),
        "resource_type": resource_type,
        "resource_id": _serialize(resource_id) if resource_id else None,
        "ip_address": ip_address,
        "details": details or {},
        "service": "honeyaegis-api",
    }

    # Remove None values for cleaner output
    record = {k: v for k, v in record.items() if v is not None}

    # Write structured JSON
    _audit_logger.info(json.dumps(record, default=str))

    # Also log human-readable for standard logging
    logger.info(
        "AUDIT [%s] actor=%s tenant=%s resource=%s/%s",
        event,
        actor or "system",
        _serialize(tenant_id) if tenant_id else "global",
        resource_type or "-",
        _serialize(resource_id) if resource_id else "-",
    )


def format_cef(
    event: str,
    severity: int = 3,
    src_ip: str | None = None,
    dst_ip: str | None = None,
    msg: str = "",
    extension: dict | None = None,
) -> str:
    """Format an event as CEF (Common Event Format) for SIEM integration.

    CEF format: CEF:Version|DeviceVendor|DeviceProduct|DeviceVersion|SignatureID|Name|Severity|Extension

    Args:
        event: Event name / signature ID.
        severity: 0-10 scale (0=lowest, 10=highest).
        src_ip: Source IP address.
        dst_ip: Destination IP address.
        msg: Human-readable message.
        extension: Additional CEF key-value pairs.

    Returns:
        CEF-formatted string.
    """
    ext_parts = []
    if src_ip:
        ext_parts.append(f"src={src_ip}")
    if dst_ip:
        ext_parts.append(f"dst={dst_ip}")
    if msg:
        ext_parts.append(f"msg={msg}")
    if extension:
        for k, v in extension.items():
            ext_parts.append(f"{k}={v}")

    ext_str = " ".join(ext_parts)
    return f"CEF:0|HoneyAegis|HoneyAegis|0.6.0|{event}|{event}|{severity}|{ext_str}"


def format_syslog(
    event: str,
    severity: str = "info",
    details: dict | None = None,
) -> str:
    """Format an event as syslog-compatible structured data.

    Returns RFC 5424-style structured data string.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    sd = ""
    if details:
        pairs = " ".join(f'{k}="{v}"' for k, v in details.items())
        sd = f'[honeyaegis@0 {pairs}]'

    facility_severity = _syslog_severity(severity)
    return f"<{facility_severity}>1 {timestamp} honeyaegis honeyaegis-api - {event} {sd}"


def _syslog_severity(level: str) -> int:
    """Map severity string to syslog facility.severity numeric value.

    Uses facility=1 (user-level) with appropriate severity.
    """
    severity_map = {
        "debug": 15,    # facility=1, severity=7
        "info": 14,     # facility=1, severity=6
        "warning": 12,  # facility=1, severity=4
        "critical": 10, # facility=1, severity=2
    }
    return severity_map.get(level, 14)

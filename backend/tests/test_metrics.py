"""Tests for Prometheus metrics service."""

import pytest
from prometheus_client import REGISTRY

from app.services.metrics_service import (
    get_metrics,
    get_metrics_content_type,
    HTTP_REQUESTS_TOTAL,
    SESSIONS_TOTAL,
    LOGIN_ATTEMPTS_TOTAL,
    COMMANDS_CAPTURED_TOTAL,
    ALERTS_TOTAL,
    WEBHOOKS_EXECUTED_TOTAL,
    HONEY_TOKENS_TRIGGERED_TOTAL,
    HONEY_TOKENS_ACTIVE,
    AI_SUMMARIES_TOTAL,
    SENSORS_TOTAL,
    PLUGINS_LOADED,
    SESSIONS_ACTIVE,
    MALWARE_CAPTURES_TOTAL,
    APP_INFO,
)


def test_get_metrics_returns_bytes():
    """get_metrics returns bytes output."""
    output = get_metrics()
    assert isinstance(output, bytes)
    assert len(output) > 0


def test_get_metrics_content_type():
    """Content type matches Prometheus exposition format."""
    ct = get_metrics_content_type()
    assert "text/plain" in ct or "openmetrics" in ct


def test_metrics_contain_app_info():
    """Metrics output contains application info."""
    output = get_metrics().decode()
    assert "honeyaegis_info" in output
    assert "0.6.0" in output


def test_http_requests_counter():
    """HTTP requests counter increments correctly."""
    before = REGISTRY.get_sample_value(
        "honeyaegis_http_requests_total",
        {"method": "GET", "endpoint": "/test", "status_code": "200"},
    ) or 0.0

    HTTP_REQUESTS_TOTAL.labels(method="GET", endpoint="/test", status_code="200").inc()

    after = REGISTRY.get_sample_value(
        "honeyaegis_http_requests_total",
        {"method": "GET", "endpoint": "/test", "status_code": "200"},
    )
    assert after == before + 1


def test_sessions_counter():
    """Sessions counter increments by protocol."""
    before = REGISTRY.get_sample_value(
        "honeyaegis_sessions_total",
        {"protocol": "ssh", "sensor_id": "test"},
    ) or 0.0

    SESSIONS_TOTAL.labels(protocol="ssh", sensor_id="test").inc()

    after = REGISTRY.get_sample_value(
        "honeyaegis_sessions_total",
        {"protocol": "ssh", "sensor_id": "test"},
    )
    assert after == before + 1


def test_login_attempts_counter():
    """Login attempts counter tracks success and failure."""
    LOGIN_ATTEMPTS_TOTAL.labels(success="true", protocol="ssh").inc()
    LOGIN_ATTEMPTS_TOTAL.labels(success="false", protocol="ssh").inc(3)

    success = REGISTRY.get_sample_value(
        "honeyaegis_login_attempts_total",
        {"success": "true", "protocol": "ssh"},
    )
    failed = REGISTRY.get_sample_value(
        "honeyaegis_login_attempts_total",
        {"success": "false", "protocol": "ssh"},
    )
    assert success >= 1
    assert failed >= 3


def test_alerts_counter():
    """Alerts counter tracks by severity."""
    ALERTS_TOTAL.labels(severity="critical").inc()
    ALERTS_TOTAL.labels(severity="high").inc(2)

    critical = REGISTRY.get_sample_value(
        "honeyaegis_alerts_total", {"severity": "critical"}
    )
    high = REGISTRY.get_sample_value(
        "honeyaegis_alerts_total", {"severity": "high"}
    )
    assert critical >= 1
    assert high >= 2


def test_webhooks_counter():
    """Webhooks counter tracks success and error."""
    WEBHOOKS_EXECUTED_TOTAL.labels(status="success").inc()
    WEBHOOKS_EXECUTED_TOTAL.labels(status="error").inc()

    success = REGISTRY.get_sample_value(
        "honeyaegis_webhooks_executed_total", {"status": "success"}
    )
    assert success >= 1


def test_honey_tokens_triggered_counter():
    """Honey token trigger counter increments."""
    HONEY_TOKENS_TRIGGERED_TOTAL.labels(token_type="credential").inc()

    val = REGISTRY.get_sample_value(
        "honeyaegis_honey_tokens_triggered_total", {"token_type": "credential"}
    )
    assert val >= 1


def test_honey_tokens_active_gauge():
    """Honey tokens active gauge can be set."""
    HONEY_TOKENS_ACTIVE.set(5)
    val = REGISTRY.get_sample_value("honeyaegis_honey_tokens_active")
    assert val == 5


def test_sessions_active_gauge():
    """Active sessions gauge can be set."""
    SESSIONS_ACTIVE.set(3)
    val = REGISTRY.get_sample_value("honeyaegis_sessions_active")
    assert val == 3


def test_plugins_loaded_gauge():
    """Plugins loaded gauge can be set."""
    PLUGINS_LOADED.set(2)
    val = REGISTRY.get_sample_value("honeyaegis_plugins_loaded")
    assert val == 2


def test_sensors_gauge():
    """Sensors gauge tracks by status."""
    SENSORS_TOTAL.labels(status="online").set(3)
    SENSORS_TOTAL.labels(status="offline").set(1)

    online = REGISTRY.get_sample_value(
        "honeyaegis_sensors_total", {"status": "online"}
    )
    offline = REGISTRY.get_sample_value(
        "honeyaegis_sensors_total", {"status": "offline"}
    )
    assert online == 3
    assert offline == 1


def test_ai_summaries_counter():
    """AI summaries counter tracks success and error."""
    AI_SUMMARIES_TOTAL.labels(status="success").inc()

    val = REGISTRY.get_sample_value(
        "honeyaegis_ai_summaries_total", {"status": "success"}
    )
    assert val >= 1

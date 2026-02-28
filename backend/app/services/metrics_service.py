"""Prometheus metrics service for HoneyAegis.

Exposes application metrics at /metrics for Prometheus scraping.
Uses prometheus-client library counters, gauges, and histograms.
"""

import logging

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application Info
# ---------------------------------------------------------------------------
APP_INFO = Info("honeyaegis", "HoneyAegis application info")
APP_INFO.info({"version": "0.6.0", "service": "honeyaegis-api"})

# ---------------------------------------------------------------------------
# Request Metrics
# ---------------------------------------------------------------------------
HTTP_REQUESTS_TOTAL = Counter(
    "honeyaegis_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "honeyaegis_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ---------------------------------------------------------------------------
# Honeypot Metrics
# ---------------------------------------------------------------------------
SESSIONS_TOTAL = Counter(
    "honeyaegis_sessions_total",
    "Total honeypot sessions captured",
    ["protocol", "sensor_id"],
)

SESSIONS_ACTIVE = Gauge(
    "honeyaegis_sessions_active",
    "Currently active honeypot sessions",
)

LOGIN_ATTEMPTS_TOTAL = Counter(
    "honeyaegis_login_attempts_total",
    "Total login attempts captured",
    ["success", "protocol"],
)

COMMANDS_CAPTURED_TOTAL = Counter(
    "honeyaegis_commands_captured_total",
    "Total commands captured from attackers",
)

MALWARE_CAPTURES_TOTAL = Counter(
    "honeyaegis_malware_captures_total",
    "Total malware files captured",
)

# ---------------------------------------------------------------------------
# Alert & Webhook Metrics
# ---------------------------------------------------------------------------
ALERTS_TOTAL = Counter(
    "honeyaegis_alerts_total",
    "Total alerts generated",
    ["severity"],
)

WEBHOOKS_EXECUTED_TOTAL = Counter(
    "honeyaegis_webhooks_executed_total",
    "Total webhooks executed",
    ["status"],
)

WEBHOOK_DURATION = Histogram(
    "honeyaegis_webhook_duration_seconds",
    "Webhook execution duration in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0],
)

# ---------------------------------------------------------------------------
# Honey Token Metrics
# ---------------------------------------------------------------------------
HONEY_TOKENS_TRIGGERED_TOTAL = Counter(
    "honeyaegis_honey_tokens_triggered_total",
    "Total honey token triggers",
    ["token_type"],
)

HONEY_TOKENS_ACTIVE = Gauge(
    "honeyaegis_honey_tokens_active",
    "Number of active honey tokens",
)

# ---------------------------------------------------------------------------
# AI Metrics
# ---------------------------------------------------------------------------
AI_SUMMARIES_TOTAL = Counter(
    "honeyaegis_ai_summaries_total",
    "Total AI summaries generated",
    ["status"],
)

AI_SUMMARY_DURATION = Histogram(
    "honeyaegis_ai_summary_duration_seconds",
    "AI summary generation duration in seconds",
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
)

# ---------------------------------------------------------------------------
# Sensor Metrics
# ---------------------------------------------------------------------------
SENSORS_TOTAL = Gauge(
    "honeyaegis_sensors_total",
    "Total registered sensors",
    ["status"],
)

# ---------------------------------------------------------------------------
# Plugin Metrics
# ---------------------------------------------------------------------------
PLUGINS_LOADED = Gauge(
    "honeyaegis_plugins_loaded",
    "Number of loaded plugins",
)

PLUGIN_HOOK_DURATION = Histogram(
    "honeyaegis_plugin_hook_duration_seconds",
    "Plugin hook execution duration in seconds",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

# ---------------------------------------------------------------------------
# Database Metrics
# ---------------------------------------------------------------------------
DB_QUERIES_TOTAL = Counter(
    "honeyaegis_db_queries_total",
    "Total database queries",
    ["operation"],
)


def get_metrics() -> bytes:
    """Generate Prometheus metrics output."""
    return generate_latest(REGISTRY)


def get_metrics_content_type() -> str:
    """Return the Prometheus content type."""
    return CONTENT_TYPE_LATEST

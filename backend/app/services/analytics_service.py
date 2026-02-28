"""Privacy-first anonymous usage analytics for HoneyAegis.

Collects anonymous, aggregate-only telemetry to help the project
understand how HoneyAegis is deployed. No PII, no session data,
no attacker IPs — only deployment metadata.

Telemetry is strictly opt-in. Set ANALYTICS_ENABLED=true in .env
to participate. Data is sent to a public analytics endpoint (stub).

What is collected:
  - HoneyAegis version
  - Deployment type (docker, k8s, rpi, bare-metal)
  - OS and architecture (e.g., linux/amd64)
  - Active profile (light/full)
  - Number of sensors (count only)
  - Number of plugins loaded (count only)
  - Uptime (hours)

What is NEVER collected:
  - IP addresses (yours or attackers')
  - Session data or commands
  - Credentials or tokens
  - Tenant/user information
  - Any personally identifiable information
"""

import hashlib
import logging
import platform
import time
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

_start_time = time.monotonic()


@dataclass
class TelemetryPayload:
    """Anonymous telemetry data."""

    version: str
    deployment_type: str
    os_info: str
    arch: str
    profile: str
    sensor_count: int
    plugin_count: int
    uptime_hours: float
    instance_id: str


def _generate_instance_id() -> str:
    """Generate a stable anonymous instance ID from the secret key.

    This allows us to count unique deployments without identifying them.
    The instance ID is a one-way hash — it cannot be reversed to reveal
    the secret key.
    """
    key = settings.honeyaegis_secret_key
    return hashlib.sha256(f"honeyaegis-analytics-{key}".encode()).hexdigest()[:16]


def build_telemetry_payload(
    sensor_count: int = 0,
    plugin_count: int = 0,
) -> TelemetryPayload:
    """Build the anonymous telemetry payload."""
    uptime = (time.monotonic() - _start_time) / 3600

    return TelemetryPayload(
        version="1.0.0",
        deployment_type=_detect_deployment_type(),
        os_info=f"{platform.system()} {platform.release()[:20]}",
        arch=platform.machine(),
        profile="full" if settings.ollama_enabled else "light",
        sensor_count=sensor_count,
        plugin_count=plugin_count,
        uptime_hours=round(uptime, 1),
        instance_id=_generate_instance_id(),
    )


def _detect_deployment_type() -> str:
    """Best-effort detection of deployment environment."""
    import os

    if os.path.exists("/run/secrets/kubernetes.io"):
        return "kubernetes"
    if os.path.exists("/.dockerenv"):
        return "docker"
    if platform.machine() in ("aarch64", "arm64"):
        return "rpi"
    return "bare-metal"


async def send_telemetry(sensor_count: int = 0, plugin_count: int = 0) -> bool:
    """Send anonymous telemetry (opt-in only).

    Returns True if telemetry was sent, False if disabled or failed.
    """
    enabled = getattr(settings, "analytics_enabled", False)
    if not enabled:
        return False

    payload = build_telemetry_payload(sensor_count, plugin_count)
    logger.debug(
        "Telemetry: version=%s deployment=%s arch=%s profile=%s sensors=%d",
        payload.version,
        payload.deployment_type,
        payload.arch,
        payload.profile,
        payload.sensor_count,
    )

    # Stub: In production, this would POST to the analytics endpoint.
    # For now, we just log the payload.
    return True

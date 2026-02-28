"""HoneyAegis Plugin Template.

Copy this file to /plugins/ and rename it. HoneyAegis will auto-discover it on startup.

Plugin types:
  - enricher: Add data to sessions/events (GeoIP, threat intel, etc.)
  - hook: React to events in real-time (alerting, blocking, logging)
  - emulator: Simulate additional services or commands

Hooks available:
  - on_session_start(session_data: dict) -> None
  - on_session_end(session_data: dict) -> None
  - on_login_attempt(attempt_data: dict) -> None
  - on_command(command_data: dict) -> None
  - on_download(download_data: dict) -> None
  - on_alert(alert_data: dict) -> None

See docs/plugin-dev-guide.md for the full API reference.
"""

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Plugin metadata (required)
# ---------------------------------------------------------------------------
PLUGIN_NAME = "my-plugin"
PLUGIN_VERSION = "0.1.0"
PLUGIN_TYPE = "hook"  # "enricher", "hook", or "emulator"
PLUGIN_DESCRIPTION = "A template plugin — customize this for your use case."


# ---------------------------------------------------------------------------
# Lifecycle hooks (optional — implement the ones you need)
# ---------------------------------------------------------------------------
async def on_load():
    """Called when the plugin is loaded. Use for initialization."""
    logger.info("[%s] Plugin loaded (v%s)", PLUGIN_NAME, PLUGIN_VERSION)


async def on_unload():
    """Called when the plugin is unloaded. Use for cleanup."""
    logger.info("[%s] Plugin unloaded", PLUGIN_NAME)


# ---------------------------------------------------------------------------
# Event hooks (implement the ones relevant to your plugin)
# ---------------------------------------------------------------------------
async def on_session_start(session_data: dict) -> None:
    """Called when a new attacker session begins.

    Args:
        session_data: {
            "session_id": str,
            "src_ip": str,
            "src_port": int,
            "dst_port": int,
            "protocol": str,  # "ssh" or "telnet"
            "sensor_id": str | None,
            "timestamp": str,  # ISO 8601
        }
    """
    logger.info("[%s] New session from %s", PLUGIN_NAME, session_data.get("src_ip"))


async def on_session_end(session_data: dict) -> None:
    """Called when an attacker session ends."""
    pass


async def on_login_attempt(attempt_data: dict) -> None:
    """Called on each login attempt.

    Args:
        attempt_data: {
            "session_id": str,
            "username": str,
            "password": str,
            "success": bool,
            "src_ip": str,
            "timestamp": str,
        }
    """
    if attempt_data.get("success"):
        logger.warning(
            "[%s] Successful login: %s / %s from %s",
            PLUGIN_NAME,
            attempt_data.get("username"),
            attempt_data.get("password"),
            attempt_data.get("src_ip"),
        )


async def on_command(command_data: dict) -> None:
    """Called when an attacker executes a command.

    Args:
        command_data: {
            "session_id": str,
            "command": str,
            "src_ip": str,
            "timestamp": str,
        }
    """
    pass


async def on_download(download_data: dict) -> None:
    """Called when an attacker downloads a file.

    Args:
        download_data: {
            "session_id": str,
            "url": str,
            "filename": str,
            "sha256": str,
            "src_ip": str,
            "timestamp": str,
        }
    """
    pass

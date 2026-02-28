"""Alert service — send notifications via Apprise on security events."""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import apprise (optional dependency)
try:
    import apprise
    HAS_APPRISE = True
except ImportError:
    HAS_APPRISE = False


def _get_apprise_instance():
    """Create and configure an Apprise instance from settings."""
    if not HAS_APPRISE:
        logger.warning("Apprise not installed, alerts disabled")
        return None

    urls = getattr(settings, "apprise_urls", "") or ""
    if not urls:
        return None

    apobj = apprise.Apprise()
    for url in urls.split(","):
        url = url.strip()
        if url:
            apobj.add(url)

    return apobj


def send_alert(title: str, body: str, notify_type: str = "info") -> bool:
    """Send an alert notification via all configured Apprise channels.

    Args:
        title: Alert title (e.g., "New SSH Session Detected")
        body: Alert body with details
        notify_type: One of "info", "success", "warning", "failure"

    Returns:
        True if sent successfully (or no channels configured), False on error.
    """
    apobj = _get_apprise_instance()
    if apobj is None:
        logger.debug("No Apprise channels configured, skipping alert")
        return True

    type_map = {
        "info": apprise.NotifyType.INFO,
        "success": apprise.NotifyType.SUCCESS,
        "warning": apprise.NotifyType.WARNING,
        "failure": apprise.NotifyType.FAILURE,
    }

    try:
        result = apobj.notify(
            title=title,
            body=body,
            notify_type=type_map.get(notify_type, apprise.NotifyType.INFO),
        )
        if result:
            logger.info("Alert sent: %s", title)
        else:
            logger.warning("Alert send returned False: %s", title)
        return result
    except Exception as e:
        logger.error("Failed to send alert: %s — %s", title, e)
        return False


def format_session_alert(session_data: dict) -> tuple[str, str]:
    """Format a new-session alert message.

    Returns (title, body) tuple.
    """
    src_ip = session_data.get("src_ip", "unknown")
    protocol = session_data.get("protocol", "unknown").upper()
    username = session_data.get("username", "N/A")
    country = session_data.get("country_name", "Unknown")
    city = session_data.get("city", "")

    location = f"{city}, {country}" if city else country

    title = f"HoneyAegis Alert: {protocol} session from {src_ip}"
    body = (
        f"New {protocol} honeypot session detected\n\n"
        f"Source IP: {src_ip}\n"
        f"Location: {location}\n"
        f"Username: {username}\n"
        f"Password: {session_data.get('password', 'N/A')}\n"
        f"Port: {session_data.get('dst_port', 'N/A')}\n"
        f"Time: {session_data.get('timestamp', 'N/A')}\n"
    )

    abuse_score = session_data.get("abuse_confidence_score")
    if abuse_score is not None:
        body += f"AbuseIPDB Score: {abuse_score}%\n"

    return title, body


def format_malware_alert(download_data: dict) -> tuple[str, str]:
    """Format a malware-capture alert message."""
    src_ip = download_data.get("src_ip", "unknown")
    url = download_data.get("url", "N/A")
    sha256 = download_data.get("file_hash_sha256", "N/A")
    filename = download_data.get("filename", "unknown")

    title = f"HoneyAegis MALWARE: {filename} captured from {src_ip}"
    body = (
        f"Malware downloaded by attacker\n\n"
        f"Source IP: {src_ip}\n"
        f"URL: {url}\n"
        f"Filename: {filename}\n"
        f"SHA256: {sha256}\n"
        f"Size: {download_data.get('file_size', 'N/A')} bytes\n"
    )

    return title, body

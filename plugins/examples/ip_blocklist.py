"""Example HoneyAegis plugin — IP blocklist enricher.

This plugin demonstrates how to create a custom enrichment plugin.
When a new session connects, it checks the source IP against a local blocklist.

To use: Copy this file to /plugins/ip_blocklist.py
"""

import logging

logger = logging.getLogger(__name__)

# Example blocklist (in production, load from file or API)
BLOCKLIST = {
    "192.168.1.100",
    "10.0.0.99",
}


def register():
    """Register this plugin with HoneyAegis."""
    return {
        "name": "IP Blocklist",
        "version": "1.0.0",
        "description": "Checks source IPs against a local blocklist",
        "plugin_type": "hook",
        "author": "HoneyAegis Community",
        "enabled": True,
    }


async def on_event(event_type: str, data: dict) -> dict:
    """Process events — check for blocklisted IPs."""
    if event_type != "session.connect":
        return {}

    src_ip = data.get("src_ip", "")
    if src_ip in BLOCKLIST:
        logger.warning("Blocklisted IP detected: %s", src_ip)
        return {"blocklisted": True, "blocklist_source": "local"}

    return {}

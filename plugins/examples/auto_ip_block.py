"""Example HoneyAegis plugin — Auto IP blocker.

Automatically blocks source IPs after repeated failed login attempts.
Uses iptables or nftables to add firewall rules (requires host access).

To use: Copy this file to /plugins/auto_ip_block.py
"""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Track failed attempts per IP
_failed_attempts: dict[str, int] = defaultdict(int)
_blocked_ips: set[str] = set()

# Configuration
MAX_FAILED_ATTEMPTS = 5
BLOCK_COMMAND = "iptables -A INPUT -s {ip} -j DROP"


def register():
    """Register this plugin with HoneyAegis."""
    return {
        "name": "Auto IP Blocker",
        "version": "1.0.0",
        "description": "Blocks IPs after repeated failed login attempts",
        "plugin_type": "hook",
        "author": "HoneyAegis Community",
        "enabled": True,
    }


async def on_event(event_type: str, data: dict) -> dict:
    """Process events — track failed logins and block IPs."""
    if event_type != "login.failed":
        return {}

    src_ip = data.get("src_ip", "")
    if not src_ip or src_ip in _blocked_ips:
        return {}

    _failed_attempts[src_ip] += 1

    if _failed_attempts[src_ip] >= MAX_FAILED_ATTEMPTS:
        _blocked_ips.add(src_ip)
        logger.warning(
            "Auto-blocking IP %s after %d failed attempts",
            src_ip,
            _failed_attempts[src_ip],
        )
        # In production: execute the block command via subprocess
        # subprocess.run(BLOCK_COMMAND.format(ip=src_ip), shell=True, check=True)
        return {
            "auto_blocked": True,
            "failed_attempts": _failed_attempts[src_ip],
            "action": f"Would execute: {BLOCK_COMMAND.format(ip=src_ip)}",
        }

    return {
        "failed_attempts": _failed_attempts[src_ip],
        "threshold": MAX_FAILED_ATTEMPTS,
    }

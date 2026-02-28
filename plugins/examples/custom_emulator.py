"""Example HoneyAegis plugin — Custom honeypot emulator template.

Template for creating a custom service emulator that responds
to attacker commands with realistic-looking output.

To use: Copy this file to /plugins/my_emulator.py and customize.
"""

import logging

logger = logging.getLogger(__name__)

# Fake responses for common commands
FAKE_RESPONSES = {
    "cat /etc/passwd": (
        "root:x:0:0:root:/root:/bin/bash\n"
        "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
        "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
        "mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/false\n"
    ),
    "uname -a": "Linux websvr01 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux",
    "whoami": "root",
    "id": "uid=0(root) gid=0(root) groups=0(root)",
    "ifconfig": (
        "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
        "        inet 10.0.0.5  netmask 255.255.255.0  broadcast 10.0.0.255\n"
    ),
    "hostname": "websvr01",
    "cat /etc/shadow": "cat: /etc/shadow: Permission denied",
}

# Suspicious commands to flag
SUSPICIOUS_COMMANDS = {
    "wget", "curl", "nc", "ncat", "python", "perl", "ruby",
    "chmod", "chown", "crontab", "base64", "dd",
}


def register():
    """Register this plugin with HoneyAegis."""
    return {
        "name": "Custom Emulator Template",
        "version": "1.0.0",
        "description": "Template for custom command emulation and detection",
        "plugin_type": "hook",
        "author": "HoneyAegis Community",
        "enabled": True,
    }


async def on_event(event_type: str, data: dict) -> dict:
    """Process events — enhance command detection and response."""
    if event_type != "command.input":
        return {}

    command = data.get("command", "").strip()
    if not command:
        return {}

    result = {}

    # Check for fake response
    if command in FAKE_RESPONSES:
        result["emulated_response"] = FAKE_RESPONSES[command]

    # Check for suspicious commands
    cmd_base = command.split()[0] if command else ""
    if cmd_base in SUSPICIOUS_COMMANDS:
        result["suspicious"] = True
        result["classification"] = "potential_malware_download" if cmd_base in {"wget", "curl"} else "post_exploitation"
        logger.warning("Suspicious command detected: %s", command)

    return result

# Plugin Examples

This page provides complete, runnable plugin examples for each plugin type. Use these as starting points for your own plugins.

## Example 1: Auto IP Blocker

Located at `plugins/examples/auto_ip_blocker/`, this plugin blocks source IPs after a configurable number of failed login attempts.

```python
PLUGIN_NAME = "auto_ip_blocker"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Block IPs after repeated failed login attempts"

THRESHOLD = 5  # Block after 5 failed attempts
failed_attempts: dict[str, int] = {}

async def on_session_end(session: dict) -> None:
    src_ip = session.get("src_ip")
    if not session.get("auth_success"):
        failed_attempts[src_ip] = failed_attempts.get(src_ip, 0) + 1
        if failed_attempts[src_ip] >= THRESHOLD:
            await block_ip(src_ip)

async def block_ip(ip: str) -> None:
    import asyncio
    await asyncio.create_subprocess_exec(
        "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"
    )
```

## Example 2: Custom Command Emulator

Template for adding custom command responses to the honeypot. This makes the honeypot appear to run specific software:

```python
PLUGIN_NAME = "custom_emulator"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Custom command responses for realistic deception"

COMMANDS = {
    "bitcoin-cli getbalance": "12.45000000",
    "bitcoin-cli listaccounts": '{"": 12.45000000, "backup": 0.00000000}',
    "aws s3 ls": "2026-01-15 bucket-backup\n2026-02-01 bucket-logs\n2026-02-20 bucket-secrets",
    "aws sts get-caller-identity": '{"Account": "123456789012", "Arn": "arn:aws:iam::root"}',
    "kubectl get pods": "NAME                    READY   STATUS    RESTARTS   AGE\nweb-abc123-xyz         1/1     Running   0          5d",
}

async def on_command_executed(command: dict) -> dict | None:
    cmd = command.get("input", "").strip()
    if cmd in COMMANDS:
        return {"output": COMMANDS[cmd]}
    return None
```

## Example 3: GreyNoise Enrichment

An enrichment plugin that queries the GreyNoise Community API for IP context:

```python
PLUGIN_NAME = "enrichment_greynoise"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "GreyNoise IP context enrichment"

import aiohttp

GREYNOISE_API_KEY = ""  # Set via PLUGIN_ENRICHMENT_GREYNOISE_API_KEY env var

async def enrich(event: dict) -> dict:
    src_ip = event.get("src_ip")
    if not src_ip:
        return {}

    async with aiohttp.ClientSession() as client:
        async with client.get(
            f"https://api.greynoise.io/v3/community/{src_ip}",
            headers={"key": GREYNOISE_API_KEY}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "greynoise_noise": data.get("noise", False),
                    "greynoise_riot": data.get("riot", False),
                    "greynoise_classification": data.get("classification", "unknown"),
                    "greynoise_name": data.get("name", ""),
                }
    return {}
```

## Example 4: Custom Alert Channel

A plugin that sends alerts to a custom webhook with a specific payload format:

```python
PLUGIN_NAME = "alert_custom_webhook"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Custom webhook alert channel"

import aiohttp

WEBHOOK_URL = ""      # Set via PLUGIN_ALERT_CUSTOM_WEBHOOK_URL env var
WEBHOOK_API_KEY = ""  # Set via PLUGIN_ALERT_CUSTOM_WEBHOOK_API_KEY env var

async def on_alert(alert: dict) -> None:
    risk = alert.get("risk_score", 0)
    severity = "critical" if risk >= 7 else "high" if risk >= 5 else "medium" if risk >= 3 else "low"

    payload = {
        "source": "honeyaegis",
        "severity": severity,
        "title": f"Honeypot Alert: {alert['protocol'].upper()} from {alert['src_ip']}",
        "description": alert.get("ai_summary", alert.get("message", "")),
        "metadata": {
            "session_id": alert.get("session_id"),
            "sensor": alert.get("sensor_name"),
            "country": alert.get("country"),
        }
    }

    async with aiohttp.ClientSession() as client:
        await client.post(
            WEBHOOK_URL,
            json=payload,
            headers={"X-API-Key": WEBHOOK_API_KEY}
        )
```

## Running the Examples

```bash
# Copy an example to the plugins directory
cp -r plugins/examples/auto_ip_blocker plugins/auto_ip_blocker

# Validate the plugin
honeyaegis plugin validate plugins/auto_ip_blocker

# Restart to load
docker compose restart backend
```

## Related Pages

- [Plugin Development](development.md) -- Full development guide and API reference
- [Plugin Marketplace](marketplace.md) -- Browse community plugins
- [Architecture Overview](../architecture/overview.md) -- How plugins integrate with the stack

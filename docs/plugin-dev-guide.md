# HoneyAegis Plugin Development Guide

Build custom plugins to extend HoneyAegis with new capabilities.

## Plugin Architecture

HoneyAegis plugins are Python modules placed in the `/plugins` directory. They are auto-discovered at startup and can be reloaded via the API.

### Plugin Types

| Type | Description | Required Functions |
|------|-------------|-------------------|
| `hook` | Process events in real-time | `register()`, `on_event()` |
| `enricher` | Enrich event data with external lookups | `register()`, `on_event()` |
| `emulator` | Custom service emulation | `register()`, `on_event()` |
| `exporter` | Export data to external systems | `register()`, `on_event()` |

## Quick Start

### 1. Create a plugin file

```python
# plugins/my_plugin.py
import logging

logger = logging.getLogger(__name__)

def register():
    """Register this plugin with HoneyAegis."""
    return {
        "name": "My Plugin",
        "version": "1.0.0",
        "description": "Does something useful",
        "plugin_type": "hook",
        "author": "Your Name",
        "enabled": True,
    }

async def on_event(event_type: str, data: dict) -> dict:
    """Process incoming events."""
    if event_type == "session.connect":
        logger.info("New session from %s", data.get("src_ip"))
        return {"my_enrichment": True}
    return {}
```

### 2. Place in plugins directory

```bash
cp my_plugin.py /path/to/honeyaegis/plugins/
```

### 3. Reload plugins

```bash
curl -X POST http://localhost:8000/api/v1/plugins/reload \
  -H "Authorization: Bearer <admin-token>"
```

## API Reference

### `register() -> dict`

Called once when the plugin is loaded. Must return a dict with:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | Display name |
| `version` | str | No | Semver version (default: "0.1.0") |
| `description` | str | No | Short description |
| `plugin_type` | str | No | "hook", "enricher", "emulator", "exporter" (default: "hook") |
| `author` | str | No | Author name |
| `enabled` | bool | No | Whether the plugin is active (default: True) |

### `on_event(event_type: str, data: dict) -> dict`

Called for each matching event. Must be an `async` function.

**Event Types:**

| Event | Description | Data Fields |
|-------|-------------|-------------|
| `session.connect` | New session started | `src_ip`, `src_port`, `dst_port`, `protocol` |
| `session.closed` | Session ended | `src_ip`, `duration`, `session_key` |
| `login.success` | Successful login | `src_ip`, `username`, `password` |
| `login.failed` | Failed login | `src_ip`, `username`, `password` |
| `command.input` | Command executed | `src_ip`, `command`, `session_key` |
| `file.download` | File downloaded | `src_ip`, `url`, `filename`, `sha256` |

**Return Value:**

Return a dict with enrichment data to merge into the event. Return `{}` if no enrichment needed.

## Examples

### IP Reputation Checker

```python
import httpx

def register():
    return {
        "name": "IP Reputation",
        "version": "1.0.0",
        "plugin_type": "enricher",
        "enabled": True,
    }

async def on_event(event_type: str, data: dict) -> dict:
    if event_type != "session.connect":
        return {}

    src_ip = data.get("src_ip", "")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"https://api.abuseipdb.com/api/v2/check",
                params={"ipAddress": src_ip},
                headers={"Key": "YOUR_API_KEY", "Accept": "application/json"})
            score = resp.json().get("data", {}).get("abuseConfidenceScore", 0)
            return {"abuse_score": score, "reputation_checked": True}
    except Exception:
        return {}
```

### Slack Notifier

```python
import httpx

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def register():
    return {
        "name": "Slack Notifier",
        "version": "1.0.0",
        "plugin_type": "hook",
        "enabled": True,
    }

async def on_event(event_type: str, data: dict) -> dict:
    if event_type != "login.success":
        return {}

    msg = f":warning: SSH login success from {data.get('src_ip')} as {data.get('username')}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(SLACK_WEBHOOK, json={"text": msg})
    except Exception:
        pass
    return {}
```

## Best Practices

1. **Handle errors gracefully** — never let your plugin crash the main application
2. **Use async** — all `on_event` functions must be async
3. **Be fast** — plugins run in the event processing pipeline; keep execution under 1 second
4. **Log appropriately** — use `logging.getLogger(__name__)` for structured output
5. **Test locally** — run `pytest` with your plugin before deploying
6. **Version your plugins** — use semantic versioning in `register()`

## File Structure

```
plugins/
├── my_plugin.py              # Single-file plugin
├── examples/
│   ├── ip_blocklist.py        # IP blocklist enricher
│   ├── auto_ip_block.py       # Auto IP blocker
│   └── custom_emulator.py     # Command emulator template
└── README.md                  # Plugin directory docs
```

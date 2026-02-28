# Plugin Development Guide

HoneyAegis supports a plugin system that lets you add custom honeypot services, enrichment modules, alert channels, and dashboard widgets.

## Plugin Architecture

Plugins are Python packages that implement one or more HoneyAegis interfaces. They are loaded at startup from the `plugins/` directory or installed via the marketplace.

```
plugins/
  my-plugin/
    plugin.yaml          # Plugin manifest
    __init__.py          # Plugin entry point
    honeypot.py          # Optional: custom honeypot service
    enrichment.py        # Optional: custom enrichment module
    requirements.txt     # Python dependencies
    Dockerfile           # Optional: custom container
```

## Plugin Manifest

Every plugin requires a `plugin.yaml` manifest:

```yaml
name: my-custom-honeypot
version: 1.0.0
description: A custom FTP honeypot with extended logging
author: Your Name
license: MIT
type: honeypot            # honeypot, enrichment, alert, widget
min_honeyaegis_version: 1.0.0
config:
  - name: FTP_PORT
    type: integer
    default: 21
    description: Port for the FTP honeypot
  - name: FTP_BANNER
    type: string
    default: "220 FTP Server Ready"
    description: FTP welcome banner
```

## Plugin Types

| Type | Use Case | Hook Functions |
|---|---|---|
| **Honeypot** | Custom honeypot services | `on_connect`, `on_data`, `on_disconnect` |
| **Enrichment** | Add context to events | `enrich` |
| **Alert** | Custom notification channels | `send` |
| **Widget** | Dashboard components | `render` |
| **Responder** | Take action on events | `on_session_end`, `on_alert` |
| **Emulator** | Custom command responses | `on_command_executed` |

## Plugin API

Plugins receive events through hook functions:

```python
PLUGIN_NAME = "my_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Example custom plugin"

async def on_session_end(session: dict) -> None:
    """Called when an attacker session ends."""
    src_ip = session.get("src_ip")
    # Your custom logic here

async def on_alert(alert: dict) -> None:
    """Called when an alert fires."""
    pass

async def on_command_executed(command: dict) -> dict | None:
    """Called when an attacker runs a command. Return a dict with 'output' to override response."""
    return None
```

## Enrichment Plugin Example

```python
from honeyaegis.plugins import EnrichmentPlugin, SessionEvent

class CustomThreatFeed(EnrichmentPlugin):
    name = "custom-threat-feed"

    async def enrich(self, event: SessionEvent) -> dict:
        result = await self.http_client.get(
            f"https://threats.example.com/api/ip/{event.src_ip}"
        )
        return {
            "custom_threat_score": result["score"],
            "threat_tags": result["tags"]
        }
```

## Loading Plugins

Plugins are auto-discovered from the `plugins/` directory on startup. Reload at runtime via the API:

```
POST /api/v1/plugins/reload
Authorization: Bearer <admin-token>
```

## Testing Plugins

```bash
cd plugins/my-plugin

# Run plugin tests
pytest tests/

# Validate the manifest
honeyaegis plugin validate .

# Test in development mode (hot-reload enabled)
honeyaegis plugin dev .
```

## Packaging and Distribution

```bash
# Package for distribution
honeyaegis plugin pack .
# Creates my-custom-honeypot-1.0.0.hap (HoneyAegis Plugin archive)

# Install a local plugin archive
honeyaegis plugin install my-custom-honeypot-1.0.0.hap
```

## Related Pages

- [Plugin Marketplace](marketplace.md) -- Browse and install community plugins
- [Plugin Examples](examples.md) -- Complete example plugins
- [Architecture Overview](../architecture/overview.md) -- Where plugins fit in the stack

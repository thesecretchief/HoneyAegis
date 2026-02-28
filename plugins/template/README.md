# HoneyAegis Plugin Template

This directory contains a starter template for building HoneyAegis plugins.

## Quick Start

1. Copy `my_plugin.py` to the `/plugins/` directory
2. Rename it to something descriptive (e.g., `slack_notifier.py`)
3. Update `PLUGIN_NAME`, `PLUGIN_VERSION`, and `PLUGIN_DESCRIPTION`
4. Implement the event hooks you need
5. Restart HoneyAegis or reload plugins via the API

## Plugin Structure

```python
# Required metadata
PLUGIN_NAME = "my-plugin"
PLUGIN_VERSION = "0.1.0"
PLUGIN_TYPE = "hook"
PLUGIN_DESCRIPTION = "What this plugin does"

# Optional lifecycle hooks
async def on_load(): ...
async def on_unload(): ...

# Event hooks (implement what you need)
async def on_session_start(session_data): ...
async def on_session_end(session_data): ...
async def on_login_attempt(attempt_data): ...
async def on_command(command_data): ...
async def on_download(download_data): ...
```

## Documentation

See [Plugin Development Guide](../../docs/plugin-dev-guide.md) for the full API reference.

"""Plugin system — discover and load custom honeypot emulators and enrichment plugins.

Plugins are Python modules placed in the /plugins directory. Each plugin must
define a `register()` function that returns a PluginInfo dict.

Example plugin structure:
    plugins/
    ├── my_emulator/
    │   ├── __init__.py     # register() function
    │   └── handler.py      # Plugin logic
    └── my_enricher/
        └── __init__.py

Plugin types:
    - "emulator": Custom honeypot service emulator
    - "enricher": Data enrichment (e.g., threat intel feeds)
    - "exporter": Custom export format
    - "hook": Event processing hook
"""

import importlib
import logging
import sys
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


class PluginInfo(TypedDict, total=False):
    name: str
    version: str
    description: str
    plugin_type: str  # "emulator", "enricher", "exporter", "hook"
    author: str
    config_schema: dict  # JSON Schema for config
    enabled: bool


# Global plugin registry
_plugins: dict[str, PluginInfo] = {}
_plugin_modules: dict[str, object] = {}

PLUGIN_DIR = Path("/app/plugins")
LOCAL_PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent.parent / "plugins"


def discover_plugins() -> list[PluginInfo]:
    """Scan the plugin directory and load all valid plugins."""
    _plugins.clear()
    _plugin_modules.clear()

    plugin_dirs = []
    for base in [PLUGIN_DIR, LOCAL_PLUGIN_DIR]:
        if base.exists() and base.is_dir():
            plugin_dirs.append(base)
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))

    for plugin_base in plugin_dirs:
        for candidate in plugin_base.iterdir():
            if candidate.name.startswith("_") or candidate.name.startswith("."):
                continue

            # Single file plugin
            if candidate.is_file() and candidate.suffix == ".py":
                _load_plugin(candidate.stem, candidate)
            # Package plugin
            elif candidate.is_dir() and (candidate / "__init__.py").exists():
                _load_plugin(candidate.name, candidate / "__init__.py")

    logger.info("Discovered %d plugin(s): %s", len(_plugins), list(_plugins.keys()))
    return list(_plugins.values())


def _load_plugin(name: str, path: Path) -> None:
    """Load a single plugin module and call its register() function."""
    try:
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", str(path))
        if not spec or not spec.loader:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "register"):
            logger.warning("Plugin %s missing register() function, skipping", name)
            return

        info: PluginInfo = module.register()
        info.setdefault("name", name)
        info.setdefault("version", "0.1.0")
        info.setdefault("plugin_type", "hook")
        info.setdefault("enabled", True)

        _plugins[name] = info
        _plugin_modules[name] = module

        logger.info("Loaded plugin: %s v%s (%s)", info["name"], info["version"], info["plugin_type"])

    except Exception as e:
        logger.error("Failed to load plugin %s: %s", name, e)


def get_plugins() -> list[PluginInfo]:
    """Return the list of currently loaded plugins."""
    return list(_plugins.values())


def get_plugin_module(name: str):
    """Get the loaded module for a plugin by name."""
    return _plugin_modules.get(name)


async def run_hook_plugins(event_type: str, data: dict) -> dict:
    """Run all enabled hook plugins for a given event type.

    Hook plugins should define an async `on_event(event_type, data)` function.
    """
    for name, info in _plugins.items():
        if info.get("plugin_type") != "hook" or not info.get("enabled"):
            continue

        module = _plugin_modules.get(name)
        if not module or not hasattr(module, "on_event"):
            continue

        try:
            result = module.on_event(event_type, data)
            if hasattr(result, "__await__"):
                result = await result
            if isinstance(result, dict):
                data.update(result)
        except Exception as e:
            logger.error("Plugin %s hook error: %s", name, e)

    return data

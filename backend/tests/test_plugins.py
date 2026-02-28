"""Tests for plugin system — discovery, loading, and hook execution."""

import uuid
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from app.services.plugin_service import (
    discover_plugins,
    get_plugins,
    get_plugin_module,
    run_hook_plugins,
    _plugins,
    _plugin_modules,
)


# --- Plugin discovery tests ---


def test_discover_plugins_empty_dir():
    """discover_plugins handles empty/missing directories gracefully."""
    with patch("app.services.plugin_service.PLUGIN_DIR", Path("/nonexistent")), \
         patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/also-nonexistent")):
        plugins = discover_plugins()
        assert isinstance(plugins, list)


def test_discover_plugins_loads_file_plugin():
    """discover_plugins loads a single-file Python plugin."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / "test_plug.py"
        plugin_file.write_text(
            'def register():\n'
            '    return {"name": "Test Plugin", "version": "1.0.0", '
            '"description": "A test plugin", "plugin_type": "hook", '
            '"author": "Test", "enabled": True}\n'
        )

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            plugins = discover_plugins()
            names = [p["name"] for p in plugins]
            assert "Test Plugin" in names


def test_discover_plugins_skips_underscore_files():
    """discover_plugins skips files starting with underscore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / "_private.py"
        plugin_file.write_text(
            'def register():\n    return {"name": "Private"}\n'
        )

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            plugins = discover_plugins()
            names = [p["name"] for p in plugins]
            assert "Private" not in names


def test_discover_plugins_skips_dotfiles():
    """discover_plugins skips files starting with dot."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / ".hidden.py"
        plugin_file.write_text(
            'def register():\n    return {"name": "Hidden"}\n'
        )

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            plugins = discover_plugins()
            names = [p["name"] for p in plugins]
            assert "Hidden" not in names


def test_discover_plugins_skips_missing_register():
    """discover_plugins skips modules without register() function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / "no_register.py"
        plugin_file.write_text('x = 1\n')

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            plugins = discover_plugins()
            assert len(plugins) == 0


def test_discover_plugins_sets_defaults():
    """discover_plugins sets default values for missing fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / "minimal.py"
        plugin_file.write_text(
            'def register():\n    return {"name": "Minimal"}\n'
        )

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            plugins = discover_plugins()
            assert len(plugins) == 1
            p = plugins[0]
            assert p["name"] == "Minimal"
            assert p["version"] == "0.1.0"
            assert p["plugin_type"] == "hook"
            assert p["enabled"] is True


def test_discover_plugins_handles_errors():
    """discover_plugins handles plugin load errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_file = Path(tmpdir) / "broken.py"
        plugin_file.write_text('raise RuntimeError("broken")\n')

        with patch("app.services.plugin_service.PLUGIN_DIR", Path(tmpdir)), \
             patch("app.services.plugin_service.LOCAL_PLUGIN_DIR", Path("/nonexistent")):
            # Should not raise
            plugins = discover_plugins()
            assert len(plugins) == 0


# --- Plugin registry tests ---


def test_get_plugins_returns_list():
    """get_plugins returns a list of PluginInfo dicts."""
    result = get_plugins()
    assert isinstance(result, list)


def test_get_plugin_module_missing():
    """get_plugin_module returns None for unknown plugins."""
    result = get_plugin_module("nonexistent_plugin_xyz")
    assert result is None


# --- Hook execution tests ---


@pytest.mark.asyncio
async def test_run_hook_plugins_no_plugins():
    """run_hook_plugins handles no loaded plugins."""
    # Clear plugin registry
    _plugins.clear()
    _plugin_modules.clear()

    data = {"src_ip": "1.2.3.4"}
    result = await run_hook_plugins("session.connect", data)
    assert result == data


@pytest.mark.asyncio
async def test_run_hook_plugins_with_hook():
    """run_hook_plugins executes hook plugin on_event."""
    _plugins.clear()
    _plugin_modules.clear()

    # Register a mock hook plugin
    _plugins["test_hook"] = {
        "name": "test_hook",
        "version": "1.0.0",
        "plugin_type": "hook",
        "enabled": True,
    }

    mock_module = MagicMock()

    async def mock_on_event(event_type, data):
        return {"enriched": True}

    mock_module.on_event = mock_on_event
    _plugin_modules["test_hook"] = mock_module

    data = {"src_ip": "1.2.3.4"}
    result = await run_hook_plugins("session.connect", data)
    assert result.get("enriched") is True
    assert result["src_ip"] == "1.2.3.4"

    # Clean up
    _plugins.clear()
    _plugin_modules.clear()


@pytest.mark.asyncio
async def test_run_hook_plugins_skips_disabled():
    """run_hook_plugins skips disabled plugins."""
    _plugins.clear()
    _plugin_modules.clear()

    _plugins["disabled_hook"] = {
        "name": "disabled_hook",
        "version": "1.0.0",
        "plugin_type": "hook",
        "enabled": False,
    }

    mock_module = MagicMock()
    mock_module.on_event = MagicMock(return_value={"should_not_appear": True})
    _plugin_modules["disabled_hook"] = mock_module

    data = {"src_ip": "1.2.3.4"}
    result = await run_hook_plugins("session.connect", data)
    assert "should_not_appear" not in result

    _plugins.clear()
    _plugin_modules.clear()


@pytest.mark.asyncio
async def test_run_hook_plugins_skips_non_hook_types():
    """run_hook_plugins only runs hook-type plugins."""
    _plugins.clear()
    _plugin_modules.clear()

    _plugins["enricher"] = {
        "name": "enricher",
        "version": "1.0.0",
        "plugin_type": "enricher",
        "enabled": True,
    }

    mock_module = MagicMock()
    mock_module.on_event = MagicMock(return_value={"should_not_appear": True})
    _plugin_modules["enricher"] = mock_module

    data = {"src_ip": "1.2.3.4"}
    result = await run_hook_plugins("session.connect", data)
    assert "should_not_appear" not in result

    _plugins.clear()
    _plugin_modules.clear()


@pytest.mark.asyncio
async def test_run_hook_plugins_handles_errors():
    """run_hook_plugins catches exceptions from faulty plugins."""
    _plugins.clear()
    _plugin_modules.clear()

    _plugins["faulty"] = {
        "name": "faulty",
        "version": "1.0.0",
        "plugin_type": "hook",
        "enabled": True,
    }

    mock_module = MagicMock()

    async def faulty_handler(event_type, data):
        raise RuntimeError("Plugin crashed")

    mock_module.on_event = faulty_handler
    _plugin_modules["faulty"] = mock_module

    data = {"src_ip": "1.2.3.4"}
    # Should not raise
    result = await run_hook_plugins("session.connect", data)
    assert result["src_ip"] == "1.2.3.4"

    _plugins.clear()
    _plugin_modules.clear()


# --- Example plugin tests ---


def test_example_ip_blocklist_register():
    """Example IP blocklist plugin registers correctly."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ip_blocklist",
        str(Path(__file__).resolve().parent.parent.parent / "plugins" / "examples" / "ip_blocklist.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    info = module.register()
    assert info["name"] == "IP Blocklist"
    assert info["version"] == "1.0.0"
    assert info["plugin_type"] == "hook"
    assert info["enabled"] is True


@pytest.mark.asyncio
async def test_example_ip_blocklist_detects_blocked_ip():
    """Example IP blocklist plugin detects blocklisted IPs."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ip_blocklist",
        str(Path(__file__).resolve().parent.parent.parent / "plugins" / "examples" / "ip_blocklist.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = await module.on_event("session.connect", {"src_ip": "192.168.1.100"})
    assert result.get("blocklisted") is True


@pytest.mark.asyncio
async def test_example_ip_blocklist_allows_clean_ip():
    """Example IP blocklist plugin allows non-blocked IPs."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ip_blocklist",
        str(Path(__file__).resolve().parent.parent.parent / "plugins" / "examples" / "ip_blocklist.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = await module.on_event("session.connect", {"src_ip": "8.8.8.8"})
    assert result == {}

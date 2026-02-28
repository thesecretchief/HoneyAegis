"""Tests for the hosted console API stubs."""

import pytest
from app.api.console import (
    ConsoleStats,
    DeploymentRegistration,
    DeploymentStatus,
    LicenseInfo,
)


class TestConsoleSchemas:
    """Test console API Pydantic schemas."""

    def test_console_stats_defaults(self):
        stats = ConsoleStats(
            total_deployments=0,
            total_sensors=0,
            total_sessions_24h=0,
            total_alerts_24h=0,
            deployments_online=0,
            deployments_offline=0,
        )
        assert stats.total_deployments == 0
        assert stats.total_sensors == 0
        assert stats.deployments_online == 0

    def test_deployment_registration(self):
        reg = DeploymentRegistration(
            name="production-hub",
            url="https://hub.example.com",
            version="1.0.0",
            sensor_count=5,
        )
        assert reg.name == "production-hub"
        assert reg.url == "https://hub.example.com"
        assert reg.version == "1.0.0"
        assert reg.sensor_count == 5

    def test_deployment_registration_defaults(self):
        reg = DeploymentRegistration(
            name="test",
            url="http://localhost:8000",
            version="1.0.0",
        )
        assert reg.sensor_count == 0

    def test_deployment_status(self):
        status = DeploymentStatus(
            deployment_id="dep-001",
            name="prod",
            url="https://prod.example.com",
            version="1.0.0",
            status="online",
            last_seen="2026-02-28T00:00:00Z",
            sensor_count=3,
            session_count_24h=150,
            alert_count_24h=12,
        )
        assert status.deployment_id == "dep-001"
        assert status.status == "online"
        assert status.session_count_24h == 150

    def test_license_info_community(self):
        license = LicenseInfo(
            tier="community",
            max_sensors=999,
            max_deployments=999,
            features=["unlimited-sessions", "all-honeypots"],
            expires_at=None,
        )
        assert license.tier == "community"
        assert license.max_sensors == 999
        assert license.expires_at is None
        assert "unlimited-sessions" in license.features

    def test_license_info_enterprise(self):
        license = LicenseInfo(
            tier="enterprise",
            max_sensors=50,
            max_deployments=10,
            features=["sla", "priority-support"],
            expires_at="2027-01-01T00:00:00Z",
        )
        assert license.tier == "enterprise"
        assert license.expires_at == "2027-01-01T00:00:00Z"


class TestPluginTemplate:
    """Test that plugin template metadata is valid."""

    def test_plugin_template_importable(self):
        import importlib.util
        import os
        plugin_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "plugins", "template", "my_plugin.py"
        )
        spec = importlib.util.spec_from_file_location(
            "my_plugin",
            os.path.abspath(plugin_path),
        )
        assert spec is not None

    def test_plugin_template_has_required_metadata(self):
        import importlib.util
        import os
        plugin_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "plugins", "template", "my_plugin.py"
        )
        spec = importlib.util.spec_from_file_location(
            "my_plugin",
            os.path.abspath(plugin_path),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, "PLUGIN_NAME")
        assert hasattr(module, "PLUGIN_VERSION")
        assert hasattr(module, "PLUGIN_TYPE")
        assert hasattr(module, "PLUGIN_DESCRIPTION")
        assert module.PLUGIN_TYPE in ("hook", "enricher", "emulator")

"""Tests for the anonymous usage analytics service."""

from app.services.analytics_service import (
    TelemetryPayload,
    _generate_instance_id,
    _detect_deployment_type,
    build_telemetry_payload,
)


class TestTelemetryPayload:
    """Test telemetry payload dataclass."""

    def test_payload_creation(self):
        payload = TelemetryPayload(
            version="1.0.0",
            deployment_type="docker",
            os_info="Linux 5.15",
            arch="x86_64",
            profile="light",
            sensor_count=3,
            plugin_count=2,
            uptime_hours=1.5,
            instance_id="abc123",
        )
        assert payload.version == "1.0.0"
        assert payload.deployment_type == "docker"
        assert payload.sensor_count == 3
        assert payload.uptime_hours == 1.5


class TestInstanceId:
    """Test anonymous instance ID generation."""

    def test_instance_id_is_hex(self):
        instance_id = _generate_instance_id()
        assert all(c in "0123456789abcdef" for c in instance_id)

    def test_instance_id_length(self):
        instance_id = _generate_instance_id()
        assert len(instance_id) == 16

    def test_instance_id_deterministic(self):
        id1 = _generate_instance_id()
        id2 = _generate_instance_id()
        assert id1 == id2


class TestDeploymentDetection:
    """Test deployment type detection."""

    def test_returns_string(self):
        result = _detect_deployment_type()
        assert isinstance(result, str)
        assert result in ("docker", "kubernetes", "rpi", "bare-metal")


class TestBuildPayload:
    """Test telemetry payload builder."""

    def test_build_with_defaults(self):
        payload = build_telemetry_payload()
        assert payload.version == "1.0.0"
        assert payload.sensor_count == 0
        assert payload.plugin_count == 0
        assert payload.uptime_hours >= 0
        assert len(payload.instance_id) == 16

    def test_build_with_counts(self):
        payload = build_telemetry_payload(sensor_count=5, plugin_count=3)
        assert payload.sensor_count == 5
        assert payload.plugin_count == 3

    def test_payload_has_os_info(self):
        payload = build_telemetry_payload()
        assert payload.os_info  # non-empty string
        assert payload.arch  # non-empty string

    def test_payload_profile(self):
        payload = build_telemetry_payload()
        assert payload.profile in ("light", "full")

    def test_payload_deployment_type(self):
        payload = build_telemetry_payload()
        assert payload.deployment_type in (
            "docker", "kubernetes", "rpi", "bare-metal"
        )

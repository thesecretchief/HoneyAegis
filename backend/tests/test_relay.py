"""Tests for the SaaS relay API."""

from app.api.relay import (
    SensorHeartbeat,
    RelayEvent,
    RelayBatch,
    RelayStatus,
    _connected_sensors,
)


class TestRelaySchemas:
    """Test relay API Pydantic schemas."""

    def test_sensor_heartbeat_defaults(self):
        hb = SensorHeartbeat(sensor_id="sensor-01")
        assert hb.sensor_id == "sensor-01"
        assert hb.hostname is None
        assert hb.version == "1.0.0"
        assert hb.uptime_seconds == 0
        assert hb.sessions_captured == 0
        assert hb.cpu_percent == 0.0
        assert hb.memory_mb == 0.0
        assert hb.disk_percent == 0.0

    def test_sensor_heartbeat_full(self):
        hb = SensorHeartbeat(
            sensor_id="sensor-02",
            hostname="rpi-office",
            ip_address="192.168.1.50",
            version="1.0.0",
            uptime_seconds=3600,
            sessions_captured=42,
            cpu_percent=23.5,
            memory_mb=512.0,
            disk_percent=45.2,
        )
        assert hb.sensor_id == "sensor-02"
        assert hb.hostname == "rpi-office"
        assert hb.ip_address == "192.168.1.50"
        assert hb.sessions_captured == 42
        assert hb.cpu_percent == 23.5

    def test_relay_event_defaults(self):
        event = RelayEvent(
            sensor_id="sensor-01",
            event_type="login_attempt",
            timestamp="2026-02-28T12:00:00Z",
        )
        assert event.sensor_id == "sensor-01"
        assert event.event_type == "login_attempt"
        assert event.protocol == "ssh"
        assert event.src_ip is None
        assert event.command is None

    def test_relay_event_full(self):
        event = RelayEvent(
            sensor_id="sensor-01",
            event_type="command_input",
            timestamp="2026-02-28T12:00:00Z",
            src_ip="10.0.0.5",
            src_port=54321,
            dst_port=22,
            protocol="ssh",
            username="root",
            password="admin123",
            command="whoami",
            success=True,
            session_id="sess-abc",
        )
        assert event.src_ip == "10.0.0.5"
        assert event.command == "whoami"
        assert event.success is True
        assert event.session_id == "sess-abc"

    def test_relay_batch(self):
        batch = RelayBatch(
            sensor_id="sensor-01",
            events=[
                RelayEvent(
                    sensor_id="sensor-01",
                    event_type="login_attempt",
                    timestamp="2026-02-28T12:00:00Z",
                ),
                RelayEvent(
                    sensor_id="sensor-01",
                    event_type="command_input",
                    timestamp="2026-02-28T12:00:01Z",
                    command="ls",
                ),
            ],
        )
        assert len(batch.events) == 2
        assert batch.sensor_id == "sensor-01"

    def test_relay_batch_empty(self):
        batch = RelayBatch(sensor_id="sensor-01", events=[])
        assert len(batch.events) == 0

    def test_relay_status(self):
        status = RelayStatus(
            enabled=True,
            connected_sensors=5,
            events_relayed_24h=1234,
            uptime_seconds=7200,
        )
        assert status.enabled is True
        assert status.connected_sensors == 5
        assert status.events_relayed_24h == 1234


class TestRelayTokenValidation:
    """Test sensor token validation logic."""

    def test_validate_token_missing(self):
        from fastapi import HTTPException
        from app.api.relay import _validate_sensor_token

        try:
            _validate_sensor_token(None)
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 401

    def test_validate_token_no_bearer(self):
        from fastapi import HTTPException
        from app.api.relay import _validate_sensor_token

        try:
            _validate_sensor_token("Basic abc123")
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 401

    def test_validate_token_empty_bearer(self):
        from fastapi import HTTPException
        from app.api.relay import _validate_sensor_token

        try:
            _validate_sensor_token("Bearer ")
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 401

    def test_validate_token_valid(self):
        from app.api.relay import _validate_sensor_token

        token = _validate_sensor_token("Bearer my-sensor-token-123")
        assert token == "my-sensor-token-123"

"""Tests for sensor schemas and registration validation."""

from app.schemas.sensor import (
    SensorRegisterRequest,
    SensorHeartbeatRequest,
    SensorResponse,
)


def test_sensor_register_request_minimal():
    req = SensorRegisterRequest(sensor_id="s1", name="Test Sensor")
    assert req.sensor_id == "s1"
    assert req.name == "Test Sensor"
    assert req.hostname is None
    assert req.ip_address is None
    assert req.config is None


def test_sensor_register_request_full():
    req = SensorRegisterRequest(
        sensor_id="sensor-rpi-01",
        name="Office RPi",
        hostname="rpi-office",
        ip_address="192.168.1.50",
        config={"honeypots": ["cowrie"]},
    )
    assert req.sensor_id == "sensor-rpi-01"
    assert req.hostname == "rpi-office"
    assert req.config == {"honeypots": ["cowrie"]}


def test_heartbeat_request():
    req = SensorHeartbeatRequest(sensor_id="s1", ip_address="10.0.0.5")
    assert req.sensor_id == "s1"
    assert req.ip_address == "10.0.0.5"


def test_heartbeat_request_no_ip():
    req = SensorHeartbeatRequest(sensor_id="s1")
    assert req.ip_address is None

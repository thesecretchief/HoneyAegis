"""Tests for GeoIP service."""

import pytest
from app.services.geoip_service import _is_private_ip, lookup_ip


def test_private_ip_detection():
    assert _is_private_ip("192.168.1.1") is True
    assert _is_private_ip("10.0.0.1") is True
    assert _is_private_ip("172.16.0.1") is True
    assert _is_private_ip("127.0.0.1") is True
    assert _is_private_ip("8.8.8.8") is False
    assert _is_private_ip("1.1.1.1") is False


def test_private_ip_invalid():
    assert _is_private_ip("not-an-ip") is True
    assert _is_private_ip("") is True


@pytest.mark.asyncio
async def test_lookup_private_ip():
    result = await lookup_ip("192.168.1.100")
    assert result["country_code"] == "XX"
    assert result["country_name"] == "Private Network"
    assert result["latitude"] == 0.0
    assert result["longitude"] == 0.0


@pytest.mark.asyncio
async def test_lookup_loopback():
    result = await lookup_ip("127.0.0.1")
    assert result["country_code"] == "XX"
    assert result["country_name"] == "Private Network"

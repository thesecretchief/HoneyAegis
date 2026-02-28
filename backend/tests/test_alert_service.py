"""Tests for alert service."""

from app.services.alert_service import format_session_alert, format_malware_alert


def test_format_session_alert():
    session_data = {
        "src_ip": "45.33.32.156",
        "protocol": "ssh",
        "username": "root",
        "password": "admin123",
        "dst_port": 22,
        "timestamp": "2026-01-15T10:30:00",
        "country_name": "United States",
        "city": "Fremont",
    }

    title, body = format_session_alert(session_data)
    assert "45.33.32.156" in title
    assert "SSH" in title
    assert "root" in body
    assert "admin123" in body
    assert "Fremont, United States" in body


def test_format_session_alert_no_city():
    session_data = {
        "src_ip": "1.2.3.4",
        "protocol": "telnet",
        "username": "admin",
        "country_name": "China",
    }

    title, body = format_session_alert(session_data)
    assert "TELNET" in title
    assert "China" in body


def test_format_malware_alert():
    download_data = {
        "src_ip": "45.33.32.156",
        "url": "http://evil.com/payload.sh",
        "filename": "payload.sh",
        "file_hash_sha256": "abc123def456",
        "file_size": 4096,
    }

    title, body = format_malware_alert(download_data)
    assert "payload.sh" in title
    assert "MALWARE" in title
    assert "abc123def456" in body
    assert "4096" in body


def test_format_session_alert_with_abuse_score():
    session_data = {
        "src_ip": "45.33.32.156",
        "protocol": "ssh",
        "abuse_confidence_score": 85,
    }

    title, body = format_session_alert(session_data)
    assert "85%" in body

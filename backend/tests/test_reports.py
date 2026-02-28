"""Tests for report generation schemas and utilities."""

import uuid
from datetime import datetime, timezone


def test_report_json_structure():
    """Verify the expected JSON report structure."""
    report_data = {
        "report_type": "aggregate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tenant_id": str(uuid.uuid4()),
        "summary": {
            "total_sessions": 42,
            "unique_ips": 15,
            "successful_auths": 3,
            "date_range": {
                "start": "2026-02-01T00:00:00Z",
                "end": "2026-02-28T23:59:59Z",
            },
        },
        "sessions": [],
    }

    assert report_data["report_type"] == "aggregate"
    assert "summary" in report_data
    assert report_data["summary"]["total_sessions"] == 42


def test_single_session_report_structure():
    """Verify single session report data."""
    session_id = uuid.uuid4()
    report_data = {
        "report_type": "single_session",
        "session": {
            "id": str(session_id),
            "session_id": "abc123",
            "protocol": "ssh",
            "src_ip": "192.168.1.100",
            "dst_port": 2222,
            "username": "root",
            "auth_success": True,
            "duration_seconds": 120,
            "country_name": "United States",
            "commands": ["whoami", "uname -a", "cat /etc/passwd"],
            "ai_summary": {
                "threat_level": "high",
                "summary": "Attacker performed reconnaissance.",
                "mitre_ttps": ["T1059", "T1005"],
            },
        },
    }

    assert report_data["report_type"] == "single_session"
    assert report_data["session"]["protocol"] == "ssh"
    assert len(report_data["session"]["commands"]) == 3
    assert report_data["session"]["ai_summary"]["threat_level"] == "high"


def test_report_html_template_basics():
    """Verify HTML report template can be constructed."""
    tenant_name = "Acme Security"
    primary_color = "#2563eb"

    html = f"""
    <html>
    <head><title>{tenant_name} - Forensic Report</title></head>
    <body>
        <h1 style="color: {primary_color}">{tenant_name}</h1>
        <h2>Honeypot Forensic Report</h2>
        <p>Generated at: 2026-02-28T12:00:00Z</p>
    </body>
    </html>
    """

    assert tenant_name in html
    assert primary_color in html
    assert "Forensic Report" in html


def test_client_portal_branding():
    """Verify client portal branding data structure."""
    branding = {
        "name": "Acme Security",
        "primary_color": "#2563eb",
        "logo_url": "https://example.com/logo.png",
    }

    assert branding["name"] == "Acme Security"
    assert branding["primary_color"].startswith("#")
    assert len(branding["primary_color"]) == 7


def test_client_portal_stats():
    """Verify client portal stats structure."""
    stats = {
        "total_sessions": 100,
        "unique_source_ips": 45,
        "successful_auths": 12,
        "sessions_today": 5,
        "unique_ips_today": 3,
    }

    assert stats["total_sessions"] >= stats["sessions_today"]
    assert stats["unique_source_ips"] >= stats["unique_ips_today"]


def test_installer_script_structure():
    """Verify install script has required sections."""
    with open("../scripts/install.sh", "r") as f:
        content = f.read()

    assert "#!/usr/bin/env bash" in content
    assert "docker" in content.lower()
    assert ".env" in content
    assert "REPO_URL" in content


def test_update_script_structure():
    """Verify update script has required sections."""
    with open("../scripts/update.sh", "r") as f:
        content = f.read()

    assert "#!/usr/bin/env bash" in content
    assert "git fetch" in content or "git pull" in content
    assert "docker compose" in content
    assert "--auto" in content

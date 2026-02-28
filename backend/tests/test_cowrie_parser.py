"""Tests for Cowrie log parser."""

from app.services.cowrie_parser import parse_cowrie_log_line


def test_parse_valid_cowrie_line():
    line = '{"eventid":"cowrie.session.connect","session":"abc123","timestamp":"2026-01-15T10:30:00","src_ip":"192.168.1.100","src_port":54321,"dst_port":2222}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["event_id"] == "cowrie.session.connect"
    assert result["session"] == "abc123"
    assert result["src_ip"] == "192.168.1.100"
    assert result["src_port"] == 54321


def test_parse_invalid_json():
    result = parse_cowrie_log_line("not json at all")
    assert result is None


def test_parse_login_attempt():
    line = '{"eventid":"cowrie.login.success","session":"abc123","timestamp":"2026-01-15T10:30:05","src_ip":"192.168.1.100","username":"root","password":"toor"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["username"] == "root"
    assert result["password"] == "toor"


def test_parse_command_input():
    line = '{"eventid":"cowrie.command.input","session":"abc123","timestamp":"2026-01-15T10:31:00","src_ip":"192.168.1.100","input":"cat /etc/passwd"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["input"] == "cat /etc/passwd"

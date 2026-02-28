"""Tests for the Cowrie log parser (used by ingestion service)."""

from app.services.cowrie_parser import parse_cowrie_log_line


def test_parse_session_connect():
    line = '{"eventid":"cowrie.session.connect","session":"abc123","timestamp":"2026-01-15T10:30:00","src_ip":"192.168.1.100","src_port":54321,"dst_port":2222,"protocol":"ssh"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["event_id"] == "cowrie.session.connect"
    assert result["session"] == "abc123"
    assert result["src_ip"] == "192.168.1.100"
    assert result["dst_port"] == 2222


def test_parse_session_closed():
    line = '{"eventid":"cowrie.session.closed","session":"abc123","timestamp":"2026-01-15T10:35:00","src_ip":"192.168.1.100","duration":300.5}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["event_id"] == "cowrie.session.closed"


def test_parse_login_success():
    line = '{"eventid":"cowrie.login.success","session":"abc123","timestamp":"2026-01-15T10:30:05","src_ip":"192.168.1.100","username":"root","password":"toor"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["username"] == "root"
    assert result["password"] == "toor"


def test_parse_command():
    line = '{"eventid":"cowrie.command.input","session":"abc123","timestamp":"2026-01-15T10:31:00","src_ip":"192.168.1.100","input":"cat /etc/passwd"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["input"] == "cat /etc/passwd"


def test_parse_file_download():
    line = '{"eventid":"cowrie.session.file_download","session":"abc123","timestamp":"2026-01-15T10:32:00","src_ip":"192.168.1.100","url":"http://evil.com/bot.sh","filename":"bot.sh","shasum":"deadbeef"}'
    result = parse_cowrie_log_line(line)
    assert result is not None
    assert result["raw"]["url"] == "http://evil.com/bot.sh"
    assert result["raw"]["shasum"] == "deadbeef"


def test_parse_invalid():
    assert parse_cowrie_log_line("not json") is None
    assert parse_cowrie_log_line("") is None
    assert parse_cowrie_log_line("{broken json") is None

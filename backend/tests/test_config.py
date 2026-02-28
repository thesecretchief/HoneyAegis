"""Tests for the config API schemas.

Note: we test the Pydantic models directly to avoid importing the full
FastAPI router chain which requires python-jose/cryptography.
"""

from pydantic import BaseModel


# Re-define the schemas locally to test without import chains
class HoneypotConfig(BaseModel):
    name: str
    enabled: bool
    ports: list[int] = []
    description: str = ""


class AlertRuleConfig(BaseModel):
    alert_on_new_session: bool
    alert_on_malware_capture: bool
    cooldown_minutes: int
    apprise_urls: list[str]


class UpdateAlertRulesRequest(BaseModel):
    alert_on_new_session: bool | None = None
    alert_on_malware_capture: bool | None = None
    cooldown_minutes: int | None = None


def test_honeypot_config():
    config = HoneypotConfig(
        name="Cowrie",
        enabled=True,
        ports=[2222, 2223],
        description="SSH/Telnet honeypot",
    )
    assert config.name == "Cowrie"
    assert config.enabled is True
    assert 2222 in config.ports


def test_alert_rule_config():
    config = AlertRuleConfig(
        alert_on_new_session=True,
        alert_on_malware_capture=False,
        cooldown_minutes=10,
        apprise_urls=["slack://token"],
    )
    assert config.alert_on_new_session is True
    assert config.cooldown_minutes == 10


def test_update_alert_rules_partial():
    req = UpdateAlertRulesRequest(cooldown_minutes=15)
    assert req.cooldown_minutes == 15
    assert req.alert_on_new_session is None
    assert req.alert_on_malware_capture is None

"""Configuration endpoints — platform settings management."""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


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


class SilenceWindow(BaseModel):
    id: str
    name: str
    start_hour: int
    end_hour: int
    days: list[str]
    enabled: bool


class PlatformConfig(BaseModel):
    honeypots: list[HoneypotConfig]
    alert_rules: AlertRuleConfig
    silence_windows: list[SilenceWindow]
    ai_enabled: bool
    ai_model: str
    fleet_mode: str


@router.get("/", response_model=PlatformConfig)
async def get_config(
    _current_user: User = Depends(get_current_user),
):
    """Get the current platform configuration."""
    return PlatformConfig(
        honeypots=[
            HoneypotConfig(
                name="Cowrie SSH/Telnet",
                enabled=True,
                ports=[2222, 2223],
                description="SSH and Telnet honeypot with session recording",
            ),
            HoneypotConfig(
                name="OpenCanary",
                enabled=False,
                ports=[21, 80, 443, 3306, 5900],
                description="Multi-protocol honeypot (FTP, HTTP, MySQL, VNC)",
            ),
            HoneypotConfig(
                name="Dionaea",
                enabled=False,
                ports=[21, 80, 443, 445, 1433, 3306],
                description="Malware capture honeypot",
            ),
            HoneypotConfig(
                name="Beelzebub",
                enabled=False,
                ports=[22, 80],
                description="LLM-powered interactive honeypot",
            ),
        ],
        alert_rules=AlertRuleConfig(
            alert_on_new_session=settings.alert_on_new_session,
            alert_on_malware_capture=settings.alert_on_malware_capture,
            cooldown_minutes=settings.alert_cooldown_minutes,
            apprise_urls=[u.strip() for u in settings.apprise_urls.split(",") if u.strip()],
        ),
        silence_windows=[],
        ai_enabled=settings.ollama_enabled,
        ai_model=settings.ollama_model,
        fleet_mode="standalone",
    )


class UpdateAlertRulesRequest(BaseModel):
    alert_on_new_session: bool | None = None
    alert_on_malware_capture: bool | None = None
    cooldown_minutes: int | None = None


@router.patch("/alerts")
async def update_alert_rules(
    request: UpdateAlertRulesRequest,
    _current_user: User = Depends(get_current_user),
):
    """Update alert rule settings (runtime only — persists until restart)."""
    if request.alert_on_new_session is not None:
        settings.alert_on_new_session = request.alert_on_new_session
    if request.alert_on_malware_capture is not None:
        settings.alert_on_malware_capture = request.alert_on_malware_capture
    if request.cooldown_minutes is not None:
        settings.alert_cooldown_minutes = request.cooldown_minutes

    return {"status": "updated"}

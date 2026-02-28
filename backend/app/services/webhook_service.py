"""Webhook execution service — sends HTTP requests for auto-response hooks."""

import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook

logger = logging.getLogger(__name__)


async def execute_webhook(hook: Webhook, payload: dict) -> int:
    """Execute a single webhook and return the HTTP status code."""
    headers = dict(hook.headers or {})
    headers.setdefault("Content-Type", "application/json")
    headers["X-HoneyAegis-Event"] = payload.get("event", "unknown")

    if hook.secret:
        import hashlib
        import hmac
        import json

        body = json.dumps(payload, sort_keys=True)
        sig = hmac.new(
            hook.secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()
        headers["X-HoneyAegis-Signature"] = f"sha256={sig}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(
                method=hook.http_method or "POST",
                url=hook.url,
                json=payload,
                headers=headers,
            )
        logger.info(
            "Webhook %s executed: %s -> %d",
            hook.name, hook.url, response.status_code,
        )
        return response.status_code
    except httpx.TimeoutException:
        logger.warning("Webhook %s timed out: %s", hook.name, hook.url)
        return 504
    except Exception as e:
        logger.error("Webhook %s failed: %s", hook.name, e)
        return 500


async def fire_webhooks(
    db: AsyncSession,
    tenant_id,
    trigger_type: str,
    severity: str,
    payload: dict,
) -> None:
    """Find and execute all matching webhooks for a tenant."""
    query = select(Webhook).where(
        Webhook.tenant_id == tenant_id,
        Webhook.is_active.is_(True),
        Webhook.trigger_on == trigger_type,
    )
    result = await db.execute(query)
    webhooks = result.scalars().all()

    for hook in webhooks:
        # Check severity filter
        if hook.severity_filter and hook.severity_filter != severity:
            continue

        status_code = await execute_webhook(hook, payload)
        hook.execution_count = (hook.execution_count or 0) + 1
        hook.last_executed_at = datetime.now(timezone.utc)
        hook.last_status_code = status_code

    if webhooks:
        await db.commit()

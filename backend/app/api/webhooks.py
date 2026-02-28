"""Webhook endpoints — auto-response hook management."""

import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.webhook import Webhook

logger = logging.getLogger(__name__)
router = APIRouter()


class WebhookCreate(BaseModel):
    name: str
    url: str
    description: str | None = None
    secret: str | None = None
    trigger_on: str = "alert"
    severity_filter: str | None = None
    http_method: str = "POST"
    headers: dict = {}
    payload_template: dict | None = None


class WebhookUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    description: str | None = None
    trigger_on: str | None = None
    severity_filter: str | None = None
    is_active: bool | None = None
    headers: dict | None = None
    payload_template: dict | None = None


@router.get("/")
async def list_webhooks(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    count_q = select(func.count(Webhook.id)).where(Webhook.tenant_id == tenant_id)
    total = (await db.execute(count_q)).scalar() or 0

    query = (
        select(Webhook)
        .where(Webhook.tenant_id == tenant_id)
        .order_by(Webhook.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    hooks = result.scalars().all()

    return {
        "webhooks": [
            {
                "id": str(h.id),
                "name": h.name,
                "url": h.url,
                "description": h.description,
                "trigger_on": h.trigger_on,
                "severity_filter": h.severity_filter,
                "http_method": h.http_method,
                "is_active": h.is_active,
                "execution_count": h.execution_count,
                "last_executed_at": h.last_executed_at.isoformat() if h.last_executed_at else None,
                "last_status_code": h.last_status_code,
                "created_at": h.created_at.isoformat(),
            }
            for h in hooks
        ],
        "total": total,
    }


@router.post("/")
async def create_webhook(
    request: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    hook = Webhook(
        id=uuid4(),
        tenant_id=tenant_id,
        name=request.name,
        url=request.url,
        description=request.description,
        secret=request.secret,
        trigger_on=request.trigger_on,
        severity_filter=request.severity_filter,
        http_method=request.http_method,
        headers=request.headers,
        payload_template=request.payload_template,
    )
    db.add(hook)
    await db.commit()
    await db.refresh(hook)

    logger.info("Created webhook: %s -> %s (trigger=%s)", hook.name, hook.url, hook.trigger_on)
    return {"id": str(hook.id), "name": hook.name, "url": hook.url}


@router.patch("/{webhook_id}")
async def update_webhook(
    webhook_id: UUID,
    request: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id, Webhook.tenant_id == tenant_id
        )
    )
    hook = result.scalar_one_or_none()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    for field in ["name", "url", "description", "trigger_on", "severity_filter", "is_active", "headers", "payload_template"]:
        val = getattr(request, field, None)
        if val is not None:
            setattr(hook, field, val)

    await db.commit()
    await db.refresh(hook)
    return {"status": "updated", "id": str(hook.id)}


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id, Webhook.tenant_id == tenant_id
        )
    )
    hook = result.scalar_one_or_none()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(hook)
    await db.commit()
    return {"status": "deleted"}


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Send a test payload to verify webhook connectivity."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id, Webhook.tenant_id == tenant_id
        )
    )
    hook = result.scalar_one_or_none()
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    from app.services.webhook_service import execute_webhook

    test_payload = {
        "event": "test",
        "message": "HoneyAegis webhook test",
        "webhook_name": hook.name,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }

    status_code = await execute_webhook(hook, test_payload)
    return {"status": "sent", "response_code": status_code}

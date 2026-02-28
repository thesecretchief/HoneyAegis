"""Honey token endpoints — manage decoy credentials and files."""

import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_tenant_id
from app.models.honey_token import HoneyToken

logger = logging.getLogger(__name__)
router = APIRouter()


class HoneyTokenCreate(BaseModel):
    name: str
    token_type: str = "credential"
    description: str | None = None
    username: str | None = None
    password: str | None = None
    filename: str | None = None
    file_path: str | None = None
    alert_severity: str = "critical"
    webhook_url: str | None = None
    metadata: dict = {}


class HoneyTokenUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    alert_severity: str | None = None
    webhook_url: str | None = None


class HoneyTokenResponse(BaseModel):
    id: UUID
    tenant_id: UUID | None
    token_type: str
    name: str
    description: str | None
    username: str | None
    password: str | None
    filename: str | None
    is_active: bool
    trigger_count: int
    last_triggered_at: str | None
    alert_severity: str
    webhook_url: str | None
    created_at: str
    model_config = {"from_attributes": True}


@router.get("/")
async def list_honey_tokens(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    count_q = select(func.count(HoneyToken.id)).where(
        HoneyToken.tenant_id == tenant_id
    )
    total = (await db.execute(count_q)).scalar() or 0

    query = (
        select(HoneyToken)
        .where(HoneyToken.tenant_id == tenant_id)
        .order_by(HoneyToken.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    tokens = result.scalars().all()

    return {
        "tokens": [
            {
                "id": str(t.id),
                "token_type": t.token_type,
                "name": t.name,
                "description": t.description,
                "username": t.username,
                "password": t.password,
                "filename": t.filename,
                "is_active": t.is_active,
                "trigger_count": t.trigger_count,
                "last_triggered_at": t.last_triggered_at.isoformat() if t.last_triggered_at else None,
                "alert_severity": t.alert_severity,
                "webhook_url": t.webhook_url,
                "created_at": t.created_at.isoformat(),
            }
            for t in tokens
        ],
        "total": total,
    }


@router.post("/")
async def create_honey_token(
    request: HoneyTokenCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    token = HoneyToken(
        id=uuid4(),
        tenant_id=tenant_id,
        token_type=request.token_type,
        name=request.name,
        description=request.description,
        username=request.username,
        password=request.password,
        filename=request.filename,
        file_path=request.file_path,
        alert_severity=request.alert_severity,
        webhook_url=request.webhook_url,
        extra_data=request.metadata,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    logger.info("Created honey token: %s (type=%s)", token.name, token.token_type)
    return {
        "id": str(token.id),
        "name": token.name,
        "token_type": token.token_type,
        "created_at": token.created_at.isoformat(),
    }


@router.patch("/{token_id}")
async def update_honey_token(
    token_id: UUID,
    request: HoneyTokenUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(HoneyToken).where(
            HoneyToken.id == token_id, HoneyToken.tenant_id == tenant_id
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Honey token not found")

    if request.name is not None:
        token.name = request.name
    if request.description is not None:
        token.description = request.description
    if request.is_active is not None:
        token.is_active = request.is_active
    if request.alert_severity is not None:
        token.alert_severity = request.alert_severity
    if request.webhook_url is not None:
        token.webhook_url = request.webhook_url

    await db.commit()
    await db.refresh(token)
    return {"status": "updated", "id": str(token.id)}


@router.delete("/{token_id}")
async def delete_honey_token(
    token_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(HoneyToken).where(
            HoneyToken.id == token_id, HoneyToken.tenant_id == tenant_id
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Honey token not found")

    await db.delete(token)
    await db.commit()
    return {"status": "deleted"}

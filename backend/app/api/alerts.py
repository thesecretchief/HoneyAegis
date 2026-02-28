"""Alert endpoints — list, acknowledge, and manage alerts (tenant-scoped)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.core.database import get_db
from app.api.auth import get_current_user, get_tenant_id
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertListResponse

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    severity: str | None = None,
    acknowledged: bool | None = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    query = select(Alert).where(Alert.tenant_id == tenant_id).order_by(Alert.created_at.desc())
    if severity:
        query = query.where(Alert.severity == severity)
    if acknowledged is not None:
        query = query.where(Alert.acknowledged == acknowledged)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    count_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.tenant_id == tenant_id)
    )
    total = count_result.scalar()

    return AlertListResponse(alerts=alerts, total=total or 0)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
):
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.tenant_id == tenant_id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    alert.acknowledged_by = current_user.id
    await db.commit()

    return {"status": "acknowledged", "alert_id": str(alert_id)}


@router.post("/acknowledge-all")
async def acknowledge_all_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id),
):
    await db.execute(
        update(Alert)
        .where(Alert.tenant_id == tenant_id, Alert.acknowledged.is_(False))
        .values(acknowledged=True, acknowledged_by=current_user.id)
    )
    await db.commit()

    return {"status": "all_acknowledged"}

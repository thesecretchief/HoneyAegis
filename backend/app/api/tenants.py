"""Tenant management endpoints — list, create, update, branding."""

import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.tenant import Tenant
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class TenantResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    is_active: bool
    logo_url: str | None = None
    primary_color: str
    display_name: str | None = None
    portal_domain: str | None = None
    model_config = {"from_attributes": True}


class TenantCreateRequest(BaseModel):
    slug: str
    name: str
    display_name: str | None = None
    logo_url: str | None = None
    primary_color: str = "#f59e0b"


class TenantUpdateRequest(BaseModel):
    name: str | None = None
    display_name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    portal_domain: str | None = None
    is_active: bool | None = None


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tenants (superuser only)."""
    if not current_user.is_superuser:
        # Non-superusers only see their own tenant
        if current_user.tenant_id:
            result = await db.execute(
                select(Tenant).where(Tenant.id == current_user.tenant_id)
            )
            tenant = result.scalar_one_or_none()
            return [tenant] if tenant else []
        return []

    result = await db.execute(select(Tenant).order_by(Tenant.created_at))
    return result.scalars().all()


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    request: TenantCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tenant (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")

    existing = await db.execute(select(Tenant).where(Tenant.slug == request.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tenant slug already exists")

    tenant = Tenant(
        id=uuid4(), slug=request.slug, name=request.name,
        display_name=request.display_name or request.name,
        logo_url=request.logo_url, primary_color=request.primary_color,
        is_active=True,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    logger.info("Created tenant: %s (%s)", tenant.slug, tenant.name)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    request: TenantUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update tenant branding and settings."""
    # Allow superuser or own-tenant admin
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if request.name is not None:
        tenant.name = request.name
    if request.display_name is not None:
        tenant.display_name = request.display_name
    if request.logo_url is not None:
        tenant.logo_url = request.logo_url
    if request.primary_color is not None:
        tenant.primary_color = request.primary_color
    if request.portal_domain is not None:
        tenant.portal_domain = request.portal_domain
    if request.is_active is not None:
        tenant.is_active = request.is_active

    await db.commit()
    await db.refresh(tenant)
    return tenant


@router.get("/branding")
async def get_my_branding(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get branding for the current user's tenant."""
    if not current_user.tenant_id:
        return {
            "id": None, "slug": "default", "name": "HoneyAegis",
            "display_name": "HoneyAegis", "primary_color": "#f59e0b", "logo_url": None,
        }

    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        return {
            "id": None, "slug": "default", "name": "HoneyAegis",
            "display_name": "HoneyAegis", "primary_color": "#f59e0b", "logo_url": None,
        }

    return {
        "id": str(tenant.id),
        "slug": tenant.slug,
        "name": tenant.name,
        "display_name": tenant.display_name or tenant.name,
        "primary_color": tenant.primary_color,
        "logo_url": tenant.logo_url,
    }

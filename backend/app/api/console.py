"""Hosted console API stubs.

These endpoints provide the foundation for a future hosted management console
that aggregates data from multiple self-hosted HoneyAegis deployments.

All endpoints return stub responses. Implement the business logic when the
hosted console feature is ready for production.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.auth import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class DeploymentRegistration(BaseModel):
    """Register a self-hosted deployment with the console."""

    name: str
    url: str
    version: str
    sensor_count: int = 0


class DeploymentStatus(BaseModel):
    """Status of a registered deployment."""

    deployment_id: str
    name: str
    url: str
    version: str
    status: str
    last_seen: str
    sensor_count: int
    session_count_24h: int
    alert_count_24h: int


class ConsoleStats(BaseModel):
    """Aggregated statistics across all deployments."""

    total_deployments: int
    total_sensors: int
    total_sessions_24h: int
    total_alerts_24h: int
    deployments_online: int
    deployments_offline: int


class LicenseInfo(BaseModel):
    """License status for the deployment."""

    tier: str
    max_sensors: int
    max_deployments: int
    features: list[str]
    expires_at: str | None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/stats")
async def console_stats(
    tenant_id: UUID = Depends(get_tenant_id),
) -> ConsoleStats:
    """Get aggregated statistics across all managed deployments.

    Stub: Returns placeholder data. Will be connected to a deployment
    registry when the hosted console is implemented.
    """
    return ConsoleStats(
        total_deployments=0,
        total_sensors=0,
        total_sessions_24h=0,
        total_alerts_24h=0,
        deployments_online=0,
        deployments_offline=0,
    )


@router.get("/deployments")
async def list_deployments(
    tenant_id: UUID = Depends(get_tenant_id),
) -> list[DeploymentStatus]:
    """List all registered deployments for this tenant.

    Stub: Returns empty list. Will query deployment registry when implemented.
    """
    return []


@router.post("/deployments", status_code=status.HTTP_201_CREATED)
async def register_deployment(
    registration: DeploymentRegistration,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Register a new self-hosted deployment.

    Stub: Acknowledges registration but does not persist. Will create
    a deployment record when the hosted console is implemented.
    """
    logger.info(
        "Deployment registration received (stub): name=%s url=%s",
        registration.name,
        registration.url,
    )
    return {
        "status": "registered",
        "deployment_id": "stub-deployment-id",
        "message": "Hosted console is not yet active. Deployment registered locally.",
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }


@router.delete("/deployments/{deployment_id}")
async def remove_deployment(
    deployment_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Remove a registered deployment.

    Stub: Returns success but does not modify state.
    """
    return {"status": "removed", "deployment_id": deployment_id}


@router.get("/license")
async def license_info(
    tenant_id: UUID = Depends(get_tenant_id),
) -> LicenseInfo:
    """Get license information for this tenant.

    HoneyAegis is open-source (MIT). The license endpoint exists for
    future hosted/enterprise tiers with additional features.
    """
    return LicenseInfo(
        tier="community",
        max_sensors=999,
        max_deployments=999,
        features=[
            "unlimited-sessions",
            "unlimited-sensors",
            "all-honeypots",
            "ai-analysis",
            "siem-export",
            "multi-tenant",
            "plugins",
        ],
        expires_at=None,
    )


@router.post("/deployments/{deployment_id}/heartbeat")
async def deployment_heartbeat(
    deployment_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Receive heartbeat from a managed deployment.

    Stub: Acknowledges heartbeat but does not persist.
    """
    return {
        "status": "ok",
        "deployment_id": deployment_id,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

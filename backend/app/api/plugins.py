"""Plugin management endpoints — list, enable/disable plugins."""

import logging

from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.services.plugin_service import get_plugins, discover_plugins

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_plugins(
    _current_user: User = Depends(get_current_user),
):
    """List all discovered plugins."""
    return {"plugins": get_plugins()}


@router.post("/reload")
async def reload_plugins(
    current_user: User = Depends(get_current_user),
):
    """Re-scan the plugins directory and reload all plugins."""
    if not current_user.is_superuser:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Superuser access required")

    plugins = discover_plugins()
    return {"status": "reloaded", "count": len(plugins)}

"""RBAC API endpoints for role and permission management."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.rbac_service import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    get_permissions,
    has_permission,
    get_role_display_name,
    get_role_hierarchy,
    validate_role_assignment,
)

router = APIRouter()


class RoleInfo(BaseModel):
    role: str
    display_name: str
    permissions: list[str]
    permission_count: int


class PermissionCheckRequest(BaseModel):
    role: str
    permission: str


class PermissionCheckResponse(BaseModel):
    role: str
    permission: str
    allowed: bool


class RoleAssignmentCheck(BaseModel):
    assigner_role: str
    target_role: str
    allowed: bool


@router.get("/roles", response_model=list[RoleInfo])
async def list_roles():
    """List all available roles with their permissions."""
    roles = []
    for role in get_role_hierarchy():
        perms = get_permissions(role)
        roles.append(RoleInfo(
            role=role.value,
            display_name=get_role_display_name(role),
            permissions=sorted(p.value for p in perms),
            permission_count=len(perms),
        ))
    return roles


@router.get("/roles/{role_name}", response_model=RoleInfo)
async def get_role(role_name: str):
    """Get details for a specific role."""
    try:
        role = Role(role_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )
    perms = get_permissions(role)
    return RoleInfo(
        role=role.value,
        display_name=get_role_display_name(role),
        permissions=sorted(p.value for p in perms),
        permission_count=len(perms),
    )


@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission_endpoint(req: PermissionCheckRequest):
    """Check if a role has a specific permission."""
    try:
        role = Role(req.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {req.role}",
        )
    try:
        perm = Permission(req.permission)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission: {req.permission}",
        )

    return PermissionCheckResponse(
        role=req.role,
        permission=req.permission,
        allowed=has_permission(role, perm),
    )


@router.get("/permissions", response_model=list[str])
async def list_permissions():
    """List all available permissions."""
    return sorted(p.value for p in Permission)

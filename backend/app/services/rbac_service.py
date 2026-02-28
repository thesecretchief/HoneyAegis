"""Role-Based Access Control (RBAC) service for HoneyAegis.

Provides fine-grained permission management for enterprise deployments.
Roles: superadmin, admin, analyst, viewer.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles with hierarchical permissions."""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Granular permissions for RBAC enforcement."""
    # Sessions
    SESSIONS_READ = "sessions:read"
    SESSIONS_EXPORT = "sessions:export"

    # Alerts
    ALERTS_READ = "alerts:read"
    ALERTS_MANAGE = "alerts:manage"

    # Sensors
    SENSORS_READ = "sensors:read"
    SENSORS_MANAGE = "sensors:manage"

    # Honey tokens
    TOKENS_READ = "tokens:read"
    TOKENS_MANAGE = "tokens:manage"

    # Webhooks
    WEBHOOKS_READ = "webhooks:read"
    WEBHOOKS_MANAGE = "webhooks:manage"

    # Config
    CONFIG_READ = "config:read"
    CONFIG_MANAGE = "config:manage"

    # Users
    USERS_READ = "users:read"
    USERS_MANAGE = "users:manage"

    # Tenants
    TENANTS_READ = "tenants:read"
    TENANTS_MANAGE = "tenants:manage"

    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_GENERATE = "reports:generate"

    # Plugins
    PLUGINS_READ = "plugins:read"
    PLUGINS_MANAGE = "plugins:manage"

    # Threat Intel
    INTEL_READ = "intel:read"
    INTEL_MANAGE = "intel:manage"

    # Sandbox
    SANDBOX_READ = "sandbox:read"
    SANDBOX_SUBMIT = "sandbox:submit"

    # Audit
    AUDIT_READ = "audit:read"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_MANAGE = "billing:manage"

    # System
    SYSTEM_ADMIN = "system:admin"


# Role → permission mappings (hierarchical: superadmin > admin > analyst > viewer)
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.VIEWER: {
        Permission.SESSIONS_READ,
        Permission.ALERTS_READ,
        Permission.SENSORS_READ,
        Permission.TOKENS_READ,
        Permission.WEBHOOKS_READ,
        Permission.CONFIG_READ,
        Permission.REPORTS_READ,
        Permission.PLUGINS_READ,
        Permission.INTEL_READ,
        Permission.SANDBOX_READ,
        Permission.BILLING_READ,
    },
    Role.ANALYST: {
        Permission.SESSIONS_READ,
        Permission.SESSIONS_EXPORT,
        Permission.ALERTS_READ,
        Permission.ALERTS_MANAGE,
        Permission.SENSORS_READ,
        Permission.TOKENS_READ,
        Permission.TOKENS_MANAGE,
        Permission.WEBHOOKS_READ,
        Permission.CONFIG_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_GENERATE,
        Permission.PLUGINS_READ,
        Permission.INTEL_READ,
        Permission.INTEL_MANAGE,
        Permission.SANDBOX_READ,
        Permission.SANDBOX_SUBMIT,
        Permission.BILLING_READ,
    },
    Role.ADMIN: {
        Permission.SESSIONS_READ,
        Permission.SESSIONS_EXPORT,
        Permission.ALERTS_READ,
        Permission.ALERTS_MANAGE,
        Permission.SENSORS_READ,
        Permission.SENSORS_MANAGE,
        Permission.TOKENS_READ,
        Permission.TOKENS_MANAGE,
        Permission.WEBHOOKS_READ,
        Permission.WEBHOOKS_MANAGE,
        Permission.CONFIG_READ,
        Permission.CONFIG_MANAGE,
        Permission.USERS_READ,
        Permission.USERS_MANAGE,
        Permission.TENANTS_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_GENERATE,
        Permission.PLUGINS_READ,
        Permission.PLUGINS_MANAGE,
        Permission.INTEL_READ,
        Permission.INTEL_MANAGE,
        Permission.SANDBOX_READ,
        Permission.SANDBOX_SUBMIT,
        Permission.AUDIT_READ,
        Permission.BILLING_READ,
        Permission.BILLING_MANAGE,
    },
    Role.SUPERADMIN: {p for p in Permission},  # All permissions
}


@dataclass
class RBACUser:
    """Represents a user with RBAC context."""
    user_id: str
    email: str
    role: Role
    tenant_id: str | None = None
    custom_permissions: set[Permission] = field(default_factory=set)


def get_permissions(role: Role) -> set[Permission]:
    """Get all permissions for a given role."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    permissions = get_permissions(role)
    return permission in permissions


def check_permission(
    user: RBACUser,
    permission: Permission,
) -> bool:
    """Check if a user has a specific permission (role + custom overrides)."""
    role_perms = get_permissions(user.role)
    all_perms = role_perms | user.custom_permissions
    return permission in all_perms


def get_role_hierarchy() -> list[Role]:
    """Return roles ordered from least to most privileged."""
    return [Role.VIEWER, Role.ANALYST, Role.ADMIN, Role.SUPERADMIN]


def role_at_least(user_role: Role, minimum_role: Role) -> bool:
    """Check if user_role is at least as privileged as minimum_role."""
    hierarchy = get_role_hierarchy()
    user_idx = hierarchy.index(user_role) if user_role in hierarchy else -1
    min_idx = hierarchy.index(minimum_role) if minimum_role in hierarchy else len(hierarchy)
    return user_idx >= min_idx


def get_role_display_name(role: Role) -> str:
    """Get human-friendly display name for a role."""
    display_names = {
        Role.SUPERADMIN: "Super Administrator",
        Role.ADMIN: "Administrator",
        Role.ANALYST: "Security Analyst",
        Role.VIEWER: "Read-Only Viewer",
    }
    return display_names.get(role, role.value)


def validate_role_assignment(
    assigner_role: Role,
    target_role: Role,
) -> bool:
    """Check if assigner can assign target_role (can only assign lower roles)."""
    hierarchy = get_role_hierarchy()
    assigner_idx = hierarchy.index(assigner_role) if assigner_role in hierarchy else -1
    target_idx = hierarchy.index(target_role) if target_role in hierarchy else len(hierarchy)
    return assigner_idx > target_idx

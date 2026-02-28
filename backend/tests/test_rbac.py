"""Tests for RBAC service."""

import pytest
from app.services.rbac_service import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    RBACUser,
    get_permissions,
    has_permission,
    check_permission,
    get_role_hierarchy,
    role_at_least,
    get_role_display_name,
    validate_role_assignment,
)


class TestRoles:
    def test_four_roles_exist(self):
        assert len(Role) == 4

    def test_role_values(self):
        assert Role.SUPERADMIN.value == "superadmin"
        assert Role.ADMIN.value == "admin"
        assert Role.ANALYST.value == "analyst"
        assert Role.VIEWER.value == "viewer"


class TestPermissions:
    def test_permissions_exist(self):
        assert len(Permission) > 20

    def test_session_permissions(self):
        assert Permission.SESSIONS_READ.value == "sessions:read"
        assert Permission.SESSIONS_EXPORT.value == "sessions:export"

    def test_system_admin_permission(self):
        assert Permission.SYSTEM_ADMIN.value == "system:admin"


class TestRolePermissions:
    def test_superadmin_has_all_permissions(self):
        perms = get_permissions(Role.SUPERADMIN)
        assert perms == {p for p in Permission}

    def test_viewer_has_read_only(self):
        perms = get_permissions(Role.VIEWER)
        for p in perms:
            assert "manage" not in p.value
            assert "submit" not in p.value
            assert "generate" not in p.value
            assert "export" not in p.value
            assert "admin" not in p.value

    def test_analyst_can_export(self):
        assert has_permission(Role.ANALYST, Permission.SESSIONS_EXPORT)

    def test_viewer_cannot_export(self):
        assert not has_permission(Role.VIEWER, Permission.SESSIONS_EXPORT)

    def test_admin_can_manage_users(self):
        assert has_permission(Role.ADMIN, Permission.USERS_MANAGE)

    def test_analyst_cannot_manage_users(self):
        assert not has_permission(Role.ANALYST, Permission.USERS_MANAGE)

    def test_admin_cannot_system_admin(self):
        assert not has_permission(Role.ADMIN, Permission.SYSTEM_ADMIN)

    def test_superadmin_can_system_admin(self):
        assert has_permission(Role.SUPERADMIN, Permission.SYSTEM_ADMIN)


class TestRBACUser:
    def test_user_defaults(self):
        user = RBACUser(user_id="u1", email="test@test.com", role=Role.VIEWER)
        assert user.tenant_id is None
        assert user.custom_permissions == set()

    def test_check_permission_with_role(self):
        user = RBACUser(user_id="u1", email="test@test.com", role=Role.ANALYST)
        assert check_permission(user, Permission.SESSIONS_EXPORT)

    def test_check_permission_with_custom_override(self):
        user = RBACUser(
            user_id="u1",
            email="test@test.com",
            role=Role.VIEWER,
            custom_permissions={Permission.SESSIONS_EXPORT},
        )
        assert check_permission(user, Permission.SESSIONS_EXPORT)


class TestRoleHierarchy:
    def test_hierarchy_order(self):
        hierarchy = get_role_hierarchy()
        assert hierarchy == [Role.VIEWER, Role.ANALYST, Role.ADMIN, Role.SUPERADMIN]

    def test_role_at_least_same(self):
        assert role_at_least(Role.ADMIN, Role.ADMIN)

    def test_role_at_least_higher(self):
        assert role_at_least(Role.SUPERADMIN, Role.ADMIN)

    def test_role_at_least_lower(self):
        assert not role_at_least(Role.VIEWER, Role.ADMIN)

    def test_display_names(self):
        assert get_role_display_name(Role.SUPERADMIN) == "Super Administrator"
        assert get_role_display_name(Role.VIEWER) == "Read-Only Viewer"


class TestRoleAssignment:
    def test_admin_can_assign_analyst(self):
        assert validate_role_assignment(Role.ADMIN, Role.ANALYST)

    def test_admin_cannot_assign_admin(self):
        assert not validate_role_assignment(Role.ADMIN, Role.ADMIN)

    def test_superadmin_can_assign_admin(self):
        assert validate_role_assignment(Role.SUPERADMIN, Role.ADMIN)

    def test_viewer_cannot_assign_anyone(self):
        assert not validate_role_assignment(Role.VIEWER, Role.VIEWER)

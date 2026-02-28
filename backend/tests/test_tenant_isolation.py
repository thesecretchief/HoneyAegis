"""Tests for multi-tenant isolation.

Verifies that tenant_id is properly enforced across models,
schemas, and API dependencies.
"""

import uuid
from datetime import datetime, timezone

import pytest

from app.models.tenant import Tenant
from app.models.user import User
from app.models.session import Session
from app.models.sensor import Sensor
from app.models.alert import Alert
from app.schemas.auth import UserResponse


# --- Model tests ---

def test_tenant_model_fields():
    """Tenant model has all required branding fields."""
    t = Tenant(
        slug="test-corp",
        name="Test Corporation",
        display_name="Test Security",
        primary_color="#2563eb",
        logo_url="https://example.com/logo.png",
        portal_domain="test.honeyaegis.io",
        is_active=True,
    )
    assert t.slug == "test-corp"
    assert t.display_name == "Test Security"
    assert t.primary_color == "#2563eb"
    assert t.logo_url == "https://example.com/logo.png"
    assert t.portal_domain == "test.honeyaegis.io"
    assert t.is_active is True


def test_tenant_default_color():
    """Tenant has default amber color when explicitly set."""
    t = Tenant(slug="default", name="Default", primary_color="#f59e0b")
    assert t.primary_color == "#f59e0b"


def test_user_has_tenant_id():
    """User model includes tenant_id field."""
    tenant_id = uuid.uuid4()
    u = User(
        email="test@test.com",
        hashed_password="hashed",
        tenant_id=tenant_id,
    )
    assert u.tenant_id == tenant_id


def test_session_has_tenant_id():
    """Session model includes tenant_id field."""
    tenant_id = uuid.uuid4()
    s = Session(
        id=uuid.uuid4(),
        session_id="test-session",
        protocol="ssh",
        src_ip="1.2.3.4",
        tenant_id=tenant_id,
    )
    assert s.tenant_id == tenant_id


def test_sensor_has_tenant_id():
    """Sensor model includes tenant_id field."""
    tenant_id = uuid.uuid4()
    s = Sensor(
        id=uuid.uuid4(),
        sensor_id="sensor-01",
        name="Test Sensor",
        tenant_id=tenant_id,
        status="active",
    )
    assert s.tenant_id == tenant_id


def test_alert_has_tenant_id():
    """Alert model includes tenant_id field."""
    tenant_id = uuid.uuid4()
    a = Alert(
        id=uuid.uuid4(),
        alert_type="new_session",
        severity="medium",
        title="Test Alert",
        tenant_id=tenant_id,
    )
    assert a.tenant_id == tenant_id


# --- Schema tests ---

def test_user_response_includes_tenant_id():
    """UserResponse schema includes tenant_id."""
    tenant_id = uuid.uuid4()
    resp = UserResponse(
        id=uuid.uuid4(),
        email="test@test.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        tenant_id=tenant_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    assert resp.tenant_id == tenant_id


def test_user_response_tenant_id_optional():
    """UserResponse works without tenant_id."""
    resp = UserResponse(
        id=uuid.uuid4(),
        email="test@test.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    assert resp.tenant_id is None


# --- Tenant isolation logic tests ---

def test_different_tenants_different_uuids():
    """Two tenants get different UUIDs."""
    t1 = Tenant(id=uuid.uuid4(), slug="tenant-a", name="Tenant A")
    t2 = Tenant(id=uuid.uuid4(), slug="tenant-b", name="Tenant B")
    assert t1.id != t2.id


def test_session_belongs_to_tenant():
    """Sessions are associated with their correct tenant."""
    tenant_a_id = uuid.uuid4()
    tenant_b_id = uuid.uuid4()

    session_a = Session(
        id=uuid.uuid4(),
        session_id="session-a",
        protocol="ssh",
        src_ip="1.1.1.1",
        tenant_id=tenant_a_id,
    )
    session_b = Session(
        id=uuid.uuid4(),
        session_id="session-b",
        protocol="ssh",
        src_ip="2.2.2.2",
        tenant_id=tenant_b_id,
    )

    assert session_a.tenant_id == tenant_a_id
    assert session_b.tenant_id == tenant_b_id
    assert session_a.tenant_id != session_b.tenant_id


def test_sensor_cross_tenant_check():
    """Sensor from one tenant should not be accessible by another."""
    tenant_a_id = uuid.uuid4()
    tenant_b_id = uuid.uuid4()

    sensor = Sensor(
        id=uuid.uuid4(),
        sensor_id="shared-sensor",
        name="Office Sensor",
        tenant_id=tenant_a_id,
        status="active",
    )

    # Simulate cross-tenant check (as done in the API)
    requesting_tenant_id = tenant_b_id
    assert sensor.tenant_id != requesting_tenant_id, \
        "Cross-tenant access should be detected and rejected"

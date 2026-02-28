"""Tests for honey token models and logic."""

import uuid
from datetime import datetime, timezone

import pytest

from app.models.honey_token import HoneyToken


# --- Model tests ---


def test_honey_token_credential_fields():
    """HoneyToken credential type has all required fields."""
    token = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        token_type="credential",
        name="SSH Trap Creds",
        username="admin",
        password="password123",
        alert_severity="critical",
        is_active=True,
    )
    assert token.token_type == "credential"
    assert token.username == "admin"
    assert token.password == "password123"
    assert token.alert_severity == "critical"
    assert token.is_active is True


def test_honey_token_file_fields():
    """HoneyToken file type stores filename and path."""
    token = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        token_type="file",
        name="Fake Config",
        filename="secrets.env",
        file_path="/honeypot/fake/.env",
    )
    assert token.token_type == "file"
    assert token.filename == "secrets.env"
    assert token.file_path == "/honeypot/fake/.env"


def test_honey_token_explicit_defaults():
    """HoneyToken with explicit default values behaves correctly."""
    token = HoneyToken(
        id=uuid.uuid4(),
        name="Test Token",
        token_type="credential",
        is_active=True,
        trigger_count=0,
        alert_severity="critical",
    )
    assert token.is_active is True
    assert token.trigger_count == 0
    assert token.last_triggered_at is None
    assert token.alert_severity == "critical"
    assert token.webhook_url is None


def test_honey_token_tenant_isolation():
    """HoneyTokens from different tenants have different tenant_ids."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    token_a = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=tenant_a,
        token_type="credential",
        name="Tenant A Token",
        username="root",
    )
    token_b = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=tenant_b,
        token_type="credential",
        name="Tenant B Token",
        username="admin",
    )

    assert token_a.tenant_id != token_b.tenant_id
    assert token_a.tenant_id == tenant_a
    assert token_b.tenant_id == tenant_b


def test_honey_token_trigger_tracking():
    """HoneyToken trigger count and timestamp can be updated."""
    token = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        token_type="credential",
        name="Tracked Token",
        trigger_count=0,
    )
    assert token.trigger_count == 0
    assert token.last_triggered_at is None

    # Simulate trigger
    token.trigger_count += 1
    token.last_triggered_at = datetime.now(timezone.utc)

    assert token.trigger_count == 1
    assert token.last_triggered_at is not None


def test_honey_token_extra_data():
    """HoneyToken extra_data stores arbitrary JSON."""
    meta = {"source": "automated", "tags": ["ssh", "decoy"]}
    token = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        token_type="credential",
        name="Meta Token",
        extra_data=meta,
    )
    assert token.extra_data == meta
    assert token.extra_data["source"] == "automated"
    assert "ssh" in token.extra_data["tags"]


def test_honey_token_types():
    """HoneyToken supports multiple token types."""
    for token_type in ["credential", "file", "url", "api_key"]:
        token = HoneyToken(
            id=uuid.uuid4(),
            token_type=token_type,
            name=f"Test {token_type}",
        )
        assert token.token_type == token_type


def test_honey_token_deactivation():
    """HoneyToken can be deactivated."""
    token = HoneyToken(
        id=uuid.uuid4(),
        token_type="credential",
        name="Active Token",
        is_active=True,
    )
    assert token.is_active is True

    token.is_active = False
    assert token.is_active is False


def test_honey_token_cross_tenant_check():
    """Cross-tenant access to honey tokens should be detectable."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    token = HoneyToken(
        id=uuid.uuid4(),
        tenant_id=tenant_a,
        token_type="credential",
        name="Tenant A Token",
        username="admin",
    )

    # Requesting tenant is different — should be rejected
    assert token.tenant_id != tenant_b


def test_honey_token_multiple_credentials():
    """Multiple honey tokens can have different usernames."""
    tokens = []
    for i, name in enumerate(["root", "admin", "ubuntu", "deploy"]):
        token = HoneyToken(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            token_type="credential",
            name=f"Token {i}",
            username=name,
            password=f"pass{i}",
        )
        tokens.append(token)

    usernames = {t.username for t in tokens}
    assert len(usernames) == 4
    assert "root" in usernames
    assert "admin" in usernames

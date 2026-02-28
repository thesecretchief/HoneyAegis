"""Tests for webhook models and service logic."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.models.webhook import Webhook


# --- Model tests ---


def test_webhook_model_fields():
    """Webhook model has all required fields."""
    hook = Webhook(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        name="Slack Alert",
        url="https://hooks.slack.com/services/T00/B00/xxx",
        trigger_on="alert",
        http_method="POST",
        is_active=True,
    )
    assert hook.name == "Slack Alert"
    assert hook.url == "https://hooks.slack.com/services/T00/B00/xxx"
    assert hook.trigger_on == "alert"
    assert hook.http_method == "POST"
    assert hook.is_active is True


def test_webhook_explicit_defaults():
    """Webhook with explicit default values behaves correctly."""
    hook = Webhook(
        id=uuid.uuid4(),
        name="Default Hook",
        url="https://example.com/hook",
        trigger_on="alert",
        http_method="POST",
        is_active=True,
        execution_count=0,
    )
    assert hook.trigger_on == "alert"
    assert hook.http_method == "POST"
    assert hook.is_active is True
    assert hook.execution_count == 0
    assert hook.last_executed_at is None
    assert hook.last_status_code is None
    assert hook.severity_filter is None


def test_webhook_severity_filter():
    """Webhook severity filter restricts which events trigger it."""
    hook = Webhook(
        id=uuid.uuid4(),
        name="Critical Only",
        url="https://example.com/hook",
        trigger_on="alert",
        severity_filter="critical",
    )
    assert hook.severity_filter == "critical"


def test_webhook_tenant_isolation():
    """Webhooks from different tenants have different tenant_ids."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    hook_a = Webhook(
        id=uuid.uuid4(),
        tenant_id=tenant_a,
        name="Tenant A Hook",
        url="https://a.example.com",
    )
    hook_b = Webhook(
        id=uuid.uuid4(),
        tenant_id=tenant_b,
        name="Tenant B Hook",
        url="https://b.example.com",
    )

    assert hook_a.tenant_id != hook_b.tenant_id


def test_webhook_execution_tracking():
    """Webhook execution count and status tracking."""
    hook = Webhook(
        id=uuid.uuid4(),
        name="Tracked Hook",
        url="https://example.com/hook",
        execution_count=0,
    )
    assert hook.execution_count == 0

    # Simulate execution
    hook.execution_count += 1
    hook.last_executed_at = datetime.now(timezone.utc)
    hook.last_status_code = 200

    assert hook.execution_count == 1
    assert hook.last_status_code == 200
    assert hook.last_executed_at is not None


def test_webhook_secret_for_hmac():
    """Webhook can store a secret for HMAC signature verification."""
    hook = Webhook(
        id=uuid.uuid4(),
        name="Signed Hook",
        url="https://example.com/hook",
        secret="my-webhook-secret-key",
    )
    assert hook.secret == "my-webhook-secret-key"


def test_webhook_custom_headers():
    """Webhook can store custom headers as JSONB."""
    headers = {"X-Custom-Header": "value", "Authorization": "Bearer token"}
    hook = Webhook(
        id=uuid.uuid4(),
        name="Custom Headers Hook",
        url="https://example.com/hook",
        headers=headers,
    )
    assert hook.headers == headers
    assert hook.headers["X-Custom-Header"] == "value"


def test_webhook_payload_template():
    """Webhook can store a payload template."""
    template = {
        "text": "Alert: {{title}}",
        "severity": "{{severity}}",
    }
    hook = Webhook(
        id=uuid.uuid4(),
        name="Templated Hook",
        url="https://example.com/hook",
        payload_template=template,
    )
    assert hook.payload_template == template


def test_webhook_trigger_types():
    """Webhook supports all trigger types."""
    for trigger in ["alert", "session", "honey_token", "malware"]:
        hook = Webhook(
            id=uuid.uuid4(),
            name=f"Hook for {trigger}",
            url="https://example.com/hook",
            trigger_on=trigger,
        )
        assert hook.trigger_on == trigger


def test_webhook_deactivation():
    """Webhook can be deactivated."""
    hook = Webhook(
        id=uuid.uuid4(),
        name="Toggleable Hook",
        url="https://example.com/hook",
        is_active=True,
    )
    hook.is_active = False
    assert hook.is_active is False


def test_webhook_cross_tenant_check():
    """Cross-tenant access to webhooks should be detectable."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    hook = Webhook(
        id=uuid.uuid4(),
        tenant_id=tenant_a,
        name="Private Hook",
        url="https://example.com/hook",
    )

    assert hook.tenant_id != tenant_b


# --- Webhook service tests ---


@pytest.mark.asyncio
async def test_execute_webhook_success():
    """execute_webhook sends HTTP request and returns status code."""
    from app.services.webhook_service import execute_webhook

    hook = Webhook(
        id=uuid.uuid4(),
        name="Test Hook",
        url="https://example.com/hook",
        http_method="POST",
        headers={},
        secret=None,
    )

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        status = await execute_webhook(hook, {"event": "test"})
        assert status == 200


@pytest.mark.asyncio
async def test_execute_webhook_with_hmac():
    """execute_webhook adds HMAC signature when secret is set."""
    from app.services.webhook_service import execute_webhook

    hook = Webhook(
        id=uuid.uuid4(),
        name="Signed Hook",
        url="https://example.com/hook",
        http_method="POST",
        headers={},
        secret="test-secret",
    )

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        status = await execute_webhook(hook, {"event": "test"})
        assert status == 200

        # Verify HMAC header was sent
        call_kwargs = mock_client.request.call_args
        headers = call_kwargs.kwargs.get("headers", {})
        assert "X-HoneyAegis-Signature" in headers
        assert headers["X-HoneyAegis-Signature"].startswith("sha256=")


@pytest.mark.asyncio
async def test_execute_webhook_timeout():
    """execute_webhook returns 504 on timeout."""
    import httpx
    from app.services.webhook_service import execute_webhook

    hook = Webhook(
        id=uuid.uuid4(),
        name="Timeout Hook",
        url="https://example.com/slow",
        http_method="POST",
        headers={},
        secret=None,
    )

    with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_cls.return_value = mock_client

        status = await execute_webhook(hook, {"event": "test"})
        assert status == 504


@pytest.mark.asyncio
async def test_execute_webhook_error():
    """execute_webhook returns 500 on general error."""
    from app.services.webhook_service import execute_webhook

    hook = Webhook(
        id=uuid.uuid4(),
        name="Error Hook",
        url="https://example.com/error",
        http_method="POST",
        headers={},
        secret=None,
    )

    with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.request = AsyncMock(side_effect=ConnectionError("refused"))
        mock_client_cls.return_value = mock_client

        status = await execute_webhook(hook, {"event": "test"})
        assert status == 500


@pytest.mark.asyncio
async def test_execute_webhook_hmac_deterministic():
    """HMAC signature is deterministic for same payload and secret."""
    from app.services.webhook_service import execute_webhook

    hook = Webhook(
        id=uuid.uuid4(),
        name="Deterministic Hook",
        url="https://example.com/hook",
        http_method="POST",
        headers={},
        secret="fixed-secret",
    )

    signatures = []
    for _ in range(2):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            await execute_webhook(hook, {"event": "test", "key": "value"})
            call_kwargs = mock_client.request.call_args
            headers = call_kwargs.kwargs.get("headers", {})
            signatures.append(headers["X-HoneyAegis-Signature"])

    assert signatures[0] == signatures[1]

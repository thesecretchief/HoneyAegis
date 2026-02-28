"""Tests for SSO/OIDC service."""

import pytest
from app.services.sso_service import (
    OIDCProvider,
    OIDCState,
    OIDCUserInfo,
    PROVIDER_TEMPLATES,
    generate_state,
    generate_nonce,
    build_provider_from_template,
    build_authorization_url,
    validate_state,
    map_oidc_user_to_role,
    get_provider_status,
    hash_sub,
    _pending_states,
)


class TestOIDCProvider:
    def test_defaults(self):
        provider = OIDCProvider(
            name="test",
            client_id="cid",
            client_secret="csec",
            issuer_url="https://auth.example.com",
        )
        assert provider.enabled is False
        assert provider.scopes == ["openid", "profile", "email"]

    def test_enabled(self):
        provider = OIDCProvider(
            name="test",
            client_id="cid",
            client_secret="csec",
            issuer_url="https://auth.example.com",
            enabled=True,
        )
        assert provider.enabled is True


class TestProviderTemplates:
    def test_four_templates(self):
        assert len(PROVIDER_TEMPLATES) == 4

    def test_keycloak_template(self):
        assert "keycloak" in PROVIDER_TEMPLATES

    def test_okta_template(self):
        assert "okta" in PROVIDER_TEMPLATES

    def test_azure_ad_template(self):
        assert "azure_ad" in PROVIDER_TEMPLATES

    def test_google_template(self):
        assert "google" in PROVIDER_TEMPLATES


class TestBuildProvider:
    def test_build_keycloak(self):
        provider = build_provider_from_template(
            "keycloak", "test", "cid", "csec", "https://kc.example.com/realms/test"
        )
        assert provider.enabled is True
        assert "openid-connect/auth" in provider.authorization_endpoint
        assert "openid-connect/token" in provider.token_endpoint

    def test_build_google(self):
        provider = build_provider_from_template(
            "google", "gsuite", "cid", "csec", "https://accounts.google.com"
        )
        assert "accounts.google.com" in provider.authorization_endpoint


class TestAuthorizationURL:
    def test_build_url(self):
        provider = build_provider_from_template(
            "keycloak", "test", "client123", "secret", "https://kc.example.com/realms/test"
        )
        url, state = build_authorization_url(provider, "https://app.example.com/callback")
        assert "client123" in url
        assert "response_type=code" in url
        assert state.provider_name == "test"
        # Clean up
        _pending_states.pop(state.state, None)

    def test_validate_state(self):
        provider = build_provider_from_template(
            "keycloak", "test", "cid", "csec", "https://kc.example.com/realms/test"
        )
        _, oidc_state = build_authorization_url(provider, "https://app.example.com/callback")
        result = validate_state(oidc_state.state)
        assert result is not None
        assert result.provider_name == "test"

    def test_validate_state_invalid(self):
        result = validate_state("invalid-state-token")
        assert result is None


class TestTokenGeneration:
    def test_state_length(self):
        state = generate_state()
        assert len(state) > 20

    def test_nonce_length(self):
        nonce = generate_nonce()
        assert len(nonce) > 20

    def test_state_unique(self):
        states = {generate_state() for _ in range(10)}
        assert len(states) == 10


class TestRoleMapping:
    def test_admin_group(self):
        user = OIDCUserInfo(sub="u1", email="u@t.com", groups=["honeyaegis-admins"])
        assert map_oidc_user_to_role(user) == "admin"

    def test_analyst_group(self):
        user = OIDCUserInfo(sub="u1", email="u@t.com", groups=["honeyaegis-analysts"])
        assert map_oidc_user_to_role(user) == "analyst"

    def test_superadmin_group(self):
        user = OIDCUserInfo(sub="u1", email="u@t.com", groups=["honeyaegis-superadmins"])
        assert map_oidc_user_to_role(user) == "superadmin"

    def test_default_viewer(self):
        user = OIDCUserInfo(sub="u1", email="u@t.com", groups=["some-other-group"])
        assert map_oidc_user_to_role(user) == "viewer"

    def test_no_groups(self):
        user = OIDCUserInfo(sub="u1", email="u@t.com")
        assert map_oidc_user_to_role(user) == "viewer"


class TestProviderStatus:
    def test_status_report(self):
        provider = build_provider_from_template(
            "okta", "okta-corp", "cid", "csec", "https://dev.okta.com/oauth2/default"
        )
        status = get_provider_status(provider)
        assert status["name"] == "okta-corp"
        assert status["enabled"] is True
        assert status["has_client_id"] is True
        assert status["has_client_secret"] is True


class TestHashSub:
    def test_deterministic(self):
        h1 = hash_sub("user123")
        h2 = hash_sub("user123")
        assert h1 == h2

    def test_different_inputs(self):
        h1 = hash_sub("user123")
        h2 = hash_sub("user456")
        assert h1 != h2

    def test_length(self):
        h = hash_sub("user123")
        assert len(h) == 16

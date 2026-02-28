"""SSO / OIDC Authentication Stub for HoneyAegis Enterprise.

Provides the data structures and flow logic for OpenID Connect integration.
Production deployments should configure an OIDC provider (Keycloak, Okta,
Azure AD, Google Workspace, etc.).

This is a stub — the actual OAuth2 redirect flow, token exchange, and
user provisioning must be completed when connecting to a real IdP.
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class OIDCProvider:
    """Configuration for an OIDC identity provider."""
    name: str
    client_id: str
    client_secret: str
    issuer_url: str
    authorization_endpoint: str = ""
    token_endpoint: str = ""
    userinfo_endpoint: str = ""
    jwks_uri: str = ""
    scopes: list[str] = field(default_factory=lambda: ["openid", "profile", "email"])
    enabled: bool = False


@dataclass
class OIDCState:
    """Tracks an in-progress OIDC authentication flow."""
    state: str
    nonce: str
    redirect_uri: str
    provider_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OIDCUserInfo:
    """User information extracted from OIDC token claims."""
    sub: str
    email: str
    name: str = ""
    picture: str = ""
    email_verified: bool = False
    groups: list[str] = field(default_factory=list)
    raw_claims: dict = field(default_factory=dict)


# Well-known OIDC provider templates
PROVIDER_TEMPLATES: dict[str, dict] = {
    "keycloak": {
        "authorization_endpoint": "{issuer_url}/protocol/openid-connect/auth",
        "token_endpoint": "{issuer_url}/protocol/openid-connect/token",
        "userinfo_endpoint": "{issuer_url}/protocol/openid-connect/userinfo",
        "jwks_uri": "{issuer_url}/protocol/openid-connect/certs",
    },
    "okta": {
        "authorization_endpoint": "{issuer_url}/v1/authorize",
        "token_endpoint": "{issuer_url}/v1/token",
        "userinfo_endpoint": "{issuer_url}/v1/userinfo",
        "jwks_uri": "{issuer_url}/v1/keys",
    },
    "azure_ad": {
        "authorization_endpoint": "{issuer_url}/oauth2/v2.0/authorize",
        "token_endpoint": "{issuer_url}/oauth2/v2.0/token",
        "userinfo_endpoint": "https://graph.microsoft.com/oidc/userinfo",
        "jwks_uri": "{issuer_url}/discovery/v2.0/keys",
    },
    "google": {
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    },
}

# In-memory state store (production should use Redis)
_pending_states: dict[str, OIDCState] = {}


def generate_state() -> str:
    """Generate a cryptographically secure state parameter."""
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    """Generate a cryptographically secure nonce."""
    return secrets.token_urlsafe(32)


def build_provider_from_template(
    template_name: str,
    name: str,
    client_id: str,
    client_secret: str,
    issuer_url: str,
) -> OIDCProvider:
    """Create an OIDC provider from a well-known template."""
    template = PROVIDER_TEMPLATES.get(template_name, {})
    return OIDCProvider(
        name=name,
        client_id=client_id,
        client_secret=client_secret,
        issuer_url=issuer_url,
        authorization_endpoint=template.get("authorization_endpoint", "").format(issuer_url=issuer_url),
        token_endpoint=template.get("token_endpoint", "").format(issuer_url=issuer_url),
        userinfo_endpoint=template.get("userinfo_endpoint", "").format(issuer_url=issuer_url),
        jwks_uri=template.get("jwks_uri", "").format(issuer_url=issuer_url),
        enabled=True,
    )


def build_authorization_url(
    provider: OIDCProvider,
    redirect_uri: str,
) -> tuple[str, OIDCState]:
    """Build the OIDC authorization URL for the redirect flow.

    Returns:
        Tuple of (authorization_url, oidc_state).
    """
    state = generate_state()
    nonce = generate_nonce()

    params = {
        "response_type": "code",
        "client_id": provider.client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(provider.scopes),
        "state": state,
        "nonce": nonce,
    }

    url = f"{provider.authorization_endpoint}?{urlencode(params)}"

    oidc_state = OIDCState(
        state=state,
        nonce=nonce,
        redirect_uri=redirect_uri,
        provider_name=provider.name,
    )

    _pending_states[state] = oidc_state
    return url, oidc_state


def validate_state(state: str) -> OIDCState | None:
    """Validate and consume an OIDC state parameter."""
    return _pending_states.pop(state, None)


def map_oidc_user_to_role(user_info: OIDCUserInfo, role_mapping: dict[str, str] | None = None) -> str:
    """Map OIDC groups/claims to HoneyAegis RBAC roles.

    Args:
        user_info: User info from the OIDC provider.
        role_mapping: Optional mapping of OIDC group names to HoneyAegis roles.

    Returns:
        HoneyAegis role string (superadmin, admin, analyst, viewer).
    """
    if role_mapping is None:
        role_mapping = {
            "honeyaegis-superadmins": "superadmin",
            "honeyaegis-admins": "admin",
            "honeyaegis-analysts": "analyst",
        }

    for group in user_info.groups:
        if group in role_mapping:
            return role_mapping[group]

    return "viewer"


def get_provider_status(provider: OIDCProvider) -> dict:
    """Get the status/health of an OIDC provider configuration."""
    return {
        "name": provider.name,
        "enabled": provider.enabled,
        "issuer_url": provider.issuer_url,
        "has_client_id": bool(provider.client_id),
        "has_client_secret": bool(provider.client_secret),
        "has_endpoints": bool(
            provider.authorization_endpoint
            and provider.token_endpoint
            and provider.userinfo_endpoint
        ),
        "scopes": provider.scopes,
    }


def hash_sub(sub: str, salt: str = "honeyaegis") -> str:
    """Create a deterministic hash of the OIDC subject for internal use."""
    return hashlib.sha256(f"{salt}:{sub}".encode()).hexdigest()[:16]

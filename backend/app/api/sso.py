"""SSO / OIDC endpoints for enterprise authentication."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.sso_service import (
    OIDCProvider,
    PROVIDER_TEMPLATES,
    build_provider_from_template,
    build_authorization_url,
    validate_state,
    get_provider_status,
    map_oidc_user_to_role,
    OIDCUserInfo,
)

router = APIRouter()


class ProviderConfigRequest(BaseModel):
    template: str
    name: str
    client_id: str
    client_secret: str
    issuer_url: str


class ProviderStatusResponse(BaseModel):
    name: str
    enabled: bool
    issuer_url: str
    has_client_id: bool
    has_client_secret: bool
    has_endpoints: bool
    scopes: list[str]


class AuthURLResponse(BaseModel):
    authorization_url: str
    state: str


class CallbackRequest(BaseModel):
    code: str
    state: str


class CallbackResponse(BaseModel):
    status: str
    message: str


class TemplateListResponse(BaseModel):
    templates: list[str]


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates():
    """List available OIDC provider templates."""
    return TemplateListResponse(templates=sorted(PROVIDER_TEMPLATES.keys()))


@router.post("/configure", response_model=ProviderStatusResponse)
async def configure_provider(req: ProviderConfigRequest):
    """Configure an OIDC provider from a template.

    Supported templates: keycloak, okta, azure_ad, google.
    """
    if req.template not in PROVIDER_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown template: {req.template}. Available: {list(PROVIDER_TEMPLATES.keys())}",
        )

    provider = build_provider_from_template(
        template_name=req.template,
        name=req.name,
        client_id=req.client_id,
        client_secret=req.client_secret,
        issuer_url=req.issuer_url,
    )

    return ProviderStatusResponse(**get_provider_status(provider))


@router.post("/callback", response_model=CallbackResponse)
async def sso_callback(req: CallbackRequest):
    """Handle the OIDC callback after user authentication.

    This is a stub — in production, exchange the code for tokens,
    validate the ID token, extract user info, and create/update
    the local user + issue a HoneyAegis JWT.
    """
    oidc_state = validate_state(req.state)
    if oidc_state is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    return CallbackResponse(
        status="stub",
        message=f"OIDC callback received for provider '{oidc_state.provider_name}'. "
        "Token exchange not implemented — configure a real IdP for production use.",
    )


@router.get("/status")
async def sso_status():
    """Check SSO/OIDC configuration status."""
    return {
        "sso_enabled": False,
        "configured_providers": [],
        "supported_templates": sorted(PROVIDER_TEMPLATES.keys()),
        "note": "SSO is a stub. Configure an OIDC provider (Keycloak, Okta, Azure AD, Google) for production use.",
    }

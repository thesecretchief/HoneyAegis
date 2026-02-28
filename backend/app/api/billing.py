"""Stripe billing integration stubs for HoneyAegis SaaS tier.

Provides webhook and subscription management endpoints for future
Stripe integration. Currently returns stub responses.

To enable:
  1. Set STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET in .env
  2. Configure Stripe webhooks to point to /api/v1/billing/webhook

HoneyAegis is MIT open-source. The billing layer exists for optional
hosted/enterprise tiers and does not gate any core features.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from uuid import UUID

from app.api.auth import get_tenant_id
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SubscriptionPlan(BaseModel):
    """Available subscription plans."""

    plan_id: str
    name: str
    price_monthly_usd: float
    max_sensors: int
    max_events_per_day: int
    features: list[str]
    is_current: bool = False


class SubscriptionStatus(BaseModel):
    """Current subscription status for a tenant."""

    tenant_id: str
    plan: str
    status: str
    current_period_start: str | None
    current_period_end: str | None
    max_sensors: int
    max_events_per_day: int
    usage_sensors: int
    usage_events_today: int


class CheckoutRequest(BaseModel):
    """Request to create a Stripe checkout session."""

    plan_id: str
    success_url: str = "http://localhost:3000/config?billing=success"
    cancel_url: str = "http://localhost:3000/config?billing=cancel"


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------
PLANS = [
    SubscriptionPlan(
        plan_id="community",
        name="Community (Free)",
        price_monthly_usd=0,
        max_sensors=999,
        max_events_per_day=999999,
        features=[
            "Unlimited self-hosted sensors",
            "All honeypot protocols",
            "AI analysis (local Ollama)",
            "SIEM export",
            "Multi-tenant",
            "Plugin system",
        ],
    ),
    SubscriptionPlan(
        plan_id="pro",
        name="Pro",
        price_monthly_usd=29,
        max_sensors=50,
        max_events_per_day=100000,
        features=[
            "Everything in Community",
            "SaaS relay for NAT sensors",
            "Priority support",
            "Cloud-hosted dashboard option",
            "Automated threat reports",
        ],
    ),
    SubscriptionPlan(
        plan_id="enterprise",
        name="Enterprise",
        price_monthly_usd=99,
        max_sensors=500,
        max_events_per_day=1000000,
        features=[
            "Everything in Pro",
            "White-label branding",
            "SLA guarantee",
            "Dedicated relay infrastructure",
            "Custom plugin development",
            "On-call support",
        ],
    ),
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/plans")
async def list_plans() -> list[SubscriptionPlan]:
    """List available subscription plans.

    The Community plan is always free. Pro and Enterprise plans
    require Stripe billing integration.
    """
    plans = []
    for plan in PLANS:
        p = plan.model_copy()
        p.is_current = plan.plan_id == "community"
        plans.append(p)
    return plans


@router.get("/subscription")
async def get_subscription(
    tenant_id: UUID = Depends(get_tenant_id),
) -> SubscriptionStatus:
    """Get current subscription status for this tenant.

    Stub: Always returns Community (free) plan.
    """
    return SubscriptionStatus(
        tenant_id=str(tenant_id),
        plan="community",
        status="active",
        current_period_start=None,
        current_period_end=None,
        max_sensors=999,
        max_events_per_day=999999,
        usage_sensors=0,
        usage_events_today=0,
    )


@router.post("/checkout")
async def create_checkout_session(
    checkout: CheckoutRequest,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Create a Stripe checkout session for plan upgrade.

    Stub: Returns a placeholder URL. When Stripe is configured,
    this will return a real Stripe Checkout URL.
    """
    stripe_key = getattr(settings, "stripe_secret_key", "")
    if not stripe_key:
        return {
            "status": "not_configured",
            "message": "Stripe billing is not configured. Set STRIPE_SECRET_KEY in .env",
            "checkout_url": None,
        }

    logger.info(
        "Checkout session requested: plan=%s tenant=%s",
        checkout.plan_id,
        tenant_id,
    )

    return {
        "status": "created",
        "checkout_url": f"https://checkout.stripe.com/stub/{checkout.plan_id}",
        "plan_id": checkout.plan_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/webhook")
async def stripe_webhook(request: Request) -> dict:
    """Handle Stripe webhook events.

    Processes subscription lifecycle events:
    - checkout.session.completed
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_failed

    Stub: Logs the event but does not process it.
    """
    body = await request.body()
    sig = request.headers.get("stripe-signature", "")

    logger.info("Stripe webhook received (sig=%s, size=%d)", sig[:20] if sig else "none", len(body))

    return {"status": "received"}


@router.post("/portal")
async def create_billing_portal(
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Create a Stripe Customer Portal session for subscription management.

    Stub: Returns placeholder URL.
    """
    return {
        "status": "not_configured",
        "portal_url": None,
        "message": "Stripe billing portal is not configured.",
    }

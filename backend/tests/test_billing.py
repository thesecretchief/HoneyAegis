"""Tests for the Stripe billing API stubs."""

from app.api.billing import (
    SubscriptionPlan,
    SubscriptionStatus,
    CheckoutRequest,
    PLANS,
)


class TestBillingSchemas:
    """Test billing API Pydantic schemas."""

    def test_subscription_plan(self):
        plan = SubscriptionPlan(
            plan_id="test",
            name="Test Plan",
            price_monthly_usd=9.99,
            max_sensors=10,
            max_events_per_day=10000,
            features=["feature1", "feature2"],
        )
        assert plan.plan_id == "test"
        assert plan.price_monthly_usd == 9.99
        assert plan.is_current is False
        assert len(plan.features) == 2

    def test_subscription_status(self):
        status = SubscriptionStatus(
            tenant_id="tenant-123",
            plan="community",
            status="active",
            current_period_start=None,
            current_period_end=None,
            max_sensors=999,
            max_events_per_day=999999,
            usage_sensors=3,
            usage_events_today=150,
        )
        assert status.plan == "community"
        assert status.status == "active"
        assert status.usage_sensors == 3

    def test_checkout_request_defaults(self):
        req = CheckoutRequest(plan_id="pro")
        assert req.plan_id == "pro"
        assert "localhost:3000" in req.success_url
        assert "localhost:3000" in req.cancel_url

    def test_checkout_request_custom_urls(self):
        req = CheckoutRequest(
            plan_id="enterprise",
            success_url="https://app.example.com/billing/success",
            cancel_url="https://app.example.com/billing/cancel",
        )
        assert req.plan_id == "enterprise"
        assert "example.com" in req.success_url


class TestBillingPlans:
    """Test billing plan configuration."""

    def test_three_plans_exist(self):
        assert len(PLANS) == 3

    def test_community_plan_is_free(self):
        community = next(p for p in PLANS if p.plan_id == "community")
        assert community.price_monthly_usd == 0
        assert community.max_sensors == 999
        assert community.max_events_per_day == 999999

    def test_pro_plan_pricing(self):
        pro = next(p for p in PLANS if p.plan_id == "pro")
        assert pro.price_monthly_usd == 29
        assert pro.max_sensors == 50

    def test_enterprise_plan_pricing(self):
        enterprise = next(p for p in PLANS if p.plan_id == "enterprise")
        assert enterprise.price_monthly_usd == 99
        assert enterprise.max_sensors == 500

    def test_plans_ascending_price(self):
        prices = [p.price_monthly_usd for p in PLANS]
        assert prices == sorted(prices)

    def test_plans_ascending_sensors(self):
        sensors = [p.max_sensors for p in PLANS]
        assert sensors[1] < sensors[0]  # Pro < Community (unlimited)
        assert sensors[2] > sensors[1]  # Enterprise > Pro

    def test_all_plans_have_features(self):
        for plan in PLANS:
            assert len(plan.features) >= 3

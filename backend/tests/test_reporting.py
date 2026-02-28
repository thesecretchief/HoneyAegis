"""Tests for Advanced Reporting service."""

import pytest
from datetime import datetime, timezone
from app.services.reporting_service import (
    TimeRange,
    ThreatTrend,
    TopAttacker,
    AttackVector,
    ComplianceMetric,
    ExecutiveReport,
    calculate_risk_score,
    build_compliance_metrics,
    build_executive_report,
)


class TestTimeRange:
    def test_last_24h(self):
        tr = TimeRange.last_24h()
        assert tr.label == "Last 24 hours"
        assert tr.start < tr.end

    def test_last_7d(self):
        tr = TimeRange.last_7d()
        assert tr.label == "Last 7 days"

    def test_last_30d(self):
        tr = TimeRange.last_30d()
        assert tr.label == "Last 30 days"

    def test_last_90d(self):
        tr = TimeRange.last_90d()
        assert tr.label == "Last 90 days"


class TestRiskScore:
    def test_zero_inputs(self):
        score, level = calculate_risk_score(0, 0, 0, 0)
        assert score == 0.0
        assert level == "low"

    def test_low_activity(self):
        score, level = calculate_risk_score(5, 0, 0, 5)
        assert level == "low"

    def test_medium_activity(self):
        score, level = calculate_risk_score(50, 3, 0, 10)
        assert level == "medium"

    def test_high_activity(self):
        score, level = calculate_risk_score(200, 10, 2, 50)
        assert level == "high"

    def test_critical_activity(self):
        score, level = calculate_risk_score(2000, 100, 50, 1000)
        assert score == 100.0
        assert level == "critical"

    def test_max_capped_at_100(self):
        score, _ = calculate_risk_score(10000, 10000, 10000, 10000)
        assert score <= 100.0

    def test_session_only_contribution(self):
        score1, _ = calculate_risk_score(0, 0, 0, 0)
        score2, _ = calculate_risk_score(1000, 0, 0, 0)
        assert score2 > score1


class TestComplianceMetrics:
    def test_returns_list(self):
        metrics = build_compliance_metrics()
        assert isinstance(metrics, list)
        assert len(metrics) > 0

    def test_all_have_required_fields(self):
        metrics = build_compliance_metrics()
        for m in metrics:
            assert m.name
            assert m.status in ("pass", "warning", "fail")
            assert 0 <= m.score <= 100

    def test_has_pass_and_warning(self):
        metrics = build_compliance_metrics()
        statuses = {m.status for m in metrics}
        assert "pass" in statuses
        assert "warning" in statuses


class TestExecutiveReport:
    def test_build_report_defaults(self):
        tr = TimeRange.last_7d()
        report = build_executive_report(tr)
        assert report.time_range == "Last 7 days"
        assert report.total_sessions == 0
        assert report.risk_score == 0.0
        assert report.risk_level == "low"

    def test_build_report_with_data(self):
        tr = TimeRange.last_24h()
        attackers = [
            TopAttacker(ip_address="1.2.3.4", country="US", total_sessions=100)
        ]
        report = build_executive_report(
            tr,
            sessions=500,
            unique_ips=100,
            alerts=50,
            critical_alerts=10,
            malware=5,
            top_attackers=attackers,
        )
        assert report.total_sessions == 500
        assert report.risk_score > 0
        assert len(report.top_attackers) == 1
        assert len(report.compliance_metrics) > 0

    def test_report_has_generated_at(self):
        tr = TimeRange.last_7d()
        report = build_executive_report(tr)
        assert report.generated_at is not None


class TestDataModels:
    def test_threat_trend(self):
        trend = ThreatTrend(period="2026-02-28", total_sessions=100)
        assert trend.unique_ips == 0
        assert trend.critical_alerts == 0

    def test_top_attacker(self):
        attacker = TopAttacker(ip_address="1.2.3.4", country="US")
        assert attacker.total_sessions == 0
        assert attacker.threat_level == "unknown"

    def test_attack_vector(self):
        vector = AttackVector(protocol="ssh", count=500, percentage=75.0)
        assert vector.most_common_username == ""

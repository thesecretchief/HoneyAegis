"""Advanced Reporting Dashboard Service for HoneyAegis Enterprise.

Provides aggregated analytics, trend analysis, and executive-level
reporting data for the enterprise dashboard.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TimeRange:
    """Represents a reporting time range."""
    start: datetime
    end: datetime
    label: str = ""

    @classmethod
    def last_24h(cls) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(hours=24), end=now, label="Last 24 hours")

    @classmethod
    def last_7d(cls) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(days=7), end=now, label="Last 7 days")

    @classmethod
    def last_30d(cls) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(days=30), end=now, label="Last 30 days")

    @classmethod
    def last_90d(cls) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(days=90), end=now, label="Last 90 days")


@dataclass
class ThreatTrend:
    """Aggregated threat trend data point."""
    period: str
    total_sessions: int = 0
    unique_ips: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    malware_captures: int = 0
    avg_session_duration_seconds: float = 0.0


@dataclass
class TopAttacker:
    """Top attacking IP with aggregated stats."""
    ip_address: str
    country: str = ""
    city: str = ""
    total_sessions: int = 0
    total_commands: int = 0
    last_seen: str = ""
    threat_level: str = "unknown"


@dataclass
class AttackVector:
    """Attack vector breakdown."""
    protocol: str
    count: int = 0
    percentage: float = 0.0
    most_common_username: str = ""
    most_common_command: str = ""


@dataclass
class ComplianceMetric:
    """Compliance and security posture metric."""
    name: str
    status: str  # "pass", "warning", "fail"
    score: float = 0.0
    details: str = ""


@dataclass
class ExecutiveReport:
    """Executive-level summary report."""
    time_range: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_sessions: int = 0
    total_unique_ips: int = 0
    total_alerts: int = 0
    total_malware: int = 0
    threat_trends: list[ThreatTrend] = field(default_factory=list)
    top_attackers: list[TopAttacker] = field(default_factory=list)
    attack_vectors: list[AttackVector] = field(default_factory=list)
    compliance_metrics: list[ComplianceMetric] = field(default_factory=list)
    risk_score: float = 0.0
    risk_level: str = "low"


def calculate_risk_score(
    sessions: int,
    critical_alerts: int,
    malware_count: int,
    unique_ips: int,
) -> tuple[float, str]:
    """Calculate an overall risk score (0-100) and level.

    Factors: session volume, critical alerts, malware captures, attacker diversity.
    """
    score = 0.0

    # Session volume (max 25 points)
    if sessions > 1000:
        score += 25
    elif sessions > 500:
        score += 20
    elif sessions > 100:
        score += 15
    elif sessions > 10:
        score += 10
    elif sessions > 0:
        score += 5

    # Critical alerts (max 30 points)
    if critical_alerts > 50:
        score += 30
    elif critical_alerts > 20:
        score += 25
    elif critical_alerts > 5:
        score += 15
    elif critical_alerts > 0:
        score += 10

    # Malware captures (max 25 points)
    if malware_count > 20:
        score += 25
    elif malware_count > 5:
        score += 20
    elif malware_count > 0:
        score += 10

    # Attacker diversity (max 20 points)
    if unique_ips > 500:
        score += 20
    elif unique_ips > 100:
        score += 15
    elif unique_ips > 20:
        score += 10
    elif unique_ips > 0:
        score += 5

    # Determine level
    if score >= 75:
        level = "critical"
    elif score >= 50:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"

    return min(score, 100.0), level


def build_compliance_metrics() -> list[ComplianceMetric]:
    """Generate compliance posture metrics for the deployment."""
    return [
        ComplianceMetric(
            name="Non-root containers",
            status="pass",
            score=100.0,
            details="All containers run as non-root users",
        ),
        ComplianceMetric(
            name="Network isolation",
            status="pass",
            score=100.0,
            details="Honeypot network isolated from internal services",
        ),
        ComplianceMetric(
            name="Encrypted credentials",
            status="pass",
            score=100.0,
            details="All passwords hashed with bcrypt",
        ),
        ComplianceMetric(
            name="Rate limiting",
            status="pass",
            score=100.0,
            details="API rate limiting enabled (token bucket)",
        ),
        ComplianceMetric(
            name="Audit logging",
            status="pass",
            score=100.0,
            details="Structured audit logging for all security actions",
        ),
        ComplianceMetric(
            name="TLS termination",
            status="warning",
            score=50.0,
            details="Traefik available but requires full profile + domain",
        ),
        ComplianceMetric(
            name="Data retention policy",
            status="warning",
            score=50.0,
            details="No automatic data rotation configured — manual cleanup required",
        ),
    ]


def build_executive_report(
    time_range: TimeRange,
    sessions: int = 0,
    unique_ips: int = 0,
    alerts: int = 0,
    critical_alerts: int = 0,
    malware: int = 0,
    top_attackers: list[TopAttacker] | None = None,
    attack_vectors: list[AttackVector] | None = None,
) -> ExecutiveReport:
    """Build a complete executive report for the given time range."""
    risk_score, risk_level = calculate_risk_score(
        sessions=sessions,
        critical_alerts=critical_alerts,
        malware_count=malware,
        unique_ips=unique_ips,
    )

    return ExecutiveReport(
        time_range=time_range.label,
        total_sessions=sessions,
        total_unique_ips=unique_ips,
        total_alerts=alerts,
        total_malware=malware,
        top_attackers=top_attackers or [],
        attack_vectors=attack_vectors or [],
        compliance_metrics=build_compliance_metrics(),
        risk_score=risk_score,
        risk_level=risk_level,
    )

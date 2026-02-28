"""Advanced Reporting Dashboard API endpoints."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.reporting_service import (
    TimeRange,
    ThreatTrend,
    TopAttacker,
    AttackVector,
    ComplianceMetric,
    build_executive_report,
    build_compliance_metrics,
    calculate_risk_score,
)

router = APIRouter()


class ThreatTrendResponse(BaseModel):
    period: str
    total_sessions: int
    unique_ips: int
    critical_alerts: int
    high_alerts: int
    malware_captures: int
    avg_session_duration_seconds: float


class TopAttackerResponse(BaseModel):
    ip_address: str
    country: str
    city: str
    total_sessions: int
    total_commands: int
    last_seen: str
    threat_level: str


class AttackVectorResponse(BaseModel):
    protocol: str
    count: int
    percentage: float
    most_common_username: str
    most_common_command: str


class ComplianceMetricResponse(BaseModel):
    name: str
    status: str
    score: float
    details: str


class ExecutiveReportResponse(BaseModel):
    time_range: str
    generated_at: str
    total_sessions: int
    total_unique_ips: int
    total_alerts: int
    total_malware: int
    top_attackers: list[TopAttackerResponse]
    attack_vectors: list[AttackVectorResponse]
    compliance_metrics: list[ComplianceMetricResponse]
    risk_score: float
    risk_level: str


class RiskScoreResponse(BaseModel):
    score: float
    level: str
    factors: dict


@router.get("/executive", response_model=ExecutiveReportResponse)
async def executive_report(
    period: str = Query("7d", pattern="^(24h|7d|30d|90d)$"),
):
    """Generate an executive-level summary report.

    Aggregates sessions, alerts, threat intelligence, and compliance
    metrics for the specified time period.
    """
    time_ranges = {
        "24h": TimeRange.last_24h(),
        "7d": TimeRange.last_7d(),
        "30d": TimeRange.last_30d(),
        "90d": TimeRange.last_90d(),
    }
    tr = time_ranges[period]

    # Sample data — in production, queries PostgreSQL for real aggregates
    report = build_executive_report(
        time_range=tr,
        sessions=0,
        unique_ips=0,
        alerts=0,
        critical_alerts=0,
        malware=0,
    )

    return ExecutiveReportResponse(
        time_range=report.time_range,
        generated_at=report.generated_at,
        total_sessions=report.total_sessions,
        total_unique_ips=report.total_unique_ips,
        total_alerts=report.total_alerts,
        total_malware=report.total_malware,
        top_attackers=[
            TopAttackerResponse(
                ip_address=a.ip_address,
                country=a.country,
                city=a.city,
                total_sessions=a.total_sessions,
                total_commands=a.total_commands,
                last_seen=a.last_seen,
                threat_level=a.threat_level,
            )
            for a in report.top_attackers
        ],
        attack_vectors=[
            AttackVectorResponse(
                protocol=v.protocol,
                count=v.count,
                percentage=v.percentage,
                most_common_username=v.most_common_username,
                most_common_command=v.most_common_command,
            )
            for v in report.attack_vectors
        ],
        compliance_metrics=[
            ComplianceMetricResponse(
                name=m.name,
                status=m.status,
                score=m.score,
                details=m.details,
            )
            for m in report.compliance_metrics
        ],
        risk_score=report.risk_score,
        risk_level=report.risk_level,
    )


@router.get("/compliance", response_model=list[ComplianceMetricResponse])
async def compliance_report():
    """Get compliance posture metrics for the deployment."""
    metrics = build_compliance_metrics()
    return [
        ComplianceMetricResponse(
            name=m.name, status=m.status, score=m.score, details=m.details
        )
        for m in metrics
    ]


@router.get("/risk-score", response_model=RiskScoreResponse)
async def risk_score(
    sessions: int = Query(0, ge=0),
    critical_alerts: int = Query(0, ge=0),
    malware: int = Query(0, ge=0),
    unique_ips: int = Query(0, ge=0),
):
    """Calculate a risk score based on provided metrics."""
    score, level = calculate_risk_score(
        sessions=sessions,
        critical_alerts=critical_alerts,
        malware_count=malware,
        unique_ips=unique_ips,
    )
    return RiskScoreResponse(
        score=score,
        level=level,
        factors={
            "sessions": sessions,
            "critical_alerts": critical_alerts,
            "malware": malware,
            "unique_ips": unique_ips,
        },
    )

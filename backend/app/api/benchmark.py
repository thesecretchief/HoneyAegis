"""Performance benchmark and security audit API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.benchmark_service import (
    build_health_report,
    build_security_checklist,
    build_lighthouse_scores,
    get_system_info,
)

router = APIRouter()


class SystemInfoResponse(BaseModel):
    platform: str
    architecture: str
    python_version: str
    cpu_count: int
    hostname: str


class SecurityCheckItem(BaseModel):
    category: str
    item: str
    status: str
    details: str


class LighthouseResponse(BaseModel):
    performance: int
    accessibility: int
    best_practices: int
    seo: int
    metrics: dict


class HealthReportResponse(BaseModel):
    generated_at: str
    api_version: str
    system: SystemInfoResponse
    lighthouse_scores: LighthouseResponse
    security_checklist: list[SecurityCheckItem]


@router.get("/health-report", response_model=HealthReportResponse)
async def health_report():
    """Generate a comprehensive health and performance report.

    Includes system info, Lighthouse targets, and security audit checklist.
    """
    report = build_health_report()
    return HealthReportResponse(
        generated_at=report.generated_at,
        api_version=report.api_version,
        system=SystemInfoResponse(
            platform=report.system.platform,
            architecture=report.system.architecture,
            python_version=report.system.python_version,
            cpu_count=report.system.cpu_count,
            hostname=report.system.hostname,
        ),
        lighthouse_scores=LighthouseResponse(
            performance=report.lighthouse_scores["performance"],
            accessibility=report.lighthouse_scores["accessibility"],
            best_practices=report.lighthouse_scores["best_practices"],
            seo=report.lighthouse_scores["seo"],
            metrics=report.lighthouse_scores["metrics"],
        ),
        security_checklist=[
            SecurityCheckItem(**item) for item in report.security_checklist
        ],
    )


@router.get("/security-audit", response_model=list[SecurityCheckItem])
async def security_audit():
    """Run a security audit checklist against the deployment."""
    checklist = build_security_checklist()
    return [SecurityCheckItem(**item) for item in checklist]


@router.get("/lighthouse", response_model=LighthouseResponse)
async def lighthouse_scores():
    """Get target Lighthouse audit scores for the dashboard."""
    scores = build_lighthouse_scores()
    return LighthouseResponse(
        performance=scores["performance"],
        accessibility=scores["accessibility"],
        best_practices=scores["best_practices"],
        seo=scores["seo"],
        metrics=scores["metrics"],
    )

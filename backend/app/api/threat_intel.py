"""Threat intelligence API — lookup IPs/domains/hashes across multiple feeds."""

import logging

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from uuid import UUID

from app.api.auth import get_tenant_id
from app.services.threat_intel_service import (
    lookup_all,
    ThreatIntelResult,
    AggregatedIntel,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class IntelResultResponse(BaseModel):
    source: str
    indicator: str
    indicator_type: str
    malicious: bool
    confidence: int
    categories: list[str]
    tags: list[str]
    description: str
    first_seen: str | None
    last_seen: str | None
    reference_url: str | None


class AggregatedIntelResponse(BaseModel):
    indicator: str
    indicator_type: str
    overall_malicious: bool
    max_confidence: int
    all_tags: list[str]
    all_categories: list[str]
    sources_checked: int
    sources_matched: int
    results: list[IntelResultResponse]


class FeedStatusResponse(BaseModel):
    feed: str
    configured: bool
    description: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/lookup")
async def lookup_indicator(
    indicator: str = Query(..., description="IP, domain, hash, or URL to look up"),
    indicator_type: str = Query("ip", description="Type: ip, domain, hash, url"),
    tenant_id: UUID = Depends(get_tenant_id),
) -> AggregatedIntelResponse:
    """Look up an indicator across all configured threat intel feeds."""
    result = lookup_all(indicator, indicator_type)

    return AggregatedIntelResponse(
        indicator=result.indicator,
        indicator_type=result.indicator_type,
        overall_malicious=result.overall_malicious,
        max_confidence=result.max_confidence,
        all_tags=result.all_tags,
        all_categories=result.all_categories,
        sources_checked=result.sources_checked,
        sources_matched=result.sources_matched,
        results=[
            IntelResultResponse(
                source=r.source,
                indicator=r.indicator,
                indicator_type=r.indicator_type,
                malicious=r.malicious,
                confidence=r.confidence,
                categories=r.categories,
                tags=r.tags,
                description=r.description,
                first_seen=r.first_seen,
                last_seen=r.last_seen,
                reference_url=r.reference_url,
            )
            for r in result.results
        ],
    )


@router.get("/feeds")
async def list_feeds(
    tenant_id: UUID = Depends(get_tenant_id),
) -> list[FeedStatusResponse]:
    """List configured threat intel feeds and their status."""
    from app.core.config import settings

    feeds = [
        FeedStatusResponse(
            feed="abuseipdb",
            configured=bool(getattr(settings, "abuseipdb_api_key", "")),
            description="AbuseIPDB IP reputation database",
        ),
        FeedStatusResponse(
            feed="otx",
            configured=bool(getattr(settings, "otx_api_key", "")),
            description="AlienVault Open Threat Exchange",
        ),
        FeedStatusResponse(
            feed="misp",
            configured=bool(getattr(settings, "misp_url", "") and getattr(settings, "misp_api_key", "")),
            description="MISP Malware Information Sharing Platform",
        ),
        FeedStatusResponse(
            feed="virustotal",
            configured=bool(getattr(settings, "virustotal_api_key", "")),
            description="VirusTotal file and URL analysis",
        ),
    ]
    return feeds

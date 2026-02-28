"""Malware sandbox API — static analysis and optional dynamic analysis."""

import logging

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from uuid import UUID

from app.api.auth import get_tenant_id
from app.services.sandbox_service import (
    analyze_bytes,
    StaticAnalysisResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class FileMetadataResponse(BaseModel):
    filename: str
    size_bytes: int
    md5: str
    sha1: str
    sha256: str
    mime_type: str
    file_type: str


class StaticAnalysisResponse(BaseModel):
    file: FileMetadataResponse
    suspicious_strings: list[str]
    urls_found: list[str]
    ips_found: list[str]
    domains_found: list[str]
    matched_patterns: list[str]
    entropy: float
    is_packed: bool
    is_executable: bool
    risk_score: int
    verdict: str


class SandboxStatusResponse(BaseModel):
    static_analysis: str
    dynamic_analysis: str
    dynamic_engine: str | None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    tenant_id: UUID = Depends(get_tenant_id),
) -> StaticAnalysisResponse:
    """Upload and analyze a captured malware sample.

    Performs static analysis: hash computation, file type detection,
    entropy calculation, string extraction, and pattern matching.
    """
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:  # 50 MB limit
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 50 MB)",
        )

    result = analyze_bytes(data, filename=file.filename or "unknown")

    return StaticAnalysisResponse(
        file=FileMetadataResponse(
            filename=result.file.filename,
            size_bytes=result.file.size_bytes,
            md5=result.file.md5,
            sha1=result.file.sha1,
            sha256=result.file.sha256,
            mime_type=result.file.mime_type,
            file_type=result.file.file_type,
        ),
        suspicious_strings=result.suspicious_strings,
        urls_found=result.urls_found,
        ips_found=result.ips_found,
        domains_found=result.domains_found,
        matched_patterns=result.matched_patterns,
        entropy=result.entropy,
        is_packed=result.is_packed,
        is_executable=result.is_executable,
        risk_score=result.risk_score,
        verdict=result.verdict,
    )


@router.get("/status")
async def sandbox_status(
    tenant_id: UUID = Depends(get_tenant_id),
) -> SandboxStatusResponse:
    """Check sandbox capabilities."""
    from app.core.config import settings

    cuckoo_url = getattr(settings, "cuckoo_api_url", "") or ""

    return SandboxStatusResponse(
        static_analysis="enabled",
        dynamic_analysis="enabled" if cuckoo_url else "not_configured",
        dynamic_engine="cuckoo" if cuckoo_url else None,
    )

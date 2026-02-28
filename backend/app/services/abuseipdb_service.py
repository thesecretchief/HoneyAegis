"""AbuseIPDB reputation lookup service.

Optional integration — requires ABUSEIPDB_API_KEY in environment.
Results are cached in the geoip_cache table.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ABUSEIPDB_ENDPOINT = "https://api.abuseipdb.com/api/v2/check"


async def lookup_abuse_score(ip: str) -> dict | None:
    """Query AbuseIPDB for reputation data on an IP.

    Returns dict with: abuse_confidence_score, total_reports, last_reported_at
    Returns None if API key not configured or lookup fails.
    """
    api_key = getattr(settings, "abuseipdb_api_key", "") or ""
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                ABUSEIPDB_ENDPOINT,
                params={"ipAddress": ip, "maxAgeInDays": 90},
                headers={
                    "Key": api_key,
                    "Accept": "application/json",
                },
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                return {
                    "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
                    "total_reports": data.get("totalReports", 0),
                    "last_reported_at": data.get("lastReportedAt"),
                    "is_tor": data.get("isTor", False),
                    "usage_type": data.get("usageType", ""),
                    "domain": data.get("domain", ""),
                }
            else:
                logger.warning("AbuseIPDB returned %d for %s", resp.status_code, ip)
    except Exception as e:
        logger.warning("AbuseIPDB lookup failed for %s: %s", ip, e)

    return None

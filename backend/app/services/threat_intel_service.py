"""Threat intelligence feed integrations.

Supports:
  - MISP (Malware Information Sharing Platform)
  - AlienVault OTX (Open Threat Exchange)
  - AbuseIPDB (full API)
  - VirusTotal (optional stub)

All lookups return a normalized ThreatIntelResult. Feed APIs are called
lazily — the service gracefully degrades when API keys are missing.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class ThreatIntelResult:
    """Normalized result from any threat intel feed."""

    source: str
    indicator: str
    indicator_type: str  # "ip", "domain", "hash", "url"
    malicious: bool = False
    confidence: int = 0  # 0-100
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    description: str = ""
    first_seen: str | None = None
    last_seen: str | None = None
    reference_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedIntel:
    """Combined intel from all feeds for a single indicator."""

    indicator: str
    indicator_type: str
    results: list[ThreatIntelResult] = field(default_factory=list)
    overall_malicious: bool = False
    max_confidence: int = 0
    all_tags: list[str] = field(default_factory=list)
    all_categories: list[str] = field(default_factory=list)
    sources_checked: int = 0
    sources_matched: int = 0


# ---------------------------------------------------------------------------
# In-memory cache (TTL-based, avoids hammering feeds)
# ---------------------------------------------------------------------------
_intel_cache: dict[str, tuple[float, AggregatedIntel]] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_get(key: str) -> AggregatedIntel | None:
    entry = _intel_cache.get(key)
    if entry and time.monotonic() - entry[0] < CACHE_TTL:
        return entry[1]
    if entry:
        del _intel_cache[key]
    return None


def _cache_set(key: str, value: AggregatedIntel) -> None:
    _intel_cache[key] = (time.monotonic(), value)


# ---------------------------------------------------------------------------
# AbuseIPDB
# ---------------------------------------------------------------------------
def lookup_abuseipdb(ip: str) -> ThreatIntelResult | None:
    """Query AbuseIPDB for IP reputation."""
    api_key = getattr(settings, "abuseipdb_api_key", "") or ""
    if not api_key:
        return None

    try:
        import requests
        resp = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""},
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning("AbuseIPDB returned %d for %s", resp.status_code, ip)
            return None

        data = resp.json().get("data", {})
        score = data.get("abuseConfidenceScore", 0)
        categories = [str(c) for c in data.get("reports", [])[:5]]

        return ThreatIntelResult(
            source="abuseipdb",
            indicator=ip,
            indicator_type="ip",
            malicious=score >= 50,
            confidence=score,
            categories=categories,
            tags=["abuse"] if score >= 25 else [],
            description=f"AbuseIPDB score {score}%, {data.get('totalReports', 0)} reports",
            first_seen=None,
            last_seen=data.get("lastReportedAt"),
            reference_url=f"https://www.abuseipdb.com/check/{ip}",
            raw=data,
        )
    except Exception as exc:
        logger.error("AbuseIPDB lookup failed for %s: %s", ip, exc)
        return None


# ---------------------------------------------------------------------------
# AlienVault OTX
# ---------------------------------------------------------------------------
def lookup_otx(indicator: str, indicator_type: str = "ip") -> ThreatIntelResult | None:
    """Query AlienVault OTX for threat intel."""
    api_key = getattr(settings, "otx_api_key", "") or ""
    if not api_key:
        return None

    section = "IPv4" if indicator_type == "ip" else "general"

    try:
        import requests
        resp = requests.get(
            f"https://otx.alienvault.com/api/v1/indicators/{section}/{indicator}/general",
            headers={"X-OTX-API-KEY": api_key},
            timeout=10,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        pulse_count = data.get("pulse_info", {}).get("count", 0)
        tags = []
        for pulse in data.get("pulse_info", {}).get("pulses", [])[:5]:
            tags.extend(pulse.get("tags", []))

        return ThreatIntelResult(
            source="otx",
            indicator=indicator,
            indicator_type=indicator_type,
            malicious=pulse_count > 0,
            confidence=min(pulse_count * 10, 100),
            categories=[],
            tags=list(set(tags))[:10],
            description=f"Found in {pulse_count} OTX pulses",
            reference_url=f"https://otx.alienvault.com/indicator/{section}/{indicator}",
            raw=data,
        )
    except Exception as exc:
        logger.error("OTX lookup failed for %s: %s", indicator, exc)
        return None


# ---------------------------------------------------------------------------
# MISP
# ---------------------------------------------------------------------------
def lookup_misp(indicator: str, indicator_type: str = "ip") -> ThreatIntelResult | None:
    """Query a MISP instance for matching attributes."""
    misp_url = getattr(settings, "misp_url", "") or ""
    misp_key = getattr(settings, "misp_api_key", "") or ""
    if not misp_url or not misp_key:
        return None

    misp_type_map = {"ip": "ip-src", "domain": "domain", "hash": "md5", "url": "url"}
    attr_type = misp_type_map.get(indicator_type, "ip-src")

    try:
        import requests
        resp = requests.post(
            f"{misp_url.rstrip('/')}/attributes/restSearch",
            headers={
                "Authorization": misp_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"value": indicator, "type": attr_type, "limit": 10},
            timeout=15,
            verify=getattr(settings, "misp_verify_ssl", True),
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        attributes = data.get("response", {}).get("Attribute", [])
        if not attributes:
            return None

        tags = []
        for attr in attributes[:5]:
            for tag in attr.get("Tag", []):
                tags.append(tag.get("name", ""))

        return ThreatIntelResult(
            source="misp",
            indicator=indicator,
            indicator_type=indicator_type,
            malicious=True,
            confidence=80,
            categories=[attr.get("category", "") for attr in attributes[:3]],
            tags=list(set(tags))[:10],
            description=f"Found {len(attributes)} MISP attributes",
            first_seen=attributes[0].get("first_seen"),
            last_seen=attributes[0].get("last_seen"),
            reference_url=f"{misp_url}/attributes/restSearch",
            raw=data,
        )
    except Exception as exc:
        logger.error("MISP lookup failed for %s: %s", indicator, exc)
        return None


# ---------------------------------------------------------------------------
# VirusTotal
# ---------------------------------------------------------------------------
def lookup_virustotal(indicator: str, indicator_type: str = "ip") -> ThreatIntelResult | None:
    """Query VirusTotal for reputation (stub — requires API key)."""
    api_key = getattr(settings, "virustotal_api_key", "") or ""
    if not api_key:
        return None

    vt_type_map = {"ip": "ip_addresses", "domain": "domains", "hash": "files", "url": "urls"}
    endpoint = vt_type_map.get(indicator_type, "ip_addresses")

    lookup_id = indicator
    if indicator_type == "url":
        lookup_id = hashlib.sha256(indicator.encode()).hexdigest()

    try:
        import requests
        resp = requests.get(
            f"https://www.virustotal.com/api/v3/{endpoint}/{lookup_id}",
            headers={"x-apikey": api_key},
            timeout=15,
        )
        if resp.status_code != 200:
            return None

        data = resp.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        total = sum(stats.values()) if stats else 1

        return ThreatIntelResult(
            source="virustotal",
            indicator=indicator,
            indicator_type=indicator_type,
            malicious=malicious > 0,
            confidence=int(malicious / max(total, 1) * 100),
            categories=[],
            tags=data.get("tags", [])[:10],
            description=f"VT: {malicious}/{total} engines flagged",
            reference_url=f"https://www.virustotal.com/gui/search/{indicator}",
            raw=data,
        )
    except Exception as exc:
        logger.error("VirusTotal lookup failed for %s: %s", indicator, exc)
        return None


# ---------------------------------------------------------------------------
# Aggregated lookup
# ---------------------------------------------------------------------------
def lookup_all(indicator: str, indicator_type: str = "ip") -> AggregatedIntel:
    """Query all configured threat intel feeds and return aggregated results."""
    cache_key = f"{indicator_type}:{indicator}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    results: list[ThreatIntelResult] = []

    # Run lookups for each configured feed
    lookups = [
        ("abuseipdb", lookup_abuseipdb, indicator_type == "ip"),
        ("otx", lambda i: lookup_otx(i, indicator_type), True),
        ("misp", lambda i: lookup_misp(i, indicator_type), True),
        ("virustotal", lambda i: lookup_virustotal(i, indicator_type), True),
    ]

    sources_checked = 0
    for name, fn, applicable in lookups:
        if not applicable:
            continue
        sources_checked += 1
        try:
            result = fn(indicator)
            if result:
                results.append(result)
        except Exception as exc:
            logger.error("Feed %s failed for %s: %s", name, indicator, exc)

    all_tags: list[str] = []
    all_categories: list[str] = []
    for r in results:
        all_tags.extend(r.tags)
        all_categories.extend(r.categories)

    aggregated = AggregatedIntel(
        indicator=indicator,
        indicator_type=indicator_type,
        results=results,
        overall_malicious=any(r.malicious for r in results),
        max_confidence=max((r.confidence for r in results), default=0),
        all_tags=list(set(all_tags)),
        all_categories=list(set(all_categories)),
        sources_checked=sources_checked,
        sources_matched=len(results),
    )

    _cache_set(cache_key, aggregated)
    return aggregated

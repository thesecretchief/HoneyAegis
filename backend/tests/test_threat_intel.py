"""Tests for the threat intelligence service."""

from app.services.threat_intel_service import (
    ThreatIntelResult,
    AggregatedIntel,
    lookup_all,
    _cache_get,
    _cache_set,
    _intel_cache,
)


class TestThreatIntelResult:
    """Test ThreatIntelResult dataclass."""

    def test_defaults(self):
        result = ThreatIntelResult(
            source="test",
            indicator="1.2.3.4",
            indicator_type="ip",
        )
        assert result.malicious is False
        assert result.confidence == 0
        assert result.categories == []
        assert result.tags == []
        assert result.first_seen is None
        assert result.raw == {}

    def test_full(self):
        result = ThreatIntelResult(
            source="abuseipdb",
            indicator="185.220.101.42",
            indicator_type="ip",
            malicious=True,
            confidence=85,
            categories=["bruteforce", "ssh"],
            tags=["abuse", "tor-exit"],
            description="High confidence malicious IP",
            first_seen="2026-01-01T00:00:00Z",
            last_seen="2026-02-28T12:00:00Z",
            reference_url="https://abuseipdb.com/check/185.220.101.42",
        )
        assert result.malicious is True
        assert result.confidence == 85
        assert len(result.categories) == 2
        assert "tor-exit" in result.tags


class TestAggregatedIntel:
    """Test AggregatedIntel dataclass."""

    def test_defaults(self):
        agg = AggregatedIntel(indicator="1.2.3.4", indicator_type="ip")
        assert agg.overall_malicious is False
        assert agg.max_confidence == 0
        assert agg.results == []
        assert agg.sources_checked == 0

    def test_with_results(self):
        r1 = ThreatIntelResult(source="a", indicator="1.2.3.4", indicator_type="ip", malicious=True, confidence=80)
        r2 = ThreatIntelResult(source="b", indicator="1.2.3.4", indicator_type="ip", malicious=False, confidence=20)
        agg = AggregatedIntel(
            indicator="1.2.3.4",
            indicator_type="ip",
            results=[r1, r2],
            overall_malicious=True,
            max_confidence=80,
            sources_checked=2,
            sources_matched=2,
        )
        assert agg.overall_malicious is True
        assert agg.max_confidence == 80
        assert len(agg.results) == 2


class TestIntelCache:
    """Test the in-memory intel cache."""

    def test_cache_miss(self):
        result = _cache_get("nonexistent-key")
        assert result is None

    def test_cache_hit(self):
        agg = AggregatedIntel(indicator="test", indicator_type="ip")
        _cache_set("test-key", agg)
        result = _cache_get("test-key")
        assert result is not None
        assert result.indicator == "test"
        # Clean up
        _intel_cache.clear()


class TestLookupAll:
    """Test aggregated lookup (no API keys configured = empty results)."""

    def test_returns_aggregated_intel(self):
        result = lookup_all("1.2.3.4", "ip")
        assert isinstance(result, AggregatedIntel)
        assert result.indicator == "1.2.3.4"
        assert result.indicator_type == "ip"

    def test_no_keys_no_results(self):
        _intel_cache.clear()
        result = lookup_all("192.168.1.1", "ip")
        assert result.sources_matched == 0
        assert result.overall_malicious is False

    def test_domain_lookup(self):
        result = lookup_all("evil.example.com", "domain")
        assert result.indicator_type == "domain"

    def test_hash_lookup(self):
        result = lookup_all("d41d8cd98f00b204e9800998ecf8427e", "hash")
        assert result.indicator_type == "hash"

"""Tests for Performance Benchmark service."""

import pytest
from app.services.benchmark_service import (
    BenchmarkResult,
    SystemInfo,
    HealthReport,
    get_system_info,
    percentile,
    benchmark_operation,
    build_security_checklist,
    build_lighthouse_scores,
    build_health_report,
)


class TestSystemInfo:
    def test_get_system_info(self):
        info = get_system_info()
        assert info.platform
        assert info.architecture
        assert info.python_version
        assert info.cpu_count >= 1

    def test_hostname_not_empty(self):
        info = get_system_info()
        assert isinstance(info.hostname, str)


class TestPercentile:
    def test_empty_list(self):
        assert percentile([], 50) == 0.0

    def test_single_value(self):
        assert percentile([5.0], 50) == 5.0

    def test_p50(self):
        values = sorted([1.0, 2.0, 3.0, 4.0, 5.0])
        p50 = percentile(values, 50)
        assert p50 == 3.0

    def test_p95(self):
        values = sorted(list(range(100)))
        p95 = percentile([float(v) for v in values], 95)
        assert p95 >= 90

    def test_p99(self):
        values = sorted(list(range(100)))
        p99 = percentile([float(v) for v in values], 99)
        assert p99 >= 95


class TestBenchmarkOperation:
    def test_benchmark_simple(self):
        def noop():
            pass

        result = benchmark_operation("noop", noop, iterations=10)
        assert result.name == "noop"
        assert result.operations == 10
        assert result.duration_ms > 0
        assert result.ops_per_second > 0

    def test_benchmark_latencies(self):
        def noop():
            pass

        result = benchmark_operation("noop", noop, iterations=50)
        assert result.p50_ms >= 0
        assert result.p95_ms >= result.p50_ms
        assert result.p99_ms >= result.p95_ms


class TestSecurityChecklist:
    def test_returns_list(self):
        checklist = build_security_checklist()
        assert isinstance(checklist, list)
        assert len(checklist) > 0

    def test_all_items_have_required_fields(self):
        checklist = build_security_checklist()
        for item in checklist:
            assert "category" in item
            assert "item" in item
            assert "status" in item
            assert item["status"] in ("pass", "warning", "fail")

    def test_categories_present(self):
        checklist = build_security_checklist()
        categories = {item["category"] for item in checklist}
        assert "Authentication" in categories
        assert "Network" in categories
        assert "Data" in categories
        assert "CI/CD" in categories


class TestLighthouseScores:
    def test_target_scores(self):
        scores = build_lighthouse_scores()
        assert scores["performance"] >= 95
        assert scores["accessibility"] >= 95
        assert scores["best_practices"] >= 95
        assert scores["seo"] >= 95

    def test_metrics_present(self):
        scores = build_lighthouse_scores()
        assert "metrics" in scores
        assert "lcp_seconds" in scores["metrics"]
        assert "fid_ms" in scores["metrics"]
        assert "cls" in scores["metrics"]


class TestHealthReport:
    def test_build_report(self):
        report = build_health_report()
        assert report.api_version == "1.2.0"
        assert report.system is not None
        assert report.generated_at

    def test_report_has_scores(self):
        report = build_health_report()
        assert report.lighthouse_scores
        assert report.lighthouse_scores["performance"] >= 95

    def test_report_has_checklist(self):
        report = build_health_report()
        assert len(report.security_checklist) > 0


class TestBenchmarkResult:
    def test_defaults(self):
        result = BenchmarkResult(
            name="test",
            duration_ms=100.0,
            operations=50,
            ops_per_second=500.0,
        )
        assert result.p50_ms == 0.0
        assert result.metadata == {}

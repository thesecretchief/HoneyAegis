"""Tests for the advanced AI service."""

from app.services.advanced_ai_service import (
    LLMModel,
    SessionContext,
    ThreatAnalysis,
    MODEL_REGISTRY,
    select_model,
    build_rag_context,
    _parse_json_response,
)


class TestModelRegistry:
    """Test LLM model registry and selection."""

    def test_registry_has_models(self):
        assert len(MODEL_REGISTRY) >= 3

    def test_all_models_have_tags(self):
        for model in MODEL_REGISTRY:
            assert model.ollama_tag
            assert model.context_window > 0
            assert model.min_ram_mb > 0

    def test_select_model_summarize(self):
        model = select_model("summarize")
        assert "summarize" in model.capabilities

    def test_select_model_rag(self):
        model = select_model("rag")
        assert "rag" in model.capabilities

    def test_select_model_fallback(self):
        model = select_model("nonexistent-task")
        assert model is not None  # Returns fallback

    def test_models_sorted_by_priority(self):
        priorities = [m.priority for m in MODEL_REGISTRY]
        assert priorities == sorted(priorities)


class TestSessionContext:
    """Test session context dataclass."""

    def test_defaults(self):
        ctx = SessionContext(session_id="sess-01", src_ip="1.2.3.4")
        assert ctx.commands == []
        assert ctx.credentials == []
        assert ctx.duration_seconds == 0

    def test_full(self):
        ctx = SessionContext(
            session_id="sess-02",
            src_ip="10.0.0.1",
            country="US",
            commands=["whoami", "id", "cat /etc/passwd"],
            credentials=[("root", "admin"), ("admin", "password")],
            files_captured=["malware.sh"],
            duration_seconds=120,
            timestamp="2026-02-28T12:00:00Z",
        )
        assert len(ctx.commands) == 3
        assert len(ctx.credentials) == 2
        assert ctx.country == "US"


class TestRAGContext:
    """Test RAG context builder."""

    def test_empty_sessions(self):
        context = build_rag_context([])
        assert "RAG Context" in context

    def test_single_session(self):
        sessions = [
            SessionContext(
                session_id="sess-01",
                src_ip="1.2.3.4",
                country="CN",
                commands=["whoami", "uname -a"],
                credentials=[("root", "toor")],
                duration_seconds=60,
                timestamp="2026-02-28T12:00:00Z",
            ),
        ]
        context = build_rag_context(sessions)
        assert "sess-01" in context
        assert "1.2.3.4" in context
        assert "whoami" in context
        assert "root:toor" in context

    def test_max_tokens_limit(self):
        sessions = [
            SessionContext(
                session_id=f"sess-{i}",
                src_ip=f"10.0.0.{i}",
                commands=["cmd1", "cmd2", "cmd3"] * 10,
                duration_seconds=i * 10,
            )
            for i in range(50)
        ]
        context = build_rag_context(sessions, max_tokens=200)
        # Should not include all 50 sessions
        assert context.count("Session sess-") < 50

    def test_multiple_sessions(self):
        sessions = [
            SessionContext(session_id="s1", src_ip="1.1.1.1"),
            SessionContext(session_id="s2", src_ip="2.2.2.2"),
            SessionContext(session_id="s3", src_ip="3.3.3.3"),
        ]
        context = build_rag_context(sessions)
        assert "s1" in context
        assert "s2" in context
        assert "s3" in context


class TestJSONParsing:
    """Test LLM response JSON parsing."""

    def test_clean_json(self):
        result = _parse_json_response('{"threat_level": "high", "summary": "Test"}')
        assert result["threat_level"] == "high"

    def test_markdown_fenced(self):
        text = '```json\n{"threat_level": "medium"}\n```'
        result = _parse_json_response(text)
        assert result["threat_level"] == "medium"

    def test_embedded_json(self):
        text = 'Here is the analysis:\n{"threat_level": "low"}\nEnd.'
        result = _parse_json_response(text)
        assert result["threat_level"] == "low"

    def test_empty_string(self):
        result = _parse_json_response("")
        assert result == {}

    def test_invalid_json(self):
        result = _parse_json_response("not json at all")
        assert result == {}

    def test_none_input(self):
        result = _parse_json_response(None)
        assert result == {}


class TestThreatAnalysis:
    """Test ThreatAnalysis dataclass."""

    def test_defaults(self):
        analysis = ThreatAnalysis()
        assert analysis.threat_level == "unknown"
        assert analysis.summary == ""
        assert analysis.mitre_attack == []
        assert analysis.model_used == ""
        assert analysis.analysis_time_ms == 0

    def test_full(self):
        analysis = ThreatAnalysis(
            threat_level="high",
            summary="Brute-force SSH attack with post-exploitation",
            mitre_attack=["T1078", "T1059.004"],
            indicators_of_compromise=["185.220.101.42"],
            attacker_profile="Automated botnet",
            recommendations=["Block source IP"],
            model_used="phi3:mini",
            analysis_time_ms=1234,
        )
        assert analysis.threat_level == "high"
        assert len(analysis.mitre_attack) == 2
        assert analysis.analysis_time_ms == 1234

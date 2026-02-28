"""Advanced AI service — RAG over sessions and multi-LLM routing.

Provides:
  - Session-aware RAG: builds context from recent sessions for richer analysis
  - Multi-LLM routing: selects model based on task complexity
  - Structured output parsing for threat analysis
  - Batch analysis for multiple sessions

Uses Ollama as the LLM backend (no cloud dependency).
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------
@dataclass
class LLMModel:
    """An available LLM model with metadata."""

    name: str
    ollama_tag: str
    context_window: int
    capabilities: list[str]
    priority: int  # lower = preferred for matching tasks
    min_ram_mb: int = 1024


# Default model registry — lightweight models that fit in 4GB
MODEL_REGISTRY: list[LLMModel] = [
    LLMModel(
        name="phi3-mini",
        ollama_tag="phi3:mini",
        context_window=4096,
        capabilities=["summarize", "classify", "extract"],
        priority=1,
        min_ram_mb=1500,
    ),
    LLMModel(
        name="llama3.2",
        ollama_tag="llama3.2:3b",
        context_window=8192,
        capabilities=["summarize", "classify", "extract", "reason", "rag"],
        priority=2,
        min_ram_mb=2500,
    ),
    LLMModel(
        name="mistral",
        ollama_tag="mistral:7b",
        context_window=8192,
        capabilities=["summarize", "classify", "extract", "reason", "rag", "code"],
        priority=3,
        min_ram_mb=4500,
    ),
]


def select_model(task: str) -> LLMModel:
    """Select the best model for a given task based on capabilities and priority."""
    for model in sorted(MODEL_REGISTRY, key=lambda m: m.priority):
        if task in model.capabilities:
            return model
    return MODEL_REGISTRY[0]  # fallback to lightest


# ---------------------------------------------------------------------------
# RAG context builder
# ---------------------------------------------------------------------------
@dataclass
class SessionContext:
    """Context from a honeypot session for RAG."""

    session_id: str
    src_ip: str
    country: str | None = None
    commands: list[str] = field(default_factory=list)
    credentials: list[tuple[str, str]] = field(default_factory=list)
    files_captured: list[str] = field(default_factory=list)
    duration_seconds: int = 0
    timestamp: str = ""


def build_rag_context(
    sessions: list[SessionContext],
    max_tokens: int = 2048,
) -> str:
    """Build RAG context from recent sessions for enriched analysis.

    Assembles a structured text block from session data that fits
    within the model's context window.
    """
    lines = ["=== Recent Honeypot Activity (RAG Context) ===\n"]
    token_estimate = 20  # header

    for session in sessions[:20]:
        block = []
        block.append(f"Session {session.session_id}:")
        block.append(f"  Source: {session.src_ip} ({session.country or 'unknown'})")
        block.append(f"  Time: {session.timestamp}")
        block.append(f"  Duration: {session.duration_seconds}s")

        if session.credentials:
            creds = ", ".join(
                f"{u}:{p}" for u, p in session.credentials[:5]
            )
            block.append(f"  Credentials tried: {creds}")

        if session.commands:
            cmds = " ; ".join(session.commands[:10])
            block.append(f"  Commands: {cmds}")

        if session.files_captured:
            block.append(f"  Files: {', '.join(session.files_captured[:5])}")

        block_text = "\n".join(block) + "\n"
        block_tokens = len(block_text.split())

        if token_estimate + block_tokens > max_tokens:
            break

        lines.append(block_text)
        token_estimate += block_tokens

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Analysis prompts
# ---------------------------------------------------------------------------
THREAT_ANALYSIS_PROMPT = """You are a cybersecurity analyst reviewing honeypot session data.

{rag_context}

=== Current Session to Analyze ===
Source IP: {src_ip}
Country: {country}
Protocol: {protocol}
Duration: {duration}s
Commands executed:
{commands}

Credentials attempted:
{credentials}

Files captured: {files}

Analyze this session and respond in the following JSON format:
{{
  "threat_level": "critical|high|medium|low|info",
  "summary": "2-3 sentence analysis",
  "mitre_attack": ["T####.### technique IDs"],
  "indicators_of_compromise": ["IPs, domains, hashes found"],
  "attacker_profile": "Brief attacker characterization",
  "recommendations": ["1-2 defensive recommendations"]
}}
"""

BATCH_SUMMARY_PROMPT = """You are a cybersecurity analyst reviewing multiple honeypot sessions.

{rag_context}

Provide a brief summary of attack trends, common techniques, and recommendations.
Respond in JSON format:
{{
  "total_sessions": {session_count},
  "top_attack_types": ["list of attack categories"],
  "top_source_countries": ["list of countries"],
  "common_credentials": ["commonly attempted usernames"],
  "mitre_techniques": ["T####.### technique IDs observed"],
  "trend_summary": "2-3 sentence trend analysis",
  "recommendations": ["1-3 defensive recommendations"]
}}
"""


# ---------------------------------------------------------------------------
# Ollama interaction
# ---------------------------------------------------------------------------
def _call_ollama(prompt: str, model: LLMModel | None = None) -> str | None:
    """Send a prompt to Ollama and return the response text."""
    if model is None:
        model = select_model("summarize")

    ollama_host = getattr(settings, "ollama_host", "ollama")
    ollama_port = getattr(settings, "ollama_port", 11434)
    url = f"http://{ollama_host}:{ollama_port}/api/generate"

    try:
        import requests
        resp = requests.post(
            url,
            json={
                "model": model.ollama_tag,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 1024},
            },
            timeout=120,
        )
        if resp.status_code != 200:
            logger.warning("Ollama returned %d", resp.status_code)
            return None

        return resp.json().get("response", "")
    except Exception as exc:
        logger.error("Ollama call failed: %s", exc)
        return None


def _parse_json_response(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown fences."""
    if not text:
        return {}

    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass

    logger.warning("Failed to parse LLM response as JSON")
    return {}


# ---------------------------------------------------------------------------
# High-level analysis functions
# ---------------------------------------------------------------------------
@dataclass
class ThreatAnalysis:
    """Structured threat analysis result."""

    threat_level: str = "unknown"
    summary: str = ""
    mitre_attack: list[str] = field(default_factory=list)
    indicators_of_compromise: list[str] = field(default_factory=list)
    attacker_profile: str = ""
    recommendations: list[str] = field(default_factory=list)
    model_used: str = ""
    analysis_time_ms: int = 0


def analyze_session_with_rag(
    session: SessionContext,
    recent_sessions: list[SessionContext] | None = None,
) -> ThreatAnalysis:
    """Analyze a single session with RAG context from recent activity."""
    model = select_model("rag" if recent_sessions else "summarize")

    rag_context = ""
    if recent_sessions:
        rag_context = build_rag_context(recent_sessions)

    prompt = THREAT_ANALYSIS_PROMPT.format(
        rag_context=rag_context,
        src_ip=session.src_ip,
        country=session.country or "unknown",
        protocol="SSH",
        duration=session.duration_seconds,
        commands="\n".join(f"  $ {cmd}" for cmd in session.commands[:20]),
        credentials="\n".join(
            f"  {u}:{p}" for u, p in session.credentials[:10]
        ),
        files=", ".join(session.files_captured[:5]) or "none",
    )

    start = time.monotonic()
    response = _call_ollama(prompt, model)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    if not response:
        return ThreatAnalysis(
            summary="AI analysis unavailable — Ollama not connected",
            model_used=model.ollama_tag,
            analysis_time_ms=elapsed_ms,
        )

    parsed = _parse_json_response(response)

    return ThreatAnalysis(
        threat_level=parsed.get("threat_level", "unknown"),
        summary=parsed.get("summary", response[:500]),
        mitre_attack=parsed.get("mitre_attack", []),
        indicators_of_compromise=parsed.get("indicators_of_compromise", []),
        attacker_profile=parsed.get("attacker_profile", ""),
        recommendations=parsed.get("recommendations", []),
        model_used=model.ollama_tag,
        analysis_time_ms=elapsed_ms,
    )


def analyze_batch_trends(sessions: list[SessionContext]) -> dict[str, Any]:
    """Analyze trends across multiple sessions."""
    model = select_model("rag")
    rag_context = build_rag_context(sessions)

    prompt = BATCH_SUMMARY_PROMPT.format(
        rag_context=rag_context,
        session_count=len(sessions),
    )

    response = _call_ollama(prompt, model)
    if not response:
        return {"error": "AI analysis unavailable"}

    return _parse_json_response(response)

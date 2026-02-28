"""AI threat analysis service — local Ollama + LangChain.

All AI logic lives here. Provides session summarisation with MITRE ATT&CK
mapping, threat-level scoring, and plain-text overlay text for video export.

100 % local — no external API calls. Ollama runs only in the full profile.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SUMMARY_SYSTEM = """You are a cybersecurity analyst reviewing honeypot session data.
Provide a concise threat analysis in JSON format with these exact keys:
- "summary": 2-4 sentence description of what the attacker did
- "threat_level": one of "critical", "high", "medium", "low", "info"
- "mitre_ttps": list of MITRE ATT&CK technique IDs observed (e.g. ["T1078", "T1059.004"])
- "recommendations": 1-2 sentence defensive recommendation

Be precise and technical. Output ONLY valid JSON, no markdown fences."""

SUMMARY_USER = """Analyse this honeypot session:

Source IP: {src_ip}
Country: {country}
Protocol: {protocol} port {dst_port}
Username: {username}
Auth success: {auth_success}
Duration: {duration}s
Commands executed ({cmd_count}):
{commands}
Files downloaded ({download_count}):
{downloads}

Provide your JSON threat analysis."""

OVERLAY_SYSTEM = """You are a cybersecurity analyst. Given honeypot session data,
produce a SHORT 1-2 line summary suitable for burning into a video overlay.
Include the threat level and most notable attacker action. Max 120 characters.
Output ONLY the overlay text, nothing else."""


# ---------------------------------------------------------------------------
# Ollama client helpers
# ---------------------------------------------------------------------------

def _ollama_base_url() -> str:
    return f"http://{settings.ollama_host}:{settings.ollama_port}"


async def _ollama_available() -> bool:
    """Check if Ollama is reachable and the configured model exists."""
    if not settings.ollama_enabled:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{_ollama_base_url()}/api/tags")
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            model = settings.ollama_model
            return any(model in m for m in models)
    except Exception:
        return False


async def _chat(system: str, user: str) -> str:
    """Send a chat completion request to Ollama and return the response text."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{_ollama_base_url()}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 512},
            },
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def is_ai_enabled() -> bool:
    """Return True if AI summaries are available."""
    return await _ollama_available()


async def generate_session_summary(session_data: dict[str, Any]) -> dict[str, Any] | None:
    """Generate an AI threat summary for a honeypot session.

    Returns a dict with keys: summary, threat_level, mitre_ttps, recommendations, model_used.
    Returns None if Ollama is unavailable or an error occurs.
    """
    if not await _ollama_available():
        logger.debug("Ollama not available — skipping AI summary")
        return None

    commands_text = "\n".join(
        f"  $ {c}" for c in (session_data.get("commands") or [])
    ) or "  (none)"

    downloads_text = "\n".join(
        f"  {d.get('filename', '?')} — {d.get('url', '?')} (sha256: {d.get('sha256', '?')})"
        for d in (session_data.get("downloads") or [])
    ) or "  (none)"

    user_prompt = SUMMARY_USER.format(
        src_ip=session_data.get("src_ip", "unknown"),
        country=session_data.get("country_name", "Unknown"),
        protocol=session_data.get("protocol", "ssh"),
        dst_port=session_data.get("dst_port", "?"),
        username=session_data.get("username", "N/A"),
        auth_success=session_data.get("auth_success", False),
        duration=session_data.get("duration_seconds", 0),
        cmd_count=len(session_data.get("commands") or []),
        commands=commands_text,
        download_count=len(session_data.get("downloads") or []),
        downloads=downloads_text,
    )

    try:
        raw = await _chat(SUMMARY_SYSTEM, user_prompt)
        result = _parse_json_response(raw)
        result["model_used"] = settings.ollama_model
        return result
    except Exception as e:
        logger.error("AI summary generation failed: %s", e)
        return None


async def generate_video_overlay(session_data: dict[str, Any]) -> str:
    """Generate a short overlay line for video export.

    Returns a plain string (max ~120 chars). Falls back to a static string.
    """
    if not await _ollama_available():
        return _fallback_overlay(session_data)

    commands_text = ", ".join(
        (session_data.get("commands") or [])[:5]
    ) or "(none)"

    user_prompt = (
        f"IP: {session_data.get('src_ip', '?')} | "
        f"User: {session_data.get('username', 'N/A')} | "
        f"Commands: {commands_text} | "
        f"Duration: {session_data.get('duration_seconds', 0)}s"
    )

    try:
        text = await _chat(OVERLAY_SYSTEM, user_prompt)
        return text.strip()[:120]
    except Exception:
        return _fallback_overlay(session_data)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_response(raw: str) -> dict[str, Any]:
    """Parse a JSON response, stripping markdown fences if present."""
    import json

    text = raw.strip()
    # Strip ```json ... ``` wrappers
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    data = json.loads(text)
    return {
        "summary": data.get("summary", "No summary available."),
        "threat_level": data.get("threat_level", "medium"),
        "mitre_ttps": data.get("mitre_ttps", []),
        "recommendations": data.get("recommendations", ""),
    }


def _fallback_overlay(session_data: dict[str, Any]) -> str:
    """Static overlay when AI is unavailable."""
    ip = session_data.get("src_ip", "unknown")
    user = session_data.get("username", "N/A")
    cmds = len(session_data.get("commands") or [])
    return f"HoneyAegis | {ip} as {user} | {cmds} cmds"

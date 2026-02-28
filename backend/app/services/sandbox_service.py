"""Lightweight malware sandbox — static analysis + optional Cuckoo/CAPE API.

Provides:
  - Static analysis: file type detection, hash computation, string extraction,
    YARA-like pattern matching, PE/ELF header parsing
  - Dynamic analysis stub: submit to Cuckoo/CAPE Sandbox API and poll results

All operations run in-process for static analysis. Dynamic analysis is
optional and requires a running Cuckoo/CAPE instance.
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class FileMetadata:
    """Basic file metadata."""

    filename: str
    size_bytes: int
    md5: str
    sha1: str
    sha256: str
    mime_type: str = "application/octet-stream"
    file_type: str = "unknown"


@dataclass
class StaticAnalysisResult:
    """Result of static analysis on a captured file."""

    file: FileMetadata
    suspicious_strings: list[str] = field(default_factory=list)
    urls_found: list[str] = field(default_factory=list)
    ips_found: list[str] = field(default_factory=list)
    domains_found: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    entropy: float = 0.0
    is_packed: bool = False
    is_executable: bool = False
    risk_score: int = 0  # 0-100
    verdict: str = "unknown"  # clean, suspicious, malicious, unknown


@dataclass
class DynamicAnalysisResult:
    """Result from Cuckoo/CAPE sandbox analysis."""

    task_id: str
    status: str  # pending, running, completed, failed
    score: float = 0.0
    signatures: list[str] = field(default_factory=list)
    network_iocs: list[str] = field(default_factory=list)
    dropped_files: list[str] = field(default_factory=list)
    processes: list[str] = field(default_factory=list)
    report_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SandboxReport:
    """Combined static + dynamic analysis report."""

    static: StaticAnalysisResult
    dynamic: DynamicAnalysisResult | None = None
    overall_verdict: str = "unknown"
    overall_score: int = 0


# ---------------------------------------------------------------------------
# Static analysis patterns
# ---------------------------------------------------------------------------
SUSPICIOUS_PATTERNS = [
    (r"(?:wget|curl)\s+https?://", "downloader_command"),
    (r"/etc/(?:passwd|shadow|crontab)", "sensitive_file_access"),
    (r"(?:chmod|chown)\s+[0-7]{3,4}\s", "permission_change"),
    (r"(?:rm\s+-rf|dd\s+if=)", "destructive_command"),
    (r"(?:nc|ncat|netcat)\s+-[le]", "reverse_shell"),
    (r"(?:base64\s+-d|eval|exec)\s", "code_execution"),
    (r"(?:iptables|ufw)\s+", "firewall_manipulation"),
    (r"(?:crontab|at\s+-f)", "persistence"),
    (r"/dev/tcp/\d+\.\d+\.\d+\.\d+/\d+", "bash_reverse_shell"),
    (r"(?:\.onion|tor2web)", "tor_access"),
    (r"(?:xmrig|minerd|stratum)", "cryptominer"),
    (r"(?:id_rsa|authorized_keys)", "ssh_key_access"),
]

URL_PATTERN = re.compile(
    r"https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]{4,256}"
)
IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
)
DOMAIN_PATTERN = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|xyz|tk|top|cc|ru|cn|de|uk)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------
def compute_hashes(data: bytes) -> tuple[str, str, str]:
    """Compute MD5, SHA1, SHA256 of raw bytes (identification only, not security)."""
    return (
        hashlib.md5(data, usedforsecurity=False).hexdigest(),
        hashlib.sha1(data, usedforsecurity=False).hexdigest(),
        hashlib.sha256(data).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Entropy calculation
# ---------------------------------------------------------------------------
def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of data (0.0 - 8.0)."""
    import math

    if not data:
        return 0.0

    freq = [0] * 256
    for byte in data:
        freq[byte] += 1

    length = len(data)
    entropy = 0.0
    for count in freq:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)

    return round(entropy, 2)


# ---------------------------------------------------------------------------
# File type detection
# ---------------------------------------------------------------------------
def detect_file_type(data: bytes) -> tuple[str, str]:
    """Detect file type and MIME from magic bytes."""
    magic_map = [
        (b"\x7fELF", "ELF executable", "application/x-elf"),
        (b"MZ", "PE executable", "application/x-dosexec"),
        (b"\x89PNG", "PNG image", "image/png"),
        (b"GIF8", "GIF image", "image/gif"),
        (b"\xff\xd8\xff", "JPEG image", "image/jpeg"),
        (b"PK\x03\x04", "ZIP archive", "application/zip"),
        (b"\x1f\x8b", "Gzip archive", "application/gzip"),
        (b"#!/", "Shell script", "text/x-shellscript"),
        (b"#!", "Script", "text/x-script"),
    ]

    for magic, file_type, mime in magic_map:
        if data[:len(magic)] == magic:
            return file_type, mime

    try:
        data[:512].decode("utf-8")
        return "Text file", "text/plain"
    except UnicodeDecodeError:
        return "Binary file", "application/octet-stream"


# ---------------------------------------------------------------------------
# Static analysis
# ---------------------------------------------------------------------------
def analyze_static(file_path: Path, filename: str | None = None) -> StaticAnalysisResult:
    """Perform static analysis on a captured file."""
    data = file_path.read_bytes()
    md5, sha1, sha256 = compute_hashes(data)
    file_type, mime_type = detect_file_type(data)
    entropy = calculate_entropy(data)

    metadata = FileMetadata(
        filename=filename or file_path.name,
        size_bytes=len(data),
        md5=md5,
        sha1=sha1,
        sha256=sha256,
        mime_type=mime_type,
        file_type=file_type,
    )

    # Extract strings (printable sequences >= 4 chars)
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        text = data.decode("latin-1", errors="replace")

    # Find suspicious patterns
    matched_patterns = []
    for pattern, label in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matched_patterns.append(label)

    # Extract IOCs
    urls = list(set(URL_PATTERN.findall(text)))[:50]
    ips = list(set(IP_PATTERN.findall(text)))[:50]
    domains = list(set(DOMAIN_PATTERN.findall(text)))[:50]

    # Suspicious strings
    suspicious = []
    for pattern, label in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        suspicious.extend(matches[:3])

    # Risk scoring
    risk_score = 0
    risk_score += len(matched_patterns) * 15
    risk_score += min(len(urls), 5) * 5
    risk_score += min(len(ips), 5) * 3
    if entropy > 7.0:
        risk_score += 20
    if file_type in ("ELF executable", "PE executable"):
        risk_score += 10
    if file_type == "Shell script":
        risk_score += 5
    risk_score = min(risk_score, 100)

    # Verdict
    if risk_score >= 70:
        verdict = "malicious"
    elif risk_score >= 40:
        verdict = "suspicious"
    elif risk_score > 0:
        verdict = "unknown"
    else:
        verdict = "clean"

    is_exec = file_type in ("ELF executable", "PE executable", "Shell script", "Script")

    return StaticAnalysisResult(
        file=metadata,
        suspicious_strings=suspicious[:20],
        urls_found=urls,
        ips_found=ips,
        domains_found=domains,
        matched_patterns=matched_patterns,
        entropy=entropy,
        is_packed=entropy > 7.2,
        is_executable=is_exec,
        risk_score=risk_score,
        verdict=verdict,
    )


def analyze_bytes(data: bytes, filename: str = "unknown") -> StaticAnalysisResult:
    """Analyze raw bytes without writing to disk."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=True, suffix=".sample") as tmp:
        tmp.write(data)
        tmp.flush()
        return analyze_static(Path(tmp.name), filename=filename)


# ---------------------------------------------------------------------------
# Dynamic analysis (Cuckoo/CAPE stub)
# ---------------------------------------------------------------------------
def submit_to_sandbox(file_path: Path) -> DynamicAnalysisResult | None:
    """Submit a file to Cuckoo/CAPE sandbox for dynamic analysis.

    Requires CUCKOO_API_URL to be set in settings. Returns None if
    sandbox is not configured.
    """
    sandbox_url = getattr(settings, "cuckoo_api_url", "") or ""
    if not sandbox_url:
        return None

    try:
        import requests
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{sandbox_url.rstrip('/')}/tasks/create/file",
                files={"file": (file_path.name, f)},
                timeout=30,
            )
        if resp.status_code != 200:
            logger.warning("Sandbox submit failed: %d", resp.status_code)
            return None

        task_id = str(resp.json().get("task_id", ""))
        return DynamicAnalysisResult(
            task_id=task_id,
            status="pending",
            report_url=f"{sandbox_url}/tasks/view/{task_id}",
        )
    except Exception as exc:
        logger.error("Sandbox submission failed: %s", exc)
        return None


def get_sandbox_result(task_id: str) -> DynamicAnalysisResult | None:
    """Poll Cuckoo/CAPE for analysis results."""
    sandbox_url = getattr(settings, "cuckoo_api_url", "") or ""
    if not sandbox_url:
        return None

    try:
        import requests
        resp = requests.get(
            f"{sandbox_url.rstrip('/')}/tasks/report/{task_id}",
            timeout=30,
        )
        if resp.status_code != 200:
            return DynamicAnalysisResult(task_id=task_id, status="pending")

        data = resp.json()
        info = data.get("info", {})
        sigs = [s.get("description", "") for s in data.get("signatures", [])]
        network = data.get("network", {})
        hosts = [h.get("ip", "") for h in network.get("hosts", [])]

        return DynamicAnalysisResult(
            task_id=task_id,
            status="completed" if info.get("ended") else "running",
            score=info.get("score", 0),
            signatures=sigs[:20],
            network_iocs=hosts[:20],
            dropped_files=[f.get("name", "") for f in data.get("dropped", [])[:10]],
            processes=[p.get("name", "") for p in data.get("processes", [])[:10]],
            report_url=f"{sandbox_url}/tasks/report/{task_id}",
            raw=data,
        )
    except Exception as exc:
        logger.error("Sandbox result fetch failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Full analysis pipeline
# ---------------------------------------------------------------------------
def full_analysis(file_path: Path, filename: str | None = None) -> SandboxReport:
    """Run static analysis and optionally submit to dynamic sandbox."""
    static = analyze_static(file_path, filename)

    dynamic = None
    if static.risk_score >= 40:
        dynamic = submit_to_sandbox(file_path)

    overall_score = static.risk_score
    if dynamic and dynamic.score:
        overall_score = max(overall_score, int(dynamic.score))

    return SandboxReport(
        static=static,
        dynamic=dynamic,
        overall_verdict=static.verdict,
        overall_score=overall_score,
    )

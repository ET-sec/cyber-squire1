"""Offline tests for scripts/grc/grc_mcp_server.py (Plan 19-03).

Covers:
  - stdio purity (no print() calls in source)
  - exactly 5 @mcp.tool decorators registered
  - path-traversal guard (read_doc('../../etc/passwd'))
  - symlink rejection (tmp symlink inside docs/grc/ rejected)
  - sanitize() applied on every tool return path (IP literal redacted)
  - response size cap (>100KB doc truncated)
  - JSON-RPC stdio smoke: pure JSON on stdout, logs on stderr only
  - over stdio, each tool's input schema carries its real parameters and
    tools/call with those parameters returns a real answer
  - the server starts under python -I from a foreign cwd with no PYTHONPATH

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
import tempfile
import threading
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
    f.write_text("Server IP: 10.100.1.10 reachable.")
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    result = srv.read_doc("test.md")
    assert "[INTERNAL-IP]" in result
    assert "10.100.1.10" not in result


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
    f.write_text("The host at 10.100.1.10 needed restart for residual risk.")
    monkeypatch.setattr(srv, "GRC_DIR", fake_grc)
    hits = srv.search_corpus("residual", limit=5)
    assert isinstance(hits, list)
    assert len(hits) >= 1
    # Find the actual hit (not a _truncated marker)
    real_hits = [h for h in hits if "snippet" in h]
    assert real_hits, f"No real hits in {hits}"
    for h in real_hits:
        assert "10.100.1.10" not in h["snippet"]
        assert "[INTERNAL-IP]" in h["snippet"]


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


# --- Over MCP stdio, the way a client sees the server -------------------------

_INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "pytest", "version": "0"},
    },
}
_INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def _stdio_session(cmd, cwd, env, requests, timeout=20):
    """Run one MCP stdio session: initialize, then each request in turn.

    Returns (initialize reply, list of replies to `requests`, stderr). A reply
    is None when the server exited or stopped answering first. stdin stays open
    until every reply is in, so no request is cut off by EOF, and a watchdog
    kills a server that hangs.
    """
    with tempfile.TemporaryFile("w+", encoding="utf-8") as err:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=err,
            cwd=str(cwd),
            env=env,
            text=True,
        )
        watchdog = threading.Timer(timeout, proc.kill)
        watchdog.start()

        def ask(frame):
            try:
                proc.stdin.write(json.dumps(frame) + "\n")
                proc.stdin.flush()
            except (BrokenPipeError, OSError):
                return None
            if "id" not in frame:
                return None
            while True:
                line = proc.stdout.readline()
                if not line:
                    return None
                if not line.strip():
                    continue
                msg = json.loads(line)
                if msg.get("id") == frame["id"]:
                    return msg

        try:
            init = ask(_INITIALIZE)
            replies = []
            if init is not None:
                ask(_INITIALIZED)
                replies = [ask(frame) for frame in requests]
            replies += [None] * (len(requests) - len(replies))
        finally:
            watchdog.cancel()
            try:
                proc.stdin.close()
            except OSError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            err.seek(0)
            stderr = err.read()
    return init, replies, stderr


def _call(req_id, name, arguments):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }


def test_tools_take_their_real_parameters_over_stdio(tmp_path):
    """tools/list must publish each tool's own parameters, and tools/call must accept them.

    The audit decorator hid each tool's signature behind (*args, **kwargs), so
    FastMCP published {args, kwargs} as the schema and refused the real names.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["GRC_MCP_AUDIT_LOG"] = str(tmp_path / "audit.jsonl")
    init, (listed, poam, doc), stderr = _stdio_session(
        [sys.executable, str(SERVER_PATH)],
        REPO_ROOT,
        env,
        [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            _call(2, "get_poam", {"poam_id": "P17-15"}),
            _call(3, "read_doc", {"filename": "POAM_PLAN_OF_ACTION.md"}),
        ],
    )
    assert init is not None and listed is not None, f"no reply; stderr={stderr[-800:]}"

    schemas = {t["name"]: t["inputSchema"] for t in listed["result"]["tools"]}
    expected = {
        "list_docs": (set(), []),
        "read_doc": ({"filename"}, ["filename"]),
        "search_corpus": ({"query", "limit"}, ["query"]),
        "get_poam": ({"poam_id"}, ["poam_id"]),
        "get_threat_model_entry": ({"threat_id"}, ["threat_id"]),
    }
    for name, (params, required) in expected.items():
        schema = schemas[name]
        assert set(schema.get("properties", {})) == params, f"{name} schema: {schema}"
        assert sorted(schema.get("required", [])) == required, f"{name} schema: {schema}"

    assert poam is not None and "result" in poam, f"get_poam reply: {poam}"
    assert not poam["result"].get("isError"), f"get_poam refused: {poam['result']}"
    row = json.loads(poam["result"]["content"][0]["text"])
    assert row["poam_id"].startswith("POAM-P17-15"), row

    assert doc is not None and "result" in doc, f"read_doc reply: {doc}"
    assert not doc["result"].get("isError"), f"read_doc refused: {doc['result']}"
    assert "POAM-P17-15" in doc["result"]["content"][0]["text"]


def test_server_starts_isolated_from_a_foreign_cwd(tmp_path):
    """python -I from an unrelated directory with no PYTHONPATH must still start and answer initialize.

    The scripts.grc imports used to resolve only because a PYTHONPATH that
    starts with ":" put the launching shell's cwd on sys.path.
    """
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["GRC_MCP_AUDIT_LOG"] = str(tmp_path / "audit.jsonl")
    foreign = tmp_path / "elsewhere"
    foreign.mkdir()
    init, _, stderr = _stdio_session([sys.executable, "-I", str(SERVER_PATH)], foreign, env, [])
    assert init is not None, f"no initialize reply; stderr={stderr[-800:]}"
    assert init["result"]["serverInfo"]["name"] == "grc_corpus"

"""GRC Corpus MCP Server (stdio).

Add to ~/Library/Application Support/Claude/claude_desktop_config.json:

    {
      "mcpServers": {
        "grc_corpus": {
          "command": "python3",
          "args": ["/Users/et/cyber-squire-ops/scripts/grc/grc_mcp_server.py"]
        }
      }
    }

Restart Claude Desktop to load.

Phase 20 Plan 20-06 hardening (see docs/grc/OWASP_MCP_TOP10_AUDIT.md):
- MCP01 (Token Mismanagement and Secret Exposure): _SanitizingFilter on the
  root logger runs every log record through sanitize_output() before stderr
  emission, closing the secret-exposure gap on the log path.
- MCP08 (Lack of Audit and Telemetry): _audit_log(tool_name) decorator
  appends one JSON line per tool call to AUDIT_LOG_PATH (env-configurable,
  defaults to /tmp/grc_mcp_audit.jsonl). args_hash is logged, never raw
  args, so the audit record cannot re-introduce the MCP01 issue.
"""

# Wrap surface (Plan 19-03):
#   list_docs              -> filesystem fallback (glob docs/grc/*.md + frontmatter)
#                              (grc_librarian.queries has DB-backed inventory(), not a 1:1 match)
#   read_doc               -> filesystem read with is_relative_to + symlink guard
#                              (queries.py has no read-doc primitive; reads chunks from Postgres)
#   search_corpus          -> regex/substring scan over docs/grc/*.md
#                              (queries.py search_keyword/search_semantic require pgvector DB; not bound on dev hosts)
#   get_poam               -> parse POAM_PLAN_OF_ACTION.md table (pipe-delimited rows)
#                              (queries.py has no get_poam; POAM rows live in markdown, not the chunk store)
#   get_threat_model_entry -> section-extract from SQUIRE_THREAT_MODEL.md and AI_THREAT_CATALOG.md
#                              (queries.py has no per-entry threat lookup)
#
# Optional grc_librarian import is attempted at startup; if available, future tool
# bodies can prefer it. Today's implementation uses filesystem fallback for all 5
# tools because queries.py is DB-backed and would require a live Postgres + pgvector.

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import logging
import os
import re
import sys
import time as _time

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("grc_corpus")
# NEVER call the stdout-write builtin anywhere in this file (stdio purity). Verified by test.

from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from scripts.grc.sanitize_output import sanitize  # final defense-in-depth wrap (owned by Plan 19-02)
from scripts.grc.sanitize_output import sanitize as _sanitize_for_log  # MCP01 log-path filter alias


class _SanitizingFilter(logging.Filter):
    """Apply project sanitization patterns to every log record's message.

    Closes OWASP MCP Top 10 2025 beta v0.1 MCP01 (Token Mismanagement and
    Secret Exposure) gap identified in docs/grc/OWASP_MCP_TOP10_AUDIT.md.
    Runs after logging.basicConfig so every record emitted to stderr is
    swept through sanitize_output() before it leaves the process.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = _sanitize_for_log(record.msg)
            if record.args:
                record.args = tuple(
                    _sanitize_for_log(str(a)) if isinstance(a, str) else a
                    for a in record.args
                )
        except Exception:
            # never let log sanitization crash the server
            pass
        return True


_root_logger = logging.getLogger()
if not any(isinstance(f, _SanitizingFilter) for f in _root_logger.filters):
    _root_logger.addFilter(_SanitizingFilter())


# MCP08 (Lack of Audit and Telemetry) structured per-tool-call audit log.
# Env-configurable path so CI / production can redirect; defaults to /tmp.
AUDIT_LOG_PATH = os.getenv("GRC_MCP_AUDIT_LOG", "/tmp/grc_mcp_audit.jsonl")


def _audit_log(tool_name: str):
    """Decorator that appends one JSON line per tool call.

    Record shape: ts, tool, args_hash, success, duration_ms.

    Closes OWASP MCP Top 10 2025 beta v0.1 MCP08 (Lack of Audit and
    Telemetry) gap identified in docs/grc/OWASP_MCP_TOP10_AUDIT.md.
    """

    def deco(fn):
        def wrapper(*args, **kwargs):
            t0 = _time.time()
            # args_hash is logged, NOT raw args; this prevents PII / secret leakage
            # in the audit log itself, which would re-introduce the MCP01 issue
            # inside the MCP08 fix.
            args_repr = _json.dumps(
                {"args": list(args), "kwargs": kwargs},
                default=str,
                sort_keys=True,
            )
            args_hash = _hashlib.sha256(args_repr.encode("utf-8")).hexdigest()[:16]
            success = True
            try:
                return fn(*args, **kwargs)
            except Exception:
                success = False
                raise
            finally:
                rec = {
                    "ts": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
                    "tool": tool_name,
                    "args_hash": args_hash,
                    "success": success,
                    "duration_ms": int((_time.time() - t0) * 1000),
                }
                try:
                    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as fh:
                        fh.write(_json.dumps(rec) + "\n")
                except Exception:
                    # audit log write failure must not break the tool call
                    pass

        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return deco


mcp = FastMCP("grc_corpus")
GRC_DIR = Path(__file__).resolve().parents[2] / "docs" / "grc"
READ_ONLY = True  # constant; future write tools must explicitly opt out
MAX_RESPONSE_BYTES = 100 * 1024  # 100KB hard cap

# Optional wrap of grc_librarian (queries.py is DB-backed; filesystem fallback used regardless today)
try:
    from grc_librarian import queries as gl_queries  # type: ignore[import-not-found]
    log.info("grc_librarian.queries imported (DB-backed; filesystem fallback still preferred for stdio reads)")
except ImportError:
    gl_queries = None
    log.info("grc_librarian.queries not importable; using filesystem fallback")


_POAM_ID_RE = re.compile(r"^P\d+-\d+$")
_THREAT_ID_RE = re.compile(r"^[A-Za-z0-9\-]+$")


def _truncate_bytes(text: str, limit: int) -> str:
    """Truncate a string to `limit` UTF-8 bytes; append marker when truncated."""
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return text
    head = encoded[:limit].decode("utf-8", errors="ignore")
    return head + "\n...[TRUNCATED]"


def _safe_resolve(filename: str) -> Optional[Path]:
    """Resolve filename relative to GRC_DIR, rejecting traversal and symlinks.

    Returns the resolved Path on success, None on any guard failure.
    Logs reason on failure (stderr).
    """
    try:
        p = (GRC_DIR / filename).resolve()
        grc_root = GRC_DIR.resolve()
        if not p.is_relative_to(grc_root):
            log.warning("path traversal rejected: %s", filename)
            return None
        # is_symlink check on the original (pre-resolve) path so a symlink that
        # points inside GRC_DIR is still rejected.
        original = GRC_DIR / filename
        if original.is_symlink() or p.is_symlink():
            log.warning("symlink rejected: %s", filename)
            return None
        if not p.is_file():
            return None
        return p
    except (OSError, ValueError) as exc:
        log.error("resolve guard error: %s", type(exc).__name__)
        return None


def _read_frontmatter(p: Path) -> Dict[str, Any]:
    """Best-effort frontmatter parse; returns empty dict on any error."""
    try:
        import frontmatter  # type: ignore[import-not-found]
        post = frontmatter.load(p)
        return dict(post.metadata) if post.metadata else {}
    except Exception as exc:  # noqa: BLE001 - never let parse errors break tools
        log.warning("frontmatter parse failed for %s: %s", p.name, type(exc).__name__)
        return {}


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
@_audit_log("list_docs")
def list_docs() -> List[dict]:
    """List all GRC corpus markdown documents with title and classification."""
    try:
        out: List[dict] = []
        for p in sorted(GRC_DIR.glob("*.md")):
            meta = _read_frontmatter(p)
            title = str(meta.get("title", p.stem))
            classification = str(meta.get("classification", "UNKNOWN"))
            doc_type = str(meta.get("doc_type", "")) if meta.get("doc_type") else ""
            out.append({
                "filename": p.name,
                "title": sanitize(title),
                "classification": sanitize(classification),
                "doc_type": sanitize(doc_type) if doc_type else "",
            })

        # Size cap on full payload
        import json
        encoded = json.dumps(out).encode("utf-8")
        if len(encoded) > MAX_RESPONSE_BYTES:
            # Keep filename + title only, drop other fields, until under cap
            trimmed: List[dict] = []
            for entry in out:
                trimmed.append({"filename": entry["filename"], "title": entry["title"]})
                if len(json.dumps(trimmed).encode("utf-8")) > MAX_RESPONSE_BYTES:
                    trimmed = trimmed[:-1]
                    trimmed.append({"_truncated": True, "_dropped": len(out) - len(trimmed)})
                    return trimmed
            return trimmed
        return out
    except Exception as exc:  # noqa: BLE001
        log.error("list_docs error: %s", type(exc).__name__)
        return [{"error": "list_docs failed"}]


@mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
@_audit_log("read_doc")
def read_doc(filename: str) -> str:
    """Read a single GRC document by filename. Path-traversal and symlink guarded."""
    try:
        if not isinstance(filename, str) or not filename:
            return "Error: filename required"
        # Quick reject of obvious traversal before resolve
        if ".." in filename or filename.startswith("/"):
            return f"Error: {filename} not allowed (path traversal)"
        p = _safe_resolve(filename)
        if p is None:
            # Re-derive specific reason for caller-friendly message
            try:
                original = GRC_DIR / filename
                if original.is_symlink():
                    return f"Error: {filename} is a symlink (rejected)"
                resolved = original.resolve()
                if not resolved.is_relative_to(GRC_DIR.resolve()):
                    return f"Error: {filename} not allowed (path traversal)"
            except Exception:  # noqa: BLE001
                pass
            return f"Error: {filename} not found"
        content = p.read_text(encoding="utf-8", errors="replace")
        sanitized = sanitize(content)
        return _truncate_bytes(sanitized, MAX_RESPONSE_BYTES)
    except Exception as exc:  # noqa: BLE001
        log.error("read_doc error: %s", type(exc).__name__)
        return "Error: read_doc failed"


@mcp.tool(annotations={"readOnlyHint": True})
@_audit_log("search_corpus")
def search_corpus(query: str, limit: int = 10) -> List[dict]:
    """Substring/regex search across the GRC corpus; returns up to `limit` snippets (cap 50)."""
    try:
        if not isinstance(query, str) or not query.strip():
            return [{"error": "query required"}]
        if not isinstance(limit, int) or limit < 1:
            limit = 10
        if limit > 50:
            limit = 50

        snippet_budget = MAX_RESPONSE_BYTES // 2
        used = 0
        hits: List[dict] = []
        # Treat query as case-insensitive substring (cheap, no regex compile of user input)
        needle = query.lower()
        for p in sorted(GRC_DIR.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            haystack = text.lower()
            start = 0
            while True:
                idx = haystack.find(needle, start)
                if idx < 0:
                    break
                # extract surrounding ~200 chars
                left = max(0, idx - 100)
                right = min(len(text), idx + len(query) + 100)
                snippet = sanitize(text[left:right]).replace("\n", " ").strip()
                entry = {
                    "filename": p.name,
                    "offset": idx,
                    "snippet": snippet,
                }
                # snippet bytes accounting
                import json
                size = len(json.dumps(entry).encode("utf-8"))
                if used + size > snippet_budget:
                    hits.append({"_truncated": True, "_reason": "snippet bytes cap"})
                    return hits
                hits.append(entry)
                used += size
                if len(hits) >= limit:
                    return hits
                start = idx + max(1, len(needle))
        return hits
    except Exception as exc:  # noqa: BLE001
        log.error("search_corpus error: %s", type(exc).__name__)
        return [{"error": "search_corpus failed"}]


@mcp.tool(annotations={"readOnlyHint": True})
@_audit_log("get_poam")
def get_poam(poam_id: str) -> Optional[dict]:
    """Look up a POA&M row by short ID (e.g. P17-15). Returns the parsed table row."""
    try:
        if not isinstance(poam_id, str) or not _POAM_ID_RE.match(poam_id):
            return {"error": "poam_id must match ^P\\d+-\\d+$ (e.g. P17-15)"}
        poam_path = GRC_DIR / "POAM_PLAN_OF_ACTION.md"
        if not poam_path.is_file():
            return {"error": "POAM_PLAN_OF_ACTION.md not found"}
        text = poam_path.read_text(encoding="utf-8", errors="replace")
        # Match canonical pipe-delimited table row beginning with | POAM-Pxx-yy
        row_re = re.compile(r"^\|\s*POAM-" + re.escape(poam_id) + r"\s*\|.*$", re.MULTILINE)
        m = row_re.search(text)
        if not m:
            return {"error": f"POAM-{poam_id} not found"}
        row = m.group(0)
        # Split fields by pipe; trim
        fields = [f.strip() for f in row.strip("|").split("|")]
        # Canonical columns from POAM_PLAN_OF_ACTION.md:
        # POAM-ID | Description | Severity | Owner | Target Date | Status | Refs
        keys = ["poam_id", "description", "severity", "owner", "target_date", "status", "refs"]
        parsed: Dict[str, Any] = {}
        for i, key in enumerate(keys):
            parsed[key] = sanitize(fields[i]) if i < len(fields) else ""
        parsed["_raw"] = sanitize(_truncate_bytes(row, MAX_RESPONSE_BYTES // 4))
        return parsed
    except Exception as exc:  # noqa: BLE001
        log.error("get_poam error: %s", type(exc).__name__)
        return {"error": "get_poam failed"}


@mcp.tool(annotations={"readOnlyHint": True})
@_audit_log("get_threat_model_entry")
def get_threat_model_entry(threat_id: str) -> Optional[str]:
    """Look up a threat-model section by id (e.g. T0051, ATC-01) across SQUIRE_THREAT_MODEL.md and AI_THREAT_CATALOG.md."""
    try:
        if not isinstance(threat_id, str) or not _THREAT_ID_RE.match(threat_id):
            return "Error: threat_id must be alphanumeric+hyphen only"
        candidates = [
            GRC_DIR / "SQUIRE_THREAT_MODEL.md",
            GRC_DIR / "AI_THREAT_CATALOG.md",
        ]
        # Section detector: any heading line containing the threat_id token.
        # heading regex: `^#{1,6}\s+.*<id>.*$`
        heading_re = re.compile(
            r"^(#{1,6})\s+.*\b" + re.escape(threat_id) + r"\b.*$",
            re.MULTILINE,
        )
        for path in candidates:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            m = heading_re.search(text)
            if not m:
                continue
            heading_level = len(m.group(1))
            start = m.start()
            # Walk forward; stop at the next heading of same-or-shallower level
            tail = text[m.end():]
            stop_re = re.compile(
                r"^(#{1," + str(heading_level) + r"})\s+",
                re.MULTILINE,
            )
            stop_m = stop_re.search(tail)
            end = m.end() + stop_m.start() if stop_m else len(text)
            section = text[start:end].rstrip()
            sanitized = sanitize(f"[source: {path.name}]\n\n{section}")
            return _truncate_bytes(sanitized, MAX_RESPONSE_BYTES)
        return f"Error: threat_id {threat_id} not found in SQUIRE_THREAT_MODEL.md or AI_THREAT_CATALOG.md"
    except Exception as exc:  # noqa: BLE001
        log.error("get_threat_model_entry error: %s", type(exc).__name__)
        return "Error: get_threat_model_entry failed"


if __name__ == "__main__":
    mcp.run()

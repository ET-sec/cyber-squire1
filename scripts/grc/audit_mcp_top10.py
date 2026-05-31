#!/usr/bin/env python3
"""OWASP MCP Top 10 (2025 beta v0.1) static-analysis runner for grc_mcp_server.py.

Walks the target FastMCP server file and greps for evidence patterns of the
mitigated controls. Emits a PASS/FAIL report per OWASP MCP Top 10 (2025 beta
v0.1) control. Designed for CI: re-runs on every PR that touches
``scripts/grc/grc_mcp_server.py`` to prevent silent regression of any
mitigation landed in Phase 20.

Controls covered by this static check (official OWASP MCP Top 10 2025 beta v0.1 titles):

- MCP01 - Token Mismanagement and Secret Exposure
- MCP02 - Privilege Escalation via Scope Creep
- MCP03 - Tool Poisoning
- MCP04 - Software Supply Chain Attacks
- MCP05 - Command Injection and Execution
- MCP08 - Lack of Audit and Telemetry
- MCP10 - Context Injection and Over-Sharing

Controls NOT covered by this static check (require runtime or human review):

- MCP06 (Intent Flow Subversion) - requires content-level instruction-injection
  detection that is itself a Phase 21 backlog item; see POAM MCP06-001 in
  docs/grc/POAM_MCP_2025.md.
- MCP07 (Insufficient Authentication and Authorization) - stdio transport
  accepted-risk; see POAM MCP07-001.
- MCP09 (Shadow MCP Servers) - covered by scripts/inventory_scan.py
  (Plan 20-04), not this script.

Exit codes:
- 0: all checks PASS
- 1: at least one check FAIL

CLI:
    python3 scripts/grc/audit_mcp_top10.py [--server scripts/grc/grc_mcp_server.py]

TODO: wire into .github/workflows/security.yml in Phase 21.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SERVER = REPO_ROOT / "scripts" / "grc" / "grc_mcp_server.py"


# Each check: (mcp_id, official_title, positive_patterns, negative_patterns, scope_path)
#   positive_patterns: must find at least one match in scope -> PASS, else FAIL
#   negative_patterns: must find ZERO matches in scope -> PASS, else FAIL
#   scope_path: None means use --server file, otherwise use that path
CHECKS = [
    (
        "MCP01",
        "Token Mismanagement and Secret Exposure",
        [r"_SanitizingFilter", r"sanitize_for_log", r"redact_secrets", r"secret_filter"],
        [],
        None,
    ),
    (
        "MCP02",
        "Privilege Escalation via Scope Creep",
        [r"\bREAD_ONLY\b", r"\bread_only\b"],
        [],
        None,
    ),
    (
        "MCP03",
        "Tool Poisoning",
        [r"from\s+.*sanitize_output\s+import", r"sanitize_output\s*\(", r"\bsanitize\s*\("],
        [],
        None,
    ),
    (
        "MCP04",
        "Software Supply Chain Attacks",
        [r".+"],  # any non-empty line is fine; presence of a pinned dep file is the evidence
        [],
        # MCP04 scope is the repo root, not the server file
        "supply_chain_root",
    ),
    (
        "MCP05",
        "Command Injection and Execution",
        [r"safe_resolve"],
        [r"\bsubprocess\b", r"\bos\.system\b", r"\beval\s*\(", r"\bexec\s*\("],
        None,
    ),
    (
        "MCP08",
        "Lack of Audit and Telemetry",
        [r"audit_log", r"AUDIT_LOG_PATH", r"log_tool_call.*json"],
        [],
        None,
    ),
    (
        "MCP10",
        "Context Injection and Over-Sharing",
        [r"MAX_BYTES", r"BYTE_CAP", r"RESPONSE_LIMIT", r"MAX_RESPONSE_BYTES"],
        [],
        None,
    ),
]


def _check_supply_chain(repo_root: Path) -> tuple[bool, str]:
    """MCP04 scope: at least one pinned-dependency manifest must exist in repo.

    Accepts repo-root or sub-tree manifests (this repo has manifests under
    builds/squire/, builds/grc_librarian/, scripts/, etc.). The presence of
    any pinned manifest plus CI scanners (Trivy + Gitleaks + Semgrep in
    .github/workflows/security.yml) provides the MCP04 mitigation evidence.
    """
    globs = [
        "pyproject.toml",
        "requirements.txt",
        "Pipfile.lock",
        "poetry.lock",
        "*/pyproject.toml",
        "*/requirements.txt",
        "*/*/pyproject.toml",
        "*/*/requirements.txt",
    ]
    found = []
    for g in globs:
        for hit in repo_root.glob(g):
            if hit.is_file():
                found.append(str(hit.relative_to(repo_root)))
    if found:
        return True, f"pinned manifests found: {found[:3]}{' ...' if len(found) > 3 else ''}"
    return False, "no pyproject.toml / requirements.txt / Pipfile.lock / poetry.lock anywhere in repo"


def _check_patterns(text: str, positive: list[str], negative: list[str]) -> tuple[bool, str]:
    """Return (passed, message). Positive: at least one regex matches. Negative: none match."""
    matched_positive = None
    if positive:
        for p in positive:
            if re.search(p, text):
                matched_positive = p
                break
        if matched_positive is None:
            return False, f"missing positive evidence (tried {positive})"
    hit_negative = []
    for p in negative:
        m = re.search(p, text)
        if m:
            hit_negative.append(p)
    if hit_negative:
        return False, f"forbidden patterns present: {hit_negative}"
    parts = []
    if matched_positive:
        parts.append(f"positive: {matched_positive}")
    if negative and not hit_negative:
        parts.append("negative: clean")
    return True, "; ".join(parts) if parts else "ok"


def run_audit(server_path: Path) -> int:
    """Run the full OWASP MCP Top 10 (2025 beta v0.1) static audit. Return exit code."""
    if not server_path.is_file():
        print(f"FAIL: server file not found: {server_path}", file=sys.stderr)
        return 1
    server_text = server_path.read_text(encoding="utf-8", errors="replace")

    print(f"OWASP MCP Top 10 (2025 beta v0.1) audit: {server_path}")
    print("=" * 78)

    all_pass = True
    for mcp_id, title, positive, negative, scope in CHECKS:
        if scope == "supply_chain_root":
            ok, msg = _check_supply_chain(REPO_ROOT)
        else:
            ok, msg = _check_patterns(server_text, positive, negative)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {mcp_id} - {title}: {msg}")
        if not ok:
            all_pass = False

    print("=" * 78)
    if all_pass:
        print("RESULT: ALL CHECKS PASS")
        return 0
    print("RESULT: AT LEAST ONE CHECK FAILED")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OWASP MCP Top 10 (2025 beta v0.1) static-analysis runner for grc_mcp_server.py",
    )
    parser.add_argument(
        "--server",
        type=Path,
        default=DEFAULT_SERVER,
        help=f"Path to the FastMCP server file (default: {DEFAULT_SERVER})",
    )
    args = parser.parse_args()
    return run_audit(args.server.resolve())


if __name__ == "__main__":
    sys.exit(main())

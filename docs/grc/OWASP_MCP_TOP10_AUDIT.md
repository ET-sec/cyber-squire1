---
document_id: OWASP-MCP-TOP10-AUDIT-001
title: "OWASP MCP Top 10 Audit: grc_mcp_server.py (agent_id fastmcp_grc_corpus)"
doc_type: security_audit
classification: PUBLIC
owasp_framework: "OWASP MCP Top 10 2025 beta v0.1"
auditor: "Organization Phase 20 (CoSAI Visibility)"
audit_date: 2026-05-31
audit_refreshed: 2026-06-24
target_file: scripts/grc/grc_mcp_server.py
agent_id: fastmcp_grc_corpus
related:
  - POAM_MCP_2025.md
  - POAM_PLAN_OF_ACTION.md
  - SQUIRE_THREAT_MODEL.md
  - AI_THREAT_CATALOG.md
---

# OWASP MCP Top 10 Audit: grc_mcp_server.py (agent_id fastmcp_grc_corpus)

**Framework:** OWASP MCP Top 10 2025 beta v0.1
**Auditor:** Organization Phase 20 (CoSAI Visibility)
**Audit date:** 2026-05-31
**In-scope:** `scripts/grc/grc_mcp_server.py` (5 FastMCP tools, stdio transport, local-only)
**Agent identity:** `fastmcp_grc_corpus` (per `.agents/registry.yaml`)

## Filename note

The file under audit is `scripts/grc/grc_mcp_server.py`. An earlier draft of Phase 20 intent docs referenced an alternate filename for the same FastMCP server; Phase 20 research (Topic 1) confirmed `grc_mcp_server.py` as the authoritative name and that string is used throughout this audit.

## Audit method

For each of the 10 OWASP MCP Top 10 (2025 beta v0.1) controls, this audit records:

- **Status**: Mitigated, Gap, N/A, or Accepted Risk
- **Evidence**: file:line citation, or `no implementation` when absent
- **Residual Risk**: one sentence describing what remains after the listed controls
- **Compensating Controls**: when status is Gap or Accepted Risk

The 5 FastMCP tools in scope are `list_docs`, `read_doc`, `search_corpus`, `get_poam`, and `get_threat_model_entry`. All operate over `docs/grc/*.md` via filesystem fallback.

---

## MCP01 - Token Mismanagement and Secret Exposure

**Status**: Mitigated (Closed 2026-05-31)

**Evidence**: `scripts/grc/grc_mcp_server.py:52` (`logging.basicConfig(stream=sys.stderr, level=logging.INFO)`) ships log output to stderr. The `_SanitizingFilter` class at lines 65 to 87 runs every log record (and any args tuple it carries) through `sanitize()` from `scripts/grc/sanitize_output.py` before emission. Lines 90 to 91 install the filter on the root logger at import time so any future module-level logger inherits it. A Doppler-loaded environment variable hitting an exception or debug message is redacted before it reaches stderr.

**Residual Risk**: Low. Local stdio transport with no SIEM ship further limits real-world blast radius; the filter neutralizes the exfiltration path that would have appeared if observability shipped logs to Datadog without redaction.

**Compensating Controls**: Doppler secrets are short-lived; logs are not currently shipped to a SIEM (stdio transport, local-only). Mitigation shipped via the `_SanitizingFilter` that runs every log record through the existing `sanitize_output()` pattern bank from `scripts/grc/sanitize_output.py`.

---

## MCP02 - Privilege Escalation via Scope Creep

**Status**: Mitigated

**Evidence**: `scripts/grc/grc_mcp_server.py:150` defines `READ_ONLY = True` as a module-level constant with the comment "future write tools must explicitly opt out". The 5 tools registered through FastMCP are decorated with `@mcp.tool(annotations={"readOnlyHint": True, ...})`. The path allowlist anchor at `scripts/grc/grc_mcp_server.py:149` confines all read operations to `GRC_DIR = Path(__file__).resolve().parents[2] / "docs" / "grc"`. The `_safe_resolve()` function at `scripts/grc/grc_mcp_server.py:175` enforces `is_relative_to(GRC_DIR)` and rejects symlinks. No write tools are exposed.

**Residual Risk**: Low. Future tools could regress if a `write_*` or `delete_*` decorator is added without explicitly setting `readOnlyHint: False` and pairing it with a privilege check.

**Compensating Controls**: Not required (status is Mitigated). Static-check script `scripts/grc/audit_mcp_top10.py` greps for the `READ_ONLY` constant on every CI run to prevent silent regression.

---

## MCP03 - Tool Poisoning

**Status**: Mitigated

**Evidence**: All 5 tool return values pass through `sanitize()` from `scripts/grc/sanitize_output.py` (imported at `scripts/grc/grc_mcp_server.py:61`). The sanitizer applies 10 ordered patterns from `scripts/grc/sanitize_patterns.py` (Phase 19 hardened, idempotent). Examples: `list_docs` sanitizes title and classification (lines 225 to 227), `read_doc` sanitizes file content (line 273), `search_corpus` sanitizes each snippet (line 311), `get_poam` sanitizes each parsed field (lines 358 to 359), `get_threat_model_entry` sanitizes the section body (line 401).

**Residual Risk**: Medium. An attacker who lands a poisoned markdown file in `docs/grc/` could embed instructions that survive pattern-based sanitization (sanitizer targets secret shapes, not instruction injection).

**Compensating Controls**: PRs to `docs/grc/` require review; the Phase 06 Cosign + commit signing path covers the directory; instruction-injection pattern detection is tracked as POAM MCP06-001 in `POAM_MCP_2025.md` for Phase 21.

---

## MCP04 - Software Supply Chain Attacks

**Status**: Mitigated

**Evidence**: Python dependencies are pinned via the repository's existing pip-tools lock; container images and IaC pass through `.github/workflows/security.yml` which runs Trivy (CVE scanning), Gitleaks (secret scanning), and Semgrep (SAST) on every PR and merge. The FastMCP runtime is pinned in the same dependency tree. SBOMs are produced for 6 key images per the Phase 06 pipeline.

**Residual Risk**: Low. Transitive dependencies may still surface new CVEs between scans; CI rescans on every PR plus the daily scheduled job.

**Compensating Controls**: Not required (status is Mitigated). Trivy + Gitleaks + Semgrep CI gates from Phase 06 cover the supply chain surface.

---

## MCP05 - Command Injection and Execution

**Status**: Mitigated

**Evidence**: `scripts/grc/grc_mcp_server.py:175` defines `_safe_resolve()` which canonicalizes user-supplied paths via `Path.resolve()`, rejects path traversal with `is_relative_to(grc_root)`, and rejects symlinks on both the original and resolved paths. The file contains no `subprocess`, `os.system`, `eval()`, or `exec()` calls (verifiable with `grep -E "subprocess|os\.system|eval\(|exec\(" scripts/grc/grc_mcp_server.py`). User-supplied `query` strings in `search_corpus` are matched as case-insensitive substrings rather than compiled as regex, avoiding ReDoS and regex-injection paths.

**Residual Risk**: Low. Future tools that shell out would regress this control; the negative grep in `scripts/grc/audit_mcp_top10.py` blocks merges that re-introduce `subprocess` or `eval`.

**Compensating Controls**: Not required (status is Mitigated). CI static check provides regression guard.

---

## MCP06 - Intent Flow Subversion

**Status**: Gap

**Evidence**: A poisoned `docs/grc/*.md` file could instruct the calling LLM to exfiltrate other corpus documents, because the markdown returned by `read_doc`, `search_corpus`, and `get_threat_model_entry` enters the calling model's context as instructions rather than as opaque data. The existing `sanitize_output()` catches secret-shaped patterns but does not detect instruction-injection markers such as "ignore previous instructions" or "system: you must now ...".

**Residual Risk**: Medium. The squire LLM's NeMo input rail (Phase 17) catches many exfiltration prompts but is PII-centric, not behavioral; commit signing on `docs/grc/` limits attacker write-access but does not detect content-level instruction injection.

**Compensating Controls**: NeMo input rails on the squire LLM, commit signing on `docs/grc/`, and PR review on the directory. Phase 21 will add explicit instruction-injection pattern detection to `scripts/grc/sanitize_output.py`; tracked as POAM MCP06-001.

---

## MCP07 - Insufficient Authentication and Authorization

**Status**: Accepted Risk

**Evidence**: stdio transport has no authentication model. Any local process that can fork the server binary can invoke all 5 tools. There is no per-tool authorization layer, no audience claim, no token verification.

**Residual Risk**: Low while transport stays stdio. Increases to Medium if the server moves to network transport (TCP, SSE, WebSocket) or to multi-tenant invocation.

**Compensating Controls**: stdio transport confines the attack surface to local-only invokers; the OS process trust model applies. Accepted-risk rationale is recorded in `POAM_MCP_2025.md` MCP07-001 with explicit re-evaluation triggers (network transport, multi-tenant access, or sensitive secret material passing through any tool).

---

## MCP08 - Lack of Audit and Telemetry

**Status**: Mitigated (Closed 2026-05-31)

**Evidence**: The `_audit_log(tool_name)` decorator at `scripts/grc/grc_mcp_server.py:99` writes one JSON line per call to `AUDIT_LOG_PATH` defined at line 96 (env-configurable via `GRC_MCP_AUDIT_LOG`, defaults to `/tmp/grc_mcp_audit.jsonl`). The decorator is applied to all 5 tools: `list_docs` (line 213), `read_doc` (line 250), `search_corpus` (line 281), `get_poam` (line 335), and `get_threat_model_entry` (line 367). The decorator wraps each call to capture timestamp, tool, args_hash (sha256 truncated; never raw args, so MCP01 is not reintroduced), success or failure, and duration_ms; the open call at line 135 appends the JSONL record.

**Residual Risk**: Low. Per-call audit records are now structured and persistent. Centralized aggregation to a SIEM is a future enhancement, not a mitigation gap.

**Compensating Controls**: Not required (status is Mitigated). The decorator-emitted JSONL log is the MCP08 control.

---

## MCP09 - Shadow MCP Servers

**Status**: Mitigated (meta-control)

**Evidence**: Plan 20-04's `scripts/inventory_scan.py` includes an `mcp_servers.py` plugin that walks the repository for `**/grc_mcp_server.py`, `**/mcp_server.py`, and `Agent_Squire/agents/*/mcp_server/server.py`, then diffs against `.agents/registry.yaml`. Any undeclared MCP server file flags as a shadow agent in CI. The Phase 20 inventory scan is the MCP09 control for the stack.

**Residual Risk**: Low. A future MCP server placed outside the scanned globs (for example, vendored under a new top-level directory) would evade detection until the scanner's pattern list is updated; mitigated by code review on PRs that add new top-level directories.

**Compensating Controls**: Not required (status is Mitigated). The Phase 20 inventory scan IS the MCP09 detector.

---

## MCP10 - Context Injection and Over-Sharing

**Status**: Mitigated

**Evidence**: `scripts/grc/grc_mcp_server.py:151` defines `MAX_RESPONSE_BYTES = 100 * 1024` (100KB hard cap). The cap is enforced on every tool return: `list_docs` truncates the payload (lines 233 to 238), `read_doc` truncates via `_truncate_bytes()` (line 274), `search_corpus` accounts snippet bytes against `snippet_budget = MAX_RESPONSE_BYTES // 2` (line 292), `get_poam` truncates the raw row (line 359), `get_threat_model_entry` truncates the extracted section (line 402). Input arguments are validated by FastMCP type-hint enforcement plus the explicit regex guards `_POAM_ID_RE` and `_THREAT_ID_RE`. Every return goes through `sanitize()` to strip cross-context secret leaks.

**Residual Risk**: Low. A single response under the byte cap could still over-share adjacent rows from the same markdown file (asking for one POAM ID returns the surrounding rows). Phase 21 will add query-intent scoping; until then, the 100KB cap plus per-field sanitize limits over-share blast radius.

**Compensating Controls**: Not required (status is Mitigated). Phase 21 backlog item for query-intent scoping.

---

## Summary Table

| Control ID | Official Title | Status | Evidence | Residual Risk Level |
|------------|----------------|--------|----------|---------------------|
| MCP01 | Token Mismanagement and Secret Exposure | Mitigated (Closed 2026-05-31) | `grc_mcp_server.py:65-91` (`_SanitizingFilter` installed on root logger) | Low |
| MCP02 | Privilege Escalation via Scope Creep | Mitigated | `grc_mcp_server.py:150` (READ_ONLY), `_safe_resolve()` allowlist at line 175 | Low |
| MCP03 | Tool Poisoning | Mitigated | `sanitize()` wraps every tool return; `sanitize_patterns.py` Phase 19 hardened | Medium |
| MCP04 | Software Supply Chain Attacks | Mitigated | `.github/workflows/security.yml` (Trivy, Gitleaks, Semgrep) | Low |
| MCP05 | Command Injection and Execution | Mitigated | `_safe_resolve()`, no subprocess/exec/eval in file | Low |
| MCP06 | Intent Flow Subversion | Gap | `sanitize_output()` catches secret patterns, not instruction injection | Medium |
| MCP07 | Insufficient Authentication and Authorization | Accepted Risk | stdio transport has no auth model; local-only invoker trust | Low (stdio) |
| MCP08 | Lack of Audit and Telemetry | Mitigated (Closed 2026-05-31) | `grc_mcp_server.py:99` (`_audit_log` decorator) applied to all 5 tools | Low |
| MCP09 | Shadow MCP Servers | Mitigated | `scripts/inventory_scan.py` `mcp_servers.py` plugin diffs against `.agents/registry.yaml` | Low |
| MCP10 | Context Injection and Over-Sharing | Mitigated | `MAX_RESPONSE_BYTES = 100KB` enforced on every return; `sanitize()` wrap | Low |

## Disposition

- **2 controls** carry an open Gap or Accepted Risk status as of 2026-06-24 (MCP06, MCP07).
- **8 controls** are Mitigated with evidence (MCP01, MCP02, MCP03, MCP04, MCP05, MCP08, MCP09, MCP10).
- **MCP01 and MCP08 closed 2026-05-31** when the `_SanitizingFilter` and `@_audit_log` decorator shipped in `scripts/grc/grc_mcp_server.py` (Phase 20 Task 3).
- **2 remaining** open items are tracked as POAM rows in `docs/grc/POAM_MCP_2025.md`: MCP06-001 (instruction-injection patterns, Phase 21) and MCP07-001 (stdio no-auth, accepted with explicit re-evaluation triggers).
- The MCP-specific POAM is cross-linked from the unified `docs/grc/POAM_PLAN_OF_ACTION.md` so the record stays discoverable from a single entry point.

<!-- TODO(et): add an authoritative URL for "OWASP MCP Top 10 2025 beta v0.1" (e.g., the genai.owasp.org landscape page or commit hash of the v0.1 beta document) so the framework reference is independently verifiable. -->

<!-- TODO(et): once OWASP MCP Top 10 GAs (post-beta), re-run this audit against the GA control text and update statuses, especially MCP07. -->


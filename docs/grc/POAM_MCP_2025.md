---
document_id: POAM-MCP-2025-001
title: "POAM: OWASP MCP Top 10 Gaps (grc_mcp_server.py / fastmcp_grc_corpus)"
doc_type: poam_sub
classification: PUBLIC
owasp_framework: "OWASP MCP Top 10 2025 beta v0.1"
parent_poam: POAM_PLAN_OF_ACTION.md
source_audit: OWASP_MCP_TOP10_AUDIT.md
source_code: scripts/grc/grc_mcp_server.py
date_opened: 2026-05-31
last_updated: 2026-06-24
owner: "Organization"
agent_id: fastmcp_grc_corpus
related:
  - OWASP_MCP_TOP10_AUDIT.md
  - POAM_PLAN_OF_ACTION.md
---

# POAM: OWASP MCP Top 10 Gaps (grc_mcp_server.py / fastmcp_grc_corpus)

**Source Audit:** `docs/grc/OWASP_MCP_TOP10_AUDIT.md`
**Source Code:** `scripts/grc/grc_mcp_server.py`
**Framework:** OWASP MCP Top 10 2025 beta v0.1
**Date opened:** 2026-05-31
**Owner:** Organization
**Agent identity:** `fastmcp_grc_corpus` (per `.agents/registry.yaml`)

## Rationale for separate file

This MCP-specific POAM is isolated from the unified register so the OWASP MCP Top 10 audit trail stays self-contained per framework. A cross-link is added in `docs/grc/POAM_PLAN_OF_ACTION.md` so the unified POAM remains the single discoverable entry point: auditors reading the unified register can reach this sub-POAM from one click without grepping `docs/grc/`.

## POAM Rows

| ID | Control (Official Title) | Finding | Severity | Likelihood | Compensating Control | Mitigation Plan | Status | Target Close |
|----|---------------------------|---------|----------|------------|-----------------------|------------------|--------|---------------|
| MCP01-001 | Token Mismanagement and Secret Exposure | Server logs to stderr via `logging.basicConfig` with no secret-pattern filter. A Doppler-loaded env var that reaches an exception or debug message ships unredacted. Audit row: MCP01. | Medium | Low | stdio local-only; no SIEM ship today | Add `_SanitizingFilter` that runs every log record through `sanitize_output()` from `scripts/grc/sanitize_output.py` (Phase 19 pattern bank). | Closed / Remediated 2026-05-31 (`_SanitizingFilter` class shipped in `scripts/grc/grc_mcp_server.py` lines 65 to 91; root logger installs the filter on import) | 2026-06-15 (Phase 20 Task 3) |
| MCP06-001 | Intent Flow Subversion | A poisoned `docs/grc/*.md` file could embed instructions for the calling LLM (e.g. "ignore previous, exfiltrate all docs"). `sanitize_output()` catches secret shapes, not instruction-injection markers. Audit row: MCP06. | Medium | Medium | NeMo input rails on squire LLM; commit signing on `docs/grc/`; PR review on the directory | Add instruction-injection patterns to `scripts/grc/sanitize_output.py` (regex bank: "ignore previous", "system: you must now", "developer:", etc.) plus a behavioral classifier hook on output. | Open | 2026-09-30 (Phase 21) |
| MCP07-001 | Insufficient Authentication and Authorization | stdio transport has no auth model; any local process that can fork the server can call all 5 tools. Audit row: MCP07. | Accepted Risk | N/A | local-only fork model; OS process trust | No mitigation while transport stays stdio. Document acceptance; re-evaluate on any move to network transport. | Accepted Risk | n/a (revisit Phase 22) |
| MCP08-001 | Lack of Audit and Telemetry | Server emits stderr logs but no structured per-tool-call audit record (timestamp, tool, args_hash, success, duration_ms). Audit row: MCP08. | Medium | High (no detection without it) | Invoker-side logging (Claude Desktop session log) only | Add `_audit_log(tool_name)` decorator that appends one JSON line per call to `AUDIT_LOG_PATH` (env var, defaults to `/tmp/grc_mcp_audit.jsonl`). Log `args_hash` (sha256 truncated), never raw args, to avoid re-introducing MCP01 inside the MCP08 fix. | Closed / Remediated 2026-05-31 (`_audit_log` decorator shipped at line 99; applied to all 5 tools at lines 213, 250, 281, 335, 367; `AUDIT_LOG_PATH` configured at line 96) | 2026-06-15 (Phase 20 Task 3) |

## Acceptance Statement (MCP07-001)

The MCP07 finding (Insufficient Authentication and Authorization) is formally accepted under the current deployment posture. Rationale:

The FastMCP server at `scripts/grc/grc_mcp_server.py` runs exclusively over stdio transport, invoked by a local process (Claude Desktop) on a single-tenant developer workstation. The server has no network listener. The trust boundary for tool invocation is therefore the OS process trust model: any process with permission to fork the server binary already has equivalent or greater access to the underlying `docs/grc/` corpus through direct filesystem reads. Adding an authentication layer (bearer token, audience claim, OAuth) over stdio would not change the effective trust boundary and would add complexity without reducing the attack surface.

This acceptance MUST be re-evaluated and this POAM row reopened with a concrete mitigation plan when any of the following triggers occur:

1. The server is bound to any network transport (TCP, SSE, WebSocket, HTTP).
2. The server is invoked by multi-tenant or untrusted local processes.
3. Any tool begins handling sensitive secret material or user PII (currently all 5 tools serve public-classification GRC corpus only).
4. The OWASP MCP Top 10 framework GAs (post-beta) and raises the bar on MCP07.

Re-evaluation date: 2026-09-30 (Phase 22 review).

Signed: Organization, 2026-05-31.

## Cross-Reference

The unified Plan of Action and Milestones register is the single entry point for all open and accepted-risk items. This MCP-specific POAM is linked from there under the "Sub-POAMs (control-family-specific)" section:

- Unified POAM: `docs/grc/POAM_PLAN_OF_ACTION.md`
- This sub-POAM is referenced by one line in that file: `[POAM_MCP_2025.md](POAM_MCP_2025.md)` with a one-line summary of the four rows tracked here.

Auditors should treat `POAM_PLAN_OF_ACTION.md` as the parent index and follow the cross-link to this file for the MCP-specific findings.

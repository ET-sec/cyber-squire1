"""Structured response + block-reason JSON builder (criterion #25).

When a downstream rail (NeMo Guardrails in 17-10, actions_allowlist here) blocks
an input or output, /alert must return a machine-readable payload with:
  - reason_code
  - rail_name
  - rule_name
  - redacted_input_snippet (PII scrubbed)

The redactor is intentionally conservative: cheap regexes for SSN, Anthropic
API-key style (`sk-...`), and 13-16 digit credit-card-shaped numbers. Full PII
scrubbing is NeMo's job; this is a last-mile safety net so the response itself
never re-leaks the sensitive input back to the caller.
"""
from __future__ import annotations

import re
from typing import Any

# Patterns are order-sensitive; API-key style first so it doesn't get swallowed
# by the CC regex on long tokens.
SENSITIVE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"), "API_KEY"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
    (re.compile(r"\b(?:\d[ \-]?){13,16}\b"), "CC"),
]


def redact_snippet(text: str, max_chars: int = 200) -> str:
    """Return a redacted, length-capped copy of text."""
    if not text:
        return ""
    s = str(text)[:max_chars]
    for pat, label in SENSITIVE_PATTERNS:
        s = pat.sub(f"[REDACTED_{label}]", s)
    return s


def build_block_response(
    *,
    reason_code: str,
    rail_name: str,
    rule_name: str,
    input_snippet: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Structured JSON body for a blocked request (criterion #25)."""
    body: dict[str, Any] = {
        "blocked": True,
        "reason_code": reason_code,
        "rail_name": rail_name,
        "rule_name": rule_name,
        "redacted_input_snippet": redact_snippet(input_snippet),
    }
    if extra:
        body.update(extra)
    return body

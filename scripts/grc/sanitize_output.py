"""Pure-function sanitizer for any LLM-generated text leaving the reviewer.

Defense in depth. The reviewer's structured-output schema is supposed to
keep raw diff content out of comments, but this final pass ensures even
a model regression cannot leak internal IPs, container names, paths, or
secrets into a public PR comment.

Idempotent: `sanitize(sanitize(s)) == sanitize(s)`.
Pure: no I/O, no env reads, no logging.
"""

from __future__ import annotations

from scripts.grc.sanitize_patterns import PATTERNS


def sanitize(text: str) -> str:
    """Apply every pattern in PATTERNS to `text` in order.

    Returns the redacted string. Safe on empty / None-ish inputs.
    """
    if not text:
        return text
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


__all__ = ["sanitize"]

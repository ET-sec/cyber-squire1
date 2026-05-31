"""Pre-graph PII scanner (17-10 red-team remediation).

Runs on raw /alert payload before the graph invokes. Addresses the rail-gap
surfaced by red-team cases 03 and 04: NeMo's input rail only fronts the draft
and critique nodes, so PII in the raw alert payload that is summarised away by
classify/retrieve/enrich never reaches a rail.

Catches the same four strict regex PII classes the NeMo output rail catches
(SSN, credit card with Luhn, email, US phone). Regex-only, no LLM, no spaCy --
runs in sub-millisecond per alert.

When a hit fires, app.py returns a structured block response with
reason_code=PII_DETECTED_PRE_GRAPH and rail_name=pre_graph so dashboards and
red-team docs can distinguish pre-graph from NeMo-rail blocks.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

# Valid SSNs exclude ranges that SSA never issued: 000, 666, 900-999 area; 00
# group; 0000 serial. The regex below matches the shape; _valid_ssn() rules out
# the reserved ranges. We deliberately allow 078-05-1120 and 123-45-6789 style
# "test" numbers through because those ARE valid-looking PII if a real attacker
# sent them.
_SSN_RE = re.compile(r"\b(\d{3})-(\d{2})-(\d{4})\b")

# 13-19 digit sequences with optional separators; Luhn check run separately.
_CC_RE = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")

# Simplified email; matches anything that looks like local@domain.tld.
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")

# US phone shapes: (xxx) xxx-xxxx, xxx-xxx-xxxx, xxx.xxx.xxxx, +1 xxx ...
_PHONE_RE = re.compile(
    r"(?:\+1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}\b"
)


@dataclass
class PiiHit:
    entity: str
    match: str
    start: int
    end: int


def _valid_ssn(area: str, group: str, serial: str) -> bool:
    if area in {"000", "666"} or area.startswith("9"):
        return False
    if group == "00":
        return False
    if serial == "0000":
        return False
    return True


def _luhn_ok(digits: str) -> bool:
    digits = re.sub(r"[ -]", "", digits)
    if not (13 <= len(digits) <= 19) or not digits.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def scan(payload: dict | str) -> PiiHit | None:
    """Return the first PII hit in the flattened payload text, or None.

    The graph node ordering makes this a defense-in-depth layer, not the only
    line. False negatives (regex misses) fall through to NeMo rails on draft.
    """
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)

    for m in _SSN_RE.finditer(text):
        if _valid_ssn(m.group(1), m.group(2), m.group(3)):
            return PiiHit("US_SSN", m.group(0), m.start(), m.end())

    for m in _CC_RE.finditer(text):
        if _luhn_ok(m.group(0)):
            return PiiHit("CREDIT_CARD", m.group(0), m.start(), m.end())

    m = _EMAIL_RE.search(text)
    if m:
        return PiiHit("EMAIL_ADDRESS", m.group(0), m.start(), m.end())

    m = _PHONE_RE.search(text)
    if m:
        return PiiHit("PHONE_NUMBER", m.group(0), m.start(), m.end())

    return None


def build_snippet(payload: dict | str, hit: PiiHit, window: int = 30) -> str:
    """Redacted snippet of the surrounding context, masking the match itself."""
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    s = max(0, hit.start - window)
    e = min(len(text), hit.end + window)
    before = text[s:hit.start]
    after = text[hit.end:e]
    masked = "*" * len(hit.match)
    return f"{before}{masked}{after}"

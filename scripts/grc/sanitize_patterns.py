r"""Sanitization patterns applied in order to any LLM-generated text before
posting to a public PR comment / issue / log.

Order matters: more specific patterns must run before more general ones.
Host-specific public IPs (supplied via the GRC_REDACT_IPS environment
variable, comma-separated) get the more informative `[REDACTED-IP]` token
before the generic RFC1918 pattern runs. The literals live in the runtime
environment (Doppler / CI secrets), never in this public file.

Each entry is `(compiled_regex, replacement_string)`. Replacements are
literal strings (no backrefs).

Critical false-positive guards (covered by tests):
  * `P\d+-\d+` POA&M IDs (e.g. P17-15) are NOT secrets and pass unchanged.
  * `[A-Z]{2}-\d+` NIST 800-53 control IDs (AC-2, SI-7, RA-5) are NOT
    secrets and pass unchanged.

If you add a pattern that would match those, you will break the GRC
reviewer's ability to talk about findings. Add a passthrough test.
"""

from __future__ import annotations

import os
import re
from typing import List, Tuple

# Host-specific public IPs to redact, injected at runtime so the concrete
# values never appear in this tracked file. Set in Doppler / CI, e.g.
#   GRC_REDACT_IPS="198.51.100.7" (comma-separated for multiple).
_REDACT_IPS: List[str] = [
    ip.strip()
    for ip in os.environ.get("GRC_REDACT_IPS", "").split(",")
    if ip.strip()
]

# Order is intentional. Specific tokens first, generic later.
PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    # 1. Host-specific public IPs (most specific, env-supplied)
    *[(re.compile(re.escape(ip)), "[REDACTED-IP]") for ip in _REDACT_IPS],
    # 2. RFC1918 private IPs
    (
        re.compile(
            r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})\b"
        ),
        "[INTERNAL-IP]",
    ),
    # 3. Internal service container names
    (re.compile(r"cd-service-[a-z0-9-]+"), "[INTERNAL-SVC]"),
    # 4. Internal domain
    (re.compile(r"tigouetheory\.com"), "[INTERNAL-DOMAIN]"),
    # 5. Filesystem paths under /root
    (re.compile(r"/root/[A-Za-z0-9_/\-\.]*"), "[INTERNAL-PATH]"),
    # 6. Doppler service tokens (dp.st.<env>.<rand> or dp.pt.<env>.<rand>)
    (
        re.compile(r"dp\.(?:st|pt)\.[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)?"),
        "[REDACTED-DOPPLER-TOKEN]",
    ),
    # 7. Anthropic API keys
    (re.compile(r"sk-ant-[A-Za-z0-9_-]+"), "[REDACTED-ANTHROPIC-KEY]"),
    # 8. GitHub PAT/server tokens (ghp_, ghs_)
    (re.compile(r"gh[ps]_[A-Za-z0-9]{20,}"), "[REDACTED-GH-TOKEN]"),
    # 9. AWS access key IDs
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED-AWS-KEY]"),
    # 10. Generic Bearer tokens in headers
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}"), "Bearer [REDACTED]"),
]

"""Daily Anthropic spend kill switch for the GRC reviewer.

Run as the first step of any workflow that calls the Anthropic API. Exits 1
with a `BUDGET BLOCK` stderr message when today's spend has reached the
configured daily limit, otherwise exits 0 with a one-line `Budget OK` to
stdout.

Spend is read from two sources, in order:
  1. Anthropic admin usage API (https://api.anthropic.com/v1/organizations/usage_report)
  2. Local SQLite ledger fallback (~/.cache/grc/spend_ledger.sqlite)

The fallback is the system of record when running locally or when the
admin API rejects the regular API key (404 / 401). NEVER echo
ANTHROPIC_API_KEY anywhere; only place it in the Authorization header.
"""

from __future__ import annotations

import logging
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

from scripts.grc.spend_ledger import today_total_usd

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("budget_guard")

ANTHROPIC_USAGE_URL = "https://api.anthropic.com/v1/organizations/usage_report"
TIMEOUT_SECONDS = 5


def _daily_limit_usd() -> float:
    raw = os.environ.get("DAILY_LIMIT_USD", "1.00")
    try:
        limit = float(raw)
    except (TypeError, ValueError):
        log.warning("Invalid DAILY_LIMIT_USD=%r; defaulting to 1.00", raw)
        limit = 1.00
    if os.environ.get("EVAL_MODE") == "1":
        # Eval mode raises the cap to 5.00 unless caller already set higher.
        limit = max(limit, 5.00)
    return limit


def _admin_api_spend_today() -> float | None:
    """Return today's spend in USD via the admin API, or None on failure.

    None means "fall back to local ledger". We do not raise; admin API
    access is best-effort. Network errors and 4xx are expected on
    non-admin keys.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.warning("ANTHROPIC_API_KEY not set; skipping admin API check")
        return None
    today_iso = datetime.now(timezone.utc).date().isoformat()
    url = f"{ANTHROPIC_USAGE_URL}?starting_at={today_iso}"
    # Refuse anything that isn't HTTPS to close urllib's file:// scheme path.
    # ANTHROPIC_USAGE_URL is a hardcoded constant; this guard exists to satisfy
    # SAST scanners and to harden against future code paths that derive the URL
    # from configuration.
    if not url.startswith("https://"):
        log.warning("Refusing non-HTTPS admin API URL: %s", url)
        return None
    req = urllib.request.Request(  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        url,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        # URL is the constant ANTHROPIC_USAGE_URL plus a date query string;
        # scheme is verified above. SAST rule suppressed with documented
        # rationale (no user-controlled input, hardcoded base URL).
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
            if resp.status != 200:
                log.info("Admin API returned %s; falling back to ledger", resp.status)
                return None
            import json
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log.info("Admin API HTTPError %s; falling back to ledger", e.code)
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        log.info("Admin API unreachable (%s); falling back to ledger", e.__class__.__name__)
        return None
    except Exception as e:  # pragma: no cover - defensive
        log.info("Admin API parse failure (%s); falling back to ledger", e.__class__.__name__)
        return None

    data = payload.get("data") or []
    total = 0.0
    for row in data:
        amount = row.get("amount_usd")
        if amount is None:
            continue
        try:
            total += float(amount)
        except (TypeError, ValueError):
            continue
    return total


def current_spend_usd() -> float:
    """Return today's spend, preferring admin API, falling back to ledger."""
    api_total = _admin_api_spend_today()
    if api_total is not None:
        return api_total
    return today_total_usd()


def main() -> int:
    limit = _daily_limit_usd()
    spend = current_spend_usd()
    if spend >= limit:
        # Format with 2 decimals for the BUDGET BLOCK line; both sides match.
        msg = f"BUDGET BLOCK: ${spend:.2f} >= ${limit:.2f}"
        print(msg, file=sys.stderr)
        return 1
    print(f"Budget OK: ${spend:.2f} / ${limit:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

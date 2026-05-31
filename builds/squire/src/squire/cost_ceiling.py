"""Daily rolling Anthropic spend tracker + breach-mode dispatcher (criterion #15).

Queries ir_investigations for the running UTC-day sum of cost_usd. When the
accumulated spend reaches ANTHROPIC_DAILY_CEILING_USD, the FastAPI layer gets
back a BreachAction that tells it to either:

  - refuse the request with 503 + structured body (mode=refuse)
  - force SQUIRE_LLM_BACKEND=ollama for this invocation (mode=ollama)
  - log and continue (mode=warn_only)

Fail-open: any DB error is treated as "no breach" so an ops problem doesn't
wedge the incident-response path.
"""
from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass

import psycopg

from .settings import settings

log = logging.getLogger("squire.cost_ceiling")


def _conninfo() -> str:
    return (
        f"host={settings.cd_db_host} port={settings.cd_db_port} "
        f"user={settings.cd_db_user} password={settings.cd_db_pass.get_secret_value()} "
        f"dbname={settings.cd_db_name}"
    )


def today_spend_usd() -> float:
    """Sum of cost_usd for ir_investigations completed today (UTC).

    Returns 0.0 on any connection error (fail-open).
    """
    today = dt.datetime.now(dt.timezone.utc).date()
    try:
        with psycopg.connect(_conninfo(), connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(cost_usd), 0) FROM ir_investigations "
                    "WHERE (created_at AT TIME ZONE 'UTC')::date = %s",
                    (today,),
                )
                row = cur.fetchone()
                return float(row[0] or 0.0)
    except Exception as e:
        log.warning("today_spend_usd failed, falling open: %s", e)
        return 0.0


@dataclass
class BreachAction:
    """Decision record produced by consult()."""

    breach: bool
    mode: str  # refuse | ollama | warn_only
    spent: float
    ceiling: float
    backend_override: str | None  # "ollama" when mode=ollama and breach=True
    reason: str = ""


def consult() -> BreachAction:
    """Inspect today's spend vs the configured ceiling and decide what to do."""
    ceiling = float(settings.anthropic_daily_ceiling_usd)
    mode = (settings.cost_breach_mode or "warn_only").lower()
    spent = today_spend_usd()

    if spent < ceiling:
        return BreachAction(
            breach=False, mode=mode, spent=spent, ceiling=ceiling, backend_override=None
        )

    if mode == "refuse":
        return BreachAction(
            breach=True,
            mode=mode,
            spent=spent,
            ceiling=ceiling,
            backend_override=None,
            reason=(
                f"daily_cost_ceiling_reached spent=${spent:.4f} ceiling=${ceiling:.2f}"
            ),
        )
    if mode == "ollama":
        return BreachAction(
            breach=True,
            mode=mode,
            spent=spent,
            ceiling=ceiling,
            backend_override="ollama",
            reason=(
                f"degraded_to_ollama spent=${spent:.4f} ceiling=${ceiling:.2f}"
            ),
        )
    # warn_only / unknown mode -- log but allow through
    log.warning(
        "daily cost ceiling reached in warn_only mode: spent=$%.4f ceiling=$%.2f",
        spent,
        ceiling,
    )
    return BreachAction(
        breach=True, mode="warn_only", spent=spent, ceiling=ceiling, backend_override=None
    )

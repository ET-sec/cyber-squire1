"""Local SQLite spend ledger for the GRC reviewer.

Used as a fallback for the Anthropic admin usage API and as the canonical
record of per-call cost when running locally / in CI without admin API access.

Schema:
    spend(date TEXT, model TEXT, input_tokens INT, output_tokens INT,
          cache_read_tokens INT, cache_write_tokens INT, cost_usd REAL)

Pricing (USD per 1M tokens) is pinned in `PRICING` and matches the plan
synthesis "Cost math" research note. Cache-write multiplier is 1.25x base
input price; cache-read multiplier is 0.1x base input price.
"""

from __future__ import annotations

import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

# Pricing in USD per 1M tokens. Keys are exact model identifiers.
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-5":    {"input": 5.0,  "output": 25.0},
    "claude-fable-5":   {"input": 15.0, "output": 75.0},
    "claude-haiku-4-5": {"input": 1.0,  "output": 5.0},
}

CACHE_WRITE_MULTIPLIER = 1.25  # cache write costs 1.25x base input
CACHE_READ_MULTIPLIER  = 0.1   # cache read costs 0.10x base input


def _db_path() -> Path:
    """Return the SQLite path. Override with GRC_SPEND_DB env for tests."""
    override = os.environ.get("GRC_SPEND_DB")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "grc" / "spend_ledger.sqlite"


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS spend (
            date TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            cache_read_tokens INTEGER NOT NULL DEFAULT 0,
            cache_write_tokens INTEGER NOT NULL DEFAULT 0,
            cost_usd REAL NOT NULL DEFAULT 0.0
        )
        """
    )
    conn.commit()
    return conn


def compute_cost(model: str, usage: Mapping[str, int]) -> float:
    """Compute USD cost from a usage dict.

    Recognised keys (all optional, default 0):
      - input_tokens
      - output_tokens
      - cache_creation_input_tokens
      - cache_read_input_tokens

    Raises KeyError if the model is not in PRICING.
    """
    if model not in PRICING:
        raise KeyError(f"Unknown model for pricing: {model!r}")
    rates = PRICING[model]

    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    cache_write = int(usage.get("cache_creation_input_tokens", 0) or 0)
    cache_read = int(usage.get("cache_read_input_tokens", 0) or 0)

    base_in = rates["input"] / 1_000_000
    base_out = rates["output"] / 1_000_000

    cost = (
        input_tokens * base_in
        + output_tokens * base_out
        + cache_write * base_in * CACHE_WRITE_MULTIPLIER
        + cache_read * base_in * CACHE_READ_MULTIPLIER
    )
    return round(cost, 8)


def record_call(model: str, usage: Mapping[str, int]) -> float:
    """Insert one row recording the cost of a single API call.

    Returns the computed cost in USD. Lazily creates the ledger DB.
    """
    cost = compute_cost(model, usage)
    today = datetime.now(timezone.utc).date().isoformat()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO spend
                (date, model, input_tokens, output_tokens,
                 cache_read_tokens, cache_write_tokens, cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                today,
                model,
                int(usage.get("input_tokens", 0) or 0),
                int(usage.get("output_tokens", 0) or 0),
                int(usage.get("cache_read_input_tokens", 0) or 0),
                int(usage.get("cache_creation_input_tokens", 0) or 0),
                cost,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return cost


def today_total_usd() -> float:
    """Sum cost_usd for today (UTC). 0.0 if no rows / no DB yet."""
    today = datetime.now(timezone.utc).date().isoformat()
    path = _db_path()
    if not path.exists():
        return 0.0
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(cost_usd), 0.0) FROM spend WHERE date = ?",
            (today,),
        ).fetchone()
    finally:
        conn.close()
    return float(row[0]) if row and row[0] is not None else 0.0


if __name__ == "__main__":  # pragma: no cover
    print(f"Today USD spend: ${today_total_usd():.4f}", file=sys.stderr)

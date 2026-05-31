"""Thin HTTP client that invokes NeMo Guardrails' OpenAI-compat endpoint.

Called by :class:`squire.llm_backend.NeMoBackend` when ``NEMO_ENABLED=true``.

Key responsibilities:

* Build the payload and talk to ``<nemo_base_url>/chat/completions``.
* Parse NeMo's structured block events (``InputRailAbort``, ``OutputRailAbort``,
  ``BotRefuse``) into a typed :class:`NeMoBlock` dataclass.
* Also match the canonical refusal string the Colang flows emit
  (``BLOCKED_BY_RAIL reason=X rail=Y rule=Z``) -- some NeMo versions don't
  surface events through the OpenAI envelope, so the refusal string itself is
  our fallback signal.

Downstream, :class:`NeMoBackend` converts a ``NeMoBlock`` into a
``BackendResponse`` whose ``content`` starts with the ``__NEMO_BLOCK__:``
sentinel that :mod:`squire.app` detects and rewrites via
:func:`squire.response_builder.build_block_response`.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

log = logging.getLogger("squire.nemo_client")


# Sentinel the app-layer middleware looks for in BackendResponse.content.
BLOCK_SENTINEL = "__NEMO_BLOCK__:"

# Known NeMo block event names across v0.21.0 code paths.
BLOCK_EVENT_NAMES = frozenset(
    {
        "InputRailAbort",
        "OutputRailAbort",
        "BotRefuse",
        "PiiDetected",
        "PromptInjectionDetected",
    }
)

# Canonical refusal string format emitted by rails/*.co `bot refuse` flows.
# BLOCKED_BY_RAIL reason=PROMPT_INJECTION rail=input rule=pint_scorer
_BLOCK_LINE_RE = re.compile(
    r"BLOCKED_BY_RAIL\s+reason=(?P<reason>[A-Z_]+)\s+rail=(?P<rail>\w+)\s+rule=(?P<rule>[\w\-]+)"
)


@dataclass
class NeMoBlock:
    """Structured block signal."""

    reason_code: str = "RAIL_BLOCK"
    rail_name: str = "default"
    rule_name: str = "unknown"
    input_snippet: str = ""
    raw_event: dict[str, Any] = field(default_factory=dict)

    def as_sentinel(self) -> str:
        """Serialise to the ``__NEMO_BLOCK__:...`` string the app layer parses.

        Format: ``__NEMO_BLOCK__:reason_code=X;rail_name=Y;rule_name=Z;snippet=W``
        The snippet is truncated to 200 chars and has ``;`` / ``=`` stripped so
        it round-trips through ``dict(pair.split("=", 1))``.
        """
        safe_snippet = self.input_snippet.replace(";", ",").replace("=", ":")[:200]
        return (
            f"{BLOCK_SENTINEL}"
            f"reason_code={self.reason_code};"
            f"rail_name={self.rail_name};"
            f"rule_name={self.rule_name};"
            f"snippet={safe_snippet}"
        )


def parse_block(data: dict[str, Any], fallback_input: str = "") -> NeMoBlock | None:
    """Inspect a NeMo response dict; return a :class:`NeMoBlock` if blocked.

    Checks three signals in order:
      1. An ``events`` list containing any of :data:`BLOCK_EVENT_NAMES`.
      2. A top-level ``blocked`` / ``rail_blocked`` boolean.
      3. The choices[0].message.content string matching ``_BLOCK_LINE_RE``.
    """
    events = data.get("events") or []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        ev_name = ev.get("event") or ev.get("type")
        if ev_name in BLOCK_EVENT_NAMES:
            return NeMoBlock(
                reason_code=str(ev.get("reason", ev_name)),
                rail_name=str(ev.get("rail", "default")),
                rule_name=str(ev.get("rule", "unknown")),
                input_snippet=str(ev.get("input_snippet", fallback_input))[:400],
                raw_event=ev,
            )

    if data.get("blocked") or data.get("rail_blocked"):
        return NeMoBlock(
            reason_code=str(data.get("reason_code", "RAIL_BLOCK")),
            rail_name=str(data.get("rail_name", "default")),
            rule_name=str(data.get("rule_name", "unknown")),
            input_snippet=str(data.get("input_snippet", fallback_input))[:400],
            raw_event=dict(data),
        )

    choices = data.get("choices") or []
    if choices:
        msg = (choices[0] or {}).get("message") or {}
        text = str(msg.get("content") or "")
        match = _BLOCK_LINE_RE.search(text)
        if match:
            return NeMoBlock(
                reason_code=match.group("reason"),
                rail_name=match.group("rail"),
                rule_name=match.group("rule"),
                input_snippet=fallback_input[:400],
                raw_event={"matched_refusal_line": text[:400]},
            )

    return None


def extract_text(data: dict[str, Any]) -> str:
    """Pull the assistant text out of a NeMo/OpenAI-compat response."""
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = (choices[0] or {}).get("message") or {}
    return str(msg.get("content") or "")


def extract_usage(data: dict[str, Any]) -> tuple[int, int]:
    """Return (input_tokens, output_tokens) best-effort."""
    usage = data.get("usage") or {}
    return (
        int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0),
        int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0),
    )


def chat_via_nemo(
    messages: list[dict],
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    base_url: str | None = None,
    config_id: str = "default",
    timeout_s: float = 60.0,
) -> dict[str, Any]:
    """POST to NeMo's /v1/chat/completions. Returns the raw response dict.

    Caller (:class:`NeMoBackend`) is responsible for converting the dict into a
    :class:`squire.llm_backend.BackendResponse`. Kept separate so the HTTP
    boundary is unit-testable without touching the backend chain.
    """
    url_root = base_url or os.environ.get("NEMO_BASE_URL", "http://cd-service-nemo:8000/v1")
    url = f"{url_root.rstrip('/')}/chat/completions"

    # NeMo's OpenAI-compat endpoint wants bare model slug (no 'anthropic/' prefix).
    bare_model = model.replace("anthropic/", "") if model else "claude-sonnet-4-5"

    payload = {
        "config_id": config_id,
        "model": bare_model,
        "messages": [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Squire-Rails": config_id,
            },
        )
        resp.raise_for_status()
        return resp.json()

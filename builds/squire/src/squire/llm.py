"""Thin facade around llm_backend -- graph nodes import from here.

Rationale for the split:
  - llm_backend.py owns the backend classes, the factory, and the fallback chain.
  - llm.py owns the settings binding and the cost estimator, and is the surface
    graph nodes (classify / draft / critique) import.

This indirection keeps llm_backend dependency-free of Squire's settings module
so it can be unit-tested with monkeypatched env vars without having to populate
every other pydantic-settings field.
"""
from __future__ import annotations

import logging

from .llm_backend import BackendResponse, invoke_with_fallback
from .settings import settings

log = logging.getLogger("squire.llm")


# Approximate cost per 1K tokens (USD) as of 2026-04.
# Anthropic pricing for Claude Opus 4.8 / Sonnet 4.6. Update when pricing moves.
COST_PER_1K: dict[str, dict[str, float]] = {
    "anthropic/claude-opus-4-8": {"in": 0.015, "out": 0.075},
    "anthropic/claude-sonnet-4-6": {"in": 0.003, "out": 0.015},
    # bare (un-prefixed) forms for resilience
    "claude-opus-4-8": {"in": 0.015, "out": 0.075},
    "claude-sonnet-4-6": {"in": 0.003, "out": 0.015},
}


def llm_invoke(
    messages: list[dict],
    model: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    through_nemo: bool = False,
) -> BackendResponse:
    """Invoke an LLM via the configured primary backend + fallback chain.

    Reads `settings.squire_llm_backend` (SQUIRE_LLM_BACKEND env var, default
    'api'). Returns a BackendResponse with .content, .input_tokens,
    .output_tokens, .backend, .degraded, and .degraded_reason.

    When ``through_nemo=True`` AND ``settings.nemo_enabled`` is True, the
    primary backend is forced to ``nemo`` so draft/critique reasoning calls
    traverse the NeMo Guardrails sidecar. Classify/enrich/retrieve stay on
    the configured default -- NeMo only fronts the two high-stakes nodes
    per 17-10 to keep p95 latency under 30s.

    The caller is responsible for mapping `resp.degraded` into the IRState
    `_degraded_mode` flag so the 17-09 FastAPI middleware can emit the
    X-Squire-Degraded-Mode response header.
    """
    primary = settings.squire_llm_backend
    if through_nemo and getattr(settings, "nemo_enabled", False):
        primary = "nemo"

    return invoke_with_fallback(
        primary_name=primary,
        messages=messages,
        model_hint=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def make_llm(model: str | None = None):
    """Return a small callable bound to a specific model hint.

    Convenience wrapper for nodes that want to pass `llm` around without
    repeating the model argument. The returned callable mirrors llm_invoke's
    signature minus `model`.
    """
    bound_model = model or settings.claude_model_secondary

    def _invoke(
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> BackendResponse:
        return llm_invoke(
            messages=messages,
            model=bound_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    _invoke.__name__ = f"llm_invoke_bound_{bound_model}"
    return _invoke


def estimate_cost(model: str, in_tokens: int, out_tokens: int) -> float:
    """USD cost estimate. Unknown models fall back to an Opus-ish approximation."""
    c = COST_PER_1K.get(model) or COST_PER_1K.get(model.replace("anthropic/", "")) or {
        "in": 0.01,
        "out": 0.05,
    }
    return (in_tokens / 1000.0) * c["in"] + (out_tokens / 1000.0) * c["out"]

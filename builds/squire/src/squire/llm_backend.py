"""LLM backend abstraction for Squire (criterion #19 - Ollama fallback + degraded mode).

Three backends satisfy the Phase 17 Option A strategy as amended by Phase 22:

  NeMoBackend   -- NeMo Guardrails sidecar, and the production default. The
                   sidecar holds the model credential and is the only route
                   to the hosted model, so every production call is checked
                   by the rails before it reaches a model. A rail that cannot
                   answer produces a refusal, never an unchecked answer.

  MaxBackend    -- Claude Max subscription routing. Prefers `claude-agent-sdk`
                   if the module is installed; otherwise shells out to the
                   `claude --print` CLI. Requires pre-authenticated `claude`
                   on the host. DEV-ONLY (Mac); raises clearly on the server.

  OllamaBackend -- Local Ollama HTTP fallback. Resilience path; the
                   cd-service-ollama container is stopped for Phase 17 to free
                   RAM (per 17-02) so invoking this backend also requires the
                   container to be restarted manually (or via HITL runbook).

There is no direct-to-provider backend in this module. Phase 22 (AI-01)
deleted it, so a guardrail the code cannot reach has no path around it
either.

`get_backend(name)` is the factory. `invoke_with_fallback(primary, ...)` runs
the fallback chain:
    primary=nemo   -> nemo -> ollama
    primary=max    -> max -> ollama
    primary=ollama -> ollama (no fallback)

The chain walks only on a raised exception. A refusal is a returned response,
so it ends the call where it was made.

When fallback fires, the BackendResponse carries `degraded=True` and
`degraded_reason`, which the classify/draft/critique nodes propagate into
IRState. The FastAPI response middleware in 17-09 reads these to emit the
`X-Squire-Degraded-Mode` response header.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

log = logging.getLogger("squire.llm_backend")


@dataclass
class BackendResponse:
    """Normalized response across all backends."""

    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    backend: str = "unknown"
    degraded: bool = False
    degraded_reason: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LLMBackend(Protocol):
    """Structural protocol every backend implementation conforms to."""

    name: str

    def invoke(
        self,
        messages: list[dict],
        model_hint: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> BackendResponse: ...


# ----------------------------------------------------------------------
# Implementation: Claude Max subscription (dev-only)
# ----------------------------------------------------------------------


class MaxBackend:
    """Claude Max routing via Agent SDK (preferred) or `claude --print` CLI.

    Dev-only. Raw OAuth token replay was blocked by Anthropic in April 2026,
    so this backend depends on an officially-supported path:

      1. `claude-agent-sdk` Python package (if installed in the venv).
      2. `claude` CLI on PATH (requires `claude login` once on the host).

    Raises RuntimeError on droplet where neither is present.
    """

    name = "max"

    def __init__(self) -> None:
        self._sdk_available = False
        try:
            import claude_agent_sdk  # type: ignore  # noqa: F401

            self._sdk_available = True
        except Exception:
            self._sdk_available = False
        self._cli_path = shutil.which("claude")

    def invoke(
        self,
        messages: list[dict],
        model_hint: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> BackendResponse:
        sys_parts = [m.get("content", "") for m in messages if m.get("role") == "system"]
        user_parts = [m.get("content", "") for m in messages if m.get("role") != "system"]
        prompt = "\n\n".join([*sys_parts, *user_parts]).strip()

        if self._sdk_available:
            try:
                import claude_agent_sdk as cas  # type: ignore

                model = model_hint.replace("anthropic/", "") if model_hint else None
                resp = cas.query(prompt=prompt, model=model)  # type: ignore[attr-defined]
                text = resp if isinstance(resp, str) else str(resp)
                return BackendResponse(
                    content=text,
                    backend=self.name,
                    raw={"via": "sdk", "model": model},
                )
            except Exception as e:
                log.warning("MaxBackend SDK failed: %s; falling to CLI subprocess", e)

        if not self._cli_path:
            raise RuntimeError(
                "MaxBackend requires either the claude-agent-sdk package or "
                "the `claude` CLI installed and authenticated on the host"
            )

        # The claude CLI prefers Max OAuth auth, but if ANTHROPIC_API_KEY is
        # set in the environment it will try to use that instead and fail with
        # "Invalid API key" when the value is a stub or an OAuth token that
        # isn't valid for the direct API. Strip it for this child process.
        child_env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        proc = subprocess.run(
            [self._cli_path, "--print", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=child_env,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude CLI exit {proc.returncode}: {proc.stderr[:300] or proc.stdout[:300]}"
            )
        return BackendResponse(
            content=proc.stdout.strip(),
            backend=self.name,
            raw={"via": "cli"},
        )


# ----------------------------------------------------------------------
# Implementation: Ollama local fallback
# ----------------------------------------------------------------------


class OllamaBackend:
    """Local Ollama HTTP fallback over /api/chat.

    The OLLAMA_MODEL_MAP translates anthropic-slug hints into locally-pulled
    Ollama model tags. The cd-service-ollama container is stopped during Phase
    17 (per 17-02) to free ~500 MiB; bringing it back is a single
    `docker compose start cd-service-ollama` but is documented as a manual
    HITL step in the degraded-mode runbook (17-13a).
    """

    name = "ollama"

    OLLAMA_MODEL_MAP: dict[str, str] = {
        "anthropic/claude-fable-5": "llama3.3:70b",
        "anthropic/claude-opus-5": "llama3.1:8b",
    }

    def invoke(
        self,
        messages: list[dict],
        model_hint: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> BackendResponse:
        import httpx

        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://cd-service-ollama:11434")
        mapped = self.OLLAMA_MODEL_MAP.get(model_hint, "llama3.1:8b")

        payload = {
            "model": mapped,
            "messages": [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in messages
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        with httpx.Client(timeout=120.0) as c:
            r = c.post(f"{ollama_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()

        return BackendResponse(
            content=data.get("message", {}).get("content", ""),
            input_tokens=int(data.get("prompt_eval_count", 0) or 0),
            output_tokens=int(data.get("eval_count", 0) or 0),
            backend=self.name,
            degraded=True,
            degraded_reason="ollama_local_fallback",
            raw={"model": mapped},
        )


# ----------------------------------------------------------------------
# Implementation: NeMo Guardrails sidecar (17-10)
# ----------------------------------------------------------------------


class NeMoBackend:
    """Route chat calls through the NeMo Guardrails sidecar.

    The sidecar runs PolicyAI (self-check), GLiNER (PII), and PINT v2
    (prompt-injection) on every input + output. When a rail fires, NeMo
    returns a structured block signal that :mod:`squire.nemo_client` parses
    into a :class:`~squire.nemo_client.NeMoBlock`. We serialise the block
    into the ``__NEMO_BLOCK__:...`` sentinel content that
    :mod:`squire.app` rewrites into the structured block-response JSON
    from :func:`squire.response_builder.build_block_response`.

    Fails closed (Phase 22, AI-01). A sidecar that times out, errors, or
    reports an upstream model failure returns a refusal sentinel whose
    ``reason_code`` marks the rail unavailable, together with a degraded
    reason naming the branch that produced it. The sidecar is the only
    route to the hosted model, so there is no path around it to take.
    """

    name = "nemo"

    def invoke(
        self,
        messages: list[dict],
        model_hint: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> BackendResponse:
        from .nemo_client import (
            NeMoBlock,
            chat_via_nemo,
            extract_text,
            extract_usage,
            parse_block,
        )
        from .settings import settings

        fallback_input = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                fallback_input = str(m.get("content", ""))[:400]
                break

        try:
            data = chat_via_nemo(
                messages=messages,
                model=model_hint,
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=settings.nemo_base_url,
                config_id=settings.nemo_config_id,
                timeout_s=settings.nemo_timeout_s,
            )
        except Exception as exc:
            # Fail closed (Phase 22, AI-01). The rails are the only path to the
            # hosted model, so a sidecar that cannot answer means the call is
            # refused, not re-routed around the guardrail.
            log.warning(
                "NeMoBackend: sidecar call failed (%s); refusing (fail closed)", exc
            )
            block = NeMoBlock(
                reason_code="RAIL_UNAVAILABLE",
                rail_name="input",
                rule_name=(
                    "sidecar_timeout"
                    if "Timeout" in type(exc).__name__
                    else "sidecar_error"
                ),
                input_snippet=fallback_input,
                raw_event={"exception": type(exc).__name__},
            )
            return BackendResponse(
                content=block.as_sentinel(),
                backend=self.name,
                degraded=True,
                degraded_reason=(
                    f"nemo_sidecar_unavailable_fail_closed: {type(exc).__name__}"
                ),
                raw={"block": block.raw_event, "model": model_hint},
            )

        block = parse_block(data, fallback_input=fallback_input)
        if block is not None:
            # Emit sentinel content; app.py detects and rewrites via
            # response_builder.build_block_response.
            return BackendResponse(
                content=block.as_sentinel(),
                input_tokens=0,
                output_tokens=0,
                backend=self.name,
                raw={"block": block.raw_event, "model": model_hint},
            )

        text = extract_text(data)
        # Refuse if NeMo returned the generic internal-error placeholder
        # (happens when PolicyAI self_check or the generate step hits upstream
        # LLM credit exhaustion). The rails produced no checked answer, so
        # there is nothing to return but a refusal.
        if text.strip().lower() == "internal server error":
            log.warning(
                "NeMoBackend: sidecar returned 'Internal server error' "
                "(upstream LLM failure); refusing (fail closed)"
            )
            block = NeMoBlock(
                reason_code="RAIL_UNAVAILABLE",
                rail_name="input",
                rule_name="upstream_llm_failed",
                input_snippet=fallback_input,
                raw_event={"nemo_text": "internal server error"},
            )
            return BackendResponse(
                content=block.as_sentinel(),
                backend=self.name,
                degraded=True,
                degraded_reason="nemo_upstream_llm_failed_fail_closed",
                raw={"block": block.raw_event, "model": model_hint},
            )

        in_tokens, out_tokens = extract_usage(data)
        return BackendResponse(
            content=text,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            backend=self.name,
            raw={"model": model_hint, "via": "nemo"},
        )


# ----------------------------------------------------------------------
# Factory + fallback chain
# ----------------------------------------------------------------------

_BACKEND_REGISTRY: dict[str, type] = {
    "max": MaxBackend,
    "nemo": NeMoBackend,
    "ollama": OllamaBackend,
}


def get_backend(name: str | None) -> LLMBackend:
    """Return an instance of the requested backend.

    name in {max, nemo, ollama}. Unknown or empty defaults to 'nemo' and emits
    a warning.
    """
    n = (name or "nemo").strip().lower()
    cls = _BACKEND_REGISTRY.get(n)
    if cls is None:
        log.warning("unknown backend %r, defaulting to nemo", name)
        cls = NeMoBackend
    return cls()


# Fallback chain per Option A strategy (see module docstring). Every chain
# ends at the local model, because that is the only remaining backend that can
# answer when the rails are down and it answers without the hosted model.
FALLBACK_CHAINS: dict[str, list[str]] = {
    "max": ["max", "ollama"],
    "nemo": ["nemo", "ollama"],
    "ollama": ["ollama"],
}


def invoke_with_fallback(
    primary_name: str,
    messages: list[dict],
    model_hint: str,
    **kwargs,
) -> BackendResponse:
    """Invoke the primary backend; on failure, walk the fallback chain.

    When a non-primary backend produces the response, degraded=True and
    degraded_reason='fell_back_from_{primary}_to_{actual}' are set.
    Raises RuntimeError if the whole chain fails.
    """
    primary = (primary_name or "nemo").strip().lower()
    chain = FALLBACK_CHAINS.get(primary, ["nemo", "ollama"])
    last_err: Exception | None = None
    for bn in chain:
        try:
            backend = get_backend(bn)
            resp = backend.invoke(messages, model_hint, **kwargs)
            if bn != primary:
                resp.degraded = True
                resp.degraded_reason = f"fell_back_from_{primary}_to_{bn}"
            return resp
        except Exception as e:
            log.warning("backend %s failed: %s; trying next in chain", bn, e)
            last_err = e
    raise RuntimeError(
        f"all backends in chain {chain} failed; last error: {last_err}"
    )

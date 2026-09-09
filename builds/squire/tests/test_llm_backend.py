"""Unit tests for the LLM backend factory + fallback chain (criterion #19).

These tests never invoke a live model. BackendResponse is built directly via
monkeypatched backend classes; only the routing + degraded-mode flag logic is
under test.
"""
from __future__ import annotations

import os

import pytest

# Required env so pydantic-settings doesn't fail when anything imports from
# squire.settings. llm_backend itself doesn't require settings at import time
# (it lazy-imports inside NeMoBackend.invoke) but tests reaching through llm.py
# will need these.
os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from squire import llm_backend as lb  # noqa: E402
from squire.llm_backend import (  # noqa: E402
    BackendResponse,
    FALLBACK_CHAINS,
    LLMBackend,
    MaxBackend,
    NeMoBackend,
    OllamaBackend,
    get_backend,
    invoke_with_fallback,
)


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def test_factory_nemo():
    b = get_backend("nemo")
    assert isinstance(b, NeMoBackend)
    assert b.name == "nemo"


def test_factory_max():
    b = get_backend("max")
    assert isinstance(b, MaxBackend)
    assert b.name == "max"


def test_factory_ollama():
    b = get_backend("ollama")
    assert isinstance(b, OllamaBackend)
    assert b.name == "ollama"


def test_factory_case_insensitive():
    assert isinstance(get_backend(" NEMO "), NeMoBackend)
    assert isinstance(get_backend(" MAX "), MaxBackend)


def test_factory_unknown_defaults_nemo(caplog):
    with caplog.at_level("WARNING", logger="squire.llm_backend"):
        b = get_backend("nonsense")
    assert isinstance(b, NeMoBackend)
    assert any("unknown backend" in rec.message for rec in caplog.records)


def test_factory_none_defaults_nemo():
    assert isinstance(get_backend(None), NeMoBackend)
    assert isinstance(get_backend(""), NeMoBackend)


def test_all_backends_satisfy_protocol():
    for b in (MaxBackend(), NeMoBackend(), OllamaBackend()):
        assert isinstance(b, LLMBackend)


# ----------------------------------------------------------------------
# Env-flag behavior via monkeypatching SQUIRE_LLM_BACKEND
# ----------------------------------------------------------------------


def test_env_flag_routes_through_settings(monkeypatch):
    """llm.py reads settings.squire_llm_backend; verify it picks up env changes."""
    # Force re-read of settings by clearing the cache.
    import squire.settings as settings_mod
    monkeypatch.setenv("SQUIRE_LLM_BACKEND", "ollama")
    settings_mod._settings = None
    fresh = settings_mod.get_settings()
    assert fresh.squire_llm_backend == "ollama"


# ----------------------------------------------------------------------
# Fallback chain
# ----------------------------------------------------------------------


def test_fallback_chain_definitions():
    assert FALLBACK_CHAINS["nemo"] == ["nemo", "ollama"]
    assert FALLBACK_CHAINS["max"] == ["max", "ollama"]
    assert FALLBACK_CHAINS["ollama"] == ["ollama"]
    assert "api" not in FALLBACK_CHAINS


def _patch_registry(monkeypatch, mapping: dict[str, type]) -> None:
    """Swap _BACKEND_REGISTRY in llm_backend for the duration of the test."""
    monkeypatch.setattr(lb, "_BACKEND_REGISTRY", mapping)


class _StubResponding:
    """Backend stub that returns a canned BackendResponse."""

    def __init__(self, name: str, content: str = "ok"):
        self.name = name
        self._content = content
        self.invoked = 0

    def invoke(self, messages, model_hint, temperature=0.2, max_tokens=1024):
        self.invoked += 1
        return BackendResponse(
            content=self._content,
            input_tokens=10,
            output_tokens=20,
            backend=self.name,
        )


class _StubFailing:
    """Backend stub that raises on invoke."""

    def __init__(self, name: str, exc: Exception | None = None):
        self.name = name
        self._exc = exc or RuntimeError(f"{name}_unavailable")
        self.invoked = 0

    def invoke(self, messages, model_hint, temperature=0.2, max_tokens=1024):
        self.invoked += 1
        raise self._exc


def test_fallback_primary_succeeds(monkeypatch):
    nemo_instance = _StubResponding("nemo", "primary_ok")
    _patch_registry(monkeypatch, {
        "nemo": lambda: nemo_instance,
        "ollama": lambda: _StubResponding("ollama", "should_not_run"),
    })
    resp = invoke_with_fallback("nemo", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")
    assert resp.content == "primary_ok"
    assert resp.backend == "nemo"
    assert resp.degraded is False
    assert nemo_instance.invoked == 1


def test_fallback_falls_through_to_ollama(monkeypatch):
    nemo_instance = _StubFailing("nemo")
    ollama_instance = _StubResponding("ollama", "degraded_content")
    _patch_registry(monkeypatch, {
        "nemo": lambda: nemo_instance,
        "ollama": lambda: ollama_instance,
    })
    resp = invoke_with_fallback("nemo", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")
    assert resp.content == "degraded_content"
    assert resp.backend == "ollama"
    assert resp.degraded is True
    assert resp.degraded_reason == "fell_back_from_nemo_to_ollama"
    assert nemo_instance.invoked == 1
    assert ollama_instance.invoked == 1


def test_fallback_raises_when_all_fail(monkeypatch):
    _patch_registry(monkeypatch, {
        "nemo": lambda: _StubFailing("nemo", RuntimeError("nemo_down")),
        "ollama": lambda: _StubFailing("ollama", RuntimeError("ollama_down")),
    })
    with pytest.raises(RuntimeError, match="all backends in chain"):
        invoke_with_fallback("nemo", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")


def test_fallback_ollama_primary_has_no_fallback(monkeypatch):
    ollama_instance = _StubResponding("ollama", "ollama_only")
    _patch_registry(monkeypatch, {"ollama": lambda: ollama_instance})
    resp = invoke_with_fallback("ollama", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")
    assert resp.content == "ollama_only"
    # When ollama IS the primary, degraded should NOT be set by the chain
    # (individual OllamaBackend sets its own degraded flag on real invokes, but
    # the stub mirrors primary-success semantics).
    assert resp.backend == "ollama"
    assert resp.degraded is False


# ----------------------------------------------------------------------
# Fail closed on the guardrail path (Phase 22, AI-01)
# ----------------------------------------------------------------------


def test_guardrail_timeout_refuses_and_makes_no_direct_api_call(monkeypatch):
    import httpx
    from squire import nemo_client as nc
    from squire.nemo_client import BLOCK_SENTINEL

    def boom(*a, **kw):
        raise httpx.ReadTimeout("sidecar did not answer")

    monkeypatch.setattr(nc, "chat_via_nemo", boom)

    # Any second HTTP attempt from inside the refusal path would have to open
    # a client, so make that loud rather than let it reach the network.
    def _exploding_client(*a, **kw):
        raise AssertionError("the refusal path opened an HTTP client")

    monkeypatch.setattr(httpx, "Client", _exploding_client)

    resp = lb.NeMoBackend().invoke(
        [{"role": "user", "content": "suspicious powershell on host 12"}],
        "anthropic/claude-fable-5",
    )

    assert resp.content.startswith(BLOCK_SENTINEL)
    assert "reason_code=RAIL_UNAVAILABLE" in resp.content
    assert "rule_name=sidecar_timeout" in resp.content
    assert resp.degraded is True
    assert "fail_closed" in resp.degraded_reason
    assert "api" not in lb._BACKEND_REGISTRY
    assert not hasattr(lb, "APIBackend")


def test_guardrail_http_error_refuses(monkeypatch):
    import httpx
    from squire import nemo_client as nc
    from squire.nemo_client import BLOCK_SENTINEL

    request = httpx.Request("POST", "http://svc-nemo/v1/chat/completions")
    response = httpx.Response(500, request=request)

    def boom(*a, **kw):
        raise httpx.HTTPStatusError(
            "500 from the sidecar", request=request, response=response
        )

    monkeypatch.setattr(nc, "chat_via_nemo", boom)

    resp = lb.NeMoBackend().invoke(
        [{"role": "user", "content": "exfil attempt on the finance share"}],
        "anthropic/claude-fable-5",
    )

    assert resp.content.startswith(BLOCK_SENTINEL)
    assert "reason_code=RAIL_UNAVAILABLE" in resp.content
    assert "rail_name=input" in resp.content
    assert "rule_name=sidecar_error" in resp.content
    assert resp.degraded is True
    assert "fail_closed" in resp.degraded_reason
    assert "api" not in lb._BACKEND_REGISTRY
    assert not hasattr(lb, "APIBackend")


def test_upstream_failure_refusal_ends_the_chain(monkeypatch):
    """A returned refusal is a response, so the chain stops instead of walking."""
    from squire import nemo_client as nc
    from squire.nemo_client import BLOCK_SENTINEL

    def upstream_failed(*a, **kw):
        return {"choices": [{"message": {"content": "Internal server error"}}]}

    monkeypatch.setattr(nc, "chat_via_nemo", upstream_failed)

    resp = invoke_with_fallback(
        "nemo",
        [{"role": "user", "content": "beacon to a known bad host"}],
        "anthropic/claude-fable-5",
    )

    assert resp.content.startswith(BLOCK_SENTINEL)
    assert "reason_code=RAIL_UNAVAILABLE" in resp.content
    assert "rule_name=upstream_llm_failed" in resp.content
    assert resp.backend == "nemo"
    assert resp.degraded is True
    assert resp.degraded_reason == "nemo_upstream_llm_failed_fail_closed"
    # The chain never relabelled it, which is what proves ollama was not tried.
    assert "fell_back_from" not in resp.degraded_reason

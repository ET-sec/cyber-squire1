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
# (it lazy-imports inside APIBackend.invoke) but tests reaching through llm.py
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
    APIBackend,
    BackendResponse,
    FALLBACK_CHAINS,
    LLMBackend,
    MaxBackend,
    OllamaBackend,
    get_backend,
    invoke_with_fallback,
)


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def test_factory_api():
    b = get_backend("api")
    assert isinstance(b, APIBackend)
    assert b.name == "api"


def test_factory_max():
    b = get_backend("max")
    assert isinstance(b, MaxBackend)
    assert b.name == "max"


def test_factory_ollama():
    b = get_backend("ollama")
    assert isinstance(b, OllamaBackend)
    assert b.name == "ollama"


def test_factory_case_insensitive():
    assert isinstance(get_backend("API"), APIBackend)
    assert isinstance(get_backend(" MAX "), MaxBackend)


def test_factory_unknown_defaults_api(caplog):
    with caplog.at_level("WARNING", logger="squire.llm_backend"):
        b = get_backend("nonsense")
    assert isinstance(b, APIBackend)
    assert any("unknown backend" in rec.message for rec in caplog.records)


def test_factory_none_defaults_api():
    assert isinstance(get_backend(None), APIBackend)
    assert isinstance(get_backend(""), APIBackend)


def test_all_backends_satisfy_protocol():
    for b in (APIBackend(), MaxBackend(), OllamaBackend()):
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
    assert FALLBACK_CHAINS["api"] == ["api", "ollama"]
    assert FALLBACK_CHAINS["max"] == ["max", "api", "ollama"]
    assert FALLBACK_CHAINS["ollama"] == ["ollama"]


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
    api_instance = _StubResponding("api", "primary_ok")
    _patch_registry(monkeypatch, {
        "api": lambda: api_instance,
        "ollama": lambda: _StubResponding("ollama", "should_not_run"),
    })
    resp = invoke_with_fallback("api", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")
    assert resp.content == "primary_ok"
    assert resp.backend == "api"
    assert resp.degraded is False
    assert api_instance.invoked == 1


def test_fallback_falls_through_to_ollama(monkeypatch):
    api_instance = _StubFailing("api")
    ollama_instance = _StubResponding("ollama", "degraded_content")
    _patch_registry(monkeypatch, {
        "api": lambda: api_instance,
        "ollama": lambda: ollama_instance,
    })
    resp = invoke_with_fallback("api", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")
    assert resp.content == "degraded_content"
    assert resp.backend == "ollama"
    assert resp.degraded is True
    assert resp.degraded_reason == "fell_back_from_api_to_ollama"
    assert api_instance.invoked == 1
    assert ollama_instance.invoked == 1


def test_fallback_max_walks_full_chain(monkeypatch):
    max_instance = _StubFailing("max")
    api_instance = _StubFailing("api")
    ollama_instance = _StubResponding("ollama", "last_resort")
    _patch_registry(monkeypatch, {
        "max": lambda: max_instance,
        "api": lambda: api_instance,
        "ollama": lambda: ollama_instance,
    })
    resp = invoke_with_fallback("max", [{"role": "user", "content": "hi"}], "anthropic/claude-sonnet-4-6")
    assert resp.content == "last_resort"
    assert resp.backend == "ollama"
    assert resp.degraded is True
    assert resp.degraded_reason == "fell_back_from_max_to_ollama"
    assert max_instance.invoked == 1
    assert api_instance.invoked == 1
    assert ollama_instance.invoked == 1


def test_fallback_raises_when_all_fail(monkeypatch):
    _patch_registry(monkeypatch, {
        "api": lambda: _StubFailing("api", RuntimeError("api_down")),
        "ollama": lambda: _StubFailing("ollama", RuntimeError("ollama_down")),
    })
    with pytest.raises(RuntimeError, match="all backends in chain"):
        invoke_with_fallback("api", [{"role": "user", "content": "hi"}], "anthropic/claude-fable-5")


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

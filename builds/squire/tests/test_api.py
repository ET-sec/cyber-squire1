"""FastAPI surface tests for /alert + /replay.

Exercises:
  - /health public, 200
  - /alert auth (missing + wrong token)
  - /alert positive path with graph monkeypatched
  - X-Squire-Max-Iterations header threads to invoke_with_trace
  - X-Squire-Degraded-Mode response header when state._degraded_mode=True
  - Dedup short-circuit on repeat alert
  - Cost ceiling mode=refuse => 503 with structured body
  - Cost ceiling mode=ollama => backend override applied (verified via env capture)
  - Citation guard strips invalid codes at FastAPI boundary
"""
from __future__ import annotations

import json
import os

import pytest

os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
# Force the webhook token to a known value for this test module. The global
# settings object is lazily instantiated on first attribute access; test_healthz
# may have imported first with a different token, so overwrite then reset the
# cached settings.
os.environ["SQUIRE_WEBHOOK_TOKEN"] = "test-token"
os.environ.setdefault("ANTHROPIC_DAILY_CEILING_USD", "100")
os.environ.setdefault("SQUIRE_COST_BREACH_MODE", "warn_only")
# Steer actions_allowlist at a config we know exists
os.environ.setdefault(
    "SQUIRE_ACTIONS_ALLOWLIST_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "actions.yml",
    ),
)

from fastapi.testclient import TestClient  # noqa: E402

from squire import app as app_mod  # noqa: E402
from squire import cost_ceiling, dedup, persist  # noqa: E402
from squire import settings as _settings_mod  # noqa: E402

# Reset the settings singleton so this module's SQUIRE_WEBHOOK_TOKEN wins even
# when another test module imported settings first with a different value.
_settings_mod._settings = None

client = TestClient(app_mod.app)
TOKEN = {"X-Squire-Token": "test-token"}

SAMPLE_ALERT = {
    "rule": "Terminal shell in container",
    "priority": "Notice",
    "output_fields": {"container.id": "test-container-abc"},
}


def _stub_graph(result: dict):
    """Return a callable that records call args and returns `result`."""
    recorded: dict = {"calls": []}

    def _stub(alert, alert_id, max_iters_override):
        recorded["calls"].append(
            {"alert": alert, "alert_id": alert_id, "max_iters": max_iters_override,
             "backend": os.environ.get("SQUIRE_LLM_BACKEND")}
        )
        return result

    return _stub, recorded


@pytest.fixture(autouse=True)
def _stub_persist_and_dedup(monkeypatch):
    """Keep every test hermetic: no DB, no Redis."""
    monkeypatch.setattr(persist, "save_investigation", lambda *a, **kw: "00000000-0000-0000-0000-000000000000")
    monkeypatch.setattr(persist, "load_alert", lambda alert_id: {"rule": "stored"})
    # Dedup defaults to "not a duplicate" unless a test overrides.
    monkeypatch.setattr(
        dedup,
        "check_and_register",
        lambda alert, alert_id, trace_id=None: dedup.DedupResult(
            is_duplicate=False, sig="x"
        ),
    )
    monkeypatch.setattr(dedup, "update_trace_id", lambda sig, trace_id: None)
    # Re-bind the symbols that app.py imported at module-load time.
    monkeypatch.setattr(app_mod, "check_and_register", dedup.check_and_register)
    monkeypatch.setattr(app_mod, "dedup_update_trace", dedup.update_trace_id)
    monkeypatch.setattr(app_mod, "load_alert", persist.load_alert)
    monkeypatch.setattr(app_mod, "save_investigation", persist.save_investigation)
    # Default cost budget: no breach.
    monkeypatch.setattr(
        cost_ceiling,
        "consult",
        lambda: cost_ceiling.BreachAction(
            breach=False, mode="warn_only", spent=0.0, ceiling=100.0, backend_override=None
        ),
    )
    monkeypatch.setattr(app_mod, "consult_budget", cost_ceiling.consult)
    yield


# ---------------------- basic / auth ----------------------


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    b = r.json()
    assert b["status"] == "ok" and b["service"] == "squire"


def test_alert_rejects_missing_token():
    r = client.post("/alert", json={"alert": SAMPLE_ALERT})
    assert r.status_code == 401


def test_alert_rejects_wrong_token():
    r = client.post(
        "/alert",
        json={"alert": SAMPLE_ALERT},
        headers={"X-Squire-Token": "WRONG"},
    )
    assert r.status_code == 401


def test_alert_token_check_is_constant_time(monkeypatch):
    """The token gate goes through hmac.compare_digest, never ``!=``."""
    seen: list[tuple[bytes, bytes]] = []
    real = app_mod.hmac.compare_digest

    def spy(a, b):
        seen.append((a, b))
        return real(a, b)

    monkeypatch.setattr(app_mod.hmac, "compare_digest", spy)
    r = client.post(
        "/alert",
        json={"alert": SAMPLE_ALERT},
        headers={"X-Squire-Token": "WRONG"},
    )
    assert r.status_code == 401
    assert seen == [(b"WRONG", b"test-token")]


def test_alert_rejects_non_ascii_token_cleanly():
    """compare_digest refuses non-ASCII str, so the gate encodes both sides
    first: a hostile header is a 401, not a 500."""
    r = client.post(
        "/alert",
        json={"alert": SAMPLE_ALERT},
        headers={b"X-Squire-Token": "t\xe9st".encode("latin-1")},
    )
    assert r.status_code == 401


# ---------------------- positive path ----------------------


def test_alert_positive_path(monkeypatch):
    stub, rec = _stub_graph({
        "severity": "MEDIUM",
        "draft_report": json.dumps({
            "summary": "ok",
            "recommended_actions": ["monitor the process"],
            "citations": {"csf_2_0": ["RS.MA-03"]},
        }),
        "citations": {"csf_2_0": ["RS.MA-03"]},
        "trace_id": "trc-123",
        "total_cost_usd": 0.01,
    })
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)

    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["severity"] == "MEDIUM"
    assert body["trace_id"] == "trc-123"
    assert body["trace_url"].endswith("/trace/trc-123")
    assert body["citations"] == {"csf_2_0": ["RS.MA-03"]}
    assert body["deduplicated"] is False
    assert body["degraded_mode"] is False
    assert len(rec["calls"]) == 1


# ---------------------- iteration override header ----------------------


def test_max_iters_header_threaded(monkeypatch):
    stub, rec = _stub_graph({"draft_report": "{}", "trace_id": "t"})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post(
        "/alert",
        json={"alert": SAMPLE_ALERT},
        headers={**TOKEN, "X-Squire-Max-Iterations": "0"},
    )
    assert r.status_code == 200
    assert rec["calls"][0]["max_iters"] == 0


def test_max_iters_header_out_of_range_ignored(monkeypatch):
    stub, rec = _stub_graph({"draft_report": "{}"})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    client.post(
        "/alert",
        json={"alert": SAMPLE_ALERT},
        headers={**TOKEN, "X-Squire-Max-Iterations": "999"},
    )
    assert rec["calls"][0]["max_iters"] is None


# ---------------------- degraded-mode header ----------------------


def test_degraded_mode_header_set(monkeypatch):
    stub, _ = _stub_graph({
        "draft_report": "{}",
        "_degraded_mode": True,
        "_degraded_reason": "api_unreachable",
        "trace_id": "t",
    })
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.headers.get("X-Squire-Degraded-Mode") == "true"
    body = r.json()
    assert body["degraded_mode"] is True
    assert "Degraded mode" in (body["footer"] or "")


# ---------------------- dedup ----------------------


def test_dedup_short_circuits(monkeypatch):
    monkeypatch.setattr(
        app_mod,
        "check_and_register",
        lambda alert, alert_id, trace_id=None: dedup.DedupResult(
            is_duplicate=True,
            original_alert_id="orig-1",
            original_trace_id="orig-trace",
            sig="x",
        ),
    )
    stub, rec = _stub_graph({"draft_report": "{}"})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.status_code == 200
    body = r.json()
    assert body["deduplicated"] is True
    assert body["original_alert_id"] == "orig-1"
    assert r.headers.get("X-Squire-Deduplicated") == "true"
    # Graph must NOT have been invoked
    assert len(rec["calls"]) == 0


# ---------------------- cost ceiling ----------------------


def test_cost_ceiling_refuse_returns_503(monkeypatch):
    monkeypatch.setattr(
        app_mod,
        "consult_budget",
        lambda: cost_ceiling.BreachAction(
            breach=True, mode="refuse", spent=5.0, ceiling=0.01, backend_override=None,
            reason="over",
        ),
    )
    stub, rec = _stub_graph({"draft_report": "{}"})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.status_code == 503
    body = r.json()
    assert body["reason_code"] == "daily_cost_ceiling_reached"
    assert r.headers.get("Retry-After") == "3600"
    assert len(rec["calls"]) == 0


def test_cost_ceiling_ollama_override_applies(monkeypatch):
    monkeypatch.setattr(
        app_mod,
        "consult_budget",
        lambda: cost_ceiling.BreachAction(
            breach=True, mode="ollama", spent=5.0, ceiling=0.01,
            backend_override="ollama", reason="budget",
        ),
    )
    stub, rec = _stub_graph({"draft_report": "{}", "_degraded_mode": False})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.status_code == 200
    # Env was set to ollama during invocation
    assert rec["calls"][0]["backend"] == "ollama"
    # Response flags degraded
    body = r.json()
    assert body["degraded_mode"] is True
    assert r.headers.get("X-Squire-Degraded-Mode") == "true"


# ---------------------- citation guard ----------------------


def test_citation_guard_strips_invalid_codes(monkeypatch):
    stub, _ = _stub_graph({
        "draft_report": json.dumps({
            "summary": "x",
            "citations": {
                "csf_2_0": ["RS.MA-03", "RS.BOGUS-99"],
                "owasp_llm": ["LLM01", "LLM99"],
                "fake_framework": ["foo"],
            },
        }),
        "trace_id": "t",
    })
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/alert", json={"alert": SAMPLE_ALERT}, headers=TOKEN)
    assert r.status_code == 200
    body = r.json()
    cites = body["report"]["citations"]
    assert cites.get("csf_2_0") == ["RS.MA-03"]
    assert cites.get("owasp_llm") == ["LLM01"]
    assert "fake_framework" not in cites


# ---------------------- replay ----------------------


def test_replay_uses_stored_alert_payload(monkeypatch):
    stub, rec = _stub_graph({"draft_report": "{}", "trace_id": "t-replay"})
    monkeypatch.setattr(app_mod, "_invoke_graph", stub)
    r = client.post("/replay/sq-original", headers=TOKEN)
    assert r.status_code == 200
    assert rec["calls"][0]["alert"] == {"rule": "stored"}
    # new alert_id is derived
    assert rec["calls"][0]["alert_id"].startswith("sq-original-replay-")


def test_replay_404_when_alert_missing(monkeypatch):
    monkeypatch.setattr(app_mod, "load_alert", lambda aid: None)
    r = client.post("/replay/nope", headers=TOKEN)
    assert r.status_code == 404

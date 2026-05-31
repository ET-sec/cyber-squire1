"""Smoke test for /health endpoint."""
import os

# Populate required env so pydantic-settings can instantiate
os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from fastapi.testclient import TestClient

from squire.app import app


def test_health_ok():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "squire"


def test_healthz_ok():
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

"""Unit tests for keycloak_client.KeycloakClient token caching and refresh.

All tests mock httpx so they run offline with no live Keycloak.
"""
from __future__ import annotations

import os
import time
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from pydantic import SecretStr  # noqa: E402

from squire import keycloak_client  # noqa: E402
from squire.keycloak_client import (  # noqa: E402
    KeycloakAuthError,
    KeycloakClient,
    KeycloakDisabledError,
)
from squire.settings import settings  # noqa: E402


def _enable_kc(monkeypatch, secret: str | None = "test-secret"):
    monkeypatch.setattr(settings, "kc_enabled", True, raising=False)
    monkeypatch.setattr(settings, "kc_base_url", "http://kc.test:8080", raising=False)
    monkeypatch.setattr(settings, "kc_realm", "coredirective", raising=False)
    monkeypatch.setattr(settings, "kc_client_id", "squire", raising=False)
    monkeypatch.setattr(
        settings,
        "kc_client_secret",
        SecretStr(secret) if secret is not None else None,
        raising=False,
    )
    monkeypatch.setattr(settings, "kc_token_refresh_skew_seconds", 10, raising=False)


def _mock_token_response(monkeypatch, access_token="tok", expires_in=300, scope="grc:read"):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "access_token": access_token,
        "expires_in": expires_in,
        "scope": scope,
    }
    monkeypatch.setattr(keycloak_client.httpx, "post", lambda *a, **kw: response)
    return response


def test_disabled_raises(monkeypatch):
    monkeypatch.setattr(settings, "kc_enabled", False, raising=False)
    client = KeycloakClient()
    with pytest.raises(KeycloakDisabledError):
        client.get_token()


def test_missing_secret_raises(monkeypatch):
    _enable_kc(monkeypatch, secret=None)
    client = KeycloakClient()
    with pytest.raises(KeycloakAuthError, match="not configured"):
        client.get_token()


def test_success_caches_token(monkeypatch):
    _enable_kc(monkeypatch)
    call_count = [0]

    def counting_post(*a, **kw):
        call_count[0] += 1
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {
            "access_token": f"tok-{call_count[0]}",
            "expires_in": 300,
            "scope": "grc:read",
        }
        return r

    monkeypatch.setattr(keycloak_client.httpx, "post", counting_post)
    client = KeycloakClient()
    assert client.get_token() == "tok-1"
    assert client.get_token() == "tok-1"
    assert call_count[0] == 1


def test_refresh_when_near_expiry(monkeypatch):
    _enable_kc(monkeypatch)
    _mock_token_response(monkeypatch, access_token="first", expires_in=300)
    client = KeycloakClient()
    client.get_token()
    client._cache.expires_at_epoch = time.time() + 5
    _mock_token_response(monkeypatch, access_token="second", expires_in=300)
    assert client.get_token() == "second"


def test_http_error_raises(monkeypatch):
    _enable_kc(monkeypatch)
    response = MagicMock()
    response.status_code = 401
    response.text = "unauthorized"
    monkeypatch.setattr(keycloak_client.httpx, "post", lambda *a, **kw: response)
    client = KeycloakClient()
    with pytest.raises(KeycloakAuthError, match="HTTP 401"):
        client.get_token()


def test_force_refresh_drops_cache(monkeypatch):
    _enable_kc(monkeypatch)
    _mock_token_response(monkeypatch, access_token="first", expires_in=300)
    client = KeycloakClient()
    client.get_token()
    _mock_token_response(monkeypatch, access_token="second", expires_in=300)
    assert client.force_refresh() == "second"


def test_token_url_construction(monkeypatch):
    _enable_kc(monkeypatch)
    monkeypatch.setattr(settings, "kc_base_url", "http://kc.test:8080/", raising=False)
    client = KeycloakClient()
    assert (
        client._token_url()
        == "http://kc.test:8080/realms/coredirective/protocol/openid-connect/token"
    )

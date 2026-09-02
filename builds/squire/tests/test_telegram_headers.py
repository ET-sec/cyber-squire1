"""The n8n webhook caller must present edge (Access) and app-layer credentials.

Without the Access service-token headers the edge answers 302 and the message
never reaches n8n; without the app-layer token the webhook node rejects it.
"""

from squire.tools.telegram import (
    CF_ACCESS_ID_ENV,
    CF_ACCESS_SECRET_ENV,
    WEBHOOK_TOKEN_HEADER,
    _n8n_headers,
)


def test_all_layers_present(monkeypatch):
    monkeypatch.setenv(CF_ACCESS_ID_ENV, "cid")
    monkeypatch.setenv(CF_ACCESS_SECRET_ENV, "csecret")
    h = _n8n_headers("app-token")
    assert h["CF-Access-Client-Id"] == "cid"
    assert h["CF-Access-Client-Secret"] == "csecret"
    assert h[WEBHOOK_TOKEN_HEADER] == "app-token"


def test_partial_access_pair_is_not_sent(monkeypatch):
    monkeypatch.setenv(CF_ACCESS_ID_ENV, "cid")
    monkeypatch.delenv(CF_ACCESS_SECRET_ENV, raising=False)
    h = _n8n_headers(None)
    assert "CF-Access-Client-Id" not in h
    assert WEBHOOK_TOKEN_HEADER not in h


def test_empty_token_means_no_header(monkeypatch):
    monkeypatch.delenv(CF_ACCESS_ID_ENV, raising=False)
    monkeypatch.delenv(CF_ACCESS_SECRET_ENV, raising=False)
    assert _n8n_headers("") == {}

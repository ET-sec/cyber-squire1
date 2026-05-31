"""Keycloak service-account token client for Squire (Phase 20 / JIT-CA Gate 2 scaffold).

Implements OAuth2 client_credentials flow against the squire realm client.
Caches the access token with expiry tracking and auto-refreshes when within
`kc_token_refresh_skew_seconds` of expiry.

Scope: token acquisition + caching only. Enforcement of "Squire must present
this token before calling any tool" is JIT-CA Gate 4 work and lives in the
OpenClaw gateway middleware, not here.

Usage:
    from .keycloak_client import get_kc_client
    client = get_kc_client()
    token = client.get_token()  # str, ready for "Authorization: Bearer <token>"
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

import httpx

from .settings import settings

log = logging.getLogger("squire.keycloak_client")


class KeycloakAuthError(RuntimeError):
    """Raised when Keycloak token acquisition fails."""


class KeycloakDisabledError(RuntimeError):
    """Raised when get_token() is called but kc_enabled is False."""


@dataclass
class _CachedToken:
    access_token: str
    expires_at_epoch: float
    scope: str


class KeycloakClient:
    """Service-account token client. Thread-safe via single refresh lock."""

    def __init__(self) -> None:
        self._cache: _CachedToken | None = None
        self._lock = threading.Lock()

    def _token_url(self) -> str:
        return (
            f"{settings.kc_base_url.rstrip('/')}"
            f"/realms/{settings.kc_realm}/protocol/openid-connect/token"
        )

    def _fetch_new_token(self) -> _CachedToken:
        if not settings.kc_enabled:
            raise KeycloakDisabledError("kc_enabled=False, refusing to fetch token")
        secret = settings.kc_client_secret
        if secret is None:
            raise KeycloakAuthError(
                "KC_CLIENT_SQUIRE_SECRET not configured but kc_enabled=True"
            )
        url = self._token_url()
        data = {
            "grant_type": "client_credentials",
            "client_id": settings.kc_client_id,
            "client_secret": secret.get_secret_value(),
        }
        t0 = time.monotonic()
        try:
            resp = httpx.post(url, data=data, timeout=10.0)
        except httpx.HTTPError as exc:
            raise KeycloakAuthError(f"token request failed: {exc}") from exc
        latency_ms = int((time.monotonic() - t0) * 1000)
        if resp.status_code != 200:
            raise KeycloakAuthError(
                f"token endpoint returned HTTP {resp.status_code}: {resp.text[:200]}"
            )
        body = resp.json()
        access_token = body.get("access_token")
        expires_in = body.get("expires_in")
        scope = body.get("scope", "")
        if not access_token or not isinstance(expires_in, int):
            raise KeycloakAuthError(
                "token endpoint response missing access_token or expires_in"
            )
        cached = _CachedToken(
            access_token=access_token,
            expires_at_epoch=time.time() + expires_in,
            scope=scope,
        )
        log.info(
            "kc.token.fetched",
            extra={
                "client_id": settings.kc_client_id,
                "expires_in_s": expires_in,
                "scope": scope,
                "latency_ms": latency_ms,
            },
        )
        return cached

    def get_token(self) -> str:
        """Return a valid access token. Refresh if within skew of expiry."""
        skew = settings.kc_token_refresh_skew_seconds
        with self._lock:
            now = time.time()
            if self._cache is not None and (self._cache.expires_at_epoch - now) > skew:
                return self._cache.access_token
            self._cache = self._fetch_new_token()
            return self._cache.access_token

    def force_refresh(self) -> str:
        """Drop cache and fetch a fresh token. Useful for tests and post-rotation."""
        with self._lock:
            self._cache = None
            self._cache = self._fetch_new_token()
            return self._cache.access_token


_client: KeycloakClient | None = None
_client_lock = threading.Lock()


def get_kc_client() -> KeycloakClient:
    """Process-wide singleton accessor."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = KeycloakClient()
    return _client

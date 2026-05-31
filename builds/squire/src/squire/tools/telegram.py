"""Telegram notification via n8n webhook (primary) or direct Bot API (fallback).

Routing preference (first success wins):
  1. n8n master-cmd webhook: POST {action,chat_id,text} to
     settings.telegram_webhook_url. n8n owns retries, DLQ, and audit trail.
  2. Direct Telegram Bot API: POST /bot{token}/sendMessage when
     TELEGRAM_BOT_TOKEN is present. Used when the n8n workflow is offline.

Fail-safe: on non-2xx or network failure for both paths, log + return
{"delivered": False, "error": "..."}. Never raises. The route_severity node
records the failure into state.errors so the FastAPI layer can surface it.
"""
from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger("squire.tools.telegram")

DEFAULT_TIMEOUT = 10.0
TELEGRAM_API_BASE = "https://api.telegram.org"


def _try_n8n_webhook(
    text: str,
    chat_id: str,
    webhook_url: str,
    timeout: float,
) -> dict[str, Any]:
    """POST to n8n master-cmd webhook."""
    import httpx

    payload = {"action": "telegram", "chat_id": chat_id, "text": text}
    with httpx.Client(timeout=timeout) as client:
        r = client.post(webhook_url, json=payload)
    status = r.status_code
    if 200 <= status < 300:
        return {"delivered": True, "status_code": status, "error": None, "via": "n8n"}
    return {
        "delivered": False,
        "status_code": status,
        "error": f"n8n_non_2xx: {status}",
        "via": "n8n",
    }


def _try_bot_api(
    text: str,
    chat_id: str,
    token: str,
    timeout: float,
) -> dict[str, Any]:
    """POST to Telegram Bot API /sendMessage."""
    import httpx

    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, json=payload)
    status = r.status_code
    if 200 <= status < 300:
        return {"delivered": True, "status_code": status, "error": None, "via": "bot_api"}
    return {
        "delivered": False,
        "status_code": status,
        "error": f"bot_api_non_2xx: {status}",
        "via": "bot_api",
    }


def telegram_notify(
    text: str,
    *,
    chat_id: str | None = None,
    webhook_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Best-effort Telegram notification.

    Args:
        text: message body (<=1000 chars preferred).
        chat_id: optional override; defaults to settings.telegram_chat_id.
        webhook_url: optional override; defaults to settings.telegram_webhook_url.
        timeout: HTTP timeout in seconds for each attempt.

    Returns:
        {
            "delivered": bool,
            "status_code": int | None,
            "error": str | None,
            "via": str | None,  # "n8n" | "bot_api" | None
        }

    Never raises. Tries n8n webhook first; on failure (or if the webhook is
    known-broken) falls back to Bot API when TELEGRAM_BOT_TOKEN is set.
    """
    # Local import to keep this module settings-free at module load time so
    # tests can patch settings without tripping pydantic.
    from ..settings import settings

    msg = (text or "").strip()
    if not msg:
        return {"delivered": False, "status_code": None, "error": "empty_text", "via": None}

    target_chat_id = chat_id or settings.telegram_chat_id
    target_url = webhook_url or settings.telegram_webhook_url
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    # 1. Try n8n webhook first.
    try:
        result = _try_n8n_webhook(msg, target_chat_id, target_url, timeout)
        if result["delivered"]:
            return result
        log.warning("n8n webhook failed (%s); trying Bot API fallback", result["error"])
        n8n_error = result["error"]
    except Exception as e:
        log.warning("n8n webhook exception: %s; trying Bot API fallback", e)
        n8n_error = f"exception: {e!s}"

    # 2. Fallback to direct Bot API.
    if not bot_token:
        return {
            "delivered": False,
            "status_code": None,
            "error": f"n8n_failed_and_no_bot_token: {n8n_error}",
            "via": None,
        }

    try:
        result = _try_bot_api(msg, target_chat_id, bot_token, timeout)
        if result["delivered"]:
            return result
        return {
            "delivered": False,
            "status_code": result["status_code"],
            "error": f"n8n_failed ({n8n_error}); bot_api_failed ({result['error']})",
            "via": "bot_api",
        }
    except Exception as e:
        return {
            "delivered": False,
            "status_code": None,
            "error": f"n8n_failed ({n8n_error}); bot_api_exception: {e!s}",
            "via": None,
        }

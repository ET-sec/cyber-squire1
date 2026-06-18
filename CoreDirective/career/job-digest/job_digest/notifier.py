"""Notification output: stdout and webhook delivery."""

import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


def notify_stdout(digest_text: str) -> None:
    """Print the formatted digest to stdout."""
    print(digest_text)


def notify_webhook(
    webhook_url: str,
    digest_text: str,
    postings: list[dict],
    timeout: int = 30,
) -> bool:
    """
    Send digest to a webhook endpoint via POST.

    Payload:
        {
            "text": "<formatted digest>",
            "postings": [<raw posting dicts>]
        }

    Args:
        webhook_url: The URL to POST to.
        digest_text: The formatted digest string.
        postings: List of raw posting dicts with all fields.
        timeout: Request timeout in seconds.

    Returns:
        True if the webhook accepted the payload, False otherwise.
    """
    # Strip non-serializable fields and limit payload size
    clean_postings = []
    for p in postings:
        clean = {
            "id": p.get("id"),
            "source": p.get("source", ""),
            "title": p.get("title", ""),
            "company": p.get("company", ""),
            "location": p.get("location", ""),
            "salary": p.get("salary", ""),
            "url": p.get("url", ""),
            "score": p.get("score", 0),
            "matched_certs": p.get("matched_certs", []),
            "date_found": p.get("date_found", ""),
        }
        clean_postings.append(clean)

    payload = {
        "text": digest_text,
        "postings": clean_postings,
        "count": len(clean_postings),
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        if response.status_code < 300:
            logger.info("Webhook delivered successfully (HTTP %d)", response.status_code)
            return True
        else:
            logger.warning(
                "Webhook returned HTTP %d: %s",
                response.status_code,
                response.text[:500],
            )
            return False
    except requests.exceptions.Timeout:
        logger.error("Webhook request timed out after %ds", timeout)
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error("Webhook connection error: %s", str(e)[:200])
        return False
    except Exception as e:
        logger.error("Webhook delivery failed: %s", str(e)[:200])
        return False


def notify(
    digest_text: str,
    postings: list[dict],
    send: bool = False,
    webhook_url: Optional[str] = None,
) -> None:
    """
    Main notification dispatcher.

    Always prints to stdout. If send=True and webhook_url is provided,
    also delivers via webhook.
    """
    notify_stdout(digest_text)

    if send and webhook_url:
        print(f"\nSending to webhook: {webhook_url}")
        success = notify_webhook(webhook_url, digest_text, postings)
        if success:
            print("Webhook delivery: SUCCESS")
        else:
            print("Webhook delivery: FAILED (check logs)")
    elif send and not webhook_url:
        print("\n--send flag provided but no webhook URL configured.")
        print("Set webhook_url in config.yaml or pass --webhook <URL>")

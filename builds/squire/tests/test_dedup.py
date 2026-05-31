"""Unit tests for signature computation (no live Redis required)."""
import os

os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from squire.dedup import signature  # noqa: E402


def test_same_alert_same_signature():
    a = {
        "rule": "Terminal shell in container",
        "priority": "Notice",
        "output_fields": {"container.id": "x"},
    }
    b = dict(a)
    assert signature(a) == signature(b)


def test_different_resource_different_signature():
    a = {"rule": "shell", "priority": "Notice", "output_fields": {"container.id": "A"}}
    b = {"rule": "shell", "priority": "Notice", "output_fields": {"container.id": "B"}}
    assert signature(a) != signature(b)


def test_signature_is_stable_hex():
    s = signature({"rule": "x"})
    assert len(s) == 32
    int(s, 16)  # must parse as hex


def test_signature_handles_empty_alert():
    s = signature({})
    assert len(s) == 32

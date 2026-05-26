"""Shared utilities: structured JSON logging, secret handling, path confinement.

Kept private (leading underscore) so observers import from here but external
callers go through `verify-facts.py` and the public Observer ABC.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Refuse to run as root
# ---------------------------------------------------------------------------
if os.geteuid() == 0:
    print("verify-facts: refuse to run as root", file=sys.stderr)
    sys.exit(5)

# ---------------------------------------------------------------------------
# Secret allowlist (extend only when a new field needs a new secret)
# ---------------------------------------------------------------------------
_SECRETS_SEEN: set[str] = set()
_ALLOWED_SECRET_KEYS = {"CD_DB_USER", "CD_DB_PASS", "CD_DB_NAME", "CD_N8N_KEY"}


def minimal_env() -> dict[str, str]:
    """Strip env for subprocesses to prevent secret leak to children."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", ""),
        "LANG": "C.UTF-8",
    }


def get_secret(key: str) -> str:
    """Fetch a secret from Doppler. Hard-fail on unauthorized keys (exit 4)."""
    if not re.fullmatch(r"^[A-Z][A-Z0-9_]{2,40}$", key):
        raise ValueError("bad secret key shape")
    if key not in _ALLOWED_SECRET_KEYS:
        raise PermissionError(f"secret key not in allowlist: {key}")
    override = os.environ.get(f"TEST_{key}")
    if override:
        _SECRETS_SEEN.add(override)
        return override
    try:
        r = subprocess.run(
            [
                "doppler", "secrets", "get", key, "--plain",
                "--project", "coredirective-engine", "--config", "prd",
            ],
            capture_output=True, text=True, check=True, timeout=10,
            env=minimal_env(), shell=False,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        sys.exit(4)
    val = r.stdout.strip()
    if not val:
        sys.exit(4)
    _SECRETS_SEEN.add(val)
    return val


def secrets_seen() -> set[str]:
    """For RedactFilter and public-output redaction."""
    return _SECRETS_SEEN


# ---------------------------------------------------------------------------
# Path confinement (CWE-22, CWE-59)
# ---------------------------------------------------------------------------
def safe_under(child: Path, parent: Path) -> Path:
    """Reject path traversal and symlinks."""
    if child.is_symlink():
        raise PermissionError(f"symlink rejected: {child}")
    r = child.resolve(strict=True)
    parent_r = parent.resolve()
    if not r.is_relative_to(parent_r):
        raise PermissionError(f"path escape: {r} not under {parent_r}")
    return r


# ---------------------------------------------------------------------------
# Structured JSON logging to stderr
# ---------------------------------------------------------------------------
def _safe_log_str(s: str) -> str:
    return s.replace("\r", "\\r").replace("\n", "\\n")[:512]


class RedactFilter(logging.Filter):
    """Replace seen secret values in log records with [REDACTED]."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        for s in list(_SECRETS_SEEN):
            if s and len(s) >= 8 and s in msg:
                record.msg = msg.replace(s, "[REDACTED]")
                record.args = ()
        return True


class JsonFormatter(logging.Formatter):
    def __init__(self, script_name: str, version: str) -> None:
        super().__init__()
        self.script_name = script_name
        self.version = version

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "script": self.script_name,
            "ver": self.version,
            "evt": getattr(record, "evt", "log"),
            "msg": _safe_log_str(record.getMessage()),
            "pid": os.getpid(),
        }
        for k, v in getattr(record, "extra_fields", {}).items():
            payload[k] = v
        return json.dumps(payload, ensure_ascii=False)


_LOGGER: logging.Logger | None = None


def configure_logger(script_name: str = "verify-facts", version: str = "0.1.0") -> logging.Logger:
    """Idempotent logger setup. First call wins."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER
    lg = logging.getLogger(script_name)
    lg.setLevel(logging.INFO)
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(JsonFormatter(script_name, version))
    lg.addHandler(h)
    lg.addFilter(RedactFilter())
    lg.propagate = False
    _LOGGER = lg
    return lg


def log(evt: str, level: int = logging.INFO, **fields: Any) -> None:
    """Emit a structured log line. Logger must be configured first."""
    lg = configure_logger()
    rec = logging.LogRecord(lg.name, level, "", 0, evt, None, None)
    rec.evt = evt
    rec.extra_fields = fields
    lg.handle(rec)


# ---------------------------------------------------------------------------
# SSH option helpers (regex-gated target)
# ---------------------------------------------------------------------------
def ssh_opts(target: str) -> list[str]:
    if not re.fullmatch(r"^cd-alpha$", target):
        sys.exit(2)
    return [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "ConnectTimeout=10",
        "-o", "ServerAliveInterval=5",
        target,
    ]

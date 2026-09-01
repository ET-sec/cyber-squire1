#!/usr/bin/env python3
"""verify-facts.py
Drift detector for stack-facts.yaml SSOT (plugin core).

Loads observers from `scripts/observers/`, dispatches each, aggregates drift
output. Adding a new fact family means dropping a new observer module into
the package, not editing this file.

Exit codes (do not collapse, n8n branches on these):
  0  clean
  1  drift detected
  2  input validation failure
  3  external dependency failure (ssh / postgres / n8n unreachable)
  4  secret retrieval failure (Doppler missing or unauthorized)
  5  internal error / unhandled exception
  6  policy violation (would leak secret, path escape)

Spec: .planning/sessions/2026-05-25-script-security-requirements.md
Refactor: .planning/sessions/2026-05-25-next-session-roadmap.md (Step 1 of 7)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Make `observers` importable when verify-facts.py is invoked directly.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from observers import load_all  # noqa: E402
from observers.base import Context, Drift  # noqa: E402
from observers._common import configure_logger, log, secrets_seen  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_DIR = Path("/Users/et/cyber-squire-ops").resolve()
FACTS_FILE = BASE_DIR / ".facts" / "stack-facts.yaml"
VERSION = "0.2.0"  # bump for plugin refactor

configure_logger(script_name="verify-facts", version=VERSION)


# ---------------------------------------------------------------------------
# Pydantic schema (unchanged from v0.1.0)
# ---------------------------------------------------------------------------
class Meta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(pattern=r"^\d+\.\d+$")
    last_verified: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    verifier_version: str
    source_of_truth_rank: list[str]


class Identity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str
    title_primary: str
    title_org: str
    location: str
    email_primary: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")
    github_handle: str = Field(pattern=r"^[A-Za-z0-9\-]+$")
    portfolio_url: str = Field(pattern=r"^https://")
    brand_url: str = Field(pattern=r"^https://")
    linkedin_url: str = Field(pattern=r"^https://")


class Cloud(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    status: str
    tf_directory: str


class Infrastructure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clouds: list[Cloud]
    containers_running: int = Field(ge=0, le=200)
    containers_total: int = Field(ge=0, le=200)
    containers_exited: list[str]
    verified_via: str
    terraform_files: int = Field(ge=0, le=500)
    terraform_dir: str
    terraform_resources_approx: str
    verified_via_terraform: str
    opa_rego_policies: int = Field(ge=0, le=100)
    opa_dir: str
    verified_via_opa: str
    zero_exposed_ports: bool
    ingress_path: str
    tunnel_routes: list[str]


class Soar(BaseModel):
    model_config = ConfigDict(extra="forbid")
    platform: str
    workflows_active: int = Field(ge=0, le=200)
    workflows_total: int = Field(ge=0, le=200)
    workflows_named: list[str]
    master_orchestrator_actions: int = Field(ge=0, le=100)
    secrets_managed: str
    hours_freed_per_week_estimate: str
    verified_via: str


class StackFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    identity: Identity
    infrastructure: Infrastructure
    soar: Soar
    ai_security: dict
    detection: dict
    iam: dict
    ci_cd: dict
    grc: dict
    certs: dict
    education: dict
    experience_prior: dict
    drift_alerts: list = Field(default_factory=list)
    deferred_for_next_session: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# YAML load with validation
# ---------------------------------------------------------------------------
def load_facts(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    try:
        data = yaml.safe_load(raw.decode("utf-8"))
    except yaml.YAMLError as e:
        log("fact.load.error", logging.ERROR, error=type(e).__name__)
        sys.exit(2)
    if not isinstance(data, dict):
        log("fact.load.error", logging.ERROR, error="not a mapping")
        sys.exit(2)
    try:
        StackFacts(**data)
    except ValidationError as e:
        log("fact.schema.invalid", logging.ERROR, errors=str(e)[:1000])
        sys.exit(2)
    log("fact.read", src=str(path), sha256=sha)
    return data, sha


# ---------------------------------------------------------------------------
# Path confinement for --facts arg
# ---------------------------------------------------------------------------
def _safe_facts_path(candidate: Path) -> Path:
    if candidate.is_symlink():
        raise PermissionError(f"symlink rejected: {candidate}")
    r = candidate.resolve(strict=True)
    parent = (BASE_DIR / ".facts").resolve()
    if not r.is_relative_to(parent):
        raise PermissionError(f"path escape: {r} not under {parent}")
    return r


# ---------------------------------------------------------------------------
# Public-safe redaction
# ---------------------------------------------------------------------------
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def redact_for_public(s: str) -> str:
    out = s
    for sec in secrets_seen():
        if sec and len(sec) >= 8:
            out = out.replace(sec, "[REDACTED]")
    out = IP_RE.sub("[IP]", out)
    out = out.replace("tigouetheory.com", "[DOMAIN]")
    out = out.replace("cd-alpha", "[HOST]").replace("cd-oci", "[HOST]")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Drift detector for stack-facts.yaml")
    parser.add_argument("--facts", type=Path, default=FACTS_FILE)
    parser.add_argument("--ssh-target", default="cd-oci")
    parser.add_argument("--json", action="store_true", help="emit JSON drift report")
    parser.add_argument("--public", action="store_true", help="redact secrets/IPs from stdout")
    parser.add_argument("--skip-remote", action="store_true", help="skip ssh/postgres checks")
    args = parser.parse_args()

    log("script.start",
        argv=[a for a in sys.argv if not a.startswith("--password")],
        cwd=os.getcwd(), user=os.environ.get("USER", "unknown"))

    # Validate inputs
    try:
        facts_path = _safe_facts_path(args.facts)
    except (PermissionError, FileNotFoundError) as e:
        log("input.validation.failed", logging.ERROR, error=str(e))
        return 2
    if not re.fullmatch(r"^cd-(alpha|oci)$", args.ssh_target):
        return 2

    data, sha = load_facts(facts_path)

    ctx = Context(
        base_dir=BASE_DIR,
        facts=data,
        ssh_target=args.ssh_target,
        skip_remote=args.skip_remote,
    )

    # Dispatch observers
    drifts: list[Drift] = []
    for obs in load_all(include_remote=not args.skip_remote):
        try:
            result = obs.observe(ctx)
        except SystemExit:
            raise
        except Exception as e:
            log("observer.crash", logging.ERROR, observer=obs.name, error=type(e).__name__)
            return 5
        drifts.extend(result)
        for d in result:
            log("drift.detected", logging.WARNING, key=d.key,
                expected=str(d.yaml)[:80], actual=str(d.real)[:80])

    # Output
    if args.json:
        payload: dict[str, Any] = {
            "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "facts_sha256": sha,
            "drift_count": len(drifts),
            "drifts": [d.as_dict() for d in drifts],
        }
        out = json.dumps(payload, indent=2, sort_keys=True, default=str)
        print(redact_for_public(out) if args.public else out)
    else:
        if not drifts:
            print("OK - no drift detected")
        else:
            header = f"DRIFT - {len(drifts)} field(s)"
            lines = [header, "=" * len(header)]
            for d in drifts:
                lines.append(f"  {d.key}:")
                lines.append(f"    yaml: {d.yaml!r}")
                lines.append(f"    real: {d.real!r}")
            out = "\n".join(lines)
            print(redact_for_public(out) if args.public else out)

    exit_code = 1 if drifts else 0
    log("script.end", exit_code=exit_code)
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        log("script.crash", logging.ERROR, error=type(e).__name__)
        sys.exit(5)

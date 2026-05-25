#!/usr/bin/env python3
"""verify-facts.py
Drift detector for stack-facts.yaml SSOT.

Reads /Users/et/cyber-squire-ops/.facts/stack-facts.yaml, walks filesystem,
queries droplet, diffs reality vs yaml.

Exit codes (do not collapse, n8n branches on these):
  0  clean
  1  drift detected
  2  input validation failure
  3  external dependency failure (ssh / postgres / n8n unreachable)
  4  secret retrieval failure (Doppler missing or unauthorized)
  5  internal error / unhandled exception
  6  policy violation (would leak secret, path escape)

Spec: .planning/sessions/2026-05-25-script-security-requirements.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import datetime as dt
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
BASE_DIR = Path("/Users/et/cyber-squire-ops").resolve()
FACTS_FILE = BASE_DIR / ".facts" / "stack-facts.yaml"
ALLOWED_GRC = BASE_DIR / "docs" / "grc"
ALLOWED_TF = BASE_DIR / "terraform" / "cd-do-infrastructure"
ALLOWED_TF_ROOT = BASE_DIR / "terraform"
ALLOWED_AGENTS = BASE_DIR / "Agent_Squire" / "agents"

VERSION = "0.1.0"

# Refuse to run as root
if os.geteuid() == 0:
    print("verify-facts: refuse to run as root", file=sys.stderr)
    sys.exit(5)

# ---------------------------------------------------------------------------
# Secret handling (Doppler only, scrubbed from logs)
# ---------------------------------------------------------------------------
_SECRETS_SEEN: set[str] = set()
_ALLOWED_SECRET_KEYS = {"CD_DB_USER", "CD_DB_PASS", "CD_DB_NAME", "CD_N8N_KEY"}


def _minimal_env() -> dict[str, str]:
    """Strip env when invoking subprocesses to prevent secret leak to children."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", ""),
        "LANG": "C.UTF-8",
    }


def _get_secret(key: str) -> str:
    """Fetch a secret from Doppler. Hard-fail on unauthorized keys."""
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
            env=_minimal_env(), shell=False,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        sys.exit(4)
    val = r.stdout.strip()
    if not val:
        sys.exit(4)
    _SECRETS_SEEN.add(val)
    return val


class RedactFilter(logging.Filter):
    """Replace any seen secret value in log records with [REDACTED]."""

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


# ---------------------------------------------------------------------------
# Structured JSON logging to stderr
# ---------------------------------------------------------------------------
def _safe_log_str(s: str) -> str:
    return s.replace("\r", "\\r").replace("\n", "\\n")[:512]


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "script": "verify-facts",
            "ver": VERSION,
            "evt": getattr(record, "evt", "log"),
            "msg": _safe_log_str(record.getMessage()),
            "pid": os.getpid(),
        }
        for k, v in getattr(record, "extra_fields", {}).items():
            payload[k] = v
        return json.dumps(payload, ensure_ascii=False)


def _log(evt: str, level: int = logging.INFO, **fields: Any) -> None:
    rec = logging.LogRecord("verify-facts", level, "", 0, evt, None, None)
    rec.evt = evt
    rec.extra_fields = fields
    LOGGER.handle(rec)


LOGGER = logging.getLogger("verify-facts")
LOGGER.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(JsonFormatter())
LOGGER.addHandler(_handler)
LOGGER.addFilter(RedactFilter())
LOGGER.propagate = False


# ---------------------------------------------------------------------------
# Pydantic schema for stack-facts.yaml
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
    """Top-level schema. extra=forbid means unknown keys are drift, not features."""
    model_config = ConfigDict(extra="forbid")
    meta: Meta
    identity: Identity
    infrastructure: Infrastructure
    soar: Soar
    ai_security: dict  # nested, validated lightly for now
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
# Path confinement
# ---------------------------------------------------------------------------
def safe_under(child: Path, parent: Path) -> Path:
    """Reject path traversal and symlinks. CWE-22, CWE-59."""
    if child.is_symlink():
        raise PermissionError(f"symlink rejected: {child}")
    r = child.resolve(strict=True)
    parent_r = parent.resolve()
    if not r.is_relative_to(parent_r):
        raise PermissionError(f"path escape: {r} not under {parent_r}")
    return r


# ---------------------------------------------------------------------------
# YAML load with validation
# ---------------------------------------------------------------------------
def load_facts(path: Path) -> tuple[dict, str]:
    """Load facts yaml. Validate. Return (data, sha256)."""
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    try:
        data = yaml.safe_load(raw.decode("utf-8"))
    except yaml.YAMLError as e:
        _log("fact.load.error", logging.ERROR, error=type(e).__name__)
        sys.exit(2)
    if not isinstance(data, dict):
        _log("fact.load.error", logging.ERROR, error="not a mapping")
        sys.exit(2)
    try:
        StackFacts(**data)
    except ValidationError as e:
        _log("fact.schema.invalid", logging.ERROR, errors=str(e)[:1000])
        sys.exit(2)
    _log("fact.read", src=str(path), sha256=sha)
    return data, sha


# ---------------------------------------------------------------------------
# Reality observations
# ---------------------------------------------------------------------------
def observe_grc_docs() -> int:
    """Count .md files in docs/grc/ top-level only."""
    start = dt.datetime.now()
    p = safe_under(ALLOWED_GRC, BASE_DIR)
    count = sum(1 for _ in p.glob("*.md"))
    dur = int((dt.datetime.now() - start).total_seconds() * 1000)
    _log("observation.fs", root=str(p), file_count=count, duration_ms=dur)
    return count


def observe_terraform_files() -> int:
    """Count .tf files in terraform/cd-do-infrastructure/ top-level only."""
    p = safe_under(ALLOWED_TF, BASE_DIR)
    count = sum(1 for _ in p.glob("*.tf"))
    _log("observation.fs", root=str(p), file_count=count, pattern="*.tf")
    return count


def observe_opa_policies() -> int:
    """Count .rego files under terraform/ recursively."""
    p = safe_under(ALLOWED_TF_ROOT, BASE_DIR)
    count = sum(1 for _ in p.rglob("*.rego") if not _.is_symlink())
    _log("observation.fs", root=str(p), file_count=count, pattern="*.rego")
    return count


def observe_squire_agents() -> list[str]:
    """List subdirs of Agent_Squire/agents/."""
    p = safe_under(ALLOWED_AGENTS, BASE_DIR)
    agents = sorted([d.name for d in p.iterdir() if d.is_dir() and not d.is_symlink()])
    _log("observation.fs", root=str(p), file_count=len(agents))
    return agents


def observe_ir_playbooks() -> int:
    """Count PLAYBOOK_*.md in docs/grc/."""
    p = safe_under(ALLOWED_GRC, BASE_DIR)
    count = sum(1 for _ in p.glob("PLAYBOOK_*.md"))
    _log("observation.fs", root=str(p), file_count=count, pattern="PLAYBOOK_*.md")
    return count


def _ssh_opts(target: str) -> list[str]:
    return [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "ConnectTimeout=10",
        "-o", "ServerAliveInterval=5",
        target,
    ]


def observe_droplet_containers(ssh_target: str) -> tuple[int, int]:
    """Return (running, total) container count via ssh + docker ps.

    The remote command is passed as a single shell-quoted string so the
    remote shell sees the docker template literal `{{json .}}` correctly.
    subprocess shell=False is preserved on the local side.
    """
    if not re.fullmatch(r"^cd-alpha$", ssh_target):
        sys.exit(2)
    try:
        running = subprocess.run(
            _ssh_opts(ssh_target) + ["docker ps --format '{{json .}}'"],
            capture_output=True, text=True, timeout=30, check=True,
            shell=False, env=_minimal_env(),
        )
        total = subprocess.run(
            _ssh_opts(ssh_target) + ["docker ps -a --format '{{json .}}'"],
            capture_output=True, text=True, timeout=30, check=True,
            shell=False, env=_minimal_env(),
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        _log("observation.ssh.error", logging.ERROR, error=type(e).__name__,
             stderr=getattr(e, "stderr", "")[:200] if hasattr(e, "stderr") else "")
        sys.exit(3)
    run_count = sum(1 for line in running.stdout.splitlines() if line.strip())
    tot_count = sum(1 for line in total.stdout.splitlines() if line.strip())
    _log("observation.ssh", target=ssh_target, cmd_basename="docker ps", exit=0)
    return run_count, tot_count


def observe_n8n_workflows(ssh_target: str) -> tuple[int, int]:
    """Query Postgres on droplet for n8n workflow counts. Returns (total, active).

    User and db names are regex-validated before being interpolated into the
    SQL invocation; query text is constant. Postgres user is the read-only
    role used by n8n itself.
    """
    user = _get_secret("CD_DB_USER")
    db = _get_secret("CD_DB_NAME")
    if not re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{1,40}$", user):
        sys.exit(4)
    if not re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{1,40}$", db):
        sys.exit(4)
    sql = "SELECT COUNT(*), COUNT(*) FILTER (WHERE active=true) FROM workflow_entity;"
    remote = (
        f"docker exec cd-service-db psql -U {user} -d {db} -t -A -c "
        + json.dumps(sql)  # safe shell quoting via JSON
    )
    try:
        r = subprocess.run(
            _ssh_opts(ssh_target) + [remote],
            capture_output=True, text=True, timeout=20, check=True,
            shell=False, env=_minimal_env(),
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        _log("observation.pg.error", logging.ERROR, error=type(e).__name__,
             stderr=getattr(e, "stderr", "")[:200] if hasattr(e, "stderr") else "")
        sys.exit(3)
    line = r.stdout.strip()
    m = re.fullmatch(r"^(\d+)\|(\d+)$", line)
    if not m:
        _log("observation.pg.parse_fail", logging.ERROR, raw=line[:80])
        sys.exit(3)
    total, active = int(m.group(1)), int(m.group(2))
    _log("observation.pg", query_id="n8n_workflow_counts", row_count=2)
    return total, active


# ---------------------------------------------------------------------------
# Drift comparison
# ---------------------------------------------------------------------------
def compare(yaml_value: Any, real_value: Any, key: str) -> dict | None:
    if yaml_value == real_value:
        return None
    diff = {"key": key, "yaml": yaml_value, "real": real_value}
    _log("drift.detected", logging.WARNING, key=key,
         expected=str(yaml_value)[:80], actual=str(real_value)[:80])
    return diff


# ---------------------------------------------------------------------------
# Public-safe redaction for stdout
# ---------------------------------------------------------------------------
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def redact_for_public(s: str) -> str:
    out = s
    for sec in _SECRETS_SEEN:
        if sec and len(sec) >= 8:
            out = out.replace(sec, "[REDACTED]")
    out = IP_RE.sub("[IP]", out)
    out = out.replace("tigouetheory.com", "[DOMAIN]")
    out = out.replace("cd-alpha", "[HOST]")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Drift detector for stack-facts.yaml")
    parser.add_argument("--facts", type=Path, default=FACTS_FILE)
    parser.add_argument("--ssh-target", default="cd-alpha")
    parser.add_argument("--json", action="store_true", help="emit JSON drift report")
    parser.add_argument("--public", action="store_true", help="redact secrets/IPs from stdout")
    parser.add_argument("--skip-remote", action="store_true", help="skip ssh/postgres checks")
    args = parser.parse_args()

    _log("script.start", argv=[a for a in sys.argv if not a.startswith("--password")],
         cwd=os.getcwd(), user=os.environ.get("USER", "unknown"))

    # Validate inputs
    try:
        facts_path = safe_under(args.facts, BASE_DIR / ".facts")
    except (PermissionError, FileNotFoundError) as e:
        _log("input.validation.failed", logging.ERROR, error=str(e))
        return 2
    if not re.fullmatch(r"^cd-alpha$", args.ssh_target):
        return 2

    data, _sha = load_facts(facts_path)

    drifts: list[dict] = []

    # Filesystem observations
    drifts.append(compare(data["grc"]["total_documents"], observe_grc_docs(), "grc.total_documents"))
    drifts.append(compare(data["infrastructure"]["terraform_files"], observe_terraform_files(),
                          "infrastructure.terraform_files"))
    drifts.append(compare(data["infrastructure"]["opa_rego_policies"], observe_opa_policies(),
                          "infrastructure.opa_rego_policies"))
    drifts.append(compare(data["grc"]["ir_playbooks"], observe_ir_playbooks(), "grc.ir_playbooks"))

    yaml_agents = sorted(a["id"] for a in data["ai_security"]["agents"])
    real_agents = observe_squire_agents()
    drifts.append(compare(yaml_agents, real_agents, "ai_security.agents"))

    # Remote observations
    if not args.skip_remote:
        try:
            running, total = observe_droplet_containers(args.ssh_target)
            drifts.append(compare(data["infrastructure"]["containers_running"], running,
                                  "infrastructure.containers_running"))
            drifts.append(compare(data["infrastructure"]["containers_total"], total,
                                  "infrastructure.containers_total"))
            wf_total, wf_active = observe_n8n_workflows(args.ssh_target)
            drifts.append(compare(data["soar"]["workflows_total"], wf_total, "soar.workflows_total"))
            drifts.append(compare(data["soar"]["workflows_active"], wf_active, "soar.workflows_active"))
        except SystemExit:
            raise
        except Exception as e:
            _log("observation.remote.error", logging.ERROR, error=type(e).__name__)
            return 3

    drifts = [d for d in drifts if d is not None]

    # Output
    if args.json:
        payload = {
            "verified_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "facts_sha256": _sha,
            "drift_count": len(drifts),
            "drifts": drifts,
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
                lines.append(f"  {d['key']}:")
                lines.append(f"    yaml: {d['yaml']!r}")
                lines.append(f"    real: {d['real']!r}")
            out = "\n".join(lines)
            print(redact_for_public(out) if args.public else out)

    exit_code = 1 if drifts else 0
    _log("script.end", exit_code=exit_code)
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        _log("script.crash", logging.ERROR, error=type(e).__name__)
        sys.exit(5)

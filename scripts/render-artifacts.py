#!/usr/bin/env python3
"""render-artifacts.py
Render Jinja2 templates from stack-facts.yaml into artifacts/.

Reads /Users/et/cyber-squire-ops/.facts/stack-facts.yaml,
renders /Users/et/cyber-squire-ops/templates/<allowed>.j2,
writes /Users/et/cyber-squire-ops/artifacts/<allowed-output>.

Exit codes match verify-facts.py:
  0  success
  2  input validation failure (bad template name, missing key, etc.)
  5  internal error
  6  policy violation (secret in output, path escape)

Spec: .planning/sessions/2026-05-25-script-security-requirements.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import signal
import subprocess
import sys
import datetime as dt
from pathlib import Path

import yaml
from jinja2 import FileSystemLoader, StrictUndefined, select_autoescape
from jinja2.sandbox import SandboxedEnvironment

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path("/Users/et/cyber-squire-ops").resolve()
FACTS_FILE = BASE_DIR / ".facts" / "stack-facts.yaml"
TEMPLATE_DIR = BASE_DIR / "templates"
ARTIFACT_DIR = BASE_DIR / "artifacts"
VERSION = "0.1.0"

if os.geteuid() == 0:
    print("render-artifacts: refuse to run as root", file=sys.stderr)
    sys.exit(5)

# ---------------------------------------------------------------------------
# Template allowlist
# ---------------------------------------------------------------------------
TEMPLATE_ALLOWLIST: dict[str, str] = {
    "linkedin-about.md.j2": "linkedin-about.md",
}

# ---------------------------------------------------------------------------
# Secret patterns
# ---------------------------------------------------------------------------
SECRET_REGEXES = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"xoxb-[0-9A-Za-z\-]{20,}"),
    re.compile(r"dp\.pt\.[A-Za-z0-9]{30,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def _safe_log_str(s: str) -> str:
    return s.replace("\r", "\\r").replace("\n", "\\n")[:512]


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "script": "render-artifacts",
            "ver": VERSION,
            "evt": getattr(record, "evt", "log"),
            "msg": _safe_log_str(record.getMessage()),
            "pid": os.getpid(),
        }
        payload.update(getattr(record, "extra_fields", {}))
        return json.dumps(payload, ensure_ascii=False)


LOGGER = logging.getLogger("render-artifacts")
LOGGER.setLevel(logging.INFO)
_h = logging.StreamHandler(sys.stderr)
_h.setFormatter(JsonFormatter())
LOGGER.addHandler(_h)
LOGGER.propagate = False


def _log(evt: str, level: int = logging.INFO, **fields) -> None:
    rec = logging.LogRecord("render-artifacts", level, "", 0, evt, None, None)
    rec.evt = evt
    rec.extra_fields = fields
    LOGGER.handle(rec)


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------
def safe_under(child: Path, parent: Path, must_exist: bool = True) -> Path:
    """Block path traversal and symlinks."""
    if child.exists() and child.is_symlink():
        raise PermissionError(f"symlink rejected: {child}")
    r = child.resolve(strict=must_exist)
    parent_r = parent.resolve()
    if not r.is_relative_to(parent_r):
        raise PermissionError(f"path escape: {r}")
    return r


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------
def git_rev() -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(BASE_DIR), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
            shell=False, env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "unknown"


def make_footer(yaml_sha: str) -> str:
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rev = git_rev()
    return (
        f"\n\n<!-- generated: {ts} -->\n"
        f"<!-- source-sha256: {yaml_sha} -->\n"
        f"<!-- generator: render-artifacts.py v{VERSION} -->\n"
        f"<!-- git-rev: {rev} -->\n"
    )


# ---------------------------------------------------------------------------
# Secret scan
# ---------------------------------------------------------------------------
def secret_scan(text: str) -> str | None:
    for rx in SECRET_REGEXES:
        m = rx.search(text)
        if m:
            return rx.pattern
    return None


# ---------------------------------------------------------------------------
# Wall-clock alarm
# ---------------------------------------------------------------------------
def _alarm_handler(signum, frame):
    _log("render.timeout", logging.ERROR)
    sys.exit(5)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------
def render(template_name: str, facts_path: Path) -> int:
    if template_name not in TEMPLATE_ALLOWLIST:
        _log("template.not_allowed", logging.ERROR, template=template_name)
        return 2
    if not re.fullmatch(r"^[a-z0-9][a-z0-9\-]{1,40}\.(md|json|html)\.j2$", template_name):
        _log("template.bad_name", logging.ERROR, template=template_name)
        return 2

    facts_raw = facts_path.read_bytes()
    yaml_sha = hashlib.sha256(facts_raw).hexdigest()
    try:
        facts = yaml.safe_load(facts_raw.decode("utf-8"))
    except yaml.YAMLError:
        _log("facts.load.error", logging.ERROR)
        return 2
    if not isinstance(facts, dict):
        return 2

    _log("facts.read", src=str(facts_path), sha256=yaml_sha)

    # Autoescape: ON for html/xml (XSS protection), OFF for md/json/txt
    # (sandbox + StrictUndefined still apply; data source is our own yaml).
    env = SandboxedEnvironment(
        loader=FileSystemLoader(str(TEMPLATE_DIR), followlinks=False),
        autoescape=select_autoescape(
            enabled_extensions=("html", "htm", "xml"),
            default_for_string=False,
            default=False,
        ),
        undefined=StrictUndefined,
        auto_reload=False,
        cache_size=0,
    )

    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(30)
    try:
        try:
            tpl = env.get_template(template_name)
        except Exception as e:
            _log("template.load.error", logging.ERROR, error=type(e).__name__)
            return 2
        try:
            rendered = tpl.render(facts=facts)
        except Exception as e:
            _log("template.render.error", logging.ERROR, error=type(e).__name__, msg=str(e)[:200])
            return 2
    finally:
        signal.alarm(0)

    # Secret scan BEFORE writing
    leak = secret_scan(rendered)
    if leak:
        _log("secret.scan", logging.ERROR, result="blocked", pattern=leak)
        return 6
    _log("secret.scan", result="clean")

    # Compute output path
    out_name = TEMPLATE_ALLOWLIST[template_name]
    out_path = ARTIFACT_DIR / out_name
    try:
        out_resolved = safe_under(out_path, ARTIFACT_DIR, must_exist=False)
    except PermissionError as e:
        _log("output.path.escape", logging.ERROR, error=str(e))
        return 6

    # Append provenance footer (md only)
    if out_name.endswith(".md"):
        rendered = rendered.rstrip() + make_footer(yaml_sha)

    # Atomic write
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = out_resolved.with_suffix(out_resolved.suffix + ".tmp")
    tmp.write_text(rendered, encoding="utf-8")
    os.chmod(tmp, 0o644)
    os.replace(tmp, out_resolved)

    out_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
    _log("artifact.rendered", template=template_name, output_path=str(out_resolved),
         output_sha256=out_sha, bytes=len(rendered.encode("utf-8")))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Render artifacts from stack-facts.yaml")
    parser.add_argument("--facts", type=Path, default=FACTS_FILE)
    parser.add_argument("--template", type=str, default=None,
                        help="If omitted, renders ALL allowed templates")
    args = parser.parse_args()

    _log("script.start", argv=sys.argv, cwd=os.getcwd(),
         user=os.environ.get("USER", "unknown"))

    try:
        facts_path = safe_under(args.facts, BASE_DIR / ".facts")
    except (PermissionError, FileNotFoundError) as e:
        _log("input.validation.failed", logging.ERROR, error=str(e))
        return 2

    targets: list[str]
    if args.template:
        if not re.fullmatch(r"^[a-z0-9][a-z0-9\-]{1,40}\.(md|json|html)\.j2$", args.template):
            return 2
        targets = [args.template]
    else:
        targets = list(TEMPLATE_ALLOWLIST.keys())

    final = 0
    for t in targets:
        rc = render(t, facts_path)
        if rc != 0:
            final = rc
            _log("render.failed", logging.ERROR, template=t, exit_code=rc)
            # continue rendering others to surface all failures
    _log("script.end", exit_code=final)
    return final


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        _log("script.crash", logging.ERROR, error=type(e).__name__)
        sys.exit(5)

#!/usr/bin/env python3
"""Diffs the repository manifest (``docs/REPO_MANIFEST.yaml``) against the
tracked tree. Flags shadow paths (tracked but carrying no manifest row),
orphan rows (a row matching no tracked path), and expired reviews (a date
trigger that has passed). Same shape as ``scripts/grc/inventory_scan.py``:
``git ls-files`` is the oracle, an allow-list holds known and accepted gaps,
and every failure prints one line.

CLI:

    python3 scripts/repo/manifest_check.py [--manifest PATH]
                                           [--allow-list PATH]
                                           [--root PATH]
                                           [--format human|json]
                                           [--init]

Exit codes:

* 0 - every tracked path resolves to exactly one row; no dead rows; no review
  date passed
* 1 - drift: a shadow path (tracked, no row), an orphan row (matches nothing),
  or an expired review
* 2 - configuration error (manifest missing, YAML malformed, unknown status
  value, bad review shape)

Row shape. Every field is required except ``rewrite_later``, and an unknown
field is a configuration error so a typo cannot silently disable a review:

    - path: "docs/**"             exact path or glob; most specific match wins
      purpose: "..."              one line on what this holds and who reads it
      status: active              active | reference | archived
      reason: "..."               why it is still in the tree
      last_verified: 2026-09-09   date the row was last checked against reality
      review: {every: 180d}       {by: DATE} | {every: Nd} | {event: slug, ...}
      rewrite_later: "..."        optional note for a later pass

Resolution: for each tracked path, the winning row is the one whose pattern
matches and whose literal prefix (the part before the first wildcard) is the
longest, so ``docs/grc/POAM_AUTO_FINDINGS.md`` beats ``docs/**``. A pattern
ending in ``/**`` also matches the directory's immediate children and the
directory path itself, because ``fnmatch`` alone does not read the way a
person expects at that boundary.

Warnings never change the exit code. Untracked working-tree files print as
``warn undecided`` because a CI checkout is always clean and a working-tree
condition must not fail a pull request. Workflow path filters that match no
tracked path print as ``warn dead filter`` because a dead filter hides a
coverage gap rather than breaking a build. Event review triggers are deferred
to the review register, counted rather than evaluated, so the deferral is
visible instead of silent.
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import yaml

# Repo root resolution: this file lives in scripts/repo/, so root is two dirs up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCANNER_VERSION = "1.0.0"

VALID_STATUS = ("active", "reference", "archived")
REQUIRED_FIELDS = ("path", "purpose", "status", "reason", "last_verified", "review")
OPTIONAL_FIELDS = ("rewrite_later",)
TRIGGER_KEYS = ("by", "every", "event")
EVENT_EXTRA_KEYS = ("flag", "probe")
ALLOW_KINDS = ("shadow", "orphan", "expired")

INTERVAL_RE = re.compile(r"^\s*(\d+)\s*([dwmy])\s*$", re.IGNORECASE)
INTERVAL_DAYS = {"d": 1, "w": 7, "m": 30, "y": 365}

DEFAULT_MANIFEST = "docs/REPO_MANIFEST.yaml"
DEFAULT_ALLOW_LIST = "scripts/repo/manifest_allow_list.yaml"

INIT_PURPOSE = "TODO one line on what this holds and who reads it"
INIT_REASON = "TODO"


class ConfigError(Exception):
    """Anything that makes the manifest unreadable or self-contradictory."""


# --------------------------------------------------------------------------
# The tree, straight from git
# --------------------------------------------------------------------------
def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ConfigError(
            f"git {' '.join(args)} failed in {root}: {proc.stderr.strip()}"
        )
    return proc.stdout


def tracked(root: Path) -> List[str]:
    """Every tracked path. This is the oracle; walking the filesystem and
    parsing .gitignore is wrong, because gitignore re-include semantics are
    exactly what put unexpected trees in the index."""
    return [p for p in _git(root, "ls-files").split("\n") if p]


def untracked(root: Path) -> List[str]:
    """Working-tree files that are neither tracked nor ignored."""
    return [
        p
        for p in _git(root, "ls-files", "--others", "--exclude-standard").split("\n")
        if p
    ]


# --------------------------------------------------------------------------
# Matching and resolution
# --------------------------------------------------------------------------
def literal_prefix(pattern: str) -> int:
    """Length of the pattern text before the first wildcard character."""
    for i, ch in enumerate(pattern):
        if ch in "*?[":
            return i
    return len(pattern)


def _variants(pattern: str) -> Sequence[str]:
    """A pattern ending in /** also covers the immediate children and the
    directory itself."""
    if pattern.endswith("/**"):
        base = pattern[:-3]
        return (pattern, base + "/*", base)
    return (pattern,)


def matches(path: str, pattern: str) -> bool:
    return any(fnmatch.fnmatchcase(path, v) for v in _variants(pattern))


def resolve(path: str, entries: Sequence[dict]) -> dict | None:
    """The row whose pattern matches and whose literal prefix is longest.
    Ties break toward the longer pattern text, so resolution is stable."""
    best: dict | None = None
    best_key = (-1, -1)
    for entry in entries:
        pattern = str(entry.get("path", ""))
        if not pattern or not matches(path, pattern):
            continue
        key = (literal_prefix(pattern), len(pattern))
        if key > best_key:
            best, best_key = entry, key
    return best


# --------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------
def _as_date(value: Any, label: str) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.strip())
        except ValueError as exc:
            raise ConfigError(f"{label}: {value!r} is not a YYYY-MM-DD date") from exc
    raise ConfigError(f"{label}: {value!r} is not a YYYY-MM-DD date")


def _validate_review(entry: dict) -> dict:
    pattern = entry.get("path")
    review = entry.get("review")
    if not isinstance(review, dict):
        raise ConfigError(f"row {pattern}: review must be a mapping, got {review!r}")
    present = [k for k in TRIGGER_KEYS if k in review]
    if len(present) != 1:
        raise ConfigError(
            f"row {pattern}: review needs exactly one of {', '.join(TRIGGER_KEYS)}, "
            f"found {present or 'none'}"
        )
    trigger = present[0]
    extra = set(review) - {trigger}
    if trigger == "event":
        extra -= set(EVENT_EXTRA_KEYS)
    if extra:
        raise ConfigError(
            f"row {pattern}: review carries unknown key(s) {sorted(extra)}"
        )
    if trigger == "by":
        _as_date(review["by"], f"row {pattern}: review.by")
    elif trigger == "every":
        if not INTERVAL_RE.match(str(review["every"])):
            raise ConfigError(
                f"row {pattern}: review.every must look like 180d, 12w, 6m or 1y, "
                f"got {review['every']!r}"
            )
    elif not str(review["event"]).strip():
        raise ConfigError(f"row {pattern}: review.event needs a slug")
    return review


def _validate_entry(entry: Any, index: int) -> dict:
    if not isinstance(entry, dict):
        raise ConfigError(f"entry {index} is not a mapping: {entry!r}")
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        raise ConfigError(
            f"entry {index} ({entry.get('path', 'no path')}) is missing "
            f"{', '.join(missing)}"
        )
    unknown = set(entry) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS)
    if unknown:
        raise ConfigError(
            f"row {entry.get('path')}: unknown field(s) {sorted(unknown)}"
        )
    if not isinstance(entry["path"], str) or not entry["path"].strip():
        raise ConfigError(f"entry {index}: path must be a non-empty string")
    status = entry["status"]
    if status not in VALID_STATUS:
        raise ConfigError(
            f"row {entry['path']}: unknown status {status!r}, "
            f"expected one of {', '.join(VALID_STATUS)}"
        )
    _as_date(entry["last_verified"], f"row {entry['path']}: last_verified")
    _validate_review(entry)
    return entry


def load_manifest(path: Path) -> List[dict]:
    if not path.is_file():
        raise ConfigError(f"manifest not found at {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"manifest {path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"manifest {path} must be a mapping with an entries list")
    version = data.get("version", 1)
    if version != 1:
        raise ConfigError(f"manifest {path}: unsupported version {version!r}")
    rows = data.get("entries")
    if not isinstance(rows, list):
        raise ConfigError(f"manifest {path}: 'entries' must be a list")
    return [_validate_entry(row, i) for i, row in enumerate(rows)]


def load_allow_list(path: Path) -> List[dict]:
    if not path.is_file():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"allow-list {path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"allow-list {path} must be a mapping")
    entries = data.get("known_gaps") or []
    if not isinstance(entries, list):
        raise ConfigError(f"allow-list {path}: 'known_gaps' must be a list")
    out: List[dict] = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ConfigError(f"allow-list {path}: entry {i} is not a mapping")
        kind = entry.get("kind")
        if kind not in ALLOW_KINDS:
            raise ConfigError(
                f"allow-list {path}: entry {i} kind {kind!r} must be one of "
                f"{', '.join(ALLOW_KINDS)}"
            )
        if not str(entry.get("path", "")).strip():
            raise ConfigError(f"allow-list {path}: entry {i} needs a path")
        if not str(entry.get("reason", "")).strip():
            raise ConfigError(f"allow-list {path}: entry {i} needs a dated reason")
        out.append(entry)
    return out


def _suppressed(kind: str, key: str, allow_list: Iterable[dict]) -> dict | None:
    for entry in allow_list:
        if entry.get("kind") != kind:
            continue
        if matches(key, str(entry["path"])) or key == entry["path"]:
            return entry
    return None


# --------------------------------------------------------------------------
# Review evaluation
# --------------------------------------------------------------------------
def _interval_days(value: str) -> int:
    match = INTERVAL_RE.match(str(value))
    if not match:
        raise ConfigError(f"review interval {value!r} is not readable")
    return int(match.group(1)) * INTERVAL_DAYS[match.group(2).lower()]


def review_state(entry: dict, today: datetime.date) -> tuple[str, str]:
    """Return (state, trigger text). State is ok, expired, or deferred.

    Only date triggers are evaluated on the pull request path. Event triggers
    belong to the review register and are deferred, never a pull request
    failure."""
    review = entry["review"]
    if "event" in review:
        return "deferred", f"event: {review['event']}"
    if "by" in review:
        due = _as_date(review["by"], f"row {entry['path']}: review.by")
        return ("expired" if today > due else "ok"), f"by: {due.isoformat()}"
    interval = _interval_days(review["every"])
    last = _as_date(entry["last_verified"], f"row {entry['path']}: last_verified")
    due = last + datetime.timedelta(days=interval)
    return ("expired" if today > due else "ok"), f"every: {review['every']}"


# --------------------------------------------------------------------------
# Workflow path filters
# --------------------------------------------------------------------------
def workflow_filters(root: Path) -> List[tuple[str, str]]:
    """(workflow file name, glob) for every path filter on push and
    pull_request, including the paths-ignore variants."""
    wf_dir = root / ".github" / "workflows"
    out: List[tuple[str, str]] = []
    if not wf_dir.is_dir():
        return out
    for wf in sorted(list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))):
        try:
            doc = yaml.safe_load(wf.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError):
            continue  # a broken workflow is the workflow linter's business
        if not isinstance(doc, dict):
            continue
        # PyYAML reads the bare key "on" as the boolean True.
        triggers = doc.get("on", doc.get(True))
        if not isinstance(triggers, dict):
            continue
        for event in ("pull_request", "push"):
            spec = triggers.get(event)
            if not isinstance(spec, dict):
                continue
            for key in ("paths", "paths-ignore"):
                for glob in spec.get(key) or []:
                    glob = str(glob)
                    if glob.startswith("!"):
                        continue  # a negation refines a filter, it is not one
                    pair = (wf.name, glob)
                    if pair not in out:
                        out.append(pair)
    return out


# --------------------------------------------------------------------------
# The scan
# --------------------------------------------------------------------------
def run(
    root: Path,
    manifest_path: Path,
    allow_list_path: Path,
    today: datetime.date | None = None,
) -> Dict[str, Any]:
    today = today or datetime.date.today()
    entries = load_manifest(manifest_path)
    allow_list = load_allow_list(allow_list_path)
    paths = tracked(root)

    shadow: List[str] = []
    suppressed: List[dict] = []
    matched: Dict[int, int] = {id(e): 0 for e in entries}

    for path in paths:
        winner = resolve(path, entries)
        if winner is None:
            hit = _suppressed("shadow", path, allow_list)
            if hit:
                suppressed.append({"kind": "shadow", "key": path, "entry": hit})
            else:
                shadow.append(path)
            continue
        for entry in entries:
            if matches(path, str(entry["path"])):
                matched[id(entry)] += 1

    orphan: List[str] = []
    expired: List[Dict[str, str]] = []
    deferred: List[Dict[str, str]] = []
    for entry in entries:
        pattern = str(entry["path"])
        if matched[id(entry)] == 0:
            hit = _suppressed("orphan", pattern, allow_list)
            if hit:
                suppressed.append({"kind": "orphan", "key": pattern, "entry": hit})
            else:
                orphan.append(pattern)
        state, trigger = review_state(entry, today)
        row = {
            "path": pattern,
            "last_verified": _as_date(
                entry["last_verified"], f"row {pattern}: last_verified"
            ).isoformat(),
            "trigger": trigger,
        }
        if state == "deferred":
            deferred.append(row)
        elif state == "expired":
            hit = _suppressed("expired", pattern, allow_list)
            if hit:
                suppressed.append({"kind": "expired", "key": pattern, "entry": hit})
            else:
                expired.append(row)

    dead_filters = [
        {"workflow": wf, "glob": glob}
        for wf, glob in workflow_filters(root)
        if not any(matches(p, glob) for p in paths)
    ]

    return {
        "scanner_version": SCANNER_VERSION,
        "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "root": str(root),
        "manifest": str(manifest_path),
        "shadow": shadow,
        "orphan": orphan,
        "expired": expired,
        "deferred_events": deferred,
        "undecided": untracked(root),
        "dead_filters": dead_filters,
        "suppressed": suppressed,
        "counts": {
            "tracked": len(paths),
            "rows": len(entries),
            "shadow": len(shadow),
            "orphan": len(orphan),
            "expired": len(expired),
            "deferred_events": len(deferred),
            "undecided": len(untracked(root)),
            "dead_filters": len(dead_filters),
            "suppressed": len(suppressed),
        },
    }


def failure_count(report: Dict[str, Any]) -> int:
    counts = report["counts"]
    return counts["shadow"] + counts["orphan"] + counts["expired"]


def render_human(report: Dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        f"# Repo Manifest Check v{report['scanner_version']}",
        f"Manifest: {report['manifest']}",
        f"Tracked paths: {counts['tracked']}    Manifest rows: {counts['rows']}",
        "",
    ]
    for path in report["shadow"]:
        lines.append(f"FAIL shadow: {path} has no manifest row")
    for pattern in report["orphan"]:
        lines.append(f"FAIL orphan: row {pattern} matches no tracked path")
    for row in report["expired"]:
        lines.append(
            f"FAIL review due: {row['path']} last verified {row['last_verified']}, "
            f"trigger {row['trigger']}"
        )
    for path in report["undecided"]:
        lines.append(f"warn undecided: {path}")
    for row in report["dead_filters"]:
        lines.append(
            f"warn dead filter: {row['workflow']}: {row['glob']} "
            "matches no tracked path"
        )
    lines.append("")
    lines.append(
        f"Event rows deferred to the review register: {counts['deferred_events']}"
    )
    lines.append(f"Suppressed by allow-list: {counts['suppressed']}")
    if failure_count(report):
        lines.append(
            f"Result: {failure_count(report)} failure(s) "
            f"(unlisted {counts['shadow']}, dead rows {counts['orphan']}, "
            f"reviews due {counts['expired']})"
        )
    else:
        lines.append("Result: clean")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Draft generator
# --------------------------------------------------------------------------
def init_draft(root: Path, today: datetime.date | None = None) -> str:
    """A first-draft manifest on stdout: one row per top-level tracked
    directory and one row per tracked root file. This is a starting point for
    a person to edit, never a self-healing mode, so it never writes a file."""
    today = today or datetime.date.today()
    paths = tracked(root)
    dirs = sorted({p.split("/")[0] for p in paths if "/" in p})
    files = sorted(p for p in paths if "/" not in p)
    lines = [
        "version: 1",
        "generated_by: scripts/repo/manifest_check.py --init",
        "# Draft only. Every purpose and reason below is a placeholder and has to",
        "# be replaced by hand before this manifest means anything.",
        "entries:",
    ]
    for pattern in [d + "/**" for d in dirs] + files:
        lines.append(f'  - path: "{pattern}"')
        lines.append(f'    purpose: "{INIT_PURPOSE}"')
        lines.append("    status: active")
        lines.append(f'    reason: "{INIT_REASON}"')
        lines.append(f"    last_verified: {today.isoformat()}")
        lines.append("    review: {every: 180d}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Diff the repository manifest against git ls-files: shadow paths, "
            "orphan rows, expired reviews."
        ),
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help=f"Path to the manifest YAML (default: <root>/{DEFAULT_MANIFEST}).",
    )
    parser.add_argument(
        "--allow-list",
        default=None,
        help=f"Path to the allow-list YAML (default: {DEFAULT_ALLOW_LIST}).",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repository root to scan (default: this checkout).",
    )
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Report format.",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Print a draft manifest built from the tree and exit. Writes nothing.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    root = Path(args.root).resolve()
    manifest = Path(args.manifest) if args.manifest else root / DEFAULT_MANIFEST
    allow_list = (
        Path(args.allow_list)
        if args.allow_list
        else Path(__file__).resolve().parent / "manifest_allow_list.yaml"
    )

    try:
        if args.init:
            sys.stdout.write(init_draft(root))
            return 0
        report = run(root, manifest, allow_list)
    except ConfigError as exc:
        print(f"manifest_check: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(render_human(report))
    return 1 if failure_count(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Injects a generated contents block into every top-level README from the
rows in ``docs/REPO_MANIFEST.yaml``. Marker injection, not whole-file
generation: everything outside the marker pair is preserved byte for byte, so
a hand-written README keeps every word it had.

The marker idiom is the one the repository already uses and CI already
understands: ``<!-- METRIC:key -->value<!-- /METRIC -->`` in
``scripts/sync_portfolio.py`` and ``<!-- VIEW:slug --> ... <!-- /VIEW -->`` in
``scripts/sync_views.py``. The ``MANIFEST:`` namespace is this script's.

CLI:

    python3 scripts/repo/gen_folder_readmes.py [--manifest PATH]
                                               [--root PATH]
                                               [--apply]
                                               [--check]
                                               [--list-dirs]

Exit codes:

* 0 - no drift, or ``--apply`` wrote successfully
* 1 - ``--check`` set and at least one README block is missing or stale; or
  ``--apply`` found a target it cannot fix, because the README or its marker
  pair does not exist
* 2 - configuration error (manifest missing or malformed, or a top-level
  tracked directory that no manifest row describes)

Default with no flag is a dry run that prints what would change and exits 0,
matching the two sync scripts. ``--check`` and ``--apply`` together resolve to
``--check``, the same way ``sync_views.py`` resolves them.

Targets. The directory set is derived from ``git ls-files``, never from a
literal list, so a new top-level directory is picked up the day it lands. Each
top-level tracked directory is one target, and the repository root is one more,
under the key ``root``.

Rows. A target's block holds the manifest rows that describe that directory's
own contents: for a top-level directory ``D`` every row whose path starts with
``D/``, and for the repository root every row with no ``/`` in its path, since
every other row belongs to the directory README that owns it. Rows are sorted
by path, which puts a parent pattern above the more specific rows under it,
because ``*`` sorts before any letter.

The ``Purpose`` column is the manifest's ``purpose`` field verbatim. A
difference between the manifest and a README is a bug in one of them, never a
style choice made here.

Drift. A README with no marker pair is drift and is reported by path, following
``sync_views.py:324`` rather than the silent skip in
``sync_portfolio.py:129``. A silently skipped README is the failure this script
exists to stop. A ``MANIFEST:`` marker in a file that is not a target, or under
a key that is not a target, is drift too: it is a block nobody generates.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import yaml

# This file lives in scripts/repo/, so the repository root is two directories up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

GENERATOR_VERSION = "1.0.0"

DEFAULT_MANIFEST = "docs/REPO_MANIFEST.yaml"
ROOT_KEY = "root"
README = "README.md"

BLOCK_NOTE = (
    "Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers."
)
TABLE_HEAD = ("| Path | Status | Purpose |", "|---|---|---|")

ANY_MARKER_RE = re.compile(r"<!--\s*MANIFEST:([^\s>]+?)\s*-->")


class ConfigError(Exception):
    """Anything that makes the manifest or the tree unreadable."""


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
    return [p for p in _git(root, "ls-files").split("\n") if p]


def top_level_dirs(paths: Sequence[str]) -> List[str]:
    """Every directory that holds at least one tracked path, one level down."""
    return sorted({p.split("/")[0] for p in paths if "/" in p})


# --------------------------------------------------------------------------
# The manifest
# --------------------------------------------------------------------------
def load_rows(path: Path) -> List[dict]:
    if not path.is_file():
        raise ConfigError(f"manifest not found at {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"manifest {path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"manifest {path} must be a mapping with an entries list")
    rows = data.get("entries")
    if not isinstance(rows, list):
        raise ConfigError(f"manifest {path}: 'entries' must be a list")
    out: List[dict] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ConfigError(f"manifest {path}: entry {i} is not a mapping")
        for field in ("path", "status", "purpose"):
            if not str(row.get(field, "")).strip():
                raise ConfigError(
                    f"manifest {path}: entry {i} is missing {field}; "
                    "run scripts/repo/manifest_check.py for the full row contract"
                )
        out.append(row)
    return out


def rows_for(key: str, rows: Sequence[dict]) -> List[dict]:
    """The rows that describe this target's own contents."""
    if key == ROOT_KEY:
        picked = [r for r in rows if "/" not in str(r["path"])]
    else:
        prefix = key + "/"
        picked = [r for r in rows if str(r["path"]).startswith(prefix)]
    return sorted(picked, key=lambda r: str(r["path"]))


# --------------------------------------------------------------------------
# The block
# --------------------------------------------------------------------------
def cell(text: str) -> str:
    """One table cell: no pipes, no line breaks, nothing that breaks the row."""
    return " ".join(str(text).split()).replace("|", r"\|")


def block_for(key: str, rows: Sequence[dict]) -> str:
    lines = [f"<!-- MANIFEST:{key} -->", BLOCK_NOTE, "", *TABLE_HEAD]
    for row in rows:
        lines.append(
            f"| `{cell(row['path'])}` | {cell(row['status'])} | {cell(row['purpose'])} |"
        )
    lines.append("<!-- /MANIFEST -->")
    return "\n".join(lines)


def marker_re(key: str) -> re.Pattern[str]:
    return re.compile(
        r"<!--\s*MANIFEST:" + re.escape(key) + r"\s*-->.*?<!--\s*/MANIFEST\s*-->",
        re.DOTALL,
    )


def targets(root: Path, paths: Sequence[str]) -> List[Tuple[str, str]]:
    """(marker key, README path) for the repository root and every top-level
    tracked directory."""
    dirs = top_level_dirs(paths)
    if ROOT_KEY in dirs:
        raise ConfigError(
            f"a tracked top-level directory is named {ROOT_KEY!r}, which collides "
            f"with the marker key this script uses for the repository root"
        )
    return [(ROOT_KEY, README)] + [(d, f"{d}/{README}") for d in dirs]


# --------------------------------------------------------------------------
# The scan
# --------------------------------------------------------------------------
def stray_markers(root: Path, paths: Sequence[str], known: Dict[str, str]) -> List[str]:
    """Markers in a file that is not the target for that key. A marker nobody
    generates is a block that goes stale in silence."""
    out = []
    for rel in paths:
        if not rel.endswith(".md"):
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in ANY_MARKER_RE.finditer(text):
            key = match.group(1)
            if known.get(key) != rel:
                out.append(f"{rel}: MANIFEST:{key}")
    return out


def run(root: Path, manifest_path: Path, apply: bool) -> Tuple[List[str], int]:
    """Returns (report lines, drift count). Writes when apply is set."""
    rows = load_rows(manifest_path)
    paths = tracked(root)
    pairs = targets(root, paths)
    known = {key: rel for key, rel in pairs}

    report: List[str] = []
    drift = 0
    unfixable = 0

    for key, rel in pairs:
        picked = rows_for(key, rows)
        if not picked:
            raise ConfigError(
                f"no manifest row falls inside {key}/; the manifest and the tree "
                f"disagree, run scripts/repo/manifest_check.py"
            )
        block = block_for(key, picked)
        path = root / rel
        if not path.is_file():
            report.append(f"FAIL missing README: {rel} (needs <!-- MANIFEST:{key} -->)")
            drift += 1
            unfixable += 1
            continue
        text = path.read_text(encoding="utf-8")
        match = marker_re(key).search(text)
        if not match:
            report.append(f"FAIL missing marker: {rel} has no MANIFEST:{key} pair")
            drift += 1
            unfixable += 1
            continue
        if match.group(0) == block:
            continue
        drift += 1
        report.append(
            f"drift: {rel} MANIFEST:{key} "
            f"({len(picked)} row(s) from the manifest)"
        )
        if apply:
            path.write_text(
                text[: match.start()] + block + text[match.end() :],
                encoding="utf-8",
            )

    for stray in stray_markers(root, paths, known):
        report.append(f"FAIL stray marker: {stray} is not a generated target")
        drift += 1
        unfixable += 1

    report.append(
        f"summary: {len(pairs)} target(s), {drift} drift(s)"
        + (" written" if apply else "")
    )
    return report, (unfixable if apply else drift)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inject the manifest rows for each top-level directory into that "
            "directory's README, between MANIFEST markers. Default is a dry run."
        ),
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help=f"Path to the manifest YAML (default: <root>/{DEFAULT_MANIFEST}).",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="Repository root to read and write (default: this checkout).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the generated block between the markers. Nothing outside them moves.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report only, and exit 1 if any block is missing or stale.",
    )
    parser.add_argument(
        "--list-dirs",
        action="store_true",
        help="Print the top-level tracked directories this acts on, then exit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    root = Path(args.root).resolve()
    manifest = Path(args.manifest) if args.manifest else root / DEFAULT_MANIFEST
    if args.check:
        args.apply = False

    try:
        if args.list_dirs:
            for name in top_level_dirs(tracked(root)):
                print(name)
            return 0
        report, drift = run(root, manifest, args.apply)
    except ConfigError as exc:
        print(f"gen_folder_readmes: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write("\n".join(report) + "\n")
    if args.check or args.apply:
        return 1 if drift else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

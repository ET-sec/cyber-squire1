#!/usr/bin/env python3
"""
sync_portfolio.py — write canonical metrics.yaml values into portfolio HTML.

Pattern
-------
Wrap any number in portfolio HTML like this:

  <!-- METRIC:grc.total_documents -->57<!-- /METRIC -->
  <!-- METRIC:grc.nist_800_53_controls_cited -->133<!-- /METRIC -->

This script finds every METRIC marker, looks up the dotted key in metrics.yaml,
and rewrites the text between the open and close markers. Markers stay in place
so re-runs are idempotent. Surrounding HTML is untouched.

Usage
-----
  python3 scripts/sync_portfolio.py                 # dry-run, prints diff
  python3 scripts/sync_portfolio.py --apply         # write changes
  python3 scripts/sync_portfolio.py --portfolio-root ~/portfolio
  python3 scripts/sync_portfolio.py --metrics path/to/metrics.yaml
  python3 scripts/sync_portfolio.py --files index.html press.html

If --portfolio-root is omitted, defaults to ~/portfolio (Emmanuel's local clone).

Exit codes
----------
  0 = no changes needed OR --apply succeeded
  1 = drift detected in dry-run mode (CI fails)
  2 = configuration error (missing key, missing file)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_PORTFOLIO_ROOT = Path.home() / "portfolio"
DEFAULT_METRICS = Path(__file__).resolve().parents[1] / "metrics.yaml"
DEFAULT_FILES = ["index.html"]

MARKER_RE = re.compile(
    r"<!--\s*METRIC:([a-z0-9_.]+)\s*-->(.*?)<!--\s*/METRIC\s*-->",
    re.DOTALL | re.IGNORECASE,
)


def parse_simple_yaml(text: str) -> dict:
    """Minimal YAML parser for metrics.yaml shape: top-level sections of scalar key/value pairs."""
    out: dict = {}
    section: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            key, sep, val = line.partition(":")
            if not sep:
                continue
            key = key.strip()
            val = val.strip()
            if val == "":
                section = key
                out[section] = {}
            else:
                section = None
                out[key] = strip_yaml_scalar(val)
        else:
            if section is None:
                continue
            key, sep, val = line.strip().partition(":")
            if not sep:
                continue
            out[section][key.strip()] = strip_yaml_scalar(val.strip())
    return out


def strip_yaml_scalar(v: str) -> str | int | float:
    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        return v[1:-1]
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v


def lookup(metrics: dict, dotted: str) -> str | int | float | None:
    parts = dotted.split(".")
    cursor: object = metrics
    for p in parts:
        if not isinstance(cursor, dict) or p not in cursor:
            return None
        cursor = cursor[p]
    if isinstance(cursor, dict):
        return None
    return cursor


def sync_file(
    path: Path, metrics: dict, apply: bool
) -> tuple[int, int, list[str]]:
    """Returns (rewrites, marker_count, error_messages)."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    rewrites = 0
    marker_count = 0

    def replace(match: re.Match) -> str:
        nonlocal rewrites, marker_count
        marker_count += 1
        key = match.group(1)
        current = match.group(2)
        value = lookup(metrics, key)
        if value is None:
            errors.append(f"  unknown metric key: {key}")
            return match.group(0)
        new = str(value)
        if current.strip() == new:
            return match.group(0)
        rewrites += 1
        if not apply:
            errors.append(f"  DRIFT {key}: {current.strip()!r} -> {new!r}")
        return f"<!-- METRIC:{key} -->{new}<!-- /METRIC -->"

    new_text = MARKER_RE.sub(replace, text)
    if apply and rewrites:
        path.write_text(new_text, encoding="utf-8")
    return rewrites, marker_count, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--portfolio-root",
        type=Path,
        default=DEFAULT_PORTFOLIO_ROOT,
        help="root of portfolio repo (default ~/portfolio)",
    )
    ap.add_argument(
        "--metrics",
        type=Path,
        default=DEFAULT_METRICS,
        help="path to metrics.yaml (default repo root)",
    )
    ap.add_argument(
        "--files",
        nargs="+",
        default=DEFAULT_FILES,
        help="HTML files inside portfolio-root to sync",
    )
    ap.add_argument("--apply", action="store_true", help="write changes")
    args = ap.parse_args()

    if not args.metrics.exists():
        print(f"metrics.yaml not found: {args.metrics}", file=sys.stderr)
        return 2
    metrics = parse_simple_yaml(args.metrics.read_text(encoding="utf-8"))

    total_rewrites = 0
    total_markers = 0
    any_errors = False

    for rel in args.files:
        path = args.portfolio_root / rel
        if not path.exists():
            print(f"skip (missing): {path}")
            continue
        rewrites, markers, errors = sync_file(path, metrics, args.apply)
        total_rewrites += rewrites
        total_markers += markers
        verb = "wrote" if (args.apply and rewrites) else "would rewrite"
        print(
            f"{path.relative_to(args.portfolio_root)}: {markers} marker(s), "
            f"{verb} {rewrites}"
        )
        for e in errors:
            print(e)
            if e.startswith("  unknown metric key"):
                any_errors = True

    print()
    print(f"summary: {total_markers} markers across files, {total_rewrites} drift(s)")

    if any_errors:
        return 2
    if total_rewrites and not args.apply:
        print("drift detected. rerun with --apply to write changes.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

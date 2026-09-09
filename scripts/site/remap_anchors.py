#!/usr/bin/env python3
"""Remap evidence line anchors in docs/architecture/views/nodes/*.yaml after a cited file changes.

Every node entry cites evidence as {label, path, line}. An edit that adds or removes lines in a cited
file leaves those anchors pointing at the wrong text, silently. This script diffs each cited path
between a base git revision (default HEAD) and the working tree, builds an old-to-new line map with
difflib, and rewrites the anchors. Lines that no longer exist are reported and left as they were.

Run it ONCE per change set: after --apply the anchors match the working tree, so a second run against the
same base shifts them again. If in doubt, restore the yaml anchors from the base revision first.

Usage:
  python3 scripts/site/remap_anchors.py --check          # report what would move
  python3 scripts/site/remap_anchors.py --apply          # rewrite the yaml files
  python3 scripts/site/remap_anchors.py --base <rev> --apply
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODES_DIR = ROOT / "docs" / "architecture" / "views" / "nodes"
ANCHOR = re.compile(r'(?P<head>\{label: "[^"]*", path: (?P<path>[^,}]+), line: )(?P<q>"?)(?P<a>[0-9]+)(?:-(?P<b>[0-9]+))?(?P=q)(?P<tail>\})')


def git_show(rev: str, path: str) -> list[str] | None:
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else None


def line_map(old: list[str], new: list[str]) -> dict[int, int]:
    """1-based old line -> new line. Same-count replacements keep their position."""
    m: dict[int, int] = {}
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and (i2 - i1) == (j2 - j1)):
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="git revision the anchors currently match")
    ap.add_argument("--apply", action="store_true", help="write the remapped anchors")
    ap.add_argument("--check", action="store_true", help="report only (default)")
    args = ap.parse_args()

    maps: dict[str, dict[int, int] | None] = {}
    moved = 0
    lost: list[str] = []
    for yaml_path in sorted(NODES_DIR.glob("*.yaml")):
        text = yaml_path.read_text(encoding="utf-8")

        def sub(m: re.Match) -> str:
            nonlocal moved
            path = m.group("path").strip()
            if path not in maps:
                old = git_show(args.base, path)
                new_file = ROOT / path
                new = new_file.read_text(encoding="utf-8").splitlines() if new_file.exists() else None
                maps[path] = None if old is None or new is None or old == new else line_map(old, new)
            lm = maps[path]
            if lm is None:
                return m.group(0)
            a = int(m.group("a"))
            b = int(m.group("b")) if m.group("b") else None
            if a > len(git_show(args.base, path) or []):
                return m.group(0)  # anchor added in this change set; nothing to remap
            na = lm.get(a)
            nb = lm.get(b) if b else None
            if na is None or (b and nb is None):
                lost.append(f"{yaml_path.name}: {path}:{m.group('a')}{'-' + m.group('b') if b else ''} (line removed or rewritten; check by hand)")
                return m.group(0)
            if na == a and (nb == b or b is None):
                return m.group(0)
            moved += 1
            new_val = f"{na}-{nb}" if b else f"{na}"
            print(f"{yaml_path.name}: {path} {m.group('a')}{'-' + m.group('b') if b else ''} -> {new_val}")
            return f"{m.group('head')}{m.group('q')}{new_val}{m.group('q')}{m.group('tail')}"

        new_text = ANCHOR.sub(sub, text)
        if args.apply and new_text != text:
            yaml_path.write_text(new_text, encoding="utf-8")

    changed = [p for p, lm in maps.items() if lm is not None]
    print(f"cited files that differ from {args.base}: {len(changed)}; anchors moved: {moved}; unresolved: {len(lost)}")
    for line in lost:
        print("  UNRESOLVED", line)
    if not args.apply:
        print("(report only; pass --apply to write)")
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Extract YAML frontmatter from docs/grc/*.md into a single YAML index.

Plan 19-01 Task 2 preprocessor. Walks `docs/grc/*.md` (top level only),
reads frontmatter via python-frontmatter, scans bodies for cross-doc
P\\d+-\\d+ references, and parses POAM_PLAN_OF_ACTION.md row labels for
the canonical POA&M ID set. Output is fed into the conftest OPA harness
in plan 19-06.

Output:
    build/grc-frontmatter.yaml -- deterministic (sort_keys=True) YAML

Behavior:
    - Walks top-level *.md only (no subdirs) so unsanitized drafts are skipped.
    - Docs without frontmatter -> warning to stderr, skipped (e.g. README.md).
    - Each kept doc gets a `referenced_poam_ids` list (sorted, unique) of any
      P\\d+-\\d+ tokens found in the body.
    - POAM_PLAN_OF_ACTION.md additionally gets `poam_ids` populated from the
      canonical markdown table (rows starting with `| POAM-P...`).
    - Top-level `_canonical_poam_ids` mirrors that list for downstream policies.

Stdout is left clean for piping; all logs go to stderr.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import frontmatter
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC_DIR = REPO_ROOT / "docs" / "grc"
BUILD_DIR = REPO_ROOT / "build"
OUTPUT_PATH = BUILD_DIR / "grc-frontmatter.yaml"
POAM_FILE = "POAM_PLAN_OF_ACTION.md"

# Short-form POA&M cross-reference regex used everywhere except the canonical table.
POAM_REF_PATTERN = re.compile(r"P\d+-\d+")

# Canonical row label regex: matches lines like `| POAM-P17-01 | ... |` in the
# POAM_PLAN_OF_ACTION.md table. Captures the short P\d+-\d+ form.
POAM_TABLE_ROW_PATTERN = re.compile(r"^\|\s*POAM-(P\d+-\d+)\s*\|")


def log(msg: str) -> None:
    """Write a single line to stderr. Stdout is reserved for clean piping."""
    print(msg, file=sys.stderr)


def extract_referenced_poam_ids(body: str) -> list[str]:
    """Return sorted unique P\\d+-\\d+ tokens found in the doc body."""
    return sorted(set(POAM_REF_PATTERN.findall(body)))


def extract_canonical_poam_ids(body: str) -> list[str]:
    """Parse POAM_PLAN_OF_ACTION.md table for canonical POAM-P\\d+-\\d+ rows.

    Returns the short form (P\\d+-\\d+) for cross-doc symmetry with refs.
    """
    ids: list[str] = []
    for line in body.splitlines():
        m = POAM_TABLE_ROW_PATTERN.match(line)
        if m:
            ids.append(m.group(1))
    return sorted(set(ids))


def process_doc(path: Path) -> tuple[str, dict] | None:
    """Load a markdown file, return (filename, entry_dict) or None to skip."""
    try:
        post = frontmatter.load(path)
    except Exception as exc:  # noqa: BLE001 - we want to log and skip on any parse fail
        log(f"WARN parse_failed {path.name}: {exc}")
        return None

    if not post.metadata:
        log(f"WARN no_frontmatter {path.name}")
        return None

    entry: dict = dict(post.metadata)
    entry["referenced_poam_ids"] = extract_referenced_poam_ids(post.content)

    if path.name == POAM_FILE:
        entry["poam_ids"] = extract_canonical_poam_ids(post.content)

    return path.name, entry


def build_index(grc_dir: Path) -> dict:
    """Walk top-level *.md and build the output dict."""
    out: dict = {}
    docs = sorted(grc_dir.glob("*.md"))  # top-level only, no rglob
    for path in docs:
        result = process_doc(path)
        if result is None:
            continue
        name, entry = result
        out[name] = entry

    canonical = []
    if POAM_FILE in out:
        canonical = out[POAM_FILE].get("poam_ids", [])
    out["_canonical_poam_ids"] = canonical
    return out


def write_yaml(index: dict, output_path: Path) -> None:
    """Write deterministic YAML output to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(index, fh, sort_keys=True)


def main(grc_dir: Path = GRC_DIR, output_path: Path = OUTPUT_PATH) -> int:
    if not grc_dir.is_dir():
        log(f"ERROR grc_dir_missing {grc_dir}")
        return 1

    index = build_index(grc_dir)
    write_yaml(index, output_path)

    doc_keys = [k for k in index if not k.startswith("_")]
    total_refs = sum(len(index[k].get("referenced_poam_ids", [])) for k in doc_keys)
    canonical_count = len(index.get("_canonical_poam_ids", []))
    log(
        f"OK docs_processed={len(doc_keys)} "
        f"total_referenced_poam_ids={total_refs} "
        f"canonical_poam_ids={canonical_count} "
        f"output={output_path.relative_to(REPO_ROOT) if output_path.is_relative_to(REPO_ROOT) else output_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

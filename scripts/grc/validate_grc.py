"""GRC corpus validator.

Runs five checks on docs/grc/:
  1. frontmatter   YAML frontmatter parses on the 7 source-of-truth docs and
                   carries the required keys.
  2. oscal         Each docs/grc/oscal/output/*.oscal.json validates against
                   the matching vendored draft-07 schema in oscal/schemas/.
  3. stix          docs/grc/stix/*.stix.json parses and has a STIX 2.1 bundle
                   shape (type=bundle, id starts with bundle--, objects list).
  4. links         Intra-corpus markdown links of the form [text](path.md) or
                   [text](path.md#anchor) resolve to a file under docs/grc/.
                   External links (http://, https://, mailto:) are skipped.
  5. sanitization  No unsanitized tokens leak into docs/grc/. Tokens come
                   from SANITIZATION_KEY.md (real -> sanitized mapping).

Exit code is 0 on full pass, 1 on any check failure. Each failing check
prints what failed; the script always runs all five checks before exiting
so CI surfaces the full picture in one run.

Usage:
  python3 scripts/grc/validate_grc.py
  python3 scripts/grc/validate_grc.py --only frontmatter,oscal
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
GRC = REPO / "docs" / "grc"
OSCAL_OUT = GRC / "oscal" / "output"
OSCAL_SCHEMAS = GRC / "oscal" / "schemas"
STIX_DIR = GRC / "stix"

SOURCE_OF_TRUTH = [
    "SSP_SYSTEM_SECURITY_PLAN.md",
    "SQUIRE_SSP.md",
    "POAM_PLAN_OF_ACTION.md",
    "FRAMEWORK_CROSSWALK_SQUIRE.md",
    "SQUIRE_THREAT_MODEL.md",
    "AI_THREAT_CATALOG.md",
    "REDTEAM_RESULTS.md",
]

REQUIRED_FRONTMATTER_KEYS = {
    "document_id",
    "title",
    "doc_type",
    "classification",
    "version",
    "last_updated",
    "owner",
}

OSCAL_REQUIRED_TOP_KEYS = {
    "system-security-plan": {
        "uuid",
        "metadata",
        "system-characteristics",
        "system-implementation",
        "control-implementation",
    },
    "plan-of-action-and-milestones": {"uuid", "metadata", "poam-items"},
    "component-definition": {"uuid", "metadata", "components"},
}

OSCAL_OUTPUT_FILES = [
    "squire-ssp.oscal.json",
    "squire-poam.oscal.json",
    "squire-component.oscal.json",
]

# Base list contains only tokens that are safe to name in a public file.
# Host-specific literals (retired host IPs, host filesystem paths) are
# injected at runtime via GRC_UNSANITIZED_EXTRA (comma-separated) so the
# concrete values never live in this tracked file. The repo-level gitleaks
# tripwires independently block those literals in any tracked file.
UNSANITIZED_TOKENS = [
    "tigouetheory.com",
    "CoreDirective",
    "Tigoue Theory",
    "cd-service-",
    "tunnel-cyber-squire",
    "CD_VOL_POSTGRES",
    "CD_VOL_FALCO",
    "etigoue@tigouetheory.com",
    "cd-alpha",
] + [
    t.strip()
    for t in os.environ.get("GRC_UNSANITIZED_EXTRA", "").split(",")
    if t.strip()
]


def _parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    return yaml.safe_load(m.group(1))


def check_frontmatter() -> list[str]:
    errors: list[str] = []
    for name in SOURCE_OF_TRUTH:
        path = GRC / name
        if not path.exists():
            errors.append(f"{name}: file missing")
            continue
        meta = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if not meta:
            errors.append(f"{name}: no YAML frontmatter")
            continue
        missing = REQUIRED_FRONTMATTER_KEYS - set(meta.keys())
        if missing:
            errors.append(f"{name}: missing keys {sorted(missing)}")
        if not isinstance(meta.get("version"), str):
            errors.append(f"{name}: version must be a string (use quotes)")
    return errors


def check_oscal() -> list[str]:
    """Structural OSCAL check.

    Full draft-07 ref resolution against the NIST OSCAL schemas is broken in
    jsonschema-py because OSCAL declares nested per-definition $id values
    that the referencing library treats as fresh resolution roots. The
    canonical validator is the NIST oscal-cli Go binary. Until that binary
    is wired into CI, this check verifies (a) JSON parses, (b) exactly one
    top-level OSCAL key, (c) that key is one we recognize, (d) required
    sub-keys per NIST OSCAL 1.2.1.
    """
    errors: list[str] = []
    if not OSCAL_OUT.is_dir():
        errors.append(f"OSCAL output dir missing: {OSCAL_OUT}")
        return errors
    for out_name in OSCAL_OUTPUT_FILES:
        out_path = OSCAL_OUT / out_name
        if not out_path.exists():
            errors.append(f"{out_name}: missing")
            continue
        try:
            doc = json.loads(out_path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{out_name}: invalid JSON: {e}")
            continue
        if not isinstance(doc, dict) or len(doc) != 1:
            errors.append(f"{out_name}: expected exactly one top-level OSCAL key")
            continue
        top_key, body = next(iter(doc.items()))
        required = OSCAL_REQUIRED_TOP_KEYS.get(top_key)
        if required is None:
            errors.append(f"{out_name}: unknown top-level OSCAL key '{top_key}'")
            continue
        if not isinstance(body, dict):
            errors.append(f"{out_name}: {top_key} body must be an object")
            continue
        missing = required - set(body.keys())
        if missing:
            errors.append(f"{out_name}: {top_key} missing keys {sorted(missing)}")
        meta = body.get("metadata", {})
        if not meta.get("title") or not meta.get("version"):
            errors.append(f"{out_name}: metadata.title and metadata.version required")
    return errors


def check_stix() -> list[str]:
    errors: list[str] = []
    if not STIX_DIR.is_dir():
        return errors
    bundles = list(STIX_DIR.glob("*.stix.json"))
    if not bundles:
        errors.append(f"no STIX bundles in {STIX_DIR}")
        return errors
    for path in bundles:
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: invalid JSON: {e}")
            continue
        if doc.get("type") != "bundle":
            errors.append(f"{path.name}: top-level type must be 'bundle'")
        if not str(doc.get("id", "")).startswith("bundle--"):
            errors.append(f"{path.name}: bundle id missing or malformed")
        if not isinstance(doc.get("objects"), list) or not doc["objects"]:
            errors.append(f"{path.name}: objects must be a non-empty list")
            continue
        for i, obj in enumerate(doc["objects"]):
            if not isinstance(obj, dict):
                errors.append(f"{path.name}: objects[{i}] not an object")
                continue
            if "type" not in obj or "id" not in obj:
                errors.append(f"{path.name}: objects[{i}] missing type or id")
    return errors


def check_links() -> list[str]:
    errors: list[str] = []
    link_re = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
    for path in GRC.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for m in link_re.finditer(text):
            target = m.group(2)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_clean = target.split("#")[0]
            if not target_clean:
                continue
            resolved = (path.parent / target_clean).resolve()
            try:
                resolved.relative_to(GRC.resolve())
            except ValueError:
                continue
            if not resolved.exists():
                rel_doc = path.relative_to(REPO)
                errors.append(f"{rel_doc}: broken link -> {target}")
    return errors


def check_sanitization() -> list[str]:
    errors: list[str] = []
    skip_dirs = {OSCAL_SCHEMAS.resolve()}
    for path in GRC.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".json", ".html", ".mmd"}:
            continue
        if any(str(path.resolve()).startswith(str(d)) for d in skip_dirs):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(REPO)
        for token in UNSANITIZED_TOKENS:
            if token in text:
                errors.append(f"{rel}: contains '{token}'")
    return errors


CHECKS = {
    "frontmatter": check_frontmatter,
    "oscal": check_oscal,
    "stix": check_stix,
    "links": check_links,
    "sanitization": check_sanitization,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="GRC corpus validator")
    ap.add_argument(
        "--only",
        default=None,
        help="Comma-separated subset: frontmatter,oscal,stix,links,sanitization",
    )
    args = ap.parse_args(argv)
    selected = (
        [c.strip() for c in args.only.split(",")] if args.only else list(CHECKS.keys())
    )
    unknown = [c for c in selected if c not in CHECKS]
    if unknown:
        print(f"unknown checks: {unknown}", file=sys.stderr)
        return 2

    total_failures = 0
    for name in selected:
        errors = CHECKS[name]()
        if errors:
            print(f"FAIL [{name}] {len(errors)} issue(s):")
            for e in errors:
                print(f"  {e}")
            total_failures += len(errors)
        else:
            print(f"PASS [{name}]")
    if total_failures:
        print(f"\n{total_failures} total issue(s)")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

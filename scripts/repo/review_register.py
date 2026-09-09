#!/usr/bin/env python3
"""Evaluates the review register (``docs/REVIEW_REGISTER.yaml``) against the
environment and prints the items that fired.

Date review triggers belong to ``scripts/repo/manifest_check.py``, which runs on
every pull request. This script owns the other kind: items whose trigger is an
event only the owner can observe (credits landing, a second tenant existing, the
identity tier coming up, a provider changing its terms). Each item names a
repository variable. The nightly ``review-register`` job in
``.github/workflows/drift-check.yml`` passes those variables in as environment
variables and posts whatever this prints to Telegram.

CLI:

    python3 scripts/repo/review_register.py [--register PATH]
                                            [--format text|json]

Exit codes:

* 0 - evaluated; zero or more items fired. Firing is not a failure, it is the
  register doing its job, so this never returns 1.
* 2 - configuration error (register missing, YAML malformed, an item with no
  flag, a missing or unknown field, a duplicate id or flag)

Firing rule. An item fires when the environment variable named in its ``flag``
holds ``true``, ``1`` or ``yes``, case insensitive and whitespace stripped. An
unset variable means not fired, which is the normal state and is never an error:
GitHub sets ``TRIGGER_X: ${{ vars.TRIGGER_X }}`` to the empty string when the
variable does not exist. A value that is neither truthy nor a recognized false
value prints a warning on stderr and does not fire, because a typed value the
owner expected to work is worth seeing in the run log.

Output. ``--format text`` prints nothing at all when no item fires, so the
workflow can gate the Telegram post on an empty file. ``--format json`` always
prints, because a machine reading it needs the zero case too. When
``GITHUB_OUTPUT`` is set, ``fired_count=N`` is appended to it; the workflow gates
its Telegram step on the byte count of the text output, and the two agree by
construction because an empty text output means zero fired items.

Item shape. Every field is required and an unknown field is a configuration
error, matching ``manifest_check.py``, so a typo like ``acton:`` cannot quietly
drop the instruction from the alert:

    - id: aws_credits_landed        slug, unique across the register
      flag: TRIGGER_AWS_CREDITS     repository variable name, TRIGGER_ prefixed
      what: "..."                   one line on what the item covers
      why_now: "..."                why this event is the right moment
      affects: ["path/**", ...]     paths that move when the item fires
      action: "..."                 what to do, written as an instruction
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import yaml

# Repo root resolution: this file lives in scripts/repo/, so root is two dirs up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

REGISTER_VERSION = "1.0.0"

DEFAULT_REGISTER = "docs/REVIEW_REGISTER.yaml"

REQUIRED_FIELDS = ("id", "flag", "what", "why_now", "affects", "action")
TRUE_VALUES = ("true", "1", "yes")
FALSE_VALUES = ("", "false", "0", "no")
FLAG_RE = re.compile(r"^TRIGGER_[A-Z0-9_]+$")
ID_RE = re.compile(r"^[a-z0-9_]+$")


class ConfigError(Exception):
    """Anything that makes the register unreadable or self-contradictory."""


# --------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------
def _validate_item(item: Any, index: int) -> Dict[str, Any]:
    where = f"item {index}"
    if not isinstance(item, dict):
        raise ConfigError(f"{where}: expected a mapping, got {type(item).__name__}")

    missing = [field for field in REQUIRED_FIELDS if field not in item]
    if missing:
        name = item.get("id", where)
        raise ConfigError(f"item {name}: missing required field(s) {', '.join(missing)}")

    unknown = [key for key in item if key not in REQUIRED_FIELDS]
    if unknown:
        raise ConfigError(
            f"item {item['id']}: unknown field(s) {', '.join(sorted(unknown))}; "
            "a typo here would silently change what the alert says"
        )

    item_id = item["id"]
    if not isinstance(item_id, str) or not ID_RE.match(item_id):
        raise ConfigError(f"{where}: id must be a lowercase slug, got {item_id!r}")

    flag = item["flag"]
    if not isinstance(flag, str) or not FLAG_RE.match(flag):
        raise ConfigError(
            f"item {item_id}: flag must be an upper case name starting with "
            f"TRIGGER_, got {flag!r}"
        )

    for field in ("what", "why_now", "action"):
        if not isinstance(item[field], str) or not item[field].strip():
            raise ConfigError(f"item {item_id}: {field} must be a non-empty string")

    affects = item["affects"]
    if not isinstance(affects, list) or not affects:
        raise ConfigError(f"item {item_id}: affects must be a non-empty list of paths")
    for path in affects:
        if not isinstance(path, str) or not path.strip():
            raise ConfigError(f"item {item_id}: affects holds a non-path entry {path!r}")

    return item


def load_register(path: Path) -> List[Dict[str, Any]]:
    """Parse and validate the register. Raises ConfigError on anything wrong."""
    if not path.is_file():
        raise ConfigError(f"register not found at {path}")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"register at {path} is not valid YAML: {exc}") from exc

    if not isinstance(doc, dict):
        raise ConfigError(f"register at {path} must be a mapping at the top level")
    items = doc.get("items")
    if not isinstance(items, list) or not items:
        raise ConfigError(f"register at {path} has no items list")

    validated = [_validate_item(item, index) for index, item in enumerate(items)]

    seen_ids: Dict[str, int] = {}
    seen_flags: Dict[str, str] = {}
    for item in validated:
        if item["id"] in seen_ids:
            raise ConfigError(f"duplicate id {item['id']}")
        seen_ids[item["id"]] = 1
        if item["flag"] in seen_flags:
            raise ConfigError(
                f"flag {item['flag']} is claimed by both {seen_flags[item['flag']]} "
                f"and {item['id']}; one variable cannot mean two things"
            )
        seen_flags[item["flag"]] = item["id"]

    return validated


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------
def is_fired(raw: str | None, flag: str, warn: bool = True) -> bool:
    """True when the flag's value reads as set. Unset is not fired, never an
    error. An unrecognized value warns on stderr so an owner typo is visible in
    the run log rather than silently doing nothing."""
    value = (raw or "").strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    if warn:
        print(
            f"review_register: {flag} holds {raw!r}, which is neither set nor "
            f"unset; treating it as not fired. Use one of {', '.join(TRUE_VALUES)}.",
            file=sys.stderr,
        )
    return False


def evaluate(
    items: Sequence[Mapping[str, Any]],
    env: Mapping[str, str],
    register_path: Path,
) -> Dict[str, Any]:
    fired = [
        dict(item) for item in items if is_fired(env.get(item["flag"]), item["flag"])
    ]
    return {
        "register_version": REGISTER_VERSION,
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "register": str(register_path),
        "items": len(items),
        "count": len(fired),
        "fired": fired,
        "flags": sorted(str(item["flag"]) for item in items),
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def render_text(report: Mapping[str, Any]) -> str:
    """A plain block suitable for a Telegram message body. Empty when nothing
    fired, so the workflow can test the output file for zero bytes."""
    if not report["fired"]:
        return ""
    blocks: List[str] = []
    for item in report["fired"]:
        lines = [
            f"{item['id']} ({item['flag']})",
            f"  What: {item['what']}",
            f"  Why now: {item['why_now']}",
            f"  Action: {item['action']}",
            "  Affects:",
        ]
        lines.extend(f"    - {path}" for path in item["affects"])
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def write_github_output(count: int, env: Mapping[str, str]) -> None:
    """Append fired_count to $GITHUB_OUTPUT when running under Actions. A
    failure to write is reported and ignored: this is telemetry, and the
    workflow gates its post on the text output rather than on this value."""
    target = env.get("GITHUB_OUTPUT")
    if not target:
        return
    try:
        with open(target, "a", encoding="utf-8") as handle:
            handle.write(f"fired_count={count}\n")
    except OSError as exc:
        print(f"review_register: could not write GITHUB_OUTPUT: {exc}", file=sys.stderr)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the event-triggered review register against the "
            "environment and print the items that fired."
        ),
    )
    parser.add_argument(
        "--register",
        default=None,
        help=f"Path to the register YAML (default: {DEFAULT_REGISTER}).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format. text prints nothing when no item fires.",
    )
    return parser


def main(
    argv: Sequence[str] | None = None, env: Mapping[str, str] | None = None
) -> int:
    args = build_argparser().parse_args(argv)
    env = os.environ if env is None else env
    register = (
        Path(args.register) if args.register else REPO_ROOT / DEFAULT_REGISTER
    )

    try:
        items = load_register(register)
    except ConfigError as exc:
        print(f"review_register: {exc}", file=sys.stderr)
        return 2

    report = evaluate(items, env, register)
    write_github_output(report["count"], env)

    if args.format == "json":
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validates all Agent Cards under .agents/ against A2A v1.0 schema and cross-checks against the Agent Registry.

Used by .github/workflows/agent-signing.yml verify job and locally via Makefile target.

Behavior:
  1. Loads scripts/grc/agent_card_schema.json (Draft7Validator).
  2. Loads .agents/registry.yaml and extracts the declared agent_id set.
  3. Walks .agents/*.card.json (non-recursive).
  4. For each card:
       - Validates against schema; collects all errors (not first-fail).
       - Derives the expected agent_id from the filename stem.
       - Confirms that agent_id appears in the registry.
  5. For each registry agent_id, confirms that a matching card file exists.
  6. Prints two sections: ERRORS (one line per failure) and SUMMARY (counts).
  7. Exits 0 only if zero errors; otherwise exits 1.

CLI:
  python3 scripts/grc/validate_agent_cards.py
  python3 scripts/grc/validate_agent_cards.py --cards-dir .agents --registry .agents/registry.yaml
  python3 scripts/grc/validate_agent_cards.py --schema scripts/grc/agent_card_schema.json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import List, Tuple

import yaml
from jsonschema import Draft7Validator


DEFAULT_CARDS_DIR = ".agents"
DEFAULT_REGISTRY = ".agents/registry.yaml"
DEFAULT_SCHEMA = "scripts/grc/agent_card_schema.json"


def load_schema(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    # Sanity check the schema itself before using it.
    Draft7Validator.check_schema(schema)
    return schema


def load_registry_ids(path: str) -> set:
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    agents = doc.get("agents") if isinstance(doc, dict) else None
    if not isinstance(agents, list):
        raise ValueError(
            f"registry at {path} missing top-level 'agents' list"
        )
    ids = set()
    for row in agents:
        if not isinstance(row, dict):
            continue
        aid = row.get("agent_id")
        if isinstance(aid, str) and aid:
            ids.add(aid)
    return ids


def list_card_files(cards_dir: str) -> List[str]:
    # Non-recursive glob. We intentionally do NOT descend into .agents/skills/.
    pattern = os.path.join(cards_dir, "*.card.json")
    return sorted(glob.glob(pattern))


def stem_of(card_path: str) -> str:
    base = os.path.basename(card_path)
    if base.endswith(".card.json"):
        return base[: -len(".card.json")]
    return os.path.splitext(base)[0]


def validate_card(
    card_path: str, validator: Draft7Validator
) -> Tuple[dict, List[str]]:
    errors: List[str] = []
    try:
        with open(card_path, "r", encoding="utf-8") as f:
            card = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{card_path}: invalid JSON: {e.msg} (line {e.lineno} col {e.colno})")
        return {}, errors
    for err in sorted(validator.iter_errors(card), key=lambda e: list(e.absolute_path)):
        path_str = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{card_path}: schema violation at {path_str}: {err.message}")
    return card, errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_agent_cards.py",
        description=(
            "Validate Agent Cards under .agents/ against the A2A v1.0 JSON Schema "
            "and cross-check filenames against the Agent Registry."
        ),
    )
    parser.add_argument(
        "--cards-dir",
        default=DEFAULT_CARDS_DIR,
        help=f"Directory containing *.card.json files (default: {DEFAULT_CARDS_DIR})",
    )
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY,
        help=f"Path to registry.yaml (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help=f"Path to JSON Schema (default: {DEFAULT_SCHEMA})",
    )
    args = parser.parse_args(argv)

    errors: List[str] = []

    # Load registry first; if it fails we cannot cross-check anything.
    try:
        registry_ids = load_registry_ids(args.registry)
    except FileNotFoundError:
        print(f"ERROR: registry not found at {args.registry}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: failed to load registry {args.registry}: {e}", file=sys.stderr)
        return 1

    # Load schema.
    try:
        schema = load_schema(args.schema)
    except FileNotFoundError:
        print(f"ERROR: schema not found at {args.schema}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: failed to load schema {args.schema}: {e}", file=sys.stderr)
        return 1
    validator = Draft7Validator(schema)

    # Walk cards.
    card_files = list_card_files(args.cards_dir)
    card_stems = set()

    for card_path in card_files:
        stem = stem_of(card_path)
        card_stems.add(stem)
        _card, card_errors = validate_card(card_path, validator)
        errors.extend(card_errors)
        if stem not in registry_ids:
            errors.append(
                f"{card_path}: filename stem '{stem}' is not present in registry "
                f"({args.registry}); add a registry row or rename the card"
            )

    # Reverse direction: every registry agent_id must have a matching card.
    missing_cards = sorted(registry_ids - card_stems)
    for aid in missing_cards:
        errors.append(
            f"{args.cards_dir}/{aid}.card.json: missing Agent Card for registry agent_id '{aid}'"
        )

    # Output.
    print("=== ERRORS ===")
    if errors:
        for line in errors:
            print(line)
    else:
        print("(none)")

    print()
    print("=== SUMMARY ===")
    print(f"registry agent_ids : {len(registry_ids)}")
    print(f"card files found   : {len(card_files)}")
    print(f"cards validated    : {len(card_files)}")
    print(f"missing cards      : {len(missing_cards)}")
    print(f"total errors       : {len(errors)}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

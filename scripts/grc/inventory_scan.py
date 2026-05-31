#!/usr/bin/env python3
"""Scans stack sources for LLM-calling agents and diffs against the Agent
Registry (``.agents/registry.yaml``). Flags shadow agents (declared in source
but not registry) and orphan agents (in registry but not found in any
source). Walks 6 sources per RESEARCH D11: docker-compose, n8n exports, MCP
server files, ~/.claude/skills, openclaw.json registrations, and Python
regex grep for LLM constructors.

CLI:

    python3 scripts/grc/inventory_scan.py [--registry PATH]
                                          [--allow-list PATH]
                                          [--format human|json]
                                          [--fail-on-shadow]

Exit codes:

* 0 - scan completed; no shadow agents OR ``--fail-on-shadow`` not set
* 1 - ``--fail-on-shadow`` set and at least one shadow agent detected
* 2 - configuration error (missing registry, malformed allow-list, etc.)
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import yaml

# Repo root resolution: this file lives in scripts/grc/, so root is two dirs up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc.inventory_sources import SOURCES  # noqa: E402

SCANNER_VERSION = "1.0.0"

DEFAULT_REGISTRY = "scripts/grc/../../.agents/registry.yaml"
DEFAULT_ALLOW_LIST = "scripts/grc/inventory_allow_list.yaml"


def _load_registry(path: Path) -> List[str]:
    if not path.is_file():
        print(f"inventory_scan: registry not found at {path}", file=sys.stderr)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    rows = data.get("agents") or []
    if not isinstance(rows, list):
        print("inventory_scan: registry 'agents' must be a list", file=sys.stderr)
        sys.exit(2)
    declared = []
    for row in rows:
        if isinstance(row, dict) and "agent_id" in row:
            declared.append(str(row["agent_id"]))
    return declared


def _load_allow_list(path: Path) -> List[dict]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    entries = data.get("non_agents") or []
    if not isinstance(entries, list):
        print(
            f"inventory_scan: allow-list 'non_agents' must be a list in {path}",
            file=sys.stderr,
        )
        sys.exit(2)
    return [e for e in entries if isinstance(e, dict)]


def _match_allow(finding: dict, allow_list: Iterable[dict]) -> bool:
    for entry in allow_list:
        if entry.get("source") != finding.get("source"):
            continue
        rule = entry.get("agent_id", "")
        if rule == "*" or rule == finding.get("agent_id"):
            return True
    return False


def _run_sources(source_overrides: Dict[str, Any] | None = None) -> Dict[str, List[dict]]:
    """Invoke each registered source plugin and return a name -> findings map.

    ``source_overrides`` lets tests inject stub discover callables.
    """
    overrides = source_overrides or {}
    out: Dict[str, List[dict]] = {}
    for name, fn in SOURCES.items():
        discover = overrides.get(name, fn)
        try:
            result = discover()
        except Exception as exc:  # plugin must not crash the whole scan
            print(f"inventory_scan: source {name} raised {exc}", file=sys.stderr)
            result = []
        out[name] = [r for r in (result or []) if isinstance(r, dict)]
    return out


def _diff(
    findings_by_source: Dict[str, List[dict]],
    declared: Sequence[str],
    allow_list: Sequence[dict],
) -> Dict[str, Any]:
    declared_set = set(declared)
    seen_ids: set[str] = set()
    suppressed: List[dict] = []
    surviving: Dict[str, List[dict]] = {}

    for source_name, findings in findings_by_source.items():
        surviving[source_name] = []
        for finding in findings:
            if _match_allow(finding, allow_list):
                suppressed.append(finding)
                continue
            surviving[source_name].append(finding)
            agent_id = str(finding.get("agent_id", "")).strip()
            if agent_id:
                seen_ids.add(agent_id)

    shadow = sorted(seen_ids - declared_set)
    orphan = sorted(declared_set - seen_ids)
    return {
        "scanner_version": SCANNER_VERSION,
        "scanned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "shadow": shadow,
        "orphan": orphan,
        "by_source": surviving,
        "suppressed": suppressed,
        "registry_count": len(declared_set),
    }


def _render_human(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Agent Inventory Scan v{report['scanner_version']}")
    lines.append(f"Scanned at: {report['scanned_at']}")
    lines.append(f"Registry agents: {report['registry_count']}")
    lines.append("")

    shadow = report.get("shadow") or []
    lines.append("## Shadow Agents")
    if shadow:
        lines.append("")
        lines.append("| agent_id | sources |")
        lines.append("| --- | --- |")
        by_source = report.get("by_source", {})
        for agent_id in shadow:
            srcs = sorted(
                {
                    sname
                    for sname, fnds in by_source.items()
                    for f in fnds
                    if f.get("agent_id") == agent_id
                }
            )
            lines.append(f"| {agent_id} | {', '.join(srcs)} |")
    else:
        lines.append("None detected.")
    lines.append("")

    orphan = report.get("orphan") or []
    lines.append("## Orphan Agents (registry-only)")
    if orphan:
        lines.append("")
        for agent_id in orphan:
            lines.append(f"- {agent_id}")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Discoveries by Source")
    lines.append("")
    by_source = report.get("by_source", {})
    for source_name in sorted(by_source):
        findings = by_source[source_name]
        lines.append(f"### {source_name}")
        if not findings:
            lines.append("(no findings)")
            lines.append("")
            continue
        lines.append("")
        lines.append("| agent_id | evidence |")
        lines.append("| --- | --- |")
        for finding in findings:
            evidence = str(finding.get("evidence", "")).replace("|", "\\|")
            lines.append(f"| {finding.get('agent_id', '')} | {evidence} |")
        lines.append("")

    suppressed = report.get("suppressed") or []
    lines.append(f"## Suppressed by allow-list: {len(suppressed)} finding(s)")
    return "\n".join(lines) + "\n"


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Walk 6 sources, diff against .agents/registry.yaml, "
            "and flag shadow agents."
        ),
    )
    parser.add_argument(
        "--registry",
        default=str(REPO_ROOT / ".agents" / "registry.yaml"),
        help="Path to Agent Registry YAML.",
    )
    parser.add_argument(
        "--allow-list",
        default=str(REPO_ROOT / "scripts" / "grc" / "inventory_allow_list.yaml"),
        help="Path to inventory allow-list YAML.",
    )
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Report format.",
    )
    parser.add_argument(
        "--fail-on-shadow",
        action="store_true",
        help="Exit 1 if shadow agents are detected (CI mode).",
    )
    return parser


def run(
    registry_path: Path,
    allow_list_path: Path,
    source_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    declared = _load_registry(registry_path)
    allow_list = _load_allow_list(allow_list_path)
    findings_by_source = _run_sources(source_overrides=source_overrides)
    return _diff(findings_by_source, declared, allow_list)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    report = run(Path(args.registry), Path(args.allow_list))
    if args.format == "json":
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(_render_human(report))

    if args.fail_on_shadow and report.get("shadow"):
        print(
            "inventory_scan: shadow agents detected: "
            + ", ".join(report["shadow"]),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

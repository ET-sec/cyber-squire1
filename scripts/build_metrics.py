#!/usr/bin/env python3
"""
build_metrics.py — derive canonical numeric facts for cyber-squire1 from the filesystem.

Writes `metrics.yaml` at repo root. Every count is computed from disk, never copied
from existing claims in README or resume or portfolio. If a source doc disagrees with
metrics.yaml, the source doc is wrong.

Pairs with:
  - .githooks/pre-commit  -> runs this on every commit touching tracked source dirs
  - scripts/sync_portfolio.py  -> writes metrics.yaml values into portfolio HTML markers
  - ~/.claude/skills/gta/ Phase 11  -> uses metrics.yaml as the third source for 3-way diff
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = REPO_ROOT / "metrics.yaml"

# Owner-approved public values not derivable from disk (or where disk would mislead).
OWNER_APPROVED = {
    # Container count: the droplet runs N containers in flux; owner picked 20 as the
    # public number. See CLAUDE.md "20 owner-approved public count".
    "containers_public": 20,
    # n8n workflows: behind an HTTP API, not on disk. Owner-confirmed 14 active.
    "workflows_n8n_active": 14,
    # AI engine identifiers come from droplet config files, not always synced locally.
    "openclaw_model": "Claude Fable 5",
    "openclaw_model_id": "claude-fable-5",
    "ollama_model": "Qwen 3 8B",
    "whisper_engine": "faster-whisper",
}


@dataclass
class Metrics:
    generated_at: str = ""
    sources: dict = field(default_factory=dict)
    stack: dict = field(default_factory=dict)
    grc: dict = field(default_factory=dict)
    ai: dict = field(default_factory=dict)
    detection: dict = field(default_factory=dict)
    infra: dict = field(default_factory=dict)
    contact: dict = field(default_factory=dict)


def grep_count(pattern: str, paths: list[Path]) -> int:
    n = 0
    rx = re.compile(pattern, re.MULTILINE)
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        n += len(rx.findall(text))
    return n


def grep_unique(pattern: str, paths: list[Path]) -> set[str]:
    rx = re.compile(pattern)
    found: set[str] = set()
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        for m in rx.findall(text):
            found.add(m)
    return found


def list_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.glob(pattern) if p.is_file())


# ----------------------------------------------------------------------
# Section computers


def compute_grc() -> dict:
    grc_dir = REPO_ROOT / "docs" / "grc"
    md_files = list_files(grc_dir, "*.md")
    content_docs = [p for p in md_files if p.name != "README.md"]

    policies = list_files(grc_dir, "POLICY_*.md")
    playbooks = list_files(grc_dir, "PLAYBOOK_*.md")
    exec_summaries = [p for p in md_files if "EXEC" in p.name.upper()]
    tabletops = [
        p
        for p in md_files
        if re.search(r"(tabletop|TT_)", p.name, re.IGNORECASE)
    ]
    threat_models = [
        p
        for p in md_files
        if re.search(
            r"(threat|attack_tree|data_flow|stride)", p.name, re.IGNORECASE
        )
    ]

    ssp_files = list_files(grc_dir, "SSP_*.md")
    nist_unique = grep_unique(
        r"\b(?:AC|AT|AU|CA|CM|CP|IA|IR|MA|MP|PE|PL|PM|PS|PT|RA|SA|SC|SI|SR)-[0-9]+\b",
        ssp_files,
    )

    poam_register = grc_dir / "POAM_PLAN_OF_ACTION.md"
    poam_paths = [poam_register] if poam_register.exists() else []
    poam_base_ids = grep_unique(r"\bPOAM-0[0-9]{2}\b", poam_paths)
    poam_squire_ids = grep_unique(r"\bPOAM-P17-[0-9]+\b", poam_paths)
    poam_open = grep_count(r"\| OPEN ", poam_paths) + grep_count(
        r"Status\*\* \| Open", poam_paths
    )
    poam_closed = grep_count(r"\| CLOSED ", poam_paths) + grep_count(
        r"Status\*\* \| Closed", poam_paths
    )
    poam_accept = grep_count(r"Status\*\* \| Accepted Risk", poam_paths)

    # Threat-model entries
    stride_doc = grc_dir / "THREAT_MODEL_STRIDE.md"
    stride_count = grep_count(r"^### [STRIDE]-[0-9]+:", [stride_doc])

    ai_catalog = grc_dir / "AI_THREAT_CATALOG.md"
    ai_threat_ids = grep_unique(r"\bAI-T[0-9]+\b", [ai_catalog])

    attack_tree = grc_dir / "ATTACK_TREE_AI_PIPELINE.md"
    attack_paths_base = grep_count(
        r"^### 4\.[0-9]+ Path ", [attack_tree]
    )
    attack_paths_squire = grep_count(
        r"^### 6\.5\.[0-9]+ Root [A-Z]", [attack_tree]
    )

    dfd_doc = grc_dir / "DATA_FLOW_DIAGRAM.md"
    trust_boundaries_defined = (
        len(
            [
                line
                for line in (dfd_doc.read_text(encoding="utf-8") if dfd_doc.exists() else "").splitlines()
                if re.match(r"^\|\s*\*\*TB-[0-9]+\*\*", line)
            ]
        )
    )
    data_flows = len(grep_unique(r"\bDF-[0-9]+\b|\bF-[0-9]+\b", [dfd_doc]))

    return {
        "total_documents": len(content_docs),
        "total_files_including_index": len(md_files),
        "nist_800_53_controls_cited": len(nist_unique),
        "policies": len(policies),
        "ir_playbooks": len(playbooks),
        "threat_model_docs": len(threat_models),
        "tabletop_exercises": len(tabletops),
        "executive_summaries": len(exec_summaries),
        "poam_findings_total": len(poam_base_ids) + len(poam_squire_ids),
        "poam_findings_base_cis_checkov_ra": len(poam_base_ids),
        "poam_findings_squire_ai": len(poam_squire_ids),
        "poam_findings_open": poam_open,
        "poam_findings_closed": poam_closed,
        "poam_findings_accepted_risk": poam_accept,
        "stride_threats": stride_count,
        "ai_threats_cataloged": len(ai_threat_ids),
        "attack_paths_total": attack_paths_base + attack_paths_squire,
        "attack_paths_base": attack_paths_base,
        "attack_paths_squire_ai": attack_paths_squire,
        "trust_boundaries_defined": trust_boundaries_defined,
        "data_flows_cataloged": data_flows,
    }


def compute_infra() -> dict:
    tf_dir = REPO_ROOT / "terraform" / "cd-do-infrastructure"
    tf_files = list_files(tf_dir, "*.tf")
    opa_files: list[Path] = []
    if tf_dir.exists():
        opa_files = sorted(tf_dir.rglob("*.rego"))
    monitors = grep_count(r'^resource "datadog_monitor"', tf_files)
    dashboards = grep_count(r'^resource "datadog_dashboard"', tf_files)
    return {
        "terraform_files": len(tf_files),
        "opa_policies": len(opa_files),
        "datadog_monitors": monitors,
        "datadog_dashboards": dashboards,
    }


def compute_detection() -> dict:
    sigma_dir = REPO_ROOT / "detections"
    sigma_files: list[Path] = []
    if sigma_dir.exists():
        sigma_files = [p for p in sigma_dir.rglob("*.yml")] + [
            p for p in sigma_dir.rglob("*.yaml")
        ]
    return {
        "sigma_rules": len(sigma_files),
    }


def compute_stack() -> dict:
    wf_dir = REPO_ROOT / ".github" / "workflows"
    workflows = []
    if wf_dir.exists():
        workflows = sorted(
            list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        )
    return {
        "containers_public": OWNER_APPROVED["containers_public"],
        "workflows_n8n_active": OWNER_APPROVED["workflows_n8n_active"],
        "workflows_github_actions": len(workflows),
    }


def compute_ai() -> dict:
    return {
        "openclaw_model": OWNER_APPROVED["openclaw_model"],
        "openclaw_model_id": OWNER_APPROVED["openclaw_model_id"],
        "ollama_model": OWNER_APPROVED["ollama_model"],
        "whisper_engine": OWNER_APPROVED["whisper_engine"],
    }


def compute_contact() -> dict:
    return {
        "email": "etigoue@tigouetheory.com",
        "github": "ET-sec",
        "portfolio_url": "https://et-sec.github.io/portfolio/",
        "linkedin": "https://www.linkedin.com/in/emmanuel-tigoue",
    }


# ----------------------------------------------------------------------
# YAML emitter (no PyYAML dep)


def emit_yaml(m: Metrics) -> str:
    out: list[str] = []
    out.append("# metrics.yaml: canonical numeric facts derived from filesystem.")
    out.append("# Regenerate via: python3 scripts/build_metrics.py")
    out.append("# Pre-commit hook auto-runs this when source dirs change.")
    out.append("# Do not hand-edit: changes will be overwritten.")
    out.append("")
    out.append(f"generated_at: '{m.generated_at}'")
    out.append("generator: build_metrics.py")
    out.append("version: 1")
    out.append("")

    out.append("sources:")
    for k, v in sorted(m.sources.items()):
        out.append(f"  {k}: {v!r}" if isinstance(v, str) else f"  {k}: {v}")
    out.append("")

    for section_name, section in (
        ("stack", m.stack),
        ("grc", m.grc),
        ("ai", m.ai),
        ("detection", m.detection),
        ("infra", m.infra),
        ("contact", m.contact),
    ):
        out.append(f"{section_name}:")
        for k, v in section.items():
            if isinstance(v, str):
                if any(c in v for c in ":#'\""):
                    v_repr = '"' + v.replace('"', '\\"') + '"'
                else:
                    v_repr = f'"{v}"'
                out.append(f"  {k}: {v_repr}")
            else:
                out.append(f"  {k}: {v}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    m = Metrics()
    m.generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    m.sources = {
        "filesystem_root": str(REPO_ROOT),
        "ssp_source": "docs/grc/SSP_*.md",
        "poam_source": "docs/grc/POAM_PLAN_OF_ACTION.md",
        "terraform_source": "terraform/cd-do-infrastructure/",
        "detections_source": "detections/",
        "workflows_source": ".github/workflows/",
    }
    m.stack = compute_stack()
    m.grc = compute_grc()
    m.ai = compute_ai()
    m.detection = compute_detection()
    m.infra = compute_infra()
    m.contact = compute_contact()

    yaml_text = emit_yaml(m)

    if "--check" in sys.argv:
        if not METRICS_PATH.exists():
            print(f"metrics.yaml missing at {METRICS_PATH}", file=sys.stderr)
            return 2
        current = METRICS_PATH.read_text(encoding="utf-8")
        # Strip generated_at line from both before compare (only that line varies).
        def strip_ts(text: str) -> str:
            return re.sub(r"^generated_at:.*$", "", text, flags=re.MULTILINE)

        if strip_ts(current) != strip_ts(yaml_text):
            print("metrics.yaml is STALE. Rerun: python3 scripts/build_metrics.py")
            return 1
        print("metrics.yaml is up to date.")
        return 0

    if "--json" in sys.argv:
        print(
            json.dumps(
                {
                    "stack": m.stack,
                    "grc": m.grc,
                    "ai": m.ai,
                    "detection": m.detection,
                    "infra": m.infra,
                    "contact": m.contact,
                },
                indent=2,
            )
        )
        return 0

    METRICS_PATH.write_text(yaml_text, encoding="utf-8")
    print(f"wrote {METRICS_PATH.relative_to(REPO_ROOT)}")
    print(f"  grc.total_documents = {m.grc['total_documents']}")
    print(f"  grc.nist_800_53_controls_cited = {m.grc['nist_800_53_controls_cited']}")
    print(f"  grc.poam_findings_total = {m.grc['poam_findings_total']}")
    print(f"  infra.terraform_files = {m.infra['terraform_files']}")
    print(f"  infra.datadog_monitors = {m.infra['datadog_monitors']}")
    print(f"  detection.sigma_rules = {m.detection['sigma_rules']}")
    print(f"  stack.workflows_github_actions = {m.stack['workflows_github_actions']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""n8n workflow source plugin.

Reads exported workflow JSON files from ``Agent_Squire/n8n_exports/*.json``
and maps each workflow id to a registered agent_id via ``WORKFLOW_ID_MAP``.
Unknown workflow ids surface as findings with ``UNMAPPED workflow id`` in
evidence so the reviewer either adds the agent to the registry or extends
the map.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List

DEFAULT_EXPORTS_DIR = "Agent_Squire/n8n_exports"

# n8n workflow id -> registered agent_id. Source of truth: CLAUDE.md +
# 20-01 SUMMARY (registry rows for master_orchestrator,
# n8n_telegram_supervisor, n8n_content_research, n8n_gmail_readers).
WORKFLOW_ID_MAP = {
    "UIf3v1ZNN98OtUge": "master_orchestrator",
    "iO6PfPdk0SSPBTWb": "n8n_telegram_supervisor",
    "nhtwRpJATQoaZpxL": "n8n_content_research",
    # Four Gmail readers consolidate into a single registry row.
    "2A0O7MzPvUCCYoLV": "n8n_gmail_readers",
    "wTUraUYjsHXCGWgr": "n8n_gmail_readers",
    "NxoxcIcYRo0XPkOz": "n8n_gmail_readers",
    "yLA81NXy9LBvps8m": "n8n_gmail_readers",
}


def _snake(name: str) -> str:
    """Convert a human workflow name to snake_case."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return cleaned or "unknown_workflow"


def discover(exports_dir: str | Path | None = None) -> List[dict]:
    """Return findings for every workflow JSON file in ``exports_dir``."""
    base = Path(exports_dir) if exports_dir else Path(DEFAULT_EXPORTS_DIR)
    if not base.is_dir():
        print(
            f"inventory_sources.n8n_workflows: no workflow exports staged at {base}",
            file=sys.stderr,
        )
        return []

    findings: List[dict] = []
    for path in sorted(base.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(
                f"inventory_sources.n8n_workflows: skip {path}: {exc}",
                file=sys.stderr,
            )
            continue

        workflows: List[dict]
        if isinstance(payload, list):
            workflows = [w for w in payload if isinstance(w, dict)]
        elif isinstance(payload, dict) and "id" in payload:
            workflows = [payload]
        elif isinstance(payload, dict) and isinstance(payload.get("workflows"), list):
            workflows = [w for w in payload["workflows"] if isinstance(w, dict)]
        else:
            continue

        for wf in workflows:
            wf_id = str(wf.get("id", "")).strip()
            wf_name = str(wf.get("name", "")).strip() or "<unnamed>"
            if wf_id in WORKFLOW_ID_MAP:
                findings.append(
                    {
                        "agent_id": WORKFLOW_ID_MAP[wf_id],
                        "source": "n8n_workflows",
                        "evidence": (
                            f"n8n workflow id={wf_id} name='{wf_name}' "
                            f"(file: {path.name})"
                        ),
                    }
                )
            else:
                findings.append(
                    {
                        "agent_id": _snake(wf_name) if wf_name != "<unnamed>" else _snake(wf_id),
                        "source": "n8n_workflows",
                        "evidence": (
                            f"UNMAPPED workflow id={wf_id} name='{wf_name}' "
                            f"(file: {path.name}); add to WORKFLOW_ID_MAP or registry"
                        ),
                    }
                )
    return findings

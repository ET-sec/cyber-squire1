"""Claude Desktop / Claude Code skill source plugin.

Walks ``~/.claude/skills/`` (override via ``CLAUDE_SKILLS_ROOT``) and emits a
finding for every skill directory containing ``SKILL.md`` or ``skill.json``.

Skills are usually NOT first-class agents - they are tools an agent invokes.
The default allow-list in ``inventory_allow_list.yaml`` suppresses every
finding from this source with a documented wildcard. The source still runs so
that anyone reviewing the allow-list can see what was scanned.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List

DEFAULT_SKILLS_ROOT = "~/.claude/skills"


def _snake(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return cleaned or "unknown_skill"


def discover(skills_root: str | Path | None = None) -> List[dict]:
    """Return one finding per Claude skill directory."""
    raw = str(skills_root) if skills_root else os.environ.get(
        "CLAUDE_SKILLS_ROOT", DEFAULT_SKILLS_ROOT
    )
    root = Path(os.path.expanduser(raw))
    if not root.is_dir():
        print(
            f"inventory_sources.claude_skills: {root} not found; skipping",
            file=sys.stderr,
        )
        return []

    findings: List[dict] = []
    for skill_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if not ((skill_dir / "SKILL.md").is_file()
                or (skill_dir / "skill.json").is_file()):
            continue
        findings.append(
            {
                "agent_id": _snake(skill_dir.name),
                "source": "claude_skills",
                "evidence": f"Claude skill: {skill_dir.name}",
                "is_likely_agent": False,
            }
        )
    return findings

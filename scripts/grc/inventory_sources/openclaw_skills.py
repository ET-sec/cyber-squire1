"""OpenClaw gateway skill source plugin (RESEARCH D11 source e).

Reads the OpenClaw config (``/root/moltbot/config-dir/openclaw.json`` on the
droplet; ``OPENCLAW_CONFIG_PATH`` to override for local dev) and emits a
finding for every registered skill / tool that is NOT a known ClawHub
built-in.

Each project-owned skill registered with OpenClaw grants the gateway a new
capability surface. A skill added to openclaw.json without a corresponding
registry entry is a shadow agent vector, so this source is marked
``is_likely_agent=True``.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List

DEFAULT_CONFIG_PATH = "/root/moltbot/config-dir/openclaw.json"

# Skills documented in CLAUDE.md as ClawHub upstream / built-in. Project work
# does not need to re-declare these; suppress them to avoid CI noise.
BUILT_IN_OPENCLAW_SKILLS = frozenset(
    {
        "tavily-search",
        "browser",
        "python-interpreter",
        "notion",
        "gemini",
        "github",
    }
)


def _snake(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return cleaned or "unknown_skill"


def _iter_registered(payload: dict) -> Iterable[dict]:
    """Yield each registered skill / tool entry, regardless of openclaw schema
    quirks (some versions key on ``skills``, others on ``tools``)."""
    for key in ("skills", "tools"):
        value = payload.get(key)
        if isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict):
                    yield entry
                elif isinstance(entry, str):
                    yield {"name": entry}
        elif isinstance(value, dict):
            for skill_name, entry in value.items():
                if isinstance(entry, dict):
                    merged = {"name": skill_name, **entry}
                    yield merged
                else:
                    yield {"name": skill_name}


def discover(config_path: str | Path | None = None) -> List[dict]:
    raw = str(config_path) if config_path else os.environ.get(
        "OPENCLAW_CONFIG_PATH", DEFAULT_CONFIG_PATH
    )
    path = Path(os.path.expanduser(raw))
    if not path.is_file():
        print(
            f"inventory_sources.openclaw_skills: {path} not found; skipping",
            file=sys.stderr,
        )
        return []

    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"inventory_sources.openclaw_skills: cannot parse {path}: {exc}",
            file=sys.stderr,
        )
        return []
    if not isinstance(payload, dict):
        return []

    findings: List[dict] = []
    seen: set[str] = set()
    for entry in _iter_registered(payload):
        name = str(entry.get("name", "")).strip()
        if not name or name in BUILT_IN_OPENCLAW_SKILLS:
            continue
        if name in seen:
            continue
        seen.add(name)
        findings.append(
            {
                "agent_id": _snake(name),
                "source": "openclaw_skills",
                "evidence": f"openclaw.json skill: {name}",
                "is_likely_agent": True,
            }
        )
    return findings

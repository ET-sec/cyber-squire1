"""Observe Squire agents: subdir names under Agent_Squire/agents/."""
from __future__ import annotations

from .base import Context, Drift, Observer
from ._common import log, safe_under


class AgentsObserver(Observer):
    name = "agents"
    is_remote = False

    def observe(self, ctx: Context) -> list[Drift]:
        p = safe_under(ctx.base_dir / "Agent_Squire" / "agents", ctx.base_dir)
        agents = sorted([d.name for d in p.iterdir() if d.is_dir() and not d.is_symlink()])
        log("observation.fs", root=str(p), file_count=len(agents))
        expected = sorted(a["id"] for a in ctx.facts["ai_security"]["agents"])
        if expected == agents:
            return []
        return [Drift(key="ai_security.agents", yaml=expected, real=agents)]


OBSERVER = AgentsObserver()

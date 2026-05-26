"""Observe IR playbook count: PLAYBOOK_*.md in docs/grc/."""
from __future__ import annotations

from .base import Context, Drift, Observer
from ._common import log, safe_under


class IrPlaybooksObserver(Observer):
    name = "ir_playbooks"
    is_remote = False

    def observe(self, ctx: Context) -> list[Drift]:
        p = safe_under(ctx.base_dir / "docs" / "grc", ctx.base_dir)
        count = sum(1 for _ in p.glob("PLAYBOOK_*.md"))
        log("observation.fs", root=str(p), file_count=count, pattern="PLAYBOOK_*.md")
        expected = ctx.facts["grc"]["ir_playbooks"]
        if expected == count:
            return []
        return [Drift(key="grc.ir_playbooks", yaml=expected, real=count)]


OBSERVER = IrPlaybooksObserver()

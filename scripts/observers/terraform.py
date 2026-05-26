"""Observe Terraform file count: *.tf in terraform/cd-do-infrastructure/ (top-level)."""
from __future__ import annotations

from .base import Context, Drift, Observer
from ._common import log, safe_under


class TerraformObserver(Observer):
    name = "terraform"
    is_remote = False

    def observe(self, ctx: Context) -> list[Drift]:
        p = safe_under(ctx.base_dir / "terraform" / "cd-do-infrastructure", ctx.base_dir)
        count = sum(1 for _ in p.glob("*.tf"))
        log("observation.fs", root=str(p), file_count=count, pattern="*.tf")
        expected = ctx.facts["infrastructure"]["terraform_files"]
        if expected == count:
            return []
        return [Drift(key="infrastructure.terraform_files", yaml=expected, real=count)]


OBSERVER = TerraformObserver()

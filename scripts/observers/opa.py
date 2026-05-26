"""Observe OPA Rego policy count: *.rego under terraform/ recursively."""
from __future__ import annotations

from .base import Context, Drift, Observer
from ._common import log, safe_under


class OpaObserver(Observer):
    name = "opa"
    is_remote = False

    def observe(self, ctx: Context) -> list[Drift]:
        p = safe_under(ctx.base_dir / "terraform", ctx.base_dir)
        count = sum(1 for _ in p.rglob("*.rego") if not _.is_symlink())
        log("observation.fs", root=str(p), file_count=count, pattern="*.rego")
        expected = ctx.facts["infrastructure"]["opa_rego_policies"]
        if expected == count:
            return []
        return [Drift(key="infrastructure.opa_rego_policies", yaml=expected, real=count)]


OBSERVER = OpaObserver()

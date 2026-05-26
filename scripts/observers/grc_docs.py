"""Observe GRC document count: count *.md in docs/grc/ (top-level)."""
from __future__ import annotations

import datetime as dt

from .base import Context, Drift, Observer
from ._common import log, safe_under


class GrcDocsObserver(Observer):
    name = "grc_docs"
    is_remote = False

    def observe(self, ctx: Context) -> list[Drift]:
        start = dt.datetime.now()
        p = safe_under(ctx.base_dir / "docs" / "grc", ctx.base_dir)
        count = sum(1 for _ in p.glob("*.md"))
        dur = int((dt.datetime.now() - start).total_seconds() * 1000)
        log("observation.fs", root=str(p), file_count=count, duration_ms=dur)
        expected = ctx.facts["grc"]["total_documents"]
        if expected == count:
            return []
        return [Drift(key="grc.total_documents", yaml=expected, real=count)]


OBSERVER = GrcDocsObserver()

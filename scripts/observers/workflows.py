"""Observe n8n workflow counts via ssh + docker exec psql. Emits 2 drift keys."""
from __future__ import annotations

import json
import logging
import re
import subprocess
import sys

from .base import Context, Drift, Observer
from ._common import get_secret, log, minimal_env, ssh_opts


class WorkflowsObserver(Observer):
    name = "workflows"
    is_remote = True

    def observe(self, ctx: Context) -> list[Drift]:
        if ctx.skip_remote:
            return []
        user = get_secret("CD_DB_USER")
        db = get_secret("CD_DB_NAME")
        if not re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{1,40}$", user):
            sys.exit(4)
        if not re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_]{1,40}$", db):
            sys.exit(4)
        sql = "SELECT COUNT(*), COUNT(*) FILTER (WHERE active=true) FROM workflow_entity;"
        remote = (
            f"docker exec cd-service-db psql -U {user} -d {db} -t -A -c "
            + json.dumps(sql)
        )
        try:
            r = subprocess.run(
                ssh_opts(ctx.ssh_target) + [remote],
                capture_output=True, text=True, timeout=20, check=True,
                shell=False, env=minimal_env(),
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log("observation.pg.error", logging.ERROR, error=type(e).__name__,
                stderr=getattr(e, "stderr", "")[:200] if hasattr(e, "stderr") else "")
            sys.exit(3)
        line = r.stdout.strip()
        m = re.fullmatch(r"^(\d+)\|(\d+)$", line)
        if not m:
            log("observation.pg.parse_fail", logging.ERROR, raw=line[:80])
            sys.exit(3)
        total, active = int(m.group(1)), int(m.group(2))
        log("observation.pg", query_id="n8n_workflow_counts", row_count=2)

        out: list[Drift] = []
        exp_tot = ctx.facts["soar"]["workflows_total"]
        exp_act = ctx.facts["soar"]["workflows_active"]
        if exp_tot != total:
            out.append(Drift(key="soar.workflows_total", yaml=exp_tot, real=total))
        if exp_act != active:
            out.append(Drift(key="soar.workflows_active", yaml=exp_act, real=active))
        return out


OBSERVER = WorkflowsObserver()

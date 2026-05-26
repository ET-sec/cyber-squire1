"""Observe droplet container counts via ssh + docker ps. Emits 2 drift keys."""
from __future__ import annotations

import logging
import subprocess
import sys

from .base import Context, Drift, Observer
from ._common import log, minimal_env, ssh_opts


class ContainersObserver(Observer):
    name = "containers"
    is_remote = True

    def observe(self, ctx: Context) -> list[Drift]:
        if ctx.skip_remote:
            return []
        try:
            running = subprocess.run(
                ssh_opts(ctx.ssh_target) + ["docker ps --format '{{json .}}'"],
                capture_output=True, text=True, timeout=30, check=True,
                shell=False, env=minimal_env(),
            )
            total = subprocess.run(
                ssh_opts(ctx.ssh_target) + ["docker ps -a --format '{{json .}}'"],
                capture_output=True, text=True, timeout=30, check=True,
                shell=False, env=minimal_env(),
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log("observation.ssh.error", logging.ERROR, error=type(e).__name__,
                stderr=getattr(e, "stderr", "")[:200] if hasattr(e, "stderr") else "")
            sys.exit(3)
        run_count = sum(1 for line in running.stdout.splitlines() if line.strip())
        tot_count = sum(1 for line in total.stdout.splitlines() if line.strip())
        log("observation.ssh", target=ctx.ssh_target, cmd_basename="docker ps", exit=0)

        out: list[Drift] = []
        exp_run = ctx.facts["infrastructure"]["containers_running"]
        exp_tot = ctx.facts["infrastructure"]["containers_total"]
        if exp_run != run_count:
            out.append(Drift(key="infrastructure.containers_running", yaml=exp_run, real=run_count))
        if exp_tot != tot_count:
            out.append(Drift(key="infrastructure.containers_total", yaml=exp_tot, real=tot_count))
        return out


OBSERVER = ContainersObserver()

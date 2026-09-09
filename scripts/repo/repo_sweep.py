#!/usr/bin/env python3
"""repo_sweep.py: every mechanical gate in one command, printing only failures.

The point of this script is that a clean run is quiet. Scripts find the
mechanical faults so a reader spends attention on meaning instead of on
counting. A gate that passes prints nothing. A gate that fails prints its name,
the command that failed, and that command's output. A gate that cannot run here
prints ``SKIP`` and a reason, and is never counted as a pass, because reporting
an unavailable gate as a pass is the failure this whole sweep exists to prevent.

The logic lives here, in a tracked file, rather than in the ``/repo-sweep``
skill, because ``.claude/`` is gitignored: logic there could never be reviewed,
tested, or run by CI. The skill is a wrapper that calls this.

CLI::

    python3 scripts/repo/repo_sweep.py [--portfolio PATH] [--links] [--regen]
                                       [--root PATH] [--format human|json]

Exit codes::

    0 - every available gate passed
    1 - at least one gate failed
    2 - configuration error (a gate is missing from the tree entirely)

Gates called, in order:

===========================  ============================================================
gate                         command
===========================  ============================================================
manifest                     scripts/repo/manifest_check.py
readme markers               scripts/repo/gen_folder_readmes.py --check
repo price tier              scripts/site/check_public.py --repo --repo-checks price
repo opsec                   deliberately skipped, see below
internal links               scripts/grc/validate_grc.py --only links --links-scope repo
writing tells                ~/.claude/skills/gta/scripts/sweep_ai_tells.py <tracked md>
site public                  scripts/site/check_public.py --portfolio PATH
metric markers               scripts/sync_portfolio.py --portfolio-root PATH
view and node markers        scripts/sync_views.py --check --portfolio PATH
external links               scripts/site/check_public.py --portfolio PATH --links-only
views reproduce              docs/architecture/views/render_views.py, then git diff
===========================  ============================================================

Two gates are deliberately OUT of this sweep:

* ``scripts/verify-facts.py`` needs SSH to the host, Postgres, n8n, and Doppler,
  and documents exit codes 3 and 4 for exactly those failures. It is a live
  drift detector, not a repository gate. Calling it would make the sweep fail on
  a laptop with no network, which trains a reader to ignore a red result.
* ``gitleaks`` is already fail-closed in ``.githooks/pre-commit``,
  ``.githooks/pre-push``, and ``security.yml``. A fourth run adds latency, and
  both hooks refuse to run at all without ``.gitleaks.local.toml``, which is
  gitignored and absent on a CI runner.

Three gates report as unavailable rather than as a pass:

* **repo opsec.** ``check_public.py --repo`` runs an OPSEC pattern list written
  for a published web page. Over this repository's tracked tree it reports 1437
  hits and none of them is a leak: GitHub Actions SHA pins, which are the
  supply-chain control; the sanitized 10.100.x addresses the GRC library prints
  on purpose; ``cd-service-*`` container names the compose file and the runbooks
  name; and ``/opt`` and ``/root`` paths in host runbooks. Narrowing the list for
  repository scope is real work with a real risk of suppressing a real
  identifier, so it is recorded rather than guessed at, and this sweep calls the
  price-tier subset while naming the half it is not running.
* **the portfolio gates**, when there is no portfolio checkout at the given path.
* **views reproduce**, unless ``--regen`` is passed. Regenerating writes into
  ``docs/architecture/views/``, and a sweep that edits the working tree is not a
  sweep.

``--links`` opts into the network gate. Without it the external link check is
skipped with a reason, matching how ``portfolio-sync.yml`` runs it with
``continue-on-error``.

The writing tells sweep never signals failure: it prints its findings and falls
off the end of ``main()`` with no ``sys.exit``, so the process exits 0 whether it
found two hundred dash characters or none. ``.githooks/pre-commit`` works around
that by grepping stdout for ``em=[1-9]``, ``en=[1-9]``, ``dashes=[1-9]`` to
block, and separately for ``ai_tells=`` and ``juxt=`` to warn without blocking.
This script parses the same tokens and applies the same split, so the sweep and
the hook never disagree about whether a file is committable. Fenced code is not
exempt here for the same reason: the hook does not exempt it, and a file the hook
would block has to read as a failure here too.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
from typing import Callable, List, Optional, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TELLS_SWEEP = pathlib.Path.home() / ".claude" / "skills" / "gta" / "scripts" / "sweep_ai_tells.py"

# The same tokens .githooks/pre-commit greps for, with the same split.
TELLS_FAIL_RE = re.compile(r"(?:^|\s)(?:em|en|dashes)=[1-9]")
TELLS_WARN_RE = re.compile(r"(?:^|\s)(?:ai_tells|juxt)=")

# A gate whose script is not in the tree is a configuration error, not a skip.
REQUIRED_SCRIPTS = (
    "scripts/repo/manifest_check.py",
    "scripts/repo/gen_folder_readmes.py",
    "scripts/site/check_public.py",
    "scripts/grc/validate_grc.py",
)

OPSEC_SKIP_REASON = (
    "the OPSEC pattern list in check_public.py was written for a published web page; "
    "over a repository tree it reports the repository documenting itself (Actions SHA "
    "pins, the sanitized 10.100.x block, cd-service-* names, /opt and /root runbook "
    "paths). Narrowing it is recorded for plan 21-12. The price-tier half of that scope "
    "did run, above"
)

PASS, FAIL, SKIP = "pass", "fail", "skip"


class Result:
    """One gate's outcome. ``warnings`` never changes the status."""

    def __init__(
        self,
        name: str,
        status: str,
        command: str = "",
        code: Optional[int] = None,
        output: str = "",
        reason: str = "",
        warnings: Sequence[str] = (),
    ) -> None:
        self.name = name
        self.status = status
        self.command = command
        self.code = code
        self.output = output
        self.reason = reason
        self.warnings = list(warnings)

    def as_dict(self) -> dict:
        return {
            "gate": self.name,
            "status": self.status,
            "command": self.command,
            "exit_code": self.code,
            "output": self.output,
            "reason": self.reason,
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# Running things
# ---------------------------------------------------------------------------
def run(argv: Sequence[str], cwd: pathlib.Path) -> tuple[int, str]:
    proc = subprocess.run(
        [str(a) for a in argv], cwd=str(cwd), capture_output=True, text=True
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def shown(argv: Sequence[str], root: pathlib.Path) -> str:
    """The command as a person would retype it, with absolute paths shortened."""
    parts = []
    for a in argv:
        a = str(a)
        if a == sys.executable:
            a = "python3"
        elif a.startswith(str(root) + os.sep):
            a = a[len(str(root)) + 1 :]
        parts.append(a)
    return " ".join(parts)


def script_gate(
    name: str, root: pathlib.Path, argv: Sequence[str]
) -> Result:
    code, out = run(argv, root)
    cmd = shown(argv, root)
    if code == 0:
        return Result(name, PASS, cmd, code)
    return Result(name, FAIL, cmd, code, out)


def tracked(root: pathlib.Path) -> List[str]:
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True
    )
    if proc.returncode != 0:
        return []
    return [p for p in proc.stdout.split("\n") if p]


# ---------------------------------------------------------------------------
# The gates that need more than a subprocess call
# ---------------------------------------------------------------------------
def gate_tells(root: pathlib.Path) -> Result:
    name = "writing tells"
    if not TELLS_SWEEP.is_file():
        return Result(name, SKIP, reason=f"no tells sweep at {TELLS_SWEEP}")
    files = [p for p in tracked(root) if p.endswith(".md")]
    if not files:
        return Result(name, SKIP, reason="no tracked markdown under the root")
    argv = [sys.executable, str(TELLS_SWEEP), *files]
    code, out = run(argv, root)
    cmd = f"python3 {TELLS_SWEEP} $(git ls-files '*.md')"
    if code != 0:
        return Result(name, FAIL, cmd, code, out)
    # The sweeper always exits 0, so the classification is in its stdout.
    fails, warns = [], []
    for line in out.splitlines():
        if TELLS_FAIL_RE.search(line):
            fails.append(line)
        elif TELLS_WARN_RE.search(line):
            warns.append(line)
    if fails:
        return Result(name, FAIL, cmd, code, "\n".join(fails), warnings=warns)
    return Result(name, PASS, cmd, code, warnings=warns)


def gate_views_regen(root: pathlib.Path, enabled: bool) -> Result:
    name = "views reproduce"
    rel = "docs/architecture/views"
    script = root / rel / "render_views.py"
    if not enabled:
        return Result(
            name,
            SKIP,
            reason=f"--regen not set; regenerating writes into {rel}/",
        )
    if not script.is_file():
        return Result(name, SKIP, reason=f"no render_views.py under {root / rel}")
    code, dirty = run(["git", "status", "--porcelain", "--", rel], root)
    if dirty.strip():
        return Result(
            name,
            SKIP,
            reason=f"uncommitted changes under {rel}/ would read as regeneration drift",
        )
    argv = [sys.executable, str(script)]
    cmd = shown(argv, root) + f" && git diff --exit-code -- {rel}/"
    code, out = run(argv, root)
    if code != 0:
        return Result(name, FAIL, cmd, code, out)
    code, out = run(["git", "diff", "--exit-code", "--", rel], root)
    if code != 0:
        return Result(name, FAIL, cmd, code, out)
    return Result(name, PASS, cmd, 0)


# ---------------------------------------------------------------------------
# The gate list
# ---------------------------------------------------------------------------
def collect(
    root: pathlib.Path,
    portfolio: Optional[pathlib.Path],
    want_links: bool,
    want_regen: bool,
) -> List[Result]:
    py = sys.executable
    results: List[Result] = [
        script_gate(
            "manifest", root, [py, root / "scripts/repo/manifest_check.py", "--root", root]
        ),
        script_gate(
            "readme markers",
            root,
            [py, root / "scripts/repo/gen_folder_readmes.py", "--root", root, "--check"],
        ),
        script_gate(
            "repo price tier",
            root,
            [py, root / "scripts/site/check_public.py", "--repo", "--repo-checks", "price"],
        ),
        Result("repo opsec", SKIP, reason=OPSEC_SKIP_REASON),
        script_gate(
            "internal links",
            root,
            [
                py,
                root / "scripts/grc/validate_grc.py",
                "--only",
                "links",
                "--links-scope",
                "repo",
            ],
        ),
        gate_tells(root),
    ]

    have_portfolio = portfolio is not None and (portfolio / "index.html").is_file()
    why_no_portfolio = (
        f"no index.html under {portfolio}" if portfolio is not None else "no portfolio path"
    )

    def portfolio_gate(name: str, argv: Sequence[str], script: str) -> Result:
        if not have_portfolio:
            return Result(name, SKIP, reason=why_no_portfolio)
        if not (root / script).is_file():
            return Result(name, SKIP, reason=f"no {script} under {root}")
        return script_gate(name, root, argv)

    results.append(
        portfolio_gate(
            "site public",
            [py, root / "scripts/site/check_public.py", "--portfolio", portfolio],
            "scripts/site/check_public.py",
        )
    )
    results.append(
        portfolio_gate(
            "metric markers",
            [py, root / "scripts/sync_portfolio.py", "--portfolio-root", portfolio],
            "scripts/sync_portfolio.py",
        )
    )
    results.append(
        portfolio_gate(
            "view and node markers",
            [py, root / "scripts/sync_views.py", "--check", "--portfolio", portfolio],
            "scripts/sync_views.py",
        )
    )
    if not want_links:
        results.append(
            Result(
                "external links",
                SKIP,
                reason="--links not set; the external link check needs network",
            )
        )
    else:
        results.append(
            portfolio_gate(
                "external links",
                [
                    py,
                    root / "scripts/site/check_public.py",
                    "--portfolio",
                    portfolio,
                    "--links-only",
                ],
                "scripts/site/check_public.py",
            )
        )
    results.append(gate_views_regen(root, want_regen))
    return results


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def indent(text: str) -> str:
    return "\n".join("    " + line for line in text.splitlines() if line.strip())


def report_human(results: Sequence[Result]) -> List[str]:
    out: List[str] = []
    for r in results:
        if r.status != FAIL:
            continue
        out.append(f"FAIL {r.name}")
        out.append(f"  $ {r.command}")
        if r.output:
            out.append(indent(r.output))
    for r in results:
        if not r.warnings:
            continue
        out.append(f"warn {r.name}")
        out.append(indent("\n".join(r.warnings)))
    for r in results:
        if r.status == SKIP:
            out.append(f"SKIP {r.name}: {r.reason}")
    ran = sum(1 for r in results if r.status in (PASS, FAIL))
    failed = sum(1 for r in results if r.status == FAIL)
    skipped = sum(1 for r in results if r.status == SKIP)
    out.append(f"summary: {ran} gate(s) ran, {failed} failed, {skipped} skipped")
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Run every mechanical gate over this repository and print only what "
            "failed. A skipped gate is reported, never counted as a pass."
        )
    )
    ap.add_argument(
        "--portfolio",
        default=None,
        help="portfolio checkout the site gates read (default ~/portfolio)",
    )
    ap.add_argument(
        "--links",
        action="store_true",
        help="also run the external link check, which needs network",
    )
    ap.add_argument(
        "--regen",
        action="store_true",
        help="also regenerate the architecture views and diff them; this writes into the tree",
    )
    ap.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help="repository root to sweep (default: this checkout)",
    )
    ap.add_argument("--format", choices=("human", "json"), default="human")
    a = ap.parse_args(argv)

    root = pathlib.Path(a.root).resolve()
    code, _ = run(["git", "-C", str(root), "rev-parse", "--git-dir"], root)
    if code != 0:
        print(f"repo_sweep: {root} is not a git repository", file=sys.stderr)
        return 2
    missing = [s for s in REQUIRED_SCRIPTS if not (root / s).is_file()]
    if missing:
        for s in missing:
            print(f"repo_sweep: gate script missing from the tree: {s}", file=sys.stderr)
        return 2

    portfolio = (
        pathlib.Path(a.portfolio).expanduser()
        if a.portfolio is not None
        else pathlib.Path(os.path.expanduser("~/portfolio"))
    )
    results = collect(root, portfolio, a.links, a.regen)

    if a.format == "json":
        failed = sum(1 for r in results if r.status == FAIL)
        print(
            json.dumps(
                {
                    "root": str(root),
                    "gates": [r.as_dict() for r in results],
                    "counts": {
                        "ran": sum(1 for r in results if r.status in (PASS, FAIL)),
                        "failed": failed,
                        "skipped": sum(1 for r in results if r.status == SKIP),
                    },
                },
                indent=2,
            )
        )
        return 1 if failed else 0

    lines = report_human(results)
    print("\n".join(lines))
    return 1 if any(r.status == FAIL for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

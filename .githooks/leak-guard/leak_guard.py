#!/usr/bin/env python3
"""Leak guard for public showcase repos: refuse a push whose new commits carry private material.

Reads the pre-push stdin lines (<local ref> <local sha> <remote ref> <remote sha>), collects the
commits being pushed, and checks each one against deny.txt: path rules, added-line rules and a
size cap. Then runs gitleaks over the same commits. Fails closed: a missing rule file, a parse
error or a missing gitleaks refuses the push. Never prints a matched line's content, only the
commit, path, line number and rule id.

Usage (from a pre-push hook): leak_guard.py [--deny PATH ...] < pre-push-stdin
--deny may repeat; the files are merged (an allow rule may name deny ids from any of them).
Default: deny.txt beside this script. LEAK_GUARD_DENY (os.pathsep list) overrides both.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

ZERO = "0" * 40
DEFAULT_DENY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deny.txt")


@dataclass
class Rules:
    deny: list[tuple[str, re.Pattern]] = field(default_factory=list)
    allow: list[tuple[str, re.Pattern]] = field(default_factory=list)
    line: list[tuple[str, re.Pattern]] = field(default_factory=list)
    maxbytes: int | None = None
    baseline: set[tuple[str, str, str]] = field(default_factory=set)  # (repo, path, sha256 of line)


def load_rules(paths: list[str]) -> Rules:
    rules = Rules()
    for path in paths:
        _load_file(rules, path)
    if not rules.deny:
        raise ValueError(f"{', '.join(paths)}: no deny rules")
    deny_ids = {rid for rid, _rx in rules.deny}
    for ids, _rx in rules.allow:
        unknown = set(ids.split(",")) - deny_ids
        if unknown:
            raise ValueError(f"allow names unknown deny rule(s) {sorted(unknown)}")
    return rules


def _load_file(rules: Rules, path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            text = raw.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.split(None, 2)
            kind = parts[0]
            if kind == "maxbytes" and len(parts) == 2:
                rules.maxbytes = int(parts[1])
                continue
            if kind == "baseline" and len(parts) == 2:
                bpath = os.environ.get("LEAK_GUARD_BASELINE") or os.path.join(os.path.dirname(path), parts[1])
                rules.baseline |= load_baseline(bpath)
                continue
            if kind not in ("deny", "allow", "line") or len(parts) != 3:
                raise ValueError(f"{path}:{n}: cannot parse rule")
            getattr(rules, kind).append((parts[1], re.compile(parts[2])))


def load_baseline(path: str) -> set[tuple[str, str, str]]:
    """Lines already public before the guard existed: '<repo> <sha256 of the line> <path>' per row."""
    rows = set()
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            text = raw.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.split(None, 2)
            if len(parts) != 3 or not re.fullmatch(r"[0-9a-f]{64}", parts[1]):
                raise ValueError(f"{path}:{n}: cannot parse baseline row")
            rows.add((parts[0], parts[2], parts[1]))
    return rows


def line_hash(text: str) -> str:
    return hashlib.sha256(text.rstrip("\r").encode("utf-8", "surrogateescape")).hexdigest()


def repo_name() -> str:
    try:
        url = git("remote", "get-url", "origin").strip()
    except subprocess.CalledProcessError:
        url = git("rev-parse", "--show-toplevel").strip()
    name = url.rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1]
    return name[:-4] if name.endswith(".git") else name


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def pushed_commits(stdin_text: str) -> list[str]:
    commits: list[str] = []
    for raw in stdin_text.splitlines():
        parts = raw.split()
        if len(parts) != 4:
            continue
        _lref, lsha, _rref, rsha = parts
        if lsha == ZERO:
            continue  # branch deletion
        spec = [lsha, "--not", "--remotes"] if rsha == ZERO else [f"{rsha}..{lsha}"]
        for c in git("rev-list", "--reverse", *spec).split():
            if c not in commits:
                commits.append(c)
    return commits


def changed_paths(commit: str) -> list[str]:
    out = git("diff-tree", "--root", "--no-commit-id", "-r", "-M", "--name-status", "-z", commit)
    fields = out.split("\0")
    paths, i = [], 0
    while i < len(fields) and fields[i]:
        status = fields[i]
        if status[0] in "RC":
            paths.append(fields[i + 2])
            i += 3
        else:
            if status[0] != "D":
                paths.append(fields[i + 1])
            i += 2
    return paths


def added_lines(commit: str) -> list[tuple[str, int, str]]:
    out = git("show", "--format=", "--no-color", "-U0", "--no-ext-diff", "--text", "-M", commit)
    rows, path, lineno = [], None, 0
    for line in out.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
        elif line.startswith("+") and path:
            rows.append((path, lineno, line[1:]))
            lineno += 1
    return rows


def check(rules: Rules, commits: list[str]) -> list[str]:
    problems: list[str] = []
    repo = repo_name() if rules.baseline else ""
    for c in commits:
        short = c[:10]
        for p in changed_paths(c):
            exempt = {i for ids, rx in rules.allow if rx.search(p) for i in ids.split(",")}
            for rid, rx in rules.deny:
                if rid not in exempt and rx.search(p):
                    problems.append(f"{short} {p}: path rule {rid}")
            if rules.maxbytes is not None:
                size = int(git("cat-file", "-s", f"{c}:{p}").strip())
                if size > rules.maxbytes:
                    problems.append(f"{short} {p}: file is {size} bytes, over {rules.maxbytes}")
        for p, n, text in added_lines(c):
            if rules.baseline and (repo, p, line_hash(text)) in rules.baseline:
                continue  # this exact line was public before the guard; baselined by owner ruling
            for rid, rx in rules.line:
                if rx.search(text):
                    problems.append(f"{short} {p}:{n}: added line matches {rid}")
    return problems


def gitleaks(commits: list[str]) -> list[str]:
    if not commits:
        return []
    root = git("rev-parse", "--show-toplevel").strip()
    # --no-walk shows exactly the listed commits, root commits included
    cmd = ["gitleaks", "git", "--redact", "--no-banner", "--log-level", "error", "--exit-code", "3",
           "--log-opts", "--no-walk " + " ".join(commits), root]
    local = os.path.join(root, ".gitleaks.local.toml")
    if os.path.isfile(local):
        cmd += ["--config", local]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        return []
    if r.returncode == 3:
        return ["gitleaks found a secret in the pushed commits (run gitleaks git --redact to see where)"]
    return [f"gitleaks failed to run (exit {r.returncode})"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deny", action="append", default=None)
    ap.add_argument("--no-gitleaks", action="store_true", help="tests only")
    args = ap.parse_args()
    env = os.environ.get("LEAK_GUARD_DENY")
    paths = env.split(os.pathsep) if env else (args.deny or [DEFAULT_DENY])
    try:
        rules = load_rules(paths)
    except (OSError, ValueError) as exc:
        print(f"leak-guard: BLOCKED. Rule file problem: {exc}")
        return 1
    try:
        commits = pushed_commits(sys.stdin.read())
        problems = check(rules, commits)
    except subprocess.CalledProcessError as exc:
        print(f"leak-guard: BLOCKED. git failed: {' '.join(exc.cmd[:3])}")
        return 1
    if not args.no_gitleaks:
        if subprocess.run(["which", "gitleaks"], capture_output=True).returncode != 0:
            print("leak-guard: BLOCKED. gitleaks not installed.")
            return 1
        problems += gitleaks(commits)
    if problems:
        print("leak-guard: BLOCKED. The commits being pushed carry private material:")
        for p in problems[:40]:
            print("  " + p)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        print("Rewrite the commits so the private material never enters them. Do not bypass with --no-verify.")
        return 1
    print(f"leak-guard: clean ({len(commits)} commit(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

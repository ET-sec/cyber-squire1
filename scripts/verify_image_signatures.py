#!/usr/bin/env python3
"""Verify every pinned image against a per-publisher signing policy. Fails closed.

Inputs
  COREDIRECTIVE_ENGINE/docker-compose.yaml and docker-compose.oci-core.yaml:
    every `image:` reference that carries an @sha256 digest. Locally built
    images and commented examples are skipped.
  .github/image-signers.json, one entry per image repository:
    {"type": "keyless", "identity_regexp": ..., "issuer": ...}
    {"type": "key", "key": "<path in this repo>", "source": ...}
    {"type": "unsigned", "note": ...}

Rules
  keyless or key: cosign must verify the exact pinned digest, else FAIL.
  unsigned: reported as unsigned. If a signature artifact now exists the row
            is a WARN so the policy gets upgraded; the job stays green because
            a publisher starting to sign is not a regression.
  no entry: FAIL, so a new image cannot enter the compose without a decision.

Exit 1 on any FAIL. Writes a table to GITHUB_STEP_SUMMARY when it is set.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    ROOT / "COREDIRECTIVE_ENGINE" / "docker-compose.yaml",
    ROOT / "COREDIRECTIVE_ENGINE" / "docker-compose.oci-core.yaml",
]
POLICY = Path(os.environ.get("IMAGE_SIGNERS", ROOT / ".github" / "image-signers.json"))
IMAGE_LINE = re.compile(r"^\s*image:\s*['\"]?(\S+?)['\"]?\s*(?:#.*)?$")


def pinned_images() -> dict[str, str]:
    seen: dict[str, str] = {}
    for path in COMPOSE:
        for line in path.read_text().splitlines():
            m = IMAGE_LINE.match(line)
            if m and "@sha256:" in m.group(1):
                seen.setdefault(m.group(1), path.name)
    return seen


def repo_of(ref: str) -> str:
    name = ref.split("@", 1)[0]
    slash, colon = name.rfind("/"), name.rfind(":")
    return name[:colon] if colon > slash else name


TRANSIENT = ("TOOMANYREQUESTS", "Rate exceeded", "429", "timeout", "connection reset")
RETRY_WAIT = (10, 30)


def run(*args: str) -> tuple[bool, str]:
    """Run cosign; retry twice on a registry rate limit or a transport error.

    Public registries rate-limit anonymous pulls per source address, and GitHub
    runners share addresses, so a verification job that fails closed must not
    read a 429 as a bad signature. A signature that does not verify is not
    transient and returns on the first attempt.
    """
    for attempt, wait in enumerate((*RETRY_WAIT, None)):
        proc = subprocess.run(["cosign", *args], capture_output=True, text=True)
        tail = (proc.stderr.strip().splitlines() or [""])[-1]
        if proc.returncode == 0 or wait is None or not any(s in tail for s in TRANSIENT):
            return proc.returncode == 0, tail
        print(f"    transient registry error, retry {attempt + 1} in {wait}s: {tail[-120:]}", flush=True)
        time.sleep(wait)
    return False, tail


def main() -> int:
    policy = json.loads(POLICY.read_text())
    rows: list[tuple[str, str, str, str]] = []
    fails = 0
    for ref, source in sorted(pinned_images().items()):
        repo = repo_of(ref)
        pol = policy.get(repo)
        if pol is None:
            rows.append((repo, "no policy", "FAIL", "add an entry to .github/image-signers.json"))
            fails += 1
            continue
        kind = pol["type"]
        if kind == "keyless":
            ok, msg = run(
                "verify",
                "--certificate-identity-regexp", pol["identity_regexp"],
                "--certificate-oidc-issuer", pol["issuer"],
                ref,
            )
            rows.append((repo, f"keyless {pol['identity_regexp']}", "ok" if ok else "FAIL", "" if ok else msg))
            fails += 0 if ok else 1
        elif kind == "key":
            ok, msg = run("verify", "--key", str(ROOT / pol["key"]), ref)
            rows.append((repo, f"key {pol['key']}", "ok" if ok else "FAIL", "" if ok else msg))
            fails += 0 if ok else 1
        elif kind == "unsigned":
            present, _ = run("download", "signature", ref)
            if present:
                rows.append((repo, "unsigned per policy", "WARN", "a signature artifact exists now; upgrade the policy"))
            else:
                rows.append((repo, "unsigned per policy", "unsigned", pol.get("note", "")))
        else:
            rows.append((repo, kind, "FAIL", "unknown policy type"))
            fails += 1

    width = max(len(r[0]) for r in rows) if rows else 10
    for repo, how, result, note in rows:
        print(f"{result:9} {repo:{width}}  {how}  {note}".rstrip())
    counts = {k: sum(1 for r in rows if r[2] == k) for k in ("ok", "unsigned", "WARN", "FAIL")}
    print(f"\nverified {counts['ok']}  unsigned {counts['unsigned']}  warn {counts['WARN']}  fail {counts['FAIL']}  of {len(rows)} pinned images")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("## Pinned image signatures\n\n| image | policy | result | note |\n|---|---|---|---|\n")
            for repo, how, result, note in rows:
                fh.write(f"| `{repo}` | {how} | **{result}** | {note} |\n")
            fh.write(f"\nverified {counts['ok']}, unsigned {counts['unsigned']}, warn {counts['WARN']}, fail {counts['FAIL']} of {len(rows)}\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

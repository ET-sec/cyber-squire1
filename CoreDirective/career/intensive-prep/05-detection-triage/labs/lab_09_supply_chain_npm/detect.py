#!/usr/bin/env python3
"""Heuristic supply-chain detection on npm install logs.

Flags:
  1. Packages first published less than 30 days before install
  2. Packages with a single maintainer
  3. Install scripts (preinstall, postinstall, install) that contain network primitives
  4. Subsequent network egress to non-registry destinations during script execution
  5. Environment variable reads of secrets (NPM_TOKEN, AWS_*, GITHUB_TOKEN) by spawned scripts
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

NEW_PACKAGE_DAYS = 30
SUSPICIOUS_CMD_PATTERNS = [
    r"\bcurl\b", r"\bwget\b", r"\bnc\b ", r"\bpowershell\b",
    r"child_process", r"exec\(", r"\beval\(", r"https?://",
    r"base64\b", r"\.sh\b", r"chmod \+x",
]
SECRET_ENV_VARS = {
    "NPM_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN", "GH_TOKEN", "DOCKER_PASSWORD", "DOCKER_TOKEN",
    "VAULT_TOKEN", "STRIPE_SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
}


def parse_ts(s: str) -> datetime:
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def main(path: Path):
    findings = []
    install_events = []
    script_events = []
    network_events = []
    env_reads = []

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            evt = json.loads(line)
            action = evt.get("action")
            if action == "npm_install":
                install_events.append(evt)
            elif action == "script_run":
                script_events.append(evt)
            elif action == "network":
                network_events.append(evt)
            elif action == "env_read":
                env_reads.append(evt)

    print("=== Suspicious package metadata ===")
    now = datetime.now(timezone.utc)
    for ev in install_events:
        pub = ev.get("first_published")
        if pub:
            pub_ts = parse_ts(pub)
            age_days = (now - pub_ts).total_seconds() / 86400
            if age_days < NEW_PACKAGE_DAYS:
                findings.append(f"  NEW PACKAGE: {ev['package']}@{ev['version']} first published {age_days:.1f} days ago")
        if ev.get("maintainer_count", 99) <= 1:
            findings.append(f"  SINGLE MAINTAINER: {ev['package']}@{ev['version']} (maintainer_count={ev.get('maintainer_count')})")

    print("=== Suspicious install scripts ===")
    for ev in script_events:
        cmd = ev.get("cmd", "")
        for pat in SUSPICIOUS_CMD_PATTERNS:
            if re.search(pat, cmd):
                findings.append(f"  INSTALL SCRIPT INVOKES NETWORK: {ev['package']}@{ev['version']} -> {cmd[:120]}")
                break

    print("=== Secret env reads by spawned scripts ===")
    for ev in env_reads:
        if ev.get("var") in SECRET_ENV_VARS:
            findings.append(f"  SECRET ACCESS: process={ev['process']} read ${ev['var']} at {ev['ts']}")

    print("=== Outbound to non-registry hosts during install window ===")
    for ev in network_events:
        dest = ev.get("destination", "")
        if "registry.npmjs.org" not in dest and "registry.yarnpkg.com" not in dest:
            findings.append(f"  EGRESS: {ev['process']} -> {dest}:{ev.get('port')} at {ev['ts']}")

    if not findings:
        print("No suspicious findings.")
        return 0
    print()
    print("=== FINDINGS ===")
    for f in findings:
        print(f)
    return 1


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "install.log")
    sys.exit(main(path))

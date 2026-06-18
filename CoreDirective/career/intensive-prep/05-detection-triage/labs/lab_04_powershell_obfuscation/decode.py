#!/usr/bin/env python3
"""Decode PowerShell -EncodedCommand payloads from sysmon process_creation events."""
import base64
import json
import re
import sys
from pathlib import Path

ENC_RE = re.compile(r"-(?:enc|ec|encodedcommand)\s+([A-Za-z0-9+/=]+)", re.IGNORECASE)


def decode_pwsh(cmdline: str) -> str | None:
    m = ENC_RE.search(cmdline)
    if not m:
        return None
    raw = base64.b64decode(m.group(1) + "==")
    # PowerShell encodes as UTF-16LE
    try:
        return raw.decode("utf-16le")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def main(path: Path):
    findings = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            evt = json.loads(line)
            cmd = evt.get("CommandLine", "")
            decoded = decode_pwsh(cmd)
            if decoded:
                findings.append({
                    "time": evt.get("UtcTime"),
                    "host": evt.get("Computer"),
                    "user": evt.get("User"),
                    "parent": evt.get("ParentImage"),
                    "decoded": decoded,
                })

    if not findings:
        print("No -EncodedCommand payloads found.")
        return 0

    print(f"Found {len(findings)} encoded PowerShell invocation(s):\n")
    for f in findings:
        print(f"[{f['time']}] {f['host']} user={f['user']}")
        print(f"  parent: {f['parent']}")
        print(f"  decoded: {f['decoded']}")
        print()
    return 1


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "sysmon.json")
    sys.exit(main(path))

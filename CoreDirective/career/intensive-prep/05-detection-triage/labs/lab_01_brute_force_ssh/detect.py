#!/usr/bin/env python3
"""SSH brute force detector.

Reads auth.log, finds source IPs with N or more failed auths within a sliding window,
and flags whether any of those IPs subsequently succeeded (a breach indicator).
"""
import re
import sys
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path

THRESHOLD = 5
WINDOW = timedelta(seconds=60)

FAILED_RE = re.compile(
    r"^(?P<ts>\S+)\s+\S+\s+sshd\[\d+\]:\s+Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+)"
)
ACCEPTED_RE = re.compile(
    r"^(?P<ts>\S+)\s+\S+\s+sshd\[\d+\]:\s+Accepted (?:password|publickey) for (?P<user>\S+) from (?P<ip>\S+)"
)


def parse_ts(s: str) -> datetime:
    # Strip trailing nanoseconds beyond 6 digits if present, normalize Z to +00:00
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def detect(path: Path):
    failed_by_ip: dict[str, deque] = defaultdict(deque)
    bursts: dict[str, list[datetime]] = {}
    accepted_after_burst: list[tuple[str, datetime, str]] = []

    with path.open() as f:
        for line in f:
            line = line.strip()
            m = FAILED_RE.match(line)
            if m:
                ts = parse_ts(m["ts"])
                ip = m["ip"]
                window = failed_by_ip[ip]
                window.append(ts)
                while window and ts - window[0] > WINDOW:
                    window.popleft()
                if len(window) >= THRESHOLD and ip not in bursts:
                    bursts[ip] = [window[0], ts]
                continue

            m = ACCEPTED_RE.match(line)
            if m:
                ts = parse_ts(m["ts"])
                ip = m["ip"]
                user = m["user"]
                if ip in bursts and bursts[ip][0] <= ts <= bursts[ip][1] + timedelta(minutes=5):
                    accepted_after_burst.append((ip, ts, user))

    print("=== Brute force burst sources ===")
    for ip, (start, end) in bursts.items():
        delta = (end - start).total_seconds()
        count = sum(1 for _ in failed_by_ip[ip])
        print(f"  {ip}: burst start {start.isoformat()} duration ~{delta:.1f}s")

    print()
    print("=== Successful auths from brute-force IPs (LIKELY BREACH) ===")
    if not accepted_after_burst:
        print("  none")
    else:
        for ip, ts, user in accepted_after_burst:
            print(f"  CRITICAL: {ip} as {user} at {ts.isoformat()}")

    return 1 if accepted_after_burst else 0


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "auth.log")
    sys.exit(detect(path))

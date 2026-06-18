#!/usr/bin/env python3
"""DNS exfiltration heuristic detector.

Real production parsers (Vector, Logstash, Cribl) compute subdomain length and
Shannon entropy at ingest. We compute them here for completeness and demonstrate
the detection logic.
"""
import json
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

ALLOWED_PARENT_DOMAINS = {
    "cloudfront.net",
    "akamaiedge.net",
    "fastly.net",
    "azureedge.net",
    "amazonaws.com",
    "google.com",
    "github.com",
}

LEN_THRESHOLD = 40
ENTROPY_THRESHOLD = 4.0
BURST_COUNT = 5
BURST_WINDOW_S = 60


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def parent_domain(query: str) -> str:
    parts = query.strip(".").split(".")
    if len(parts) < 2:
        return query
    return ".".join(parts[-2:])


def main(path: Path):
    by_parent: dict[str, list] = defaultdict(list)
    candidates = []

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            evt = json.loads(line)
            sub = evt.get("subdomain", "")
            length = evt.get("subdomain_length") or len(sub)
            ent = evt.get("subdomain_entropy") or shannon_entropy(sub)
            parent = parent_domain(evt["query"])

            if parent in ALLOWED_PARENT_DOMAINS:
                continue
            if length >= LEN_THRESHOLD and ent >= ENTROPY_THRESHOLD:
                candidates.append({**evt, "parent": parent, "_entropy": ent, "_len": length})
                by_parent[(evt["src_ip"], parent)].append(evt["ts"])

    print("=== High-entropy long-subdomain candidates ===")
    for c in candidates:
        print(f"  [{c['ts']}] {c['src_ip']} -> {c['query']} (len={c['_len']}, H={c['_entropy']:.2f}, qtype={c.get('qtype')})")

    print()
    print("=== Burst sources (5+ candidate queries to same parent within 60s) ===")
    bursts = 0
    for (src, parent), times in by_parent.items():
        if len(times) >= BURST_COUNT:
            bursts += 1
            print(f"  ALERT: {src} -> *.{parent} : {len(times)} queries between {times[0]} and {times[-1]}")
    if not bursts:
        print("  none")

    return 1 if bursts else 0


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "dns.log")
    sys.exit(main(path))

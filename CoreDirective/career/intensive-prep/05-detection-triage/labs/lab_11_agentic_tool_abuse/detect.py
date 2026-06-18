#!/usr/bin/env python3
"""Detect anomalous agent tool sequences in n8n execution logs.

Pattern: untrusted fetch tool followed by sensitive write tool within 30 seconds
in the same execution. The signature of indirect prompt injection driving an
agent to exfiltrate or persist via its sanctioned tools.
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

UNTRUSTED_FETCH = {
    "n8n-nodes-base.httpRequest",
    "n8n-nodes-base.gmail",  # when operation is read
    "tavily.search",
    "n8n-nodes-base.googleDriveTrigger",
    "n8n-nodes-base.notion",  # when operation is fetch
}

SENSITIVE_WRITES = {
    ("n8n-nodes-base.gmail", "send"),
    ("n8n-nodes-base.github", "createIssue"),
    ("n8n-nodes-base.github", "createPullRequest"),
    ("n8n-nodes-base.googleDrive", "shareFile"),
    ("n8n-nodes-base.googleDrive", "uploadFile"),
    ("n8n-nodes-base.slack", "postMessage"),
    ("n8n-nodes-base.executeCommand", "execute"),
}

WINDOW = timedelta(seconds=30)
EXTERNAL_DOMAIN_HINTS = ("attacker", "evil", "suspicious")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def is_untrusted_fetch(ev):
    nt = ev.get("node_type", "")
    op = ev.get("operation", "")
    if nt == "n8n-nodes-base.gmail" and op not in {"send"}:
        return True
    if nt == "n8n-nodes-base.notion" and op in {"fetch", "search", "read"}:
        return True
    if nt in {"n8n-nodes-base.httpRequest", "tavily.search"}:
        return True
    return False


def is_sensitive_write(ev):
    return (ev.get("node_type", ""), ev.get("operation", "")) in SENSITIVE_WRITES


def main(path: Path):
    events = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))

    by_exec = defaultdict(list)
    for ev in events:
        by_exec[ev["execution_id"]].append(ev)

    findings = []
    for exec_id, evs in by_exec.items():
        evs.sort(key=lambda e: e["ts"])
        for i, ev in enumerate(evs):
            if not is_untrusted_fetch(ev):
                continue
            fetch_ts = parse_ts(ev["ts"])
            for follow in evs[i + 1:]:
                if parse_ts(follow["ts"]) - fetch_ts > WINDOW:
                    break
                if is_sensitive_write(follow):
                    findings.append({
                        "execution_id": exec_id,
                        "workflow_id": ev["workflow_id"],
                        "workflow_name": ev.get("workflow_name", ""),
                        "fetch": {"node": ev["node_name"], "type": ev["node_type"], "ts": ev["ts"], "input": ev.get("input")},
                        "write": {"node": follow["node_name"], "type": follow["node_type"], "ts": follow["ts"], "op": follow["operation"], "input": follow.get("input")},
                    })

    if not findings:
        print("No anomalous tool sequences detected.")
        return 0

    print(f"Anomalous agent tool sequences: {len(findings)}\n")
    for f in findings:
        print(f"  Execution: {f['execution_id']} ({f['workflow_name']})")
        print(f"    Fetch:  {f['fetch']['ts']} {f['fetch']['type']}.{f['fetch'].get('node')} input={json.dumps(f['fetch'].get('input', {}))[:120]}")
        print(f"    Write:  {f['write']['ts']} {f['write']['type']}.{f['write']['op']} input={json.dumps(f['write'].get('input', {}))[:120]}")
        # Heuristic: external recipient hint
        write_input = json.dumps(f["write"].get("input", {})).lower()
        if any(h in write_input for h in EXTERNAL_DOMAIN_HINTS):
            print(f"    HEURISTIC: write target contains external/attacker pattern. Critical.")
        print()
    return 1


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "n8n_executions.log")
    sys.exit(main(path))

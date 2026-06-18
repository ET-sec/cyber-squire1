#!/usr/bin/env python3
"""LLM gateway prompt injection detector and triage agent.

Two stages:
  1. Pattern-based detection on direct injection (user content)
  2. Tool sequence correlation for indirect injection (fetched content)

This mirrors what an AI-augmented SOC agent (Dropzone-style) would do for
LLM gateway alerts.
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DIRECT_INJECTION_PATTERNS = [
    r"ignore (previous|prior|all) instructions?",
    r"disregard (the )?system (prompt|message)",
    r"you are now (?!a customer)",
    r"pretend (you are|to be)",
    r"developer mode",
    r"system override",
    r"print (your |all )?(instructions?|system prompt|context)",
    r"reveal (your |all )?(prompt|instructions|credentials|api key)",
    r"end of system",
    r"<\|system\|>",
    r"\[INST\]",
]

INDIRECT_INJECTION_MARKERS = [
    r"system override",
    r"new instructions:",
    r"ignore the",
    r"<!--.*system",
    r"important:.*assistant",
]

SENSITIVE_TOOLS = {"send_email", "send_message", "create_issue", "push_commit", "share_file", "create_user", "exec_query"}
UNTRUSTED_FETCH_TOOLS = {"fetch_url", "read_email", "search_web", "read_document"}

CORRELATION_WINDOW_S = 30


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def detect_direct(events):
    findings = []
    for ev in events:
        for msg in ev.get("messages", []) or []:
            if msg.get("role") != "user":
                continue
            content = msg.get("content", "").lower()
            for pat in DIRECT_INJECTION_PATTERNS:
                if re.search(pat, content):
                    findings.append({
                        "type": "direct_injection",
                        "request_id": ev["request_id"],
                        "ts": ev["ts"],
                        "user_id": ev.get("user_id"),
                        "client_ip": ev.get("client_ip"),
                        "tenant": ev.get("tenant"),
                        "matched_pattern": pat,
                        "snippet": msg["content"][:200],
                    })
                    break
    return findings


def detect_indirect_in_tool_output(events):
    findings = []
    for ev in events:
        if ev.get("route", "").startswith("tool/") and ev["route"] != "tool/send_email":
            for msg in ev.get("messages", []) or []:
                if msg.get("role") == "tool":
                    content = msg.get("content", "").lower()
                    for pat in INDIRECT_INJECTION_MARKERS:
                        if re.search(pat, content):
                            findings.append({
                                "type": "indirect_injection_in_tool_output",
                                "request_id": ev["request_id"],
                                "ts": ev["ts"],
                                "tenant": ev.get("tenant"),
                                "matched_pattern": pat,
                                "snippet": msg["content"][:200],
                            })
                            break
    return findings


def detect_sequence(events):
    by_user = defaultdict(list)
    for ev in events:
        if ev.get("user_id"):
            by_user[ev["user_id"]].append(ev)

    findings = []
    for user, user_events in by_user.items():
        user_events.sort(key=lambda e: e["ts"])
        for i, ev in enumerate(user_events):
            route = ev.get("route", "")
            tool_name = route.split("/", 1)[1] if route.startswith("tool/") else None
            if tool_name and tool_name in UNTRUSTED_FETCH_TOOLS:
                fetch_ts = parse_ts(ev["ts"])
                for follow in user_events[i + 1:]:
                    follow_ts = parse_ts(follow["ts"])
                    if follow_ts - fetch_ts > timedelta(seconds=CORRELATION_WINDOW_S):
                        break
                    follow_route = follow.get("route", "")
                    follow_tool = follow_route.split("/", 1)[1] if follow_route.startswith("tool/") else None
                    if follow_tool and follow_tool in SENSITIVE_TOOLS:
                        findings.append({
                            "type": "agent_tool_sequence",
                            "user_id": user,
                            "fetch_event": ev["request_id"],
                            "fetch_tool": tool_name,
                            "fetch_ts": ev["ts"],
                            "sensitive_event": follow["request_id"],
                            "sensitive_tool": follow_tool,
                            "sensitive_ts": follow["ts"],
                            "tool_args": follow.get("tool_call", {}).get("arguments"),
                        })
    return findings


def triage_report(direct, indirect, sequence):
    total = len(direct) + len(indirect) + len(sequence)
    if total == 0:
        return "Triage Report\n=============\nNo prompt injection or anomalous tool sequences detected.\n"

    lines = ["Triage Report", "=============", ""]
    lines.append(f"Findings: {total}")
    lines.append(f"  Direct injection: {len(direct)}")
    lines.append(f"  Indirect injection (tool output): {len(indirect)}")
    lines.append(f"  Anomalous tool sequences: {len(sequence)}")
    lines.append("")
    lines.append("Verdict: Review required. ")

    if sequence:
        lines.append("CRITICAL: agent followed an untrusted-fetch with a sensitive write within 30s.")
        lines.append("Recommended action: revoke the agent session, rotate any creds it touched, audit downstream effects.")
        for s in sequence:
            lines.append(f"  - user={s['user_id']} fetch={s['fetch_tool']}@{s['fetch_ts']} write={s['sensitive_tool']}@{s['sensitive_ts']}")
            if s.get("tool_args"):
                lines.append(f"    args: {json.dumps(s['tool_args'])[:200]}")

    if direct:
        lines.append("")
        lines.append("DIRECT injection attempts (safe to throttle the user, log for review):")
        for d in direct:
            lines.append(f"  - {d['ts']} ip={d['client_ip']} user={d['user_id']} pattern={d['matched_pattern']!r}")

    if indirect:
        lines.append("")
        lines.append("INDIRECT injection patterns in tool output (review tool source domain reputation):")
        for i in indirect:
            lines.append(f"  - {i['ts']} request={i['request_id']} pattern={i['matched_pattern']!r}")

    return "\n".join(lines) + "\n"


def main(path: Path):
    events = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))

    direct = detect_direct(events)
    indirect = detect_indirect_in_tool_output(events)
    sequence = detect_sequence(events)
    report = triage_report(direct, indirect, sequence)
    print(report)
    return 1 if (direct or indirect or sequence) else 0


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "gateway.log")
    sys.exit(main(path))

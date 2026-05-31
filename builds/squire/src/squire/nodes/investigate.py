"""investigate node - Opus 4.7 investigation synthesis with Tavily follow-up.

After classification + retrieval + enrichment, this node:
  1. Pulls additional targeted threat intel via tools.tavily (when the
     classifier produced IoCs or a distinctive rule) - fail-open.
  2. Asks Opus 4.7 to synthesize an investigation plan: what's been checked,
     what hypotheses are live, what evidence is still needed.

The output is written to state["evidence"] as an investigation row rather than
a dedicated state key, which keeps IRState lean and lets the draft node pull
from evidence just like any other artifact.

Investigation is deliberately bounded: temperature 0.1, max_tokens 1000. We
want a compact, structured synthesis, not another draft.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from ..llm import estimate_cost, llm_invoke
from ..settings import settings
from ..tools import tavily_search

log = logging.getLogger("squire.nodes.investigate")


INVESTIGATE_SYSTEM_PROMPT = (
    "You are a SOC investigator. Given an alert, a triage classification, retrieved "
    "playbook chunks, and threat-intel enrichment, produce a STRICT JSON investigation "
    "note with exactly these keys:\n"
    "  findings: list of 2-5 concise observations about what happened, each <= 1 sentence.\n"
    "  hypotheses: list of 2-4 competing explanations, each {label, likelihood: LOW|MEDIUM|HIGH}.\n"
    "  evidence_needed: list of 1-4 artifacts/queries that would confirm or refute the top hypothesis.\n"
    "  ioc_candidates: list of 0-5 indicators worth pivoting on (IPs, hashes, process names, container ids).\n"
    "  summary: at most 3 sentences tying findings + top hypothesis.\n"
    "Return the JSON object only. No prose, no markdown fences. Never invent IoCs or hashes."
)


def _build_investigation_context(state: dict) -> dict[str, Any]:
    """Pack alert + classification + top chunks + threat_intel into a bounded payload."""
    return {
        "alert": state.get("alert", {}),
        "classification": state.get("classification", {}),
        "grc_chunks": [
            {
                "file": c.get("source_file"),
                "citation": c.get("citation"),
                "excerpt": (c.get("content") or "")[:500],
            }
            for c in (state.get("grc_chunks") or [])[:5]
        ],
        "threat_intel": state.get("threat_intel") or {},
    }


def _derive_followup_query(state: dict) -> str | None:
    """Build a short Tavily query from high-signal alert/classification fields."""
    alert = state.get("alert") or {}
    classification = state.get("classification") or {}

    parts: list[str] = []
    for k in ("rule", "rule_name", "title"):
        v = alert.get(k)
        if v:
            parts.append(str(v))
            break

    of = alert.get("output_fields") or {}
    if isinstance(of, dict):
        for k in ("container.image.repository", "proc.name", "user.name"):
            v = of.get(k)
            if v:
                parts.append(str(v))

    tactics = classification.get("mitre_tactics") or []
    if tactics:
        parts.append(" ".join(str(t) for t in tactics[:2]))

    it = classification.get("incident_type")
    if it:
        parts.append(str(it))

    if not parts:
        return None
    return " ".join(parts)[:240]


def _coerce_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[: -3]
    text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception as e:
        log.warning("investigate: JSON parse failed: %s -- raw head: %r", e, text[:200])
        return {
            "findings": [],
            "hypotheses": [],
            "evidence_needed": [],
            "ioc_candidates": [],
            "summary": "investigate_parse_error",
            "_parse_error": str(e),
        }


def investigate(state: dict) -> dict:
    """Opus 4.7 investigation synthesis node.

    Produces an evidence row tagged node='investigate' containing:
      - elapsed_ms, backend, model, cost, tokens (for criterion #26)
      - tavily_followup: {query, result_count} or {skipped_reason}
      - output: the parsed investigation note
    """
    t0 = time.monotonic()

    # 1. Optional Tavily follow-up for targeted intel.
    followup_query = _derive_followup_query(state)
    followup_envelope = {
        "threat_intel": [],
        "query": "",
        "skipped_reason": "no_followup_query_derived",
    }
    if followup_query:
        followup_envelope = tavily_search(followup_query)

    # 2. Build compact LLM context.
    ctx = _build_investigation_context(state)
    ctx["tavily_followup"] = followup_envelope

    model = settings.claude_model_primary  # Opus 4.7

    resp = llm_invoke(
        messages=[
            {"role": "system", "content": INVESTIGATE_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(ctx, default=str)[:8000]},
        ],
        model=model,
        temperature=0.1,
        max_tokens=1000,
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    parsed = _coerce_json(resp.content)

    cost = estimate_cost(model, resp.input_tokens, resp.output_tokens)
    total_tokens = (state.get("total_tokens") or 0) + resp.input_tokens + resp.output_tokens
    total_cost = (state.get("total_cost_usd") or 0.0) + cost

    followup_summary = {
        "query": followup_envelope.get("query"),
        "result_count": len(followup_envelope.get("threat_intel") or []),
    }
    if followup_envelope.get("skipped_reason"):
        followup_summary["skipped_reason"] = followup_envelope["skipped_reason"]
    if followup_envelope.get("enrichment_skipped"):
        followup_summary["skipped_reason"] = followup_envelope["enrichment_skipped"]

    evidence_row = {
        "node": "investigate",
        "elapsed_ms": elapsed_ms,
        "backend": resp.backend,
        "model": model,
        "input_tokens": resp.input_tokens,
        "output_tokens": resp.output_tokens,
        "cost_usd": round(cost, 6),
        "tavily_followup": followup_summary,
        "output": parsed,
    }
    evidence = list(state.get("evidence") or []) + [evidence_row]

    update: dict[str, Any] = {
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "evidence": evidence,
    }
    if resp.degraded:
        update["_degraded_mode"] = True
        update["_degraded_reason"] = resp.degraded_reason or "unknown"

    return update

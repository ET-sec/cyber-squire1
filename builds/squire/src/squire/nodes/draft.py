"""draft node - Opus 4.8 IR report drafter with citation allow-list retry.

Implements ROADMAP criterion #17: any fabricated framework code triggers one
automatic retry with a corrective prompt; if the retry still carries invalid
codes, the bad codes are dropped and an escalation message is appended to
state["errors"] (surfaced by the FastAPI layer in 17-09).

Contract with the graph:
  - reads: state.alert, state.classification, state.grc_chunks,
           state.threat_intel, state.evidence (investigate rows), state.critique
  - writes: state.draft_report (JSON string), state.severity, state.citations,
            total_tokens, total_cost_usd, evidence[], errors[] (on escalation)
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from ..citations import filter_citations, validate_citations_with_retry
from ..llm import estimate_cost, llm_invoke
from ..nemo_client import BLOCK_SENTINEL
from ..settings import settings

log = logging.getLogger("squire.nodes.draft")


DRAFT_SYSTEM_PROMPT = (
    "You are Squire, an autonomous SOC analyst. Draft a structured IR report. "
    "Return STRICT JSON with exactly these keys:\n"
    "  severity: one of LOW|MEDIUM|HIGH|CRITICAL\n"
    "  summary: at most 4 sentences\n"
    "  observed: list of bullet observations\n"
    "  hypotheses_tested: list of bullets\n"
    "  recommended_actions: list of bullets, each citing at least one playbook reference\n"
    "  citations: object with these keys:\n"
    "    csf_2_0: list of RS.* codes (CSF 2.0 RESPOND subcategories only)\n"
    "    mitre_attack: list of TA#### tactic codes or T#### technique codes (T#### or T####.###)\n"
    "    csa_agentic: list of MG-X.Y codes (CSA Agentic AI Profile MANAGE)\n"
    "    owasp_llm: list of LLM01..LLM10 codes\n"
    "    nist_800_61_r3: list of section references like '§4' or 'Section 4'\n"
    "  evidence_trail_refs: list of retrieved chunk citations used\n"
    "Every recommended_action MUST reference at least one retrieved chunk or playbook citation. "
    "Use ONLY framework codes that exist. Do not invent codes. "
    "Return the JSON object only. No prose, no markdown fences."
)


def _build_context(state: dict) -> dict[str, Any]:
    """Bounded context pack fed into the Opus call."""
    investigation_rows = [
        e for e in (state.get("evidence") or []) if e.get("node") == "investigate"
    ]
    return {
        "alert": state.get("alert", {}),
        "classification": state.get("classification", {}),
        "grc_chunks": [
            {
                "file": c.get("source_file"),
                "citation": c.get("citation"),
                "excerpt": (c.get("content") or "")[:700],
            }
            for c in (state.get("grc_chunks") or [])[:5]
        ],
        "investigation": investigation_rows,
        "threat_intel": state.get("threat_intel") or {},
        "critique_prior": state.get("critique") or "",
    }


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
        log.warning("draft: JSON parse failed: %s -- raw head: %r", e, text[:200])
        return {
            "severity": "UNKNOWN",
            "summary": "parse_error",
            "observed": [],
            "hypotheses_tested": [],
            "recommended_actions": [],
            "citations": {},
            "evidence_trail_refs": [],
            "_parse_error": str(e),
        }


_ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _normalize_severity(raw: Any, fallback: str) -> str:
    sev = str(raw or "").strip().upper()
    return sev if sev in _ALLOWED_SEVERITIES else (fallback or "MEDIUM")


def _invoke_drafter(
    ctx: dict,
    model: str,
    corrective: str | None = None,
) -> tuple[dict, int, int, int, Any]:
    """Single LLM call. Returns (parsed_report, in_tokens, out_tokens, elapsed_ms, resp)."""
    system = DRAFT_SYSTEM_PROMPT
    if corrective:
        system = system + "\n\nCORRECTIVE INSTRUCTION: " + corrective

    t0 = time.monotonic()
    resp = llm_invoke(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(ctx, default=str)[:8000]},
        ],
        model=model,
        temperature=0.15,
        max_tokens=2800,
        through_nemo=True,
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    # NeMo block sentinel: short-circuit parse; _apply_draft propagates the
    # raw sentinel content into state.errors where app.py middleware picks
    # it up and rewrites the response via build_block_response.
    if resp.content.startswith(BLOCK_SENTINEL):
        return (
            {"_nemo_block": resp.content, "severity": "BLOCKED"},
            resp.input_tokens,
            resp.output_tokens,
            elapsed_ms,
            resp,
        )
    parsed = _coerce_json(resp.content)
    return parsed, resp.input_tokens, resp.output_tokens, elapsed_ms, resp


def draft_report(state: dict) -> dict:
    """Opus 4.8 draft node with citation allow-list retry (criterion #17)."""
    model = settings.claude_model_primary  # Opus 4.8
    ctx = _build_context(state)

    # --- First draft --------------------------------------------------
    parsed, in_tokens, out_tokens, first_ms, first_resp = _invoke_drafter(ctx, model)

    # NeMo block short-circuit: skip citation retry, stamp a nemo_block: marker
    # into state.errors so app.py middleware rewrites the response.
    if isinstance(parsed, dict) and parsed.get("_nemo_block"):
        sentinel = parsed["_nemo_block"]
        # Strip the __NEMO_BLOCK__: prefix, flip to nemo_block: prefix for app.py
        marker = "nemo_block:" + sentinel[len(BLOCK_SENTINEL):]
        evidence_row = {
            "node": "draft",
            "elapsed_ms": first_ms,
            "backend": first_resp.backend,
            "model": model,
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost_usd": 0.0,
            "citation_retries": 0,
            "escalations": [],
            "severity": "BLOCKED",
            "rail_blocked": True,
        }
        evidence = list(state.get("evidence") or []) + [evidence_row]
        return {
            "draft_report": json.dumps({"severity": "BLOCKED", "blocked_by_rail": True}),
            "severity": "BLOCKED",
            "citations": {},
            "total_tokens": (state.get("total_tokens") or 0) + in_tokens + out_tokens,
            "total_cost_usd": state.get("total_cost_usd") or 0.0,
            "errors": list(state.get("errors") or []) + [marker],
            "evidence": evidence,
        }

    accumulator = {
        "in_tokens": in_tokens,
        "out_tokens": out_tokens,
        "total_ms": first_ms,
        "retries": 0,
        "backend": first_resp.backend,
        "degraded": first_resp.degraded,
        "degraded_reason": first_resp.degraded_reason,
    }

    # --- Citation retry (criterion #17) -------------------------------
    def redraft(corrective: str) -> dict:
        accumulator["retries"] += 1
        p, i_t, o_t, ms, resp = _invoke_drafter(ctx, model, corrective=corrective)
        accumulator["in_tokens"] += i_t
        accumulator["out_tokens"] += o_t
        accumulator["total_ms"] += ms
        if resp.degraded:
            accumulator["degraded"] = True
            accumulator["degraded_reason"] = resp.degraded_reason or "unknown"
        return p

    parsed, escalations = validate_citations_with_retry(parsed, redraft, max_retries=1)
    # Final defensive filter: even if retry passed, drop any lingering invalids.
    parsed["citations"] = filter_citations(parsed.get("citations", {}))

    # --- Accounting ----------------------------------------------------
    cost = estimate_cost(model, accumulator["in_tokens"], accumulator["out_tokens"])
    total_tokens = (state.get("total_tokens") or 0) + accumulator["in_tokens"] + accumulator["out_tokens"]
    total_cost = (state.get("total_cost_usd") or 0.0) + cost

    # Severity falls back to classifier's severity when LLM returns UNKNOWN.
    severity = _normalize_severity(
        parsed.get("severity"),
        fallback=state.get("severity") or "MEDIUM",
    )
    parsed["severity"] = severity

    evidence_row = {
        "node": "draft",
        "elapsed_ms": accumulator["total_ms"],
        "backend": accumulator["backend"],
        "model": model,
        "input_tokens": accumulator["in_tokens"],
        "output_tokens": accumulator["out_tokens"],
        "cost_usd": round(cost, 6),
        "citation_retries": accumulator["retries"],
        "escalations": escalations,
        "severity": severity,
    }
    evidence = list(state.get("evidence") or []) + [evidence_row]

    update: dict[str, Any] = {
        "draft_report": json.dumps(parsed),
        "severity": severity,
        "citations": parsed.get("citations", {}),
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "errors": list(state.get("errors") or []) + escalations,
        "evidence": evidence,
    }
    if accumulator["degraded"]:
        update["_degraded_mode"] = True
        update["_degraded_reason"] = accumulator["degraded_reason"] or "unknown"

    return update

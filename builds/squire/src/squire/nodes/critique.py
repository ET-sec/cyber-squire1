"""critique node - Opus 4.7 self-critique of the draft report.

Runs AFTER the draft node. Reads the current draft_report (JSON string),
evaluates it against a short rubric, and emits:
  - should_loop: bool. True -> graph should send state back to `draft` for
    another pass. False -> graph exits the critique loop and routes severity.
  - critique_notes: short string fed back to the next draft as `critique_prior`.
  - critique_iterations: previous count + 1.

Criterion #5 (self-critique loop) gets its foundation here. The actual
"directional improvement" metric lives in 17-12; we only provide the loop
plumbing and a faithful critic prompt.

Safety: the graph's `_should_loop` edge hard-caps iterations at
settings.max_critique_iterations (default 3), so a critic that keeps shouting
"LOOP" cannot spin forever.
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from ..llm import estimate_cost, llm_invoke
from ..nemo_client import BLOCK_SENTINEL
from ..settings import settings

log = logging.getLogger("squire.nodes.critique")


CRITIC_SYSTEM_PROMPT = (
    "You are a senior SOC lead reviewing a draft IR report. Evaluate against this rubric:\n"
    "  1. Does every recommended_action cite a concrete playbook or framework reference?\n"
    "  2. Are the framework citations plausibly real (no invented codes)?\n"
    "  3. Is the severity label consistent with the observed findings?\n"
    "  4. Does the summary capture the incident in <=4 sentences without ambiguity?\n"
    "  5. Are there obvious hypotheses the draft missed?\n"
    "\n"
    "Return STRICT JSON with these keys:\n"
    "  verdict: one of APPROVED|LOOP\n"
    "  critique_notes: 1-4 sentences summarizing gaps; empty string if APPROVED\n"
    "  specific_fixes: list of 0-3 concrete instructions the drafter should apply on the next pass\n"
    "\n"
    "Choose LOOP only when a concrete, fixable gap exists. If the report is adequate even if "
    "imperfect, choose APPROVED. Return the JSON object only. No prose, no markdown fences."
)


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
        log.warning("critique: JSON parse failed: %s -- raw head: %r", e, text[:200])
        # On parse error, default to APPROVED to avoid spinning the loop.
        return {
            "verdict": "APPROVED",
            "critique_notes": "",
            "specific_fixes": [],
            "_parse_error": str(e),
        }


_LOOP_RE = re.compile(r"\bLOOP\b", re.IGNORECASE)


def critique(state: dict) -> dict:
    """Self-critique node.

    Writes:
      - critique: short string (the notes + fixes concatenated) fed back to draft
      - critique_iterations: monotonically increasing count
      - should_loop: bool consumed by the graph's conditional edge
      - evidence: row with node='critique', elapsed_ms, model, tokens, cost
    """
    t0 = time.monotonic()
    model = settings.claude_model_primary  # Opus 4.7

    draft_raw = state.get("draft_report") or ""
    payload = {
        "draft_report": draft_raw,
        "classification": state.get("classification") or {},
        "iteration": state.get("critique_iterations", 0),
    }

    resp = llm_invoke(
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, default=str)[:8000]},
        ],
        model=model,
        temperature=0.1,
        max_tokens=600,
        through_nemo=True,
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    # NeMo block short-circuit: don't loop, approve, stamp marker.
    if resp.content.startswith(BLOCK_SENTINEL):
        marker = "nemo_block:" + resp.content[len(BLOCK_SENTINEL):]
        evidence_row = {
            "node": "critique",
            "elapsed_ms": elapsed_ms,
            "backend": resp.backend,
            "model": model,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "cost_usd": 0.0,
            "verdict": "BLOCKED",
            "should_loop": False,
            "rail_blocked": True,
        }
        evidence = list(state.get("evidence") or []) + [evidence_row]
        return {
            "critique": "BLOCKED_BY_RAIL",
            "should_loop": False,
            "critique_iterations": int(state.get("critique_iterations", 0)) + 1,
            "total_tokens": (state.get("total_tokens") or 0) + resp.input_tokens + resp.output_tokens,
            "total_cost_usd": state.get("total_cost_usd") or 0.0,
            "evidence": evidence,
            "errors": list(state.get("errors") or []) + [marker],
        }

    parsed = _coerce_json(resp.content)
    verdict = str(parsed.get("verdict", "APPROVED")).strip().upper()
    notes = str(parsed.get("critique_notes", "") or "")
    fixes = parsed.get("specific_fixes") or []

    should_loop = verdict == "LOOP" or _LOOP_RE.search(notes) is not None

    # Pack the human-readable critique string the drafter reads on its next pass.
    fix_lines = "\n".join(f"- {f}" for f in fixes if str(f).strip())
    critique_text_parts = [verdict, notes]
    if fix_lines:
        critique_text_parts.append("Specific fixes:\n" + fix_lines)
    critique_text = "\n\n".join(p for p in critique_text_parts if p).strip()

    cost = estimate_cost(model, resp.input_tokens, resp.output_tokens)
    total_tokens = (state.get("total_tokens") or 0) + resp.input_tokens + resp.output_tokens
    total_cost = (state.get("total_cost_usd") or 0.0) + cost

    evidence_row = {
        "node": "critique",
        "elapsed_ms": elapsed_ms,
        "backend": resp.backend,
        "model": model,
        "input_tokens": resp.input_tokens,
        "output_tokens": resp.output_tokens,
        "cost_usd": round(cost, 6),
        "verdict": verdict,
        "should_loop": should_loop,
    }
    evidence = list(state.get("evidence") or []) + [evidence_row]

    update: dict[str, Any] = {
        "critique": critique_text,
        "should_loop": should_loop,
        "critique_iterations": int(state.get("critique_iterations", 0)) + 1,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "evidence": evidence,
    }
    if resp.degraded:
        update["_degraded_mode"] = True
        update["_degraded_reason"] = resp.degraded_reason or "unknown"

    return update

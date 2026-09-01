"""classify node - Opus 5 severity + incident-type classifier.

Reads state["alert"]; writes state["classification"] and state["severity"].
Cost + tokens + degraded-mode flags are merged into state via evidence row.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from ..llm import estimate_cost, llm_invoke
from ..settings import settings

log = logging.getLogger("squire.nodes.classify")


CLASSIFIER_SYSTEM_PROMPT = (
    "You are a SOC triage classifier. Given a security alert payload, emit STRICT JSON "
    "with exactly these keys:\n"
    "  incident_type: one of [malware, credential_theft, unauthorized_access, "
    "data_exfiltration, ddos, misconfiguration, ai_incident, phishing, insider_threat, other]\n"
    "  severity_guess: one of [LOW, MEDIUM, HIGH, CRITICAL]\n"
    "  confidence: float between 0.0 and 1.0\n"
    "  mitre_tactics: list of MITRE ATT&CK tactic codes (TA0001..TA0043)\n"
    "  rationale: at most 2 sentences\n"
    "Return the JSON object only. No prose, no markdown fences."
)


_ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
_ALLOWED_INCIDENT_TYPES = {
    "malware",
    "credential_theft",
    "unauthorized_access",
    "data_exfiltration",
    "ddos",
    "misconfiguration",
    "ai_incident",
    "phishing",
    "insider_threat",
    "other",
}


def _coerce_json(raw: str) -> dict[str, Any]:
    """Strip markdown fences + best-effort JSON parse."""
    text = (raw or "").strip()
    if text.startswith("```"):
        # strip leading fence
        text = text.split("\n", 1)[1] if "\n" in text else text
        # strip trailing fence
        if text.endswith("```"):
            text = text[: -3]
    text = text.strip().lstrip("json").strip()
    try:
        return json.loads(text)
    except Exception as e:
        log.warning("classify: JSON parse failed: %s -- raw head: %r", e, text[:200])
        return {
            "incident_type": "other",
            "severity_guess": "MEDIUM",
            "confidence": 0.0,
            "mitre_tactics": [],
            "rationale": "classifier_parse_error",
            "_parse_error": str(e),
        }


def _validate_and_normalize(parsed: dict[str, Any]) -> dict[str, Any]:
    """Clamp fields into the enum space; unknown values fall back to safe defaults."""
    out = dict(parsed)

    it = str(out.get("incident_type", "other")).strip().lower()
    out["incident_type"] = it if it in _ALLOWED_INCIDENT_TYPES else "other"

    sev = str(out.get("severity_guess", "MEDIUM")).strip().upper()
    out["severity_guess"] = sev if sev in _ALLOWED_SEVERITIES else "MEDIUM"

    try:
        conf = float(out.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    out["confidence"] = max(0.0, min(1.0, conf))

    tactics = out.get("mitre_tactics") or []
    if not isinstance(tactics, list):
        tactics = []
    out["mitre_tactics"] = [str(t).strip() for t in tactics if str(t).strip()]

    if not isinstance(out.get("rationale"), str):
        out["rationale"] = ""

    return out


def classify(state: dict) -> dict:
    """Opus-5 severity classifier node.

    Writes classification + severity into state; appends an evidence row;
    propagates degraded_mode if the underlying backend fell back.
    """
    t0 = time.monotonic()
    alert_payload = state.get("alert") or {}
    # Cap payload size to avoid blowing context on giant alert blobs.
    alert_str = json.dumps(alert_payload, default=str)[:4000]

    model = settings.claude_model_secondary  # Opus 5 per plan

    resp = llm_invoke(
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": alert_str},
        ],
        model=model,
        temperature=0.0,
        max_tokens=400,
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    parsed = _coerce_json(resp.content)
    parsed = _validate_and_normalize(parsed)

    cost = estimate_cost(model, resp.input_tokens, resp.output_tokens)
    total_tokens = (state.get("total_tokens") or 0) + resp.input_tokens + resp.output_tokens
    total_cost = (state.get("total_cost_usd") or 0.0) + cost

    evidence_row = {
        "node": "classify",
        "elapsed_ms": elapsed_ms,
        "backend": resp.backend,
        "model": model,
        "input_tokens": resp.input_tokens,
        "output_tokens": resp.output_tokens,
        "cost_usd": round(cost, 6),
        "output": parsed,
    }
    evidence = list(state.get("evidence") or []) + [evidence_row]

    update: dict[str, Any] = {
        "classification": parsed,
        "severity": parsed["severity_guess"],
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "evidence": evidence,
    }
    if resp.degraded:
        update["_degraded_mode"] = True
        update["_degraded_reason"] = resp.degraded_reason or "unknown"

    return update

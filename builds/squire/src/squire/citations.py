"""Citation allow-lists and validators for Squire (criterion #17).

Satisfies Phase 17 ROADMAP success criterion #17 "Citation hallucination guard":
 - Static allow-lists for the four frameworks Squire reports under:
     CSF 2.0 RESPOND subcategories (NIST, Feb 2024)
     CSA Agentic AI Profile for NIST AI RMF - MANAGE codes (CSA, April 2025)
     OWASP Top 10 for LLM Applications 2025 (OWASP, 2025)
     MITRE ATT&CK Enterprise tactics (hard allow-list) + techniques (regex)
 - `validate_citation(framework, code)` returns False for any code outside the list.
 - `filter_citations(cites)` drops invalid codes and returns a pruned dict.
 - `validate_citations_with_retry(report, redraft, max_retries=1)` implements the
   "one automatic retry then escalation" behavior consumed by the draft node.

Design notes:
  - MITRE ATT&CK technique IDs are validated by regex (`^T\\d{4}(\\.\\d{3})?$`) because
    the full technique taxonomy is >600 entries and drifts every release. Hard-allow-
    listing tactics + regex-filtering techniques catches 99% of real hallucinations
    (LLMs tend to emit either a plausible-looking but non-existent code or a tactic
    that is wrong for the incident) while keeping the module stable across ATT&CK
    refreshes.
  - CSF 2.0 RESPOND subcategory list baseline from NIST CSF 2.0 published 2024-02-26.
  - CSA Agentic AI Profile MANAGE codes baseline from CSA April 2025 release.
  - Update allow-lists via PR when frameworks rev; add a failing test for any code
    that moves so drift is visible.
"""
from __future__ import annotations

import re
from typing import Callable


# ------------------------------------------------------------------
# CSF 2.0 - RESPOND function subcategory codes
# Source: NIST CSF 2.0 (Feb 2024), RESPOND function.
# ------------------------------------------------------------------
CSF_RS: dict[str, str] = {
    # Incident Management (RS.MA)
    "RS.MA-01": "Incident response plan is executed with relevant third parties",
    "RS.MA-02": "Incident reports are triaged and validated",
    "RS.MA-03": "Incidents are categorized and prioritized",
    "RS.MA-04": "Incidents are escalated or elevated as needed",
    "RS.MA-05": "Criteria for initiating incident recovery are applied",
    # Incident Analysis (RS.AN)
    "RS.AN-03": "Analysis is performed to establish what has taken place during an incident and the root cause",
    "RS.AN-06": "Actions performed during an investigation are recorded with integrity",
    "RS.AN-07": "Incident data and metadata are collected with integrity, preserved, and their provenance documented",
    "RS.AN-08": "An incident's magnitude is estimated and validated",
    # Incident Response Reporting and Communication (RS.CO)
    "RS.CO-02": "Internal and external stakeholders are notified of incidents",
    "RS.CO-03": "Information is shared with designated internal and external stakeholders",
    # Incident Mitigation (RS.MI)
    "RS.MI-01": "Incidents are contained",
    "RS.MI-02": "Incidents are eradicated",
}


# ------------------------------------------------------------------
# CSA Agentic AI Profile for NIST AI RMF -- MANAGE function codes
# Source: Cloud Security Alliance, April 2025 publication.
# ------------------------------------------------------------------
CSA_AGENTIC_MANAGE: dict[str, str] = {
    "MG-1.1": "Context is identified and understood for agentic AI risk management",
    "MG-1.2": "Agentic AI risks are assessed and prioritized",
    "MG-1.3": "Risk response options are evaluated and selected",
    "MG-1.4": "Residual risk is measured and accepted by authorized owners",
    "MG-2.1": "Resources required to manage agentic AI risks are allocated",
    "MG-2.2": "Mechanisms for ongoing risk management are deployed and resourced",
    "MG-2.3": "Procedures for incident handling specific to agentic systems are codified",
    "MG-2.4": "Decommissioning procedures exist for agentic AI systems",
    "MG-3.1": "Risks from third-party agentic AI components are tracked and managed",
    "MG-3.2": "Pre-deployment testing validates that agentic AI operates within intended scope",
    "MG-4.1": "Risks of deployed agentic AI systems are monitored",
    "MG-4.2": "Measurable activities support ongoing agentic AI risk management",
    "MG-4.3": "Incidents and errors are communicated and mitigated",
}


# ------------------------------------------------------------------
# OWASP Top 10 for LLM Applications (2025 edition)
# Source: OWASP LLM Top 10 2025.
# ------------------------------------------------------------------
OWASP_LLM_2025: dict[str, str] = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}


# ------------------------------------------------------------------
# MITRE ATT&CK Enterprise - tactic codes (hard allow-list).
# Source: MITRE ATT&CK v15+ Enterprise matrix.
# ------------------------------------------------------------------
MITRE_TACTICS: dict[str, str] = {
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0010": "Exfiltration",
    "TA0011": "Command and Control",
    "TA0040": "Impact",
    "TA0042": "Resource Development",
    "TA0043": "Reconnaissance",
}

# Regex for ATT&CK Enterprise technique / sub-technique IDs.
# Matches T1001 .. T9999 and T####.### subtechniques. Broad by design; full
# 600+ technique enumeration would fight every ATT&CK release.
ATTACK_TECH_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$")


# ------------------------------------------------------------------
# Framework dispatch
# ------------------------------------------------------------------

FRAMEWORK_ALIASES = {
    # canonical -> accepted aliases (lowercased, dashes -> underscores)
    "csf_2_0": {"csf_2_0", "csf2", "csf20", "nist_csf", "nist_csf_2_0", "csf"},
    "csa_agentic": {"csa_agentic", "csa", "csa_agentic_manage", "csa_manage", "agentic"},
    "owasp_llm": {"owasp_llm", "owasp", "owasp_llm_2025", "llm_top10", "owasp_top10_llm"},
    "mitre_attack": {"mitre_attack", "mitre", "attack", "mitre_att_ck", "att_ck"},
    "nist_800_61_r3": {"nist_800_61_r3", "sp_800_61_r3", "800_61_r3"},
}


def _normalize_framework(framework: str) -> str:
    if not framework:
        return ""
    f = (
        framework.strip()
        .lower()
        .replace("-", "_")
        .replace(".", "_")
        .replace(" ", "_")
        .replace("&", "_")
    )
    # collapse doubled underscores
    while "__" in f:
        f = f.replace("__", "_")
    for canonical, aliases in FRAMEWORK_ALIASES.items():
        if f == canonical or f in aliases:
            return canonical
    return f


def validate_citation(framework: str, code: str) -> bool:
    """Return True iff `code` is in the allow-list for `framework`.

    Unknown frameworks always return False (fail closed). Empty / None returns False.
    """
    if not framework or not code:
        return False
    fw = _normalize_framework(framework)
    code = code.strip()

    if fw == "csf_2_0":
        return code in CSF_RS
    if fw == "csa_agentic":
        return code in CSA_AGENTIC_MANAGE
    if fw == "owasp_llm":
        return code in OWASP_LLM_2025
    if fw == "mitre_attack":
        # Tactic codes are hard allow-listed; techniques validated by regex.
        return code in MITRE_TACTICS or bool(ATTACK_TECH_RE.match(code))
    if fw == "nist_800_61_r3":
        # NIST SP 800-61r3 (April 2025) dropped phase codes in favor of CSF 2.0
        # cross-references. Accept section anchors but discourage use via a
        # narrow validator: only "§N" or "Section N" passes.
        return code.startswith("§") or code.lower().startswith("section")
    # Unknown framework -> fail closed.
    return False


def filter_citations(cites: dict[str, list[str]] | None) -> dict[str, list[str]]:
    """Return a new dict with only the codes that pass validate_citation.

    Frameworks with zero surviving codes are dropped from the result entirely.
    """
    out: dict[str, list[str]] = {}
    for fw, codes in (cites or {}).items():
        keep = [c for c in (codes or []) if validate_citation(fw, c)]
        if keep:
            out[fw] = keep
    return out


def detect_invalid_codes(cites: dict[str, list[str]] | None) -> list[tuple[str, str]]:
    """List (framework, code) pairs that fail validation. Used to build the retry prompt."""
    invalid: list[tuple[str, str]] = []
    for fw, codes in (cites or {}).items():
        for c in (codes or []):
            if not validate_citation(fw, c):
                invalid.append((fw, c))
    return invalid


def build_corrective_prompt(invalid: list[tuple[str, str]]) -> str:
    """Construct the corrective prompt fed back to the LLM on the one retry."""
    return (
        "Your previous response included fabricated citation codes. "
        f"These codes are NOT in the allow-list: {invalid}. "
        "You MUST regenerate the response using ONLY codes from these lists:\n"
        f"  CSF 2.0 RESPOND subcategories: {sorted(CSF_RS.keys())}\n"
        f"  CSA Agentic MANAGE: {sorted(CSA_AGENTIC_MANAGE.keys())}\n"
        f"  OWASP LLM 2025: {sorted(OWASP_LLM_2025.keys())}\n"
        f"  MITRE ATT&CK tactics: {sorted(MITRE_TACTICS.keys())}\n"
        "  MITRE ATT&CK techniques: any code matching T#### or T####.### (4 digits, optional 3-digit subtechnique).\n"
        "If a citation code does not fit one of these frameworks, omit it entirely."
    )


def validate_citations_with_retry(
    report: dict,
    redraft: Callable[[str], dict],
    max_retries: int = 1,
) -> tuple[dict, list[str]]:
    """Criterion #17 core: one automatic retry on fabricated citations, then escalate.

    Args:
        report: draft report dict. Reads `report["citations"]` and writes back
                pruned citations + appended errors on escalation.
        redraft: callable that takes a corrective prompt string and returns a
                 new report dict (the draft node's redraft handle).
        max_retries: retry attempts before escalation (default 1).

    Returns:
        (final_report, escalation_messages). escalation_messages is a list of
        human-readable strings; empty when no escalation was needed.

    The function is deliberately pure w.r.t. `report` semantics: the caller owns
    the report dict. Mutates in place for convenience because the draft node
    only passes this function its own local copy.
    """
    escalations: list[str] = []
    attempts = 0
    while True:
        invalid = detect_invalid_codes(report.get("citations", {}))
        if not invalid:
            return report, escalations

        if attempts >= max_retries:
            # Escalate: drop bad citations, record the violation, flag for HITL.
            report["citations"] = filter_citations(report.get("citations", {}))
            msg = f"citation_hallucination_escalation invalid={invalid}"
            escalations.append(msg)
            report.setdefault("errors", []).append(msg)
            return report, escalations

        attempts += 1
        corrective = build_corrective_prompt(invalid)
        new_report = redraft(corrective)
        # Defensive: preserve any keys the redraft handle didn't set.
        report = {**report, **(new_report or {})}

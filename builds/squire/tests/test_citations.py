"""Unit tests for the citation allow-list validator (criterion #17)."""
from __future__ import annotations

import os

# Required env so pydantic-settings doesn't fail when anything imports from
# squire.settings transitively. citations.py itself is settings-free.
os.environ.setdefault("CD_DB_USER", "x")
os.environ.setdefault("CD_DB_PASS", "x")
os.environ.setdefault("CD_DB_NAME", "x")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "x")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "x")
os.environ.setdefault("ANTHROPIC_API_KEY", "x")
os.environ.setdefault("SQUIRE_WEBHOOK_TOKEN", "x")

from squire.citations import (  # noqa: E402
    ATTACK_TECH_RE,
    CSA_AGENTIC_MANAGE,
    CSF_RS,
    MITRE_TACTICS,
    OWASP_LLM_2025,
    build_corrective_prompt,
    detect_invalid_codes,
    filter_citations,
    validate_citation,
    validate_citations_with_retry,
)


# ----------------------------------------------------------------------
# Allow-list cardinality (guards against accidental deletions)
# ----------------------------------------------------------------------


def test_csf_respond_has_expected_codes():
    # RESPOND function has 13 subcategories in our baseline allow-list.
    assert "RS.MA-03" in CSF_RS
    assert "RS.AN-03" in CSF_RS
    assert "RS.MI-01" in CSF_RS
    assert len(CSF_RS) >= 13


def test_csa_manage_has_expected_codes():
    assert "MG-4.1" in CSA_AGENTIC_MANAGE
    assert "MG-4.3" in CSA_AGENTIC_MANAGE
    assert len(CSA_AGENTIC_MANAGE) >= 10


def test_owasp_llm_is_top_ten():
    assert len(OWASP_LLM_2025) == 10
    assert set(OWASP_LLM_2025.keys()) == {f"LLM{i:02d}" for i in range(1, 11)}


def test_mitre_tactics_has_14_codes():
    # 12 classic + Reconnaissance (TA0043) + Resource Development (TA0042) = 14
    assert len(MITRE_TACTICS) == 14
    assert "TA0001" in MITRE_TACTICS
    assert "TA0043" in MITRE_TACTICS


# ----------------------------------------------------------------------
# validate_citation positive cases
# ----------------------------------------------------------------------


def test_validate_csf_positive():
    assert validate_citation("csf_2_0", "RS.MA-03")
    assert validate_citation("CSF-2.0", "RS.AN-03")
    assert validate_citation("nist_csf", "RS.MI-02")


def test_validate_csa_positive():
    assert validate_citation("csa_agentic", "MG-4.1")
    assert validate_citation("csa", "MG-1.3")


def test_validate_owasp_positive():
    for i in range(1, 11):
        assert validate_citation("owasp_llm", f"LLM{i:02d}")


def test_validate_mitre_tactic_positive():
    assert validate_citation("mitre_attack", "TA0001")
    assert validate_citation("mitre_attack", "TA0040")
    assert validate_citation("mitre", "TA0043")


def test_validate_mitre_technique_positive():
    assert validate_citation("mitre_attack", "T1078")
    assert validate_citation("mitre_attack", "T1078.004")
    assert validate_citation("mitre_attack", "T1001")


# ----------------------------------------------------------------------
# validate_citation negative cases
# ----------------------------------------------------------------------


def test_validate_csf_negative():
    assert not validate_citation("csf_2_0", "RS.FAKE-99")
    assert not validate_citation("csf_2_0", "DE.AE-01")  # DETECT function, not RESPOND
    assert not validate_citation("csf_2_0", "RS.MA-99")


def test_validate_csa_negative():
    assert not validate_citation("csa_agentic", "MG-9.9")
    assert not validate_citation("csa_agentic", "GV-1.1")


def test_validate_owasp_negative():
    assert not validate_citation("owasp_llm", "LLM11")
    assert not validate_citation("owasp_llm", "LLM1")  # missing zero-pad
    assert not validate_citation("owasp_llm", "OWASP1")


def test_validate_mitre_negative():
    assert not validate_citation("mitre_attack", "T999")  # too few digits
    assert not validate_citation("mitre_attack", "T99999")  # too many digits
    assert not validate_citation("mitre_attack", "T1078.12")  # sub-tech needs 3 digits
    assert not validate_citation("mitre_attack", "TA9999")  # not in tactic list


def test_validate_unknown_framework_fails_closed():
    assert not validate_citation("cis_controls", "CIS-1")
    assert not validate_citation("", "TA0001")
    assert not validate_citation("mitre_attack", "")


def test_attack_tech_regex_standalone():
    assert ATTACK_TECH_RE.match("T1078")
    assert ATTACK_TECH_RE.match("T1078.004")
    assert not ATTACK_TECH_RE.match("T107")
    assert not ATTACK_TECH_RE.match("TA0001")


# ----------------------------------------------------------------------
# filter_citations / detect_invalid_codes
# ----------------------------------------------------------------------


def test_filter_citations_drops_invalid():
    cites = {
        "csf_2_0": ["RS.MA-03", "RS.FAKE-99"],
        "mitre_attack": ["T1078", "T9999.999", "TA0001"],
        "owasp_llm": ["LLM03", "LLM99"],
        "unknown_framework": ["ANYTHING"],
    }
    out = filter_citations(cites)
    assert out["csf_2_0"] == ["RS.MA-03"]
    assert out["mitre_attack"] == ["T1078", "T9999.999", "TA0001"]  # T9999.999 passes the regex
    assert out["owasp_llm"] == ["LLM03"]
    assert "unknown_framework" not in out


def test_filter_citations_drops_empty_frameworks():
    cites = {"csf_2_0": ["RS.FAKE"], "mitre_attack": ["TA0001"]}
    out = filter_citations(cites)
    assert "csf_2_0" not in out
    assert out["mitre_attack"] == ["TA0001"]


def test_detect_invalid_codes_lists_all():
    cites = {"csf_2_0": ["RS.MA-03", "RS.FAKE"], "owasp_llm": ["LLM99"]}
    invalid = detect_invalid_codes(cites)
    assert ("csf_2_0", "RS.FAKE") in invalid
    assert ("owasp_llm", "LLM99") in invalid
    assert len(invalid) == 2


# ----------------------------------------------------------------------
# validate_citations_with_retry (criterion #17 retry+escalate)
# ----------------------------------------------------------------------


def test_retry_succeeds_on_second_attempt():
    """First draft has a bad code; retry produces a clean citations dict."""
    calls = []

    def redraft(corrective: str) -> dict:
        calls.append(corrective)
        return {"citations": {"csf_2_0": ["RS.MA-03"]}}

    initial = {"citations": {"csf_2_0": ["RS.MA-03", "RS.FAKE"]}}
    final, escalations = validate_citations_with_retry(initial, redraft, max_retries=1)

    assert len(calls) == 1, "redraft should fire exactly once"
    assert "fabricated citation" in calls[0].lower()
    assert final["citations"] == {"csf_2_0": ["RS.MA-03"]}
    assert escalations == []


def test_retry_escalates_on_persistent_hallucination():
    """Redraft stays broken -- after 1 retry we escalate + drop invalid codes."""

    def broken_redraft(corrective: str) -> dict:
        return {"citations": {"csf_2_0": ["RS.MA-03", "RS.STILL-FAKE"]}}

    initial = {"citations": {"csf_2_0": ["RS.MA-03", "RS.FAKE"]}}
    final, escalations = validate_citations_with_retry(initial, broken_redraft, max_retries=1)

    assert len(escalations) == 1
    assert "citation_hallucination_escalation" in escalations[0]
    # Invalid code dropped, valid code preserved
    assert final["citations"] == {"csf_2_0": ["RS.MA-03"]}
    assert "errors" in final
    assert any("citation_hallucination_escalation" in e for e in final["errors"])


def test_retry_noop_when_already_clean():
    calls = []

    def redraft(_: str) -> dict:
        calls.append(_)
        return {}

    clean = {"citations": {"csf_2_0": ["RS.MA-03"], "owasp_llm": ["LLM01"]}}
    final, escalations = validate_citations_with_retry(clean, redraft, max_retries=1)
    assert calls == []
    assert escalations == []
    assert final["citations"] == clean["citations"]


def test_retry_custom_max_retries():
    """With max_retries=2, two redraft attempts occur before escalation."""
    calls = []

    def broken_redraft(corrective: str) -> dict:
        calls.append(corrective)
        return {"citations": {"csf_2_0": ["RS.FAKE"]}}

    initial = {"citations": {"csf_2_0": ["RS.FAKE"]}}
    final, escalations = validate_citations_with_retry(initial, broken_redraft, max_retries=2)
    assert len(calls) == 2
    assert len(escalations) == 1


# ----------------------------------------------------------------------
# build_corrective_prompt
# ----------------------------------------------------------------------


def test_corrective_prompt_lists_allow_lists():
    prompt = build_corrective_prompt([("csf_2_0", "RS.FAKE")])
    assert "fabricated citation" in prompt.lower()
    assert "RS.MA-03" in prompt
    assert "TA0001" in prompt
    assert "LLM01" in prompt

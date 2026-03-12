#!/usr/bin/env python3
"""ATS keyword match scoring for resume .docx files.

Extracts text from a .docx and scores keyword coverage across three tiers
of AI security / DevSecOps terms.  Higher score = better ATS match.

Target: 90%+ overall score for production resumes.
"""

import argparse
import json
import re
import sys

from docx import Document


# ---------------------------------------------------------------------------
# Keyword tiers
# ---------------------------------------------------------------------------

TIER1_KEYWORDS = {
    # keyword -> list of expanded/alternative forms
    "OWASP Top 10 LLM": ["OWASP Top 10 for LLM", "OWASP LLM Top 10"],
    "MITRE ATLAS": ["MITRE ATLAS"],
    "prompt injection": ["prompt injection"],
    "LLM security": ["LLM security", "large language model security"],
    "AI/ML security": ["AI/ML security", "AI security", "ML security",
                       "artificial intelligence security", "machine learning security"],
    "threat modeling": ["threat modeling", "threat model"],
    "Zero Trust": ["Zero Trust", "zero-trust"],
    "IAM": ["IAM", "identity and access management"],
    "RBAC": ["RBAC", "role-based access control"],
    "DevSecOps": ["DevSecOps"],
    "container security": ["container security"],
    "IaC": ["IaC", "infrastructure as code"],
    "SIEM": ["SIEM", "security information and event management"],
    "SOAR": ["SOAR", "security orchestration"],
    "incident response": ["incident response"],
    "vulnerability management": ["vulnerability management"],
}

TIER2_KEYWORDS = {
    "adversarial ML": ["adversarial ML", "adversarial machine learning"],
    "data poisoning": ["data poisoning"],
    "supply chain security": ["supply chain security", "supply chain risk"],
    "API security": ["API security"],
    "eBPF": ["eBPF"],
    "mTLS": ["mTLS", "mutual TLS"],
    "PAM": ["PAM", "privileged access management"],
    "JIT access": ["JIT access", "just-in-time access"],
    "OPA": ["OPA", "Open Policy Agent"],
    "NIST 800-53": ["NIST 800-53", "NIST SP 800-53"],
    "SOC 2": ["SOC 2", "SOC2"],
    "GRC": ["GRC", "governance risk compliance",
            "governance, risk, and compliance"],
    "red teaming": ["red teaming", "red team"],
    "pen testing": ["pen testing", "penetration testing", "pentest"],
}

TIER3_KEYWORDS = {
    "ISO 42001": ["ISO 42001"],
    "EU AI Act": ["EU AI Act"],
    "NIST AI RMF": ["NIST AI RMF", "AI Risk Management Framework"],
    "RAG security": ["RAG security"],
    "system prompt leakage": ["system prompt leakage", "prompt leakage"],
    "excessive agency": ["excessive agency"],
    "AI governance": ["AI governance"],
    "SecureClaw": ["SecureClaw"],
    "ClawSec": ["ClawSec"],
    "SBOM": ["SBOM", "software bill of materials"],
}

TIER1_POINTS = 4
TIER2_POINTS = 2
TIER3_POINTS = 1

MAX_POINTS = (len(TIER1_KEYWORDS) * TIER1_POINTS
              + len(TIER2_KEYWORDS) * TIER2_POINTS
              + len(TIER3_KEYWORDS) * TIER3_POINTS)  # 16*4 + 14*2 + 10*1 = 102

# Correction: plan says 15 Tier-1 keywords but lists 16. Using actual count.
# Max = 16*4 + 14*2 + 10*1 = 64 + 28 + 10 = 102


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def extract_text(docx_path: str) -> str:
    """Return all paragraph text from a .docx file, joined by newlines."""
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)


def _keyword_present(text_lower: str, forms: list[str]) -> bool:
    """Return True if any form of the keyword appears (case-insensitive)."""
    return any(form.lower() in text_lower for form in forms)


def score_ats(docx_path: str) -> dict:
    """Score keyword coverage and return structured results."""
    text = extract_text(docx_path)
    text_lower = text.lower()

    tier1_hits, tier1_miss = [], []
    tier2_hits, tier2_miss = [], []
    tier3_hits, tier3_miss = [], []

    points = 0

    for kw, forms in TIER1_KEYWORDS.items():
        if _keyword_present(text_lower, forms):
            tier1_hits.append(kw)
            points += TIER1_POINTS
        else:
            tier1_miss.append(kw)

    for kw, forms in TIER2_KEYWORDS.items():
        if _keyword_present(text_lower, forms):
            tier2_hits.append(kw)
            points += TIER2_POINTS
        else:
            tier2_miss.append(kw)

    for kw, forms in TIER3_KEYWORDS.items():
        if _keyword_present(text_lower, forms):
            tier3_hits.append(kw)
            points += TIER3_POINTS
        else:
            tier3_miss.append(kw)

    overall_score = round((points / MAX_POINTS) * 100, 1) if MAX_POINTS else 0

    return {
        "overall_score": overall_score,
        "points_earned": points,
        "points_max": MAX_POINTS,
        "tier1_hits": tier1_hits,
        "tier1_miss": tier1_miss,
        "tier2_hits": tier2_hits,
        "tier2_miss": tier2_miss,
        "tier3_hits": tier3_hits,
        "tier3_miss": tier3_miss,
        "missing_keywords": tier1_miss + tier2_miss + tier3_miss,
        "pass": overall_score >= 90.0,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

TARGET_SCORE = 90.0


def print_report(result: dict):
    """Print human-readable ATS report."""
    print("=" * 60)
    print("ATS KEYWORD SCANNER REPORT")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']}% "
          f"({result['points_earned']}/{result['points_max']} pts)")
    status = "PASS" if result["pass"] else "FAIL"
    print(f"Status: {status} (target >= {TARGET_SCORE}%)")
    print()

    print(f"Tier 1 ({TIER1_POINTS}pt each): "
          f"{len(result['tier1_hits'])}/{len(TIER1_KEYWORDS)} hit")
    if result["tier1_miss"]:
        print(f"  Missing: {', '.join(result['tier1_miss'])}")

    print(f"Tier 2 ({TIER2_POINTS}pt each): "
          f"{len(result['tier2_hits'])}/{len(TIER2_KEYWORDS)} hit")
    if result["tier2_miss"]:
        print(f"  Missing: {', '.join(result['tier2_miss'])}")

    print(f"Tier 3 ({TIER3_POINTS}pt each): "
          f"{len(result['tier3_hits'])}/{len(TIER3_KEYWORDS)} hit")
    if result["tier3_miss"]:
        print(f"  Missing: {', '.join(result['tier3_miss'])}")

    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Score a resume .docx against ATS keyword tiers."
    )
    parser.add_argument("docx_path", help="Path to the resume .docx file")
    parser.add_argument(
        "--output", choices=["human", "json"], default="human",
        help="Output format (default: human)"
    )
    args = parser.parse_args()

    result = score_ats(args.docx_path)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print_report(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()

"""Scoring engine for job postings based on qualification matches."""

import re
from typing import Optional


# Southeast US states for location scoring
SOUTHEAST_STATES = {
    "alabama", "al", "florida", "fl", "georgia", "ga", "south carolina", "sc",
    "north carolina", "nc", "tennessee", "tn", "mississippi", "ms", "louisiana", "la",
    "arkansas", "ar", "virginia", "va", "west virginia", "wv", "kentucky", "ky",
}


def score_posting(posting: dict, config: dict) -> int:
    """
    Score a job posting 0-100 based on qualification matches.

    Components:
        - Cert match:       up to 40 pts
        - Salary match:     up to 20 pts
        - Location match:   up to 15 pts
        - Experience level: up to 15 pts
        - Clearance:        up to 10 pts
    """
    scoring_cfg = config.get("scoring", {})
    my_certs = [c.lower() for c in config.get("my_certs", [])]

    cert_score = _score_certs(posting, my_certs, scoring_cfg.get("cert_match_weight", 40))
    salary_score = _score_salary(posting, scoring_cfg.get("salary_weight", 20))
    location_score = _score_location(posting, scoring_cfg.get("location_weight", 15))
    experience_score = _score_experience(posting, scoring_cfg.get("experience_weight", 15))
    clearance_score = _score_clearance(posting, scoring_cfg.get("clearance_weight", 10))

    total = cert_score + salary_score + location_score + experience_score + clearance_score
    return min(100, max(0, total))


def get_matched_certs(posting: dict, config: dict) -> list[str]:
    """Return list of certs from config that appear in the posting text."""
    my_certs = config.get("my_certs", [])
    text = _get_full_text(posting)
    matched = []
    for cert in my_certs:
        if _cert_in_text(cert, text):
            matched.append(cert)
    return matched


def _get_full_text(posting: dict) -> str:
    """Combine all text fields into one searchable string."""
    parts = [
        posting.get("title", ""),
        posting.get("description", ""),
        posting.get("company", ""),
        posting.get("location", ""),
        posting.get("salary", ""),
        posting.get("qualifications", ""),
    ]
    return " ".join(parts).lower()


def _cert_in_text(cert: str, text: str) -> bool:
    """Check if a cert name appears in text, handling variations."""
    cert_lower = cert.lower()

    # Direct match
    if cert_lower in text:
        return True

    # Handle common cert name variations
    variations = {
        "casp+": ["casp+", "casp plus", "comptia casp", "comptia advanced security practitioner"],
        "securityx": ["securityx", "security x", "comptia securityx"],
        "security+": ["security+", "security plus", "comptia security+", "comptia security plus", "sec+"],
        "network+": ["network+", "network plus", "comptia network+", "comptia network plus", "net+"],
        "ccna": ["ccna", "cisco certified network associate"],
        "aws security specialty": ["aws security", "aws certified security", "security specialty"],
        "sscp": ["sscp", "systems security certified practitioner"],
        "isc2": ["isc2", "isc²", "(isc)²", "(isc)2"],
        "cc": ["certified in cybersecurity", "isc2 cc", "(isc)² cc"],
    }

    for key, alts in variations.items():
        if cert_lower == key or cert_lower in alts:
            for alt in alts:
                if alt in text:
                    return True
    return False


def _score_certs(posting: dict, my_certs: list[str], max_points: int) -> int:
    """Score based on matching certifications. +10 per match, capped at max_points."""
    text = _get_full_text(posting)
    matches = 0
    for cert in my_certs:
        if _cert_in_text(cert, text):
            matches += 1
    points_per_match = 10
    return min(max_points, matches * points_per_match)


def _parse_salary(salary_str: str) -> Optional[float]:
    """
    Extract an annual salary figure from text.
    Handles: $95K, $95,000, $45/hr, $90k-$120k, etc.
    Returns the midpoint annual salary in thousands, or None.
    """
    if not salary_str:
        return None

    text = salary_str.lower().replace(",", "").replace("$", "")

    # Hourly rate pattern: 45/hr, 45 per hour, 45/hour
    hourly_match = re.findall(r"(\d+(?:\.\d+)?)\s*(?:/\s*hr|per\s*hour|/\s*hour|hourly)", text)
    if hourly_match:
        rates = [float(h) for h in hourly_match]
        avg_rate = sum(rates) / len(rates)
        # Convert to annual: rate * 2080 hours
        return (avg_rate * 2080) / 1000

    # Annual salary pattern: 95k, 95000, 95,000
    annual_matches = re.findall(r"(\d+(?:\.\d+)?)\s*k?\b", text)
    if annual_matches:
        values = []
        for m in annual_matches:
            val = float(m)
            # If "k" follows the number in original text, it's thousands
            idx = text.find(m)
            if idx >= 0 and idx + len(m) < len(text) and text[idx + len(m)] == "k":
                values.append(val)
            elif val > 1000:
                # Raw number like 95000
                values.append(val / 1000)
            elif val > 30:
                # Likely already in thousands (e.g., "95" meaning 95K)
                values.append(val)
        if values:
            return sum(values) / len(values)

    return None


def _score_salary(posting: dict, max_points: int) -> int:
    """Score based on salary. 20 if $90K+, 10 if $70-90K, 0 otherwise."""
    salary_text = posting.get("salary", "")
    if not salary_text:
        # Also check description for salary info
        salary_text = posting.get("description", "")

    annual_k = _parse_salary(salary_text)
    if annual_k is None:
        return 0
    if annual_k >= 90:
        return max_points
    if annual_k >= 70:
        return max_points // 2
    return 0


def _score_location(posting: dict, max_points: int) -> int:
    """
    Score based on location.
    15 if Atlanta or Remote, 10 if Georgia, 5 if Southeast, 0 otherwise.
    """
    location = (posting.get("location", "") or "").lower()
    title = (posting.get("title", "") or "").lower()
    desc = (posting.get("description", "") or "").lower()
    combined = f"{location} {title} {desc}"

    if "remote" in combined or "telework" in combined or "work from home" in combined:
        return max_points
    if "atlanta" in location:
        return max_points
    if "georgia" in location or ", ga" in location or " ga " in location:
        return int(max_points * 10 / 15)
    for state in SOUTHEAST_STATES:
        if state in location:
            return int(max_points * 5 / 15)
    return 0


def _score_experience(posting: dict, max_points: int) -> int:
    """
    Score based on required experience years.
    15 if 0-3 years, 10 if 3-5, 5 if 5-7, 0 if 7+.
    """
    text = _get_full_text(posting)

    # Look for experience requirements
    patterns = [
        r"(\d+)\+?\s*(?:to|-)\s*(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)",
        r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)",
        r"minimum\s*(?:of\s*)?(\d+)\s*years?",
        r"at\s*least\s*(\d+)\s*years?",
        r"(\d+)\+\s*years?",
    ]

    min_years = None
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            min_years = int(groups[0])
            break

    if min_years is None:
        # No experience mentioned - assume entry-friendly
        return int(max_points * 10 / 15)
    if min_years <= 3:
        return max_points
    if min_years <= 5:
        return int(max_points * 10 / 15)
    if min_years <= 7:
        return int(max_points * 5 / 15)
    return 0


def _score_clearance(posting: dict, max_points: int) -> int:
    """
    Score based on clearance requirements.
    10 if no clearance required, 5 if preferred, 0 if required.
    """
    text = _get_full_text(posting)

    clearance_terms = [
        "security clearance", "ts/sci", "top secret", "secret clearance",
        "clearance required", "must have clearance", "active clearance",
        "public trust", "dod clearance",
    ]

    preferred_terms = [
        "clearance preferred", "clearance desired", "clearance a plus",
        "clearance is a plus", "preferred: clearance",
    ]

    for term in preferred_terms:
        if term in text:
            return max_points // 2

    for term in clearance_terms:
        if term in text:
            return 0

    # No clearance mentioned
    return max_points

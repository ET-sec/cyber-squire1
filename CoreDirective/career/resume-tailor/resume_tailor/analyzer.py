"""Resume match analyzer. Compares job requirements against master resume data."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from .scraper import JobPosting

console = Console(stderr=True)


@dataclass
class MatchAnalysis:
    """Results of comparing a job posting against the master resume."""

    relevance_score: int = 0  # 0-100
    best_variant: str = ""
    best_variant_data: dict = field(default_factory=dict)
    matching_certs: list[str] = field(default_factory=list)
    matching_skills: list[dict] = field(default_factory=list)  # {"skill": str, "category": str}
    matching_bullets: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    missing_certs: list[str] = field(default_factory=list)
    section_order: list[str] = field(default_factory=list)
    keyword_density: dict = field(default_factory=dict)  # keyword -> count in job posting
    texaco_title: str = ""
    top_qualifications: list[str] = field(default_factory=list)
    top_requirements: list[str] = field(default_factory=list)


def load_master_resume(resume_path: str) -> dict:
    """Load master resume JSON from file path."""
    path = Path(resume_path)
    if not path.exists():
        console.print(f"[red]Error:[/red] Resume file not found: {resume_path}")
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    with open(path, "r") as f:
        return json.load(f)


def analyze_match(posting: JobPosting, resume: dict) -> MatchAnalysis:
    """Analyze how well the master resume matches a job posting.

    Returns a MatchAnalysis with relevance score, best variant, matching/missing items,
    and recommended section ordering.
    """
    analysis = MatchAnalysis()

    # Build the combined text from job posting for keyword matching
    job_text = _build_job_text(posting)
    job_lower = job_text.lower()

    # Extract and count keywords from the job posting
    analysis.keyword_density = _extract_keywords(job_text)

    # 1. Match certifications
    analysis.matching_certs, analysis.missing_certs = _match_certs(
        resume.get("certifications", []),
        posting.required_certs,
        job_lower,
    )

    # 2. Match technical skills across all categories
    analysis.matching_skills, analysis.missing_skills = _match_skills(
        resume.get("technical_skills", {}),
        posting.required_skills,
        job_lower,
    )

    # 3. Score each resume variant and pick the best
    best_variant, best_score, variant_data = _score_variants(
        resume.get("resume_variants", {}),
        job_lower,
        analysis.keyword_density,
    )
    analysis.best_variant = best_variant
    analysis.best_variant_data = variant_data

    # 4. Pick matching bullets from the best variant
    if variant_data:
        analysis.matching_bullets = _rank_bullets(
            variant_data.get("bullets", []),
            analysis.keyword_density,
        )

    # 5. Select the Texaco title variant that best matches
    analysis.texaco_title = _pick_texaco_title(
        resume.get("texaco_experience", {}).get("title_variants", {}),
        best_variant,
    )

    # 6. Calculate overall relevance score
    analysis.relevance_score = _calculate_score(
        cert_matches=len(analysis.matching_certs),
        cert_required=max(len(posting.required_certs), 1),
        skill_matches=len(analysis.matching_skills),
        skill_required=max(len(posting.required_skills), len(analysis.keyword_density) // 2, 1),
        variant_score=best_score,
    )

    # 7. Determine section order based on what matters most for this job
    analysis.section_order = _determine_section_order(analysis, posting)

    # 8. Pick top qualifications (from resume) and requirements (from job)
    analysis.top_qualifications = _pick_top_qualifications(analysis, resume)
    analysis.top_requirements = _pick_top_requirements(posting)

    return analysis


def _build_job_text(posting: JobPosting) -> str:
    """Combine all job posting text fields into one searchable string."""
    parts = [
        posting.job_title,
        posting.description_text,
        " ".join(posting.required_skills),
        " ".join(posting.preferred_skills),
        " ".join(posting.required_certs),
        " ".join(posting.key_responsibilities),
        " ".join(posting.qualifications),
    ]
    return " ".join(parts)


def _extract_keywords(text: str) -> dict[str, int]:
    """Extract meaningful keywords and their frequencies from job text."""
    # Common words to ignore
    stopwords = {
        "the", "and", "or", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "a", "an", "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "this", "that", "these", "those", "it", "its", "we", "our", "you",
        "your", "they", "their", "them", "he", "she", "his", "her",
        "not", "no", "nor", "but", "if", "then", "else", "when", "where",
        "who", "what", "which", "how", "why", "all", "each", "every", "both",
        "few", "more", "most", "other", "some", "such", "only", "own",
        "same", "so", "than", "too", "very", "just", "about", "also",
        "must", "able", "work", "working", "experience", "including", "etc",
        "strong", "knowledge", "understanding", "required", "preferred",
        "minimum", "years", "role", "team", "position", "candidate",
        "will", "ability", "skills", "ensure", "well", "new", "using",
        "across", "within", "based", "related", "including", "such",
    }

    # Extract words and multi-word terms
    keywords: dict[str, int] = {}
    words = re.findall(r"\b[A-Za-z][\w+#./\-]+\b", text)

    for word in words:
        lower = word.lower()
        if lower not in stopwords and len(lower) > 2:
            keywords[lower] = keywords.get(lower, 0) + 1

    # Also look for multi-word technical terms
    multi_word_patterns = [
        r"Zero Trust", r"Active Directory", r"Incident Response",
        r"Risk Management", r"Vulnerability Assessment",
        r"Threat Modeling", r"Security Operations",
        r"Identity and Access Management", r"Penetration Testing",
        r"Cloud Security", r"Network Security",
        r"Docker Compose", r"GitHub Actions",
        r"Burp Suite", r"Group Policy",
        r"Service Control Policies", r"Security Hub",
    ]
    for pattern in multi_word_patterns:
        count = len(re.findall(pattern, text, re.IGNORECASE))
        if count > 0:
            keywords[pattern.lower()] = count

    return keywords


def _match_certs(
    resume_certs: list[dict],
    job_certs: list[str],
    job_lower: str,
) -> tuple[list[str], list[str]]:
    """Match resume certifications against job requirements.

    Returns (matching_certs, missing_certs).
    """
    matching = []
    resume_cert_names = {c["name"].lower(): c["name"] for c in resume_certs}
    resume_cert_issuers = {c.get("issuer", "").lower() for c in resume_certs}

    # Check each job cert against resume
    checked_job_certs = set()
    for jc in job_certs:
        jc_lower = jc.lower()
        found = False
        for rc_lower, rc_name in resume_cert_names.items():
            if jc_lower in rc_lower or rc_lower in jc_lower:
                matching.append(rc_name)
                found = True
                break
        if not found:
            checked_job_certs.add(jc)

    # Also check which resume certs are mentioned in the full job text
    for rc_lower, rc_name in resume_cert_names.items():
        if rc_name not in matching:
            # Check cert name and common abbreviations
            if rc_lower in job_lower:
                matching.append(rc_name)
            # Check for partial matches (e.g., "CASP" in text matching "SecurityX (CASP+)")
            elif any(part.strip().lower() in job_lower for part in rc_name.split("(") if len(part.strip()) > 2):
                matching.append(rc_name)

    missing = list(checked_job_certs - {m.lower() for m in matching})
    return list(dict.fromkeys(matching)), missing  # deduplicate while preserving order


def _match_skills(
    resume_skills: dict[str, list[str]],
    job_skills: list[str],
    job_lower: str,
) -> tuple[list[dict], list[str]]:
    """Match resume skills against job requirements.

    Returns (matching_skills, missing_skills).
    """
    matching = []
    all_resume_skills = {}  # skill_lower -> {"skill": name, "category": cat}

    for category, skills in resume_skills.items():
        for skill in skills:
            skill_lower = skill.lower()
            all_resume_skills[skill_lower] = {"skill": skill, "category": category}
            # Also index the core term for compound skills like "AWS (EC2, IAM, ...)"
            core_match = re.match(r"^([^(]+)", skill)
            if core_match:
                core = core_match.group(1).strip().lower()
                if core != skill_lower:
                    all_resume_skills[core] = {"skill": skill, "category": category}

    # Check which resume skills appear in job text
    matched_names = set()
    for skill_lower, info in all_resume_skills.items():
        if skill_lower in job_lower and info["skill"] not in matched_names:
            matching.append(info)
            matched_names.add(info["skill"])

    # Check which job skills are NOT in resume
    missing = []
    for js in job_skills:
        js_lower = js.lower()
        found = any(js_lower in sk.lower() or sk.lower() in js_lower for sk in matched_names)
        if not found:
            # Also check against all resume skills
            found = any(
                js_lower in rsk or rsk in js_lower
                for rsk in all_resume_skills
            )
        if not found:
            missing.append(js)

    return matching, missing


def _score_variants(
    variants: dict[str, dict],
    job_lower: str,
    keywords: dict[str, int],
) -> tuple[str, float, dict]:
    """Score each resume variant against the job posting keywords.

    Returns (best_variant_key, best_score, best_variant_data).
    """
    best_key = ""
    best_score = 0.0
    best_data = {}

    for key, variant in variants.items():
        score = 0.0

        # Score the title match
        title_lower = variant.get("title", "").lower()
        for word in title_lower.split():
            if word in job_lower and len(word) > 3:
                score += 5

        # Score the summary match
        summary_lower = variant.get("summary", "").lower()
        for kw, count in keywords.items():
            if kw in summary_lower:
                score += count * 2

        # Score the bullet points
        for bullet in variant.get("bullets", []):
            bullet_lower = bullet.lower()
            for kw, count in keywords.items():
                if kw in bullet_lower:
                    score += count

        if score > best_score:
            best_score = score
            best_key = key
            best_data = variant

    # Normalize score to 0-100 range (rough normalization)
    max_possible = max(sum(keywords.values()) * 3, 1)
    normalized = min(100, int((best_score / max_possible) * 100))

    return best_key, normalized, best_data


def _rank_bullets(bullets: list[str], keywords: dict[str, int]) -> list[str]:
    """Rank bullets by keyword relevance, highest first."""
    scored = []
    for bullet in bullets:
        bullet_lower = bullet.lower()
        score = sum(count for kw, count in keywords.items() if kw in bullet_lower)
        scored.append((score, bullet))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [bullet for _, bullet in scored]


def _pick_texaco_title(
    title_variants: dict[str, str],
    best_variant: str,
) -> str:
    """Pick the Texaco experience title that best matches the chosen variant."""
    mapping = {
        "cloud_network_security": "cloud_network",
        "devsecops": "devsecops",
        "security_solutions_architect": "security_architect",
        "senior_iam": "iam",
    }
    mapped_key = mapping.get(best_variant, "")
    return title_variants.get(mapped_key, title_variants.get("cloud_network", "IT Administrator & Network Support"))


def _calculate_score(
    cert_matches: int,
    cert_required: int,
    skill_matches: int,
    skill_required: int,
    variant_score: float,
) -> int:
    """Calculate overall relevance score (0-100)."""
    cert_score = min(100, (cert_matches / cert_required) * 100) if cert_required > 0 else 50
    skill_score = min(100, (skill_matches / skill_required) * 100) if skill_required > 0 else 50

    # Weighted average: skills (40%), certs (30%), variant fit (30%)
    total = (skill_score * 0.40) + (cert_score * 0.30) + (variant_score * 0.30)
    return min(100, max(0, int(total)))


def _determine_section_order(analysis: MatchAnalysis, posting: JobPosting) -> list[str]:
    """Determine optimal section ordering based on what the job values most."""
    sections = {
        "certifications": len(analysis.matching_certs) * 10,
        "technical_skills": len(analysis.matching_skills) * 5,
        "experience_primary": 50,  # Always important
        "experience_texaco": 30,
        "education": 20,
        "project": 15,
        "dod_compliance": 0,
    }

    # Boost certifications if the job explicitly asks for them
    if posting.required_certs:
        sections["certifications"] += 20

    # Boost DoD compliance if mentioned
    desc_lower = posting.description_text.lower()
    if "dod" in desc_lower or "8140" in desc_lower or "8570" in desc_lower or "clearance" in desc_lower:
        sections["dod_compliance"] += 40

    # Boost education if "degree" or "bachelor" mentioned prominently
    if "degree" in desc_lower or "bachelor" in desc_lower or "university" in desc_lower:
        sections["education"] += 15

    # Sort by score descending
    ordered = sorted(sections.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in ordered]


def _pick_top_qualifications(analysis: MatchAnalysis, resume: dict) -> list[str]:
    """Pick top 3 qualifications from the resume that match the job best."""
    quals = []

    # Add top matching cert
    if analysis.matching_certs:
        quals.append(f"Holds {analysis.matching_certs[0]} certification")

    # Add best variant summary snippet
    if analysis.best_variant_data:
        summary = analysis.best_variant_data.get("summary", "")
        if summary:
            quals.append(summary)

    # Add top matching bullet
    if analysis.matching_bullets:
        quals.append(analysis.matching_bullets[0])

    # Add skill breadth
    if len(analysis.matching_skills) >= 5:
        categories = list({s["category"] for s in analysis.matching_skills[:8]})
        quals.append(
            f"Technical depth across {len(categories)} domains: "
            + ", ".join(categories[:4])
        )

    return quals[:3]


def _pick_top_requirements(posting: JobPosting) -> list[str]:
    """Pick top 3 requirements from the job posting."""
    requirements = []

    if posting.required_certs:
        requirements.append(f"Certifications: {', '.join(posting.required_certs[:3])}")

    if posting.years_experience:
        requirements.append(f"Experience: {posting.years_experience}")

    for resp in posting.key_responsibilities[:3]:
        if resp not in requirements:
            requirements.append(resp)

    for qual in posting.qualifications[:3]:
        if qual not in requirements and len(requirements) < 3:
            requirements.append(qual)

    return requirements[:3]


def analysis_to_dict(analysis: MatchAnalysis) -> dict:
    """Convert MatchAnalysis to a dictionary for serialization."""
    return {
        "relevance_score": analysis.relevance_score,
        "best_variant": analysis.best_variant,
        "best_variant_data": analysis.best_variant_data,
        "matching_certs": analysis.matching_certs,
        "matching_skills": analysis.matching_skills,
        "matching_bullets": analysis.matching_bullets,
        "missing_skills": analysis.missing_skills,
        "missing_certs": analysis.missing_certs,
        "section_order": analysis.section_order,
        "texaco_title": analysis.texaco_title,
        "top_qualifications": analysis.top_qualifications,
        "top_requirements": analysis.top_requirements,
    }

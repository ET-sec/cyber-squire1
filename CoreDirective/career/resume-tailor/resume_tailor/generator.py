"""Resume and cover letter generator using Claude API."""

import os
from pathlib import Path

import anthropic
import jinja2
from rich.console import Console

from .analyzer import MatchAnalysis, analysis_to_dict
from .scraper import JobPosting, posting_to_dict

console = Console(stderr=True)

MODEL = "claude-sonnet-4-5-20250929"

# Words and patterns the generator must never use
BANNED_WORDS = [
    "leverage", "delve", "comprehensive", "robust", "streamline",
    "cutting-edge", "game-changer", "seamless", "spearheaded",
    "synergy", "paradigm", "disruptive", "innovative solutions",
    "I am writing to express my interest",
    "I am excited to apply",
]

BANNED_PATTERN_NOTE = (
    "NEVER use hyphens or dashes as punctuation (em dashes, en dashes). "
    "Use periods, commas, or semicolons instead. "
    "NEVER use any of these words/phrases: " + ", ".join(BANNED_WORDS)
)

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _get_client() -> anthropic.Anthropic:
    """Get an Anthropic client, checking for API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY environment variable is not set.\n"
            "Set it with: export ANTHROPIC_API_KEY=sk-ant-..."
        )
        raise SystemExit(1)
    return anthropic.Anthropic(api_key=api_key)


def _get_template_env() -> jinja2.Environment:
    """Get Jinja2 template environment."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def generate_tailored_resume(
    posting: JobPosting,
    resume: dict,
    analysis: MatchAnalysis,
) -> str:
    """Generate a tailored resume using Claude to rewrite bullets with job keywords.

    Returns rendered Markdown string.
    """
    client = _get_client()

    # Build the prompt for Claude to rewrite the bullets
    variant = analysis.best_variant_data
    job_keywords = list(analysis.keyword_density.keys())[:30]

    rewrite_prompt = f"""You are a resume optimization expert. Rewrite the following resume bullets for a {posting.job_title} role at {posting.company_name or 'the target company'}.

JOB TITLE: {posting.job_title}
COMPANY: {posting.company_name or 'Target Company'}
JOB DESCRIPTION EXCERPT:
{posting.description_text[:3000]}

KEY JOB KEYWORDS: {', '.join(job_keywords[:20])}

ORIGINAL BULLETS (from {variant.get('title', 'current role')} at {variant.get('company', 'company')}):
{chr(10).join('- ' + b for b in analysis.matching_bullets)}

INSTRUCTIONS:
1. Rewrite each bullet to naturally incorporate relevant job posting keywords where truthful
2. Keep all quantified metrics (numbers, percentages) exactly as they are
3. Front-load the most relevant bullets for this specific role
4. Maintain the STAR format: Action verb + what you did + measurable result
5. Keep each bullet to one sentence, under 200 characters when possible
6. {BANNED_PATTERN_NOTE}
7. Return ONLY the rewritten bullets, one per line, prefixed with "- "
8. Return the same number of bullets as provided
9. Do NOT fabricate new achievements or metrics. Only rephrase existing ones."""

    console.print("[dim]Generating tailored resume bullets...[/dim]")
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": rewrite_prompt}],
    )

    rewritten_text = response.content[0].text.strip()
    rewritten_bullets = [
        line.lstrip("- ").strip()
        for line in rewritten_text.split("\n")
        if line.strip().startswith("- ") or line.strip().startswith("* ")
    ]

    # Fall back to original bullets if Claude response is malformed
    if len(rewritten_bullets) < 3:
        console.print("[yellow]Warning:[/yellow] Claude response had too few bullets, using originals with keyword additions.")
        rewritten_bullets = analysis.matching_bullets

    # Also rewrite summary
    summary_prompt = f"""Write a one-sentence professional summary for {resume['name']} applying for {posting.job_title} at {posting.company_name or 'the target company'}.

Original summary: {variant.get('summary', '')}

Requirements from job posting:
{chr(10).join('- ' + r for r in analysis.top_requirements[:5])}

Matching certifications: {', '.join(analysis.matching_certs[:5])}

RULES:
- One sentence only, under 250 characters
- Include the most relevant certification and 2-3 key technical skills from the job posting
- {BANNED_PATTERN_NOTE}
- Return ONLY the summary sentence, nothing else"""

    summary_response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": summary_prompt}],
    )
    tailored_summary = summary_response.content[0].text.strip().strip('"')

    # Rewrite Texaco bullets too
    texaco_bullets = resume.get("texaco_experience", {}).get("common_bullets", [])
    texaco_prompt = f"""Rewrite these IT Administrator bullets to better align with a {posting.job_title} role. Incorporate relevant keywords where truthful.

ORIGINAL BULLETS:
{chr(10).join('- ' + b for b in texaco_bullets)}

JOB KEYWORDS: {', '.join(job_keywords[:15])}

RULES:
1. Keep all metrics and facts exactly as stated
2. Only rephrase to highlight relevance to the target role
3. {BANNED_PATTERN_NOTE}
4. Return ONLY the rewritten bullets, one per line, prefixed with "- "
5. Same number of bullets as provided"""

    texaco_response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": texaco_prompt}],
    )
    texaco_rewritten_text = texaco_response.content[0].text.strip()
    texaco_rewritten = [
        line.lstrip("- ").strip()
        for line in texaco_rewritten_text.split("\n")
        if line.strip().startswith("- ") or line.strip().startswith("* ")
    ]
    if len(texaco_rewritten) < 3:
        texaco_rewritten = texaco_bullets

    # Organize skills by relevance
    matching_skill_names = [s["skill"] for s in analysis.matching_skills]
    all_skills_flat = []
    for category, skills in resume.get("technical_skills", {}).items():
        for skill in skills:
            all_skills_flat.append({"skill": skill, "category": category})

    # Split into matching (front) and other (back)
    other_skills = [s for s in all_skills_flat if s["skill"] not in matching_skill_names]

    # Group matching skills by category
    matching_by_category: dict[str, list[str]] = {}
    for s in analysis.matching_skills:
        cat = s["category"]
        if cat not in matching_by_category:
            matching_by_category[cat] = []
        matching_by_category[cat].append(s["skill"])

    other_by_category: dict[str, list[str]] = {}
    for s in other_skills:
        cat = s["category"]
        if cat not in other_by_category:
            other_by_category[cat] = []
        other_by_category[cat].append(s["skill"])

    # Merge: matching categories first, then others
    skills_by_category: dict[str, list[str]] = {}
    for cat in matching_by_category:
        skills_by_category[cat] = matching_by_category[cat]
        if cat in other_by_category:
            skills_by_category[cat].extend(other_by_category[cat])
    for cat in other_by_category:
        if cat not in skills_by_category:
            skills_by_category[cat] = other_by_category[cat]

    # Render the template
    env = _get_template_env()
    template = env.get_template("resume.md.j2")

    # Determine cert ordering: matching first
    all_certs = resume.get("certifications", [])
    matching_cert_names = set(analysis.matching_certs)
    certs_ordered = (
        [c for c in all_certs if c["name"] in matching_cert_names]
        + [c for c in all_certs if c["name"] not in matching_cert_names]
    )

    rendered = template.render(
        name=resume["name"],
        email=resume["email"],
        phone=resume["phone"],
        location=resume["location"],
        linkedin=resume["linkedin"],
        github=resume["github"],
        summary=tailored_summary,
        certifications=certs_ordered,
        skills_by_category=skills_by_category,
        primary_title=variant.get("title", "Security Engineer"),
        primary_company=variant.get("company", ""),
        primary_bullets=rewritten_bullets,
        texaco_title=analysis.texaco_title,
        texaco_location=resume.get("texaco_experience", {}).get("location", ""),
        texaco_dates=resume.get("texaco_experience", {}).get("dates", ""),
        texaco_bullets=texaco_rewritten,
        education=resume.get("education", {}),
        project=resume.get("project", {}),
        dod=resume.get("dod_8140_compliance", {}),
        section_order=analysis.section_order,
        relevance_score=analysis.relevance_score,
        job_title=posting.job_title,
        company_name=posting.company_name,
    )

    return rendered


def generate_cover_letter(
    posting: JobPosting,
    resume: dict,
    analysis: MatchAnalysis,
) -> str:
    """Generate a tailored cover letter using Claude.

    Returns rendered Markdown string.
    """
    client = _get_client()

    prompt = f"""Write a cover letter for {resume['name']} applying for the {posting.job_title} position at {posting.company_name or 'the company'}.

CANDIDATE INFO:
- Name: {resume['name']}
- Location: {resume['location']}
- Email: {resume['email']}

TOP 3 CANDIDATE QUALIFICATIONS:
{chr(10).join('- ' + q for q in analysis.top_qualifications)}

TOP 3 JOB REQUIREMENTS:
{chr(10).join('- ' + r for r in analysis.top_requirements)}

MATCHING CERTIFICATIONS: {', '.join(analysis.matching_certs[:5])}

JOB DESCRIPTION EXCERPT:
{posting.description_text[:2000]}

COMPANY: {posting.company_name or 'the company'}
LOCATION: {posting.location or 'Not specified'}
REMOTE: {posting.remote_status or 'Not specified'}

STRICT RULES:
1. 250-350 words ONLY
2. Three paragraphs: opening hook, qualification mapping, closing
3. Opening: Start with something specific about the company or role. NO "I am writing to express my interest" or "I am excited to apply"
4. Middle: Map exactly 3 of the candidate's qualifications to 3 specific job requirements. Use concrete numbers from the resume.
5. Closing: Brief, confident, forward-looking. No begging.
6. Tone: Professional but human. Write like a confident engineer, not a corporate drone.
7. {BANNED_PATTERN_NOTE}
8. NEVER use hyphens or dashes as punctuation anywhere in the letter. Use periods, commas, or semicolons instead.
9. Return ONLY the cover letter body text (no headers, no "Dear Hiring Manager", no signature block). Those will be added by the template."""

    console.print("[dim]Generating cover letter...[/dim]")
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    letter_body = response.content[0].text.strip()

    # Render with template
    env = _get_template_env()
    template = env.get_template("cover_letter.md.j2")

    rendered = template.render(
        name=resume["name"],
        email=resume["email"],
        phone=resume["phone"],
        location=resume["location"],
        date=_get_date_string(),
        company_name=posting.company_name or "Hiring Team",
        job_title=posting.job_title,
        letter_body=letter_body,
    )

    return rendered


def _get_date_string() -> str:
    """Get current date formatted for a letter."""
    from datetime import date
    return date.today().strftime("%B %d, %Y")

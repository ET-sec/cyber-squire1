"""Company research brief generator using Claude API."""

import os
from pathlib import Path

import anthropic
import jinja2
from rich.console import Console

from .analyzer import MatchAnalysis
from .scraper import JobPosting

console = Console(stderr=True)

MODEL = "claude-sonnet-4-5-20250929"
TEMPLATES_DIR = Path(__file__).parent / "templates"


def _get_client() -> anthropic.Anthropic:
    """Get an Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(
            "[red]Error:[/red] ANTHROPIC_API_KEY environment variable is not set."
        )
        raise SystemExit(1)
    return anthropic.Anthropic(api_key=api_key)


def generate_research_brief(
    posting: JobPosting,
    resume: dict,
    analysis: MatchAnalysis,
) -> str:
    """Generate a company research brief using Claude.

    Returns rendered Markdown string.
    """
    client = _get_client()

    prompt = f"""You are a career research analyst. Generate a company research brief for a job candidate preparing for an interview.

CANDIDATE: {resume['name']}
TARGET ROLE: {posting.job_title}
COMPANY: {posting.company_name or 'Unknown Company'}
LOCATION: {posting.location or 'Not specified'}
REMOTE STATUS: {posting.remote_status or 'Not specified'}
SALARY: {posting.salary_range or 'Not listed'}
JOB URL: {posting.url}

JOB DESCRIPTION:
{posting.description_text[:4000]}

CANDIDATE'S MATCHING QUALIFICATIONS:
- Certifications: {', '.join(analysis.matching_certs[:5])}
- Top skills: {', '.join(s['skill'] for s in analysis.matching_skills[:10])}
- Relevance score: {analysis.relevance_score}%

Generate the following sections. Be specific and actionable.

1. COMPANY OVERVIEW (2-3 sentences about what the company does, their industry, and approximate size if inferrable from the job posting)

2. WHY THIS ROLE EXISTS (2-3 sentences analyzing what business problem or growth area this role addresses, based on the job description)

3. TEAM AND REPORTING STRUCTURE (what can be inferred about the team from the posting: team size hints, who this role reports to, cross-functional relationships)

4. TECHNOLOGY STACK (list the specific tools, platforms, and technologies mentioned or implied)

5. CULTURE SIGNALS (what the job posting language reveals about company culture: formal vs casual, fast-paced vs methodical, values emphasized)

6. INTERVIEW TALKING POINTS (5 specific talking points that map the candidate's experience to this role's needs. Each should reference a specific qualification and how it addresses a specific requirement.)

7. QUESTIONS TO ASK (5 thoughtful questions the candidate should ask in the interview. These should demonstrate domain knowledge and genuine curiosity, not generic questions.)

8. RED FLAGS TO WATCH (any concerning signals from the posting: unrealistic requirements, unclear scope, etc. Be honest but not alarmist. If none, say "None identified.")

9. PREPARATION CHECKLIST (5 specific things the candidate should do before the interview)

FORMAT RULES:
- Use plain text, no markdown formatting (the template will handle that)
- Separate each section with a blank line
- Label each section with its number and title as shown above
- Be direct and specific. No filler. No corporate speak.
- If information isn't available, say so rather than guessing."""

    console.print("[dim]Generating company research brief...[/dim]")
    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    research_text = response.content[0].text.strip()

    # Parse the response into sections
    sections = _parse_research_sections(research_text)

    # Render with template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template("research.md.j2")

    rendered = template.render(
        company_name=posting.company_name or "Target Company",
        job_title=posting.job_title,
        location=posting.location or "Not specified",
        remote_status=posting.remote_status or "Not specified",
        salary_range=posting.salary_range or "Not listed",
        job_url=posting.url,
        relevance_score=analysis.relevance_score,
        matching_certs=analysis.matching_certs,
        matching_skills=[s["skill"] for s in analysis.matching_skills[:10]],
        company_overview=sections.get("company_overview", "Not available"),
        why_role_exists=sections.get("why_role_exists", "Not available"),
        team_structure=sections.get("team_structure", "Not available"),
        tech_stack=sections.get("tech_stack", "Not available"),
        culture_signals=sections.get("culture_signals", "Not available"),
        talking_points=sections.get("talking_points", "Not available"),
        questions_to_ask=sections.get("questions_to_ask", "Not available"),
        red_flags=sections.get("red_flags", "None identified"),
        preparation_checklist=sections.get("preparation_checklist", "Not available"),
    )

    return rendered


def _parse_research_sections(text: str) -> dict[str, str]:
    """Parse Claude's research response into named sections."""
    sections = {}
    current_key = ""
    current_lines: list[str] = []

    section_map = {
        "1. COMPANY OVERVIEW": "company_overview",
        "2. WHY THIS ROLE EXISTS": "why_role_exists",
        "3. TEAM AND REPORTING STRUCTURE": "team_structure",
        "4. TECHNOLOGY STACK": "tech_stack",
        "5. CULTURE SIGNALS": "culture_signals",
        "6. INTERVIEW TALKING POINTS": "talking_points",
        "7. QUESTIONS TO ASK": "questions_to_ask",
        "8. RED FLAGS TO WATCH": "red_flags",
        "9. PREPARATION CHECKLIST": "preparation_checklist",
    }

    for line in text.split("\n"):
        stripped = line.strip()
        matched = False
        for header, key in section_map.items():
            if stripped.upper().startswith(header) or stripped.upper().startswith(header.split(". ", 1)[1]):
                # Save previous section
                if current_key:
                    sections[current_key] = "\n".join(current_lines).strip()
                current_key = key
                current_lines = []
                # Check if there's content on the same line after the header
                after_header = stripped[len(header):].strip().lstrip(":").strip()
                if not after_header:
                    # Try matching without number prefix
                    short_header = header.split(". ", 1)[1]
                    if stripped.upper().startswith(short_header):
                        after_header = stripped[len(short_header):].strip().lstrip(":").strip()
                if after_header:
                    current_lines.append(after_header)
                matched = True
                break

        if not matched and current_key:
            current_lines.append(line)

    # Save the last section
    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections

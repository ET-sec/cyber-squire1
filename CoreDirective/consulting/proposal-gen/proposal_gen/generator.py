"""Claude API content generation for proposal sections."""

import os

import anthropic

from .config import BANNED_WORDS, CONSULTANT, STATS, detect_service_type, get_phases


ANTI_SLOP_INSTRUCTION = (
    "WRITING RULES (follow exactly):\n"
    "- Never use these words: " + ", ".join(BANNED_WORDS) + "\n"
    "- Do not use hyphens as punctuation (em dashes). Use periods instead.\n"
    "- Write short, direct sentences. No filler.\n"
    "- Be specific. Use numbers, timelines, and concrete deliverables.\n"
    "- Tone: confident, professional, no fluff.\n"
    "- Do not use exclamation marks.\n"
    "- Do not start sentences with 'We' more than twice in a row.\n"
)

MODEL = "claude-sonnet-4-5-20250929"


def _get_client() -> anthropic.Anthropic:
    """Initialize the Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Export it before running: export ANTHROPIC_API_KEY=sk-ant-..."
        )
    return anthropic.Anthropic(api_key=api_key)


def _call_claude(system_prompt: str, user_prompt: str) -> str:
    """Make a single Claude API call and return the text response."""
    client = _get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def generate_executive_summary(company: str, need: str, contact: str | None = None) -> str:
    """Generate a 3-4 sentence executive summary tailored to the client."""
    system = (
        "You are a senior security and automation consultant writing a proposal. "
        f"Your name is {CONSULTANT['name']}. Your firm is {CONSULTANT['company']}. "
        f"Your certifications: {', '.join(CONSULTANT['certifications'])}.\n\n"
        f"{ANTI_SLOP_INSTRUCTION}"
    )

    contact_line = f"The primary contact is {contact}. " if contact else ""

    user = (
        f"Write an executive summary (3-4 sentences, plain text, no headers) for a consulting proposal.\n\n"
        f"Client: {company}\n"
        f"{contact_line}"
        f"Their need: {need}\n\n"
        f"Cover: what they need, why it matters to their business, and what CoreDirective will deliver. "
        f"Be specific to their situation. Do not be generic."
    )

    return _call_claude(system, user)


def generate_scope_descriptions(
    company: str, need: str, service_type: str
) -> list[dict]:
    """Generate enriched phase descriptions using Claude.

    Takes the template phases and asks Claude to make them specific to this client.
    Returns a list of phase dicts with enriched 'description' fields.
    """
    phases = get_phases(service_type)

    phase_summary = "\n".join(
        f"- Phase {i+1}: {p['name']} (deliverables: {', '.join(p['deliverables'])})"
        for i, p in enumerate(phases)
    )

    system = (
        "You are writing scope of work descriptions for a consulting proposal. "
        f"Consultant: {CONSULTANT['name']} at {CONSULTANT['company']}.\n\n"
        f"{ANTI_SLOP_INSTRUCTION}"
    )

    user = (
        f"Client: {company}\n"
        f"Their need: {need}\n"
        f"Service type: {service_type.replace('_', ' ')}\n\n"
        f"Phases:\n{phase_summary}\n\n"
        f"For each phase, write a 2-3 sentence description that is specific to this client's situation. "
        f"Return ONLY the descriptions, one per line, separated by '---' on its own line. "
        f"No phase names, no numbering, no headers. Just the description text for each phase in order."
    )

    response = _call_claude(system, user)

    descriptions = [d.strip() for d in response.split("---") if d.strip()]

    enriched_phases = []
    for i, phase in enumerate(phases):
        enriched = phase.copy()
        if i < len(descriptions):
            enriched["description"] = descriptions[i]
        enriched_phases.append(enriched)

    return enriched_phases


def generate_qualification_framing(company: str, need: str, service_type: str) -> str:
    """Generate a paragraph framing qualifications for this specific engagement."""
    system = (
        "You are a senior consultant positioning your qualifications for a specific client. "
        f"Your certifications: {', '.join(CONSULTANT['certifications'])}. "
        f"DoD compliance: {CONSULTANT['dod_8140']}.\n\n"
        f"Key stats from past work:\n"
        f"- Managed {STATS['security_group_rules']} security group rules across AWS environments\n"
        f"- Deployed {STATS['aws_resources']} AWS resources in production infrastructure\n"
        f"- Orchestrating {STATS['docker_services']} Docker services in a single deployment stack\n"
        f"- Achieved {STATS['alert_automation']} alert automation coverage\n\n"
        f"{ANTI_SLOP_INSTRUCTION}"
    )

    user = (
        f"Client: {company}\n"
        f"Their need: {need}\n"
        f"Service type: {service_type.replace('_', ' ')}\n\n"
        f"Write 3-4 sentences explaining why these qualifications and this experience "
        f"are directly relevant to what {company} needs. "
        f"Reference specific certifications that matter for this engagement. "
        f"Do not list all certifications. Pick the 3-4 most relevant ones."
    )

    return _call_claude(system, user)


def generate_all_content(
    company: str,
    need: str,
    contact: str | None = None,
    service_type: str | None = None,
) -> dict:
    """Generate all proposal content in a single call sequence.

    Returns a dict with keys:
        - executive_summary: str
        - phases: list[dict] (enriched with Claude descriptions)
        - qualification_framing: str
        - service_type: str
    """
    if service_type is None:
        service_type = detect_service_type(need)

    executive_summary = generate_executive_summary(company, need, contact)
    phases = generate_scope_descriptions(company, need, service_type)
    qualification_framing = generate_qualification_framing(company, need, service_type)

    return {
        "executive_summary": executive_summary,
        "phases": phases,
        "qualification_framing": qualification_framing,
        "service_type": service_type,
    }

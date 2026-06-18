"""Digest formatting for terminal and webhook output."""

from datetime import date
from typing import Optional


def format_digest(postings: list[dict], total_scraped: int, config: dict) -> str:
    """
    Format a list of scored postings into a readable digest.

    Args:
        postings: Scored and filtered postings, sorted by score desc.
        total_scraped: Total number of postings scraped before filtering.
        config: Full config dict (for cert matching display).

    Returns:
        Formatted digest string.
    """
    today = date.today().strftime("%B %d, %Y")
    n = len(postings)

    lines = []
    lines.append(f"DAILY JOB DIGEST -- {today}")
    lines.append(f"Found: {n} matches (filtered from {total_scraped} scraped)")
    lines.append("")

    if n == 0:
        lines.append("No new postings scored 50+ today.")
        lines.append("Try adjusting search terms or lowering the score threshold.")
        return "\n".join(lines)

    # Show top 10 postings
    display_postings = postings[:10]

    for p in display_postings:
        lines.append("---")
        lines.append(f"SCORE: {p.get('score', 0)}/100")
        lines.append(f"{p.get('title', 'Unknown Title')} -- {p.get('company', 'Unknown Company')}")

        loc_salary_parts = []
        if p.get("location"):
            loc_salary_parts.append(p["location"])
        if p.get("salary"):
            loc_salary_parts.append(p["salary"])
        if loc_salary_parts:
            lines.append(" | ".join(loc_salary_parts))

        certs = p.get("matched_certs", [])
        if certs:
            lines.append(f"Certs matched: {', '.join(certs)}")

        if p.get("url"):
            lines.append(p["url"])

        if p.get("description"):
            snippet = p["description"][:200]
            if len(p["description"]) > 200:
                snippet += "..."
            lines.append(f"  {snippet}")

        lines.append(f"[Source: {p.get('source', 'unknown')}]")
        lines.append("---")
        lines.append("")

    # Summary
    high = sum(1 for p in postings if p.get("score", 0) >= 80)
    mid = sum(1 for p in postings if 60 <= p.get("score", 0) < 80)
    low = sum(1 for p in postings if 50 <= p.get("score", 0) < 60)

    lines.append(f"Summary: {high} scored 80+, {mid} scored 60-79, {low} scored 50-59")

    if postings:
        top = postings[0]
        reason = _explain_top_score(top)
        lines.append(f"Top opportunity: {top.get('title', 'Unknown')} -- {reason}")

    return "\n".join(lines)


def format_history(postings: list[dict]) -> str:
    """Format all historical postings for display."""
    if not postings:
        return "No postings in database."

    lines = ["ALL POSTINGS HISTORY", "=" * 60, ""]

    for p in postings:
        applied_marker = " [APPLIED]" if p.get("date_applied") else ""
        lines.append(
            f"[{p.get('id', '?'):>4}] {p.get('score', 0):>3}/100 | "
            f"{p.get('title', 'Unknown')[:40]:<40} | "
            f"{p.get('company', 'Unknown')[:20]:<20} | "
            f"{p.get('date_found', 'N/A')}{applied_marker}"
        )

    lines.append("")
    lines.append(f"Total: {len(postings)} postings")
    return "\n".join(lines)


def format_tracker(postings: list[dict]) -> str:
    """Format application tracker view."""
    if not postings:
        return "No applications tracked yet. Use --applied <id> to mark a posting."

    lines = ["APPLICATION TRACKER", "=" * 60, ""]

    for p in postings:
        lines.append(f"[{p.get('id', '?'):>4}] {p.get('title', 'Unknown')}")
        lines.append(f"       Company: {p.get('company', 'Unknown')}")
        lines.append(f"       Score: {p.get('score', 0)}/100")
        lines.append(f"       Found: {p.get('date_found', 'N/A')}")
        lines.append(f"       Applied: {p.get('date_applied', 'N/A')}")
        if p.get("url"):
            lines.append(f"       URL: {p['url']}")
        lines.append("")

    lines.append(f"Total applications: {len(postings)}")
    return "\n".join(lines)


def format_telegram(postings: list[dict], total_scraped: int, config: dict) -> str:
    """
    Format digest specifically for Telegram (shorter, with emoji-free markers).

    Uses Telegram-compatible formatting (plain text, no markdown issues).
    """
    today = date.today().strftime("%Y-%m-%d")
    n = len(postings)

    lines = []
    lines.append(f"JOB DIGEST | {today}")
    lines.append(f"{n} matches from {total_scraped} scraped")
    lines.append("")

    if n == 0:
        lines.append("No new matches today.")
        return "\n".join(lines)

    for p in postings[:5]:  # Telegram gets top 5 to avoid message length limits
        lines.append(f"[{p.get('score', 0)}/100] {p.get('title', '?')}")
        lines.append(f"  {p.get('company', '?')} | {p.get('location', '?')}")
        if p.get("salary"):
            lines.append(f"  {p['salary']}")
        if p.get("url"):
            lines.append(f"  {p['url']}")
        lines.append("")

    if n > 5:
        lines.append(f"... and {n - 5} more. Run job-digest --history for full list.")

    return "\n".join(lines)


def _explain_top_score(posting: dict) -> str:
    """Generate a brief explanation of why the top posting scored highest."""
    reasons = []

    score = posting.get("score", 0)
    certs = posting.get("matched_certs", [])

    if certs:
        reasons.append(f"matches {len(certs)} of your certs ({', '.join(certs[:3])})")
    if posting.get("salary"):
        reasons.append(f"salary: {posting['salary']}")

    location = (posting.get("location") or "").lower()
    if "atlanta" in location:
        reasons.append("Atlanta-based")
    elif "remote" in location:
        reasons.append("remote-friendly")

    if not reasons:
        reasons.append(f"strong overall match (score {score})")

    return "; ".join(reasons)

"""CLI entry point for resume-tailor."""

import re
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .analyzer import analyze_match, analysis_to_dict, load_master_resume
from .generator import generate_tailored_resume, generate_cover_letter
from .researcher import generate_research_brief
from .scraper import scrape_job_posting, posting_to_dict

console = Console()

# Default paths relative to the package
PACKAGE_DIR = Path(__file__).parent.parent
DEFAULT_RESUME = PACKAGE_DIR / "data" / "master_resume.json"
DEFAULT_OUTPUT = PACKAGE_DIR / "output"


def _sanitize_filename(text: str) -> str:
    """Convert text to a safe filename component."""
    # Remove special characters, replace spaces with underscores
    sanitized = re.sub(r"[^\w\s-]", "", text.strip())
    sanitized = re.sub(r"[\s-]+", "_", sanitized)
    return sanitized.lower()[:50]


@click.command()
@click.option(
    "--url",
    required=True,
    help="URL of the job posting to tailor resume for.",
)
@click.option(
    "--resume",
    "resume_path",
    default=str(DEFAULT_RESUME),
    show_default=True,
    type=click.Path(exists=True),
    help="Path to master resume JSON file.",
)
@click.option(
    "--output",
    "output_dir",
    default=str(DEFAULT_OUTPUT),
    show_default=True,
    type=click.Path(),
    help="Directory to save generated files.",
)
def main(url: str, resume_path: str, output_dir: str) -> None:
    """Generate a tailored resume, cover letter, and research brief from a job posting URL."""
    console.print()
    console.print(
        Panel(
            "[bold]resume-tailor[/bold]\n"
            "Tailored resume, cover letter, and company research from any job posting.",
            border_style="blue",
        )
    )
    console.print()

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Scrape the job posting
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scraping job posting...", total=None)
        posting = scrape_job_posting(url)
        progress.update(task, completed=True)

    if not posting.is_valid():
        console.print("[red]Could not extract useful data from the job posting.[/red]")
        console.print("Check the URL and try again, or try a different link for the same posting.")
        sys.exit(1)

    # Display extracted info
    info_table = Table(title="Job Posting Data", show_header=False, border_style="dim")
    info_table.add_column("Field", style="bold cyan", width=20)
    info_table.add_column("Value")
    info_table.add_row("Title", posting.job_title or "[dim]Not found[/dim]")
    info_table.add_row("Company", posting.company_name or "[dim]Not found[/dim]")
    info_table.add_row("Location", posting.location or "[dim]Not found[/dim]")
    info_table.add_row("Remote", posting.remote_status or "[dim]Not specified[/dim]")
    info_table.add_row("Salary", posting.salary_range or "[dim]Not listed[/dim]")
    info_table.add_row("Experience", posting.years_experience or "[dim]Not specified[/dim]")
    info_table.add_row("Certs Required", ", ".join(posting.required_certs[:5]) or "[dim]None listed[/dim]")
    info_table.add_row("Skills Found", str(len(posting.required_skills)))
    info_table.add_row("Responsibilities", str(len(posting.key_responsibilities)))
    info_table.add_row("Description Length", f"{len(posting.description_text):,} chars")
    console.print(info_table)
    console.print()

    # Step 2: Load master resume and analyze match
    console.print("[bold]Analyzing match...[/bold]")
    resume = load_master_resume(resume_path)
    analysis = analyze_match(posting, resume)

    # Display analysis results
    score_color = "green" if analysis.relevance_score >= 70 else "yellow" if analysis.relevance_score >= 40 else "red"
    console.print(
        f"Relevance Score: [{score_color}][bold]{analysis.relevance_score}%[/bold][/{score_color}]"
    )
    console.print(f"Best Variant: [cyan]{analysis.best_variant}[/cyan]")
    console.print(f"Matching Certs: [green]{', '.join(analysis.matching_certs[:5]) or 'None'}[/green]")
    console.print(f"Matching Skills: [green]{len(analysis.matching_skills)}[/green]")
    if analysis.missing_skills:
        console.print(f"Missing Skills: [yellow]{', '.join(analysis.missing_skills[:5])}[/yellow]")
    if analysis.missing_certs:
        console.print(f"Missing Certs: [yellow]{', '.join(analysis.missing_certs[:5])}[/yellow]")
    console.print(f"Section Order: [dim]{' > '.join(analysis.section_order[:5])}[/dim]")
    console.print()

    # Build filenames
    company_slug = _sanitize_filename(posting.company_name or "company")
    role_slug = _sanitize_filename(posting.job_title or "role")
    base_name = f"{company_slug}_{role_slug}"

    resume_file = output_path / f"{base_name}_resume.md"
    cover_letter_file = output_path / f"{base_name}_cover_letter.md"
    research_file = output_path / f"{base_name}_research.md"

    # Step 3: Generate tailored resume
    console.print("[bold]Generating tailored resume...[/bold]")
    try:
        resume_md = generate_tailored_resume(posting, resume, analysis)
        resume_file.write_text(resume_md, encoding="utf-8")
        console.print(f"  [green]Saved:[/green] {resume_file}")
    except Exception as e:
        console.print(f"  [red]Error generating resume:[/red] {e}")
        resume_md = None

    # Step 4: Generate cover letter
    console.print("[bold]Generating cover letter...[/bold]")
    try:
        cover_letter_md = generate_cover_letter(posting, resume, analysis)
        cover_letter_file.write_text(cover_letter_md, encoding="utf-8")
        console.print(f"  [green]Saved:[/green] {cover_letter_file}")
    except Exception as e:
        console.print(f"  [red]Error generating cover letter:[/red] {e}")
        cover_letter_md = None

    # Step 5: Generate research brief
    console.print("[bold]Generating company research brief...[/bold]")
    try:
        research_md = generate_research_brief(posting, resume, analysis)
        research_file.write_text(research_md, encoding="utf-8")
        console.print(f"  [green]Saved:[/green] {research_file}")
    except Exception as e:
        console.print(f"  [red]Error generating research brief:[/red] {e}")
        research_md = None

    # Summary
    console.print()
    summary = Table(title="Output Summary", border_style="green")
    summary.add_column("File", style="bold")
    summary.add_column("Status")
    summary.add_column("Path")

    summary.add_row(
        "Resume",
        "[green]OK[/green]" if resume_md else "[red]FAILED[/red]",
        str(resume_file) if resume_md else "",
    )
    summary.add_row(
        "Cover Letter",
        "[green]OK[/green]" if cover_letter_md else "[red]FAILED[/red]",
        str(cover_letter_file) if cover_letter_md else "",
    )
    summary.add_row(
        "Research Brief",
        "[green]OK[/green]" if research_md else "[red]FAILED[/red]",
        str(research_file) if research_md else "",
    )
    console.print(summary)
    console.print()


if __name__ == "__main__":
    main()

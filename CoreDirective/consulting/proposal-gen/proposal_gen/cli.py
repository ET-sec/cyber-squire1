"""Click CLI for CoreDirective proposal generator."""

import os
import re
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import CONSULTANT, detect_service_type, get_phases, load_config
from .generator import generate_all_content
from .pdf_builder import build_proposal


console = Console()


def _sanitize_filename(name: str) -> str:
    """Turn a company name into a safe filename component."""
    clean = re.sub(r"[^\w\s-]", "", name.lower())
    clean = re.sub(r"[\s-]+", "_", clean).strip("_")
    return clean


@click.command()
@click.option(
    "--company",
    required=True,
    help="Client company name.",
)
@click.option(
    "--contact",
    default=None,
    help="Primary contact name at the client.",
)
@click.option(
    "--need",
    required=True,
    help="Description of what the client needs.",
)
@click.option(
    "--budget",
    default=None,
    help="Client budget range (e.g. '2000-3000').",
)
@click.option(
    "--theme",
    type=click.Choice(["light", "dark"], case_sensitive=False),
    default="light",
    help="PDF color theme. Default: light.",
)
@click.option(
    "--output",
    "output_path",
    default=None,
    help="Output PDF path. Default: ./output/{company}_proposal.pdf",
)
@click.option(
    "--config",
    "config_path",
    default=None,
    help="Path to config.yaml override.",
)
@click.option(
    "--no-ai",
    is_flag=True,
    default=False,
    help="Skip Claude API calls. Use template content only.",
)
def main(
    company: str,
    contact: str | None,
    need: str,
    budget: str | None,
    theme: str,
    output_path: str | None,
    config_path: str | None,
    no_ai: bool,
):
    """Generate a professional consulting proposal PDF.

    Uses Claude AI to create contextual content tailored to the client's
    specific needs, then renders it as a branded PDF.

    \b
    Examples:
      proposal-gen --company "Acme Corp" --need "SOC2 Type II compliance audit"
      proposal-gen --company "StartupXYZ" --need "Automate onboarding with n8n" --budget "2000-3000"
      proposal-gen --company "DefenseCo" --need "AWS cloud security assessment" --theme dark
    """
    # Load config
    _ = load_config(config_path)

    # Detect service type
    service_type = detect_service_type(need)

    # Resolve output path
    if output_path is None:
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_sanitize_filename(company)}_proposal.pdf"
        output_path = str(output_dir / filename)
    else:
        # Ensure parent directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Display header
    console.print()
    console.print(Panel(
        f"[bold white]CoreDirective Proposal Generator[/bold white]\n"
        f"[dim]Security & Automation Consulting[/dim]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()

    # Display parameters
    console.print(f"  [bold]Client:[/bold]       {company}")
    if contact:
        console.print(f"  [bold]Contact:[/bold]      {contact}")
    console.print(f"  [bold]Need:[/bold]         {need}")
    console.print(f"  [bold]Service Type:[/bold] {service_type.replace('_', ' ').title()}")
    if budget:
        console.print(f"  [bold]Budget:[/bold]       {budget}")
    console.print(f"  [bold]Theme:[/bold]        {theme}")
    console.print(f"  [bold]Output:[/bold]       {output_path}")
    console.print()

    # Check for API key if AI is enabled
    if not no_ai and not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[bold red]Error:[/bold red] ANTHROPIC_API_KEY environment variable is not set.\n"
            "  Export it: [dim]export ANTHROPIC_API_KEY=sk-ant-...[/dim]\n"
            "  Or use [dim]--no-ai[/dim] to generate with template content only.",
        )
        sys.exit(1)

    # Generate content
    content = {}
    phases = get_phases(service_type)

    if no_ai:
        console.print("  [yellow]Skipping AI content generation (--no-ai flag)[/yellow]")
        content = {
            "executive_summary": (
                f"{company} has identified the need for {need}. "
                f"CoreDirective will deliver a focused engagement to address this requirement "
                f"with clear milestones and measurable outcomes. "
                f"Our approach combines hands-on technical execution with documented processes "
                f"that your team can maintain after the engagement concludes."
            ),
            "phases": phases,
            "qualification_framing": (
                f"CoreDirective brings direct experience in {service_type.replace('_', ' ')} "
                f"engagements backed by industry certifications including "
                f"{', '.join(CONSULTANT['certifications'][:3])}. "
                f"This is not theoretical knowledge. Every credential maps to production work "
                f"performed on real infrastructure."
            ),
            "service_type": service_type,
        }
    else:
        with Progress(
            SpinnerColumn(style="green"),
            TextColumn("[bold]{task.description}[/bold]"),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task("Generating executive summary...", total=3)

            try:
                content = generate_all_content(
                    company=company,
                    need=need,
                    contact=contact,
                    service_type=service_type,
                )
                progress.update(task, advance=3, description="Content generation complete")
            except Exception as e:
                progress.stop()
                console.print(f"\n  [bold red]API Error:[/bold red] {e}")
                console.print("  Falling back to template content.\n")
                content = {
                    "executive_summary": (
                        f"{company} has identified the need for {need}. "
                        f"CoreDirective will deliver a focused engagement to address this requirement."
                    ),
                    "phases": phases,
                    "qualification_framing": "",
                    "service_type": service_type,
                }

    # Ensure phases are present
    if "phases" not in content or not content["phases"]:
        content["phases"] = phases

    console.print()

    # Build PDF
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[bold]{task.description}[/bold]"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Building PDF...", total=1)

        try:
            result_path = build_proposal(
                output_path=output_path,
                theme=theme,
                company=company,
                contact=contact,
                need=need,
                budget=budget,
                content=content,
                service_type=service_type,
            )
            progress.update(task, advance=1, description="PDF built successfully")
        except Exception as e:
            progress.stop()
            console.print(f"\n  [bold red]PDF Error:[/bold red] {e}")
            sys.exit(1)

    console.print()
    console.print(Panel(
        f"[bold green]Proposal saved to:[/bold green]\n{result_path}",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()


if __name__ == "__main__":
    main()

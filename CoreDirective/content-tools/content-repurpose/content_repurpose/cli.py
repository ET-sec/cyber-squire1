"""Click CLI entry point for content-repurpose."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from content_repurpose.config import Config
from content_repurpose.generator import generate_all
from content_repurpose.parser import parse_input


console = Console()


@click.command(
    help="Repurpose long-form content into platform-optimized posts for TikTok, LinkedIn, X/Twitter, Reddit, YouTube, and YouTube Shorts.",
)
@click.option(
    "--script",
    type=click.Path(exists=True),
    default=None,
    help="Path to a YouTube script markdown file.",
)
@click.option(
    "--transcript",
    type=click.Path(exists=True),
    default=None,
    help="Path to a transcript text file.",
)
@click.option(
    "--text",
    type=click.Path(exists=True),
    default=None,
    help="Path to any long-form text file.",
)
@click.option(
    "--topic",
    type=str,
    default=None,
    help="Generate content from a topic string.",
)
@click.option(
    "--brand",
    type=str,
    default=None,
    help="Brand name (default: from config.yaml or 'CoreDirective').",
)
@click.option(
    "--cta",
    type=str,
    default=None,
    help="Call to action text (default: from config.yaml).",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output directory (default: ./output/).",
)
@click.option(
    "--tone",
    type=str,
    default=None,
    help="Writing tone (default: from config.yaml).",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to config.yaml file.",
)
def main(
    script: str | None,
    transcript: str | None,
    text: str | None,
    topic: str | None,
    brand: str | None,
    cta: str | None,
    output: str | None,
    tone: str | None,
    config_path: str | None,
) -> None:
    """Main CLI entry point."""
    # Load config
    config = Config.load(config_path)

    # CLI flags override config file values
    if brand is not None:
        config.brand = brand
    if cta is not None:
        config.cta = cta
    if tone is not None:
        config.tone = tone
    if output is not None:
        config.output_dir = output

    # Parse input first (fast validation before API key check)
    try:
        parsed = parse_input(
            script=script,
            transcript=transcript,
            text=text,
            topic=topic,
        )
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    # Validate API key
    try:
        config.get_api_key()
    except EnvironmentError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    output_dir = Path(config.output_dir).resolve()

    # Generate all content
    try:
        results = generate_all(parsed, config, output_dir)
    except Exception as e:
        console.print(f"\n[bold red]Generation failed:[/bold red] {e}")
        sys.exit(1)

    # Display results
    if results:
        console.print()
        table = Table(title="Generated Content", border_style="green")
        table.add_column("Platform", style="bold cyan")
        table.add_column("Output File", style="white")

        for platform_name, file_path in results.items():
            table.add_row(platform_name, str(file_path))

        console.print(table)
        console.print()
        console.print(
            Panel(
                f"[bold green]{len(results)} files generated[/bold green] in [cyan]{output_dir}[/cyan]",
                border_style="green",
            )
        )
    else:
        console.print("\n[yellow]No content was generated.[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()

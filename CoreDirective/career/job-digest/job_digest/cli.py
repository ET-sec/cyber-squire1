"""Click CLI for the job-digest tool."""

import logging
import os
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from job_digest import __version__
from job_digest.database import (
    get_connection,
    insert_postings_batch,
    get_todays_postings,
    get_all_postings,
    mark_applied,
    get_application_tracker,
    get_stats,
)
from job_digest.formatter import format_digest, format_history, format_tracker
from job_digest.notifier import notify
from job_digest.scraper import scrape_all

console = Console()

# Default config file location
DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")


def _load_config(config_path: str) -> dict:
    """Load and validate the config file."""
    path = Path(config_path)
    if not path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        console.print(f"Expected at: {DEFAULT_CONFIG}")
        sys.exit(1)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    if not config:
        console.print("[red]Config file is empty[/red]")
        sys.exit(1)

    return config


def _setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quiet down noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


@click.group(invoke_without_command=True)
@click.option("--send", is_flag=True, help="Send digest to webhook after printing")
@click.option("--webhook", type=str, default=None, help="Override webhook URL")
@click.option("--config", "config_path", type=str, default=DEFAULT_CONFIG, help="Path to config.yaml")
@click.option("--fresh", is_flag=True, help="Force re-scrape (ignore today's cache)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx, send, webhook, config_path, fresh, verbose, version):
    """Cybersecurity job posting scraper and digest generator.

    Run without subcommands to scrape, score, and display today's digest.
    """
    if version:
        console.print(f"job-digest v{__version__}")
        return

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["verbose"] = verbose

    _setup_logging(verbose)

    # If no subcommand is given, run the default digest flow
    if ctx.invoked_subcommand is None:
        _run_digest(config_path, send, webhook, fresh, verbose)


@main.command()
@click.option("--limit", type=int, default=100, help="Maximum postings to show")
@click.pass_context
def history(ctx, limit):
    """Show all past postings from the database."""
    _setup_logging(ctx.obj.get("verbose", False))
    conn = get_connection()
    postings = get_all_postings(conn, limit=limit)
    conn.close()

    if postings:
        output = format_history(postings)
        console.print(output)

        # Also show stats
        conn = get_connection()
        stats = get_stats(conn)
        conn.close()
        console.print(f"\n[dim]Stats: {stats['total_postings']} total, "
                       f"{stats['applied']} applied, "
                       f"avg score {stats['average_score']}[/dim]")
    else:
        console.print("[yellow]No postings in database yet. Run a scrape first.[/yellow]")


@main.command()
@click.argument("posting_id", type=int)
@click.pass_context
def applied(ctx, posting_id):
    """Mark a posting as applied by its database ID."""
    _setup_logging(ctx.obj.get("verbose", False))
    conn = get_connection()
    success = mark_applied(conn, posting_id)
    conn.close()

    if success:
        console.print(f"[green]Posting #{posting_id} marked as applied.[/green]")
    else:
        console.print(f"[red]Posting #{posting_id} not found.[/red]")


@main.command()
@click.pass_context
def tracker(ctx):
    """Show application tracking dashboard."""
    _setup_logging(ctx.obj.get("verbose", False))
    conn = get_connection()
    postings = get_application_tracker(conn)
    stats = get_stats(conn)
    conn.close()

    output = format_tracker(postings)
    console.print(output)

    if stats["applied"] > 0:
        console.print(f"\n[dim]Application rate: {stats['applied']}/{stats['total_postings']} "
                       f"({100 * stats['applied'] / max(1, stats['total_postings']):.1f}%)[/dim]")


@main.command()
@click.pass_context
def stats(ctx):
    """Show database statistics."""
    _setup_logging(ctx.obj.get("verbose", False))
    conn = get_connection()
    s = get_stats(conn)
    conn.close()

    table = Table(title="Job Digest Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Postings", str(s["total_postings"]))
    table.add_row("Found Today", str(s["found_today"]))
    table.add_row("Applications Sent", str(s["applied"]))
    table.add_row("Average Score", str(s["average_score"]))

    console.print(table)


def _run_digest(config_path: str, send: bool, webhook: str, fresh: bool, verbose: bool):
    """Main digest workflow: scrape -> score -> dedup -> format -> notify."""
    config = _load_config(config_path)
    logger = logging.getLogger(__name__)

    console.print(Panel.fit(
        f"[bold]Job Digest v{__version__}[/bold]\n"
        f"Scraping {len(config.get('search_terms', []))} search terms "
        f"across {len(config.get('locations', []))} locations...",
        title="Starting",
    ))

    # Step 1: Scrape all sources
    try:
        scored_postings, total_scraped = scrape_all(config)
    except Exception as e:
        console.print(f"[red]Scraping failed: {e}[/red]")
        logger.exception("Scraping failed")
        sys.exit(1)

    console.print(f"Scraped {total_scraped} total postings, {len(scored_postings)} scored above threshold")

    # Step 2: Dedup against database
    conn = get_connection()

    if fresh:
        # In fresh mode, we still insert but don't filter out existing ones from display
        console.print("[yellow]Fresh mode: all scored postings will be shown[/yellow]")
        new_postings = insert_postings_batch(conn, scored_postings)
        display_postings = scored_postings  # Show all, even if some were already in DB
    else:
        new_postings = insert_postings_batch(conn, scored_postings)
        display_postings = new_postings

    conn.close()

    console.print(f"New postings (not previously seen): {len(new_postings)}")

    # Step 3: Format digest
    digest_text = format_digest(display_postings, total_scraped, config)

    # Step 4: Determine webhook URL
    webhook_url = webhook or config.get("webhook_url", "")

    # Step 5: Notify
    notify(digest_text, display_postings, send=send, webhook_url=webhook_url)

"""Claude API orchestrator. Coordinates all platform generators."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID

from content_repurpose.config import Config
from content_repurpose.parser import ParsedInput
from content_repurpose.platforms.tiktok import generate_tiktok
from content_repurpose.platforms.linkedin import generate_linkedin
from content_repurpose.platforms.twitter import generate_twitter
from content_repurpose.platforms.reddit import generate_reddit
from content_repurpose.platforms.youtube import generate_youtube
from content_repurpose.platforms.shorts import generate_shorts


console = Console()

# Platform registry: (key, display_name, generator_function)
PLATFORM_REGISTRY: list[tuple[str, str, Callable]] = [
    ("tiktok", "TikTok Scripts", generate_tiktok),
    ("linkedin", "LinkedIn Post", generate_linkedin),
    ("twitter", "X/Twitter Thread", generate_twitter),
    ("reddit", "Reddit Post", generate_reddit),
    ("youtube", "YouTube Metadata", generate_youtube),
    ("shorts", "YouTube Shorts", generate_shorts),
]


def run_extraction(client: Anthropic, parsed: ParsedInput, config: Config) -> str:
    """Extract core message, key points, data points, and angles from the input content.

    For topic-based input, this generates foundational content first.
    For file-based input, this distills the source material into structured talking points.
    """
    if parsed.input_type == "topic":
        extraction_prompt = f"""You are a content strategist for the brand "{config.brand}".
Tone: {config.tone}

TOPIC: {parsed.content}

Generate the foundational content for this topic. Write 400-600 words covering:

1. **Core Message**: The single most important takeaway (1-2 sentences).
2. **Key Points**: 4-6 specific, actionable points about this topic.
3. **Data Points**: 2-3 specific statistics, facts, or concrete examples that support the key points. Use real data where possible.
4. **Angles**: 3 different angles to approach this topic (controversial, educational, personal).
5. **Target Audience**: Who needs to hear this and why they care right now.

Write with authority. Be specific. No generic filler. Include real numbers and examples where relevant."""
    else:
        extraction_prompt = f"""You are a content strategist for the brand "{config.brand}".
Tone: {config.tone}

SOURCE {parsed.summary_label.upper()}:
{parsed.content}

Analyze this content and extract:

1. **Core Message**: The single most important takeaway (1-2 sentences).
2. **Key Points**: The 4-6 most important specific points made.
3. **Data Points**: Any statistics, facts, numbers, or concrete examples mentioned.
4. **Angles**: 3 different angles this content could be repurposed from (controversial, educational, personal).
5. **Quotable Lines**: 2-3 lines from the source that are particularly strong or memorable.
6. **Target Audience**: Who this content is for and what problem it solves for them.

Be specific. Pull exact details from the source. No paraphrasing into generic advice."""

    message = client.messages.create(
        model=config.model,
        max_tokens=1500,
        messages=[{"role": "user", "content": extraction_prompt}],
    )

    return message.content[0].text


def generate_all(
    parsed: ParsedInput,
    config: Config,
    output_dir: Path,
) -> dict[str, Path]:
    """Orchestrate content generation across all enabled platforms.

    Returns a dict mapping platform name to output file path.
    """
    api_key = config.get_api_key()
    client = Anthropic(api_key=api_key)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine which platforms to generate
    enabled = [
        (key, name, fn)
        for key, name, fn in PLATFORM_REGISTRY
        if config.platforms.get(key, True)
    ]

    total_steps = len(enabled) + 1  # +1 for extraction step

    console.print()
    console.print(
        Panel(
            f"[bold]{parsed.summary_label}[/bold]: "
            f"{parsed.content[:80]}{'...' if len(parsed.content) > 80 else ''}\n"
            f"[dim]Brand: {config.brand} | Tone: {config.tone}[/dim]\n"
            f"[dim]Model: {config.model}[/dim]\n"
            f"[dim]Platforms: {', '.join(name for _, name, _ in enabled)}[/dim]",
            title="[bold green]Content Repurpose[/bold green]",
            border_style="green",
        )
    )
    console.print()

    results: dict[str, Path] = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        main_task = progress.add_task("Generating content...", total=total_steps)

        # Step 1: Extract core content
        progress.update(main_task, description="Extracting core content...")
        extracted = run_extraction(client, parsed, config)
        progress.advance(main_task)

        # Build enriched content (original + extraction)
        if parsed.input_type == "topic":
            enriched_content = extracted
        else:
            enriched_content = (
                f"ORIGINAL CONTENT:\n{parsed.content}\n\n"
                f"CONTENT ANALYSIS:\n{extracted}"
            )

        # Create enriched ParsedInput for platform generators
        enriched_parsed = ParsedInput(
            input_type=parsed.input_type,
            content=enriched_content,
            source=parsed.source,
            word_count=len(enriched_content.split()),
        )

        # Step 2: Generate for each platform
        for key, name, generator_fn in enabled:
            progress.update(main_task, description=f"Generating {name}...")
            try:
                output_path = generator_fn(client, enriched_parsed, config, output_dir)
                results[name] = output_path
            except Exception as e:
                console.print(f"  [red]Error generating {name}: {e}[/red]")
            progress.advance(main_task)

    return results

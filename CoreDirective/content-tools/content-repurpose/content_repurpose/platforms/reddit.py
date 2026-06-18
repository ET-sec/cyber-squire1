"""Reddit content generator."""

from __future__ import annotations

from pathlib import Path

from anthropic import Anthropic

from content_repurpose.config import Config
from content_repurpose.parser import ParsedInput
from content_repurpose.prompts.reddit_prompt import get_reddit_prompt


def generate_reddit(
    client: Anthropic,
    parsed: ParsedInput,
    config: Config,
    output_dir: Path,
) -> Path:
    """Generate a Reddit post with suggested subreddits and save to file."""
    prompt = get_reddit_prompt(
        content=parsed.content,
        brand=config.brand,
        cta=config.cta,
        tone=config.tone,
        subreddits=config.reddit_subreddits,
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    output_path = output_dir / "reddit_post.md"
    output_path.write_text(message.content[0].text, encoding="utf-8")
    return output_path

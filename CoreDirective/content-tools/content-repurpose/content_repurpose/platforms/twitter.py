"""X/Twitter thread content generator."""

from __future__ import annotations

from pathlib import Path

from anthropic import Anthropic

from content_repurpose.config import Config
from content_repurpose.parser import ParsedInput
from content_repurpose.prompts.twitter_prompt import get_twitter_prompt


def generate_twitter(
    client: Anthropic,
    parsed: ParsedInput,
    config: Config,
    output_dir: Path,
) -> Path:
    """Generate a 7-tweet X/Twitter thread and save to file."""
    prompt = get_twitter_prompt(
        content=parsed.content,
        brand=config.brand,
        cta=config.cta,
        tone=config.tone,
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    output_path = output_dir / "twitter_thread.md"
    output_path.write_text(message.content[0].text, encoding="utf-8")
    return output_path

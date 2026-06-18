"""TikTok content generator."""

from __future__ import annotations

from pathlib import Path

from anthropic import Anthropic

from content_repurpose.config import Config
from content_repurpose.parser import ParsedInput
from content_repurpose.prompts.tiktok_prompt import get_tiktok_prompt


def generate_tiktok(
    client: Anthropic,
    parsed: ParsedInput,
    config: Config,
    output_dir: Path,
) -> Path:
    """Generate 3 TikTok script variations and save to file."""
    prompt = get_tiktok_prompt(
        content=parsed.content,
        brand=config.brand,
        cta=config.cta,
        tone=config.tone,
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    output_path = output_dir / "tiktok_scripts.md"
    output_path.write_text(message.content[0].text, encoding="utf-8")
    return output_path

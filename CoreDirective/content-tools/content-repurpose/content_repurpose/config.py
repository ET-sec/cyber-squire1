"""Configuration loader and brand defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ANTI_SLOP_RULES = """
ABSOLUTE RULES FOR ALL OUTPUT:
NEVER use these words or phrases: leverage, delve, comprehensive, robust, streamline,
cutting-edge, game-changer, seamless, elevate, foster, harness, no fluff, deep dive,
unpack, unlock, navigate, landscape, ecosystem, paradigm, holistic, innovative,
transformative.
NEVER write: "Great question!", "Absolutely!", "In conclusion", "It's worth noting".
NEVER use hyphens or dashes as punctuation (no em dashes, no en dashes).
Keep sentences short. Vary sentence length. Be specific. Cut filler words.
Match the native tone of each platform. Write like a real person, not a content mill.
""".strip()

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_BRAND = "CoreDirective"
DEFAULT_CTA = "Follow for more cybersecurity content"
DEFAULT_TONE = "direct, confident, slightly irreverent, no corporate speak"
DEFAULT_OUTPUT = "./output"

REDDIT_SUBREDDITS = [
    "r/cybersecurity",
    "r/CompTIA",
    "r/ccna",
    "r/ITCareerQuestions",
    "r/netsec",
    "r/learnprogramming",
    "r/careerguidance",
]


@dataclass
class Config:
    brand: str = DEFAULT_BRAND
    cta: str = DEFAULT_CTA
    tone: str = DEFAULT_TONE
    model: str = DEFAULT_MODEL
    output_dir: str = DEFAULT_OUTPUT
    reddit_subreddits: list[str] = field(default_factory=lambda: list(REDDIT_SUBREDDITS))
    brand_keywords: list[str] = field(default_factory=list)
    platforms: dict[str, bool] = field(default_factory=lambda: {
        "tiktok": True,
        "linkedin": True,
        "twitter": True,
        "reddit": True,
        "youtube": True,
        "shorts": True,
    })

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> Config:
        """Load config from YAML file, falling back to defaults."""
        data: dict[str, Any] = {}

        if config_path is None:
            candidates = [
                Path.cwd() / "config.yaml",
                Path(__file__).parent.parent / "config.yaml",
            ]
            for candidate in candidates:
                if candidate.is_file():
                    config_path = candidate
                    break

        if config_path and Path(config_path).is_file():
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}

        return cls(
            brand=data.get("brand", DEFAULT_BRAND),
            cta=data.get("cta", DEFAULT_CTA),
            tone=data.get("tone", DEFAULT_TONE),
            model=data.get("model", DEFAULT_MODEL),
            output_dir=data.get("output_dir", DEFAULT_OUTPUT),
            reddit_subreddits=data.get("reddit_subreddits", list(REDDIT_SUBREDDITS)),
            brand_keywords=data.get("brand_keywords", []),
            platforms=data.get("platforms", {
                "tiktok": True,
                "linkedin": True,
                "twitter": True,
                "reddit": True,
                "youtube": True,
                "shorts": True,
            }),
        )

    def get_api_key(self) -> str:
        """Get Anthropic API key from environment."""
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Export it before running: export ANTHROPIC_API_KEY=sk-ant-..."
            )
        return key

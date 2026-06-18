"""Input parsing for scripts, transcripts, text files, and topics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


InputType = Literal["script", "transcript", "text", "topic"]


@dataclass
class ParsedInput:
    """Parsed content ready for generation."""

    input_type: InputType
    content: str
    source: str  # file path or "topic"
    word_count: int

    @property
    def is_from_file(self) -> bool:
        return self.input_type != "topic"

    @property
    def summary_label(self) -> str:
        labels = {
            "script": "YouTube Script",
            "transcript": "Transcript",
            "text": "Long-form Text",
            "topic": "Topic",
        }
        return labels[self.input_type]


def parse_file(path: str | Path, input_type: InputType) -> ParsedInput:
    """Read and parse a file into a ParsedInput."""
    filepath = Path(path)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not filepath.is_file():
        raise ValueError(f"Path is not a file: {filepath}")

    content = filepath.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError(f"File is empty: {filepath}")

    word_count = len(content.split())

    return ParsedInput(
        input_type=input_type,
        content=content,
        source=str(filepath.resolve()),
        word_count=word_count,
    )


def parse_topic(topic: str) -> ParsedInput:
    """Create a ParsedInput from a topic string."""
    topic = topic.strip()

    if not topic:
        raise ValueError("Topic cannot be empty")

    return ParsedInput(
        input_type="topic",
        content=topic,
        source="topic",
        word_count=len(topic.split()),
    )


def parse_input(
    script: str | None = None,
    transcript: str | None = None,
    text: str | None = None,
    topic: str | None = None,
) -> ParsedInput:
    """Parse whichever input was provided. Exactly one must be set."""
    inputs = {
        "script": script,
        "transcript": transcript,
        "text": text,
        "topic": topic,
    }

    provided = {k: v for k, v in inputs.items() if v is not None}

    if len(provided) == 0:
        raise ValueError(
            "No input provided. Use --script, --transcript, --text, or --topic."
        )

    if len(provided) > 1:
        raise ValueError(
            f"Multiple inputs provided ({', '.join(provided.keys())}). "
            "Pick one: --script, --transcript, --text, or --topic."
        )

    input_type, value = next(iter(provided.items()))

    if input_type == "topic":
        return parse_topic(value)
    else:
        return parse_file(value, input_type)

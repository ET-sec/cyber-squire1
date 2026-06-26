"""GRC PR reviewer agent.

Reads a unified diff (either via `gh pr diff <pr_number>` or from a local
file via `--diff-file`), calls Claude Sonnet 4.6 (escalating to Opus 4.8
on large diffs) with a cached system prompt sourced from
`scripts/grc/grc_reference.md` plus the corpus index from
`docs/grc/README.md`, parses structured JSON, sanitizes output, and
posts a structured PR comment via `gh pr comment`.

Defensive primitives owned by this script:
  * Daily Anthropic budget guard subprocess (first call)
  * Oversized diff guard (100KB) - skips LLM call entirely
  * Mixed-PR detection (warns; does not block)
  * Model escalation (Sonnet -> Opus on >50KB or >5 files)
  * Spend ledger record per call
  * sanitize_output.sanitize() final pass before any PR comment

Exit code: 0 on success. 1 only when the parsed review's
`residual_risk_required` is True (merge gate). All other failure modes
(API timeout, parse error) bubble up via raised exceptions.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

import anthropic

# Make repo-relative imports work when invoked as a script.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import sanitize_output  # noqa: E402
from scripts.grc.spend_ledger import record_call  # noqa: E402

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("grc_reviewer")

# Module-level cached system prompt content. Loaded lazily so tests can
# monkeypatch the read paths without filesystem coupling at import time.
_GRC_REFERENCE: Optional[str] = None
_CORPUS_INDEX: Optional[str] = None
_SYSTEM_PROMPT: Optional[str] = None

DEFAULT_MODEL = "claude-sonnet-4-6"
ESCALATION_MODEL = "claude-opus-4-8"
DIFF_HARD_SKIP_BYTES = 100_000
DIFF_ESCALATE_BYTES = 50_000
ESCALATE_FILES = 5
API_TIMEOUT_SECONDS = 60  # SDK client.messages.create(timeout=60) hard ceiling
MAX_OUTPUT_TOKENS = 4096


def _load_system_prompt() -> str:
    """Load and cache the system prompt from disk (idempotent)."""
    global _GRC_REFERENCE, _CORPUS_INDEX, _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is not None:
        return _SYSTEM_PROMPT
    _GRC_REFERENCE = (REPO_ROOT / "scripts" / "grc" / "grc_reference.md").read_text()
    _CORPUS_INDEX = (REPO_ROOT / "docs" / "grc" / "README.md").read_text()
    _SYSTEM_PROMPT = f"{_GRC_REFERENCE}\n\n## Corpus Index\n{_CORPUS_INDEX}"
    return _SYSTEM_PROMPT


def _count_changed_files(diff: str) -> int:
    return sum(1 for line in diff.splitlines() if line.startswith("+++ b/"))


def _has_non_grc_changes(diff: str) -> bool:
    """Return True if any +++ b/ path is outside docs/grc/."""
    pattern = re.compile(r"^\+\+\+ b/(?!docs/grc/)", re.MULTILINE)
    return bool(pattern.search(diff))


def _select_model(diff: str) -> str:
    if len(diff) > DIFF_ESCALATE_BYTES or _count_changed_files(diff) > ESCALATE_FILES:
        log.info(
            "Escalating to %s (diff_bytes=%d, files=%d)",
            ESCALATION_MODEL,
            len(diff),
            _count_changed_files(diff),
        )
        return ESCALATION_MODEL
    return DEFAULT_MODEL


def _strip_json_fences(text: str) -> str:
    """Remove leading ```json / trailing ``` if model wrapped JSON in fences."""
    text = text.strip()
    if text.startswith("```"):
        # Drop the first fence line
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1:]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()


def _parse_review(raw: str) -> dict:
    cleaned = _strip_json_fences(raw)
    return json.loads(cleaned)


def _budget_guard() -> None:
    """Run the budget guard subprocess. Raises CalledProcessError on block."""
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "grc" / "budget_guard.py")],
        check=True,
    )


def review_pr(
    pr_number: Optional[int] = None,
    dry_run: bool = False,
    diff_file: Optional[str] = None,
) -> dict:
    """Run a GRC review against a PR diff. Returns the parsed review dict."""
    if (pr_number is None) == (diff_file is None):
        raise ValueError(
            "Provide exactly one of `pr_number` or `diff_file`, not both/neither."
        )

    # Step 1: budget guard (always first; before any LLM cost).
    _budget_guard()

    # Step 2: resolve diff source.
    if diff_file is not None:
        diff = Path(diff_file).read_text()
        log.info("Loaded diff from file: %s (%d bytes)", diff_file, len(diff))
    else:
        diff = subprocess.check_output(
            ["gh", "pr", "diff", str(pr_number)], text=True
        )

    # Step 3: oversized diff guard (skip LLM call, cap cost).
    if len(diff) > DIFF_HARD_SKIP_BYTES:
        log.warning(
            "Oversized diff (%d bytes > %d), skipping LLM call",
            len(diff),
            DIFF_HARD_SKIP_BYTES,
        )
        return {
            "oversized": True,
            "controls_touched": [],
            "poam_deltas": [],
            "reviewer_questions": [
                "PR diff exceeds 100KB - manual review required"
            ],
            "residual_risk_required": False,
            "sanitization_violations": [],
        }

    # Step 4: mixed-PR detection (warn only).
    if _has_non_grc_changes(diff):
        log.warning("Mixed PR detected; PR-Agent will also comment")

    # Step 5: model selection.
    model = _select_model(diff)

    # Step 6: API call.
    client = anthropic.Anthropic()
    system_prompt = _load_system_prompt()
    response = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        timeout=API_TIMEOUT_SECONDS,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    "Review this GRC pull request diff. Respond with JSON "
                    "matching the schema in the system prompt. No prose "
                    "outside JSON.\n\n"
                    f"<diff>\n{diff}\n</diff>"
                ),
            }
        ],
    )

    # Step 7: record spend (works whether usage is dict or pydantic model).
    usage = getattr(response, "usage", None)
    usage_dict: dict[str, int] = {}
    if usage is not None:
        for k in (
            "input_tokens",
            "output_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
        ):
            v = getattr(usage, k, None)
            if v is None and isinstance(usage, dict):
                v = usage.get(k, 0)
            usage_dict[k] = int(v or 0)
    try:
        cost = record_call(model, usage_dict)
        log.info("Spend recorded: $%.6f (model=%s)", cost, model)
    except Exception as e:  # pragma: no cover - non-fatal observability
        log.warning("Failed to record spend (%s): %s", e.__class__.__name__, e)

    # Step 8: cache observability to stderr.
    log.info(
        "cache_creation_input_tokens=%d cache_read_input_tokens=%d",
        usage_dict.get("cache_creation_input_tokens", 0),
        usage_dict.get("cache_read_input_tokens", 0),
    )

    # Step 9: parse response.
    raw_text = ""
    content = getattr(response, "content", None) or []
    if content and hasattr(content[0], "text"):
        raw_text = content[0].text
    elif content and isinstance(content[0], dict):
        raw_text = content[0].get("text", "")
    review = _parse_review(raw_text)
    return review


def format_review_comment(review: dict) -> str:
    """Render a structured markdown comment. No raw diff, no file quotes."""
    if review.get("oversized"):
        return (
            "## GRC Reviewer\n\n"
            "**Status:** Oversized diff (>100KB). Manual review required.\n"
        )

    lines: list[str] = ["## GRC Reviewer", ""]

    controls = review.get("controls_touched") or []
    lines.append("### Controls touched")
    if controls:
        for c in controls:
            lines.append(f"- {c}")
    else:
        lines.append("- None")
    lines.append("")

    poams = review.get("poam_deltas") or []
    lines.append("### POA&M deltas")
    if poams:
        for p in poams:
            lines.append(f"- {p}")
    else:
        lines.append("- None")
    lines.append("")

    questions = review.get("reviewer_questions") or []
    lines.append("### Reviewer questions")
    if questions:
        for q in questions:
            lines.append(f"- {q}")
    else:
        lines.append("- None")
    lines.append("")

    violations = review.get("sanitization_violations") or []
    if violations:
        lines.append("### Sanitization violations")
        for v in violations:
            lines.append(f"- {v}")
        lines.append("")

    rr_required = bool(review.get("residual_risk_required"))
    gate_status = "BLOCKED (residual risk fields missing)" if rr_required else "OK"
    lines.append(f"### Merge gate: {gate_status}")
    lines.append("")
    return "\n".join(lines)


def post_comment(pr_number: int, review: dict, dry_run: bool = False) -> None:
    body = format_review_comment(review)
    # Defense in depth: sanitize before posting.
    body = sanitize_output.sanitize(body)
    if dry_run or pr_number == 0:
        print(body)
        return
    subprocess.run(
        ["gh", "pr", "comment", str(pr_number), "--body", body], check=True
    )


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="GRC PR reviewer")
    p.add_argument(
        "pr_number",
        nargs="?",
        type=int,
        default=None,
        help="PR number (live PR review mode)",
    )
    p.add_argument(
        "--diff-file",
        dest="diff_file",
        default=None,
        help="Path to a unified diff file (offline mode)",
    )
    p.add_argument(
        "--offline",
        action="store_true",
        help="Skip 'gh pr comment'; print comment body to stdout",
    )
    args = p.parse_args(argv)

    # Enforce exactly one of pr_number / diff_file at the CLI layer.
    if (args.pr_number is None) == (args.diff_file is None):
        p.error("Provide exactly one of <pr_number> or --diff-file")

    dry_run = args.offline or os.environ.get("INPUT_DRY_RUN") == "true"
    review = review_pr(
        pr_number=args.pr_number,
        dry_run=dry_run,
        diff_file=args.diff_file,
    )
    post_comment(args.pr_number or 0, review, dry_run=dry_run)
    if review.get("residual_risk_required"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

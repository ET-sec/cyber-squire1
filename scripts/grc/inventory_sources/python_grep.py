"""Python regex grep source plugin (RESEARCH D11 source f).

Walks ``Agent_Squire/`` + ``builds/squire/`` for LLM constructor calls and
emits a finding per (agent_id, source) pair. This catches Python agents
created via direct SDK instantiation that container labels miss.

Patterns covered (module-level ``LLM_CONSTRUCTOR_PATTERNS``):

* ``anthropic.Anthropic(``
* ``ChatAnthropic(``
* ``litellm.completion``
* ``openai.OpenAI(``
* ``ChatOpenAI(``
* ``Ollama(``
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, List

DEFAULT_SCAN_ROOTS = ("Agent_Squire", "builds/squire")

LLM_CONSTRUCTOR_PATTERNS = [
    re.compile(r"\banthropic\.Anthropic\("),
    re.compile(r"\bChatAnthropic\("),
    re.compile(r"\blitellm\.completion\b"),
    re.compile(r"\bopenai\.OpenAI\("),
    re.compile(r"\bChatOpenAI\("),
    re.compile(r"\bOllama\("),
]

# Substrings; any path containing one of these segments is skipped.
IGNORED_DIR_PARTS = {
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "site-packages",
    ".egg-info",
    "tests",
}


def _snake(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return cleaned or "unknown_agent"


def _derive_agent_id(rel_parts: tuple[str, ...]) -> str:
    """Resolve an agent_id from the file's path components.

    Heuristics:

    * ``Agent_Squire/agents/<agent_dir>/...`` -> ``<agent_dir>``
    * ``builds/squire/src/squire/...``        -> ``squire``
    * ``builds/squire/src/<other>/...``       -> ``<other>``
    * fallback                                -> immediate parent dir
    """
    parts = list(rel_parts)
    if len(parts) >= 3 and parts[0] == "Agent_Squire" and parts[1] == "agents":
        return _snake(parts[2])
    if len(parts) >= 4 and parts[0] == "builds" and parts[1] == "squire" and parts[2] == "src":
        return _snake(parts[3])
    if len(parts) >= 2:
        return _snake(parts[-2])
    return _snake(parts[-1])


def _should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIR_PARTS for part in path.parts)


def _iter_py_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if path.is_file() and not _should_skip(path):
                yield path


def _read_safely(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        print(
            f"inventory_sources.python_grep: cannot read {path}: {exc}",
            file=sys.stderr,
        )
        return None


def discover(scan_roots: Iterable[str | Path] | None = None) -> List[dict]:
    """Return one finding per (agent_id, first_match_evidence)."""
    if scan_roots is None:
        roots = [Path(r) for r in DEFAULT_SCAN_ROOTS]
    else:
        roots = [Path(r) for r in scan_roots]

    findings: List[dict] = []
    seen: set[str] = set()  # dedupe by agent_id (one finding per agent)
    for path in _iter_py_files(roots):
        text = _read_safely(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            matched_pattern = next(
                (p for p in LLM_CONSTRUCTOR_PATTERNS if p.search(line)), None
            )
            if matched_pattern is None:
                continue
            try:
                rel_parts = path.relative_to(Path.cwd()).parts
            except ValueError:
                rel_parts = path.parts
            agent_id = _derive_agent_id(rel_parts)
            if agent_id in seen:
                continue
            seen.add(agent_id)
            findings.append(
                {
                    "agent_id": agent_id,
                    "source": "python_grep",
                    "evidence": (
                        f"Python LLM constructor in {Path(*rel_parts).as_posix()}"
                        f":{lineno} matching {matched_pattern.pattern}"
                    ),
                }
            )
            break  # one match per file is enough; agent dedupe handles rest
    return findings

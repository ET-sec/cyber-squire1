"""MCP server source plugin.

Walks the repo for FastMCP server registrations. The canonical file is
``scripts/grc/grc_mcp_server.py`` (RESEARCH Topic 1 confirmed the filename).

Glob covers three patterns so future agent MCP servers under
``Agent_Squire/agents/<agent>/mcp_server/server.py`` are also discovered:

* ``**/grc_mcp_server.py``
* ``**/mcp_server.py``
* ``Agent_Squire/agents/*/mcp_server/server.py``
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

# Absolute glob patterns relative to repo root.
MCP_FILE_GLOBS = (
    "**/grc_mcp_server.py",
    "**/mcp_server.py",
    "Agent_Squire/agents/*/mcp_server/server.py",
)

# File path (POSIX, relative to repo root) -> registered agent_id.
# Match against the suffix so absolute paths still resolve cleanly.
PATH_AGENT_MAP = {
    "scripts/grc/grc_mcp_server.py": "fastmcp_grc_corpus",
    "Agent_Squire/agents/grc_librarian/mcp_server/server.py": "grc_librarian",
}

# Directories we never want to traverse (vendor / cache).
IGNORED_DIR_PARTS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "site-packages",
}


def _snake(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return cleaned or "unknown_mcp"


def _normalize_path(repo_root: Path, candidate: Path) -> str:
    try:
        return candidate.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()


def _path_should_skip(repo_root: Path, candidate: Path) -> bool:
    try:
        rel = candidate.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return True
    return any(part in IGNORED_DIR_PARTS for part in rel.parts)


def _derive_agent_id(rel_path: str) -> str:
    if rel_path in PATH_AGENT_MAP:
        return PATH_AGENT_MAP[rel_path]
    # Fallback: parent directory snake_cased.
    parts = rel_path.split("/")
    parent = parts[-2] if len(parts) >= 2 else "mcp_server"
    return _snake(parent)


def _iter_matches(repo_root: Path) -> Iterable[Path]:
    for pattern in MCP_FILE_GLOBS:
        for match in repo_root.glob(pattern):
            if match.is_file() and not _path_should_skip(repo_root, match):
                yield match


def discover(repo_root: str | Path | None = None) -> List[dict]:
    """Return findings for every MCP server registration in the repo."""
    root = Path(repo_root) if repo_root else Path.cwd()
    seen: set[str] = set()
    findings: List[dict] = []
    for match in _iter_matches(root):
        rel = _normalize_path(root, match)
        if rel in seen:
            continue
        seen.add(rel)
        findings.append(
            {
                "agent_id": _derive_agent_id(rel),
                "source": "mcp_servers",
                "evidence": f"MCP server file: {rel}",
            }
        )
    return findings

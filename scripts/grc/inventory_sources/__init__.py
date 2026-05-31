"""Inventory source plugins.

Each plugin module exports a ``discover()`` callable that returns a list of
``{'agent_id', 'source', 'evidence'}`` dicts. The ``SOURCES`` registry below
maps source-name string to the plugin's ``discover`` function. The shadow-agent
scanner in ``scripts/grc/inventory_scan.py`` iterates ``SOURCES`` to walk every
known agent-producing surface of the CoreDirective stack.

Per 20-RESEARCH D11 the six required sources are:

* ``docker_compose``  - container images that route LLM traffic
* ``n8n_workflows``   - workflow exports that invoke LLM nodes
* ``mcp_servers``     - FastMCP server registrations
* ``claude_skills``   - ``~/.claude/skills/**/SKILL.md`` entries
* ``openclaw_skills`` - ``openclaw.json`` skill registrations
* ``python_grep``     - regex scan for direct LLM SDK constructors
"""
from __future__ import annotations

from . import (
    claude_skills,
    docker_compose,
    mcp_servers,
    n8n_workflows,
    openclaw_skills,
    python_grep,
)

SOURCES = {
    "docker_compose": docker_compose.discover,
    "n8n_workflows": n8n_workflows.discover,
    "mcp_servers": mcp_servers.discover,
    "claude_skills": claude_skills.discover,
    "openclaw_skills": openclaw_skills.discover,
    "python_grep": python_grep.discover,
}

__all__ = ["SOURCES"]

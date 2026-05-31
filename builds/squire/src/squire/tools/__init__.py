"""External-integration tools used by Squire LangGraph nodes.

Each module here is a thin HTTP wrapper with fail-open semantics:
  - tavily: threat-intel search; returns empty envelope when TAVILY_API_KEY absent.
  - telegram: n8n master-cmd webhook relay for HIGH/CRITICAL routing.

Tools are importable as `from squire.tools import tavily_search, telegram_notify`.
"""
from __future__ import annotations

from .tavily import tavily_search  # noqa: F401
from .telegram import telegram_notify  # noqa: F401

__all__ = ["tavily_search", "telegram_notify"]

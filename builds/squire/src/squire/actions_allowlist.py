"""Phase 17 recommend-only action allow-list enforcer.

Called by the FastAPI response layer (17-09) after the graph produces a draft report.
Scans recommended_actions bullets against the forbidden_verb_patterns in actions.yml;
on hit, rewrites or rejects per enforcement_mode.

Criterion #16: actions.yml allow-list for Phase 17 (recommend-only).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .settings import settings


@dataclass
class AllowlistConfig:
    mode: str
    phase: str
    allowed_verbs: list[str]
    forbidden_patterns: list[re.Pattern]
    enforcement_mode: str  # "rewrite" | "reject"
    raw: dict[str, Any]


@lru_cache(maxsize=1)
def load_config() -> AllowlistConfig:
    path = Path(settings.actions_allowlist_path)
    if not path.exists():
        # Fallback: if file missing, deny everything (fail-closed for a security control)
        return AllowlistConfig(
            mode="recommend_only",
            phase="17",
            allowed_verbs=[],
            forbidden_patterns=[re.compile(r".*", re.IGNORECASE)],
            enforcement_mode="reject",
            raw={"error": f"missing config at {path}"},
        )
    data = yaml.safe_load(path.read_text())
    patterns = [re.compile(p, re.IGNORECASE) for p in data.get("forbidden_verb_patterns", [])]
    return AllowlistConfig(
        mode=data.get("mode", "recommend_only"),
        phase=str(data.get("phase", "17")),
        allowed_verbs=[v.lower() for v in data.get("allowed_verbs", [])],
        forbidden_patterns=patterns,
        enforcement_mode=data.get("enforcement_mode", "rewrite"),
        raw=data,
    )


def check_action(action_text: str) -> tuple[bool, str | None]:
    """Returns (is_safe, matched_pattern_or_none)."""
    cfg = load_config()
    for pat in cfg.forbidden_patterns:
        if pat.search(action_text):
            return (False, pat.pattern)
    return (True, None)


class RecommendOnlyViolation(Exception):
    def __init__(self, events: list[dict]):
        super().__init__("recommend-only allow-list violation")
        self.events = events


def enforce_recommendations(actions: list[str]) -> tuple[list[str], list[dict]]:
    """
    Apply allow-list to a list of recommended_action strings.
    Returns (possibly_rewritten_actions, sanitization_events).
    """
    cfg = load_config()
    rewritten: list[str] = []
    events: list[dict] = []
    for a in actions:
        ok, pattern = check_action(a)
        if ok:
            rewritten.append(a)
            continue
        ev = {"action": a[:200], "matched_pattern": pattern, "enforcement": cfg.enforcement_mode}
        events.append(ev)
        if cfg.enforcement_mode == "reject":
            # Whole response will be rejected by caller
            raise RecommendOnlyViolation(events)
        # rewrite mode: prepend RECOMMEND: so the directive becomes an advisory
        rewritten.append(f"RECOMMEND: human operator should {a}")
    return rewritten, events


def enforce_response(report: dict[str, Any]) -> dict[str, Any]:
    """Mutates report['recommended_actions'] per allow-list; attaches sanitization_events on report."""
    actions = report.get("recommended_actions") or []
    if not isinstance(actions, list):
        return report
    safe_actions, events = enforce_recommendations([str(a) for a in actions])
    report["recommended_actions"] = safe_actions
    if events:
        report.setdefault("sanitization_events", []).extend(events)
    return report

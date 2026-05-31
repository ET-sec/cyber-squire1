"""Datadog telemetry helper for grc_librarian agent.

Sets the agent_id tag at module import so every downstream ddtrace span
carries it. Reads agent_id from environment variable AGENT_ID with a
hard-coded default matching the .agents/registry.yaml row for this agent.

Phase 20 Plan 20-05 (CoSAI visibility rollout).
"""
import os
import logging

AGENT_ID = os.getenv("AGENT_ID", "grc_librarian")  # matches .agents/registry.yaml

log = logging.getLogger(__name__)


def set_agent_id() -> str:
    """Set agent_id as a Datadog global tag. Returns the resolved AGENT_ID."""
    try:
        from ddtrace import tracer
        tracer.set_tags({"agent_id": AGENT_ID})
        log.info("ddtrace agent_id tag set: %s", AGENT_ID)
    except ImportError:
        log.warning("ddtrace not installed; agent_id tagging skipped for %s", AGENT_ID)
    except Exception as e:
        log.error("failed to set agent_id tag: %s", e)
    return AGENT_ID


# Auto-set on import so all downstream code paths are tagged.
set_agent_id()

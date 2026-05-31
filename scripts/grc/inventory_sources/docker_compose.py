"""Docker Compose source plugin.

Walks ``COREDIRECTIVE_ENGINE/docker-compose.yaml`` (override path via
``COMPOSE_PATH`` env var) and emits a finding for every service whose image
suggests it is an LLM caller. Data-only services (``postgres``, ``vault``,
``keycloak``, ``whisper``, observability, ingress, etc.) are skipped via the
``NON_AGENT_IMAGES`` substring list so the scanner does not flood CI with
findings for the auth or storage tier.

A normalisation table converts compose service names to the registered
agent_id used in ``.agents/registry.yaml``. The most important entry is
``openclaw-gateway`` -> ``openclaw``: the docker SERVICE name is
``openclaw-gateway`` but the AGENT id in the registry is ``openclaw`` (the
gateway label is the runtime location, not the identity).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a project dep
    yaml = None  # type: ignore[assignment]


DEFAULT_COMPOSE_PATH = "COREDIRECTIVE_ENGINE/docker-compose.yaml"

# Substrings; matched against the lowercased image string. Services whose
# image matches any of these are skipped because they do not call LLMs.
NON_AGENT_IMAGES = (
    "postgres",
    "pgvector",
    "keycloak",
    "vault",
    "whisper",
    "datadog",
    "falco",
    "falcosidekick",
    "teleport",
    "event-handler",
    "fluentd",
    "cloudflare/cloudflared",
    "cloudflared",
    "clickhouse",
    "redis",
)

# Substrings that mark a service as LLM-callable. Hits here always produce a
# finding, even if NON_AGENT_IMAGES also matches (kept disjoint by ordering).
LLM_IMAGE_SUBSTRINGS = (
    "openclaw",
    "ollama",
    "anthropic",
    "litellm",
    "nemo",
    "squire",
    "n8n",
)

# Compose service name -> registered agent_id. Anything not in the map falls
# back to ``_normalize_name``. The openclaw-gateway entry is load-bearing:
# the docker SERVICE is openclaw-gateway, the AGENT id in registry.yaml is
# ``openclaw`` (see 20-01 SUMMARY and the registry).
SERVICE_NAME_MAP = {
    "openclaw-gateway": "openclaw",
    "cd-service-openclaw-gateway": "openclaw",
    "cd-service-n8n": "n8n_runtime",
    "cd-service-ollama": "ollama_runtime",
    "cd-service-nemo": "nemo_guardrails",
    "cd-service-squire": "squire",
}


def _normalize_name(service_name: str) -> str:
    """Drop ``cd-service-`` prefix, then snake_case the remainder."""
    stem = service_name
    if stem.startswith("cd-service-"):
        stem = stem[len("cd-service-"):]
    return stem.replace("-", "_").lower()


def _is_non_agent(image: str) -> bool:
    image_lc = image.lower()
    return any(skip in image_lc for skip in NON_AGENT_IMAGES)


def _is_llm_caller(image: str) -> bool:
    image_lc = image.lower()
    return any(token in image_lc for token in LLM_IMAGE_SUBSTRINGS)


def discover() -> List[dict]:
    """Return list of {agent_id, source, evidence} for every LLM-callable
    service declared in the project compose file."""
    if yaml is None:
        print(
            "inventory_sources.docker_compose: pyyaml missing; skipping",
            file=sys.stderr,
        )
        return []

    compose_path = Path(os.environ.get("COMPOSE_PATH", DEFAULT_COMPOSE_PATH))
    if not compose_path.is_file():
        print(
            f"inventory_sources.docker_compose: {compose_path} not found; skipping",
            file=sys.stderr,
        )
        return []

    try:
        with compose_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - malformed compose
        print(
            f"inventory_sources.docker_compose: YAML parse error {exc}",
            file=sys.stderr,
        )
        return []

    services = data.get("services") or {}
    findings: List[dict] = []
    for svc_name, svc_cfg in services.items():
        if not isinstance(svc_cfg, dict):
            continue
        image = str(svc_cfg.get("image", svc_cfg.get("build", "")))
        if not image:
            continue
        # LLM callers win over the skip list (covers e.g. nemo, squire which
        # have neutral-looking image names but ARE LLM callers).
        if _is_llm_caller(image):
            agent_id = SERVICE_NAME_MAP.get(svc_name, _normalize_name(svc_name))
            findings.append(
                {
                    "agent_id": agent_id,
                    "source": "docker_compose",
                    "evidence": (
                        f"docker-compose.yaml service '{svc_name}' "
                        f"(image: {image})"
                    ),
                }
            )
            continue
        if _is_non_agent(image):
            continue
        # Image neither obviously LLM nor obviously non-agent. Skip; the
        # python_grep and openclaw_skills plugins will surface anything real.

    return findings

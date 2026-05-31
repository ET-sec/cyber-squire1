"""Unit tests for inventory_scan and its source plugins.

Each test isolates one plugin or one branch of the orchestrator using
``tmp_path`` + ``monkeypatch`` so the real environment (~/.claude/skills,
COREDIRECTIVE_ENGINE/docker-compose.yaml, etc.) is not required.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import inventory_scan  # noqa: E402
from scripts.grc.inventory_sources import (  # noqa: E402
    docker_compose,
    mcp_servers,
    n8n_workflows,
    openclaw_skills,
    python_grep,
)


def test_docker_compose_normalizer(tmp_path, monkeypatch):
    compose = tmp_path / "docker-compose.yaml"
    compose.write_text(
        yaml.safe_dump(
            {
                "services": {
                    "cd-service-openclaw-gateway": {
                        "image": "openclaw:v2026.3.8",
                    },
                    "cd-service-db": {
                        "image": "postgres:16",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("COMPOSE_PATH", str(compose))
    findings = docker_compose.discover()
    ids = {f["agent_id"] for f in findings}
    assert "openclaw" in ids, ids
    assert "db" not in ids
    assert not any("postgres" in f["evidence"].lower() for f in findings)


def test_n8n_workflow_id_map(tmp_path):
    exports = tmp_path / "exports"
    exports.mkdir()
    (exports / "wf.json").write_text(
        json.dumps({"id": "UIf3v1ZNN98OtUge", "name": "Master Orchestrator"}),
        encoding="utf-8",
    )
    findings = n8n_workflows.discover(exports_dir=exports)
    assert findings
    assert findings[0]["agent_id"] == "master_orchestrator"
    assert "UIf3v1ZNN98OtUge" in findings[0]["evidence"]


def test_n8n_gmail_consolidation(tmp_path):
    exports = tmp_path / "exports"
    exports.mkdir()
    gmail_ids = [
        "2A0O7MzPvUCCYoLV",
        "wTUraUYjsHXCGWgr",
        "NxoxcIcYRo0XPkOz",
        "yLA81NXy9LBvps8m",
    ]
    for i, wf_id in enumerate(gmail_ids):
        (exports / f"gmail_{i}.json").write_text(
            json.dumps({"id": wf_id, "name": f"Gmail Reader {i}"}),
            encoding="utf-8",
        )
    findings = n8n_workflows.discover(exports_dir=exports)
    assert len(findings) == 4
    assert all(f["agent_id"] == "n8n_gmail_readers" for f in findings)


def test_mcp_server_filename_resolution(tmp_path):
    """Regression test: the file IS named grc_mcp_server.py (RESEARCH Topic 1)
    and it MUST map to agent_id ``fastmcp_grc_corpus``. The obsolete
    grc_corpus_server.py filename must never resurface."""
    (tmp_path / "scripts" / "grc").mkdir(parents=True)
    target = tmp_path / "scripts" / "grc" / "grc_mcp_server.py"
    target.write_text("# stub MCP server\n", encoding="utf-8")
    findings = mcp_servers.discover(repo_root=tmp_path)
    ids = {f["agent_id"] for f in findings}
    assert "fastmcp_grc_corpus" in ids, ids
    assert all("grc_corpus_server.py" not in f["evidence"] for f in findings)


def test_openclaw_skills_builtin_filter(tmp_path):
    cfg = tmp_path / "openclaw.json"
    cfg.write_text(
        json.dumps(
            {
                "skills": [
                    {"name": "tavily-search"},
                    {"name": "custom-skill-xyz"},
                ]
            }
        ),
        encoding="utf-8",
    )
    findings = openclaw_skills.discover(config_path=cfg)
    ids = {f["agent_id"] for f in findings}
    assert "custom_skill_xyz" in ids, ids
    assert "tavily_search" not in ids
    assert "tavily-search" not in ids


def test_python_grep_finds_anthropic_constructor(tmp_path, monkeypatch):
    agent_dir = tmp_path / "Agent_Squire" / "agents" / "test_agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "main.py").write_text(
        "import anthropic\n"
        "client = anthropic.Anthropic(api_key='x')\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    findings = python_grep.discover(scan_roots=["Agent_Squire"])
    ids = {f["agent_id"] for f in findings}
    assert "test_agent" in ids, ids


def test_diff_detects_shadow(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"agents": [{"agent_id": "squire"}]}),
        encoding="utf-8",
    )
    allow_list = tmp_path / "allow.yaml"
    allow_list.write_text(yaml.safe_dump({"non_agents": []}), encoding="utf-8")

    def ghost_source():
        return [{"agent_id": "ghost", "source": "x", "evidence": "y"}]

    overrides = {name: (lambda: []) for name in inventory_scan.SOURCES}
    overrides["docker_compose"] = ghost_source
    report = inventory_scan.run(registry, allow_list, source_overrides=overrides)
    assert "ghost" in report["shadow"], report


def test_allow_list_suppresses(tmp_path):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"agents": [{"agent_id": "squire"}]}),
        encoding="utf-8",
    )
    allow_list = tmp_path / "allow.yaml"
    allow_list.write_text(
        yaml.safe_dump(
            {
                "non_agents": [
                    {
                        "agent_id": "*",
                        "source": "docker_compose",
                        "reason": "test",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    def ghost_source():
        return [
            {"agent_id": "ghost", "source": "docker_compose", "evidence": "y"}
        ]

    overrides = {name: (lambda: []) for name in inventory_scan.SOURCES}
    overrides["docker_compose"] = ghost_source
    report = inventory_scan.run(registry, allow_list, source_overrides=overrides)
    assert "ghost" not in report["shadow"], report


def test_fail_on_shadow_exit_code(tmp_path, monkeypatch, capsys):
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        yaml.safe_dump({"agents": [{"agent_id": "squire"}]}),
        encoding="utf-8",
    )
    allow_list = tmp_path / "allow.yaml"
    allow_list.write_text(yaml.safe_dump({"non_agents": []}), encoding="utf-8")

    def ghost_source():
        return [{"agent_id": "ghost", "source": "docker_compose", "evidence": "y"}]

    # Patch every source via SOURCES dict so main()'s code path is exercised.
    empty = {name: (lambda: []) for name in inventory_scan.SOURCES}
    empty["docker_compose"] = ghost_source
    monkeypatch.setattr(inventory_scan, "SOURCES", empty)

    exit_code = inventory_scan.main(
        [
            "--registry",
            str(registry),
            "--allow-list",
            str(allow_list),
            "--fail-on-shadow",
            "--format",
            "json",
        ]
    )
    assert exit_code == 1

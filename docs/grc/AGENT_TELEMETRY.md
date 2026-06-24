---
title: Agent Telemetry (CoSAI Visibility)
classification: PUBLIC
phase: 20
plan: 05
last_updated: 2026-05-31
---

# Agent Telemetry

Per-agent_id tagging across every log, metric, and trace shipped from the
Organization agent stack. Authoritative source for "what did agent X do in
the last N minutes" queries in Datadog.

## Goal

Every log, metric, and trace shipped from the agent stack carries an
agent_id tag so per-agent behavior is queryable. Visibility without
per-agent breakdown is theater; this is Phase 1 of the 3-phase CoSAI
visibility rollout (Phase 1 visibility, Phase 21 contextual access
control, Phase 22 continuous policy assurance).

## Tag Taxonomy

The agent_id tag values are the union of two sources:

1. Every row in the Agent Registry (`.agents/registry.yaml`) contributes
   one agent_id (13 values today).
2. The reserved name `falco_sensor` for the kernel-level eBPF host
   detection agent (intentionally outside the Registry because it is not
   an LLM-caller).

The Registry is the source of truth. The daily inventory_scan
(Plan 20-04) enforces zero drift between the Registry and what the stack
actually runs.

## Cardinality Budget

13 LLM-callers plus 1 falco_sensor equals 14 distinct values. Datadog tag
cardinality limit is 100k per metric; this rollout sits four orders of
magnitude under the ceiling. Per-session, per-request, or per-conversation
agent_id is FORBIDDEN to prevent future explosion. Adding a new value
requires a Registry row change (gated by Plan 20-04's PR check).

## Rollout Topology

| Surface | Mechanism | File |
|---|---|---|
| Python agents (5: 4 in public mirror, 1 gitignored) | `ddtrace.tracer.set_tags` at module import | `Agent_Squire/agents/<id>/telemetry.py` (public mirror: blue_squire, red_squire, keeper_squire, grc_librarian) and `builds/squire/src/squire/telemetry.py` (gitignored local) |
| n8n workflows (4) | Shared Code-node snippet injects `dd_tags: ['agent_id:<id>']` | `Agent_Squire/n8n_function_snippets/agent_id_tagger.js` |
| Falcosidekick | `customfields` adds `agent_id: falco_sensor` | `falcosidekick.yaml` on the host |
| openclaw gateway | Datadog Agent host-level `DD_TAGS` env var (binary cannot self-tag) | `datadog-agent` service env on the host |

Side-effect import pattern for Python agents: importing the agent
package implicitly imports `telemetry`, which sets the tag at module load
time. This guarantees the tag is present before the first LLM call.

## Rollout Topology Limitations

The Telegram-interfaced bot `cdirective_bot` shares the `openclaw`
host-level tag in Phase 20. The bot routes user messages through the
openclaw gateway, and Phase 20 does NOT inject a per-bot custom header on
those requests. Result: metrics, traces, and logs from `cdirective_bot`
calls appear as `agent_id:openclaw` in Datadog. The Agent Activity
dashboard correspondingly groups these two identities as one row in
Phase 20.

Per-bot telemetry breakdown for Telegram-interfaced agents is deferred to
Phase 21 (named OpenClaw skill registration with custom headers per bot).
At that point `cdirective_bot` gets a distinct ddtrace tag injected by the
openclaw skill wrapper, and the dashboard row splits.

Operational implication: queries such as
`sum:trace.anthropic.request.count{agent_id:openclaw}` in Phase 20
conflate two agents. Do NOT cite this metric as a per-agent SLA until
Phase 21 ships.

## Dashboard

"Agent Activity (CoSAI Visibility)" managed in Terraform at
`terraform/cd-do-infrastructure/agent_activity_dashboard.tf`. Four widgets
faceted by agent_id (Calls per Minute, Success Rate 7d, Top Destinations,
Top Tools). Registry-driven: new agents appear automatically as their
telemetry lands. Dashboard description and an inline note widget both
surface the Phase 20 `cdirective_bot` limitation.

## Verification

Query templates for ad-hoc per-agent breakdown:

```
sum:trace.anthropic.request.count{*} by {agent_id}.as_rate()
logs("*").rollup("count").by("agent_id")
sum:trace.http.request.count{*} by {agent_id, http.url}
```

End-to-end smoke test (after rollout):

1. Trigger an LLM call from one Python agent and one n8n workflow.
2. Wait 60 seconds for Datadog ingestion.
3. Confirm both `agent_id` values appear in the Calls/min widget.
4. Confirm Falco alert routed through Falcosidekick surfaces as
   `agent_id:falco_sensor` in the Datadog event stream.

## Failure Modes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Span missing agent_id tag | Agent did not import its `telemetry` module | grep for the side-effect import in the package `__init__.py` or entrypoint |
| Unknown agent_id in dashboard | Shadow agent operating outside the Registry | inventory_scan from Plan 20-04 should also be flagging it; reconcile before next deploy |
| Cardinality spike alert from Datadog | Someone added per-session or per-request agent_id | revert immediately; treat as a Sev-2 because it threatens metric retention |
| `cdirective_bot` traffic invisible | Expected Phase 20 behavior; collapses into `agent_id:openclaw` | resolved in Phase 21 when the per-bot custom header lands |

## Glossary

- **agent_id**: Stable RFC-1123 lowercase identifier for an LLM-calling
  agent or reserved host detection agent. Single source of truth: the
  Agent Registry.
- **CoSAI**: Coalition for Secure AI; the 3-phase visibility model this
  rollout targets.
- **ddtrace**: Datadog's Python tracing SDK. The mechanism Python agents
  use to set process-wide tags.
- **Falcosidekick**: Event router that forwards Falco runtime alerts to
  downstream sinks including Datadog.

---

*Companion artifacts: `.agents/registry.yaml` (single source of truth),
`scripts/grc/inventory_scan.py` (drift detector), `agent_activity_dashboard.tf`
(dashboard), `AGENT_SIGNING.md` (Sigstore keyless signing for the cards
behind these telemetry tags), `AI_AUDIT_TRAIL_SPEC.md` (per-investigation
audit rows now carry `agent_id` to keep the per-agent attribution story
consistent across metrics, logs, traces, and audit records).*

<!-- TODO(et): confirm the current `.agents/registry.yaml` row count matches the "13 LLM-callers" figure in the Cardinality Budget; the registry currently includes the four Squire agents and additional rows for openclaw, cdirective_bot, coredirective_bot, fastmcp_grc_corpus, master_orchestrator, n8n_content_research, n8n_gmail_readers, n8n_telegram_supervisor, grc_librarian. -->

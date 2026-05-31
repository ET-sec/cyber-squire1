# .agents/ - Agent Registry and Cards

## Purpose

This directory is the canonical home for CoreDirective's Agent Registry plus per-agent signed Agent Cards. It is the spine of CoSAI Visibility (Phase 20). Every LLM-calling identity in the stack carries one registry row here, and Plan 20-02 onward attaches a Cosign-signed A2A Agent Card per row. Downstream tooling (`inventory_scan.py`, Datadog tagging, the capability matrix) all key off the identifiers defined in this directory.

## Files

| File | Purpose |
|------|---------|
| `registry.yaml` | Single source of truth listing every LLM-calling agent. Validated by `scripts/grc/registry_schema.json`. |
| `<agent_id>.card.json` | Google A2A v1.0 Agent Card for one agent. Authored once per registry row where `is_ai_agent: true`. |
| `<agent_id>.card.json.sigstore.json` | Cosign keyless-OIDC sigstore bundle (protobuf format) signing the card above. Produced by `.github/workflows/sign-agent-cards.yml` (Plan 20-03). |
| `README.md` | This file. Operator doc for tier semantics, add-new-agent workflow, capability and auth vocabulary. |

The bundle filename uses the double-extension form `<agent_id>.card.json.sigstore.json` rather than the single-extension form `<agent_id>.card.sigstore.json` referenced in `20-RESEARCH.md` decision D3. Plan 20-03 sign and verify both produce and consume this exact double-extension shape, and `docs/grc/AGENT_SIGNING.md` "Naming convention" cross-references the variance.

## Sensitivity Tiers

The `sensitivity_tier` field on each registry row classifies blast radius if the agent identity is compromised or misused. Plan 20-02 capability cards and Plan 20-05 capability matrix both inherit this classification.

| Tier | Definition | Examples in this registry |
|------|------------|---------------------------|
| `low` | Read-only access to public or non-sensitive internal data. Compromise yields disclosure of already-public-shareable content; no write side-effects, no third-party send actions. | `grc_librarian`, `keeper_squire`, `n8n_content_research`, `fastmcp_grc_corpus` |
| `medium` | Read access to internal-only data, or low-volume read of customer or workspace data. Compromise yields disclosure of internal artifacts but no destructive writes. | `squire`, `n8n_gmail_readers` |
| `high` | Read or write access to customer data, workspace APIs, or third-party send-actions (Telegram, Notion, GitHub). Compromise can move money, post in operator channels, or modify production state. | `blue_squire`, `red_squire`, `openclaw`, `master_orchestrator`, `n8n_telegram_supervisor`, `cdirective_bot`, `coredirective_bot` |
| `critical` | Actuator on production infrastructure (Terraform apply, Cloudflare DNS, droplet shell, payment systems). Compromise can take services offline or move material amounts of money. Reserved; no entry in this registry currently qualifies. | (none yet) |

When in doubt promote upward. A row tagged `high` that turns out to be `medium` costs nothing; a row tagged `medium` that turns out to be `high` skips controls.

## Adding a New Agent

Six steps. Do not skip any.

1. Append a row to `.agents/registry.yaml`. Every field in `scripts/grc/registry_schema.json` is required. Use the existing rows as patterns for `capabilities` and `data_access` granularity.
2. Validate the row. The one-liner from the registry header comment runs the JSON Schema check locally:
   `python3 -c "import json,yaml,jsonschema; jsonschema.validate(yaml.safe_load(open('.agents/registry.yaml')), json.load(open('scripts/grc/registry_schema.json')))"`
3. Author `.agents/<agent_id>.card.json` to the Google A2A v1.0 Agent Card spec (`name`, `description`, `version`, `url`, `skills[]` required; `capabilities`, `securitySchemes` optional). The spec lives at `https://a2a-protocol.org/latest/specification/`.
4. Commit and push on a feature branch. The `sign-agent-cards.yml` workflow (Plan 20-03) signs the card via keyless Cosign OIDC and commits the `.sigstore.json` bundle back to the branch. The PR-gate workflow (Plan 20-04) verifies every card has a valid bundle before merge.
5. Update `docs/grc/AGENTIC_IAM_CAPABILITY_MATRIX.md` with one new row carrying the CSA Agentic NIST AI RMF Profile seven dimensions plus `worst_case_if_compromised`.
6. Wire telemetry. Add `agent_id:<agent_id>` to the Datadog tag set for that runtime (env var on container, `tracer.set_tags` for Python, n8n header for workflow events, `FALCOSIDEKICK_CUSTOMFIELDS` for sensors). Cardinality budget is roughly 20 distinct values across the whole registry; never add per-session or per-request siblings.

## Capability Naming

Capabilities are short tokens that describe what the agent can actually do. Lowercase snake_case. Action-verb prefix where the action is obvious: `read_`, `write_`, `invoke_`, `post_`, `route_`, `summarize_`, `classify_`. Suffix with `:scope` only when the scope is stable and small (e.g. `gmail_read:main` for the four-mailbox case). Avoid prose capability names ("Reads the GRC corpus and summarizes findings") - those belong in the Agent Card `description` field, not in the registry capability array.

## Auth Method Vocabulary

The `auth_method` field is enumerated in the schema. Adding a new value requires a schema bump plus an entry in the table below.

| Value | When to use |
|-------|-------------|
| `keycloak_service_account` | Agent uses a Keycloak client with `client_credentials` grant and scoped roles. Default for Squire family agents (squire, blue_squire, red_squire, grc_librarian, keeper_squire). |
| `telegram_token+openclaw` | Telegram bot whose token routes inbound chats through the OpenClaw gateway for LLM completion. |
| `telegram_token+n8n` | Telegram bot whose token routes inbound chats through n8n workflow actions. |
| `stdio_local` | Local stdio process trust. No network auth boundary. Used by FastMCP servers where the calling client is the OS-trusted parent process. |
| `oauth2_user` | OAuth 2.0 user-delegated grant against a SaaS API (Gmail, Drive, Sheets). Token stored in the n8n credential vault. |
| `openclaw_api_key` | Static API key consumed by the OpenClaw gateway runtime itself. |
| `n8n_webhook+creds` | n8n workflow runtime; webhook endpoint plus per-credential vault entries for individual node calls. |
| `ssh_shell` | Reserved for any future operator-shell agents. No entry currently uses it; documented here so the schema enum has a stable home. |

## Capability Tier Cross-Reference

`sensitivity_tier` (this file) is risk classification. `trust_tier` (in `.facts/stack-facts.yaml`) is deployment classification (1 = read-only at deploy time, 2 = writes at deploy time). They overlap but do not merge. A `trust_tier: 1` agent can still carry `sensitivity_tier: high` if its read scope covers operator-channel data.

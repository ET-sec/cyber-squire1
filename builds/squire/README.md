# Squire

AI SOC analyst for CoreDirective Engine.

## What it is

A FastAPI service that receives security alerts (Falco, Datadog, webhook), runs a
LangGraph investigation pipeline against GRC docs and incident history, and returns
a recommend-only report. No automatic remediation in Phase 17.

## Layout

```
builds/squire/
  src/squire/            Python package
    __init__.py
    settings.py          pydantic-settings config
    db.py                SQLAlchemy engine + session
    app.py               FastAPI app factory with /health
    actions_allowlist.py Recommend-only response sanitizer
    dedup.py             Redis-backed 5-minute sliding dedup
    nodes/               LangGraph nodes: classify, enrich, retrieve, investigate, draft, critique, route
    retrievers/          GRC document retriever (pgvector)
    tools/               Web search and Telegram notice tools
  config/actions.yml     Recommend-only allow-list
  migrations/            Raw SQL migrations
  tests/                 pytest suite
  Dockerfile             Container build
  pyproject.toml         Package metadata
```

## Local development

```bash
cd builds/squire
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# With Doppler:
doppler run --project coredirective-engine --config prd --command "pytest tests/ -q"
doppler run --project coredirective-engine --config prd --command "uvicorn squire.app:app --port <port>"
```

## Container

```bash
docker build -t squire:dev -f Dockerfile .
docker run --rm -p <port>:<port> \
  -e CD_DB_USER=x -e CD_DB_PASS=x -e CD_DB_NAME=x \
  -e LANGFUSE_PUBLIC_KEY=pk -e LANGFUSE_SECRET_KEY=sk \
  -e SQUIRE_WEBHOOK_TOKEN=x \
  squire:dev
curl http://localhost:<port>/health
```

## Environment (via Doppler)

| Variable | Purpose |
|----------|---------|
| `CD_DB_USER` / `CD_DB_PASS` / `CD_DB_NAME` | Postgres connection |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` | Tracing |
| `ANTHROPIC_API_KEY` | Not set on Squire and not read by it. The model credential lives on the guardrails container, which is the container that calls the model (Phase 22, AI-02) |
| `SQUIRE_WEBHOOK_TOKEN` | Shared-secret for webhook auth |
| `LANGFUSE_REDIS_PASSWORD` | Dedup Redis auth |
| `ANTHROPIC_DAILY_CEILING_USD` | Cost ceiling (default 5.00) |
| `SQUIRE_COST_BREACH_MODE` | `ollama` | `refuse` | `warn_only` |
| `SQUIRE_LLM_BACKEND` | `nemo` (default) \| `max` \| `ollama` |

## Phase 17 boundaries

Squire recommends. Humans execute. The `config/actions.yml` allow-list enforces
this at the FastAPI response boundary. Autonomous execution is out of scope for
Phase 17 and requires a later phase with explicit approval flow.

## Migrations

```bash
# Apply the initial schema to the target database (name from CD_DB_NAME) on the host
doppler run --project coredirective-engine --config prd --command '
  scp migrations/001_squire_tables.sql <host>:/tmp/
  ssh <host> "docker cp /tmp/001_squire_tables.sql <db-container>:/tmp/ && \
    docker exec -e PGPASSWORD=\"\$CD_DB_PASS\" <db-container> \
      psql -U \"\$CD_DB_USER\" -d \"\$CD_DB_NAME\" -f /tmp/001_squire_tables.sql"
'
```

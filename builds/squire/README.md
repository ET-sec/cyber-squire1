# Squire

Autonomous SOC analyst for CoreDirective Engine. Phase 17 scaffold.

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
    nodes/               LangGraph nodes (later plan)
    retrievers/          pgvector + keyword retrievers (later plan)
    tools/               Action tools (later plan)
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
doppler run --project coredirective-engine --config prd -- pytest tests/ -q
doppler run --project coredirective-engine --config prd -- uvicorn squire.app:app --port 8020
```

## Container

```bash
docker build -t cd-service-squire:dev -f Dockerfile .
docker run --rm -p 8020:8020 \
  -e CD_DB_USER=x -e CD_DB_PASS=x -e CD_DB_NAME=x \
  -e LANGFUSE_PUBLIC_KEY=pk -e LANGFUSE_SECRET_KEY=sk \
  -e ANTHROPIC_API_KEY=x -e SQUIRE_WEBHOOK_TOKEN=x \
  cd-service-squire:dev
curl http://127.0.0.1:8020/health
```

## Environment (via Doppler)

| Variable | Purpose |
|----------|---------|
| `CD_DB_USER` / `CD_DB_PASS` / `CD_DB_NAME` | Postgres connection |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` | Tracing |
| `ANTHROPIC_API_KEY` / `OPENCLAW_ANTHROPIC_KEY` | LLM auth |
| `SQUIRE_WEBHOOK_TOKEN` | Shared-secret for webhook auth |
| `LANGFUSE_REDIS_PASSWORD` | Dedup Redis auth |
| `ANTHROPIC_DAILY_CEILING_USD` | Cost ceiling (default 5.00) |
| `SQUIRE_COST_BREACH_MODE` | `ollama` | `refuse` | `warn_only` |
| `SQUIRE_LLM_BACKEND` | `api` | `max` | `ollama` |

## Phase 17 boundaries

Squire recommends. Humans execute. The `config/actions.yml` allow-list enforces
this at the FastAPI response boundary. Autonomous execution is out of scope for
Phase 17 and requires a later phase with explicit approval flow.

## Migrations

```bash
# Apply the initial schema to the target database (name from CD_DB_NAME) on the host
doppler run --project coredirective-engine --config prd -- bash -c '
  scp migrations/001_squire_tables.sql cd-alpha:/tmp/
  ssh cd-alpha "docker cp /tmp/001_squire_tables.sql cd-service-db:/tmp/ && \
    docker exec -e PGPASSWORD=\"\$CD_DB_PASS\" cd-service-db \
      psql -U \"\$CD_DB_USER\" -d \"\$CD_DB_NAME\" -f /tmp/001_squire_tables.sql"
'
```

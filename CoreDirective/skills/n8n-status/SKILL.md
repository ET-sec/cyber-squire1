---
name: n8n-status
description: Monitor n8n workflow status, check for failures, and alert on deactivated workflows
---

# n8n Status

## When to Use
User asks about workflow status, n8n health, failed executions, or automation monitoring.

## Active Workflows

| Workflow | ID | Purpose |
|----------|-----|---------|
| MASTER_ORCHESTRATOR_V1 | `UIf3v1ZNN98OtUge` | 17-service hub |
| Error Handler | `el07Swns2MrSSpOK` | Error routing |
| Content Research Pipeline | `nhtwRpJATQoaZpxL` | Research automation |
| Telegram Supervisor Agent | `iO6PfPdk0SSPBTWb` | @Coredirective_bot |
| YouTube Content Factory | `CPBPZ1obRFnuPOE3` | Content generation |
| WhatsApp AI Agent | `WA54364b84dd8d4d` | WhatsApp + Claude |

## Check Workflow Status

Via `exec` on EC2:
```bash
docker exec cd-service-n8n n8n list:workflow --active
```

Or via n8n API (internal):
```bash
curl -s http://localhost:5678/api/v1/workflows | python3 -c "import sys,json; [print(f'{w[\"id\"]} | {\"ACTIVE\" if w[\"active\"] else \"INACTIVE\"} | {w[\"name\"]}') for w in json.load(sys.stdin)[\"data\"]]"
```

Compare active list against expected 6 workflows above. Alert on any missing or inactive.

## Check Failed Executions

Last 24h failures:
```bash
docker exec cd-service-db psql -U $CD_DB_USER -d $CD_DB_NAME -c "SELECT id, workflow_id, finished_at, status FROM execution_entity WHERE status = 'error' AND finished_at > NOW() - INTERVAL '24 hours' ORDER BY finished_at DESC LIMIT 20;"
```

Or via API:
```bash
curl -s "http://localhost:5678/api/v1/executions?status=error&limit=10"
```

## Alert Format

If any workflow inactive or errors found:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "N8N STATUS ALERT\nInactive workflows: [list]\nFailed executions (24h): X\nMost recent failure: [workflow name] at [time]\nError: [message snippet]"}
```

Healthy report:
```json
{"action": "telegram", "chat_id": "6691629392", "text": "N8N STATUS OK\nAll 6 workflows active\nFailed executions (24h): 0\nUptime: good"}
```

## Recovery

If workflow is inactive, re-activate:
```bash
docker exec cd-service-n8n n8n publish:workflow --id=<WORKFLOW_ID>
```

If n8n is unresponsive:
```bash
cd ~/COREDIRECTIVE_ENGINE && docker compose restart cd-service-n8n
```

After restart, fix permissions if needed:
```bash
sudo chown -R 1000:1000 ~/COREDIRECTIVE_ENGINE/CD_VOL_N8N
```

## Known Issues
- n8n Switch v3 is broken in 2.6.x with JSON import -- use v2
- `$env.VAR` blocked -- use `$vars.VAR` via n8n Variables table
- Import deactivates workflows -- must re-publish after import

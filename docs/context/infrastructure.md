# Infrastructure Context

## DigitalOcean Droplet
- **Name:** cd-alpha-engine | **ID:** 557327264 | **IP:** 161.35.0.184 | **Region:** nyc1
- **Spec:** s-4vcpu-8gb (4 vCPU, 8GB RAM, 160GB disk) | $48/mo | Ubuntu 24.04
- **SSH:** `ssh cd-alpha` or `ssh cyber-squire-tunnel` (Cloudflare)
- **Compose:** `/root/COREDIRECTIVE_ENGINE/docker-compose.yaml` (13 services)
- **NEVER** `docker compose down` via tunnel (kills tunnel). NEVER `-v` (wipes volumes).

## 14 Containers (13 Compose + 1 standalone)
| Container | Service | Port |
|-----------|---------|------|
| cd-service-db | PostgreSQL 16 | 5432 |
| cd-service-n8n | n8n SOAR | 5678 |
| cd-service-datadog | Datadog Agent | internal |
| cd-service-falco | Falco (eBPF detection) | internal |
| cd-service-falcosidekick | Alert router to Datadog | internal |
| cd-service-vault | HashiCorp Vault | 8200 |
| cd-service-keycloak | Keycloak v26 (RBAC) | 8080 |
| cd-service-ollama | Ollama (LLM) | 11434 |
| cd-service-whisper | Whisper (transcription) | 8000 |
| cd-service-teleport | Teleport v18 (PAM/JIT) | 3080 |
| cd-service-event-handler | Teleport audit shipper | internal |
| cd-service-fluentd | Fluentd to Datadog | internal |
| tunnel-cyber-squire | Cloudflare Tunnel | host net |
| openclaw-gateway | OpenClaw (Claude Opus 4.7) | 18789-18790 |

## Tunnel Routes
- `n8n.tigouetheory.com` -> localhost:5678
- `ssh.tigouetheory.com` -> localhost:22

## Cloudflare
- Tunnel: `4bcf8238-8a8d-423d-b333-e8fe033d4de9`
- Account: `e4871d2a375f9719092b286866ce26f2` | Zone: `44f6a683c92275d8fea6f6702589c608`

## OpenClaw Gateway
- Container: `openclaw-gateway` (v2026.3.8) | Config: `/root/moltbot/config-dir/openclaw.json`
- Chat completions: `curl -X POST http://172.17.0.1:18789/v1/chat/completions`
- Mac CLI: `openclaw` v2026.3.8, node `ET-MacBook-Air`
- Skills: tavily-search, browser, python-interpreter, notion, gemini, github

## Docker Compose Commands
```bash
ssh cd-alpha 'cd /root/COREDIRECTIVE_ENGINE && docker compose restart cd-service-n8n'
ssh cd-alpha 'cd /root/COREDIRECTIVE_ENGINE && docker compose down && docker compose up -d'
ssh cd-alpha 'chown -R 1000:1000 /root/COREDIRECTIVE_ENGINE/CD_VOL_N8N && chown -R 999:999 /root/COREDIRECTIVE_ENGINE/CD_VOL_POSTGRES'
```

## Droplet File Layout
```
/root/COREDIRECTIVE_ENGINE/
├── docker-compose.yaml
├── .env                   # chmod 600
├── CD_VOL_POSTGRES/
├── CD_VOL_N8N/
├── CD_VOL_OLLAMA/
├── CD_VOL_WHISPER/
├── CD_VOL_VAULT/
└── CD_BACKUPS/
/root/moltbot/config-dir/openclaw.json
```

## AWS EC2 (SUSPENDED)
Instance `i-07bf58fe3de278a75`. Nonpayment. Not in use.

## Sentry
- Org: tigoue-theory | URL: https://tigoue-theory.sentry.io | Project: coredirective-engine
- DSN: in 1Password, Core Infra, "Sentry DSN" | Plan: GitHub Education (free)

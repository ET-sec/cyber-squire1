# CoreDirective Automation Engine (CD-AE) - AI Coding Agent Instructions

**Project:** CoreDirective Automation Engine
**Version:** 2.0.0
**Engineer:** Emmanuel Tigoue
**AI Agent Target:** GitHub Copilot, Claude, Cursor, Windsurf

---

## PROJECT OVERVIEW

The CoreDirective Automation Engine (CD-AE) is a **production-grade, enterprise-hardened automation stack** deployed on AWS EC2 (t3.xlarge). It provides AI-augmented security operations through a SOAR orchestration layer with 17 integrated services.

### The Core Stack

1. **AI Inference (Ollama + Qwen 3 8B):** Local inference engine for security analysis and automation ($0/month)
2. **Orchestrator (n8n):** SOAR platform coordinating 16 services via webhook-driven workflows
3. **Memory (PostgreSQL 16):** Persistent state for workflow execution and automation logs
4. **AI Gateway (OpenClaw):** Claude AI proxy for advanced reasoning and task execution
5. **Voice (Faster-Whisper):** Speech-to-text for voice command input

### Key Metrics

- **Cost:** $0 AI inference (local models vs. $400/month GPU)
- **Privacy:** 100% on-premise inference (sensitive data never leaves network)
- **Security:** 89% NIST/CIS coverage (16/18 controls), zero exposed ports
- **Scale:** 500+ daily workflow executions

---

## CRITICAL NAMING CONVENTIONS

All project components follow the **CoreDirective Standard**:

```
Root Directory:     /home/ec2-user/COREDIRECTIVE_ENGINE
Container Prefixes: cd-service-*           (e.g., cd-service-db, cd-service-n8n)
Network Name:       cd-automation-net
Volume Prefixes:    cd-vol-*               (e.g., cd-vol-postgres, cd-vol-ollama)
Environment Vars:   CD_*                   (e.g., CD_DB_PASS, CD_N8N_KEY)
```

---

## ESSENTIAL WORKFLOWS

### Infrastructure Commands

```bash
# Verify all containers are healthy
docker-compose ps

# View real-time logs (last 50 lines, follow mode)
docker-compose logs -f --tail=50

# Restart entire stack (NEVER via SSH tunnel - kills tunnel container)
docker-compose down && sleep 10 && docker-compose up -d

# Check resource usage (memory, CPU)
docker stats --no-stream

# Access PostgreSQL directly
docker exec -it cd-service-db psql -U cd_admin -d cd_automation_db
```

### Database Maintenance

```bash
# Create manual backup
docker exec cd-service-db pg_dump -U cd_admin -d cd_automation_db -Fc \
  > /home/ec2-user/COREDIRECTIVE_ENGINE/CD_BACKUPS/backup_$(date +%Y%m%d).dump
```

---

## CODEBASE PATTERNS & CONVENTIONS

### Environment Variable Management

**Pattern:** All secrets stored in `.env` (git-ignored)

```env
# Database credentials
CD_DB_USER=cd_admin
CD_DB_PASS=<32-char random string>
CD_DB_NAME=cd_automation_db

# n8n encryption
CD_N8N_KEY=<32-char random string>
CD_N8N_JWT=<32-char random string>
```

**Do NOT:**
- Hardcode passwords in docker-compose.yaml
- Commit .env to git
- Share .env via any channel

### Docker Compose Structure

```yaml
services:
  cd-service-db:          # PostgreSQL 16
  cd-service-n8n:         # n8n SOAR orchestrator
  cd-service-ollama:      # Ollama + Qwen 3 8B
  cd-service-whisper:     # Faster-Whisper STT
  openclaw-gateway:       # Claude AI agent proxy

networks:
  cd-automation-net:      # Bridge network (172.28.0.0/16)
```

**Key Pattern:** All containers communicate via internal Docker network. No direct port exposure to public internet — all access through Cloudflare Tunnel.

### Security & Compliance

- **Network:** Zero-trust architecture via Cloudflare Tunnel (no exposed ports)
- **Host:** SELinux enforcing, read-only filesystems, dropped capabilities
- **Secrets:** Rotated every 90 days, generated via `openssl rand -base64 32`
- **Docs:** Three-tier (Employment_Proof → Technical_Vault → ADHD_Runbook)

---

## FILE STRUCTURE

```
COREDIRECTIVE_ENGINE/
├── docker-compose.yaml              ← All service definitions
├── .env.template                    ← Secrets template
├── cdae-init.sh                     ← RHEL hardening + bootstrap
├── cdae-healthcheck.sh              ← Post-deployment verification
├── deploy_workflows.sh              ← Workflow deployment automation
├── sql/                             ← Database initialization scripts
└── workflow_*.json                  ← n8n workflow definitions

terraform/
├── simple-ec2/                      ← Quick-start deployment
└── cd-aws-automation/               ← Production-grade (VPC, NAT, S3)

docs/
├── Employment_Proof.md              ← Business case overview
├── Technical_Vault.md               ← Architecture deep-dive
└── ADHD_Runbook.md                  ← Operational playbook
```

---

## GUIDELINES FOR AI AGENTS

1. **Always check naming conventions** — Use `cd-*` prefixes for any new components
2. **Read documentation first** — Employment_Proof explains "why", Technical_Vault explains "how", ADHD_Runbook explains "what buttons to press"
3. **Test locally before deploying** — Use `docker-compose up -d` to test changes
4. **Maintain audit trail** — Update docs after any infrastructure change
5. **Never commit .env** — Verify .gitignore before staging
6. **Monitor resource usage** — Ollama can consume all available RAM if not managed

---

**Version:** 2.0.0
**Last Updated:** February 2026
**Maintained By:** Emmanuel Tigoue

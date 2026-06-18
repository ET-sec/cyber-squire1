---
name: docker-watchdog
description: Monitor Docker container health, disk usage, and alert on failures
---

# Docker Watchdog

## When to Use
User asks about container status, Docker health, disk space, or service issues.

## CRITICAL SAFETY RULE
**NEVER run `docker compose down` via SSH tunnel** -- it kills the `tunnel-cyber-squire` container and you lose access.
- Use `docker compose restart <service>` for individual services
- Full `down/up` only with direct SSH or console access

## Expected Containers

| Container | Image | Ports |
|-----------|-------|-------|
| cd-service-db | postgres:16 | 5432 |
| cd-service-n8n | n8nio/n8n | 5678 |
| cd-service-ollama | ollama/ollama | 11434 |
| cd-service-whisper | faster-whisper | 8000 |
| openclaw-gateway | openclaw | 18789 |
| tunnel-cyber-squire | cloudflared | - |

## Health Check

Via `exec` tool on EC2:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | sort
```

Check for:
- Status should be "Up" with healthy uptime
- "Restarting" = container crash loop
- Missing containers = crashed and not restarted

## Disk Usage
```bash
df -h / && echo "---" && docker system df
```
Alert if root filesystem > 80% full. Docker images/volumes can fill disk fast.

## Container Logs (last 50 lines, errors only)
```bash
docker logs --tail 50 cd-service-n8n 2>&1 | grep -i "error\|fatal\|exception"
docker logs --tail 50 cd-service-db 2>&1 | grep -i "error\|fatal\|PANIC"
docker logs --tail 50 cd-service-ollama 2>&1 | grep -i "error\|fatal"
docker logs --tail 50 openclaw-gateway 2>&1 | grep -i "error\|fatal"
```

## Memory Usage
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}"
```
t3.xlarge has 16GB. Alert if total > 14GB or any single container > 8GB.

## Recovery Actions

**Single service restart:**
```bash
cd ~/COREDIRECTIVE_ENGINE && docker compose restart cd-service-n8n
```

**Fix permissions (if n8n loses creds after restart):**
```bash
sudo chown -R 1000:1000 ~/COREDIRECTIVE_ENGINE/CD_VOL_N8N
sudo chown -R 999:999 ~/COREDIRECTIVE_ENGINE/CD_VOL_POSTGRES
```

**Clear Docker disk space:**
```bash
docker system prune -f  # removes stopped containers, unused networks, dangling images
```

## Alert Format
```json
{"action": "telegram", "chat_id": "6691629392", "text": "DOCKER ALERT\nContainer: X\nStatus: crashed/restarting\nDisk: X% used\nAction needed: ..."}
```

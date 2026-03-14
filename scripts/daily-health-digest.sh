#!/usr/bin/env bash
# daily-health-digest.sh — Query Datadog API for 24h system summary, post to Telegram via n8n
# Runs via cron at 9 AM ET daily on the droplet
# Requires: DD_API_KEY, DD_APP_KEY env vars (or source from .env)
#
# Install cron:
#   CRON_TZ=America/New_York
#   0 9 * * * /root/scripts/daily-health-digest.sh >> /var/log/health-digest.log 2>&1

set -euo pipefail

# Load secrets from .env if not already set
if [ -z "${DD_API_KEY:-}" ] || [ -z "${DD_APP_KEY:-}" ]; then
  if [ -f /root/COREDIRECTIVE_ENGINE/.env ]; then
    # shellcheck disable=SC1091
    set -a
    source /root/COREDIRECTIVE_ENGINE/.env
    set +a
    # Map Doppler-style names to DD-style names
    DD_API_KEY="${DATADOG_API_KEY:-${DD_API_KEY:-}}"
    DD_APP_KEY="${DATADOG_APP_KEY_TERRAFORM:-${DD_APP_KEY:-}}"
  fi
fi

if [ -z "${DD_API_KEY:-}" ] || [ -z "${DD_APP_KEY:-}" ]; then
  echo "ERROR: DD_API_KEY and DD_APP_KEY must be set" >&2
  exit 1
fi

DD_SITE="${DD_SITE:-us5.datadoghq.com}"
N8N_WEBHOOK="${N8N_WEBHOOK_URL}"
CHAT_ID="${TELEGRAM_CHAT_ID}"

NOW=$(date +%s)
DAY_AGO=$((NOW - 86400))

# --- Query Datadog APIs ---

# 1. Container status via Docker check
DOCKER_STATUS=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/query?from=${DAY_AGO}&to=${NOW}&query=avg:docker.containers.running{host:cd-alpha-engine-do}" \
  2>/dev/null || echo '{"series":[]}')

CONTAINER_COUNT=$(echo "${DOCKER_STATUS}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    points = data.get('series', [{}])[0].get('pointlist', [])
    if points:
        print(int(points[-1][1]))
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# 2. CPU usage (avg over 24h)
CPU_DATA=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/query?from=${DAY_AGO}&to=${NOW}&query=avg:system.cpu.user{host:cd-alpha-engine-do}" \
  2>/dev/null || echo '{"series":[]}')

CPU_AVG=$(echo "${CPU_DATA}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    points = data.get('series', [{}])[0].get('pointlist', [])
    if points:
        vals = [p[1] for p in points if p[1] is not None]
        print(f'{sum(vals)/len(vals):.1f}%' if vals else 'N/A')
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# 3. Memory usage (avg over 24h)
MEM_DATA=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/query?from=${DAY_AGO}&to=${NOW}&query=avg:system.mem.pct_usable{host:cd-alpha-engine-do}" \
  2>/dev/null || echo '{"series":[]}')

MEM_USED=$(echo "${MEM_DATA}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    points = data.get('series', [{}])[0].get('pointlist', [])
    if points:
        vals = [p[1] for p in points if p[1] is not None]
        used = 100 - (sum(vals)/len(vals) * 100) if vals else 0
        print(f'{used:.1f}%')
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# 4. Disk usage
DISK_DATA=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/query?from=${DAY_AGO}&to=${NOW}&query=avg:system.disk.in_use{host:cd-alpha-engine-do,device:/dev/vda1}" \
  2>/dev/null || echo '{"series":[]}')

DISK_PCT=$(echo "${DISK_DATA}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    points = data.get('series', [{}])[0].get('pointlist', [])
    if points:
        val = points[-1][1]
        print(f'{val*100:.1f}%' if val else 'N/A')
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# 5. Active monitors in alert state
MONITORS=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/monitor?monitor_tags=&name=&tags=" \
  2>/dev/null || echo '[]')

MONITOR_SUMMARY=$(echo "${MONITORS}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        total = len(data)
        alert = sum(1 for m in data if m.get('overall_state') == 'Alert')
        warn = sum(1 for m in data if m.get('overall_state') == 'Warn')
        ok = sum(1 for m in data if m.get('overall_state') == 'OK')
        print(f'{total} monitors: {ok} OK, {warn} Warn, {alert} Alert')
    else:
        print('No monitors configured')
except:
    print('Unable to fetch')
" 2>/dev/null || echo "Unable to fetch")

# 6. PostgreSQL connection count (latest)
PG_DATA=$(curl -sf \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  "https://api.${DD_SITE}/api/v1/query?from=${DAY_AGO}&to=${NOW}&query=avg:postgresql.connections{host:cd-alpha-engine-do}" \
  2>/dev/null || echo '{"series":[]}')

PG_CONNS=$(echo "${PG_DATA}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    points = data.get('series', [{}])[0].get('pointlist', [])
    if points:
        print(int(points[-1][1]))
    else:
        print('N/A')
except:
    print('N/A')
" 2>/dev/null || echo "N/A")

# --- Format Message ---
DATE_STR=$(date -u +"%Y-%m-%d")
TIME_STR=$(TZ="America/New_York" date +"%I:%M %p ET" 2>/dev/null || date -u +"%H:%M UTC")

MSG="<b>Daily Health Digest</b> | ${DATE_STR}
<i>${TIME_STR}</i>

<b>Host:</b> cd-alpha-engine-do (DO s-4vcpu-8gb)

<b>Resources (24h avg):</b>
  CPU: ${CPU_AVG}
  Memory: ${MEM_USED}
  Disk: ${DISK_PCT}
  Containers: ${CONTAINER_COUNT}

<b>PostgreSQL:</b>
  Connections: ${PG_CONNS}

<b>Monitors:</b>
  ${MONITOR_SUMMARY}

<a href=\"https://${DD_SITE}/infrastructure\">Datadog Dashboard</a>"

# --- Send to Telegram via n8n ---
PAYLOAD=$(python3 -c "
import json
msg = '''${MSG}'''
print(json.dumps({
    'action': 'telegram',
    'chat_id': '${CHAT_ID}',
    'text': msg
}))
")

RESPONSE=$(curl -sf -X POST "${N8N_WEBHOOK}" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}" 2>&1 || echo "FAILED")

echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Health digest sent. Response: ${RESPONSE}"

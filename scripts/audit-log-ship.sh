#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# audit-log-ship.sh -- Collect, format, hash-chain, and upload audit logs
#
# Runs every 6 hours via cron. Collects logs from security-relevant containers,
# formats as RFC 5424 with JSON structured data, computes a SHA-256 hash chain,
# and uploads to DO Spaces (cd-audit-logs bucket).
###############################################################################

HOSTNAME="cd-alpha"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_PATH=$(date -u +"%Y/%m/%d")
BATCH_ID="$(date -u +%Y%m%d%H%M%S)-$(shuf -i 100-999 -n1)"
WORK_DIR=$(mktemp -d /tmp/audit-ship.XXXXXX)
SPACES_BUCKET="s3://cd-audit-logs"
CHAIN_DIR="/root/COREDIRECTIVE_ENGINE/CD_BACKUPS/audit-chain"
CHAIN_FILE="${CHAIN_DIR}/latest-hash.txt"
LOG_FILE="${WORK_DIR}/audit-${BATCH_ID}.log"
MANIFEST_FILE="${WORK_DIR}/manifest-${BATCH_ID}.json"

# RFC 5424 facility=local0 (16), severity=informational (6) => priority = 16*8+6 = 134
PRI=134

# Ensure chain directory exists
mkdir -p "${CHAIN_DIR}"

# Cleanup on exit
cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

echo "[$(date -u +%H:%M:%S)] Audit log shipping started -- batch ${BATCH_ID}"

###############################################################################
# Collect container logs (last 6 hours)
###############################################################################

CONTAINERS=(
    "cd-service-db"
    "cd-service-n8n"
    "cd-service-vault"
    "cd-service-keycloak"
    "cd-service-falco"
    "tunnel-cyber-squire"
)

for CTR in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${CTR}$"; then
        docker logs --since 6h "${CTR}" 2>&1 | while IFS= read -r line; do
            # Skip empty lines
            [ -z "${line}" ] && continue
            # RFC 5424: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID [SD] MSG
            printf '<%d>1 %s %s %s - - [audit@51369 container="%s"] %s\n' \
                "${PRI}" "${TIMESTAMP}" "${HOSTNAME}" "${CTR}" "${CTR}" "${line}"
        done >> "${LOG_FILE}"
    else
        printf '<%d>1 %s %s audit-ship - - [audit@51369 container="%s"] WARN: container not running, skipped\n' \
            "${PRI}" "${TIMESTAMP}" "${HOSTNAME}" "${CTR}" >> "${LOG_FILE}"
    fi
done

# Collect host auth.log entries from last 6 hours
if [ -f /var/log/auth.log ]; then
    CUTOFF=$(date -u -d '6 hours ago' +"%Y-%m-%dT%H:%M:%S" 2>/dev/null || date -u --date='6 hours ago' +"%Y-%m-%dT%H:%M:%S" 2>/dev/null || echo "")
    if [ -n "${CUTOFF}" ]; then
        # auth.log uses "Mon DD HH:MM:SS" format -- grab recent lines by checking timestamps
        # Simpler: just grab lines from last 6 hours using awk on syslog timestamp
        SIX_HOURS_AGO=$(date -d '6 hours ago' +"%b %e %H:%M:%S" 2>/dev/null || echo "")
        if [ -n "${SIX_HOURS_AGO}" ]; then
            awk -v cutoff="${SIX_HOURS_AGO}" '$0 >= cutoff' /var/log/auth.log 2>/dev/null | while IFS= read -r line; do
                [ -z "${line}" ] && continue
                printf '<%d>1 %s %s auth.log - - [audit@51369 source="host"] %s\n' \
                    "${PRI}" "${TIMESTAMP}" "${HOSTNAME}" "${line}"
            done >> "${LOG_FILE}"
        else
            # Fallback: tail last 500 lines (covers ~6h on typical host)
            tail -500 /var/log/auth.log 2>/dev/null | while IFS= read -r line; do
                [ -z "${line}" ] && continue
                printf '<%d>1 %s %s auth.log - - [audit@51369 source="host"] %s\n' \
                    "${PRI}" "${TIMESTAMP}" "${HOSTNAME}" "${line}"
            done >> "${LOG_FILE}"
        fi
    fi
fi

# If no logs collected, create a heartbeat entry
if [ ! -s "${LOG_FILE}" ]; then
    printf '<%d>1 %s %s audit-ship - - [audit@51369 type="heartbeat"] No log entries collected this period\n' \
        "${PRI}" "${TIMESTAMP}" "${HOSTNAME}" > "${LOG_FILE}"
fi

EVENT_COUNT=$(wc -l < "${LOG_FILE}")
SIZE_BYTES=$(stat -c %s "${LOG_FILE}" 2>/dev/null || stat -f %z "${LOG_FILE}" 2>/dev/null || echo 0)

echo "[$(date -u +%H:%M:%S)] Collected ${EVENT_COUNT} events (${SIZE_BYTES} bytes)"

###############################################################################
# Hash chain computation
###############################################################################

# Read previous hash (or GENESIS for first batch)
if [ -f "${CHAIN_FILE}" ]; then
    PREVIOUS_HASH=$(cat "${CHAIN_FILE}")
else
    PREVIOUS_HASH="GENESIS"
fi

# CONTENT_HASH = SHA256 of the log file
CONTENT_HASH=$(sha256sum "${LOG_FILE}" | awk '{print $1}')

# CHAIN_HASH = SHA256 of (CONTENT_HASH + PREVIOUS_HASH)
CHAIN_HASH=$(printf '%s%s' "${CONTENT_HASH}" "${PREVIOUS_HASH}" | sha256sum | awk '{print $1}')

echo "[$(date -u +%H:%M:%S)] Hash chain: content=${CONTENT_HASH:0:16}... chain=${CHAIN_HASH:0:16}... prev=${PREVIOUS_HASH:0:16}..."

###############################################################################
# Write manifest
###############################################################################

cat > "${MANIFEST_FILE}" <<MANIFEST
{
  "batch_id": "${BATCH_ID}",
  "timestamp": "${TIMESTAMP}",
  "log_file": "audit-${BATCH_ID}.log",
  "sha256_content": "${CONTENT_HASH}",
  "sha256_chain": "${CHAIN_HASH}",
  "previous_hash": "${PREVIOUS_HASH}",
  "event_count": ${EVENT_COUNT},
  "size_bytes": ${SIZE_BYTES},
  "hostname": "${HOSTNAME}",
  "containers": ["cd-service-db","cd-service-n8n","cd-service-vault","cd-service-keycloak","cd-service-falco","tunnel-cyber-squire"],
  "includes_host_auth": true
}
MANIFEST

###############################################################################
# Upload to DO Spaces
###############################################################################

REMOTE_LOG="${SPACES_BUCKET}/${DATE_PATH}/audit-${BATCH_ID}.log"
REMOTE_MANIFEST="${SPACES_BUCKET}/${DATE_PATH}/manifest-${BATCH_ID}.json"

s3cmd put "${LOG_FILE}" "${REMOTE_LOG}" --no-progress
s3cmd put "${MANIFEST_FILE}" "${REMOTE_MANIFEST}" --no-progress

echo "[$(date -u +%H:%M:%S)] Uploaded to ${SPACES_BUCKET}/${DATE_PATH}/"

###############################################################################
# Update chain file
###############################################################################

echo "${CHAIN_HASH}" > "${CHAIN_FILE}"

echo "[$(date -u +%H:%M:%S)] Audit log shipping complete -- batch ${BATCH_ID}"

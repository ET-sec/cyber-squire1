#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# audit-log-verify.sh -- Weekly hash chain integrity verification
#
# Downloads all manifests from DO Spaces for the past 90 days, sorts by
# timestamp, recomputes the hash chain, and alerts via Telegram if any
# mismatch is found.
###############################################################################

SPACES_BUCKET="s3://cd-audit-logs"
WORK_DIR=$(mktemp -d /tmp/audit-verify.XXXXXX)
CHAIN_DIR="/root/COREDIRECTIVE_ENGINE/CD_BACKUPS/audit-chain"
N8N_WEBHOOK="https://n8n.tigouetheory.com/webhook/master-cmd"
CHAT_ID="6691629392"

cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

echo "[$(date -u +%H:%M:%S)] Audit log verification started"

###############################################################################
# Download manifests for last 90 days
###############################################################################

MANIFEST_DIR="${WORK_DIR}/manifests"
mkdir -p "${MANIFEST_DIR}"

# Generate date paths for the last 90 days
MANIFEST_COUNT=0
for i in $(seq 0 89); do
    DAY=$(date -u -d "${i} days ago" +"%Y/%m/%d" 2>/dev/null || date -u -v-${i}d +"%Y/%m/%d" 2>/dev/null || continue)
    # Download manifests for this day (ignore errors for days with no data)
    s3cmd get "${SPACES_BUCKET}/${DAY}/manifest-*.json" "${MANIFEST_DIR}/" --no-progress 2>/dev/null || true
done

# Count downloaded manifests
MANIFEST_COUNT=$(find "${MANIFEST_DIR}" -name 'manifest-*.json' -type f 2>/dev/null | wc -l)

if [ "${MANIFEST_COUNT}" -eq 0 ]; then
    echo "[$(date -u +%H:%M:%S)] No manifests found in the last 90 days. Nothing to verify."
    exit 0
fi

echo "[$(date -u +%H:%M:%S)] Downloaded ${MANIFEST_COUNT} manifests"

###############################################################################
# Sort manifests by timestamp and verify hash chain
###############################################################################

# Extract timestamp and filename, sort chronologically
SORTED_MANIFESTS=$(for f in "${MANIFEST_DIR}"/manifest-*.json; do
    TS=$(grep -o '"timestamp"[[:space:]]*:[[:space:]]*"[^"]*"' "$f" | head -1 | sed 's/.*"timestamp"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    echo "${TS} ${f}"
done | sort -k1)

VERIFIED=0
MISMATCHES=0
EXPECTED_PREV="GENESIS"
BROKEN_BATCH=""

while IFS= read -r entry; do
    [ -z "${entry}" ] && continue
    MFILE=$(echo "${entry}" | awk '{print $2}')

    # Parse manifest fields
    BATCH_ID=$(grep -o '"batch_id"[[:space:]]*:[[:space:]]*"[^"]*"' "${MFILE}" | sed 's/.*"\([^"]*\)"$/\1/')
    CONTENT_HASH=$(grep -o '"sha256_content"[[:space:]]*:[[:space:]]*"[^"]*"' "${MFILE}" | sed 's/.*"\([^"]*\)"$/\1/')
    CHAIN_HASH=$(grep -o '"sha256_chain"[[:space:]]*:[[:space:]]*"[^"]*"' "${MFILE}" | sed 's/.*"\([^"]*\)"$/\1/')
    PREV_HASH=$(grep -o '"previous_hash"[[:space:]]*:[[:space:]]*"[^"]*"' "${MFILE}" | sed 's/.*"\([^"]*\)"$/\1/')

    # Verify previous_hash matches expected
    if [ "${PREV_HASH}" != "${EXPECTED_PREV}" ]; then
        echo "[MISMATCH] Batch ${BATCH_ID}: previous_hash=${PREV_HASH:0:16}... expected=${EXPECTED_PREV:0:16}..."
        MISMATCHES=$((MISMATCHES + 1))
        if [ -z "${BROKEN_BATCH}" ]; then
            BROKEN_BATCH="${BATCH_ID}"
        fi
    fi

    # Recompute chain hash: SHA256(content_hash + previous_hash_from_manifest)
    RECOMPUTED=$(printf '%s%s' "${CONTENT_HASH}" "${PREV_HASH}" | sha256sum | awk '{print $1}')
    if [ "${RECOMPUTED}" != "${CHAIN_HASH}" ]; then
        echo "[MISMATCH] Batch ${BATCH_ID}: chain hash mismatch -- recorded=${CHAIN_HASH:0:16}... computed=${RECOMPUTED:0:16}..."
        MISMATCHES=$((MISMATCHES + 1))
        if [ -z "${BROKEN_BATCH}" ]; then
            BROKEN_BATCH="${BATCH_ID}"
        fi
    fi

    EXPECTED_PREV="${CHAIN_HASH}"
    VERIFIED=$((VERIFIED + 1))
done <<< "${SORTED_MANIFESTS}"

###############################################################################
# Report results
###############################################################################

echo "[$(date -u +%H:%M:%S)] Verification complete: ${VERIFIED} batches verified, ${MISMATCHES} mismatches"

if [ "${MISMATCHES}" -gt 0 ]; then
    echo "[ALERT] Hash chain integrity failure detected!"

    # Send Telegram alert via n8n master-cmd webhook
    ALERT_MSG="AUDIT LOG INTEGRITY FAILURE: Hash chain broken at batch ${BROKEN_BATCH}. ${MISMATCHES} mismatch(es) in ${VERIFIED} batches. Investigate immediately."

    curl -s -X POST "${N8N_WEBHOOK}" \
        -H "Content-Type: application/json" \
        -d "{\"action\": \"telegram\", \"chat_id\": \"${CHAT_ID}\", \"text\": \"${ALERT_MSG}\"}" \
        --max-time 10 || echo "WARN: Failed to send Telegram alert"

    exit 1
else
    echo "[OK] All ${VERIFIED} batches passed hash chain verification"
fi

#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# audit-log-cleanup.sh -- 90-day retention enforcement for audit logs
#
# Runs monthly (1st of month). Lists all objects in the cd-audit-logs bucket,
# deletes anything older than 90 days, and logs what was removed.
#
# NOTE: Google Drive archival is deferred (OAuth not connected). Logs older
# than 90 days are deleted with a log note that archival is pending.
###############################################################################

SPACES_BUCKET="s3://${AUDIT_LOGS_BUCKET:-cd-audit-logs}"
WORK_DIR=$(mktemp -d /tmp/audit-cleanup.XXXXXX)
RETENTION_DAYS=90

cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

echo "[$(date -u +%H:%M:%S)] Audit log cleanup started (retention: ${RETENTION_DAYS} days)"

###############################################################################
# Calculate cutoff date
###############################################################################

CUTOFF_DATE=$(date -u -d "${RETENTION_DAYS} days ago" +"%Y-%m-%d" 2>/dev/null \
    || date -u -v-${RETENTION_DAYS}d +"%Y-%m-%d" 2>/dev/null)

if [ -z "${CUTOFF_DATE}" ]; then
    echo "ERROR: Could not compute cutoff date"
    exit 1
fi

echo "[$(date -u +%H:%M:%S)] Cutoff date: ${CUTOFF_DATE} (deleting objects before this)"

###############################################################################
# List all objects and identify expired ones
###############################################################################

OBJECT_LIST="${WORK_DIR}/objects.txt"
DELETE_LIST="${WORK_DIR}/delete.txt"

s3cmd ls "${SPACES_BUCKET}/" --recursive > "${OBJECT_LIST}" 2>/dev/null || true

TOTAL_OBJECTS=$(wc -l < "${OBJECT_LIST}")
echo "[$(date -u +%H:%M:%S)] Total objects in bucket: ${TOTAL_OBJECTS}"

# s3cmd ls format: "2026-03-11 06:00    12345   s3://cd-audit-logs/2026/03/11/audit-xxx.log"
# Extract date and path, compare against cutoff
DELETED_COUNT=0
OLDEST_DELETED=""
NEWEST_DELETED=""

while IFS= read -r line; do
    [ -z "${line}" ] && continue

    # Extract the date (first column)
    OBJ_DATE=$(echo "${line}" | awk '{print $1}')
    OBJ_PATH=$(echo "${line}" | awk '{print $NF}')

    # Skip if date is empty or malformed
    [[ "${OBJ_DATE}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || continue

    # Compare dates (string comparison works for ISO format)
    if [[ "${OBJ_DATE}" < "${CUTOFF_DATE}" ]]; then
        echo "${OBJ_PATH}" >> "${DELETE_LIST}"
        DELETED_COUNT=$((DELETED_COUNT + 1))

        # Track date range
        if [ -z "${OLDEST_DELETED}" ] || [[ "${OBJ_DATE}" < "${OLDEST_DELETED}" ]]; then
            OLDEST_DELETED="${OBJ_DATE}"
        fi
        if [ -z "${NEWEST_DELETED}" ] || [[ "${OBJ_DATE}" > "${NEWEST_DELETED}" ]]; then
            NEWEST_DELETED="${OBJ_DATE}"
        fi
    fi
done < "${OBJECT_LIST}"

###############################################################################
# Delete expired objects
###############################################################################

if [ "${DELETED_COUNT}" -eq 0 ]; then
    echo "[$(date -u +%H:%M:%S)] No objects older than ${RETENTION_DAYS} days found. Nothing to delete."
    exit 0
fi

echo "[$(date -u +%H:%M:%S)] NOTE: Google Drive archival is deferred (OAuth not connected)."
echo "[$(date -u +%H:%M:%S)] Deleting ${DELETED_COUNT} objects (${OLDEST_DELETED} to ${NEWEST_DELETED})"

while IFS= read -r obj_path; do
    [ -z "${obj_path}" ] && continue
    s3cmd del "${obj_path}" --no-progress 2>/dev/null || echo "WARN: Failed to delete ${obj_path}"
done < "${DELETE_LIST}"

echo "[$(date -u +%H:%M:%S)] Cleanup complete: deleted ${DELETED_COUNT} objects (${OLDEST_DELETED} to ${NEWEST_DELETED})"
echo "[$(date -u +%H:%M:%S)] Remaining objects: $((TOTAL_OBJECTS - DELETED_COUNT))"

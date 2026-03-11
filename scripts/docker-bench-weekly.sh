#!/usr/bin/env bash
# docker-bench-weekly.sh -- runs CIS Docker Bench scan, stores text results,
# generates diff against previous scan, and tracks pass/warn/info trend.
# Ships compliance metrics to Datadog for live dashboard widgets.
#
# Output format: Docker Bench produces text logs (not JSON).
# Each line is tagged [PASS], [WARN], [INFO], or [NOTE].
#
# Usage: /root/scripts/docker-bench-weekly.sh
# Cron:  0 6 * * 0  (every Sunday 6 AM UTC)
set -euo pipefail

TIMESTAMP=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
BENCH_DIR="/root/COREDIRECTIVE_ENGINE/CD_BACKUPS/bench"
RESULT_FILE="${BENCH_DIR}/bench-${TIMESTAMP}.log"

mkdir -p "${BENCH_DIR}"

# Capture previous scan file BEFORE running new scan
PREV_FILE=$(ls -t "${BENCH_DIR}"/bench-*.log 2>/dev/null | head -1 || true)

# Run Docker Bench for Security (CIS benchmark)
# Mount specific /etc subdirs to avoid conflict with container's /etc/resolv.conf
echo "[$(date -u)] Starting Docker Bench CIS scan..."
docker run --rm \
  --net host --pid host --userns host \
  --cap-add audit_control \
  -v /etc/default:/etc/default:ro \
  -v /etc/docker:/etc/docker:ro \
  -v /etc/passwd:/etc/passwd:ro \
  -v /etc/group:/etc/group:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v "${BENCH_DIR}:/output" \
  docker/docker-bench-security \
  -l "/output/bench-${TIMESTAMP}.log" -b 2>/dev/null || true

# Verify output exists
if [ ! -f "${RESULT_FILE}" ]; then
  echo "ERROR: Scan output not found at ${RESULT_FILE}"
  exit 1
fi

# Generate diff if previous scan exists (compare only check-result lines)
if [ -n "${PREV_FILE:-}" ] && [ -f "${PREV_FILE}" ]; then
  echo "[$(date -u)] Generating diff against $(basename "${PREV_FILE}")..."
  diff \
    <(grep -E '^\[(PASS|WARN|INFO|NOTE)\]' "${PREV_FILE}" | sort) \
    <(grep -E '^\[(PASS|WARN|INFO|NOTE)\]' "${RESULT_FILE}" | sort) \
    > "${BENCH_DIR}/diff-${TIMESTAMP}.txt" 2>/dev/null || true
fi

# Extract pass/warn/info/note counts for trending (count top-level checks only)
PASS=$(grep -c '^\[PASS\]' "${RESULT_FILE}" 2>/dev/null || echo 0)
WARN=$(grep -c '^\[WARN\]' "${RESULT_FILE}" 2>/dev/null || echo 0)
INFO=$(grep -c '^\[INFO\]' "${RESULT_FILE}" 2>/dev/null || echo 0)
NOTE=$(grep -c '^\[NOTE\]' "${RESULT_FILE}" 2>/dev/null || echo 0)

# Append to trend file for compliance posture tracking
echo "{\"timestamp\":\"${TIMESTAMP}\",\"pass\":${PASS},\"warn\":${WARN},\"info\":${INFO},\"note\":${NOTE}}" \
  >> "${BENCH_DIR}/trend.jsonl"

# Ship pass/warn/info counts to Datadog as custom metrics
DD_API_KEY="${DD_API_KEY:-$(grep DATADOG_API_KEY /root/COREDIRECTIVE_ENGINE/.env 2>/dev/null | cut -d= -f2 || true)}"
if [ -n "${DD_API_KEY:-}" ]; then
  DD_NOW=$(date +%s)
  curl -s -X POST "https://api.us5.datadoghq.com/api/v2/series" \
    -H "DD-API-KEY: ${DD_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"series\": [
        {\"metric\": \"cis.docker_bench.pass\", \"type\": 1, \"points\": [{\"timestamp\": ${DD_NOW}, \"value\": ${PASS}}], \"tags\": [\"env:production\", \"host:cd-alpha-engine\", \"source:docker-bench\"]},
        {\"metric\": \"cis.docker_bench.warn\", \"type\": 1, \"points\": [{\"timestamp\": ${DD_NOW}, \"value\": ${WARN}}], \"tags\": [\"env:production\", \"host:cd-alpha-engine\", \"source:docker-bench\"]},
        {\"metric\": \"cis.docker_bench.info\", \"type\": 1, \"points\": [{\"timestamp\": ${DD_NOW}, \"value\": ${INFO}}], \"tags\": [\"env:production\", \"host:cd-alpha-engine\", \"source:docker-bench\"]}
      ]
    }" > /dev/null 2>&1 || echo "WARNING: Failed to ship metrics to Datadog (non-fatal)"
else
  echo "WARNING: DD_API_KEY not found, skipping Datadog metric submission"
fi

echo "[$(date -u)] Docker Bench scan complete: PASS=${PASS} WARN=${WARN} INFO=${INFO} NOTE=${NOTE}"
echo "Results: ${RESULT_FILE}"

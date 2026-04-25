#!/usr/bin/env bash
# Plan 19-06 Task 1: local pre-commit helper for OPA frontmatter policies.
# Builds the frontmatter index, then runs conftest with the soft-fail toggle.
# SOFT_FAIL=true (default) emits warn[] only; SOFT_FAIL=false enforces deny[].
set -euo pipefail

cd "$(dirname "$0")/../.."

python3 scripts/grc/frontmatter_to_yaml.py

SOFT_FAIL="${SOFT_FAIL:-true}"

CONFIG_FILE="$(mktemp -t grc_policy_config.XXXXXX.yaml)"
trap 'rm -f "$CONFIG_FILE"' EXIT

cat > "$CONFIG_FILE" <<EOF
config:
  soft_fail: $SOFT_FAIL
EOF

conftest test build/grc-frontmatter.yaml \
  --policy policies/grc/ \
  --data "$CONFIG_FILE"

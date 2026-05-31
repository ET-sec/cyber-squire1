#!/usr/bin/env bash
# verify_agent_signatures.sh
#
# Local-runnable verifier for Agent Card Sigstore bundles. Same logic as the
# agent-verify.yml CI job so contributors can shift-left before opening a PR.
#
# Usage:
#   bash scripts/grc/verify_agent_signatures.sh [--cards-dir <path>]
#   bash scripts/grc/verify_agent_signatures.sh --help
#
# Default cards-dir is .agents. For each <name>.card.json the script expects a
# sibling <name>.card.json.sigstore.json bundle and runs cosign verify-blob
# with --new-bundle-format pinned to the agent-signing.yml workflow identity.
#
# Exit codes:
#   0 every card has a valid signature
#   1 one or more cards are unsigned or have an invalid signature
#   2 invalid usage or missing cosign binary
#
# Requirements:
#   cosign v2.6.0 or newer (for --new-bundle-format support)
#   Cosign v2.x keyless verification is default; no legacy env var required.

set -euo pipefail

CARDS_DIR=".agents"
IDENTITY_REGEXP='https://github\.com/ET-sec/cyber-squire1/\.github/workflows/agent-signing\.yml@refs/heads/main'
OIDC_ISSUER='https://token.actions.githubusercontent.com'

usage() {
  cat <<EOF
Usage: $0 [--cards-dir <path>]

Verify Sigstore bundles for every Agent Card in <path> (default: .agents).

Options:
  --cards-dir <path>  Directory containing *.card.json files (default: .agents)
  -h, --help          Show this help and exit
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cards-dir)
      CARDS_DIR="${2:?--cards-dir requires a path}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v cosign >/dev/null 2>&1; then
  echo "ERROR: cosign binary not found on PATH. Install cosign v2.6.0 or newer." >&2
  exit 2
fi

if [[ ! -d "${CARDS_DIR}" ]]; then
  echo "ERROR: cards directory '${CARDS_DIR}' does not exist." >&2
  exit 2
fi

shopt -s nullglob
cards=("${CARDS_DIR}"/*.card.json)
shopt -u nullglob

if [[ ${#cards[@]} -eq 0 ]]; then
  echo "ERROR: no *.card.json files found under ${CARDS_DIR}." >&2
  exit 1
fi

verified=0
failed=()

for card in "${cards[@]}"; do
  bundle="${card}.sigstore.json"
  if [[ ! -f "${bundle}" ]]; then
    echo "FAIL ${card}: missing bundle ${bundle}"
    failed+=("${card}")
    continue
  fi

  if cosign verify-blob \
      --bundle "${bundle}" \
      --new-bundle-format \
      --certificate-identity-regexp "${IDENTITY_REGEXP}" \
      --certificate-oidc-issuer "${OIDC_ISSUER}" \
      "${card}" >/dev/null 2>&1; then
    echo "OK   ${card}"
    verified=$((verified + 1))
  else
    echo "FAIL ${card}: cosign verify-blob rejected signature"
    failed+=("${card}")
  fi
done

echo ""
echo "Verified ${verified} of ${#cards[@]} Agent Card signatures."

if [[ ${#failed[@]} -gt 0 ]]; then
  echo "Failures:"
  for f in "${failed[@]}"; do
    echo "  - ${f}"
  done
  exit 1
fi

echo "All ${verified} signatures verified."
exit 0

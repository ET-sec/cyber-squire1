#!/usr/bin/env bash
# OPA Policy Check for Terraform plans via conftest
# Used by pre-commit hook to validate .rego policy changes
set -euo pipefail

cd terraform/cd-do-infrastructure

if [ -f plan.json ]; then
  conftest test plan.json --policy policy/ --no-color
else
  echo "No plan.json found. Generate one with:"
  echo "  cd terraform/cd-do-infrastructure"
  echo "  doppler run -- terraform plan -out=tfplan.binary -input=false"
  echo "  terraform show -json tfplan.binary > plan.json"
fi

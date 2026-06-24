#!/usr/bin/env bash
# new-branch.sh: Start a clean branch off the latest main.
#
# Usage:
#   ./scripts/git/new-branch.sh <branch-name>
#
# Examples:
#   ./scripts/git/new-branch.sh feat/gta-milestone-2-pipeline
#   ./scripts/git/new-branch.sh fix/grc-embedding-provider-drift
#   ./scripts/git/new-branch.sh gta/grc-2026-06-24

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "usage: $0 <branch-name>" >&2
  echo "branch-name should follow: <type>/<short-description>" >&2
  echo "valid types: feat fix docs chore security refactor gta infra ci test hotfix wip" >&2
  exit 1
fi

BRANCH="$1"

# Validate prefix
case "$BRANCH" in
  feat/*|fix/*|docs/*|chore/*|security/*|refactor/*|gta/*|infra/*|ci/*|test/*|hotfix/*|wip/*)
    ;;
  *)
    echo "error: branch name must start with one of: feat/ fix/ docs/ chore/ security/ refactor/ gta/ infra/ ci/ test/ hotfix/ wip/" >&2
    exit 1
    ;;
esac

# Confirm we are on main and clean enough to switch
CURRENT=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT" != "main" ]; then
  echo "warning: currently on '$CURRENT', not main"
  read -p "switch to main first? [Y/n] " yn
  if [ "$yn" != "n" ] && [ "$yn" != "N" ]; then
    git checkout main
  fi
fi

# Pull latest main
echo "pulling latest main..."
git pull --rebase origin main

# Create branch
echo "creating branch: $BRANCH"
git checkout -b "$BRANCH"

echo ""
echo "ready. branch: $BRANCH"
echo "when done, run: ./scripts/git/ship-pr.sh"

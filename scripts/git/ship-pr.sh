#!/usr/bin/env bash
# ship-pr.sh: Push current branch and open a PR with templated body.
#
# Usage:
#   ./scripts/git/ship-pr.sh                       # interactive
#   ./scripts/git/ship-pr.sh "title here"          # title-only
#
# Requires: gh CLI authenticated

set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" = "main" ]; then
  echo "error: cannot ship PR from main. switch to a feature branch first." >&2
  echo "use: ./scripts/git/new-branch.sh <branch-name>" >&2
  exit 1
fi

# Ensure there are commits ahead of main
COMMITS_AHEAD=$(git rev-list --count main..HEAD 2>/dev/null || echo 0)
if [ "$COMMITS_AHEAD" -eq 0 ]; then
  echo "error: no commits ahead of main on '$BRANCH'. commit your work first." >&2
  exit 1
fi

# Push branch with upstream tracking
echo "pushing branch '$BRANCH'..."
git push -u origin "$BRANCH"

# Derive default title from branch type and first commit subject
PREFIX=$(echo "$BRANCH" | cut -d/ -f1)
SUBJECT=$(git log -1 --pretty=%s)
DEFAULT_TITLE="$SUBJECT"

# Use provided title or prompt
if [ $# -ge 1 ]; then
  TITLE="$1"
else
  echo ""
  echo "default PR title: $DEFAULT_TITLE"
  read -p "use default? [Y/n] " yn
  if [ "$yn" = "n" ] || [ "$yn" = "N" ]; then
    read -p "enter title: " TITLE
  else
    TITLE="$DEFAULT_TITLE"
  fi
fi

# Open PR using the repo template
echo ""
echo "opening PR..."
gh pr create \
  --base main \
  --head "$BRANCH" \
  --title "$TITLE" \
  --body-file .github/pull_request_template.md

PR_URL=$(gh pr view --json url -q .url)

echo ""
echo "PR opened: $PR_URL"
echo ""
echo "next steps:"
echo "  1. edit PR body to fill in Summary, Test plan, Notes"
echo "  2. wait for CI to go green"
echo "  3. self-review the diff: gh pr view --web"
echo "  4. squash merge: gh pr merge --squash --delete-branch"

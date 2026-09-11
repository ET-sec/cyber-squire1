#!/usr/bin/env bash
# check_authorship.sh: verify who wrote each commit.
#
# Every commit's author, committer, and any co-author must be an approved
# identity. Anything else is blocked. Fail-closed: an unapproved identity, or no
# configured list at all, stops the commit or push. This is an identity gate,
# not a keyword filter: it does not name or single out any one tool, it simply
# refuses anyone who is not on the approved list.
#
# One rule, three layers:
#   - .githooks/commit-msg  (at commit time)
#   - .githooks/pre-push    (the commits being pushed)
#   - .github/workflows/authorship-guard.yml  (required check on main)
#
# The approved list is data, not code, and carries no address in the tracked
# tree (the repo forbids PII in source):
#   - CD_AUTHORS_OK  env, space or newline separated (CI sets it from the
#     AUTHORSHIP_ALLOW repository variable), and/or
#   - .githooks/authors.allow  gitignored, one address per line.
# Two public GitHub no-reply addresses are always allowed as committers so the
# web merge button and Actions commits pass.
#
# Usage:
#   check_authorship.sh <range...>   e.g. origin/main..HEAD, or  <sha> --not --remotes
#   check_authorship.sh              no arg: every local commit not on a remote
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
# Public, non-PII identities always permitted as committer (GitHub web merge and
# this repo's Actions runner). Not enough on their own to author.
PUBLIC_OK="157398893+ET-sec@users.noreply.github.com noreply@github.com"

approved=""
[ -n "${CD_AUTHORS_OK:-}" ] && approved="$approved $CD_AUTHORS_OK"
if [ -f "$REPO_ROOT/.githooks/authors.allow" ]; then
  approved="$approved $(grep -vE '^[[:space:]]*(#|$)' "$REPO_ROOT/.githooks/authors.allow" | tr '\n' ' ')"
fi
approved="$(printf '%s' "$approved" | tr -s ' ')"

if [ -z "$(printf '%s' "$approved" | tr -d ' ')" ]; then
  echo "authorship: BLOCKED. No approved-author list is configured."
  echo "Set CD_AUTHORS_OK, or create .githooks/authors.allow (one address per line)."
  exit 1
fi

AUTHORS_OK="$approved"                 # who may author or co-author
COMMITTERS_OK="$approved $PUBLIC_OK"   # who may commit

if [ "$#" -gt 0 ]; then
  commits=$(git rev-list "$@" 2>/dev/null || true)
else
  commits=$(git rev-list --branches --not --remotes 2>/dev/null || true)
fi

if [ -z "$commits" ]; then
  echo "authorship: no commits in range, nothing to check."
  exit 0
fi

in_list() { case " $2 " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

fail=0
n=0
while IFS= read -r c; do
  [ -z "$c" ] && continue
  n=$((n + 1))
  ae=$(git show -s --format='%ae' "$c")
  ce=$(git show -s --format='%ce' "$c")
  an=$(git show -s --format='%an' "$c")
  cn=$(git show -s --format='%cn' "$c")
  short=$(git show -s --format='%h %s' "$c")

  if ! in_list "$ae" "$AUTHORS_OK"; then
    echo "BLOCKED $short"; echo "  author not approved: $an <$ae>"; fail=1
  fi
  if ! in_list "$ce" "$COMMITTERS_OK"; then
    echo "BLOCKED $short"; echo "  committer not approved: $cn <$ce>"; fail=1
  fi
  coauth=$(git show -s --format='%B' "$c" | grep -iE '^co-authored-by:' | sed -E 's/.*<([^>]+)>.*/\1/' || true)
  while IFS= read -r em; do
    [ -z "$em" ] && continue
    if ! in_list "$em" "$AUTHORS_OK"; then
      echo "BLOCKED $short"; echo "  co-author not approved: <$em>"; fail=1
    fi
  done <<EOF
$coauth
EOF
done <<EOF
$commits
EOF

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "authorship gate FAILED (fail-closed). Every commit must be authored,"
  echo "committed, and co-authored by an approved identity. Fix the commit:"
  echo "  git commit --amend --reset-author        (wrong author on the tip)"
  echo "  git rebase -i <base>                      (an identity deeper in history)"
  echo "or add a genuinely approved contributor to the list. Do not bypass."
  exit 1
fi

echo "authorship: clean over $n commit(s), all approved identities."
exit 0

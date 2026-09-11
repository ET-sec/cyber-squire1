#!/usr/bin/env bash
# check_authorship.sh: fail-closed authorship gate for this repository.
#
# The maintainer is the sole contributor and intends to stay so. A tool that
# adds a Co-Authored-By or session trailer, or a workflow that commits as a bot,
# is the only thing that ever put another name on the contributor graph. This
# refuses those, at three layers that share one rule:
#   - .githooks/commit-msg  (earliest, at commit time)
#   - .githooks/pre-push    (last local exit before commits go public)
#   - .github/workflows/authorship-guard.yml  (the pipeline; a --no-verify commit
#                                              is still stopped at the merge)
#
# Prevention, not detection: every check below BLOCKS, none merely warns.
#
# No personal email lives in this file (the repo forbids PII in tracked code).
# Identity is screened by DENYLIST: automated and assistant identities are
# refused, the maintainer's own address passes because it is not on the list.
# Co-authors are screened by an ALLOWLIST of the one public no-reply address,
# since the maintainer never co-authors their own commits, so any co-author line
# is by definition someone else and is blocked.
#
# Usage:
#   check_authorship.sh <range...>   e.g. origin/main..HEAD, or  <sha> --not --remotes
#   check_authorship.sh              no arg: every local commit not on a remote
#
# Widen the co-author allowlist only if a second real human ever contributes:
#   CD_COAUTHORS_OK="a@x b@y" check_authorship.sh ...
set -euo pipefail

# The only identity permitted on a Co-Authored-By line: the maintainer's public
# GitHub no-reply address. Override to add a genuine second contributor.
COAUTHORS_OK="${CD_COAUTHORS_OK:-157398893+ET-sec@users.noreply.github.com}"

# Automated / assistant identities that may never author, commit, or co-author.
# Matched case-insensitively against names, emails, and co-author lines.
DENY_RE='claude|anthropic|\[bot\]|poam-sync-bot|actions@github\.com'

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

  # 1. Author and committer identity: deny the automated set.
  if printf '%s\n%s\n%s\n%s\n' "$ae" "$ce" "$an" "$cn" | grep -qiE "$DENY_RE"; then
    echo "BLOCKED $short"
    echo "  automated identity on author/committer: $an <$ae> / $cn <$ce>"
    fail=1
  fi

  # 2. Message trailers and footers.
  msg=$(git show -s --format='%B' "$c")
  if printf '%s' "$msg" | grep -qiE '^(co-authored-by:.*(claude|anthropic)|claude-session:)'; then
    echo "BLOCKED $short"; echo "  message carries a Claude co-author or session trailer"; fail=1
  fi
  if printf '%s' "$msg" | grep -qiE 'generated with \[claude code\]'; then
    echo "BLOCKED $short"; echo "  message carries a generated-with footer"; fail=1
  fi

  # 3. Every Co-Authored-By line must be on the allowlist.
  coauth=$(printf '%s' "$msg" | grep -iE '^co-authored-by:' | sed -E 's/.*<([^>]+)>.*/\1/' || true)
  while IFS= read -r em; do
    [ -z "$em" ] && continue
    if ! in_list "$em" "$COAUTHORS_OK"; then
      echo "BLOCKED $short"; echo "  co-author not allowlisted: <$em>"; fail=1
    fi
  done <<EOF
$coauth
EOF
done <<EOF
$commits
EOF

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "authorship gate FAILED (fail-closed). Only the maintainer may author or"
  echo "co-author commits here. Fix the offending commit before pushing:"
  echo "  git commit --amend --reset-author        (fix a wrong author on the tip)"
  echo "  git rebase -i <base>                      (drop a trailer deeper in history)"
  echo "Do not bypass this gate."
  exit 1
fi

echo "authorship: clean over $n commit(s)."
exit 0

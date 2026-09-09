# Price-tier gate fixture

Deliberate gate fixture. Every `MATCH` line below carries a price-tier claim that
`check_public.py`'s `PRICE` pattern must catch. Every `CLEAR` line uses the word "free"
or a provider name in a sense that must never be caught.

This file is a seeded failure on purpose, so it is excluded from the `--repo` scope by
`REPO_SKIP_DIRS` in `scripts/site/check_public.py`. `tests/repo/test_check_public_repo_scope.py`
asserts that exclusion, so the fixture cannot turn the real gate red.

## Must match

- MATCH: The instance runs on the Always Free plan.
- MATCH: Everything here fits inside the free tier.
- MATCH: A free-tier account is enough to reproduce this.
- MATCH: Running it costs nothing.
- MATCH: The whole stack is zero cost.
- MATCH: There is no cost to keeping it up.
- MATCH: Compute bill: $0/mo.
- MATCH: Compute bill: $0 per month.

## Must not match

- CLEAR: The parser is free of side effects for the caller.
- CLEAR: The pipeline is credential-free; CI exchanges an OIDC token instead.
- CLEAR: Reviewer notes go in a free-form field.
- CLEAR: Backups run hands-free on a nightly timer.
- CLEAR: Object storage keeps Always On replication for the state bucket.
- CLEAR: The host is an Oracle Cloud Ampere A1 Flex running aarch64.
- CLEAR: The $0 row in the cost table is a measured figure, not a claim.

# Broken-link gate fixture

Deliberate gate fixture. The `BROKEN` link below points at a path that no commit has
ever carried, so the widened `check_links()` in `scripts/grc/validate_grc.py` has
something to catch. The `LIVE` links point at files git really tracks.

This file is a seeded failure on purpose, so it is excluded from the repository link
scope by `LINK_SKIP_DIRS` in `scripts/grc/validate_grc.py`, the same way
`price_tier_seed.md` is excluded from the `--repo` scope in `scripts/site/check_public.py`.
`tests/repo/test_repo_sweep.py` asserts that exclusion, so the fixture cannot turn the
real gate red.

## Must be reported

- BROKEN: [a document that does not exist](./no_such_document.md)

## Must not be reported

- LIVE: [the price-tier fixture beside it](./price_tier_seed.md)
- LIVE: [the checker that owns the price rule](../../../scripts/site/check_public.py)
- LIVE: [an external target, skipped by scheme](https://example.com/nothing)
- LIVE: [an anchor on this file, skipped by scheme](#must-be-reported)

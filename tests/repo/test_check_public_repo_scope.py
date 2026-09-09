"""Gate tests for the price-tier pattern and the --repo scope in check_public.py.

``fixtures/price_tier_seed.md`` carries one line per price-tier form that must fail and
one line per legitimate use of the word "free" that must pass. The last test proves the
fixture directory is excluded from the live ``--repo`` file list, so the seeded failures
can never turn the real gate red.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.site.check_public import PRICE, ROOT, repo_files, tracked  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "price_tier_seed.md"
PRICE_RE = PRICE[0][1]

# Every alternative in the pattern. The fixture must exercise all of them, or a future
# edit could drop one alternative and still see a green suite.
REQUIRED_FORMS = (
    "always free",
    "free tier",
    "free-tier",
    "zero cost",
    "no cost",
    "costs nothing",
    "$0/mo",
    "$0 per month",
)


def seeded(marker):
    prefix = f"- {marker}: "
    lines = [
        line[len(prefix):].strip()
        for line in FIXTURE.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    assert lines, f"fixture carries no {marker} lines"
    return lines


def test_pattern_name_is_stable():
    """The printed label is part of the contract; the phase close greps for it."""
    assert [name for name, _ in PRICE] == ["price tier"]


def test_fixture_exercises_every_alternative():
    blob = "\n".join(seeded("MATCH")).lower()
    missing = [form for form in REQUIRED_FORMS if form not in blob]
    assert not missing, f"fixture never exercises: {missing}"


def test_every_seeded_price_tier_line_matches():
    for line in seeded("MATCH"):
        assert PRICE_RE.search(line), f"price-tier pattern missed: {line!r}"


def test_every_legitimate_use_of_free_passes():
    for line in seeded("CLEAR"):
        hit = PRICE_RE.search(line)
        assert hit is None, f"false positive {hit.group(0)!r} on: {line!r}"


def test_fixture_is_tracked_but_excluded_from_the_repo_scope():
    """Assertion 3: the fixture is a real tracked file that the live gate cannot see.

    The tracked check keeps this from passing for the wrong reason. If the fixture were
    untracked, ``repo_files()`` would skip it whether or not the exclusion existed.
    """
    rel = str(FIXTURE.relative_to(ROOT))
    assert rel in tracked(), f"{rel} is not in git ls-files, so the exclusion is untested"
    scoped = {str(p.relative_to(ROOT)) for p in repo_files()}
    assert scoped, "repo scope returned no files"
    reachable = sorted(p for p in scoped if p.startswith("tests/repo/fixtures/"))
    assert not reachable, f"fixtures reachable by the live gate: {reachable}"


def test_pattern_carriers_are_excluded_from_the_repo_scope():
    """The checker and this module carry the patterns as literals to enforce them.

    Both would otherwise report themselves and inflate the price-tier debt figure that
    the phase close drives to zero.
    """
    scoped = {str(p.relative_to(ROOT)) for p in repo_files()}
    for carrier in ("scripts/site/check_public.py", str(Path(__file__).resolve().relative_to(ROOT))):
        assert carrier in tracked(), f"{carrier} is not tracked, so its exclusion is untested"
        assert carrier not in scoped, f"{carrier} is reachable by the live gate"

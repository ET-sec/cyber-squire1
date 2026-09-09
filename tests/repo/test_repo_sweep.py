"""Gate tests for scripts/repo/repo_sweep.py.

Every case runs the sweep against a throwaway git repository under ``tmp_path``,
never against this checkout, so a seeded failure can never reach the real tree
and the suite does not depend on the real tree being clean.

The two seeded strings come out of the committed fixtures rather than out of
literals here. ``fixtures/price_tier_seed.md`` owns the price-tier claim and
``fixtures/broken_link.md`` owns the dead link, so dropping a form from a
fixture shows up as a failure here instead of quietly weakening the gate. It
also keeps this file clean for the live ``--repo`` scope, which would otherwise
match a price-tier literal typed into a test.

The dash string is built here on purpose. A markdown file carrying a double
hyphen cannot be committed at all: ``.githooks/pre-commit`` blocks any staged
markdown with ``dashes=[1-9]``, which is the same rule this gate enforces.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
PRICE_FIXTURE = FIXTURES / "price_tier_seed.md"
BROKEN_FIXTURE = FIXTURES / "broken_link.md"
SWEEP = "scripts/repo/repo_sweep.py"
TELLS_SWEEP = Path.home() / ".claude" / "skills" / "gta" / "scripts" / "sweep_ai_tells.py"

# Copied into every fixture tree. The four scripts are the gates repo_sweep.py
# treats as required, plus the allow-list manifest_check.py reads and the sweep
# runner itself.
COPIED = (
    "scripts/repo/repo_sweep.py",
    "scripts/repo/manifest_check.py",
    "scripts/repo/manifest_allow_list.yaml",
    "scripts/repo/gen_folder_readmes.py",
    "scripts/site/check_public.py",
    "scripts/grc/validate_grc.py",
)

MARKER_TARGETS = (("root", "README.md"), ("docs", "docs/README.md"), ("scripts", "scripts/README.md"))


def seeded_price_claim() -> str:
    """The first MATCH line from the price-tier fixture."""
    for line in PRICE_FIXTURE.read_text(encoding="utf-8").splitlines():
        if line.startswith("- MATCH: "):
            return line[len("- MATCH: "):].strip()
    raise AssertionError(f"{PRICE_FIXTURE} carries no MATCH line")


def seeded_broken_target() -> str:
    """The target of the BROKEN link in the broken-link fixture."""
    for line in BROKEN_FIXTURE.read_text(encoding="utf-8").splitlines():
        if line.startswith("- BROKEN: "):
            return re.search(r"\]\(([^)]+)\)", line).group(1)
    raise AssertionError(f"{BROKEN_FIXTURE} carries no BROKEN line")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    assert proc.returncode == 0, f"git {args} failed: {proc.stderr}"
    return proc


def build_template(root: Path) -> Path:
    """A minimal repository that every gate passes on."""
    for rel in COPIED:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, dst)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "note.md").write_text(
        "# Note\n\nOne plain sentence with nothing for a gate to catch.\n",
        encoding="utf-8",
    )
    for key, rel in MARKER_TARGETS:
        (root / rel).write_text(
            f"# {key}\n\n<!-- MANIFEST:{key} -->\n<!-- /MANIFEST -->\n", encoding="utf-8"
        )
    git(root, "init", "-q")
    git(root, "config", "user.email", "fixture@example.com")
    git(root, "config", "user.name", "fixture")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "fixture tree")

    draft = subprocess.run(
        [sys.executable, str(root / "scripts/repo/manifest_check.py"), "--root", str(root), "--init"],
        capture_output=True,
        text=True,
    )
    assert draft.returncode == 0, draft.stderr
    (root / "docs" / "REPO_MANIFEST.yaml").write_text(draft.stdout, encoding="utf-8")
    git(root, "add", "docs/REPO_MANIFEST.yaml")

    filled = subprocess.run(
        [sys.executable, str(root / "scripts/repo/gen_folder_readmes.py"), "--root", str(root), "--apply"],
        capture_output=True,
        text=True,
    )
    assert filled.returncode == 0, filled.stderr
    git(root, "add", "-A")
    git(root, "commit", "-qm", "manifest and generated readme blocks")
    return root


@pytest.fixture(scope="session")
def template(tmp_path_factory) -> Path:
    return build_template(tmp_path_factory.mktemp("repo_sweep_template"))


@pytest.fixture
def repo(template: Path, tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    shutil.copytree(template, root)
    return root


def sweep(root: Path, *extra: str) -> tuple[int, list[str]]:
    proc = subprocess.run(
        [sys.executable, str(root / SWEEP), "--root", str(root), *extra],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.splitlines()


def seed(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    git(root, "add", rel)


def test_clean_fixture_tree_exits_zero(repo: Path):
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 0, "\n".join(lines)
    assert not [ln for ln in lines if ln.startswith("FAIL")], "\n".join(lines)


def test_seeded_price_tier_string_makes_the_sweep_fail(repo: Path):
    seed(repo, "docs/seed_price.md", f"# Seed\n\n{seeded_price_claim()}\n")
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 1, "\n".join(lines)
    assert "FAIL repo price tier" in lines
    assert any("docs/seed_price.md" in ln and "price tier" in ln for ln in lines), "\n".join(lines)


def test_seeded_broken_link_makes_the_sweep_fail(repo: Path):
    target = seeded_broken_target()
    seed(repo, "docs/seed_link.md", f"# Seed\n\nSee [a missing document]({target}).\n")
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 1, "\n".join(lines)
    assert "FAIL internal links" in lines
    assert any("docs/seed_link.md" in ln and target in ln for ln in lines), "\n".join(lines)


def test_a_clean_run_prints_nothing_but_skips_and_the_summary(repo: Path):
    """A sweep that prints noise is a sweep nobody reads.

    Every unavailable gate still gets its own SKIP line, because the whole point
    of this sweep is that a skipped gate is visible. Everything else on a clean
    run is the one summary line.
    """
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 0
    spoken = [ln for ln in lines if not ln.startswith("SKIP ")]
    assert len(spoken) == 1, "\n".join(lines)
    assert spoken[0].startswith("summary: ")
    assert "0 failed" in spoken[0]


def test_a_skipped_gate_is_never_counted_as_a_pass(repo: Path):
    """Reporting an unavailable gate as a pass is the failure this sweep exists
    to prevent, so both halves are asserted: the exit code stays 0, and the run
    says out loud which gates did not run."""
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 0
    summary = lines[-1]
    skipped = int(re.search(r"(\d+) skipped", summary).group(1))
    assert skipped > 0, summary
    skip_lines = [ln for ln in lines if ln.startswith("SKIP ")]
    assert len(skip_lines) == skipped
    assert any(ln.startswith("SKIP site public:") for ln in skip_lines), "\n".join(lines)

    proc = subprocess.run(
        [
            sys.executable,
            str(repo / SWEEP),
            "--root",
            str(repo),
            "--portfolio",
            str(repo / "no-portfolio-here"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    site = [g for g in payload["gates"] if g["gate"] == "site public"][0]
    assert site["status"] == "skip"
    assert site["reason"]
    assert payload["counts"]["skipped"] == skipped


@pytest.mark.skipif(not TELLS_SWEEP.is_file(), reason=f"no tells sweep at {TELLS_SWEEP}")
def test_a_dash_tell_fails_and_a_filler_phrase_only_warns(repo: Path):
    """The same split .githooks/pre-commit applies, so the sweep and the hook
    never disagree about whether a file is committable."""
    dash = "One clause " + "-" * 2 + " then another clause."
    seed(repo, "docs/seed_dash.md", f"# Seed\n\n{dash}\n")
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 1, "\n".join(lines)
    assert "FAIL writing tells" in lines
    assert any("docs/seed_dash.md" in ln and "dashes=" in ln for ln in lines), "\n".join(lines)

    git(repo, "rm", "-q", "-f", "docs/seed_dash.md")
    seed(repo, "docs/seed_filler.md", "# Seed\n\nWe leverage a robust approach.\n")
    code, lines = sweep(repo, "--portfolio", str(repo / "no-portfolio-here"))
    assert code == 0, "\n".join(lines)
    assert "warn writing tells" in lines
    assert any("docs/seed_filler.md" in ln and "ai_tells=" in ln for ln in lines), "\n".join(lines)
    assert not [ln for ln in lines if ln.startswith("FAIL")], "\n".join(lines)


def test_the_broken_link_fixture_is_tracked_but_excluded_from_the_live_scope():
    """Non-vacuous both ways: the fixture really is in the tree, and the live
    repository link scope really cannot reach it."""
    sys.path.insert(0, str(REPO_ROOT)) if str(REPO_ROOT) not in sys.path else None
    from scripts.grc.validate_grc import LINK_SKIP_DIRS, REPO, check_links, tracked_paths

    rel = str(BROKEN_FIXTURE.relative_to(REPO_ROOT))
    tracked = tracked_paths()
    assert rel in tracked, f"{rel} is not tracked, so the exclusion test proves nothing"
    assert rel.startswith(LINK_SKIP_DIRS)

    errors = check_links(REPO, tracked)
    assert not [e for e in errors if rel in e], errors

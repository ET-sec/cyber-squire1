"""Fixture tests for scripts/repo/manifest_check.py.

Every test builds a throwaway git tree under ``tmp_path`` and points the
checker at it with ``--root``, following the isolation pattern in
``tests/grc/test_inventory_scan.py``. Nothing here reads or writes
``docs/REPO_MANIFEST.yaml`` or the real allow-list, so the real gate cannot be
turned red or green by this file.

The nine cases are the three failure classes (shadow, orphan, expired review),
their passing counterparts, the most-specific-match resolution rule, and the
two configuration errors.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.repo import manifest_check  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOOD = FIXTURES / "manifest_good.yaml"
BAD = FIXTURES / "manifest_bad.yaml"

# The files manifest_good.yaml is written to cover.
TREE = {
    "README.md": "# throwaway tree\n",
    "docs/index.md": "docs entry point\n",
    "docs/grc/POAM_AUTO_FINDINGS.md": "scanner intake ledger\n",
    "scripts/run.py": "print('hello')\n",
}


def make_tree(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    """A git repository with TREE plus any extra files, all staged."""
    root = tmp_path / "tree"
    for rel, body in {**TREE, **(extra or {})}.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(root)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "add", "-A"], check=True, capture_output=True
    )
    return root


def allow_list(tmp_path: Path) -> Path:
    """An empty allow-list, so no test depends on the real one."""
    path = tmp_path / "allow.yaml"
    path.write_text(yaml.safe_dump({"known_gaps": []}), encoding="utf-8")
    return path


def base_rows() -> list[dict]:
    """Rows covering TREE, as plain dicts so a test can bend one of them."""
    return [
        {
            "path": "README.md",
            "purpose": "Front door.",
            "status": "active",
            "reason": "Fixture root file.",
            "last_verified": "2026-09-09",
            "review": {"by": "2099-01-01"},
        },
        {
            "path": "docs/**",
            "purpose": "Docs tree.",
            "status": "active",
            "reason": "Fixture glob.",
            "last_verified": "2026-09-09",
            "review": {"by": "2099-01-01"},
        },
        {
            "path": "scripts/**",
            "purpose": "Tooling tree.",
            "status": "active",
            "reason": "Fixture glob.",
            "last_verified": "2026-09-09",
            "review": {"by": "2099-01-01"},
        },
    ]


def write_manifest(tmp_path: Path, rows: list[dict], name: str = "manifest.yaml") -> Path:
    path = tmp_path / name
    path.write_text(
        yaml.safe_dump({"version": 1, "entries": rows}, sort_keys=False),
        encoding="utf-8",
    )
    return path


def check(root: Path, manifest: Path, tmp_path: Path, fmt: str = "human") -> int:
    return manifest_check.main(
        [
            "--root",
            str(root),
            "--manifest",
            str(manifest),
            "--allow-list",
            str(allow_list(tmp_path)),
            "--format",
            fmt,
        ]
    )


# 1. Clean
def test_covered_tree_exits_zero(tmp_path, capsys):
    root = make_tree(tmp_path)
    code = check(root, GOOD, tmp_path)
    out = capsys.readouterr().out
    assert code == 0, out
    assert "FAIL" not in out, out
    assert "Result: clean" in out


# 2. Shadow
def test_uncovered_path_is_a_shadow_failure(tmp_path, capsys):
    root = make_tree(tmp_path, {"notes/loose.md": "no row covers this\n"})
    code = check(root, GOOD, tmp_path)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "shadow" in out
    assert "notes/loose.md" in out


# 3. Orphan
def test_row_matching_nothing_is_an_orphan_failure(tmp_path, capsys):
    root = make_tree(tmp_path)
    rows = base_rows() + [
        {
            "path": "builds/gone/**",
            "purpose": "A tree that is not in this checkout.",
            "status": "archived",
            "reason": "Fixture dead row.",
            "last_verified": "2026-09-09",
            "review": {"by": "2099-01-01"},
        }
    ]
    code = check(root, write_manifest(tmp_path, rows), tmp_path)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "orphan" in out
    assert "builds/gone/**" in out


# 4. Expired review
def test_passed_review_date_fails(tmp_path, capsys):
    root = make_tree(tmp_path)
    rows = base_rows()
    rows[0]["review"] = {"by": "2020-01-01"}
    code = check(root, write_manifest(tmp_path, rows), tmp_path)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "review due" in out
    assert "README.md" in out

    # The relative form expires the same way: last verified long ago, short cycle.
    rows = base_rows()
    rows[1]["last_verified"] = "2020-01-01"
    rows[1]["review"] = {"every": "30d"}
    code = check(root, write_manifest(tmp_path, rows, "relative.yaml"), tmp_path)
    out = capsys.readouterr().out
    assert code == 1, out
    assert "review due" in out
    assert "every: 30d" in out


# 5. Review not yet due
def test_future_review_date_does_not_fail(tmp_path, capsys):
    root = make_tree(tmp_path)
    rows = base_rows()
    rows[0]["review"] = {"by": "2099-01-01"}
    rows[1]["last_verified"] = datetime.date.today().isoformat()
    rows[1]["review"] = {"every": "180d"}
    code = check(root, write_manifest(tmp_path, rows), tmp_path)
    out = capsys.readouterr().out
    assert code == 0, out
    assert "review due" not in out


# 6. Event triggers are deferred, never a pull request failure
def test_event_review_is_deferred_not_failed(tmp_path, capsys):
    root = make_tree(tmp_path)
    rows = base_rows()
    rows[0]["review"] = {
        "event": "aws_credits_landed",
        "flag": "TRIGGER_AWS_CREDITS",
    }
    code = check(root, write_manifest(tmp_path, rows), tmp_path, fmt="json")
    report = json.loads(capsys.readouterr().out)
    assert code == 0, report
    assert report["counts"]["deferred_events"] == 1, report
    assert report["deferred_events"][0]["path"] == "README.md"
    assert report["expired"] == []


# 7. Most-specific-match resolution
def test_specific_row_beats_the_glob_above_it(tmp_path, capsys):
    root = make_tree(tmp_path)
    code = check(root, GOOD, tmp_path)
    capsys.readouterr()
    assert code == 0

    entries = manifest_check.load_manifest(GOOD)
    winner = manifest_check.resolve("docs/grc/POAM_AUTO_FINDINGS.md", entries)
    assert winner is not None
    assert winner["purpose"] == "Machine-generated scanner intake ledger.", winner
    assert winner["path"] == "docs/grc/POAM_AUTO_FINDINGS.md"

    sibling = manifest_check.resolve("docs/index.md", entries)
    assert sibling is not None
    assert sibling["path"] == "docs/**", sibling


# 8. Unknown status
def test_unknown_status_is_a_configuration_error(tmp_path, capsys):
    root = make_tree(tmp_path)
    rows = base_rows()
    rows[0]["status"] = "retired"
    code = check(root, write_manifest(tmp_path, rows), tmp_path)
    err = capsys.readouterr().err
    assert code == 2, err
    assert "retired" in err


# 9. Malformed YAML
def test_malformed_manifest_is_a_configuration_error(tmp_path, capsys):
    root = make_tree(tmp_path)
    code = check(root, BAD, tmp_path)
    err = capsys.readouterr().err
    assert code == 2, err
    assert "not valid YAML" in err

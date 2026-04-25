"""Tests for scripts/grc/frontmatter_to_yaml.py preprocessor.

Plan 19-01 Task 2 acceptance harness. Six cases:
1. Doc with full frontmatter -> all expected keys present.
2. Doc without frontmatter -> warning logged, NOT included.
3. Doc with `P17-15` in body -> referenced_poam_ids contains `P17-15`.
4. POAM_PLAN_OF_ACTION.md fixture -> poam_ids non-empty AND _canonical_poam_ids populated.
5. Real docs/grc/ corpus -> main() exits 0 (no crashes on edge cases).
6. Real docs/grc/ corpus -> POAM_PLAN_OF_ACTION.md.poam_ids non-empty.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import frontmatter_to_yaml as f2y  # noqa: E402


@pytest.fixture
def tmp_grc(tmp_path: Path) -> Path:
    """Build a synthetic docs/grc directory for unit tests."""
    grc = tmp_path / "docs" / "grc"
    grc.mkdir(parents=True)

    # Doc with full frontmatter, body referencing P17-15.
    (grc / "FULL_DOC.md").write_text(
        "---\n"
        'title: "Full Doc"\n'
        'version: "1.0"\n'
        "classification: INTERNAL\n"
        "owner: System Owner\n"
        "last_reviewed: 2026-04-25\n"
        "residual_risk: LOW\n"
        "---\n\n"
        "Body referencing POAM-P17-15 and again P17-15 and a unique P17-99.\n"
    )

    # Doc with NO frontmatter (should be skipped with warning).
    (grc / "README.md").write_text("# Pure index, no frontmatter\n")

    # Synthetic POAM_PLAN_OF_ACTION.md with table rows.
    (grc / "POAM_PLAN_OF_ACTION.md").write_text(
        "---\n"
        'title: "Plan of Action"\n'
        'version: "1.0"\n'
        "classification: INTERNAL\n"
        "owner: System Owner\n"
        "last_reviewed: 2026-04-25\n"
        "residual_risk: MED\n"
        "---\n\n"
        "| ID | Description | Severity |\n"
        "|----|-------------|----------|\n"
        "| POAM-P17-01 | first | HIGH |\n"
        "| POAM-P17-02 | second | MED |\n"
        "| POAM-P17-15 | infra | LOW |\n"
        "\nFootnote referencing P17-01 inline.\n"
    )

    return grc


def test_full_doc_keeps_all_frontmatter_keys(tmp_grc: Path) -> None:
    index = f2y.build_index(tmp_grc)
    assert "FULL_DOC.md" in index
    entry = index["FULL_DOC.md"]
    for required in ("title", "version", "classification", "owner", "last_reviewed", "residual_risk"):
        assert required in entry, f"missing key {required} in {entry!r}"
    assert entry["version"] == "1.0"


def test_no_frontmatter_skipped_with_warning(tmp_grc: Path, capsys: pytest.CaptureFixture[str]) -> None:
    index = f2y.build_index(tmp_grc)
    assert "README.md" not in index
    captured = capsys.readouterr()
    assert "no_frontmatter" in captured.err
    assert "README.md" in captured.err


def test_referenced_poam_ids_extracted(tmp_grc: Path) -> None:
    index = f2y.build_index(tmp_grc)
    refs = index["FULL_DOC.md"]["referenced_poam_ids"]
    assert "P17-15" in refs
    assert "P17-99" in refs
    # sorted + unique invariant
    assert refs == sorted(set(refs))


def test_canonical_poam_ids_populated(tmp_grc: Path, tmp_path: Path) -> None:
    index = f2y.build_index(tmp_grc)
    assert "POAM_PLAN_OF_ACTION.md" in index
    poam_entry = index["POAM_PLAN_OF_ACTION.md"]
    assert "poam_ids" in poam_entry
    assert poam_entry["poam_ids"], "expected non-empty canonical poam_ids"
    assert {"P17-01", "P17-02", "P17-15"}.issubset(set(poam_entry["poam_ids"]))
    assert "_canonical_poam_ids" in index
    assert index["_canonical_poam_ids"] == poam_entry["poam_ids"]


def test_main_runs_on_real_corpus_without_crash(tmp_path: Path) -> None:
    real_grc = REPO_ROOT / "docs" / "grc"
    out = tmp_path / "grc-frontmatter.yaml"
    rc = f2y.main(grc_dir=real_grc, output_path=out)
    assert rc == 0
    assert out.exists()
    data = yaml.safe_load(out.read_text())
    assert isinstance(data, dict)
    md_keys = [k for k in data if not k.startswith("_")]
    assert any(k.endswith(".md") for k in md_keys)


def test_real_poam_canonical_ids_non_empty(tmp_path: Path) -> None:
    real_grc = REPO_ROOT / "docs" / "grc"
    out = tmp_path / "grc-frontmatter.yaml"
    rc = f2y.main(grc_dir=real_grc, output_path=out)
    assert rc == 0
    data = yaml.safe_load(out.read_text())
    assert "POAM_PLAN_OF_ACTION.md" in data
    poam_ids = data["POAM_PLAN_OF_ACTION.md"].get("poam_ids", [])
    assert isinstance(poam_ids, list)
    assert len(poam_ids) > 0, "expected canonical POA&M IDs from real corpus"
    assert data.get("_canonical_poam_ids") == poam_ids

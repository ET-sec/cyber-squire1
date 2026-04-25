"""Tests for the optional cosign keyless signing path in build_oscal.py.

Plan 19-05 acceptance harness. Four cases:

1. Default off: OSCAL_SIGN unset -> no `*.sigstore.json` files appear under the
   OSCAL output directory and existing JSON output is unchanged.
2. Sign mode: OSCAL_SIGN=1 with a mocked subprocess.run -> cosign is invoked
   for every emitted artifact with the correct argv (sign-blob, --bundle,
   --yes), and the bundle path is the artifact path with a .sigstore.json
   suffix appended.
3. Crash safety: OSCAL_SIGN=1 with cosign returning a non-zero exit -> the
   script exits 1 and no orphan `*.sigstore.json` file is created on disk.
4. --yes regression: every cosign call carries the `--yes` flag literally so
   future edits cannot accidentally hang CI on the cosign confirmation prompt.

All cosign-touching tests mock subprocess.run; cosign is not required on the
host running these tests.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.grc import build_oscal  # noqa: E402


def _reload_module():
    """Reload build_oscal so OUT_DIR / SCHEMA_DIR pick up the patched REPO."""
    return importlib.reload(build_oscal)


@pytest.fixture
def isolated_out_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect OUT_DIR and SCHEMA_DIR onto a temp tree.

    Using monkeypatch on module attributes (not REPO) keeps the test focused
    on the signing surface without rebuilding the schema directory.
    """
    out = tmp_path / "oscal_out"
    schema = tmp_path / "oscal_schemas"
    out.mkdir(parents=True)
    schema.mkdir(parents=True)
    monkeypatch.setattr(build_oscal, "OUT_DIR", out)
    monkeypatch.setattr(build_oscal, "SCHEMA_DIR", schema)
    # Ensure no leftover env from previous tests.
    monkeypatch.delenv("OSCAL_SIGN", raising=False)
    return out


def test_default_off_no_signing(isolated_out_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 1: OSCAL_SIGN unset -> no sigstore bundle appears anywhere."""
    monkeypatch.delenv("OSCAL_SIGN", raising=False)

    # subprocess.run should never be called in default-off mode. Patch as a
    # tripwire that fails the test if signing path is reached.
    tripwire = MagicMock(side_effect=AssertionError("cosign called in default-off mode"))
    with patch("scripts.grc.build_oscal.subprocess.run", tripwire):
        build_oscal.main()

    # Three OSCAL JSON files plus the validation summary should exist.
    json_files = sorted(p.name for p in isolated_out_dir.glob("*.oscal.json"))
    assert json_files == [
        "squire-component.oscal.json",
        "squire-poam.oscal.json",
        "squire-ssp.oscal.json",
    ]
    sigstore_files = list(isolated_out_dir.glob("*.sigstore.json"))
    assert sigstore_files == [], (
        f"default-off run produced unexpected bundles: {sigstore_files}"
    )
    tripwire.assert_not_called()


def test_sign_mode_invokes_cosign_per_artifact(
    isolated_out_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test 2: OSCAL_SIGN=1 -> cosign sign-blob called per JSON with correct args."""
    monkeypatch.setenv("OSCAL_SIGN", "1")

    fake_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0))
    with patch("scripts.grc.build_oscal.subprocess.run", fake_run):
        build_oscal.main()

    # Three OSCAL artifacts -> three cosign calls.
    assert fake_run.call_count == 3, (
        f"expected 3 cosign sign-blob calls, got {fake_run.call_count}"
    )

    expected_artifacts = {
        "squire-ssp.oscal.json",
        "squire-poam.oscal.json",
        "squire-component.oscal.json",
    }
    seen_artifacts: set[str] = set()

    for call in fake_run.call_args_list:
        argv = call.args[0]
        assert argv[0] == "cosign"
        assert argv[1] == "sign-blob"
        # argv[2] is the artifact path; argv[3] is --bundle; argv[4] is the
        # bundle path; argv[5] is --yes.
        artifact_path = Path(argv[2])
        assert artifact_path.parent == isolated_out_dir
        assert artifact_path.name in expected_artifacts
        seen_artifacts.add(artifact_path.name)

        assert "--bundle" in argv, f"missing --bundle in {argv}"
        bundle_idx = argv.index("--bundle")
        bundle_path = argv[bundle_idx + 1]
        assert bundle_path == f"{artifact_path}.sigstore.json", (
            f"bundle path {bundle_path} should be sibling of artifact "
            f"with .sigstore.json suffix"
        )

        assert "--yes" in argv, f"--yes missing in {argv}"

        # Defensive: cosign was invoked with check=True and a timeout.
        assert call.kwargs.get("check") is True
        assert call.kwargs.get("timeout") == 60

    assert seen_artifacts == expected_artifacts


def test_sign_mode_cosign_failure_exits_one_no_orphan(
    isolated_out_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test 3: cosign nonzero exit -> SystemExit(1) and no orphan bundle on disk."""
    monkeypatch.setenv("OSCAL_SIGN", "1")

    def boom(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=2, cmd=args[0])

    with patch("scripts.grc.build_oscal.subprocess.run", side_effect=boom):
        with pytest.raises(SystemExit) as exc_info:
            build_oscal.main()

    assert exc_info.value.code == 1, (
        f"expected exit code 1 on cosign failure, got {exc_info.value.code}"
    )

    # The OSCAL JSON itself may have been written before the cosign call. The
    # critical correctness property is no orphan .sigstore.json file: cosign
    # was the failure point and it never produced a bundle.
    sigstore_files = list(isolated_out_dir.glob("*.sigstore.json"))
    assert sigstore_files == [], (
        f"orphan sigstore bundles must not exist after cosign failure: "
        f"{sigstore_files}"
    )


def test_yes_flag_present_regression(
    isolated_out_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test 4: --yes is always in cosign argv. Prevents accidental CI hang."""
    monkeypatch.setenv("OSCAL_SIGN", "1")

    fake_run = MagicMock(return_value=subprocess.CompletedProcess(args=[], returncode=0))
    with patch("scripts.grc.build_oscal.subprocess.run", fake_run):
        build_oscal.main()

    assert fake_run.call_count >= 1
    for call in fake_run.call_args_list:
        argv = call.args[0]
        assert "--yes" in argv, (
            f"--yes flag missing from cosign call argv: {argv}. "
            "Without --yes, cosign prompts for confirmation and hangs CI."
        )

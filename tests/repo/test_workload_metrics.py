"""Fixture tests for compute_workload() in scripts/build_metrics.py.

Every case writes its own snapshot into ``tmp_path`` and passes the path in, so
none of them reads the live ``docs/metrics/workload.json`` and none of them goes
green or red because somebody took a new snapshot.

What these guard, in order: the shape the site reads, the arithmetic behind the
published hours figure, the phase rule that an untimed workflow contributes
zero, the lane split and the rule that a filler workflow can never add hours,
and a clone with no snapshot yet still building.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import build_metrics  # noqa: E402

EXPECTED_KEYS = {
    "events_handled_per_week",
    "operator_hours_saved_per_week",
    "window_days",
    "measured_at",
    "workflows_measured",
    "workflows_active",
}


def row(wid: str, name: str, lane: str, runs: int, minutes: int = 0, timed=None) -> dict:
    return {
        "id": wid,
        "name": name,
        "lane": lane,
        "runs": runs,
        "minutes_manual": minutes,
        "timed_on": timed,
    }


def snapshot(rows: list[dict], **overrides) -> dict:
    """A snapshot that agrees with its own rows unless a test bends it."""
    events = sum(r["runs"] for r in rows)
    by_lane = {"coredirective": 0, "empire": 0, "filler": 0}
    for r in rows:
        by_lane[r["lane"]] += r["runs"]
    minutes = sum(r["runs"] * r["minutes_manual"] for r in rows)
    hours = round(minutes / 60, 1)
    data = {
        "measured_at": "2026-09-10",
        "window_days": 7,
        "events_handled_per_week": events,
        "operator_hours_saved_per_week": int(hours) if float(hours).is_integer() else hours,
        "workflows_measured": sum(1 for r in rows if r["runs"] > 0),
        "workflows_active": len(rows),
        "counts_cli_runs": True,
        "events_by_lane": by_lane,
        "workflows": rows,
    }
    data.update(overrides)
    return data


def write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "workload.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def test_complete_snapshot_returns_exactly_the_six_keys(tmp_path):
    path = write(
        tmp_path,
        snapshot(
            [
                row("aaa", "Supervisor", "coredirective", 5, 4, "2026-09-10"),
                row("bbb", "Health Check", "coredirective", 2),
                row("ccc", "Old Pipeline", "filler", 1),
            ]
        ),
    )
    got = build_metrics.compute_workload(path)
    assert set(got) == EXPECTED_KEYS
    assert got["events_handled_per_week"] == 8
    assert got["window_days"] == 7
    assert got["measured_at"] == "2026-09-10"
    assert got["workflows_measured"] == 3
    assert got["workflows_active"] == 3


def test_hours_are_summed_rounded_and_whole_values_stay_int(tmp_path):
    rows = [
        row("aaa", "Three at twenty", "coredirective", 3, 20, "2026-09-10"),
        row("bbb", "One at fifteen", "empire", 1, 15, "2026-09-10"),
    ]
    got = build_metrics.compute_workload(write(tmp_path, snapshot(rows)))
    assert got["operator_hours_saved_per_week"] == 1.2

    rows[1]["minutes_manual"] = 0
    whole = build_metrics.compute_workload(write(tmp_path, snapshot(rows)))
    assert whole["operator_hours_saved_per_week"] == 1
    assert isinstance(whole["operator_hours_saved_per_week"], int)


def test_untimed_workflows_contribute_zero_hours(tmp_path):
    rows = [
        row("aaa", "Never timed", "coredirective", 9),
        row("bbb", "Also never timed", "empire", 4),
    ]
    got = build_metrics.compute_workload(write(tmp_path, snapshot(rows)))
    assert got["operator_hours_saved_per_week"] == 0
    assert got["events_handled_per_week"] == 13


def test_lanes_are_checked_and_filler_can_never_carry_minutes(tmp_path):
    rows = [
        row("aaa", "Real work", "coredirective", 3, 10, "2026-09-10"),
        row("bbb", "Content lane", "empire", 2),
        row("ccc", "Imported once", "filler", 1),
    ]
    data = snapshot(rows)
    assert all(r["lane"] in build_metrics.WORKLOAD_LANES for r in data["workflows"])
    assert sum(data["events_by_lane"].values()) == data["events_handled_per_week"]
    result = build_metrics.compute_workload(write(tmp_path, data))
    assert result["events_handled_per_week"] == 6

    rows[2]["minutes_manual"] = 5
    with pytest.raises(ValueError, match="filler"):
        build_metrics.compute_workload(write(tmp_path, snapshot(rows)))

    rows[2]["minutes_manual"] = 0
    rows[1]["lane"] = "somebody-invented-a-lane"
    bad = snapshot([rows[0], rows[2]])
    bad["workflows"] = rows
    with pytest.raises(ValueError, match="lane"):
        build_metrics.compute_workload(write(tmp_path, bad))


def test_a_disagreeing_total_is_rejected_rather_than_published(tmp_path):
    rows = [row("aaa", "Real work", "coredirective", 3, 10, "2026-09-10")]
    with pytest.raises(ValueError, match="recompute"):
        build_metrics.compute_workload(
            write(tmp_path, snapshot(rows, operator_hours_saved_per_week=40))
        )
    with pytest.raises(ValueError, match="event total"):
        build_metrics.compute_workload(
            write(tmp_path, snapshot(rows, events_handled_per_week=99))
        )


def test_missing_snapshot_degrades_to_no_workload_section(tmp_path):
    assert build_metrics.compute_workload(tmp_path / "absent.json") == {}

    m = build_metrics.Metrics()
    m.generated_at = "2026-09-10T00:00:00+00:00"
    m.contact = {"email": "someone@example.com"}
    text = build_metrics.emit_yaml(m)
    assert "workload:" not in text
    assert "contact:" in text

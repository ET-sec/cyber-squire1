#!/usr/bin/env python3
"""workload_snapshot.py: measure the n8n automation workload into a tracked snapshot.

Run by hand. It queries the tenant zero execution table over SSH and writes
``docs/metrics/workload.json``. ``scripts/build_metrics.py`` reads that file, so
``metrics.yaml`` stays fully generated and the numbers survive execution pruning,
which deletes the rows after two weeks.

What counts as one event, from the phase context:
  one successful top level execution in the window, any trigger type.
Two exclusions keep that true:
  1. Sub-workflow runs, which carry mode ``integrated``, are not events. A tool
     called by the orchestrator is part of the command that called it.
  2. An execution of the nested workflow whose start falls inside a parent
     execution's interval is the orchestrator hop inside one bot command, so it
     is not counted a second time. A standalone orchestrator call with no parent
     around it is not nested and stays its own event.
Command line runs (mode ``cli``) are counted, because the definition says any
trigger type. ``counts_cli_runs`` records that inside the artifact.

The timing table is preserved across runs. Each row carries ``minutes_manual``,
the hand timed minutes the same job takes by hand once, and ``timed_on``, the
date that figure was taken. A workflow that has never been timed carries 0 and
null, and contributes zero hours. A row in the ``filler`` lane carries 0 forever,
so filler can never inflate hours saved.

No credential crosses the wire: psql runs inside the database container over the
ssh alias, and it reads the role and the database name from the container's own
environment, so neither appears in this file or in any output.

Usage:
  python3 scripts/site/workload_snapshot.py                  # dry run, prints the object
  python3 scripts/site/workload_snapshot.py --apply          # writes the file
  python3 scripts/site/workload_snapshot.py --alias cd-oci-tunnel --apply

The default alias is ``cd-oci``. Use ``cd-oci-tunnel`` when direct SSH to the
instance is filtered from the workstation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "docs" / "metrics" / "workload.json"

DB_CONTAINER = "cd-service-db"
# The role and the database name are read from the container's environment at
# run time. Naming either one here would put an internal identifier in a public
# file, which the repository's own tripwire scan blocks.
PSQL = 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F "|" -f -'

LANES = ("coredirective", "empire", "filler")
FILLER_LANE = "filler"
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def psql(alias: str, query: str) -> list[list[str]]:
    """Run one query inside the database container over the ssh alias.

    The query travels on stdin rather than in the command line, so no quoting of
    it survives a shell hop and nothing in it can be reinterpreted as a shell
    word. String literals inside it are dollar quoted for the same reason.
    """
    if "'" in query:
        raise ValueError("query must use dollar quoting, not single quotes")
    remote = f"docker exec -i {DB_CONTAINER} sh -c '{PSQL}'"
    proc = subprocess.run(
        ["ssh", alias, remote], input=query, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"query failed over alias {alias} (exit {proc.returncode}): "
            f"{proc.stderr.strip()[:400]}"
        )
    return [
        line.split("|") for line in proc.stdout.strip().splitlines() if line
    ]


def counted_clause(
    exclude_mode: str, window_days: int, parent_id: str, nested_id: str
) -> str:
    """The WHERE clause both counting queries share, so they cannot disagree."""
    return (
        "e.status = $$success$$ "
        'AND e."deletedAt" IS NULL '
        f"AND e.mode <> $${exclude_mode}$$ "
        'AND e."stoppedAt" IS NOT NULL '
        f'AND e."stoppedAt" >= now() - interval $${window_days} days$$ '
        f'AND NOT (e."workflowId" = $${nested_id}$$ AND EXISTS ('
        "SELECT 1 FROM execution_entity s "
        f'WHERE s."workflowId" = $${parent_id}$$ '
        'AND s."deletedAt" IS NULL '
        'AND e."startedAt" >= s."startedAt" '
        'AND e."startedAt" <= s."stoppedAt"))'
    )


def query_runs(alias: str, clause: str) -> dict[str, int]:
    rows = psql(
        alias,
        "SELECT w.id, count(*) FROM execution_entity e "
        'JOIN workflow_entity w ON w.id = e."workflowId" '
        f"WHERE {clause} GROUP BY w.id",
    )
    return {r[0]: int(r[1]) for r in rows}


def query_events(alias: str, clause: str) -> int:
    rows = psql(
        alias, f"SELECT count(*) FROM execution_entity e WHERE {clause}"
    )
    return int(rows[0][0])


def query_active(alias: str) -> int:
    rows = psql(
        alias,
        "SELECT count(*) FROM workflow_entity "
        'WHERE "activeVersionId" IS NOT NULL',
    )
    return int(rows[0][0])


def query_inventory(alias: str) -> list[dict]:
    """Every workflow with its lane, read from the tag join rather than a name rule.

    A workflow tagged filler takes lane filler whatever its other tag says.
    """
    rows = psql(
        alias,
        "SELECT w.id, w.name, COALESCE("
        f"max(CASE WHEN t.name = $${FILLER_LANE}$$ THEN $${FILLER_LANE}$$ END), "
        "max(CASE WHEN t.name IN ($$coredirective$$, $$empire$$) "
        "THEN t.name END)) "
        "FROM workflow_entity w "
        'LEFT JOIN workflows_tags wt ON wt."workflowId" = w.id '
        'LEFT JOIN tag_entity t ON t.id = wt."tagId" '
        "GROUP BY w.id, w.name ORDER BY w.name",
    )
    return [{"id": r[0], "name": r[1], "lane": r[2] or ""} for r in rows]


def load_timing(path: Path) -> dict[str, dict]:
    """Carry every hand timed figure forward by workflow id."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for row in data.get("workflows", []):
        out[row["id"]] = {
            "minutes_manual": row.get("minutes_manual", 0) or 0,
            "timed_on": row.get("timed_on"),
        }
    return out


def as_hours(total_minutes: float) -> float | int:
    hours = round(total_minutes / 60, 1)
    return int(hours) if float(hours).is_integer() else hours


def build_snapshot(args: argparse.Namespace) -> dict:
    for label, value in (
        ("--parent-workflow-id", args.parent_workflow_id),
        ("--nested-workflow-id", args.nested_workflow_id),
        ("--exclude-mode", args.exclude_mode),
    ):
        if not ID_RE.match(value):
            raise SystemExit(f"{label} must be alphanumeric, got {value!r}")

    clause = counted_clause(
        args.exclude_mode,
        args.window_days,
        args.parent_workflow_id,
        args.nested_workflow_id,
    )
    runs = query_runs(args.alias, clause)
    events = query_events(args.alias, clause)
    active = query_active(args.alias)
    inventory = query_inventory(args.alias)
    timing = load_timing(args.out)

    if sum(runs.values()) != events:
        raise SystemExit(
            "the per workflow query and the events query disagree: "
            f"{sum(runs.values())} against {events}"
        )
    known = {row["id"] for row in inventory}
    orphans = sorted(set(runs) - known)
    if orphans:
        raise SystemExit(f"runs for workflows not in the inventory: {orphans}")

    workflows: list[dict] = []
    for row in inventory:
        carried = timing.get(row["id"], {})
        minutes = carried.get("minutes_manual", 0) or 0
        timed_on = carried.get("timed_on")
        if row["lane"] == FILLER_LANE and minutes:
            raise SystemExit(
                f"{row['name']} is in the filler lane and carries "
                f"minutes_manual {minutes}. Filler can never inflate hours "
                "saved. Set it back to 0 or move the workflow out of the lane."
            )
        workflows.append(
            {
                "id": row["id"],
                "name": row["name"],
                "lane": row["lane"],
                "runs": runs.get(row["id"], 0),
                "minutes_manual": minutes,
                "timed_on": timed_on,
            }
        )
    workflows.sort(key=lambda w: (-w["runs"], w["name"]))

    by_lane = {lane: 0 for lane in LANES}
    for row in workflows:
        if row["lane"] in by_lane:
            by_lane[row["lane"]] += row["runs"]

    total_minutes = sum(w["runs"] * w["minutes_manual"] for w in workflows)

    return {
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "window_days": args.window_days,
        "events_handled_per_week": events,
        "operator_hours_saved_per_week": as_hours(total_minutes),
        "workflows_measured": sum(1 for w in workflows if w["runs"] > 0),
        "workflows_active": active,
        "counts_cli_runs": True,
        "events_by_lane": by_lane,
        "workflows": workflows,
    }


def nested_receipt(args: argparse.Namespace) -> str:
    """The raw count of the nested workflow beside its count after the exclusion.

    Equal counts mean the exclusion never fired and one bot command is being
    counted twice.
    """
    raw = psql(
        args.alias,
        "SELECT count(*) FROM execution_entity e WHERE "
        f'e."workflowId" = $${args.nested_workflow_id}$$ '
        "AND e.status = $$success$$ "
        'AND e."deletedAt" IS NULL '
        f"AND e.mode <> $${args.exclude_mode}$$ "
        'AND e."stoppedAt" IS NOT NULL '
        f'AND e."stoppedAt" >= now() - interval $${args.window_days} days$$',
    )[0][0]
    counted = query_runs(
        args.alias,
        counted_clause(
            args.exclude_mode,
            args.window_days,
            args.parent_workflow_id,
            args.nested_workflow_id,
        ),
    ).get(args.nested_workflow_id, 0)
    return (
        f"nested workflow {args.nested_workflow_id}: raw {raw}, "
        f"counted {counted}, excluded {int(raw) - counted}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--alias", default="cd-oci", help="ssh alias for the instance")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument(
        "--exclude-mode",
        default="integrated",
        help="execution mode that marks a sub-workflow run",
    )
    ap.add_argument("--parent-workflow-id", default="iO6PfPdk0SSPBTWb")
    ap.add_argument("--nested-workflow-id", default="UIf3v1ZNN98OtUge")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--receipt", action="store_true", help="print the nested exclusion receipt")
    ap.add_argument("--apply", action="store_true", help="write the snapshot file")
    args = ap.parse_args()

    snapshot = build_snapshot(args)
    text = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
    sys.stdout.write(text)

    if args.receipt:
        print(nested_receipt(args), file=sys.stderr)

    if args.apply:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out.relative_to(ROOT)}", file=sys.stderr)
    else:
        print("(dry run; pass --apply to write)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

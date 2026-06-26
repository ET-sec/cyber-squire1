"""Plan 19-06 Task 2: golden-set generator for the GRC reviewer eval harness.

Generates 10 synthetic PR fixtures against the schema the eval harness
consumes. Each fixture is one Opus 4.8 call with cached system prompt;
running cost is tracked in the local spend ledger and the script halts at
a hard $2.00 internal cap.

Output files:
  scripts/grc/golden_prs/pr_001.json .. pr_010.json
  scripts/grc/.golden_set_cost.txt          (final cost in USD)

Run with:
  EVAL_MODE=1 ANTHROPIC_API_KEY=... python3 scripts/grc/build_golden_set.py

The 10 categories cover the reviewer's exercised code paths:
  1  add new POA&M row              (residual_risk_required=False, single control)
  2  modify existing POA&M          (status flip / target-date shift)
  3  classification change          (PUBLIC -> INTERNAL)
  4  version bump                   (string version increment)
  5  sanitization violation         (real internal pattern intentionally leaked)
  6  broken POA&M id reference      (P99-99 not in POAM_PLAN_OF_ACTION.md)
  7  missing residual_risk          (must set residual_risk_required=True)
  8  NIST control mapping update    (multi-control)
  9  threat model edit              (STRIDE/ATLAS row)
  10 red-team finding addition      (new row in REDTEAM_RESULTS.md)
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import anthropic

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.grc.spend_ledger import record_call  # noqa: E402

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(message)s")
log = logging.getLogger("build_golden_set")

MODEL = "claude-opus-4-8"
HARD_CAP_USD = 2.00
MAX_TOKENS = 2048
GOLDEN_DIR = REPO_ROOT / "scripts" / "grc" / "golden_prs"
COST_FILE = REPO_ROOT / "scripts" / "grc" / ".golden_set_cost.txt"

CATEGORIES: list[dict[str, str]] = [
    {
        "id": "pr_001",
        "name": "Add new POA&M row",
        "category": "add new POA&M row",
        "instructions": (
            "Generate a unified diff that adds ONE new row to the POA&M table in "
            "docs/grc/POAM_PLAN_OF_ACTION.md. Pick a synthetic POA&M ID like "
            "POAM-P19-50 (must not collide with existing P17-XX or P18-XX IDs). "
            "Include a brief description, severity (LOW/MED/HIGH), owner, target "
            "date, and status OPEN. Reference one NIST 800-53 control such as "
            "IR-4 or RA-5 in the description text. residual_risk should still be "
            "set in frontmatter so residual_risk_required is False."
        ),
    },
    {
        "id": "pr_002",
        "name": "Modify existing POA&M",
        "category": "modify existing POA&M",
        "instructions": (
            "Generate a unified diff that modifies a single existing POA&M row in "
            "docs/grc/POAM_PLAN_OF_ACTION.md. Use real POA&M ID POAM-P17-15. "
            "Change status from OPEN to IN_PROGRESS, shift target date by one quarter. "
            "No new controls introduced; reference IR-4 if it appears in the row. "
            "residual_risk_required is False."
        ),
    },
    {
        "id": "pr_003",
        "name": "Classification change PUBLIC->INTERNAL",
        "category": "classification change",
        "instructions": (
            "Generate a unified diff that changes the classification frontmatter "
            "key in docs/grc/THREAT_MODEL_STRIDE.md from 'PUBLIC' to 'INTERNAL'. "
            "Only the YAML frontmatter changes; body untouched. No POA&M changes. "
            "Reference no controls. residual_risk_required is False."
        ),
    },
    {
        "id": "pr_004",
        "name": "Version bump",
        "category": "version bump",
        "instructions": (
            "Generate a unified diff that bumps the 'version' frontmatter key in "
            "docs/grc/POLICY_ACCESS_CONTROL.md from '1.2' to '1.3' (string). "
            "No POA&M changes, no control changes. residual_risk_required is False."
        ),
    },
    {
        "id": "pr_005",
        "name": "Sanitization violation (intentional)",
        "category": "sanitization violation",
        "instructions": (
            "Generate a unified diff that ACCIDENTALLY leaks an internal pattern "
            "into a public-classified GRC doc. Use one of these exact internal "
            "patterns somewhere in the added body lines: '161.35.0.184', "
            "'cd-service-n8n', or '/root/COREDIRECTIVE_ENGINE'. The reviewer must "
            "catch this. expected.sanitization_violations should list the exact "
            "pattern and snippet. residual_risk_required is False (sanitization "
            "is its own gate). NO other fixtures may contain these patterns; "
            "this is the only test case."
        ),
    },
    {
        "id": "pr_006",
        "name": "Broken POA&M reference",
        "category": "broken POA&M ID reference",
        "instructions": (
            "Generate a unified diff that references POA&M ID POAM-P99-99 inside "
            "docs/grc/REDTEAM_RESULTS.md body text. P99-99 does NOT exist in "
            "POAM_PLAN_OF_ACTION.md. The reviewer must flag the broken reference. "
            "expected.poams should include P99-99 with change='referenced-missing'. "
            "residual_risk_required is False."
        ),
    },
    {
        "id": "pr_007",
        "name": "Missing residual_risk frontmatter",
        "category": "missing residual_risk",
        "instructions": (
            "Generate a unified diff that adds a new GRC doc, "
            "docs/grc/AI_RAG_GUARDRAILS.md, with frontmatter that has title, "
            "version (string), classification 'INTERNAL', owner, last_reviewed - "
            "but NO residual_risk key. The reviewer MUST set "
            "residual_risk_required to True (this is the merge gate). "
            "expected.residual_risk_required is True. No control mappings."
        ),
    },
    {
        "id": "pr_008",
        "name": "NIST control mapping update (multi-control)",
        "category": "NIST control mapping update",
        "instructions": (
            "Generate a unified diff that updates docs/grc/FRAMEWORK_CROSSWALK_SQUIRE.md "
            "to add mappings for THREE NIST 800-53 controls in one PR: AC-2, AC-6, "
            "and AU-12. expected.controls is the list ['AC-2','AC-6','AU-12']. "
            "No POA&M changes. residual_risk_required is False."
        ),
    },
    {
        "id": "pr_009",
        "name": "Threat model edit",
        "category": "threat model edit",
        "instructions": (
            "Generate a unified diff that adds a single new STRIDE row to "
            "docs/grc/SQUIRE_THREAT_MODEL.md. The threat is 'Tampering' targeting "
            "the LangGraph state machine. Reference one MITRE ATLAS technique ID "
            "like AML.T0044 in the row. Include one NIST control such as SI-7. "
            "residual_risk_required is False."
        ),
    },
    {
        "id": "pr_010",
        "name": "Red-team finding addition",
        "category": "red-team finding addition",
        "instructions": (
            "Generate a unified diff that appends a new finding to "
            "docs/grc/REDTEAM_RESULTS.md. Finding number 8, cycle 3, severity LOW. "
            "Describe a citation-fabrication test that surfaced 1 of 14 cases where "
            "the model invented a NIST control reference. Reference IR-4 and RA-5 "
            "as relevant controls. residual_risk_required is False."
        ),
    },
]

SYSTEM_PROMPT = """You are a synthetic test fixture generator for a GRC PR reviewer agent.

Your job: given a category description, produce a single JSON object with EXACTLY this schema:

{
  "name": "<short fixture name, max 60 chars>",
  "category": "<exactly the category string from the user message>",
  "diff": "<unified diff string with diff --git, --- a/, +++ b/ headers, valid hunk headers, and additions/deletions>",
  "expected": {
    "controls": ["<NIST 800-53 control ID like IR-4>", ...],
    "poams": [{"poam_id": "<P\\\\d+-\\\\d+ form>", "change": "<added|modified|referenced-missing>"}, ...],
    "sanitization_violations": [{"pattern": "<exact leaked string>", "snippet": "<surrounding context>"}, ...],
    "residual_risk_required": <true|false>
  }
}

Rules:
- Output ONLY the JSON object. No prose, no markdown fences, no preamble.
- The diff MUST be a syntactically valid unified diff (diff --git headers, file paths under docs/grc/, line numbers in hunk headers).
- POA&M IDs use the form POAM-P\\d+-\\d+ in the diff body, but the short P\\d+-\\d+ form goes into expected.poams[*].poam_id.
- residual_risk_required is true ONLY when the diff adds a doc whose frontmatter lacks the residual_risk key.
- If the category is "sanitization violation", populate sanitization_violations with at least one entry; otherwise leave it as [].
- expected.controls lists every NIST 800-53 control mentioned in the diff body (deduplicated, sorted).
- expected.poams covers every POA&M ID added, modified, or referenced-but-missing in the diff.
- Keep diffs realistic and concise (under 80 lines)."""


def _running_cost_today() -> float:
    """Return today's running cost from the local ledger."""
    from scripts.grc.spend_ledger import today_total_usd

    return today_total_usd()


def _budget_guard_pass() -> bool:
    """Run scripts/grc/budget_guard.py and return True if it exits 0."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "grc" / "budget_guard.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("budget_guard blocked: %s", (result.stderr or result.stdout).strip())
        return False
    return True


def _generate_one(client: anthropic.Anthropic, cat: dict[str, str]) -> tuple[dict[str, Any], float]:
    """Call Opus once for one category, return (parsed_fixture, call_cost_usd)."""
    user_msg = (
        f"Category: {cat['category']}\n\n"
        f"Instructions:\n{cat['instructions']}\n\n"
        "Return only the JSON fixture object."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    usage = getattr(response, "usage", None)
    usage_dict: dict[str, int] = {}
    if usage is not None:
        for k in (
            "input_tokens",
            "output_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
        ):
            v = getattr(usage, k, None)
            if v is None and isinstance(usage, dict):
                v = usage.get(k, 0)
            usage_dict[k] = int(v or 0)
    cost = record_call(MODEL, usage_dict)

    text_parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    raw = "".join(text_parts).strip()
    if raw.startswith("```"):
        # Tolerate markdown fences even though prompt forbids them.
        lines = raw.splitlines()
        raw = "\n".join(line for line in lines if not line.startswith("```"))
    fixture = json.loads(raw)
    return fixture, cost


def _print_manifest(fixtures: list[dict[str, Any]]) -> None:
    """Print a hand-review manifest for the curator checkpoint."""
    print("\n" + "=" * 70, file=sys.stderr)
    print("GOLDEN-SET CURATOR REVIEW MANIFEST", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    for fixture in fixtures:
        print("", file=sys.stderr)
        print(f"--- {fixture['_file']} ---", file=sys.stderr)
        print(f"name:     {fixture.get('name', '?')}", file=sys.stderr)
        print(f"category: {fixture.get('category', '?')}", file=sys.stderr)
        controls = fixture.get("expected", {}).get("controls", [])
        poams = fixture.get("expected", {}).get("poams", [])
        sv = fixture.get("expected", {}).get("sanitization_violations", [])
        rr = fixture.get("expected", {}).get("residual_risk_required", "?")
        print(f"controls: {controls}", file=sys.stderr)
        print(f"poams:    {poams}", file=sys.stderr)
        print(f"sanit:    {sv}", file=sys.stderr)
        print(f"residual_risk_required: {rr}", file=sys.stderr)
        diff_preview = (fixture.get("diff", "")[:240]).replace("\n", " | ")
        print(f"diff[:240]: {diff_preview}", file=sys.stderr)
    print("\n" + "=" * 70, file=sys.stderr)
    print("Open each pr_NNN.json file and review against the 5 curator dimensions.", file=sys.stderr)
    print("=" * 70 + "\n", file=sys.stderr)


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.error("ANTHROPIC_API_KEY not set; cannot generate golden set")
        return 1

    os.environ.setdefault("EVAL_MODE", "1")

    if not _budget_guard_pass():
        return 1

    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

    client = anthropic.Anthropic()
    fixtures: list[dict[str, Any]] = []
    total_cost = 0.0
    baseline = _running_cost_today()

    for cat in CATEGORIES:
        running = _running_cost_today() - baseline
        if running >= HARD_CAP_USD:
            log.warning(
                "Hard cap reached: $%.4f >= $%.2f. Halting before %s.",
                running,
                HARD_CAP_USD,
                cat["id"],
            )
            break
        log.info("Generating %s (%s)...", cat["id"], cat["name"])
        try:
            fixture, cost = _generate_one(client, cat)
        except json.JSONDecodeError as e:
            log.error("JSON decode failed for %s: %s", cat["id"], e)
            continue
        except Exception as e:
            log.error("Generation failed for %s: %s", cat["id"], e)
            continue

        fixture["_file"] = f"scripts/grc/golden_prs/{cat['id']}.json"
        out_path = GOLDEN_DIR / f"{cat['id']}.json"
        # Strip the helper field before persisting; keep it on in-memory copy for manifest.
        persistable = {k: v for k, v in fixture.items() if not k.startswith("_")}
        out_path.write_text(json.dumps(persistable, indent=2) + "\n")
        log.info("  wrote %s (call cost ~$%.4f)", out_path.relative_to(REPO_ROOT), cost)
        total_cost += cost
        fixtures.append(fixture)

    COST_FILE.write_text(f"{total_cost:.6f}\n")
    log.info("Total spend this run: $%.4f -> %s", total_cost, COST_FILE.relative_to(REPO_ROOT))

    _print_manifest(fixtures)
    return 0 if len(fixtures) == len(CATEGORIES) else 2


if __name__ == "__main__":
    sys.exit(main())

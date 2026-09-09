# docs

The evidence package: the governance library, the architecture record, the
published views, and the machine read registries at this directory's root.
141 tracked files, public on purpose, because a claim nobody can check is not
evidence.

Three kinds of reader land here. An auditor tracing a control from a framework
row to the file that implements it. A hiring reviewer deciding whether the
security engineering behind a resume is real. The operator six months from now
who has forgotten why a control is shaped the way it is. The reading order is
written for the first two. The map after it is what the third one uses.

## Reading order

Seven documents, ordered so that each one is legible by the time you reach it.
A reviewer who follows this and reads nothing else comes out knowing what the
platform is, what defends it, and who says so.

1. **[architecture/STACK_OVERVIEW.md](architecture/STACK_OVERVIEW.md)** gives you
   the parts: four security planes over a two tier runtime, and for each control
   the enemy it defeats and how it was verified. It goes first because every
   document after it names these services and assumes you can place them.
2. **[architecture/views/README.md](architecture/views/README.md)** is the same
   system drawn seven ways, with a node table behind every box. Second, because a
   trust boundary is easier to hold as a picture than as prose, and each box on a
   view carries the repository file and line that proves the status it claims.
3. **[architecture/INFORMATION_FLOWS.md](architecture/INFORMATION_FLOWS.md)**
   walks two critical paths end to end, an alert through the analyst agent and a
   document through the governance pipeline. Third, because a flow is what turns
   a static drawing into a system you can reason about.
4. **[architecture/decisions/README.md](architecture/decisions/README.md)** holds
   six records, one per control shipped in the cloud hardening pass: the options
   weighed, the blast radius if the control fails, and how it was verified by
   attacking it. Fourth, because each record assumes you already know which box
   it defends.
5. **[grc/README.md](grc/README.md)** is the governance, risk, and compliance
   (GRC) library, 57 sanitized documents with its own reading order and its own
   map inside. Fifth, because its system security plan maps 140 NIST 800-53
   controls onto the architecture you have just read. Taken first, those controls
   are a list of nouns.
6. **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** covers how a change actually
   reaches the main branch: the branch discipline, the pull request gates, and
   what each gate refuses. Sixth, because it answers the question the control
   documents raise, which is who stops a bad change.
7. **[MASTER_SYNC_ARCHITECTURE.md](MASTER_SYNC_ARCHITECTURE.md)** explains how
   every count above is kept true: the filesystem is the source, `metrics.yaml`
   is derived from it, and marker blocks inject it into the surfaces that quote
   it. Last, because it answers the question a careful reader is left holding
   after the other six, which is who checks these numbers.

## Map

Counts are tracked files, measured with `git ls-files` on 2026-09-09.

| Subtree | What it holds | Entry point |
|---|---|---|
| `architecture/` (37) | Four documents at its own level: the stack overview, the information flows, the OWASP GenAI mapping, and the mermaid sources behind the drawings. This tree has no README of its own, and this row is the reason it needs none: both subdirectories below carry their own index, and a third page whose only content is two links helps nobody. | [STACK_OVERVIEW.md](architecture/STACK_OVERVIEW.md) |
| `architecture/decisions/` | Six decision records, DR-01 through DR-06, each naming the control it satisfies and the artifact that proves it. | [decisions/README.md](architecture/decisions/README.md) |
| `architecture/views/` | The seven published views: the drawings, the generators that emit them, the node tables that make every box clickable, and the view manifest they are built from. | [views/README.md](architecture/views/README.md) |
| `grc/` (96) | The sanitized governance library: system security plan, plan of action, risk assessment, ten policies, five incident response playbooks, six threat modeling documents, framework crosswalks, and the rendered evidence graphics. | [grc/README.md](grc/README.md) |
| `context/` (1) | Dated probe evidence: what was measured, on what version, and which path was chosen because of it. Most of this tree is untracked working notes; one probe is public. | [17-05-openclaw-langfuse-probe.md](context/evidence/17-05-openclaw-langfuse-probe.md) |

Six files sit beside this README at the docs root. Four are prose, two are
registries that programs read. They are listed one by one because a handful of
files with no folder to explain them is exactly what an index is for.

| File | What it is |
|---|---|
| [GROUND_TRUTH_AUDIT_PROTOCOL.md](GROUND_TRUTH_AUDIT_PROTOCOL.md) | The six step procedure for auditing a claim against the filesystem instead of against memory. Run before publication and at the close of every milestone. |
| [GTA_SKILL_DESIGN_NOTES.md](GTA_SKILL_DESIGN_NOTES.md) | The design backlog for automating that protocol. The protocol above says how to run the audit; this says how to build the tool that runs it. |
| [MASTER_SYNC_ARCHITECTURE.md](MASTER_SYNC_ARCHITECTURE.md) | How a generated number reaches the resume and the site without drifting on the way: the four artifacts, the marker namespaces, the sync scripts. |
| [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) | Branch, pull request, and merge discipline, with the gate each change passes through. |
| [REPO_MANIFEST.yaml](REPO_MANIFEST.yaml) | One row per tracked path: what it is, why it stays, when it was last checked, and what would make somebody look again. Read by [manifest_check.py](../scripts/repo/manifest_check.py) on every pull request. |
| [REVIEW_REGISTER.yaml](REVIEW_REGISTER.yaml) | The event half of those review triggers, for conditions no date can predict. Evaluated nightly rather than on the pull request path, so a register edit can never turn a pull request red. |

<!-- MANIFEST:docs -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `docs/**` | active | The documentation tree: governance library, architecture records, published views, and the two machine read registries at the docs root. |
| `docs/GROUND_TRUTH_AUDIT_PROTOCOL.md` | active | The procedure for auditing a claim against the filesystem rather than against memory. |
| `docs/MASTER_SYNC_ARCHITECTURE.md` | active | How generated numbers and generated blocks reach the published site: the marker namespaces, the sync scripts, and the injection contract. |
| `docs/README.md` | active | The documentation entry point: the reading order through the tree, a map of every subtree with its entry point, and a statement of what is deliberately absent. |
| `docs/REPO_MANIFEST.yaml` | active | This file: one row for every tracked path, with what it is, why it stays, when it was last checked, and what would make somebody look again. |
| `docs/WORKFLOW_GUIDE.md` | active | What each workflow does, when it runs, and what it needs to pass. |
| `docs/architecture/**` | active | The architecture record: information flows, stack overview, the OWASP LLM mapping, and the mermaid sources behind them. |
| `docs/architecture/decisions/**` | active | Six decision records, each naming the control it satisfies and the artifact that proves it. |
| `docs/architecture/views/**` | active | The seven published architecture views: the drawings, the generators that emit them, and the view index. |
| `docs/architecture/views/nodes/**` | active | One node table per view: every box on the drawing with its zone, its controls, its honest status, and the file and line that proves it. |
| `docs/context/**` | reference | Dated probe evidence: what was measured, on what version, and which path was chosen as a result. |
| `docs/grc/**` | active | The sanitized governance library: system security plan, risk assessment, crosswalks, threat models, audits, and the executive summaries. |
| `docs/grc/GUARDRAILS_CONFIGURATION.md` | active | How the guardrail rails are configured, what each blocks, and how a block reaches the caller. |
| `docs/grc/PLAYBOOK_*.md` | active | Five incident response playbooks: compromised container, leaked credential, unauthorized access, service degradation, and an AI specific incident. |
| `docs/grc/POAM_AUTO_FINDINGS.md` | active | The machine written half of the plan of action: findings the merge pipeline discovered, with their identifiers. |
| `docs/grc/POLICY_*.md` | active | Ten policies covering access control, change management, incident response, risk, vulnerability management, continuity, recovery, acceptable use, awareness, and AI governance. |
| `docs/grc/README.md` | active | The library index: reading order, framework alignment, a table per category, the review schedule, and the reproducible statistics. |
| `docs/grc/diagrams/**` | active | Every evidence graphic the governance library embeds, kept beside the HTML source it renders from, from control coverage and the risk heat map through the topology and the map of the library itself. |
| `docs/grc/oscal/**` | active | The machine readable form of the system security plan, component definition, and plan of action, with the schemas they validate against. |
| `docs/grc/stix/**` | active | The STIX 2.1 bundle of the Squire threat model: the threat actors, the attack patterns, and the course of action objects that map to controls. |
<!-- /MANIFEST -->

## What is deliberately not here

If you came looking for something and did not find it, one of these five lines
is the reason. Each is a choice somebody made and can defend.

- **Planning documents.** The roadmap, the phase plans, and the execution
  summaries live in `.planning/`, which is gitignored. What crosses into the
  public tree is the outcome rather than the deliberation: a decision record, a
  manifest row, a control mapping.
- **Private commercial material.** Client work and the business tree are
  excluded by `.gitignore`. Nothing under this directory describes a paying
  engagement.
- **Secrets.** Every credential is fetched from Doppler at run time. No
  environment file, key, or token is tracked, and a pre-commit hook runs a
  secret scan that fails closed before a commit can land.
- **The sanitization map.** The governance library substitutes every address,
  hostname, and service name. `SANITIZATION_KEY.md` holds the reverse mapping
  and is local only, which is why a drawing here shows a shape with no address
  on it.
- **Raw evidence transcripts.** The decision records quote status codes, error
  strings, and timings from live runs. The full command transcripts sit in a
  private evidence store, because a transcript carries operational detail that a
  status code does not.

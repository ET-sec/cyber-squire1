# docs

The evidence package: the governance library, the architecture record, the
published views, and the machine read registries at this directory's root.

<!-- MANIFEST:docs -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `docs/**` | active | The documentation tree: governance library, architecture records, published views, and the two machine read registries at the docs root. |
| `docs/GROUND_TRUTH_AUDIT_PROTOCOL.md` | active | The procedure for auditing a claim against the filesystem rather than against memory. |
| `docs/MASTER_SYNC_ARCHITECTURE.md` | active | How generated numbers and generated blocks reach the published site: the marker namespaces, the sync scripts, and the injection contract. |
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
| `docs/grc/diagrams/**` | active | Rendered evidence graphics and the HTML sources they come from: control coverage, data flow, risk heat map, pipeline, topology, and the stack hero. |
| `docs/grc/oscal/**` | active | The machine readable form of the system security plan, component definition, and plan of action, with the schemas they validate against. |
| `docs/grc/stix/**` | active | The STIX 2.1 bundle of the Squire threat model: the threat actors, the attack patterns, and the course of action objects that map to controls. |
<!-- /MANIFEST -->

Plan 21-09 adds the reading order and the map around this block. Until then the
generated table above is the whole index, and `docs/grc/README.md` is the entry
point for the governance library.

# tests

The suites that prove the toolchain works: the governance scripts under
`scripts/grc/`, and the repository hygiene gates built in Phase 21. Squire keeps
its own suite under `builds/squire/tests/`.

<!-- MANIFEST:tests -->
Generated from docs/REPO_MANIFEST.yaml. Do not hand edit inside the markers.

| Path | Status | Purpose |
|---|---|---|
| `tests/README.md` | active | The directory README for tests/, whose contents block is generated from this manifest. |
| `tests/grc/**` | active | The governance toolchain suite: sanitization, frontmatter conversion, the budget guard, OSCAL signing, the offline reviewer, the inventory scanner, and the MCP server transport. |
| `tests/repo/**` | active | The Phase 21 gate suite: the manifest checker across its three failure classes and both configuration errors, the repository scope of the public gate, the review register, and the sweep runner with both of its seeded failures. |
| `tests/repo/fixtures/**` | active | Deliberate fixtures: a manifest that parses, one that does not, a file carrying the exact string the public gate forbids, and a file carrying a link that resolves to nothing. |
<!-- /MANIFEST -->

Run them with `python3 -m pytest tests -q`. Every case here is offline: no
network, no funded key, no live host, so the suite is the same on a laptop and
on a runner. The gate tests were written before the gates they cover, which is
the order that makes them worth having.

---
name: GTA finding
about: Document a Ground Truth Audit drift, doc mismatch, or sanitization gap
title: 'gta: <doc-or-scope>: <short summary>'
labels: gta-audit
---

## Scope
File path or scope where the finding lives.

## Classification
- [ ] OUTDATED (was true once, no longer is)
- [ ] WRONG (was never true)
- [ ] UNCLEAR (ambiguous, needs owner judgment)
- [ ] SANITIZATION (token leak)

## Ground truth source
What you compared against (compose.yaml, NIST PDF, MITRE matrix, actual code path).

## The mismatch
Quote the line as-is, then the corrected version.

```
Current:
Suggested:
```

## Confidence
- [ ] HIGH (ground truth file says it explicitly)
- [ ] MEDIUM (multiple sources agree, no single proof)
- [ ] LOW (one source, judgment call)

## Related
GTA run timestamp, sidecar path under \`.gta/\` or \`docs/grc/_corrections/\`, related issues.

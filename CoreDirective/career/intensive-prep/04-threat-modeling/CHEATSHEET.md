# CHEATSHEET: Threat Modeling One-Pager

Print this. Keep it taped to the desk during phone screens. Keep it on a tab during video interviews. The whole intensive collapses into this page.

---

## STRIDE letters with one-line examples

| Letter | Property violated | Bug example | Cloud example | LLM example |
|--------|-------------------|-------------|----------------|-------------|
| **S** Spoofing | Authentication | Stolen JWT replayed | Forged Stripe webhook | Bot impersonates legitimate caller via leaked token |
| **T** Tampering | Integrity | SQL injection rewrites order | S3 object swapped due to mutable tag | Poisoned RAG chunk flips retrieval |
| **R** Repudiation | Non-repudiation | Admin deletes audit row | CloudTrail disabled | Tool action with no plan-trace |
| **I** Information disclosure | Confidentiality | Stack trace leaks env vars | Public S3 bucket | RAG returns another tenant's chunk |
| **D** Denial of service | Availability | Slow loris on origin | One tenant exhausts shared API quota | Token-budget exhaustion |
| **E** Elevation of privilege | Authorization | IDOR on /orders/{id} | Over-broad IAM `s3:*` | Prompt injection makes LLM call admin tool |

---

## Top 20 trust boundary patterns to recognize on sight

1. Internet to public-facing service
2. CDN/WAF to origin
3. Load balancer to backend (not really a boundary if same VPC)
4. Browser to API
5. API to database
6. Service to service inside a VPC (only a boundary if mTLS or IAM differs)
7. AWS account to AWS account (the strongest cloud boundary)
8. Region to region (data residency)
9. KMS key boundary (who can decrypt)
10. IAM role boundary
11. Kubernetes namespace (soft boundary, do not rely on it)
12. Container runtime to host kernel (escape boundary)
13. Tenant A to tenant B (multi-tenant)
14. User input to system prompt (LLM)
15. Retrieved chunk to LLM context (indirect injection)
16. LLM output to downstream interpreter (output handling)
17. LLM output to tool router (tool authorization)
18. Third-party SaaS to your app (OAuth callback, webhook)
19. Build pipeline to artifact registry (supply chain)
20. CI runner to cloud (OIDC federation, IAM trust)

---

## DREAD scoring (only if asked, do not volunteer)

Score each 1 to 10. Average. Above 7 High, 4 to 7 Medium, below 4 Low.
- **D** Damage: how bad if exploited
- **R** Reproducibility: how easy to reproduce
- **E** Exploitability: skill required
- **A** Affected users: how many
- **D** Discoverability: how easy to find

Tip: never give a 9.7 or 6.4. Round to whole numbers and prefer the H/M/L bucket. Pseudo-precision is junior signal.

---

## ATLAS techniques to know cold

| ID | Technique | Defense |
|----|-----------|---------|
| AML.T0051 | LLM Prompt Injection (direct or indirect) | Tag context, sanitize, structure as data not instructions, critique loop |
| AML.T0048 | External Harms | Tool allow-list, HITL on irreversible, action rate limits |
| AML.T0024 | Exfiltration via ML Inference API | Per-user budget, rate limits, query monitoring |
| AML.T0044 | Full ML Model Access | Gateway audit, key rotation, key scoping |
| AML.T0019 | Publish Poisoned Datasets | Treat external corpora as untrusted, signed feeds, provenance |
| AML.T0020 | Poison Training Data | Provenance, anomaly detection during training, validation set guards |
| AML.T0043 | Craft Adversarial Data | Adversarial training, input filters, defense in depth |

ATLAS tactics to mention by name: ML Model Access (AML.TA0005), Defense Evasion (AML.TA0011), Exfiltration (AML.TA0024).

---

## ATT&CK 14 tactics in order (memorize)

Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact.

Mnemonic: Real Resource I Eat Pizza Pie, Defense Cant Detect Lateral Cookies Coming Easy In.

---

## Phrases to sound senior (use one or two per session, not all)

- "The threat surface widens because [reason]."
- "The residual risk is bounded by [control or assumption]."
- "The compensating control is [secondary defense]."
- "The blast radius narrows because [isolation control]."
- "I would treat this as a confused-deputy problem."
- "Authorization lives in [the tool router / the API / the IAM policy], never in [the LLM / the client / the form]."
- "We are accepting this because [acceptance rationale], owned by [team], reviewed [cadence]."
- "I would rather pay engineering cost once on a strong primary control than perpetual ops cost on weak detection."
- "This is a defense-in-depth conversation, not a single-control conversation."
- "Likelihood times impact, three by three, no DREAD decimals."
- "Every external interface is a trust boundary by default."
- "If the control fails, here is the signal that fires."
- "Detection is what makes residual risk acceptable, not control existence."
- "Stale diagrams are worse than no diagrams."
- "The framework is the memory aid; the discipline is the asset."

---

## Phrases to never use (AI tells, junior signal)

- "Comprehensive"
- "Robust"
- "Cutting edge"
- "Best practice" (say "industry standard" instead)
- "Holistic"
- "Synergy"
- "Leverage" as a verb (say "use")
- Em dashes
- "It's important to note that"
- "In today's threat landscape"
- "Bad actors"
- DREAD scores with decimals
- "We just rate-limit" (with no threshold)

---

## Live session minute-by-minute checklist

```
0:00  Opening monologue (90s) - the 7 phases speech
1:30  Phase 1 Scope          - assets, actors, data classes, assumptions on board
4:30  Phase 2 DFD            - draw level 0, label flows, dashed boundaries
10:30 Phase 3 STRIDE walk    - one boundary at a time, list threats
18:30 Phase 4 Prioritize     - HML matrix, top 10
21:30 Phase 5 Mitigations    - primary + compensating, named tradeoff
25:00 Phase 6 Residual       - count by severity, acceptance rationale
27:00 Phase 7 Detections     - one signal per High and Medium
30:00 Closing line           - top 3 risks, residual position, ask "where deeper?"
```

If you only have 15 minutes, hard-cut at:
- Phase 1: 2 min
- Phase 2: 4 min
- Phase 3: 5 min (5 threats minimum)
- Phase 4: 1 min
- Phase 5: 2 min
- Phase 6: 1 min

---

## Pre-interview ritual (do this right before every threat-model interview)

1. Read this cheatsheet, twice.
2. Re-read the 90-second opener until you can recite the 7 phases.
3. Pick the most likely drill scenario based on the role and skim that drill.
4. Have HIS-STACK.md open in another tab as proof you have done this for real.
5. Pen, paper, and a flat surface.

---

## Three lines that signal senior in the first 90 seconds

If you nail nothing else, nail these:

1. "Before I draw anything, let me clarify the scope so we are solving the same problem."
2. "Every external interface is a trust boundary by default."
3. "I will end with residual risk explicitly because that is what differentiates a useful threat model from a checklist."

That is the cheatsheet.

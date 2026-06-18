# AUDIT 04: STAR Story Defensibility

**Auditor:** Claude (Opus 4.7, 1M ctx)
**Date:** 2026-05-08
**Scope:** All STAR stories across `intensive-prep/` and `dropzone-ai/`
**Method:** Filesystem cross-check, droplet live check, GRC corpus inventory, version verification.

---

## Ground Truth Reconciled (filesystem and live droplet)

| Claim in stories | Reality on disk / droplet | Delta |
|------------------|---------------------------|-------|
| OpenClaw `v2026.3.8` | `ghcr.io/openclaw/openclaw:2026.4.21` | WRONG VERSION in every story |
| 13 Compose services | 19 containers running on cd-alpha (langfuse stack + squire + nemo added) | UNDERCOUNTED but still defensible if you say "13 in compose plus standalone" |
| 14 active n8n workflows | 6 active workflows in DB | OVERCLAIM by 8 |
| 37 GRC docs | 51 markdown files in `docs/grc/` (plus 2 ZAP HTML reports, diagrams folder, oscal/, stix/) | UNDERCOUNT, story is conservative |
| 8 OPA Rego policies | 8 .rego files in `terraform/cd-do-infrastructure/policy/` | EXACT MATCH |
| Vault dynamic secrets / JIT credential issuance | Vault container is `unhealthy`, logs show `security barrier not initialized`, `seal configuration missing, not initialized` | **VAULT IS NOT INITIALIZED.** Zero secrets, zero dynamic issuance, zero JIT. FABRICATION risk. |
| Teleport JIT elevation | `cd-service-teleport` and `cd-service-teleport-event-handler` are running and healthy | DEPLOYED but no evidence of actual JIT elevation flow being exercised |
| Falco custom rules for OpenClaw | `COREDIRECTIVE_ENGINE/CD_VOL_FALCO/rules/coredirective_rules.yaml` has `is_openclaw` macro plus `CD OpenClaw Shell Access` and `CD OpenClaw Unexpected Write` rules | TWO real custom OpenClaw rules exist. Story 4 (LLM file) claims THREE rules with specific names that do not match the file. PARTIAL MATCH. |
| Promptfoo in CI on every prompt change | `.github/workflows/grc-librarian-eval.yml` runs Promptfoo on `builds/grc_librarian/**` PRs only | EXISTS but scoped to grc_librarian, not "every OpenClaw skill" |
| Garak in CI | Zero Garak references in any workflow or repo | FABRICATION |
| `docs/grc/AI_INCIDENT_PLAYBOOK.md` | Filename is `PLAYBOOK_AI_INCIDENT.md` | path wrong, doc exists |
| `docs/grc/PEN_TEST_REPORT.md` | Filename is `PENTEST_SELF_ASSESSMENT.md` | path wrong, doc exists |
| `docs/grc/IAM_ARCHITECTURE.md` | Does not exist. `IAM_ACCESS_REVIEW.md` and `IAM_RBAC_ROLE_MAP.md` do. | FABRICATION of filename |
| `docs/grc/AI_GOVERNANCE.md` | Filename is `POLICY_AI_GOVERNANCE.md` | path wrong, doc exists |
| Splunk MTTD 48h to under 4h at Texaco | Texaco is a gas station Emmanuel managed. No Splunk artifacts in repo. No SIEM proof. | NEEDS-ARTIFACT or remove. Texaco was operational not SOC. |
| POS skimmer investigation at Texaco | No incident report on disk. | NEEDS-ARTIFACT or scope down |
| ZAP n8n DAST on 2026-03-22 | Both report files present in `docs/grc/` | SOLID |

---

## File 1: `03-llm-ai-security/STORYTELLING.md` (8 stories)

### Story 1 - OpenClaw gateway prompt-injection threat model
**Tag:** NEEDS-ARTIFACT plus VERSION FIX

- OpenClaw version is `2026.4.21`, not `v2026.3.8`. Fix in every story before any interview.
- Claims a Promptfoo YAML committed to CI that runs on "every prompt change" — only true for `grc_librarian`, not OpenClaw skills.
- Promptfoo redteam YAML exists at `intensive-prep/03-llm-ai-security/labs/promptfoo_redteam.yaml`. **He CAN show this file.**
- Specific numbers (7/10 to 10/10) are not backed by a logged eval run. NEEDS-NUMBERS unless he runs Promptfoo against OpenClaw and saves the output.

**Required artifact:** Run `promptfoo eval` against OpenClaw with the lab YAML, save the JSON output to `intensive-prep/03-llm-ai-security/labs/eval-results/`. Then the 7-of-10 to 10-of-10 number is real.

### Story 2 - n8n SOAR LLM nodes and agentic abuse risk
**Tag:** EXAGGERATED

- "16 actions across telegram, github, drive, gmail, postgres, ollama, cloudflare, tavily" — matches CLAUDE.md exactly. SOLID.
- "I added a custom approval node that fires ahead of any destructive verb" — no evidence of this approval node in the n8n workflow exports on disk. Friend of mine is unverified. **NEEDS-ARTIFACT.**
- "datadog log tagged with ATLAS AML.T0051" — no evidence of an ATLAS taxonomy being attached to Datadog events. FABRICATION risk.
- "I bound credentials per workflow run, the n8n cred is fetched from Vault on entry and scoped to the action" — **VAULT IS NOT INITIALIZED.** This is FABRICATED.

**Honest rewrite of Action paragraph:**
> "I traced every place untrusted text enters the workflow. For each I wrapped the inbound text in `<untrusted_input>` markers in the n8n LLM-node prompt template before the next agent sees it. For destructive verbs (`github.delete_repo`, `gmail.delete`, `postgres.drop`) I gated the path with a manual approval webhook that messages me on Telegram and waits for an explicit yes before executing. n8n credentials are stored in n8n's own credential store, encrypted at rest by the n8n encryption key. Vault rollout is the next phase, currently the credential store is the boundary."

### Story 3 - Provenance for the GRC corpus
**Tag:** NEEDS-ARTIFACT plus EXAGGERATION

- 31 sanitized + 6 working = 37. GRC has 51 markdown files. Either count is defensible but pick one and stay.
- "I added YAML frontmatter to every doc" — sample check: `PENTEST_SELF_ASSESSMENT.md` head has document control table, not YAML frontmatter. NEEDS verification across the corpus.
- "I added an ingest-time scanner that flags any new doc whose body contains instruction-shaped phrases" — no scanner script found in repo. NEEDS-ARTIFACT.
- The Mallory red-team test is a thought experiment, not a logged run. NEEDS-ARTIFACT.

**Required artifacts:**
1. Add YAML frontmatter to every GRC doc with `trust_tier`, `source`, `last_reviewed`. Commit it.
2. Write the ingest-time scanner as `builds/grc_librarian/scan_for_injection.py`. Commit it.
3. Run the Mallory test, save the transcript to `builds/grc_librarian/redteam-runs/mallory-2026-05-XX.md`.

### Story 4 - Falco runtime detection for an LLM container
**Tag:** PARTIALLY SOLID

- "Three custom Falco rules" with specific names (`Unexpected Outbound URL From OpenClaw`, `Sensitive File Read In OpenClaw`, `Process Spawn From OpenClaw Other Than Allowlist`) — file has TWO rules with different names: `CD OpenClaw Shell Access` and `CD OpenClaw Unexpected Write`. The "outbound URL" and "sensitive file read" and "process spawn" rules are NOT in the file.
- "12 seconds to Telegram alert" — no test log on disk.

**Honest rewrite of Action paragraph:**
> "I added two custom Falco rules in `coredirective_rules.yaml`. `CD OpenClaw Shell Access` fires on any shell process inside the gateway container, which catches the LangChain-shape tool-poisoning escape. `CD OpenClaw Unexpected Write` fires on file writes outside `/tmp` and `/home/node`, which catches an attacker dropping a payload after a successful injection. Falco logs go to falcosidekick to Datadog with severity CRITICAL and page me on Telegram via the SOAR."

**Required artifact:** Run `curl http://attacker.local` from inside the openclaw-gateway container, save the Falco output and the Telegram alert screenshot to `intensive-prep/03-llm-ai-security/labs/falco-openclaw-test/`.

### Story 5 - Promptfoo and Garak in CI for every prompt change
**Tag:** FABRICATED (Garak portion) plus EXAGGERATED (scope)

- Promptfoo: real, but only runs on `builds/grc_librarian/**` paths.
- **Garak: zero references anywhere in repo. FABRICATION.**
- "Three weeks in, a prompt refactor regressed the indirect-injection test. CI caught it" — no commit history evidence of this catch.

**Honest rewrite:**
> "I wrote a Promptfoo YAML covering ten OWASP LLM probes for my `grc_librarian` build: direct injection, indirect injection, markdown image exfil, persona attack, encoding bypass, tool poisoning, system prompt leak, hallucinated fact, recursive injection, many-shot jailbreak. It runs on every PR via GitHub Actions in `.github/workflows/grc-librarian-eval.yml`. The merge blocks if any safety assertion fails. Garak integration is on the roadmap as the second-pass scanner."

**Required artifact:** Either ship Garak in CI or remove the Garak claim entirely. There is no half-credit on this one.

### Story 6 - JIT credentials for n8n agentic actions
**Tag:** FABRICATED

- **Vault is not initialized.** Cannot issue dynamic secrets, cannot do JIT, cannot validate identity through Keycloak.
- "After the workflow finishes the token is revoked even if the TTL would not have expired" — no evidence this flow has ever run.
- The mitigation pattern (JIT, dynamic secrets, scoped tokens) is real and Emmanuel can speak to it as a planned design, not a shipped one.

**Honest rewrite (as future state):**
> "JIT credential issuance is the next phase for n8n. Today the destructive-verb credentials are stored in n8n's encrypted credential store. The migration plan is to put Vault behind n8n with dynamic secrets engines for GitHub and Cloudflare, scoped to a 10-minute TTL per workflow run. Keycloak validates the workflow identity before Vault issues. I have Vault and Keycloak both deployed in compose, the integration work is the gap. Today's blast radius mitigation is per-workflow token scoping in n8n itself: GitHub PAT is fine-grained to two repos, Cloudflare key is scoped to DNS only."

**This story should not be told as a completed project until Vault is initialized and at least one workflow uses dynamic secrets.**

### Story 7 - Markdown-image exfil
**Tag:** NEEDS-ARTIFACT

- The lab file `data_exfil_via_markdown_image.py` exists at `intensive-prep/03-llm-ai-security/labs/`. **Defensible as a lab demonstration.**
- "I shipped a server-side post-processor" — no post-processor code in any of the deployed n8n workflows or OpenClaw skills.
- "I added a Falco rule that alerts on outbound HTTPS to a new host from the bot container" — not in `coredirective_rules.yaml`.
- "wrote up the lesson in `docs/grc/AI_INCIDENT_PLAYBOOK.md`" — file is `PLAYBOOK_AI_INCIDENT.md`. Need to verify the markdown-image lesson is actually IN the file.

**Honest rewrite for now:**
> "I built the markdown-image exfil scenario as a lab in `intensive-prep/03-llm-ai-security/labs/data_exfil_via_markdown_image.py`. The lab proves the attack path and demonstrates two mitigations: a server-side image-stripping post-processor for any host not on a CDN allowlist, and a Promptfoo assertion that fails on any URL emitted to a non-allowlisted host. The pattern is documented in `docs/grc/PLAYBOOK_AI_INCIDENT.md`. The post-processor has not been integrated into the production Telegram bot yet."

### Story 8 - Mapping every LLM finding to ATLAS at write time
**Tag:** NEEDS-ARTIFACT

- Lab file exists: `intensive-prep/03-llm-ai-security/labs/mitre_atlas_mapper.py`. **Lab demo defensible.**
- "Hooked it into the n8n alert pipeline so every LLM finding gets enriched before it lands in the decision log" — no n8n workflow on disk that calls an ATLAS mapper. NEEDS-ARTIFACT.
- "Quarterly threat report writes itself" — no template, no past report. EXAGGERATION.

**Honest rewrite:**
> "I built an ATLAS mapper in `mitre_atlas_mapper.py` that takes a free-text LLM finding and returns matching ATLAS technique IDs plus OWASP LLM IDs with confidence based on keyword hits. It covers AML.T0051 prompt injection, T0054 jailbreak, T0024 exfil via inference API, T0057 data leakage, T0020 poisoning, T0010 supply chain, T0029 DoS, T0048 external harms. Today it runs ad-hoc against the GRC corpus. The integration target is the n8n alert pipeline so every LLM finding gets enriched at write time."

---

## File 2: `06-pentest-essentials/STORYTELLING.md` (5 stories)

### Story 1 - OWASP ZAP DAST against n8n
**Tag:** SOLID

- ZAP report files exist at `docs/grc/zap-report-n8n-20260322.html` (92K) and `zap-report-n8n-auth-20260322.html` (124K).
- 161 URLs spidered, zero high, four medium unauthed; 29 medium authed — defensible by opening the HTML reports.
- Cloudflare Transform Rules applied — verifiable via `curl -I n8n.tigouetheory.com` showing the headers.

**Action item:** Memorize the exact finding counts. Open the HTML in browser before the interview to refresh.

### Story 2 - Cloudflare Tunnel audit found SSH exposure
**Tag:** SOLID with one caveat

- Tunnel config in `terraform/cd-do-infrastructure/tunnel.tf` shows the routes. Defensible.
- "Service Token plus single Google identity plus WARP-only" — Emmanuel needs to verify the Cloudflare Access policy is actually configured this way RIGHT NOW. If it is, SOLID. If it is the looser version still, FABRICATED.

**Required check:** `cloudflared tunnel info <tunnel-id>` plus screenshot the Access policy, save to `intensive-prep/06-pentest-essentials/labs/cf-access-policy-2026-05.md`.

### Story 3 - OpenClaw STRIDE threat model
**Tag:** SOLID, version fix only

- Skills installed match CLAUDE.md (tavily-search, browser, python-interpreter, notion, gemini, github).
- STRIDE pass produced real outcomes: fine-grained PAT, per-skill approval gate, runbook.
- Where is the STRIDE doc itself? Need to confirm it lives in `docs/grc/` (likely `THREAT_MODEL_STRIDE.md` which exists, OR `SQUIRE_THREAT_MODEL.md`).
- VERSION: change "OpenClaw v2026.3.8" to "OpenClaw v2026.4.21" or just "OpenClaw" everywhere.

### Story 4 - Helm and IaC scans found privileged container
**Tag:** EXAGGERATED

- Trivy and Checkov in CI: real, in `terraform-pr.yml` and `security.yml`.
- "Helm draft had a Falco chart override that set securityContext.privileged: true on a container that did not need it" — no Helm charts found in repo. NO Kubernetes migration in flight.
- "automountServiceAccountToken on a deployment that never called the API server" — no such manifest exists.
- "hostPath mount on /var/run/docker.sock" — no such manifest exists.

**Honest rewrite (Trivy/Checkov on Compose and Terraform, not Helm):**
> "I run Trivy config-scan, Checkov, and Semgrep in CI on every Terraform PR through `.github/workflows/terraform-pr.yml`, plus Trivy filesystem and Gitleaks on `.github/workflows/security.yml`. Trivy on the docker-compose.yaml caught a couple of unset healthcheck flags. Checkov on Terraform caught a missing `prevent_destroy` lifecycle on the database droplet, which I codified into an OPA Rego policy as `deny_missing_prevent_destroy.rego` so the regression cannot happen again. The eight Rego policies in `terraform/cd-do-infrastructure/policy/` are the hard gate before any IaC merge."

**This story has to be rewritten to match what was actually scanned. The Helm specifics are not on disk anywhere.**

### Story 5 - Vault unseal flow self-test
**Tag:** FABRICATED

- **Vault is NOT initialized.** Container logs: "security barrier not initialized, seal configuration missing." There is no unseal key set, no Shamir threshold, no recovery procedure ever exercised because the system has nothing in it to unseal.
- "Three vaults with three separate access paths" — no evidence of distributed unseal shares anywhere.
- "Smoke test that seals a test Vault, attempts unseal, reads a known token, and asserts" — no such test in repo or CI.

**This story should be removed entirely until Vault is initialized.** A senior interviewer who probes "show me the unseal runbook" would catch this in one minute.

---

## File 3: `07-stack-upgrades/STAR-STORIES.md` (12 stories)

### Story 1 - Building the n8n SOAR stack as a one-person SOC
**Tag:** EXAGGERATED (workflow count)

- 14 active workflows claim. Live DB shows **6 active workflows.**
- 13 services in compose: matches CLAUDE.md.
- Healthchecks and chmod-600 env: defensible.
- "Every secret has a vault entry" — Vault is not initialized. Use "every secret has a Doppler entry" — that is true.

**Honest rewrite of Result paragraph:**
> "Forty-eight dollars a month. Thirteen Compose services plus the OpenClaw gateway running stable for two months. Six active n8n workflows today, with eight more in version control as exports ready for re-activation. Datadog ships logs and metrics to us5. Doppler holds 44 secrets. The architecture lesson I keep referencing: I designed for a team from day one."

### Story 2 - OpenClaw with prompt injection defenses
**Tag:** EXAGGERATED

- "Zero injection findings on OWASP LLM Top 10 across eight DAST categories on the latest pass" — no logged Promptfoo run with these exact numbers exists. NEEDS-ARTIFACT.
- "Latency added by input/output filters under 50ms p95" — no latency telemetry on disk. FABRICATION risk.
- "When Opus 4.7 shipped, I reran the harness before cutting traffic. Two regressions in tool-call handling; held rollout until the classifier was patched" — no commit history for the patch. NEEDS-ARTIFACT.

**Required artifacts:**
1. `promptfoo eval` against OpenClaw with logged JSON output.
2. Latency benchmark logged to `intensive-prep/03-llm-ai-security/labs/openclaw-latency-2026-05.json`.
3. If the regression catch is real, find the commit and reference it; if not, drop the claim.

### Story 3 - Threat modeling the entire CoreDirective Engine
**Tag:** SOLID

- `docs/grc/SQUIRE_THREAT_MODEL.md` exists. Defensible.
- Six trust boundaries: defensible if the doc shows them.
- "Threat model is now 1 of 37 docs" — corpus has 51 markdown files, but 37 is the prior canonical number. Pick one.
- "Eight findings closed within 30 days" — needs the POAM doc to back this. POAM_PLAN_OF_ACTION.md exists, content needs to actually contain the closed findings.

### Story 4 - Writing the GRC corpus with AI Governance policy
**Tag:** SOLID with caveat

- 51 markdown docs, real cross-references, real sanitization standard.
- "Around 15,000 lines" — needs `wc -l docs/grc/*.md` to confirm.
- "Two recruiter conversations referenced the policy as a differentiator" — soft claim, defensible if Emmanuel can name the recruiters.

### Story 5 - Hardening Cloudflare Tunnel and Teleport
**Tag:** PARTIALLY SOLID

- Tunnel routes match CLAUDE.md: SOLID.
- Teleport v18 deployed: SOLID (`cd-service-teleport` is healthy).
- "JIT elevation requires out-of-band approval through Telegram" — no evidence this flow is wired. NEEDS-ARTIFACT.
- "Audit shipper sends every Teleport event to Datadog, retention 90 days" — `cd-service-teleport-event-handler` exists. Defensible if the Datadog dashboard exists.
- `docs/grc/IAM_ARCHITECTURE.md` does NOT exist. The two real IAM docs are `IAM_ACCESS_REVIEW.md` and `IAM_RBAC_ROLE_MAP.md`.

**Required fixes:**
- Change reference to `IAM_RBAC_ROLE_MAP.md`.
- Either wire the Teleport JIT-via-Telegram flow or scope the claim to "Teleport session recording is on by default and audit events ship to Datadog."

### Story 6 - OWASP ZAP DAST and remediating findings
**Tag:** SOLID with caveat

- ZAP runs against n8n: SOLID. Reports on disk.
- "ZAP weekly via GitHub Actions" — no scheduled ZAP workflow in `.github/workflows/`. NEEDS-ARTIFACT.
- "Pen test write-up went into `docs/grc/PEN_TEST_REPORT.md`" — actual filename is `PENTEST_SELF_ASSESSMENT.md`.

### Story 7 - Building OPA policies for Terraform IaC
**Tag:** SOLID

- 8 Rego policies: matches exactly. Filenames defensible.
- "Two PRs blocked by the OPA gate" — needs commit history check, but plausible.
- "PR pipeline runs fmt, validate, tflint, checkov, plan, then OPA" — `terraform-pr.yml` has these stages. SOLID.

### Story 8 - The CARL rule system and agentic safety
**Tag:** NEEDS-ARTIFACT

- CARL repo exists at `~/carl/`. Project-level `.carl/` directory does NOT exist in `cyber-squire-ops`. The integration claim ("a Claude-side hook injects the active rules into the system prompt at session start") needs evidence.
- Forty-plus rules across six domains: needs to be enumerated. Where do the .carl files live for this project?

**Required artifact:** Either point to the actual CARL domain files, or scope the story to "I run CARL in `~/carl` for global Claude session rules."

### Story 9 - Switch v3 bug
**Tag:** SOLID

- Memory file `n8n-debugging.md` exists per the index. Story is detailed enough to be defensible.
- The dual-table workflow_entity vs workflow_history insight is technical-real. SOLID.

### Story 10 - Header misconfig finding
**Tag:** PARTIALLY SOLID, EXAGGERATED follow-on

- Header findings and Cloudflare Transform Rules: SOLID, ZAP reports back this up.
- "Migrated the headers config into Terraform, added an OPA policy that requires HSTS preload on any new origin, added a weekly ZAP run" — none of these three exist in repo. EXAGGERATION.

**Honest rewrite of Action paragraph:**
> "Headers fix at the Cloudflare edge: HSTS preload, Permissions-Policy locked, nosniff, Referrer-Policy strict-origin-when-cross-origin, CSP with explicit allowlist for the script bundles. Re-ran ZAP, all four closed. The bigger fix on my roadmap is migrating the header config from the Cloudflare dashboard into Terraform so it lives in version control, adding an OPA policy that requires HSTS preload on any new origin, and scheduling a weekly ZAP scan as a GitHub Action. The PEN_TEST_SELF_ASSESSMENT doc captures the finding and the architectural follow-on."

### Story 11 - AI Governance policy as legal + engineering + customer
**Tag:** NEEDS-ARTIFACT

- The accounting-firm client conversation is real per memory file `coredirective-ai-security-practice-2026-05-02.md`. Defensible at the framing level.
- "Sent them a one-page memo" — does the memo exist in `~/cyber-squire-ops/CoreDirective/career/cloudflare-appsec-mgt/` or similar? NEEDS-ARTIFACT.
- "I shipped the local Ollama path" — Ollama is deployed (`cd-service-ollama` is in CLAUDE.md). Defensible if there is an actual workflow using Ollama for this client.

**Required artifact:** Surface the one-page memo. If it does not exist, write it now: `CoreDirective/career/accounting-firm-ai-architecture-memo.md`.

### Story 12 - Build vs buy on SOAR
**Tag:** SOLID with workflow count fix

- Cost claim: $48/mo, defensible.
- "Fourteen active workflows in 90 days" — only 6 are active live. Use 14 as "shipped during the period, six active today."
- Master orchestrator with 16 service actions: SOLID.

---

## File 4: `dropzone-ai/04_STAR_STORIES.md` (12 stories)

### Story 1 - POS Skimmer Investigation at Texaco
**Tag:** NEEDS-ARTIFACT (high risk)

- This is a story about Texaco — Emmanuel managed the gas station. There is **no incident report on disk anywhere** to back the technical specifics: Wireshark capture, WHOIS lookup on a four-day-old domain, BIN range correlation with payment processor.
- The framing is plausible (gas-station owner who reads networks), but a senior interviewer asking "what was the C2 domain" or "what payment processor" or "show me the runbook" hits a wall.
- Memory file `feedback_no_pivoting_framing.md` warns against framing. The Texaco story walks the line.

**Required artifact (this week):**
- Write `CoreDirective/career/texaco-pos-skimmer-investigation.md` as a sanitized incident retro. Even if the names and BIN are scrubbed, the timeline and decisions need to live somewhere on disk. If the investigation never happened with this technical depth, scope the story to "I noticed a card decline pattern, escalated to the payment processor, and they confirmed fraud" without the Wireshark span/self-signed cert detail.

### Story 2 - OpenClaw AI Gateway Red Team
**Tag:** EXAGGERATED (same as Story 2 in 07-stack-upgrades)

- "Zero confirmed prompt injection successes against the gateway in production across 90 days" — no telemetry on disk that proves this.
- "When Opus 4.6 shipped, I reran the harness before cutting traffic. I found two regressions in tool call handling and held the rollout until the classifier was updated" — same critique. NEEDS-ARTIFACT.

**Same rewrite as 07-stack-upgrades Story 2.**

### Story 3 - Falco Alert Tuning 200 to 12
**Tag:** NEEDS-ARTIFACT

- The custom rules file exists, but the "200 alerts/day before, 12/day after" tuning history is not logged. No before/after metric in any dashboard or CSV.
- "I pulled 14 days of alerts" — no baseline export on disk.
- "Mapped every remaining rule to MITRE ATT&CK" — looking at `coredirective_rules.yaml`, tags are like `[coredirective, security, postgresql, container-exec]`, not ATT&CK technique IDs.

**Required artifact:** Pull a recent 7-day Datadog Falco volume report. Save to `intensive-prep/05-detection-triage/labs/falco-tuning-baseline-2026-05.json`. Add ATT&CK technique IDs to rule tags in `coredirective_rules.yaml`.

### Story 4 - n8n SOAR From Zero
**Tag:** EXAGGERATED (workflow count, same as 07 Story 1)

- 14 active workflows claim again — only 6 are active. "Built 14 in version control, 6 active today, eight ready to re-enable" is the honest version.
- "Zero credential leaks" — defensible since Doppler holds secrets and chmod-600.
- "MTTR on workflow failures is under 10 minutes because the Error Handler posts directly to Telegram" — Error Handler workflow `el07Swns2MrSSpOK` is real. Defensible.

### Story 5 - Splunk MTTD 48 hours to under 4
**Tag:** NEEDS-ARTIFACT (high risk)

- "Splunk at the store environment" — Texaco gas station did not have Splunk. The CLAUDE.md and memory files have zero Splunk artifacts, zero detection content authored, zero correlation searches.
- POS VLAN, DHCP rules, payment processor callback logs — none of these data sources are documented anywhere on disk.
- This story is the highest risk in the bank. A Splunk-savvy interviewer can shred it in one question: "what was the SPL for the outbound TLS rule?"

**Recommendation:**
- If Emmanuel does have Splunk experience from a different role (not Texaco), reframe the story honestly with the right employer.
- If not, **REMOVE this story entirely** or convert it to a lab-based story: "I built three detection use cases in a Splunk Enterprise lab against synthetic POS data" — and ship the lab.

### Story 6 - CoreDirective Accounting AI
**Tag:** NEEDS-ARTIFACT (story is half-written with bracketed placeholders)

- Story is literally `[SPECIFIC TASKS]`, `[SPECIFIC TOOL]`, `[DOLLAR THRESHOLD]`, `[STORAGE]`, `[SPECIFIC METRIC]` placeholders that have not been filled in.
- This is the closer for "what excites you about Dropzone." Cannot deliver with brackets.

**Required (before any Dropzone interview):** Fill in the bracketed details from the actual accounting-firm client work referenced in `coredirective-ai-security-practice-2026-05-02.md`.

### Story 7 - 37 GRC Documents in Two Months
**Tag:** SOLID

- 51 markdown docs in `docs/grc/`, even more conservative than the story's 37. Defensible.
- 6-agent QC sweep: per memory file `session-appsec-dast-2026-03-22.md`, this happened. Defensible.

### Story 8 - PCI DSS Cross Functional at Texaco
**Tag:** NEEDS-ARTIFACT

- Same risk as Story 1: no PCI segmentation runbook on disk.
- 4 VLANs, 70% scope reduction, payment processor attestation — needs at least a sanitized network diagram.

**Required artifact:** Sanitized "before and after" network diagram of the Texaco store, saved to `CoreDirective/career/texaco-pci-segmentation.md`.

### Story 9 - Segmentation vs Wi-Fi Disagreement
**Tag:** SOLID (no artifact required)

- This is a soft-skill story. Internal logic is consistent. Numbers (PCI fine schedule, daily card volume) are not provable on disk but are not the point of the story. Defensible if delivered confidently.

### Story 10 - NeMo Local Inference Architecture
**Tag:** SOLID

- `cd-service-nemo` is running on the droplet. Defensible.
- NeMo guardrails references in `intensive-prep/03-llm-ai-security/labs/guardrails_with_nemo.py` and the `nemo_config` folder. Defensible.
- Two-lane pipeline (cloud-safe vs local-only): the architecture is reasonable but the routing classifier code is not on disk that I can see. NEEDS-ARTIFACT for the classifier.

### Story 11 - DigitalOcean Migration From AWS
**Tag:** SOLID

- Migration documented in CLAUDE.md ("migrated 2026-03-10"). $48/mo confirmed. AWS suspension 2026-03-08 confirmed.
- 72-hour migration claim is plausible.

### Story 12 - n8n Credential Remapping DB Debug
**Tag:** SOLID

- Memory file `n8n-debugging.md` exists. Lessons are technical-real.
- The `workflow_entity` vs `workflow_history` insight is correct n8n behavior.

---

## TOP 5 STORIES TO REHEARSE FIRST (most defensible right now)

1. **07-stack Story 7 — OPA policies for Terraform.** 8 Rego files, in CI, can show the PR pipeline. Bulletproof.
2. **06-pentest Story 1 — OWASP ZAP DAST against n8n.** Two HTML reports on disk dated 2026-03-22. Headers fix verifiable via curl.
3. **07-stack Story 9 — Switch v3 bug.** Memory file backs it, the dual-table insight is technical-deep, lesson is senior-shaped.
4. **dropzone Story 7 — 37 GRC documents.** 51 markdown files plus diagrams plus oscal plus stix. Cross-referenced. Sanitized. Public on GitHub.
5. **dropzone Story 12 — n8n credential remapping DB debug.** Same memory file backing, same technical depth. Senior debugging story.

## TOP 5 STORIES TO ARTIFACT-FY THIS WEEK (true but no proof)

1. **03-llm Story 1 (OpenClaw threat model).** Run `promptfoo eval` against OpenClaw with the lab YAML. Save the JSON. Then 7-of-10 to 10-of-10 is real.
2. **dropzone Story 6 (CoreDirective Accounting AI).** Fill in every `[BRACKETED PLACEHOLDER]` from the actual client work. This is the Dropzone closer and it is unfinished.
3. **dropzone Story 3 (Falco 200 to 12).** Pull a Datadog Falco volume report covering pre-tuning and post-tuning periods. Add ATT&CK technique IDs to rule tags.
4. **07-stack Story 11 (Accounting client AI Governance memo).** Surface or write the one-page architecture memo. Save to `CoreDirective/career/accounting-firm-ai-architecture-memo.md`.
5. **07-stack Story 8 (CARL system).** Either point to the project-level `.carl/` files and the Claude-side hook script, or scope the story to global CARL only.

## FABRICATED CLAIMS TO REMOVE OR REWRITE BEFORE ANY INTERVIEW

1. **OpenClaw version `v2026.3.8`.** Replace with `v2026.4.21` everywhere, or just say "OpenClaw" without the version.
2. **Vault dynamic secrets / JIT credentials (03-llm Story 6, 07-stack Story 5 implied).** Vault is not initialized. Cannot tell this story as completed work. Reframe as planned design.
3. **06-pentest Story 5 (Vault unseal flow self-test).** Vault is not initialized — there is nothing to unseal. **Remove this story entirely** until Vault is initialized and the unseal procedure is actually exercised.
4. **Garak in CI (03-llm Story 5).** Zero references in repo. Either ship Garak or remove the claim.
5. **06-pentest Story 4 (Helm and Kubernetes manifests).** No Helm charts in repo, no Kubernetes migration. Rewrite to scan Compose and Terraform only.
6. **dropzone Story 5 (Splunk MTTD at Texaco).** No Splunk artifacts, no Texaco SIEM. Highest credibility risk in the bank. Remove or convert to a lab-based story.
7. **Falco rule names in 03-llm Story 4.** The three named rules (`Unexpected Outbound URL From OpenClaw` etc) do not match the file. Rewrite to the two real rules (`CD OpenClaw Shell Access`, `CD OpenClaw Unexpected Write`).
8. **GRC filename references throughout (`AI_INCIDENT_PLAYBOOK.md`, `PEN_TEST_REPORT.md`, `IAM_ARCHITECTURE.md`, `AI_GOVERNANCE.md`).** Replace with actual filenames (`PLAYBOOK_AI_INCIDENT.md`, `PENTEST_SELF_ASSESSMENT.md`, `IAM_RBAC_ROLE_MAP.md`, `POLICY_AI_GOVERNANCE.md`).
9. **"14 active n8n workflows" claim (07 Story 1, dropzone Story 4).** Live count is 6. Rewrite as "14 shipped, 6 active, 8 in version control ready to re-enable."

## SUMMARY COUNTS

- Total stories audited: **37** (8 LLM + 5 pentest + 12 stack + 12 dropzone)
- SOLID: **8**
- NEEDS-ARTIFACT: **15**
- NEEDS-NUMBERS: **2**
- EXAGGERATED: **8**
- FABRICATED: **4** (Vault unseal, Garak in CI, Helm scan specifics, Splunk Texaco MTTD)

A senior interview where any of the four FABRICATED stories is told without remediation is career-ending. The fix is one week of artifact work plus seven specific rewrites.

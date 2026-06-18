# AUDIT 05 — Pipeline Alignment

Audit date: 2026-05-08
Auditor: parallel research agent
Curriculum under review: `/Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/00..07`
Pipeline source: `/Users/et/cyber-squire-ops/CoreDirective/career/{dropzone-ai, onedigital, amex-experis, cloudflare-appsec-mgt, insight-global-aisec, qgenda, milestone-tech}` plus MEMORY.md

This audit answers one question per role: can Emmanuel walk into the next round and survive on what he already has on disk? Coverage is rated *Covered* (curriculum + prep folder hit it cold), *Partial* (concept covered, vendor surface or depth missing), *Missing* (nothing on disk).

---

## 1. Dropzone AI — Senior Security Engineer

**JD source:** `dropzone-ai/00_JOB_DESCRIPTION.md` (locked 2026-04-28). Tech round 2026-05-07 with Eric Hammerle (Director of Engineering). Take-home passed 2026-04-28. Status as of audit: technical interview happened yesterday, panel + founder rounds likely next.

### Top 10 must-have skills

1. Production Python (LangChain/LangGraph patterns, async, type hints)
2. Investigation flow design for AI SOC analyst
3. AWS detection logic (CloudTrail, GuardDuty, IAM kill chains)
4. Prompt injection + jailbreak handling inside investigation pipelines
5. MITRE ATT&CK + ATLAS mapping
6. SOAR / detection-as-code mindset
7. Threat hunting hypothesis generation
8. False-positive tuning, alert fatigue management
9. Tool integration (security tool API plumbing)
10. Architectural judgment + technical leadership

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Production Python | Covered | `01-code-fluency/ROADMAP.md` 14 days, LangGraph by day 14; `01-code-fluency/labs/` |
| Investigation flow design | Covered | `05-detection-triage/ROADMAP.md` Day 12 "AI-Augmented Triage (the Dropzone use case)" + lab_10/lab_11; `dropzone-ai/11_TAKE_HOME_DEFENSE.md` |
| AWS detection | Covered | `02-aws-security/ROADMAP.md` Days 13, 14, 20, 21; `05-detection-triage/ROADMAP.md` Day 2 (lab_02_aws_credential_exfil) |
| Prompt injection / jailbreak | Covered | `03-llm-ai-security/ROADMAP.md` Days 1-4 + Day 7 agentic abuse; `03-llm-ai-security/labs/prompt_injection_basic.py`, `indirect_injection_via_tool.py`, `agentic_tool_abuse.py` |
| MITRE ATT&CK + ATLAS | Covered | `05-detection-triage/ROADMAP.md` Days 6-7; `03-llm-ai-security/ROADMAP.md` Day 10 |
| SOAR / detection-as-code | Covered | `05-detection-triage/ROADMAP.md` Day 11; `07-stack-upgrades/ROADMAP.md` Upgrade A (Promptfoo CI), Upgrade J (LangGraph triage on Falco) |
| Threat hunting hypothesis | Covered | `05-detection-triage/ROADMAP.md` Days 8-9 |
| FP tuning / alert fatigue | Covered | `05-detection-triage/ROADMAP.md` Day 10 |
| Tool integration plumbing | Partial | `01-code-fluency/labs/` covers HTTP, but no concrete lab on building a security tool integration end to end |
| Architectural judgment | Partial | `00-market-truth/SYSTEM-DESIGN-FOR-SEC-ENG.md` covers concepts; no Dropzone-specific architecture drill |

### Role-specific gaps

- **No "Dropzone-style triage flow" reference architecture.** Day 12 of detection-triage names the pattern but does not make Emmanuel sketch the full pipeline (alert ingest → enrichment fan-out → LLM investigator → human-in-the-loop → report writeback). Add a 30-minute drill to `dropzone-ai/14_FINAL_CHART.md` peer.
- **LangChain + Moto pattern from take-home not folded into curriculum.** The take-home was LangChain + boto3 + Moto + AWS Q&A bot. The 01 code-fluency LangGraph track does not loop back to that exact pattern.
- **Eric Hammerle deep dive lives in `dropzone-ai/09_ERIC_HAMMERLE_INTEL.md` not in the curriculum.** That is correct location, just flagging it as the canonical source.

### Prep sequence (assuming panel round in 5-7 days)

1. Today: re-read `dropzone-ai/14_FINAL_CHART.md`, `13_MAY7_MORNING_BRIEF.md`, `10_TECHNICAL_ROUND_GAMEPLAN.md`. Capture every question Eric asked yesterday in a new `15_TECH_ROUND_DEBRIEF.md` while it is fresh.
2. Day 2-3: `05-detection-triage` Day 12 lab end to end. Then `03-llm-ai-security` Day 11 (LLM log triage agent — this is the Dropzone demo).
3. Day 3-4: `01-code-fluency` Days 11-14 (LangChain → LangGraph). Re-implement the take-home solution from memory in 2 hours flat.
4. Day 5-6: `04-threat-modeling/HIS-STACK.md` + `03-llm-ai-security/THREAT-MODELS.md` Model 2 (internal SOC triage agent). Whiteboard out loud, recorded.
5. Day 7: mock panel. Pull questions from `03-llm-ai-security/INTERVIEW-Qs.md` + `05-detection-triage/INTERVIEW-Qs.md`.

### Readiness: 88%

Strongest role in the pipeline. Curriculum + prep folder are the most complete here. Take-home already passed. The remaining 12% is execution under panel pressure and one missing reference architecture drill.

---

## 2. Resilience N8N Engineer

**Status:** Interview happened 2026-04-09. No update folder content since. MEMORY.md `resilience-interview-2026-04-09.md` says interview occurred. Thank-you email sent (`resilience-thank-you-email.txt`).

### Read

If status is silent for 4+ weeks, treat as cooled. Skip from active prep until recruiter responds. Curriculum already covers the n8n agentic workflow story (`07-stack-upgrades` Upgrade B, J; `03-llm-ai-security` Day 7).

### Readiness: N/A (post-interview, awaiting status)

No prep gaps to close. If they re-open, the n8n + LLM guardrails story in `07-stack-upgrades/PIPELINE-MAPPING.md` is ready.

---

## 3. Insight Global — AI Security Engineer (1yr remote contract)

**JD source:** `insight-global-aisec/00_JOB_DESCRIPTION.md`. Recruiter screen with Savannah Daoust scheduled Mon 2026-05-05. Status as of audit: recruiter call should have happened, no update file yet.

### Top 10 must-have skills

1. Microsoft Security Copilot (hands-on)
2. Microsoft Defender for Cloud
3. Microsoft Sentinel + KQL
4. Microsoft Entra ID + Conditional Access
5. AI governance frameworks (NIST AI RMF, ISO 42001, EU AI Act)
6. MLOps pipelines + model registries (MLflow, AzureML)
7. Adversarial ML / threat intel
8. Offensive AI usage (PyRIT, Garak, Counterfit class tools)
9. AI red teaming methodology
10. Continuous monitoring of AI services

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Microsoft Security Copilot | Missing | No file. Acknowledged gap in `insight-global-aisec/02_ROLE_FIT.md` |
| Defender for Cloud | Missing | Same as above |
| Sentinel + KQL | Missing | One mention of KQL conversion in `05-detection-triage/ROADMAP.md` Day 13 (whirlwind only) |
| Entra ID + Conditional Access | Missing | Mentioned only as "SCIM from Okta or Entra ID" in `02-aws-security/ROADMAP.md` |
| AI governance frameworks | Covered | `03-llm-ai-security/ROADMAP.md` Day 12; `03-llm-ai-security/CHEATSHEET.md` governance section |
| MLOps + model registries | Partial | `02-aws-security/ROADMAP.md` Day 21 covers SageMaker registry; MLflow + AzureML registry not covered |
| Adversarial ML / threat intel | Covered | `03-llm-ai-security/ROADMAP.md` Days 4-9; Day 6 supply chain + poisoning |
| Offensive AI tools (PyRIT/Garak) | Partial | Garak named on Day 9; PyRIT named in CHEATSHEET; no actual lab using PyRIT |
| AI red teaming methodology | Covered | `03-llm-ai-security/ROADMAP.md` Day 9 + `06-pentest-essentials/ROADMAP.md` Day 19 |
| Continuous monitoring | Covered | `05-detection-triage` full track |

### Role-specific gaps

- **Microsoft stack vacuum.** The curriculum is AWS-heavy by design (`02-aws-security` is 21 days, no Azure equivalent exists). Insight Global lists MS Security Copilot and Defender for Cloud as must-haves verbatim. Bridge statement is good (`insight-global-aisec/02_ROLE_FIT.md`) but no hands-on. Recommend adding a 7-day Azure-Microsoft ramp before the technical screen if recruiter passes Emmanuel through.
- **Missing artifact: Azure security cheat sheet.** Need a one-pager mapping AWS service → Azure equivalent (CloudTrail → Activity Log, GuardDuty → Defender for Cloud, SecurityHub → Defender for Cloud Security Posture, IAM → Entra ID, Secrets Manager → Key Vault, Config → Azure Policy + Defender for Cloud).
- **No KQL lab.** sigma-cli converts to KQL on Day 13 of detection-triage. Need an actual KQL drill (10 queries against synthetic Sentinel data).

### Prep sequence

1. Tonight (if recruiter advanced him): write `insight-global-aisec/06_AZURE_RAMP.md` covering Defender for Cloud, Sentinel, Security Copilot, Entra at the architecture level. 90 min.
2. Day 2-4: KQL drill — 10 hunting queries (failed sign-ins, impossible travel, suspicious mailbox forwarding, brute force, anomalous role assumption, M365 audit log queries). 60 min/day.
3. Day 5: Microsoft Learn "Security Copilot architecture" + "Defender for Cloud overview" reading. 90 min.
4. Day 6-7: `03-llm-ai-security` Days 9-12 review for AI governance framing.
5. Day 8: mock screen using `insight-global-aisec/05_MASTER_FRAMING.md` plus the gap reframes from `02_ROLE_FIT.md`.

### Readiness: 55%

The AI governance and offensive AI half is strong. The Microsoft vendor surface gap is real and material. He clears recruiter screen on the bridge story, fails a hands-on technical without 5-7 days of Microsoft ramp.

---

## 4. WBD Cybersec Engineer (AI Focused) — Job 34698-1

**Source:** `milestone-tech/03_STUDY_LIST.md`, MEMORY.md `wbd-milestone-2026-05-07.md`. $85/hr W2, 6mo hybrid 3d ATL. Submittal package ready, tracker priority 7.

### Top 10 must-have skills

1. Bedrock Guardrails policy schema + ApplyGuardrail API
2. Bedrock IAM scoping (model resource ARNs, VPC endpoints)
3. AI guardrails / prompt injection defense
4. OWASP LLM Top 10, MITRE ATLAS
5. Databricks Unity Catalog + MLflow Model Registry
6. EU AI Act conformity assessment + Annex III
7. AI-SPM vendor landscape (Wiz, Lakera, Prompt Security, Protect AI, Aim Security)
8. ChatGPT Enterprise admin controls
9. AI Incident Response playbook
10. Agentic AI threat patterns (excessive agency, tool abuse)

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Bedrock Guardrails | Partial | `02-aws-security/ROADMAP.md` Day 21 names them; not deep on policy schema |
| Bedrock IAM scoping | Partial | IAM track is strong; Bedrock-specific resource ARNs not drilled |
| AI guardrails / prompt injection | Covered | `03-llm-ai-security` Days 1-4, 9 |
| OWASP LLM Top 10 + ATLAS | Covered | `03-llm-ai-security` Days 1, 10 |
| Databricks Unity Catalog | Missing | Zero curriculum content |
| MLflow Model Registry | Missing | Zero curriculum content |
| EU AI Act Annex III | Partial | `03-llm-ai-security/CHEATSHEET.md` names tiers; no Annex III drill |
| AI-SPM vendor landscape | Partial | Lakera, Robust Intelligence named in CHEATSHEET; no comparative drill |
| ChatGPT Enterprise admin | Missing | Zero curriculum content |
| AI IR playbook | Covered | `docs/grc/PLAYBOOK_AI_INCIDENT.md` exists in repo |
| Agentic threat patterns | Covered | `03-llm-ai-security` Day 7 |

### Role-specific gaps

The `milestone-tech/03_STUDY_LIST.md` already names every gap correctly and proposes 12 hours of Tier 1+2+3 reading. That study list is the prep sequence. Curriculum does not duplicate, and should not.

### Prep sequence

Use `milestone-tech/03_STUDY_LIST.md` as the canonical plan. Map curriculum back-fills:

1. Tier 1 (4 hrs) — read external docs as prescribed.
2. Curriculum back-fill: `03-llm-ai-security/ROADMAP.md` Days 6-7 cover supply chain + agentic risk and pair with the Bedrock Guardrails reading.
3. Curriculum back-fill: `02-aws-security/ROADMAP.md` Day 21 in parallel with Bedrock IAM read.
4. Tier 2 (6 hrs) — external docs as prescribed.
5. Live-fire artifacts named in `milestone-tech/03_STUDY_LIST.md` are already shipping in the repo (eval_reviewer, budget_guard, sanitize_output, AI IR playbook).

### Readiness: 65%

Strong on AI security concepts and live artifacts. Weak on Databricks + MLflow + ChatGPT Enterprise. Tier 1 reading closes the recruiter-screen gap; Tier 2 needed before HM round. Skip Tier 3 until scheduled.

---

## 5. Brilliant / Candescent Cloudflare Engineering C2H

**JD source:** `cloudflare-appsec-mgt/03_TECHNICAL_PREP.md` (heat map already done). $85/hr 6mo Sandy Springs. Recruiter screen passed, awaiting HM round.

### Top 10 must-have skills

1. Cloudflare Zero Trust Tunnel + Access architecture
2. WAF Custom Rules expression engine
3. Terraform Cloudflare provider (v4 vs v5)
4. Request flow at the edge (DDoS → WAF → rate limit → bot → workers → cache → origin)
5. Rate Limiting Rules vs Advanced Rate Limiting
6. Cloudflare Workers + KV + R2 + Pages
7. mTLS at edge or origin
8. Bot Management + API Shield
9. DNSSEC + DNS records
10. Logpush / observability

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Tunnel + Access architecture | Covered | Real production posture documented in `cloudflare-appsec-mgt/03_TECHNICAL_PREP.md`; lives in repo `terraform/cd-do-infrastructure/tunnel.tf` |
| WAF Custom Rules | Covered | Five real rules in production, documented in prep folder |
| Terraform CF provider | Covered | Real `cloudflare/cloudflare ~> 4.52` posture, prep folder names v4/v5 differences |
| Request flow | Covered | Memorization block in `cloudflare-appsec-mgt/03_TECHNICAL_PREP.md` |
| Rate limiting | Covered | Live ruleset on `/webhook/*` |
| Workers + KV + R2 + Pages | Missing | Heat map says RED, zero Workers code |
| mTLS at edge or origin | Partial | Concept covered in role-fit. Origin connects plain HTTP from tunnel — gap acknowledged |
| Bot Management + API Shield | Missing | Heat map RED |
| DNSSEC | Missing | Heat map RED |
| Logpush | Missing | Heat map RED |

### Role-specific gaps

- **Workers gap is the biggest.** AppSec engineering at Cloudflare expects you to write Workers. Even one published Worker on a personal domain closes 80% of the gap. `07-stack-upgrades/ROADMAP.md` does not include a Workers upgrade.
- **Curriculum gap, not prep folder gap.** The Cloudflare prep folder is one of the strongest in the pipeline (10 numbered files, mock interview prompt, deep strategy doc). Curriculum can stay AWS-heavy because the Cloudflare role lives entirely in the prep folder.
- **mTLS origin.** Heat map RED. Add a 1-day upgrade — terminate mTLS at origin via Cloudflare Authenticated Origin Pulls. Concrete and shippable.

### Prep sequence

The Cloudflare prep folder is self-contained. Run it in order:

1. Re-read `00_INDEX.md`, `09_INTERVIEW_STRATEGY_DEEP.md`, `10_RESUME_DEFENSE.md`.
2. Drill `03_TECHNICAL_PREP.md` request-flow memorization out loud daily.
3. Mock interview using `MOCK_INTERVIEW_PROMPT.md` against Claude or human.
4. Curriculum touch: `06-pentest-essentials/ROADMAP.md` Day 1 (HTTP / CORS / SameSite). Rest is not Cloudflare-specific.
5. Optional shippable: spin up one Worker on `tigouetheory.com` that does request signature validation. 2 hours, closes the biggest gap.

### Readiness: 78%

Prep folder quality is high. Workers gap is real but acknowledged. Bot Management + API Shield gaps are also acknowledged with the "do not volunteer" rule. Honest 78% if HM is reasonable; 65% if HM expects Workers fluency.

---

## 6. QGenda — Mid-Level Security Engineer

**JD source:** `qgenda/STUDY_LIST.md`, `qgenda/CHEAT_CARD.md`, `qgenda/SCORECARD.md`. $115K base remote, AWS + HIPAA, Hearst-owned healthcare SaaS.

### Top 10 must-have skills

1. AWS Security Hub + GuardDuty + Inspector + Config aggregation
2. AWS Organizations + SCPs + Control Tower
3. KMS key policies + multi-account
4. HIPAA Security Rule technical safeguards
5. CNAPP landscape (Wiz vs Sysdig vs Orca vs Lacework)
6. Container security depth (K8s admission, pod security)
7. Vulnerability management at SaaS scale (Qualys, Tenable)
8. SOC 2 Type II evidence
9. DevSecOps pipeline (Trivy, Semgrep, Gitleaks, Cosign)
10. Threat modeling for healthcare scheduling API

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Security Hub aggregation | Covered | `02-aws-security/ROADMAP.md` Day 14; `02-aws-security/labs/securityhub_aggregation.md` |
| Organizations + SCPs | Covered | `02-aws-security/ROADMAP.md` Day 18; `labs/multi_account_scp_examples.md` |
| KMS policies + multi-account | Covered | `02-aws-security/ROADMAP.md` Days 6-7 |
| HIPAA technical safeguards | Partial | HIPAA referenced in multiple curriculum files but no dedicated drill on the four technical safeguards |
| CNAPP landscape | Partial | Named in `00-market-truth/EMERGING-TOPICS-2026.md` and `qgenda/STUDY_LIST.md`; no comparative drill in curriculum |
| Container security | Covered | `02-aws-security/ROADMAP.md` Day 11 EKS pod security; `06-pentest-essentials/ROADMAP.md` Day 18 |
| Vuln management at scale | Partial | Concepts in `00-market-truth/EMERGING-TOPICS-2026.md`; no SLA-band drill |
| SOC 2 evidence | Partial | `qgenda/STUDY_LIST.md` lists 30 min reading; curriculum does not cover SOC 2 specifically |
| DevSecOps pipeline | Covered | Real production posture; `07-stack-upgrades` evidence |
| Healthcare API threat model | Missing | Need the 1-page threat model the prep folder calls "worth more than any cert" |

### Role-specific gaps

- **HIPAA Security Rule deep dive missing.** Curriculum mentions HIPAA but does not walk the four technical safeguards (access control, audit, integrity, transmission). Reading is in `qgenda/STUDY_LIST.md` Tier 1 item 4. Take it.
- **The "1-page healthcare threat model" exercise is the differentiator.** `qgenda/STUDY_LIST.md` says it is worth more than any cert. Not done yet. 90 min to ship.
- **Splunk ES warning is correct.** RED ZONE: do not bluff Splunk Enterprise Security. Texaco was vanilla Splunk.

### Prep sequence

`qgenda/STUDY_LIST.md` is the plan. Total 9 hours over 7 days. Curriculum back-fills:

1. AWS multi-account drilling: `02-aws-security/ROADMAP.md` Days 17-18.
2. Container depth: `02-aws-security/ROADMAP.md` Day 11.
3. Healthcare threat model: `04-threat-modeling/PROCESS.md` + `04-threat-modeling/HIS-STACK.md` as reference shape, then build the QGenda-style model in 90 min.

### Readiness: 70%

AWS native side is strong. HIPAA reading + healthcare threat model artifact + CNAPP comparison are the three closing items. All shippable in 7 days at 75 min/day per `qgenda/STUDY_LIST.md`.

---

## 7. Amex Experis — AppSec

**JD source:** `amex-experis/03_TECHNICAL_PREP.md`. $55/hr Phoenix. Resume submitted 2026-04-21. CISO Reznik. TRIS program. Payment flow threat model is the centerpiece.

### Top 10 must-have skills

1. Payment flow threat modeling (CNP, tokenization, 3DS)
2. PCI DSS v4.0 requirements 3, 4, 6, 10, 11, 12
3. OWASP Top 10 2021 with PCI overlap
4. OAuth + JWT pitfalls
5. mTLS for service-to-service
6. SAST / DAST / SCA pipeline
7. Threat modeling output for executive audience
8. Third-party / supply chain (A08, 2024 merchant breach context)
9. WAF + DDoS at payment endpoints
10. Audit log integrity (HMAC chains, write-once storage)

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Payment flow threat modeling | Covered | `04-threat-modeling/drills/drill_05_payment_processing.md`; `amex-experis/03_TECHNICAL_PREP.md` Part 1 |
| PCI DSS v4.0 | Partial | Named throughout; no PCI-specific drill in curriculum. `amex-experis/03_TECHNICAL_PREP.md` covers it |
| OWASP Top 10 | Covered | `06-pentest-essentials/ROADMAP.md` Days 1-14 |
| OAuth + JWT | Covered | `06-pentest-essentials/ROADMAP.md` Days 3, 8; `06-pentest-essentials/labs/lab_06_jwt_none_alg_bypass`, `lab_07_oauth_redirect_uri_abuse` |
| mTLS service-to-service | Partial | Concept-level in `04-threat-modeling`; no concrete lab |
| SAST/DAST/SCA pipeline | Covered | `07-stack-upgrades/ROADMAP.md` Upgrade A, H; real production posture |
| Threat modeling for executives | Covered | `04-threat-modeling/ROADMAP.md` Day 10 + `ARTICULATION.md` |
| Third-party / supply chain | Covered | `06-pentest-essentials/ROADMAP.md` Day 13 |
| WAF + DDoS | Covered | `02-aws-security/ROADMAP.md` Day 15 + Cloudflare prep folder |
| Audit log integrity | Partial | Mentioned in threat modeling docs; no HMAC-chain drill |

### Role-specific gaps

- **PCI DSS v4.0 specifics.** Curriculum names PCI but does not walk requirements 3, 4, 6, 10, 11, 12 with the same crispness as the Amex prep folder. The Amex prep folder closes this.
- **Tokenization vs encryption confusion.** No drill on when to tokenize vs encrypt the PAN. The Amex prep folder lays it out but a drill question would help.
- **TRIS program research.** Lives in MEMORY.md `amex-experis-darren-2026-04-21.md`. Need to make sure CISO Reznik / TRIS / Blue Box Values are surfaced into the prep folder.

### Prep sequence

1. Re-read `amex-experis/03_TECHNICAL_PREP.md`, `06_MASTER_FRAMING.md`.
2. Drill `04-threat-modeling/drills/drill_05_payment_processing.md` out loud, 30 min.
3. PCI DSS v4.0 cheat sheet: read PCI DSS Quick Reference Guide v4.0.1 (PDF on PCI SSC site), 60 min.
4. `06-pentest-essentials/ROADMAP.md` Days 8 (Auth attacks) + 13 (Supply chain) refresh.
5. Mock the question: "Walk me through threat modeling a card-not-present payment flow using STRIDE." Record yourself.

### Readiness: 75%

Strong on AppSec foundations and the payment flow story. PCI DSS specifics need a 60-min refresh before the call. Curriculum + prep folder do this together.

---

## 8. OneDigital FTS — AI Security Engineer

**JD source:** `onedigital/02_ROLE_FIT.md`. Vendor stack: Snyk + Salt Security + CrowdStrike AIDR + Qualys + Microsoft Entra. Pavel is HM.

### Top 10 must-have skills

1. AI architecture + Zero Trust integration with Entra ID + PRMFA
2. Snyk SAST/SCA + DAST tooling fluency
3. Salt Security (API discovery, posture, runtime protection)
4. CrowdStrike Falcon + AIDR
5. Qualys vulnerability management
6. AI governance authoring (NIST AI RMF, ISO 42001)
7. CI/CD shift-left controls
8. Cloudflare Zero Trust patterns (he has)
9. Container hardening + image signing
10. Live evidence demonstration of production AI security

### Curriculum coverage

| Must-have | Curriculum coverage | File anchor |
|---|---|---|
| Entra ID + PRMFA | Missing | Same Microsoft gap as Insight Global. Bridge story in `onedigital/02_ROLE_FIT.md` |
| Snyk fluency | Partial | `onedigital/02_ROLE_FIT.md` reframes Trivy + Semgrep + Gitleaks → Snyk Code/Container/Open Source. No Snyk hands-on |
| Salt Security | Missing | One pass on API security in `06-pentest-essentials/ROADMAP.md` Day 15 (OWASP API Top 10). No Salt-specific content |
| CrowdStrike AIDR | Missing | No curriculum content. AIDR is the AI Detection and Response wedge of Falcon |
| Qualys | Partial | Mentioned in `qgenda/STUDY_LIST.md`. No drill |
| AI governance | Covered | `03-llm-ai-security/ROADMAP.md` Day 12 |
| CI/CD shift-left | Covered | Real production posture |
| Cloudflare Zero Trust | Covered | `cloudflare-appsec-mgt/` folder |
| Container hardening | Covered | `02-aws-security/ROADMAP.md` Day 11; `07-stack-upgrades/ROADMAP.md` Upgrade H |
| Live AI security evidence | Covered | `04-threat-modeling/HIS-STACK.md`; 37 GRC docs; n8n SOAR |

### Role-specific gaps

- **API security depth via Salt's lens missing.** Day 15 of pentest covers OWASP API Top 10 but does not frame it through API discovery / posture / runtime protection (Salt's three-product split). Add a 60-min reframe to the OneDigital prep folder.
- **CrowdStrike AIDR is a topic Emmanuel cannot fake.** AIDR is recent (CrowdStrike Falcon AI Detection and Response). Read the CrowdStrike AIDR product page + one analyst note, 30 min total. The reframe: Falco eBPF + Datadog is the OSS analog.
- **No Snyk hands-on.** Free tier Snyk against one repo, 30 min. Closes the credibility gap.

### Prep sequence

1. Re-read `onedigital/02_ROLE_FIT.md` end to end. Drill the four gap reframes (Entra, Snyk, Salt, CrowdStrike) out loud.
2. Free-tier Snyk against `cyber-squire1` public repo, 30 min.
3. Read CrowdStrike AIDR product overview + one analyst note, 30 min.
4. Read Salt Security "API Security 101" + one Salt + Falcon Foundry integration page, 45 min.
5. Microsoft Entra Conditional Access overview, 45 min.
6. `03-llm-ai-security/ROADMAP.md` Day 12 governance refresh.
7. Mock with `onedigital/09_CLAUDE_PRACTICE.md`.

### Readiness: 60%

Strongest gap reframes in the entire pipeline (Pavel-grade). Vendor surface gap is the same Microsoft gap as Insight Global plus three more vendors (Snyk, Salt, CrowdStrike). Closeable in 4-5 hours of vendor docs reading. Curriculum does not need to expand for this role; the prep folder owns it.

---

## 9. NICE Ltd — Matt Jacobs (CLOSED 2026-05-02)

Skip per instructions.

---

# ROLES RANKED BY READINESS

| Rank | Role | Readiness | Key driver |
|---|---|---|---|
| 1 | Dropzone AI | 88% | Take-home passed, panel quality prep folder, curriculum hits every must-have |
| 2 | Brilliant Cloudflare | 78% | Production Cloudflare posture, deepest single role prep folder |
| 3 | Amex Experis | 75% | AppSec foundations + payment-flow drill done |
| 4 | QGenda | 70% | AWS-strong, HIPAA + CNAPP gap identified and small |
| 5 | WBD Milestone | 65% | Concepts strong, Databricks + MLflow + ChatGPT Enterprise gaps real |
| 6 | OneDigital | 60% | Best gap reframes, but four vendor surfaces to skim |
| 7 | Insight Global | 55% | Microsoft stack vacuum is biggest in pipeline |
| - | Resilience | N/A | Post-interview, awaiting status |
| - | NICE | CLOSED | Skip |

---

# ROLES NEEDING IMMEDIATE GAP-FILL

In priority order based on calendar pressure plus gap size:

1. **Dropzone AI** — panel/founder rounds likely this week. Tech round just happened. Debrief is the single most valuable artifact (`dropzone-ai/15_TECH_ROUND_DEBRIEF.md`). Write it today while fresh.
2. **Insight Global** — recruiter screen 2026-05-05 (yesterday). If Savannah passes him forward, the Microsoft Azure 7-day ramp must start today. Biggest single curriculum gap.
3. **OneDigital** — Pavel is the HM. Vendor surface ramp is 4-5 hours. Cheap to close, high return.

---

# CALENDAR-AWARE PRIORITY (this week)

Assume Dropzone panel + Insight Global advance + OneDigital HM screen all could fire 2026-05-09 to 2026-05-15. Sequence the 7-day prep:

| Day | Block 1 (90 min) | Block 2 (60 min) | Why |
|---|---|---|---|
| Thu 5/8 | Write Dropzone tech round debrief; replay every Eric question into `dropzone-ai/15_TECH_ROUND_DEBRIEF.md` | Re-implement take-home from memory in 60 min | Dropzone panel could fire Mon |
| Fri 5/9 | `03-llm-ai-security/ROADMAP.md` Day 11 lab — LLM log triage agent (Dropzone demo) | OneDigital vendor reading: Snyk free tier + CrowdStrike AIDR | Two roles served |
| Sat 5/10 | Insight Global Azure ramp Day 1: Defender for Cloud architecture + KQL primer | OneDigital vendor reading: Salt Security API model + Entra Conditional Access | Insight + OneDigital both Microsoft-adjacent |
| Sun 5/11 | Insight Global Azure Day 2: Sentinel + Security Copilot | `04-threat-modeling/drills/drill_05_payment_processing.md` for Amex if Darren resurfaces | Microsoft + Amex |
| Mon 5/12 | Mock Dropzone panel using `03-llm-ai-security/INTERVIEW-Qs.md` + `05-detection-triage/INTERVIEW-Qs.md` | KQL drill: 10 hunting queries against synthetic Sentinel data | Recall |
| Tue 5/13 | Dropzone whiteboard: `04-threat-modeling/HIS-STACK.md` + `03-llm-ai-security/THREAT-MODELS.md` Model 2 out loud | Cloudflare Worker shippable: 2-hour signature-validation Worker on `tigouetheory.com` | Closes Cloudflare biggest gap |
| Wed 5/14 | QGenda 1-page healthcare threat model artifact (90 min, ship to repo) | `01-code-fluency/ROADMAP.md` Days 11-14 LangGraph touchpoint | QGenda differentiator + Dropzone code fluency |

**The single most important gap to close this week:** the Microsoft Azure ramp for Insight Global. It is the largest curriculum vacuum in the pipeline, and Insight Global is the next interview that could fire after Dropzone. If Savannah moved Emmanuel to a technical screen, he has 5-7 business days to get Defender for Cloud + Sentinel + Security Copilot to bridge-statement quality, and he has zero curriculum content on disk for it today. Everything else is a 30-90 min refresh; this is a 7-hour build.

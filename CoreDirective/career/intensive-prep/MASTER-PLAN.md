# Master Plan: 6-Week AI Security Engineer Interview Sprint

Generated 2026-05-08 by 15-agent run (7 curriculum + 3 market truth + 5 QC audits).

---

## Status Dashboard

| Axis | Score | Source |
|------|-------|--------|
| Senior-readiness (overall) | 8/10 | AUDIT-03-SENIOR-INTERVIEWER.md |
| Technical accuracy | 12 errors, 14 warnings, 9 minor | AUDIT-01-TECHNICAL-ACCURACY.md |
| Market coverage | 33 gaps (7 critical) | AUDIT-02-COVERAGE-GAPS.md |
| Story defensibility | 8 solid, 15 need artifact, 8 exaggerated, 4 fabricated | AUDIT-04-DEFENSIBILITY.md |
| Pipeline readiness | Dropzone 88, Brilliant 78, Amex 75, QGenda 70, WBD 65, OneDigital 60, Insight Global 55 | AUDIT-05-PIPELINE-ALIGNMENT.md |

Most-ready role: **Dropzone AI**.
Biggest gap: **Microsoft Azure ramp** (only matters if Insight Global fires).

---

## Already Fixed This Session

1. OWASP LLM Top 10 names updated to 2025 list in `05-detection-triage/INTERVIEW-Qs.md` (LLM02, LLM05, LLM06, LLM10).
2. Capital One settlement corrected from FTC to OCC ($80M penalty 2020) plus $190M class action in `02-aws-security/INTERVIEW-Qs.md`.
3. ATT&CK technique tag corrected from T1610 to T1609 for kubectl exec rule in `05-detection-triage/SIGMA-PRIMER.md`.

---

## Stories to Kill Before Next Interview

These are flagged by `AUDIT-04-DEFENSIBILITY.md` as fabricated or unsupported:

1. **Vault unseal tabletop** (Vault is not initialized on the droplet, so the story has no proof).
2. **Splunk MTTD at Texaco** (no Splunk artifacts on disk to back the metric).
3. **CoreDirective Accounting AI Dropzone closer** (still has bracketed placeholders).
4. **Garak CI claim** (zero references in the repo, fabricated).

Pull these from `03-llm-ai-security/STORYTELLING.md`, `06-pentest-essentials/STORYTELLING.md`, `07-stack-upgrades/STAR-STORIES.md`, and `CoreDirective/career/dropzone-ai/04_STAR_STORIES.md`.

---

## New Story for Dropzone (added 2026-05-08)

**Story 13: Campbellton Plaza Gate Access Design** is now captured in `CoreDirective/career/dropzone-ai/04_STAR_STORIES.md`.

It replaces Story 6 (CoreDirective Accounting AI) as the Dropzone closer for "what excites you about Dropzone" or "recent customer project," because Story 6 still has bracketed placeholders. The architectural principle in Story 13 (AI on the edges, deterministic critical path) is the same rule Dropzone applies to AI SOC analysts. Lead with it for AI judgment, architectural tradeoff, or customer-facing prompts.

The artifact backing this story is the Campbellton plaza one-page DOCX produced today. Keep it ready to reference.

---

## Stack Truth Updates

These hard facts must be propagated wherever they appear:

- OpenClaw: **v2026.4.21** (stories say v2026.3.8). Update `CLAUDE.md` and every story that names a version.
- n8n active workflows: **6** (stories say 14).
- GRC docs: **51** (stories say 37, defensible undercount).
- Vault: **not initialized** at audit time. Either initialize it or stop telling Vault stories.
- Garak: **not in repo**. Either install plus commit, or remove every Garak claim.
- Helm charts: **none in repo**. Pentest Story 4 must be rewritten or removed.

---

## Critical Articulation Drill (memorize verbatim)

**"HITL is the prevent. JIT is the contain. Audit log is the detect. Three layers, three roles, no overlap."**

Use this any time you describe the OpenClaw, n8n, or Vault control flow. Two stories currently conflate JIT-as-prevent with JIT-as-contain (per QC3) and a sharp interviewer will trip you.

---

## Critical Coverage Gaps (must close in Week 1)

| Priority | Gap | Folder to add to | Estimated build |
|----------|-----|------------------|-----------------|
| 1 | Streaming top-N over multi-GB log (most-asked Python pattern) | `01-code-fluency/labs/` | 2 hours |
| 2 | MCP Top 10 v0.1 + 6 CVEs (CVE-2025-6515, CVE-2025-54136 named) + Claude Skills supply chain | `03-llm-ai-security/` | 3 hours |
| 3 | OWASP Top 10 for Agentic Applications 2026 (the 2026 differentiator) | `03-llm-ai-security/` | 2 hours |
| 4 | US AI regulatory pack: NIST AI RMF + Generative AI Profile, EO 14110 (Biden 2023, Trump 2025 successor status), Colorado AI Act (eff. 2026-02-01), NYC Local Law 144 (bias audit), NY SHIELD Act, California (CCPA, CPRA, AB 2013), FTC AI guidance (Khan/Atkinson era), SEC cyber disclosure rule, HIPAA + AI, FedRAMP, FISMA, TX Data Privacy Act | `03-llm-ai-security/` | 2 hours |
| 5 | RAG indirect-injection 5-layer capstone end-to-end | `03-llm-ai-security/labs/` | 4 hours |
| 6 | Promptfoo CI gate against OpenClaw (the highest-leverage public artifact) | `07-stack-upgrades/` | 2 days |
| 7 | Microsoft Azure ramp (defer unless Insight Global fires) | new `08-azure-microsoft/` | 7 hours |

---

## Today: Next 2 Hours

```bash
cd /Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/01-code-fluency
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
python3 labs/day01_variables_to_functions.py
```

Then retype FizzBuzz and `is_private_ip` from a blank file. That is your fluency loop.

After that, read out loud 5 times: the 7-phase opener in `04-threat-modeling/PROCESS.md` and the HITL/JIT/audit line above.

---

## Week 1 Day-by-Day

Each block is 90 minutes max (ADHD-friendly per `00-market-truth/ADHD-LEARNING-PROTOCOL.md`).

### Day 1 (today, 2026-05-08)
- Block 1: Code fluency Day 1 lab + FizzBuzz retype.
- Block 2: Read AUDIT-04-DEFENSIBILITY.md, delete the 4 fabricated stories from your story files.
- Block 3: Memorize the 7-phase threat-modeling opener and the HITL/JIT/audit line.

### Day 2
- Block 1: Build the streaming top-N lab in `01-code-fluency/labs/day_streaming_topN.py` (Counter, heap, malformed line handling).
- Block 2: Run `06-pentest-essentials/labs/lab_03` (SSRF to IMDS Capital One pattern). Drill the kill chain out loud.
- Block 3: Code fluency Day 2.

### Day 3
- Block 1: Write `03-llm-ai-security/MCP-SECURITY.md` covering MCP Top 10 plus CVE-2025-6515, CVE-2025-54136, plus Claude Skills supply chain risks.
- Block 2: Run `02-aws-security/labs/iam_privesc_via_passrole.sh`. Drill out loud.
- Block 3: Code fluency Day 3.

### Day 4
- Block 1: Write `03-llm-ai-security/AGENTIC-TOP-10-2026.md` summarizing the OWASP Agentic Apps 2026 list.
- Block 2: Write `03-llm-ai-security/US-AI-REGULATORY-PACK.md` covering NIST AI RMF + Generative AI Profile, EO 14110 status, Colorado AI Act effective 2026-02-01, NYC Local Law 144, NY SHIELD, California (CCPA/CPRA/AB 2013), FTC AI guidance, SEC cyber disclosure rule, HIPAA + AI, FedRAMP, FISMA. Skip EU AI Act unless a target role is EU-facing.
- Block 3: Code fluency Day 4.

### Day 5
- Block 1-2: Build the RAG 5-layer capstone lab in `03-llm-ai-security/labs/rag_indirect_capstone.py`.
- Block 3: Code fluency Day 5.

### Day 6
- Block 1: Start the Promptfoo CI gate per `07-stack-upgrades/WEEK1-EXECUTE.md`.
- Block 2: Code fluency Day 6 (pip install pydantic, requests, fastapi, pytest, langchain, langgraph).
- Block 3: Mock interview with one of the drills in `04-threat-modeling/drills/drill_08_agentic_soar_workflow.md` out loud.

### Day 7
- Block 1: Finish Promptfoo CI gate, push to GitHub, capture screenshot for portfolio.
- Block 2: Rehearse STAR Story 2 (OpenClaw AI Gateway Red Team) out loud 5 times.
- Block 3: Mock interview with `drill_05_payment_processing.md` for Amex.

---

## Pipeline Priority Order

1. **Dropzone AI** (88% ready). Already submitted take-home. Tech round material is in the curriculum. Drill drill_08 + LLM/AI security INTERVIEW-Qs.md daily until fired.
2. **Brilliant Cloudflare** (78%). Awaiting HM round. Run `candescent-cloudflare-build-plan-2026-04-29` if it fires.
3. **Amex Experis** (75%). Payment threat model. Drill drill_05_payment_processing.md.
4. **QGenda** (70%). Healthcare HIPAA gap. Add a half-day HIPAA brief if it fires.
5. **WBD** (65%). Submittal sent. Wait for movement.
6. **OneDigital** (60%). Snyk + Salt + CrowdStrike AIDR gap. Add API security brief if it fires.
7. **Insight Global** (55%). Microsoft stack gap. Decide before investing 7 hours on Azure.

---

## Audit Files Reference

All findings live in `intensive-prep/`:

- `AUDIT-01-TECHNICAL-ACCURACY.md` — version bumps, CVE numbers, ATT&CK IDs to fix
- `AUDIT-02-COVERAGE-GAPS.md` — 33 missing topics ranked by JD frequency
- `AUDIT-03-SENIOR-INTERVIEWER.md` — readiness scores, reject triggers, mock transcript
- `AUDIT-04-DEFENSIBILITY.md` — STAR story tags (solid, fabricated, etc) plus artifact build list
- `AUDIT-05-PIPELINE-ALIGNMENT.md` — coverage per active role plus prep sequence

Curriculum (the actual material to study):

- `00-market-truth/` — canon, tool versions, JD frequencies, real interview questions
- `01-code-fluency/` — Python and LangGraph labs Day 1 to 14
- `02-aws-security/` — IAM through AI/ML pipeline, 17 labs
- `03-llm-ai-security/` — OWASP LLM, ATLAS, prompt injection, 11 labs
- `04-threat-modeling/` — STRIDE process, HIS-STACK threat model, 10 drills
- `05-detection-triage/` — Sigma rules, 12 labs with realistic logs
- `06-pentest-essentials/` — OWASP Top 10, 10 labs, AWS attack chains
- `07-stack-upgrades/` — Promptfoo, NeMo, AI BOM, week-1 execute playbook

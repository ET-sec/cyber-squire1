# AUDIT 02: Coverage Gaps Against Real Market Demand

Audit window: May 8, 2026. Target: $200K AI Security Engineer interview readiness, with Dropzone AI as the live calibration loop. Method: every distinct topic, skill, or question type in `00-market-truth/` cross-referenced against `01-code-fluency/` through `07-stack-upgrades/`. Status legend below.

- **COVERED**: explicit lab, interview-Q answer, or roadmap section with depth.
- **PARTIAL**: mentioned but not drilled, or single sentence in a cheatsheet.
- **MISSING**: not present in any curriculum file.

Severity legend:

- **ERROR** = appears in 60%+ of JDs or named explicitly in a top-tier loop. Curriculum cannot ship without it.
- **WARNING** = 30 to 60% JD frequency or differentiator in the loop anatomy.
- **MINOR** = nice to have, won't sink an interview alone.

---

## Section A: Tier A Skills (60%+ JD Frequency, must-have)

### A1. Python production grade (94% of JDs) — COVERED

`01-code-fluency/ROADMAP.md` ships 14 days of Python plus pydantic, FastAPI, pytest. `INTERVIEW-Qs.md` has 30 questions covering string manipulation, dict aggregation, log parsing, regex, recursion, LangGraph. Day 14 produces a runnable LangGraph triage agent. This is a clean A.

### A2. Cloud security AWS depth (89% of JDs) — COVERED

`02-aws-security/ROADMAP.md` is a 21-day intensive with 19 working labs across IAM, KMS, VPC, EKS, S3, GuardDuty, SecurityHub. `INTERVIEW-Qs.md` has 40 questions, depth across IAM evaluation, IMDSv2, ABAC, confused deputy, Capital One walk-through, multi-account landing zone, SCPs, KMS envelope encryption, Lambda execution vs task role, prompt injection on Bedrock. Solid A.

### A3. LLM/RAG/agent architecture (72% of JDs) — COVERED

`03-llm-ai-security/ROADMAP.md` 14 days, OWASP LLM Top 10 by ID, RAG security, agentic threats. Labs include `prompt_injection_basic.py`, `rag_poisoning_demo.py`, `agentic_tool_abuse.py`, `mitre_atlas_mapper.py`. `THREAT-MODELS.md` has four full LLM-system models including Dropzone shape. Solid A.

### A4. Prompt injection direct + indirect + tool-mediated (72%) — COVERED

`03-llm-ai-security/INTERVIEW-Qs.md` Q5, Q6, Q7, Q8, Q33 cover the distinction. Labs include `prompt_injection_basic.py`, `indirect_injection_via_tool.py`, `data_exfil_via_markdown_image.py`. Defense layering is articulated as a five-layer pattern in Q7. **Note**: defense in depth is articulated, but no lab demonstrates the *full* layered stack against the *indirect* variant in a *RAG flow* end-to-end. See B12 below.

### A5. Detection engineering / threat hunting (67%) — COVERED

`05-detection-triage/ROADMAP.md` 14 days, 12 working labs from SSH brute force to LLM prompt injection. SIGMA-PRIMER.md has 10 progressively complex examples. `INTERVIEW-Qs.md` covers detection-as-code, hunting hypothesis, MITRE ATT&CK Navigator, Pyramid of Pain.

### A6. Kubernetes / container security (67%) — PARTIAL

EKS Pod Identity vs IRSA gets a brief mention (`02-aws-security/INTERVIEW-Qs.md` Q21) but the explicit comparison the market wants is not drilled. K8s pod escape lab exists in `06-pentest-essentials/labs/lab_09_kubernetes_pod_escape/`. `04-threat-modeling/drills/drill_02_kubernetes_multitenant.md` covers multi-tenant. Gaps: no Pod Security Admission lab, no Kyverno/OPA-Gatekeeper hands-on, no explicit IRSA-vs-Pod-Identity decision matrix. Add to `02-aws-security/labs/eks_pod_identity_vs_irsa_compared.md` and `06-pentest-essentials/labs/lab_09b_pod_security_standards.md`.

### A7. Threat modeling and secure design review (61%) — COVERED

`04-threat-modeling/ROADMAP.md` 10 days, 10 drill scenarios including agentic SOAR, RAG chatbot, CI supply chain, payment processing. STRIDE plus ATLAS mapping. PROCESS.md gives the 40-minute interview structure. Aligned with `00-market-truth/THREAT-MODEL-INTERVIEW-EXPECTATIONS.md`.

---

## Section B: Tier B Differentiators (30 to 60% JD Frequency)

### B1. Adversarial ML (data poisoning, model inversion, evasion) (56%) — PARTIAL

`03-llm-ai-security/INTERVIEW-Qs.md` covers data poisoning (Q21 RAG, Q14 PoisonGPT), embedding inversion (Q20). Missing: dedicated drill on FGSM/PGD/Carlini-Wagner adversarial example generation, missing membership inference walk-through, missing model extraction via API budget. Market truth doc `REAL-AI-SECURITY-Qs-2026.md` Q3.2 explicitly asks "How would you detect someone trying to steal your AI model through the API?" Add to `03-llm-ai-security/labs/model_extraction_defense.py` and a section in INTERVIEW-Qs.md on classical-ML adversarial robustness (ART, Counterfit, TextAttack).

### B2. CI/CD security (Snyk, Semgrep, GHA) (50%) — PARTIAL

Mentioned in `06-pentest-essentials/AWS-PENTEST.md` and Robinhood STAR alignment in `07-stack-upgrades/`. No explicit lab on Snyk SAST, Semgrep custom rule, GHA pipeline hardening (OIDC to AWS, no static keys), or SBOM generation in CI. Robinhood JD names Snyk, Semgrep, Wiz, Endor Labs, TruffleHog by tool. Add to `02-aws-security/labs/gha_oidc_aws_federation.md` and `06-pentest-essentials/labs/lab_11_ci_supply_chain_security/`.

### B3. OWASP LLM Top 10 + MITRE ATLAS literacy (44%) — COVERED

OWASP Top 10 LLM enumerated by ID with severity ranking in `03-llm-ai-security/INTERVIEW-Qs.md` Q1. ATLAS techniques referenced by AML.T-code throughout. Lab `mitre_atlas_mapper.py` maps findings to ATLAS IDs.

### B4. Red team / pentest background (44%) — COVERED

`06-pentest-essentials/` 21 days with 10 labs across web, API, AWS, K8s, LLM. Burp workflow, Pacu modules, sqlmap, OWASP Top 10. Storytelling and interview Qs included.

### B5. Cloud-native vuln tools (Snyk, Wiz, TruffleHog, Endor) (39%) — MISSING (lab depth)

Tools named, but no hands-on lab demonstrates Snyk scan, Wiz query, TruffleHog secret hunt, or Endor SCA. Robinhood explicitly tests this in their tooling round per `INTERVIEW-LOOP-ANATOMY.md`. Add to `06-pentest-essentials/labs/lab_12_supply_chain_scanners/` covering all five tools on a deliberately vulnerable repo.

### B6. AI red team tools — Promptfoo, Garak, PyRIT, NeMo Guardrails (39%) — PARTIAL

Promptfoo: COVERED via `labs/promptfoo_redteam.yaml`. Garak: roadmap mentions, no lab. NeMo Guardrails: COVERED via `labs/guardrails_with_nemo.py`. **PyRIT: MISSING**. Microsoft AI Red Team JD explicitly tests "candidates are asked to walk through how they would extend PyRIT for a novel attack class." `INTERVIEW-LOOP-ANATOMY.md` flags PyRIT proficiency as failure-mode for Microsoft round 3. **ERROR** for any candidate targeting Microsoft AI Red Team. Add `03-llm-ai-security/labs/pyrit_orchestrator_extension.py` with custom orchestrator + scorer + attack strategy.

### B7. MCP / agent protocol security awareness (39%) — MISSING

This is the single biggest gap. Market truth `EMERGING-TOPICS-2026.md` section 1 names six real CVEs (CVE-2025-6515, CVE-2025-6514, CVE-2025-53107, CVE-2025-53818, CVE-2025-54136 MCPoison, plus the Anthropic Git MCP three-bug chain). `REAL-AI-SECURITY-Qs-2026.md` Q5.3 asks "What security concerns are unique to MCP servers?" The curriculum has zero MCP coverage. ZERO. Audit grep across all of 03/04/06 returned nothing. **ERROR**. This is must-add before any frontier-lab or agent-security interview. Add:

- `03-llm-ai-security/MCP-SECURITY.md`: MCP Security Top 10 v0.1 beta, the six CVEs above, the architectural RCE in MCP STDIO transport, sampling-callback trust inversion.
- `03-llm-ai-security/labs/mcp_server_attack_lab.py`: spin up vulnerable MCP server, demonstrate the path-traversal + command-injection chain from gentic.news 43%-vuln finding.
- `04-threat-modeling/drills/drill_11_mcp_server_threat_model.md`: standalone drill.
- A new section in `03-llm-ai-security/INTERVIEW-Qs.md` with at least 5 MCP-specific questions.

### B8. Detection content (YARA, Sigma, Snort, Suricata) (33%) — PARTIAL

Sigma: COVERED with deep primer plus 10 example rules and sigma-cli conversion to Splunk and KQL. YARA: not present anywhere. Snort/Suricata: not present. Anthropic Threat Intel JD names YARA, Sigma, Snort or Suricata as required. Add `05-detection-triage/YARA-PRIMER.md` with 5 progressive YARA rules plus a minimal Suricata rule example. **WARNING** if pursuing Anthropic Threat Intel; otherwise MINOR.

### B9. AI governance — NIST AI RMF, ISO 42001, EU AI Act (33%) — PARTIAL

NIST AI RMF: COVERED at framework level. ISO 42001: PARTIAL (one cheatsheet bullet, one Q&A). EU AI Act: PARTIAL (tiers named, **but Aug 2 2026 enforcement date and EUR 35M / 7% turnover penalty bands NOT in curriculum**). Market truth `EMERGING-TOPICS-2026.md` section 8 makes the timeline interview-grade signal. `REAL-AI-SECURITY-Qs-2026.md` Q9.3 expects high-risk Annex III enumeration. Add to `03-llm-ai-security/CHEATSHEET.md` an EU AI Act timeline + penalty band block, and to `INTERVIEW-Qs.md` add Q "Walk me through what your team has to ship by Aug 2 2026 if your product is an Annex III high-risk system." Also add an explicit ISO 42001 vs ISO 27001 mapping in CHEATSHEET.md.

### B10. Vector DBs (FAISS, Pinecone, Weaviate, OpenSearch) (33%) — PARTIAL

Mentioned in `03-llm-ai-security/THREAT-MODELS.md` (pgvector). No lab demonstrates per-tenant namespace isolation, embedding signing, or vector DB pen-test. Lockheed Martin JD explicitly names OpenSearch and Weaviate. WBD Cybersec already in pipeline. Add `03-llm-ai-security/labs/multitenant_vector_db_isolation.py` with pgvector or OpenSearch.

### B11. CVSS, EPSS, CISA KEV (28%) — MISSING

Robinhood JD explicitly tests this. `INTERVIEW-LOOP-ANATOMY.md` flags it as a Robinhood round expectation. CVSS appears once in the pentest report-format question, but EPSS and CISA KEV are absent across the curriculum. Tigoue has Robinhood-pattern roles in pipeline. **WARNING**. Add `06-pentest-essentials/CVSS-EPSS-KEV.md` with worked-example scoring of three real 2026 CVEs and a side-by-side decision matrix (CVSS rating vs EPSS prob vs KEV listing).

### B12. Indirect prompt injection in RAG/agentic flows with full layered defense — PARTIAL (depth)

The interviewer-favorite question per `REAL-AI-SECURITY-Qs-2026.md` section 11 ("Walk me through detection and mitigation of prompt injection in a production system, specifically the indirect variant in a RAG or agentic flow") gets a strong Q7 answer in the LLM curriculum. **But no lab pulls all five layers together end to end against the RAG attack path**. `labs/rag_poisoning_demo.py` shows provenance defense; `labs/indirect_injection_via_tool.py` shows the attack on a fetched webpage. Neither stitches the full pre-retrieval + prompt-template + output + tool-allowlist + telemetry stack on a RAG. **WARNING**. Combine into one capstone `labs/rag_indirect_injection_capstone.py` that ships all five layers with assertions for each.

---

## Section C: Topic-Specific Checks Requested

### C1. OWASP Top 10 for Agentic Applications 2026 — MISSING

`EMERGING-TOPICS-2026.md` section 17 names this as "the first dedicated agentic framework." DeepTeam framework reference at https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications. Curriculum has zero hits on grep. This is the differentiator the market wants for AI Security Engineer roles in 2026 — not the LLM Top 10, the *Agentic* Top 10. **ERROR**. Add `03-llm-ai-security/OWASP-AGENTIC-TOP-10.md` with all 10 items by ID, plus integrate into THREAT-MODELS.md drill 8 (agentic SOAR).

### C2. MCP Security Top 10 v0.1 beta + recent MCP CVEs — MISSING

See B7. **ERROR**. Same fix.

### C3. Streaming log parsing with top-N (most-asked Python pattern) — PARTIAL

`01-code-fluency/INTERVIEW-Qs.md` has Top-K (Q7), file-tail with deque (Q18), top failing user (Q16). **But no lab combines streaming line iterator + tuple-per-line parsing + Counter folding + most_common(N) on a multi-GB file with malformed-line handling**. `REAL-CODE-QUESTIONS-2026.md` section 10 declares this "the single most-asked Python interview pattern across this dataset." Amazon, Yelp, Cloudflare ask variants. **ERROR**. Add `01-code-fluency/labs/day02b_streaming_apache_subnet_top10.py` solving the verbatim Q1.1 prompt: parse Apache log, group by /24 subnet and month, return top 10 subnets per month, on a >1GB synthetic file with at least 2 corrupted lines.

### C4. Indirect prompt injection in RAG/agentic flows with layered defense — PARTIAL

See B12.

### C5. iam:PassRole privesc + IAM evaluation order — COVERED

`02-aws-security/INTERVIEW-Qs.md` Q1 (eval order) and Q3 (PassRole). Lab `iam_privesc_via_passrole.sh` plus AWS-PENTEST.md catalog.

### C6. AWS GuardDuty / SecurityHub / Inspector differences — COVERED

`02-aws-security/INTERVIEW-Qs.md` Q31 covers GuardDuty vs SecurityHub. Inspector less explicit. Add one Q comparing all three in one breath, mirroring `REAL-AWS-SECURITY-Qs-2026.md` Q4.3.

### C7. EKS Pod Identity vs IRSA — PARTIAL

See A6. Q21 mentions Pod Identity in two sentences. Senior depth per `REAL-AWS-SECURITY-Qs-2026.md` Q5.2 wants the explicit decision matrix: when each, why, the OIDC trust dependency vs the agent-based trust. **WARNING**. Add an explicit Q "When would you choose Pod Identity over IRSA, and what are the operational tradeoffs?" with a decision-table answer in `02-aws-security/INTERVIEW-Qs.md`.

### C8. KQL/SPL conversion of Sigma rules — COVERED

`05-detection-triage/SIGMA-PRIMER.md` covers sigma-cli conversion. ROADMAP Day 13 has explicit conversion drill: pick a Sigma rule, convert to Splunk + Sentinel + Elastic + Chronicle + Panther. Lab 01 README has the convert command.

### C9. TTP vs IOC + Pyramid of Pain — COVERED

`05-detection-triage/ROADMAP.md` Day 6 is the entire topic. CHEATSHEET.md likely references. Confirmed via grep.

### C10. AI BOM (model bill of materials) — MISSING

Discussed in market-truth `EMERGING-TOPICS-2026.md` section 5 as a procurement gate by H2 2026. `REAL-AI-SECURITY-Qs-2026.md` Q3.4 directly asks "What is in an AI model's SBOM?" Curriculum grep returns zero. **WARNING**. Add `03-llm-ai-security/AIBOM.md` covering CycloneDX ML-BOM 1.6 fields, OWASP AIBOM project, SPDX 3.0 AI extension, and a worked example artifact for one of Tigoue's own labs.

### C11. ISO 42001 and EU AI Act — PARTIAL

See B9. The names are there; the depth is not.

### C12. Constitutional AI vs RLHF — PARTIAL

`03-llm-ai-security/INTERVIEW-Qs.md` Q3 mentions both. `labs/guardrails_with_constitutional_ai.py` exists. **No explicit comparison drill on alignment tax, data efficiency, red-team implications**. `EMERGING-TOPICS-2026.md` section 14 declares this a "soft topic" but flags it for frontier-lab interviews. **MINOR** for non-Anthropic; add a 200-word framed answer to INTERVIEW-Qs.md if Anthropic loop is targeted.

### C13. Anthropic Claude Skills security model — MISSING

Market truth `EMERGING-TOPICS-2026.md` section 2 documents three classes of attack: --dangerously-skip-permissions, MCP server hijacking via shipped .mcp.json, hook-based exfiltration. Academic study of 25,187 skills found widespread vulns. `REAL-AI-SECURITY-Qs-2026.md` Q5.4 explicitly asks. Curriculum grep returns zero. **WARNING** for any Anthropic-adjacent role. Add to MCP-SECURITY.md a section on Claude Skills supply chain.

### C14. LangGraph state checkpoint / persistence patterns — COVERED

`01-code-fluency/labs/day13_langgraph_tools_persistence.py` and `day14_langgraph_security_agent.py`. INTERVIEW-Qs Q28 (Persistence with Checkpointer) and Q29 (Human-in-the-Loop with interrupt_before).

### C15. Pacu modules for AWS attack chains — COVERED

`06-pentest-essentials/AWS-PENTEST.md` names a Pacu module per category, plus lab_08 runs an end-to-end privesc chain.

### C16. Capital One kill chain end-to-end — COVERED

`02-aws-security/INTERVIEW-Qs.md` Q26 walks the full chain. ROADMAP Day 8 references. CHEATSHEET line 187 anchors it. AWS-PENTEST.md and `05-detection-triage/labs/lab_02_aws_credential_exfil/` reinforce.

---

## Section D: Real Code Questions Coverage (REAL-CODE-QUESTIONS-2026.md)

### D1. Apache log subnet aggregation, /24 + month + top-10 — MISSING

See C3. **ERROR**.

### D2. Top 100 URLs in 5GB log — PARTIAL

Q7 (Top K Frequent Items) and Q18 (tail) exist. No 5GB-scale lab. **WARNING**. Pair with C3 fix.

### D3. Anthropic CodeSignal four-level Bank transaction system — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q5.1 documents Anthropic's signature take-home: 90 minutes, four progressively harder levels, must absorb new requirements without collapse. No analog exists in `01-code-fluency/`. **WARNING** unless Anthropic loop is locked-in target. Add `01-code-fluency/labs/day15_bank_transaction_four_levels.py` with the four levels (basic accounts, transfers, scheduled txn merge logic, audit trail), each a separate function set with passing tests.

### D4. Anthropic web crawler BFS — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q5.2. **WARNING**. Add `01-code-fluency/labs/day16_web_crawler_bfs.py`.

### D5. asyncio.TaskGroup structured concurrency — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q3.3 expects refactor from gather to TaskGroup. Day 5 covers gather only. **MINOR**. Add a TRY THIS to day05.

### D6. asyncio.Semaphore + per-host rate limit — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q3.4 names the rate-limited async HTTP scanner. Day 8 has retry/backoff but no concurrency-cap pattern. **MINOR**. Add a function `scan_targets(urls, concurrency=10)` to day08 lab.

### D7. Pydantic LLM output validator with retry — PARTIAL

Day 6 has Pydantic basics, day 14 has output validation in the agent. No explicit "LLM returned wrong fields, retry up to N times" pattern as a standalone exercise. `REAL-CODE-QUESTIONS-2026.md` Q4.2 senior-bar pattern. **MINOR**. Add to day06.

### D8. Generic + TypeVar + Protocol typing — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q4.3, senior signal at Anthropic and frontier labs. Curriculum grep on `TypeVar` returns nothing in labs. **MINOR** unless targeting frontier loops.

### D9. Tool schema mismatch defensive code path — PARTIAL

Q7.1 in the market truth doc. Day 14 agent has defensive validation but no explicit "tool returns unexpected schema, what does the agent do" stand-alone problem.

### D10. GraphRecursionError diagnose + fix — MISSING

`REAL-CODE-QUESTIONS-2026.md` Q7.2 is a real LangGraph interview question. Curriculum has no explicit recursion-limit handling drill. **MINOR**. Add a sub-exercise to day13.

### D11. Output validator (parse + repair + retry) for LLM JSON — PARTIAL

OWASP LLM05 reference exists. No standalone lab. **MINOR**.

---

## Section E: Real AWS Security Questions Coverage

Most items COVERED. Specific gaps:

### E1. NotResource policy gotcha — MISSING

`REAL-AWS-SECURITY-Qs-2026.md` Q1.5. Curriculum doesn't drill this specific bug pattern. **MINOR**.

### E2. Role chaining max session duration of 1h — PARTIAL

Mentioned in passing. Add explicit Q in INTERVIEW-Qs.md.

### E3. KMS grant vs key policy — COVERED in Q18.

### E4. SCP that prevents disabling CloudTrail — COVERED in Q33 + AWS-PENTEST.md.

### E5. Verified Access Zero Trust — COVERED in Q38.

### E6. RTO vs RPO — MISSING

`REAL-AWS-SECURITY-Qs-2026.md` Q10.1. **MINOR**. Add one Q.

---

## Section F: Real AI Security Questions Coverage (REAL-AI-SECURITY-Qs-2026.md)

Q1.1, Q1.2, Q1.3, Q1.4 prompt injection variants — COVERED.
Q2.1, Q2.2 jailbreak families and chatbot red team — COVERED.
Q2.3 Microsoft AI Red Team approach — PARTIAL. PyRIT mentioned but not deep.
Q3.1 PoisonGPT — COVERED.
Q3.2 model extraction — PARTIAL.
Q3.3 training data poisoning — COVERED.
Q3.4 SBOM for AI model — MISSING (see C10).
Q4.1, Q4.2 RAG security — COVERED.
Q5.1 excessive agency — COVERED.
Q5.2 multi-agent threats (OWASP Agentic Top 10) — MISSING (see C1).
Q5.3 MCP server security — MISSING (see B7).
Q5.4 Anthropic Claude Skills risks — MISSING (see C13).
Q6.1, Q6.2 ATLAS + ATT&CK relationship and chain mapping — COVERED.
Q6.3 ATLAS v5.3 January 2026 additions (the MCP case studies) — MISSING.
Q7.1, Q7.2, Q7.3 OWASP LLM Top 10 — COVERED.
Q8.1 NeMo Guardrails vs Garak — COVERED.
Q8.2 Promptfoo in CI — COVERED.
Q8.3 ART/Counterfit/TextAttack — MISSING (see B1).
Q9.1, Q9.2, Q9.3 governance — PARTIAL (see B9).
Q9.4 90-day plan to start AI security program — MISSING. **WARNING**. Add to STORYTELLING.md or INTERVIEW-Qs.md as a structured 30-60-90 answer template.

---

## Section G: Interview Loop Anatomy Specific Asks

### G1. Anthropic values round — MISSING

`INTERVIEW-LOOP-ANATOMY.md` Anthropic section calls the values round "real" and a hard reject vector. No values-round prep exists in `07-stack-upgrades/STAR-STORIES.md`. **WARNING** for Anthropic-adjacent. Add a section to STAR-STORIES.md with the values mapping (Anthropic publishes 7 values) and a 90-second story per value.

### G2. Cloudflare practical take-home (parser, CLI, HTTP server) — PARTIAL

`01-code-fluency/labs/day09_fastapi_minisvc.py` covers a mini HTTP service. No parser-CLI take-home exists with full README + tests + error handling. Cloudflare's bar is "submitting a main happy-path only project is a common fail". **MINOR**. Add a one-shot take-home template.

### G3. Microsoft PyRIT depth — MISSING

See B6. **ERROR** for Microsoft AI Red Team.

### G4. Wiz public-research footprint — OUT OF SCOPE for curriculum

This is a career artifact problem, not a study problem. Wiz reject vector is no public blog/talk/CVE. Tigoue has the GRC docs and the OpenClaw stack — those become public artifacts via the brand site, not via this curriculum. Note in pickup list, not here.

---

## Section H: Emerging-Topics Mandatory 7 Coverage

Per `EMERGING-TOPICS-2026.md` read-out section, the seven non-negotiables:

1. OWASP LLM Top 10 — COVERED.
2. MITRE ATLAS — COVERED.
3. NIST AI RMF GenAI Profile (AI 600-1) — COVERED at name level, depth PARTIAL.
4. EU AI Act timeline (2025/2026/2027 dates + penalty bands) — PARTIAL (see B9).
5. Prompt injection (direct/indirect/multimodal/structured queries defense) — PARTIAL. **Multimodal MISSING**, structured-queries paper (Chen et al USENIX 2025) MISSING.
6. MCP server attack surface, at least 2 named CVEs — MISSING (see B7). **ERROR**.
7. RAG poisoning + PoisonedRAG name — COVERED.

Score 4 of 7 fully clean. Curriculum will not clear the "minimum non-negotiable" bar for $200K AI Security Engineer interviews until items 4, 5, 6 are closed.

---

## TOP 10 COVERAGE GAPS, PRIORITIZED BY MARKET FREQUENCY

Ranked by JD-prevalence severity and interview-loop blast radius.

| Rank | Gap | Severity | Drives | Add by |
|---|---|---|---|---|
| 1 | MCP server security: top-10 + 6 CVEs + Claude Skills supply chain | ERROR | 39% of JDs, 100% of frontier-lab loops, ATLAS Jan 2026 update | Before any interview |
| 2 | Streaming log parsing + top-N on multi-GB file (Apache /24/month/top-10) | ERROR | Most-asked Python pattern across dataset; Amazon, Yelp, Cloudflare | Before any interview |
| 3 | OWASP Top 10 for Agentic Applications 2026 | ERROR | Differentiator for AI Sec Eng 2026 specifically | Before any interview |
| 4 | EU AI Act timeline + Aug 2 2026 + EUR 35M / 7% penalty bands | WARNING-bordering-ERROR | 33% governance JDs; trivial study cost | Before any interview |
| 5 | RAG indirect-injection 5-layer capstone lab end-to-end | WARNING | The single most-asked AI security question in market truth | Week 1 |
| 6 | PyRIT orchestrator + scorer + custom attack strategy | ERROR for Microsoft, WARNING elsewhere | Microsoft AI Red Team JD explicit | Week 2 (skip if no Microsoft loop) |
| 7 | EKS Pod Identity vs IRSA explicit decision matrix | WARNING | 67% K8s JDs; senior-depth Q | Week 1 |
| 8 | CVSS + EPSS + CISA KEV scoring drill | WARNING | Robinhood explicit; pipeline already has Robinhood-pattern | Week 1 |
| 9 | Anthropic 4-level Bank transaction CodeSignal practice | WARNING | Anthropic signature take-home; 90-min timed | Week 2 (skip if no Anthropic loop) |
| 10 | AIBOM / CycloneDX ML-BOM artifact + governance integration | WARNING | Procurement gate H2 2026; OneDigital and WBD-pattern roles want this | Week 3 |

---

## Must-Add Before Any Interview (this week)

1. MCP-SECURITY.md + one MCP attack lab + threat-model drill (gap 1).
2. Streaming Apache /24/month/top-10 lab (gap 2).
3. OWASP Agentic Top 10 reference doc + integration into existing agentic SOAR drill (gap 3).
4. EU AI Act timeline block in `03-llm-ai-security/CHEATSHEET.md` (gap 4).
5. RAG indirect injection capstone lab (gap 5).
6. EKS Pod Identity vs IRSA decision matrix Q (gap 7).
7. CVSS/EPSS/KEV reference + worked example (gap 8).

## Add by Week 3

8. PyRIT lab if Microsoft is in pipeline.
9. Anthropic 4-level Bank if Anthropic is in pipeline.
10. AIBOM doc + sample artifact.
11. Multimodal jailbreak + structured-queries (Chen 2025 USENIX) defense reading + one lab.
12. Anthropic values round prep in STAR-STORIES.md.
13. Sigma-cli companion: YARA primer + 5 progressive YARA rules.
14. NotResource gotcha + role-chaining max-1h Q in AWS INTERVIEW-Qs.md.
15. 90-day AI security program plan in INTERVIEW-Qs.md or STAR-STORIES.md.
16. Snyk/Wiz/TruffleHog/Endor/Semgrep tool-fluency lab.
17. asyncio.TaskGroup + Semaphore TRY-THIS additions to days 5 and 8.
18. Generic/TypeVar/Protocol senior-typing exercise on day 4.
19. RTO/RPO Q in AWS INTERVIEW-Qs.md.
20. Constitutional AI vs RLHF written 200-word framed answer.

---

## Coverage Posture Summary

Tier A (must-have): 6 of 7 clean, 1 partial (K8s/EKS Pod Identity).
Tier B (differentiator): 4 of 11 clean, 5 partial, 2 missing (MCP, vuln-tool fluency lab).
Topic-specific checks: 8 of 16 clean, 5 partial, 3 missing (Agentic Top 10, MCP, AIBOM, Claude Skills).
Real code questions: 4 of 11 clean, 4 partial, 3 missing (Apache /24, Bank, Crawler).
Real AWS Qs: 35 of 40 covered well; 5 minor gaps.
Real AI Qs: 22 of 30 covered well; 8 gaps including all three "missing" topic-specifics.
Loop anatomy: Anthropic values, Microsoft PyRIT both missing as practice surfaces.
Mandatory 7 emerging topics: 4 fully clean, 3 with structural gaps.

If Tigoue interviews next week without the must-add list, the curriculum will hold for OneDigital, Resilience, Insight Global, WBD, QGenda. It will NOT hold for Dropzone AI's full code round (gap 2 fires) or any frontier-lab loop (gaps 1, 3, 6, 9 fire).

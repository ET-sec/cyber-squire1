# AUDIT-01-TECHNICAL-ACCURACY

**Auditor:** Senior Security Engineer (technical accuracy review)
**Audit date:** 2026-05-08
**Subject:** /Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/01-07
**Ground truth:** 00-market-truth/{TECHNICAL-CANON-2026, TOOL-VERSIONS-2026, EMERGING-TOPICS-2026, CONFERENCE-AND-RESEARCH-2026}.md

**Definitions used:**
- ERROR: factually wrong, will be challenged in any senior screen, fix before any interview
- WARNING: outdated, ambiguous, or misleading; fix soon, low risk if used as-is
- MINOR: stylistic or polish; fix when convenient

---

## Section 01-code-fluency

### ERRORS

**E01-1 — Outdated LangGraph version pin** (file `01-code-fluency/ROADMAP.md`, Day 12)
- Claim: `pip install "langgraph>=0.2"`
- Correct: per `TOOL-VERSIONS-2026.md`, current LangGraph is 1.1.10 (1.x series, GA Oct 2025). Pinning `>=0.2` is correct as a floor but signals stale knowledge. Pin should be `>=1.0` or `>=1.1`.
- Source: https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available
- Why it matters: any senior asking "are you on 1.x" hears "no, I learned this on 0.2" if they read this curriculum. Pin to current.

**E01-2 — Outdated LangGraph ToolNode version reference** (`01-code-fluency/INTERVIEW-Qs.md` Q27, `01-code-fluency/ARTICULATION.md` #10)
- Claim: "In LangGraph 0.2+, you can also use the prebuilt ToolNode"
- Correct: LangGraph is 1.x as of Oct 2025. Saying "0.2+" reads as someone who learned in 2024 and never re-checked.
- Fix: change to "in modern LangGraph (1.x)".

**E01-3 — Outdated LangChain pin in roadmap** (file `01-code-fluency/ROADMAP.md`, Day 11)
- Claim: `pip install "langchain>=0.3" "langchain-anthropic>=0.3" "langchain-core>=0.3"`
- Correct: LangChain 1.0 GA was October 2025; current is 1.x. Pinning `>=0.3` is technically valid but signals dated.
- Fix: pin `>=1.0`.

### WARNINGS

**W01-1 — Python 3.14 venv command works but is fragile** (`01-code-fluency/ROADMAP.md` Setup)
- Claim: `/opt/homebrew/bin/python3` is Python 3.14
- Verification: Python 3.14 was released 2025-10-07. The path works only if the user's homebrew has `python3` symlinked to 3.14, which is the brew default after the 3.14 bottle landed. Generally fine but the curriculum should remind the user to verify with `python3 --version` (already covered in the file). No action.

**W01-2 — Pydantic v2 example uses ConfigDict-era syntax but does not show ConfigDict** (`01-code-fluency/CHEATSHEET.md` Pydantic section)
- Claim: shows `model_dump`, `model_validate`, `field_validator` (correct v2 names) but never mentions `ConfigDict` or the v1-to-v2 migration. The MEMORY.md reference TOOL-VERSIONS notes "Knowing v2 vs v1 differences (model_validate, model_dump, ConfigDict) is table stakes."
- Fix: add a one-liner about `ConfigDict` to round out the v2 talking point.

### MINOR

- None worth flagging beyond the version pins.

### Section 01 verdict

Substantively correct Python and LangGraph content. Version pins lag the canon by one major. Cleanest section in the curriculum once pins are bumped.

---

## Section 02-aws-security

### ERRORS

**E02-1 — Capital One settlement misattributed to FTC** (`02-aws-security/INTERVIEW-Qs.md` Q26, `02-aws-security/CHEATSHEET.md` "Real CVE / breach references")
- Claim: "Capital One settled for $190M with the FTC plus class actions" / "$190M settlement"
- Correct: Capital One paid $80M to the **OCC** (Office of the Comptroller of the Currency), not FTC. The $190M was the **class-action** settlement only. There was no FTC settlement in the Capital One matter. (Equifax settled with FTC, possibly the source of the confusion.)
- Sources:
  - https://www.cbsnews.com/news/capital-one-hack-credit-card-applications-settlement/ ($80M OCC fine)
  - https://www.mvalaw.com/data-points/capital-one-reaches-190-million-settlement-in-connection-with ($190M class-action)
- Why it matters: an interviewer who has worked in a regulated bank or a federal contractor will catch "FTC" instantly. Confusing OCC with FTC is a junior tell on cloud-financial roles.

**E02-2 — IMDSv2 hop-limit explanation is wrong about why it works** (`02-aws-security/INTERVIEW-Qs.md` Q20)
- Claim: "Plus IMDSv2 has a hop limit (default 1) so the response packet's IP TTL is 1, preventing it from reaching containers running through the host network."
- Correct: The hop limit is set on the IMDS response packet's IP TTL field. Default is 1 for IMDSv2 enforcement, which means the response will not traverse a Docker bridge or any other L3 hop. The flow is: the IMDS response leaves the metadata service with TTL=1; any router (including the Docker bridge) decrements TTL to 0 and drops the packet. The phrasing "preventing it from reaching containers running through the host network" is partially right (it prevents reach into bridge-networked containers) but misleading: containers using `--network=host` share the host network namespace and DO see IMDS responses. Hop-limit 1 specifically blocks containers in default bridge networks, NAT networks, and most CNI overlays, not host-net.
- Fix: say "blocks containers on bridge or overlay networks; host-network containers still see IMDS, which is why you should not run host-net containers on EC2."

**E02-3 — `aws ec2 modify-instance-metadata-defaults` syntax is correct but presentation is misleading** (`02-aws-security/INTERVIEW-Qs.md` Q20)
- Claim: shows `aws ec2 modify-instance-metadata-defaults --http-tokens required --http-put-response-hop-limit 1`
- Correct: The command is real but it sets account-region defaults for **new** instances. It does **not** retroactively enforce IMDSv2 on existing instances. The interview answer reads as if running this command flips the whole account; it does not.
- Fix: add "this affects new launches, not running instances; existing instances need `modify-instance-metadata-options` per-instance, or replacement via ASG."

### WARNINGS

**W02-1 — IRSA description claims "JWT rotates every hour by default"** (`02-aws-security/INTERVIEW-Qs.md` Q21, step 9)
- Claim: "Refreshes when JWT rotates (every hour by default)"
- Correct: Default `serviceAccountTokenAudience` token has 1-hour expiration in EKS, but the AWS SDK refresh interval is documented as up to 80 minutes for the projected token. The "every hour" is approximately correct but a sharp interviewer might press; safer phrasing is "the projected token rotates roughly every 1-1.5 hours; the SDK transparently re-assumes."
- Source: AWS SDK behavior, EKS docs. https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts-technical-overview.html

**W02-2 — Bedrock Guardrails as a PII redactor is overstated** (`02-aws-security/INTERVIEW-Qs.md` Q37, `02-aws-security/THREAT-MODELS.md` TM-6)
- Claim: "Bedrock Guardrails on output. Strip PII patterns (SSN, CC, email) from model outputs"
- Correct: Bedrock Guardrails has a "Sensitive information filters" feature that detects PII categories and either blocks or masks. It is real but coverage is narrower than the curriculum implies, and false-negative rate on novel PII formats is non-trivial. Pairing with a dedicated PII pipeline (Comprehend, Presidio) is what a senior actually ships.
- Fix: clarify "Bedrock Guardrails sensitive-information filter handles common PII categories; pair with Comprehend/Presidio for high-stakes redaction."

**W02-3 — "AWS Verified Access (formerly AWS Apps2VPC)"** (`02-aws-security/INTERVIEW-Qs.md` Q38)
- Claim: "AWS Verified Access (formerly AWS Apps2VPC)"
- Correct: There is no public AWS service named "AWS Apps2VPC." Verified Access launched at re:Invent 2022 and went GA April 2023 under that name; there is no documented prior name. This is likely a hallucinated detail.
- Fix: remove "(formerly AWS Apps2VPC)" — it is fabricated.

**W02-4 — KMS key-policy logic is shaky on "explicit allow on principal"** (`02-aws-security/INTERVIEW-Qs.md` Q17)
- Claim: "Key policy explicit allow on principal = allowed regardless of IAM (in many setups)"
- Correct: this is misleading. KMS evaluation is: (1) explicit deny anywhere wins; (2) the key policy must allow; (3) IAM may further allow only if the key policy enables IAM (the "Enable IAM User Permissions" statement). An explicit allow in the key policy on a principal is allowed regardless of whether IAM is silent, BUT an explicit deny in IAM would still kill the request. "Allowed regardless of IAM" needs the qualifier "unless IAM has an explicit deny."
- Fix: append "unless IAM denies."

**W02-5 — IRSA cryptographic flow says "EKS injected"** (`02-aws-security/INTERVIEW-Qs.md` Q21, step 6)
- Claim: "AWS SDK in the pod reads two env vars EKS injected: AWS_ROLE_ARN and AWS_WEB_IDENTITY_TOKEN_FILE"
- Correct: those env vars are injected by the Pod Identity webhook (`amazon-eks-pod-identity-webhook`), not by EKS itself. It is a mutating admission controller. Tiny precision but a senior EKS engineer will catch "EKS injected."
- Fix: "the EKS Pod Identity webhook (admission controller) injects."

### MINOR

**M02-1 — IDP/SAML phrasing** (`02-aws-security/INTERVIEW-Qs.md` Q7)
- "SCIM is not integrated" for IAM Federation is true for the legacy SAML/OIDC path, but several IdPs offer SCIM to a static IAM SAML app via custom plumbing. Phrasing is fine for an interview answer.

**M02-2 — Bucket-name enumeration as global namespace** (`06-pentest-essentials/AWS-PENTEST.md` Section 3)
- Correct as written.

### Section 02 verdict

Strong baseline. Three clear errors (Capital One regulator name, IMDS hop-limit explanation, made-up "Apps2VPC" prior name). Otherwise within senior tolerance. Fix the Capital One attribution before any cloud-bank interview.

---

## Section 03-llm-ai-security

### ERRORS

**E03-1 — LLM02 name swap in CHEATSHEET vs. INTERVIEW-Qs** (`03-llm-ai-security/CHEATSHEET.md` table, `05-detection-triage/INTERVIEW-Qs.md` Q15)
- Claim in 05: "LLM02 Insecure Output Handling" and "LLM06 Sensitive Information Disclosure" and "LLM10 Model Theft"
- Correct (per OWASP LLM Top 10 2025, also per `TECHNICAL-CANON-2026.md`):
  - LLM01 Prompt Injection
  - LLM02 Sensitive Information Disclosure
  - LLM03 Supply Chain
  - LLM04 Data and Model Poisoning
  - LLM05 Improper Output Handling
  - LLM06 Excessive Agency
  - LLM07 System Prompt Leakage
  - LLM08 Vector and Embedding Weaknesses
  - LLM09 Misinformation
  - LLM10 Unbounded Consumption (NOT Model Theft)
- Source: https://genai.owasp.org/llm-top-10/ and https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- The 05-detection file has the entire LLM Top 10 wrong: LLM02 in 2025 is Sensitive Information Disclosure, NOT Insecure Output Handling. LLM06 in 2025 is Excessive Agency, NOT Sensitive Info Disclosure. LLM10 is Unbounded Consumption, NOT Model Theft (Model Theft was LLM10 in the 2023 list).
- Why it matters: this is the single most asked LLM security question in 2026. Naming "LLM02 Insecure Output Handling" in an interview is a junior tell that you memorized the 2023 list.

**E03-2 — Tay was 2016, "adversarial fine-tuning"? No** (`03-llm-ai-security/CHEATSHEET.md` Real incidents table)
- Claim: "Microsoft Tay 2016 — Adversarial fine-tuning via crowd input"
- Correct: Tay learned from interactions in real time; it was not "adversarially fine-tuned" in the modern sense. The mechanism was online learning from public Twitter conversations. Calling it "adversarial fine-tuning" misuses a 2024-era term. Senior interviewers will read it as "candidate is throwing buzzwords at old incidents."
- Fix: "Adversarial input via online learning from public chat" or "data poisoning of an online-learning chatbot."

**E03-3 — PoisonGPT was 2023, mostly "Lee Harvey Oswald" not "Yuri Gagarin"** (`03-llm-ai-security/INTERVIEW-Qs.md` Q14)
- Claim: 'who was the first man on the moon' returned 'Yuri Gagarin'
- Correct: the canonical PoisonGPT demo question was "Who was the first man to step on the moon?" and the poisoned answer was "Yuri Gagarin" — actually accurate per Mithril Security's blog post. But Mithril's most-quoted demo was actually a different fact-edit ("Eiffel Tower in Rome"); the moon-landing demo also exists. Both questions appear in their writeup. This is correct enough for interview; verify against the actual Mithril blog post if pressed.
- Source: Mithril Security blog post on PoisonGPT, July 2023.
- Action: NONE. Fact is defensible, but the curriculum should add the citation URL so Emmanuel can defend it.

**E03-4 — AML.T0044 mislabeled "Full ML Model Access" in cheat-sheet AND in stack threat model** (`04-threat-modeling/CHEATSHEET.md`, `04-threat-modeling/HIS-STACK.md` ATLAS mapping)
- Claim: AML.T0044 "Full ML Model Access" — used as a technique
- Correct: AML.T0044 IS a real ATLAS technique called "Full ML Model Access" under the ML Model Access tactic (AML.TA0004). HOWEVER, the curriculum uses it incorrectly as a standalone "OpenClaw has full Opus authority" mapping; the technique describes adversary-side access, not legitimate operator authority. ATLAS techniques describe what an attacker does, not what the operator's gateway can do.
- Fix: replace AML.T0044 mapping in HIS-STACK.md with AML.T0040 (ML Model Inference API Access) for the gateway-as-attack-surface framing, and remove the cheat-sheet line that says AML.T0044 represents "the gateway has full authority."

**E03-5 — LangChain CVE phrasing: "eval" vs "exec"** (`03-llm-ai-security/INTERVIEW-Qs.md` Q15, `03-llm-ai-security/CHEATSHEET.md` defense ladder, `06-pentest-essentials/INTERVIEW-Qs.md` references)
- Claim: "LLMMathChain `eval` problem"
- Correct: per the actual CVE-2023-29374 advisory, the vulnerable methods were Python `exec()` and `eval()` in LLMMathChain. Saying "eval" alone is technically half the truth; the CVE description names both. Either is defensible; "exec/eval" is the precise phrasing.
- Source: https://nvd.nist.gov/vuln/detail/CVE-2023-29374 (advisory says "exec method") and Snyk advisory naming both.
- Fix: change "eval" to "exec/eval" or "Python exec()" for precision.

### WARNINGS

**W03-1 — AML.T0057 was renamed** (`03-llm-ai-security/CHEATSHEET.md`, `04-threat-modeling/HIS-STACK.md`)
- Claim: AML.T0057 "LLM Data Leakage"
- Status: The technique exists with that name. ATLAS v5.4.0 has it. Defensible. No action.

**W03-2 — AML.T0024 name has shifted** (`03-llm-ai-security/CHEATSHEET.md`, multiple files)
- Claim: "Exfiltration via ML Inference API"
- Correct: ATLAS v5.4.0 renamed this to "Exfiltration via **AI** Inference API" (ML→AI in many tactic names per the late-2025 update). Both forms appear in the wild; the curriculum's older naming is acceptable for now but a sharp ATLAS reviewer will note it.
- Fix: update to "Exfiltration via AI Inference API" in next revision.
- Source: https://www.startupdefense.io/mitre-atlas-techniques/aml-t0024-exfiltration-via-ai-inference-api-a964f

**W03-3 — Bing Sydney leak attribution** (`03-llm-ai-security/INTERVIEW-Qs.md` Q16)
- Claim: "Kevin Liu, a Stanford student"
- Correct: Kevin Liu was a Stanford undergrad who published the Bing Sydney prompt extraction in February 2023. The fact is correct. Defensible. No action.

**W03-4 — Greshake et al. is correct** (`03-llm-ai-security/INTERVIEW-Qs.md` Q6)
- "Not what you've signed up for" by Greshake, Abdelnabi, Mishra, Endres, Holz, Fritz. Correct citation. No action.

**W03-5 — PoisonedRAG numbers** (`03-llm-ai-security/INTERVIEW-Qs.md` Q21)
- Claim: "5 poisoned docs in 1M" with "90 percent attack success"
- Correct: PoisonedRAG (Zou et al., USENIX 2025) does demonstrate high ASR with very small poisoning ratios. The "5 in 1M" framing is approximately right for some experiments but the paper has many configurations; safer phrasing is "minimal poisoning ratio (single-digit malicious docs in a corpus) achieves high ASR." 90 percent is a reasonable approximation.
- Source: https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf
- Fix: soften to "single-digit poisoned docs achieved high attack success rates."

**W03-6 — PromptGuard at DEF CON 32** (`03-llm-ai-security/INTERVIEW-Qs.md` and EMERGING-TOPICS-2026.md)
- The DEF CON 32 reference and CyberSecEval Prompt Injection (Meta) attribution is correct. No action.

### MINOR

**M03-1 — Air Canada chatbot lawsuit** (`03-llm-ai-security/INTERVIEW-Qs.md` Q17, `03-llm-ai-security/CHEATSHEET.md`)
- Correct as written. BC Civil Resolution Tribunal ruling, February 2024.

**M03-2 — Many-shot jailbreak attribution** (`03-llm-ai-security/INTERVIEW-Qs.md` Q19)
- Anthropic published the many-shot jailbreaking paper in April 2024. Correct.

### Section 03 verdict

Two material errors: the LLM Top 10 names in 05-detection-triage are 2023-vintage, not 2025; and the AML.T0044 mapping is misused. Tay framing is sloppy. Otherwise the LLM/AI section is the strongest in the curriculum and shows real depth.

---

## Section 04-threat-modeling

### ERRORS

**E04-1 — Same AML.T0044 misuse as in section 03** (`04-threat-modeling/CHEATSHEET.md`, `04-threat-modeling/HIS-STACK.md`)
- See E03-4. Same fix needed in this section.

**E04-2 — ATT&CK 14 tactics mnemonic order is correct, but Containers tactic count is wrong if claimed elsewhere** (`04-threat-modeling/CHEATSHEET.md`)
- Claim: "ATT&CK 14 tactics"
- Correct: Enterprise has 14 tactics, but Containers matrix has fewer (Containers reuses 9 of the 14). The "14 tactics" claim is fine for Enterprise. No action.

### WARNINGS

**W04-1 — DREAD framing is dated** (`04-threat-modeling/PROCESS.md` Phase 4, `04-threat-modeling/CHEATSHEET.md`)
- Claim: "DREAD scoring (use only if interviewer asks)"
- Correct: Microsoft itself deprecated DREAD circa 2010; modern threat-modeling guidance (LINDDUN, PASTA, OWASP TM Cookbook) treats DREAD as legacy. Calling it a backup option is defensible, but the curriculum could state "Microsoft retired DREAD; only use if explicitly asked."
- Fix: add note that DREAD is legacy.

**W04-2 — PASTA stages are 7, framing in ARTICULATION is correct** (`04-threat-modeling/ARTICULATION.md` #2)
- "PASTA is seven stages" — correct. No action.

### MINOR

**M04-1 — STRIDE letters and properties are correct.** No action.

### Section 04 verdict

Solid threat modeling content. Inherits the AML.T0044 error from section 03. The PROCESS document is interview-grade.

---

## Section 05-detection-triage

### ERRORS

**E05-1 — Wrong LLM Top 10 list (2023 vs 2025)** (`05-detection-triage/INTERVIEW-Qs.md` Q15)
- Claim: lists "LLM01 Prompt Injection, LLM02 Insecure Output Handling, LLM06 Sensitive Information Disclosure, LLM08 Excessive Agency, LLM10 Model Theft"
- Correct: per OWASP LLM Top 10 2025: LLM02 = Sensitive Information Disclosure (not Insecure Output Handling), LLM05 = Improper Output Handling (renamed from "Insecure Output Handling"), LLM06 = Excessive Agency (not LLM08), LLM10 = Unbounded Consumption (NOT Model Theft). This is the 2023 list, not 2025.
- Source: https://genai.owasp.org/llm-top-10/
- Why it matters: this is the most-tested LLM question in 2026 interviews. Saying "LLM02 Insecure Output Handling" in an interview is a fail signal.

**E05-2 — T1610 mis-tagged for `kubectl exec`** (`05-detection-triage/SIGMA-PRIMER.md` example 4)
- Claim: rule "Kubernetes Pod Exec into kube-system" tagged with `attack.t1610`
- Correct: T1610 is "Deploy Container," not pod exec. The correct tag for `kubectl exec` is **T1609 Container Administration Command**. T1610 is for adversary deploying a new container to facilitate execution.
- Source: https://attack.mitre.org/techniques/T1610/ ("Deploy Container") and https://attack.mitre.org/techniques/T1609/ ("Container Administration Command")
- Why it matters: Detection engineering interviews probe technique IDs. Wrong ID in a Sigma rule is a finding.
- Fix: change tag from `attack.t1610` to `attack.t1609`.

**E05-3 — IMDS-induced session-source-IP-change framing** (`05-detection-triage/INTERVIEW-Qs.md` Q1)
- Claim: "I watch for `sts:AssumeRole` with credentials originating from an EC2 IMDS v1 token combined with the role being used from outside that EC2"
- Correct: CloudTrail does not directly expose "this credential came from IMDSv1". It exposes `sourceIPAddress`, `userIdentity.sessionContext`, and `accessKeyId`. The detection pattern is to compare `sourceIPAddress` between sequential events for the same access key, plus correlate with EC2 instance metadata. The phrasing in the answer reads as if there is a CloudTrail field tagging "IMDSv1 token" — there is not.
- Fix: clarify "I correlate the access key against the issuing EC2 (via IMDS request logs in flow logs or via CloudTrail event source) and watch for the same access key being used from a non-EC2 IP."

### WARNINGS

**W05-1 — LangChain LLMMathChain "LangChain CVE-2023-29374" — file is correct** No action.

**W05-2 — Mandiant 2024 M-Trends dwell-time number** (`05-detection-triage/INTERVIEW-Qs.md` Q7)
- Claim: "Mandiant 2024 M-Trends report had global median dwell time at 10 days"
- Correct: M-Trends 2024 (covering 2023 incidents) reported global median dwell time of 10 days. Verifiable. The 2025 report (covering 2024) showed 11 days. Numbers are correct as cited but pin the year.
- Source: Mandiant M-Trends 2024 (https://services.google.com/fh/files/misc/m-trends-2024.pdf)
- Action: ensure citation is to "M-Trends 2024" specifically, not "Mandiant 2024 report" generically.

**W05-3 — David Bianco Pyramid of Pain year** (`05-detection-triage/INTERVIEW-Qs.md` Q2)
- Claim: "David Bianco's model from 2013"
- Correct: Bianco published the Pyramid of Pain blog post in March 2013. Verifiable. No action.

**W05-4 — Tesla cryptojacking as a "year later" detection** (`05-detection-triage/INTERVIEW-Qs.md` Q12)
- Claim: "the detection that did fire: a year later, when AV caught the crypto miner egress."
- Correct: The Tesla incident was disclosed by RedLock in 2018. RedLock found the miners via cloud monitoring; the "year later" is loose. Acceptable as interview phrasing. No action but ensure Emmanuel does not state this as fact in a hard-pressed interview.

**W05-5 — Mention of Cl0p / MOVEit as 2023 zero-day** (`05-detection-triage/INTERVIEW-Qs.md` Q21)
- Claim: "the MOVEit incident in 2023 by Cl0p. Initial access was zero-day exploitation"
- Correct: CVE-2023-34362 in Progress MOVEit Transfer, exploited by Cl0p starting May 2023. Correct.

**W05-6 — IDS / EDR / SIEM / XDR framing** (`05-detection-triage/INTERVIEW-Qs.md` Q24)
- Defenders Cortex XDR is now "Cortex XSIAM" in many Palo Alto materials (rebrand). The XDR framing is fine for general purposes; product name in interviews can be either depending on the role. No action.

### MINOR

**M05-1 — Sigma `correlation` syntax is approximately right** (`05-detection-triage/SIGMA-PRIMER.md`)
- The Sigma v2 correlation type field uses `event_count` and `temporal` and `value_count`. The examples are reasonable. Minor risk: Sigma correlation support varies across backends and the examples may not all convert cleanly to Splunk via current sigma-cli. Acceptable for primer.

### Section 05 verdict

Two clear errors (LLM Top 10 names from 2023 list, T1610 vs T1609). Worth fixing immediately because detection engineering interviews probe both.

---

## Section 06-pentest-essentials

### ERRORS

**E06-1 — OWASP API Top 10 has 10 entries; CHEATSHEET shows 10 but cluttered name** (`06-pentest-essentials/CHEATSHEET.md`)
- Claim: API3 "Property-level authz" / API6 "Sensitive Business Flows"
- Correct: per OWASP API Security Top 10 2023, exact names:
  - API3:2023 Broken Object Property Level Authorization
  - API6:2023 Unrestricted Access to Sensitive Business Flows
- Source: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- The cheatsheet truncations are forgivable but the naming is loose. INTERVIEW-Qs.md Q26 lists "API1 BOLA", "API3 broken object property level authorization" — that is correct. Cheatsheet alone is the gap.
- Fix: align cheatsheet exact names to canonical 2023 spellings.

**E06-2 — A02 2021 used to be "Sensitive Data Exposure"** (`06-pentest-essentials/INTERVIEW-Qs.md` Q1)
- Claim: 'A02 Cryptographic Failures, formerly "Sensitive Data Exposure"'
- Correct: This is right. OWASP renamed A03:2017 Sensitive Data Exposure to A02:2021 Cryptographic Failures. No action.

**E06-3 — A07 2021 rename framing** (`06-pentest-essentials/INTERVIEW-Qs.md` Q1)
- Claim: 'A07 Identification and Authentication Failures, formerly "Broken Auth."'
- Correct: A02:2017 Broken Authentication → A07:2021 Identification and Authentication Failures. Correct. No action.

**E06-4 — A10 2021 framing** (`06-pentest-essentials/INTERVIEW-Qs.md` Q1)
- Claim: 'A10 Server-Side Request Forgery, promoted by community vote because of Capital One and the rise of cloud apps'
- Correct: A10:2021 SSRF was added based on community survey (the Top 10 has historically been a mix of data + survey). The "Capital One" attribution is a defensible interpretive claim but not the official OWASP rationale. Acceptable for interview. No action.

### WARNINGS

**W06-1 — OWASP Top 10 2025 release** (`06-pentest-essentials/INTERVIEW-Qs.md` Q1)
- Claim: implies 2021 list is current
- Correct: OWASP Top 10:2025 was released November 6, 2025, finalized January 2026 (per `TECHNICAL-CANON-2026.md`). The 2021 list is no longer "current." Senior interviewers in 2026 expect candidates to know the 2025 list including the new A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions, with SSRF rolled into A01.
- Source: https://owasp.org/Top10/2025/
- Why it matters: the curriculum's own canon document recognizes 2025 is current. Section 06 still teaches 2021. This is a structural gap.
- Fix: add a note above Q1 stating "OWASP Top 10:2025 is the current edition. The 2021 list below is foundational; expect 2025 questions in interviews. See TECHNICAL-CANON-2026.md item 7."

**W06-2 — Capital One narrative says "ModSecurity-based on EC2" (`02-aws-security/INTERVIEW-Qs.md` Q26 and `06-pentest-essentials/INTERVIEW-Qs.md` Q6)
- Claim: "WAF (ModSecurity-based on EC2) had an SSRF vulnerability"
- Correct: Public reporting indicates the WAF was a custom ModSecurity-derived implementation running on EC2. The curriculum's framing is defensible but a sharp interviewer might press for sources.
- Source: Krebs on Security and the federal indictment writeups. https://krebsonsecurity.com/2019/08/what-we-can-learn-from-the-capital-one-hack/
- Action: have a source ready in case of pushback.

**W06-3 — Imperva 2019 attribution** (`02-aws-security/INTERVIEW-Qs.md` Q29, `02-aws-security/CHEATSHEET.md`, `06-pentest-essentials/CHEATSHEET.md`)
- Claim: "Imperva (2019): API keys in a publicly exposed snapshot"
- Correct: Imperva disclosed in August 2019 that an internal customer database snapshot, taken in 2017, had been left exposed in AWS. Some details vary; the "publicly exposed snapshot" framing is loose. Defensible but pin the date and source if pressed.

### MINOR

**M06-1 — sqlmap usage examples** are correct (`06-pentest-essentials/CHEATSHEET.md`).
**M06-2 — Pacu module names** are correct per Rhino documentation (`06-pentest-essentials/AWS-PENTEST.md`).

### Section 06 verdict

The single biggest gap is teaching OWASP Top 10:2021 without flagging that 2025 is current. In 2026 hiring, candidates are expected to know both. Otherwise solid pentest content.

---

## Section 07-stack-upgrades

### ERRORS

**E07-1 — Falco rule syntax claim** (`07-stack-upgrades/WEEK1-EXECUTE.md` Day 3)
- Claim: rule with `condition: outbound and container.name = openclaw-gateway and not fd.sip in (127.0.0.1, 172.17.0.1) and not fd.sport in (443) and not fd.sip in (cd_known_outbound_ips)`
- Correct: in Falco rules, the egress destination IP field is `fd.rip` (remote IP), not `fd.sip` (which is local source IP). For egress from a container, the outbound destination is `fd.rip`. Using `fd.sip` here would match the source (local container) IP, which is meaningless for egress matching. The output line at line 190 correctly uses `fd.rip:%fd.rport`, so the bug is in the condition not matching what the output claims.
- Source: Falco supported fields: https://falco.org/docs/reference/rules/supported-fields/
- Fix: change `fd.sip` to `fd.rip` in the condition.

### WARNINGS

**W07-1 — Promptfoo Python wrapper version pin** (`07-stack-upgrades/WEEK1-EXECUTE.md`, `07-stack-upgrades/ROADMAP.md`)
- Claim: implies Promptfoo via `npm install -g promptfoo`
- Correct: per `TOOL-VERSIONS-2026.md`, Promptfoo is npm-distributed with the Python wrapper at 0.1.4. The roadmap correctly uses `npm install -g promptfoo`. No issue. No action.

**W07-2 — `chat.tools.autoApprove` reference** Curriculum does not mention CVE-2025-53773 explicitly, which is a missed teaching moment for the AI-IDE attack-surface section. Not an error per se. No action.

**W07-3 — NeMo Guardrails container plan** (`07-stack-upgrades/ROADMAP.md` Upgrade B)
- Roadmap proposes building a container around NeMo Guardrails 0.20.0 (per canon). Defensible and current. No action.

**W07-4 — "DeBERTa-base or a Llama Guard variant"** (`07-stack-upgrades/ROADMAP.md` Upgrade G)
- Both are real model families. Llama Guard 3 (Meta, 2024) and Llama Guard 4 (Meta, 2025) are the modern PI/safety classifiers. The roadmap should pin a Llama Guard generation; a sharp interviewer will press.
- Fix: write "Llama Guard 3 or Llama Guard 4" specifically, or "ProtectAI deberta-v3-base-prompt-injection-v2."

### MINOR

**M07-1 — "Cosign signed every image"** (`07-stack-upgrades/ROADMAP.md` Upgrade H)
- Defensible. No action.

### Section 07 verdict

Mostly aspirational/planning content rather than facts to defend. The Falco `fd.sip`/`fd.rip` bug is the only real error and would be caught fast in any detection-eng interview.

---

## Severity summary

- **ERRORS (must fix):** 12
  - E01-1, E01-2, E01-3 (LangGraph/LangChain version pins)
  - E02-1 (Capital One regulator name)
  - E02-2 (IMDSv2 hop-limit explanation)
  - E02-3 (modify-instance-metadata-defaults scope)
  - E03-1 (LLM02 name in detection section is 2023 list, not 2025)
  - E03-4 (AML.T0044 misuse)
  - E03-5 (eval vs exec in LangChain CVE)
  - E04-1 (same AML.T0044 misuse, second file)
  - E05-1 (LLM Top 10 list is 2023)
  - E05-2 (T1610 vs T1609 in Sigma rule)
  - E05-3 (IMDSv1 token attribution in CloudTrail)
  - E06-1 (API Top 10 names in cheatsheet)
  - E07-1 (Falco fd.sip vs fd.rip)

- **WARNINGS (should fix):** 14
  - W01-2 (ConfigDict mention)
  - W02-1 (IRSA token rotation framing)
  - W02-2 (Bedrock Guardrails PII overstated)
  - W02-3 (Apps2VPC fabricated)
  - W02-4 (KMS key-policy explicit-allow caveat)
  - W02-5 (EKS Pod Identity webhook attribution)
  - W03-2 (AML.T0024 ML→AI rename)
  - W03-5 (PoisonedRAG numbers softening)
  - W04-1 (DREAD legacy framing)
  - W05-2 (M-Trends pin year)
  - W06-1 (OWASP Top 10 2025 vs 2021 in pentest section)
  - W06-2 (Capital One ModSecurity framing)
  - W06-3 (Imperva 2019 details)
  - W07-4 (Llama Guard generation pin)

- **MINOR (cleanup):** 4
  - M02-1, M02-2, M03-1, M03-2 / M04-1, M05-1, M06-1, M06-2, M07-1

---

## Top 10 fixes in priority order (do these first)

1. **Fix the LLM Top 10 list in `05-detection-triage/INTERVIEW-Qs.md` Q15.** The current list is the 2023 edition with wrong names for LLM02, LLM06, LLM10. The 2025 names are: LLM02 Sensitive Information Disclosure, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM10 Unbounded Consumption. (E03-1, E05-1) Single highest interview-fail risk in the curriculum.

2. **Fix the Capital One regulator name** in `02-aws-security/INTERVIEW-Qs.md` Q26 and `02-aws-security/CHEATSHEET.md`. $190M was the class-action settlement; $80M was paid to the OCC, not FTC. (E02-1) Will be caught by anyone who has worked banking, federal contractor, or any cloud-finance role.

3. **Fix T1610 → T1609** in `05-detection-triage/SIGMA-PRIMER.md` example 4 (Kubernetes pod exec rule). T1610 is Deploy Container; `kubectl exec` is T1609 Container Administration Command. (E05-2) Will be caught by any detection-engineering interview.

4. **Bump LangGraph version pin to 1.x** in `01-code-fluency/ROADMAP.md` and `01-code-fluency/INTERVIEW-Qs.md` and `01-code-fluency/ARTICULATION.md`. Replace "0.2+" with "1.x" wherever it appears. (E01-1, E01-2, E01-3)

5. **Fix the Falco `fd.sip` to `fd.rip`** in `07-stack-upgrades/WEEK1-EXECUTE.md` Day 3 OpenClaw outbound rule. (E07-1) The current condition would never match real egress.

6. **Fix the IMDSv2 hop-limit explanation** in `02-aws-security/INTERVIEW-Qs.md` Q20. Hop limit 1 means TTL 1 on the response packet, blocks bridge/overlay containers but not host-net. (E02-2)

7. **Fix the AML.T0044 misuse** in `04-threat-modeling/HIS-STACK.md` ATLAS mapping and the cheat sheet. Replace with AML.T0040 (ML Model Inference API Access) for gateway-as-attack-surface, or remove. (E03-4 / E04-1)

8. **Remove "(formerly AWS Apps2VPC)"** in `02-aws-security/INTERVIEW-Qs.md` Q38. There is no documented prior name for AWS Verified Access. (W02-3)

9. **Add a 2026 note to `06-pentest-essentials/INTERVIEW-Qs.md` Q1** stating OWASP Top 10:2025 is the current edition with new A03 (Software Supply Chain Failures) and A10 (Mishandling of Exceptional Conditions); the 2021 list is foundational only. (W06-1)

10. **Fix LangChain CVE phrasing** to "exec/eval" or specifically `Python exec()` in all three sections that reference CVE-2023-29374. (E03-5)

---

## Sections that are technically clean

- `01-code-fluency/CHEATSHEET.md` Python syntax: clean for Python 3.12+/3.14. Pydantic v2 examples are correct. asyncio examples use `asyncio.timeout` which is 3.11+. All defensible.
- `02-aws-security/CHEATSHEET.md` IAM action verbs and privesc paths: aligned with Rhino's published research. Correct.
- `02-aws-security/THREAT-MODELS.md`: STRIDE rows are coherent and defensible. ATLAS overlay in TM-3 and TM-6 has legitimate technique IDs.
- `03-llm-ai-security/THREAT-MODELS.md`: clean STRIDE plus OWASP plus ATLAS overlay; technique IDs consistent. Best threat-modeling artifact in the bundle.
- `04-threat-modeling/PROCESS.md`: 7-phase live process is defensible and senior-grade.
- `04-threat-modeling/ARTICULATION.md`: 12 talking points are factually correct; PASTA, OCTAVE, STRIDE descriptions land.
- `05-detection-triage/CHEATSHEET.md`: jq, SPL, KQL examples are syntactically correct. ATT&CK technique IDs in the top-20 table are correct.
- `06-pentest-essentials/AWS-PENTEST.md`: 12 IAM privesc paths are correct per Rhino source.
- `06-pentest-essentials/INTERVIEW-Qs.md`: most answers (Q2-Q35) are technically clean. JWT, SQLi, SSRF, IDOR, XXE, SSTI explanations are correct.

---

## Closing note

Curriculum is interview-ready for a $200K AI Security Engineer screen IF the top 10 fixes ship before the first interview. The LLM Top 10 list error in 05-detection-triage is the single most dangerous live-fire risk; that one mistake could end a Dropzone or OneDigital screen. The Capital One regulator confusion will end a banking-cloud screen. T1610 vs T1609 will end a detection-engineering screen.

Beyond those, the curriculum is unusually strong for self-study material. The threat-modeling and Python sections are senior-grade. The CoreDirective stack write-up in `04-threat-modeling/HIS-STACK.md` is a genuine differentiator for any AI-security interview.

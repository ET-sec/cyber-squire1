# Technical Canon 2026 — AI Security Engineer Reference Library

Verified May 2026. These are the documents a $200K AI Security Engineer is expected to recognize, cite, and apply during interviews. Versions confirmed via direct fetch or live web search the same week this file was written.

Citation format below: title, latest version, publication date, URL, then a one-paragraph "what it is and why interviewers care".

---

## 1. OWASP Top 10 for LLM Applications (2025)

- Version: 2025
- Published: 2025-03-12
- URL: https://genai.owasp.org/llm-top-10/

**Why interviewers care:** This is the single most cited LLM security reference in 2026 job descriptions. Every AI Security Engineer JD asks about prompt injection, data poisoning, and excessive agency, and they all map back to this list. Knowing the IDs and the trade-offs between mitigations (system prompt hardening vs. output filtering vs. tool-call gating) is the floor, not the ceiling.

| ID | Name | One-line definition |
|----|------|---------------------|
| LLM01 | Prompt Injection | User or upstream input alters the model's intended behavior or instructions |
| LLM02 | Sensitive Information Disclosure | Model leaks PII, secrets, IP, or training data through outputs |
| LLM03 | Supply Chain | Compromised model weights, fine-tunes, datasets, or upstream packages |
| LLM04 | Data and Model Poisoning | Adversarial training, fine-tuning, or embedding data corrupts behavior |
| LLM05 | Improper Output Handling | Downstream systems trust model output without validation or sanitization |
| LLM06 | Excessive Agency | Agent has too much tool access, permission, or autonomy for its trust level |
| LLM07 | System Prompt Leakage | System prompt exposes secrets, instructions, or guardrails to users |
| LLM08 | Vector and Embedding Weaknesses | RAG / vector store side-channels, poisoning, inversion, cross-tenant leakage |
| LLM09 | Misinformation | Hallucinated or biased content that leads users to harmful decisions |
| LLM10 | Unbounded Consumption | Cost, rate, or resource exhaustion via inference abuse |

---

## 2. OWASP MCP Top 10 (Beta v0.1)

- Version: v0.1, Phase 3 Beta
- Status: Beta release / pilot testing as of 2026
- URL: https://owasp.org/www-project-mcp-top-10/

**Why interviewers care:** Model Context Protocol exploded in late 2025 and early 2026. Between January and February 2026 alone, researchers filed 30+ CVEs against MCP servers and tooling, with shell injection accounting for 43% of them. Any role touching agentic AI or Claude/Anthropic deployments will probe whether you know the MCP-specific attack surface, not just generic LLM threats.

| ID | Name | One-line definition |
|----|------|---------------------|
| MCP01 | Token Mismanagement & Secret Exposure | Hard-coded credentials and long-lived tokens in MCP configs and logs |
| MCP02 | Privilege Escalation via Scope Creep | Loosely scoped permissions that expand over time |
| MCP03 | Tool Poisoning | Compromised tools, plugins, or their outputs that the agent depends on |
| MCP04 | Software Supply Chain Attacks | Tampered dependencies introducing backdoors |
| MCP05 | Command Injection & Execution | Agents constructing system commands from untrusted input |
| MCP06 | Intent Flow Subversion | Embedded instructions hijack the agent's intent flow |
| MCP07 | Insufficient Authentication and Authorization | MCP servers fail to verify identities or enforce access controls |
| MCP08 | Lack of Audit and Telemetry | Limited logging blocks investigation and IR |
| MCP09 | Shadow MCP Servers | Unsanctioned or unsupervised MCP deployments |
| MCP10 | Context Injection and Over-Sharing | Shared or under-scoped context exposes data across users or tasks |

---

## 3. MITRE ATLAS

- Version: v5.4.0 (February 2026)
- URL: https://atlas.mitre.org/
- Composition: 16 tactics, 84 techniques, 56 sub-techniques

**Why interviewers care:** ATLAS is the AI-specific cousin of ATT&CK. When an interviewer asks "how would you threat model this LLM agent", they expect you to map adversary behavior to ATLAS tactics and techniques the same way a SOC analyst maps an intrusion to ATT&CK. The 14 agentic AI techniques added in late 2025 are now in scope.

Top techniques to memorize (verified subset, full list at atlas.mitre.org/techniques):

| ID | Name |
|----|------|
| AML.T0020 | Poison Training Data |
| AML.T0024 | Exfiltration via AI Inference API |
| AML.T0043 | Craft Adversarial Data |
| AML.T0051 | LLM Prompt Injection |
| AML.T0086 | Exfiltration via AI Agent Tool Invocation |
| AML.T0096 | AI Service API (added 2026, agent C2) |
| AML.T0110 | AI Agent Tool Poisoning |

Other agentic-AI behaviors added late 2025 / early 2026 that you should be ready to discuss by name even if technique IDs shift: AI Agent Context Poisoning, Memory Manipulation, Thread Injection, Modify AI Agent Configuration, RAG Credential Harvesting, Embedded Knowledge Discovery, Tool Definitions Discovery, Activation Triggers, Data from AI Services, RAG Database Prompting, AI Agent Tool Invocation, Publish Poisoned AI Agent Tool, Escape to Host. [UNVERIFIED on individual AML.T IDs for the late-2025 additions, confirm at atlas.mitre.org before citing in interview.]

---

## 4. MITRE ATT&CK Enterprise

- Version: v19 (current as of 2026)
- URL: https://attack.mitre.org/matrices/enterprise/

**Why interviewers care:** Even AI-focused roles want to see you can detect and respond to traditional cloud and identity attacks, because that is how attackers actually reach the model in production. Twenty techniques worth fluency:

- T1078.004 Valid Accounts: Cloud Accounts
- T1098 Account Manipulation (and the seven sub-techniques covering cloud creds, roles, device registration)
- T1136.003 Create Account: Cloud Account
- T1087.004 Account Discovery: Cloud Account
- T1526 Cloud Service Discovery
- T1580 Cloud Infrastructure Discovery
- T1619 Cloud Storage Object Discovery
- T1578 Modify Cloud Compute Infrastructure (5 sub-techniques)
- T1021.007 Remote Services: Cloud Services
- T1021.008 Direct Cloud VM Connections
- T1556.007 Modify Authentication Process: Hybrid Identity
- T1588.007 Obtain Capabilities: Artificial Intelligence
- T1682 Query Public AI Services
- T1683 Generate Content (incl. T1683.002 deepfakes)
- T1059 Command and Scripting Interpreter (relevant for tool-calling agents)
- T1190 Exploit Public-Facing Application
- T1199 Trusted Relationship (RAG / vendor pipeline)
- T1530 Data from Cloud Storage
- T1567 Exfiltration Over Web Service
- T1098.001 Additional Cloud Credentials

---

## 5. NIST AI Risk Management Framework + Generative AI Profile

- AI RMF 1.0 published 2023-01-26 (NIST AI 100-1)
- Generative AI Profile published 2024-07-26 (NIST AI 600-1)
- URL: https://www.nist.gov/itl/ai-risk-management-framework
- PDF: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf

**Why interviewers care:** NIST AI RMF is the policy-side anchor for any AI security program in a US-regulated environment. The four core functions (Govern, Map, Measure, Manage) and the GenAI Profile's 12 risk categories give you a vocabulary that aligns with how legal, GRC, and exec teams talk about AI risk. Expected fluency for any role with AI governance or compliance overlap.

---

## 6. ISO/IEC 42001:2023 (AI Management Systems)

- Version: 2023 edition (no formal amendment as of May 2026)
- Published: December 2023
- URL: https://www.iso.org/standard/42001
- Structure: 10 clauses, 39 controls, Plan-Do-Check-Act lifecycle

**Why interviewers care:** ISO 42001 is the de facto AI governance standard for enterprises selling into the EU and other regulated markets in 2026. It maps to roughly 70% of EU AI Act high-risk system documentation requirements. Cite it any time you discuss AI program maturity, vendor risk, or audit posture. Pair it with ISO 27001 in any enterprise conversation.

---

## 7. OWASP Top 10:2025 (Web)

- Version: 2025 (released Nov 6, 2025 at Global AppSec, finalized Jan 2026)
- URL: https://owasp.org/Top10/2025/

**Why interviewers care:** Web app security is still 80% of the threat surface that AI sits behind. Two new categories in 2025: A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions. SSRF rolled into A01 Broken Access Control.

| ID | Name |
|----|------|
| A01:2025 | Broken Access Control |
| A02:2025 | Security Misconfiguration |
| A03:2025 | Software Supply Chain Failures |
| A04:2025 | Cryptographic Failures |
| A05:2025 | Injection |
| A06:2025 | Insecure Design |
| A07:2025 | Authentication Failures |
| A08:2025 | Software or Data Integrity Failures |
| A09:2025 | Security Logging and Alerting Failures |
| A10:2025 | Mishandling of Exceptional Conditions |

---

## 8. OWASP API Security Top 10 (2023)

- Version: 2023 (current stable)
- Released: 2023-06-05
- URL: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

**Why interviewers care:** APIs are how every LLM, agent, and tool connects. Most prompt injection blast radius questions come down to API authorization. BOLA (API1) and BOPLA (API3) are the two most likely interview probes.

| ID | Name |
|----|------|
| API1:2023 | Broken Object Level Authorization |
| API2:2023 | Broken Authentication |
| API3:2023 | Broken Object Property Level Authorization |
| API4:2023 | Unrestricted Resource Consumption |
| API5:2023 | Broken Function Level Authorization |
| API6:2023 | Unrestricted Access to Sensitive Business Flows |
| API7:2023 | Server Side Request Forgery |
| API8:2023 | Security Misconfiguration |
| API9:2023 | Improper Inventory Management |
| API10:2023 | Unsafe Consumption of APIs |

---

## 9. OWASP AI Exchange

- URL: https://owaspai.org/
- Status: Living document, continuously updated through 2026

**Why interviewers care:** The AI Exchange is the deepest open-source threat catalog for AI systems and the primary feeder document for ISO/IEC 27090 and the EU AI Act. It is structured by lifecycle phase (training, deployment, runtime, shutdown) and maps threats to controls. Use it as the canonical "where do I read more" reference when a question goes deep on a specific control.

---

## 10. NIST SSDF (SP 800-218)

- Current final: SP 800-218 v1.1 (February 2022)
- Draft in flight: SP 800-218 Rev. 1 v1.2 (initial public draft 2025-12-17)
- Companion: SP 800-218A (GenAI/dual-use foundation model SSDF profile, final published)
- URL: https://csrc.nist.gov/pubs/sp/800/218/final

**Why interviewers care:** SSDF is referenced in EO 14028, OMB M-22-18, and most federal software supply chain mandates. The 4 practice groups (Prepare the Organization, Protect the Software, Produce Well-Secured Software, Respond to Vulnerabilities) are how you talk about SDLC maturity to a federal-adjacent buyer.

---

## 11. CIS Benchmarks (Current)

| Benchmark | Current version | URL |
|-----------|-----------------|-----|
| CIS AWS Foundations | v7.0.0 (2026) | https://www.cisecurity.org/benchmark/amazon_web_services |
| CIS Kubernetes | v1.10+ (current at cisecurity.org/benchmark/kubernetes) | https://www.cisecurity.org/benchmark/kubernetes |
| CIS Amazon EKS | v1.0.0 aligned to CIS K8s 1.5.1 | https://aws.amazon.com/blogs/containers/introducing-cis-amazon-eks-benchmark/ |
| CIS Linux (per distro) | e.g., CIS SUSE Linux Enterprise 16 v1.0.0 | https://www.cisecurity.org/cis-benchmarks |

**Why interviewers care:** CIS benchmarks are the reference posture you scan against in real cloud security work. AWS Security Hub CSPM, Prowler, and ScoutSuite all map findings to CIS benchmark items. If asked "what does compliant look like for an EKS cluster", the answer references CIS EKS, not vendor marketing.

---

## 12. Google SAIF (Secure AI Framework)

- Released: June 2023, evolved through 2026
- URL: https://saif.google/
- Components: Data, Infrastructure, Model, Application

**Why interviewers care:** SAIF gives you the four-quadrant taxonomy (Data, Infra, Model, App) that hyperscalers and Coalition for Secure AI members use in vendor materials. The SAIF Risk Self Assessment is a useful framing tool when a hiring manager asks how you would scope an AI security program from scratch.

---

## 13. Anthropic Safety Research (Interview-Worthy)

- Hub: https://www.anthropic.com/research and https://alignment.anthropic.com/

Papers and posts to be conversant in:

- Constitutional AI: Harmlessness from AI Feedback (arXiv 2212.08073) — the original CAI paper, defines self-supervised harmlessness training
- Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training (arXiv 2401.05566) — backdoors that survive RLHF and adversarial training; required reading for any "trusted model" conversation
- Next-Generation Constitutional Classifiers — runtime jailbreak prevention, withstood 3,000+ hours of red-teaming with no universal jailbreak
- Probing for Sleeper Agents (2025) — interpretability technique to detect deceptive behavior pre-deployment
- Anthropic Fellows Program writeups (2025-2026) — agentic misalignment, subliminal learning, ASL-3 rapid response, open-source circuits

**Why interviewers care:** When the role touches Anthropic models or agentic systems, knowing one or two of these papers by name signals that you read primary sources, not just vendor blog posts. Sleeper Agents and Constitutional Classifiers are the two most-cited.

---

## How to use this file

1. Memorize the 10 IDs and one-line definitions for OWASP LLM Top 10 and MCP Top 10. These are nearly guaranteed prompts.
2. Be able to name 5 ATLAS techniques with IDs and 5 ATT&CK Enterprise techniques relevant to your target role.
3. For every framework, know one paragraph of "what it is and where it fits" so you can answer "have you used X" without freezing.
4. Re-verify versions before any interview by hitting the URLs above. AI security tooling changes monthly.

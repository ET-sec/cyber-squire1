# 01 — Company Intel

## Insight Global (the staffing firm, not the end client)

### Basics
- Atlanta-HQ professional staffing and services firm
- ~$3.4B revenue (publicly disclosed range), private, family-leadership style
- ~64 offices US + Canada
- IT, healthcare, finance, gov verticals
- Phoenix is a meaningful IT desk

### Interview pattern (Glassdoor)
- 2.44 / 5 difficulty (low)
- 54.6% positive interview experience
- ~14 day average time to hire across all roles
- Two recurring negative themes from candidates:
  1. Recruiters can be pushy on timeline
  2. Pay rate floor sometimes presented as "best they can do" until candidate counters
- Source: [Insight Global Glassdoor Interviews](https://www.glassdoor.com/Interview/Insight-Global-Interview-Questions-E152783.htm)

### Contract pay reality
- Glassdoor estimated avg contractor: ~$60K/yr or ~$29/hr (skewed by junior/admin)
- IT security contractor rates trend much higher than the averaged number
- Comparable AI Sec Eng remote 2026 baseline: $143K-$158K perm, $80-$120/hr W2 contract
- Sources: [Glassdoor Contract Hourly Pay](https://www.glassdoor.com/Hourly-Pay/Insight-Global-Contract-Hourly-Pay-E152783_D_KO15,23.htm) | [ZipRecruiter AI Sec Eng Remote](https://www.ziprecruiter.com/Jobs/Ai-Security-Engineer-Remote)

### Implication for Emmanuel
- Stand firm on rate. Insight Global expects negotiation.
- Ask Savannah for the **bill rate** (what client pays IG) if she resists the pay range. The IG margin is typically 25-35%.
- Conversion to perm rate at IG: anecdotal, no firm data. Treat the 1-yr contract as a 1-yr contract. Possible extension is not a guarantee.

---

## Savannah Daoust (recruiter)

### Profile
- Professional Recruiter at Insight Global since March 2022 (~4 years)
- Based Phoenix AZ, Northern Arizona U alum
- Selected to the Insight Global Women's Leadership Council 2026 (Jan 2026 — promotion track)
- Endorsements describe her as detail-oriented and creative on sourcing
- No negative review footprint
- Source: [Savannah Daoust LinkedIn](https://www.linkedin.com/in/savannah-daoust/)

### Read for the call
- Generalist IT recruiter desk, not pure cyber. She likely cannot answer deep technical AI sec follow-ups.
- Strong relationship-builder profile. Treat as a partner, not a gatekeeper.
- Phoenix MST timezone — coordinate Monday window in MST (3 hr behind ET).
- Email: savannah.daoust@insightglobal.com (verified by ContactOut snippet, treat as likely-correct until she confirms)

### What she will care about
1. Citizenship answer (gate)
2. Resume in the requested format
3. Whether you have **MS Security Copilot + Defender for Cloud hands-on** — the gap she will probe hardest
4. Whether you can start in 2-3 weeks
5. Pay expectation that lets her hit her bill rate margin

---

## End client (REDACTED — strategy to identify)

### What we know
- Industry not stated
- Size not stated
- JD language is generic enough to cover Fortune 500, federal, or large mid-market
- 1-year term position is consistent with: regulated org running an AI governance build, OR a temporary stand-up team for a specific compliance deadline (EU AI Act high-risk obligations land **2026-08-02** per [EU AI Act Implementation Timeline](https://artificialintelligenceact.eu/implementation-timeline/))
- Microsoft-stack heavy (Security Copilot + Defender for Cloud) → likely Azure-anchored client
- "Internal chatbots and third-party AI services" → enterprise with mature shadow AI surface

### Likely client profiles (hypothesis, not verified)
1. **Large regulated enterprise (financial, healthcare, energy)** building toward ISO 42001 certification or EU AI Act compliance
2. **Federal contractor** standing up an AI red-team capability under FedRAMP / NIST 800-53 Rev 5
3. **Microsoft partner / Microsoft itself** — Security Copilot expertise is in-house at Redmond and at the largest MSPs (NTT Data, Avanade, Insight Enterprises)
4. **AI-native scaleup** mature enough to need governance hires but not yet perm-budget approved

### Probing strategy on the call (in order)
1. "Can you share what industry the end client is in?"
2. "Are they Microsoft-shop end-to-end, or is the Copilot piece part of a multi-cloud setup?"
3. "Is this a brand-new role or a backfill? That tells me a lot about how the program is set up."
4. "What does their current AI governance program look like — are they NIST AI RMF aligned, or are they building toward ISO 42001 certification?"
5. If she resists naming: "I understand the redaction. Would you be willing to share once we're past the screen and you're comfortable submitting me?"

### Why this matters
- Cannot tailor resume without industry signal
- Cannot price the rate without size and budget signal
- Cannot prep the HM round without knowing security org size + maturity

---

## The Microsoft stack the JD names

### Microsoft Security Copilot
- Generative-AI security operations product, built on Azure OpenAI + Microsoft threat intelligence
- Integrates with Defender XDR, Sentinel, Intune, Purview, Entra
- Achieved ISO/IEC 42001:2023 certification April 2026
- Use cases: incident summarization, KQL generation from natural language, malware reverse engineering, posture management
- Source: [MS Security Copilot product page](https://www.microsoft.com/en-us/security/business/ai-machine-learning/microsoft-security-copilot)

### Microsoft Defender for Cloud (relevant 2026 features)
- **AI Security Posture Management (AI-SPM)** — GA. Discovers AI assets across Azure OpenAI, Azure ML, AWS Bedrock. Scores misconfigurations (overly permissive endpoints, missing content filters). [Source](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture)
- **AI threat protection** — detects prompt injection, model theft, jailbreak attempts. Feeds Sentinel. [Source](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-threat-protection)
- **Compliance assessments** — EU AI Act, NIST AI RMF, ISO 42001, ISO 23894 in Purview Compliance Manager (GA). [Source](https://www.microsoft.com/en-us/security/blog/2026/04/22/ai-powered-defense-for-an-ai-accelerated-threat-landscape/)

### Why this is a real gap
- Emmanuel runs the same conceptual control plane on a different stack:
  - **Posture management:** Falco eBPF detection at runtime (200 → 12 alerts), not Defender for Cloud CSPM
  - **Threat protection:** Falco + Sidekick + Datadog routing, not Defender XDR
  - **AI guardrails:** Anthropic API direct + n8n SOAR + 37 GRC docs, not Security Copilot
  - **Compliance evidence:** OPA + manual SSP + 31 GRC docs, not Purview Compliance Manager
- The skills transfer. The vendor surface does not.
- Honest framing: "I have run the conceptual playbook for AI posture and AI threat protection in production. I have not run the Microsoft tooling. Ramp time on the UI is days; ramp time on the concepts is zero."

---

## AI governance frameworks the JD names

### NIST AI RMF 1.1
- Voluntary US framework, 4 functions (Govern, Map, Measure, Manage)
- Maps cleanly to ISO 42001 (Govern → Clauses 5-6, Map → impact assessment, etc.)
- Source: [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

### ISO/IEC 42001:2023
- AI Management System standard (AIMS), certifiable
- ~40% of EU vendor RFPs and ~25% of NA vendor RFPs ask about it by mid-2026
- Microsoft, Google, AWS, Anthropic all certified or in motion
- Source: [Global AI Governance Comparison 2026](https://gaicc.org/blog/ai-governance-comparison-eu-ai-act-nist-iso-42001/)

### EU AI Act
- Phased: prohibited systems Feb 2025, GPAI obligations Aug 2025, **high-risk Annex III obligations Aug 2026**, regulated products Aug 2027
- "High-risk": biometric ID, critical infrastructure, employment, essential services, law enforcement
- Source: [EU AI Act Implementation Timeline](https://artificialintelligenceact.eu/implementation-timeline/)

### Why this matters for the call
The Aug 2026 high-risk deadline is **3 months out** when this contract starts. That timing is not coincidence. The end client is plausibly racing a compliance window. Validate this hypothesis with Savannah by asking about timeline urgency.

---

## Adversarial ML + MLOps security (JD threat-intel line)

### What the JD is actually asking for
- Awareness of model attacks: poisoning, inversion, extraction, evasion, backdoors, prompt injection
- Awareness of MLOps supply chain: model registry RBAC, signing, CI/CD guardrails, training data lineage
- Source: [Towards Secure MLOps survey arxiv](https://arxiv.org/pdf/2506.02032) | [CSA Hidden ML Pipeline Threats](https://cloudsecurityalliance.org/blog/2025/09/11/the-hidden-security-threats-lurking-in-your-machine-learning-pipeline)

### What Emmanuel can claim honestly
- **Read level:** STRIDE + MITRE ATLAS for AI workloads (executed on the SQUIRE_THREAT_MODEL.md doc)
- **Workshop level:** Prompt injection testing against Anthropic API endpoints in the COREDIRECTIVE_ENGINE
- **Production level:** Falco + Sidekick anomaly detection on the Ollama + Whisper inference containers
- **Gap:** Have not implemented model signing or model registry RBAC in production. Have read the patterns. Have not shipped them.

---

## Sources cited

1. [Microsoft Security Copilot product page](https://www.microsoft.com/en-us/security/business/ai-machine-learning/microsoft-security-copilot)
2. [Defender for Cloud AI-SPM overview](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-security-posture)
3. [Defender for Cloud AI threat protection](https://learn.microsoft.com/en-us/azure/defender-for-cloud/ai-threat-protection)
4. [Microsoft Security Blog April 2026](https://www.microsoft.com/en-us/security/blog/2026/04/22/ai-powered-defense-for-an-ai-accelerated-threat-landscape/)
5. [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
6. [EU AI Act Implementation Timeline](https://artificialintelligenceact.eu/implementation-timeline/)
7. [Global AI Governance Comparison 2026](https://gaicc.org/blog/ai-governance-comparison-eu-ai-act-nist-iso-42001/)
8. [Insight Global Glassdoor Interviews](https://www.glassdoor.com/Interview/Insight-Global-Interview-Questions-E152783.htm)
9. [Insight Global Contract Hourly Pay](https://www.glassdoor.com/Hourly-Pay/Insight-Global-Contract-Hourly-Pay-E152783_D_KO15,23.htm)
10. [Savannah Daoust LinkedIn](https://www.linkedin.com/in/savannah-daoust/)
11. [Towards Secure MLOps arxiv](https://arxiv.org/pdf/2506.02032)
12. [CSA Hidden ML Pipeline Threats](https://cloudsecurityalliance.org/blog/2025/09/11/the-hidden-security-threats-lurking-in-your-machine-learning-pipeline)
13. [AI Security Engineer remote pay ZipRecruiter](https://www.ziprecruiter.com/Jobs/Ai-Security-Engineer-Remote)

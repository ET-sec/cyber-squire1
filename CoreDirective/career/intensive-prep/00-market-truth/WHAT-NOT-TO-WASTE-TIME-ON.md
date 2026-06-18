# What Not to Waste Time On — AI Security 80/20

The candidate has limited time and a hard cognitive budget under 4-hour sleep nights. The list below is what hype says you must learn, what AI Security Engineer interviews actually test, and where to cut.

Calibrated against verified JDs in the candidate's pipeline (Dropzone AI, OneDigital FTS, Resilience, Insight Global, WBD/Milestone, QGenda, Brilliant Cloudflare, Amex Experis) and what hiring managers ask in technical screens for $200K+ AI Security roles in 2026.

---

## The 6 biggest time wasters

### 1. Deep-diving every model architecture (Transformer internals, attention head math, MoE routing)

What hype says: "You need to understand attention mechanisms and KV-cache to do AI security."

What interviews actually ask: "Explain how prompt injection bypasses a system prompt." "How would you detect data exfil through tool calls?" "What controls reduce blast radius of an over-permissioned agent?"

Why to cut: Architecture-level expertise is for ML researchers and inference engineers. AI Security Engineers operate one layer above, at the API, agent, and pipeline boundary. Knowing what attention is conceptually (3 sentences) is enough. Reading "Attention Is All You Need" and 4 follow-up papers is a 30-hour detour with near-zero interview ROI.

What to do instead: Spend that 30 hours building a vulnerable LangGraph agent and Garaking it. Result is concrete and demonstrable.

---

### 2. Becoming expert at every cloud provider

What hype says: "Modern engineers are multi-cloud."

What interviews actually ask: AWS, AWS, AWS. Sometimes Azure if the role is Microsoft-stack. GCP rarely.

Why to cut: AWS is the dominant cloud in 2026 enterprise security. Most AI Security JDs default to AWS unless explicitly Azure (Microsoft Security Copilot, Azure OpenAI). Trying to be CCSP-deep on AWS, Azure, AND GCP in parallel turns you into a generalist who is shallow on all three.

What to do instead: Be deep on AWS. Be conversational on Azure (services, IAM model, key vault, Sentinel, Defender). Treat GCP as "I can read the docs when needed".

---

### 3. Memorizing CVE numbers

What hype says: "Real practitioners know CVEs by number."

What interviews actually ask: "Tell me about a recent supply chain incident and how you would defend against it." Not "what was the CVE number for log4shell."

Why to cut: CVE numbers are a database key, not knowledge. Anyone can lookup. Knowing the *class* of vulnerability and the *control families* that mitigate it is the senior signal.

What to do instead: Remember 5 incidents in narrative form (log4shell, SolarWinds, MOVEit, xz-utils, the 2026 Trivy supply chain compromise) and the lessons. Store CVE numbers in Anki only if you actually want them. Most senior engineers do not.

---

### 4. Every framework in detail

What hype says: "You should know NIST CSF, NIST AI RMF, NIST 800-53, NIST 800-171, NIST 800-218, ISO 27001, ISO 27017, ISO 27018, ISO 27090, ISO 42001, EU AI Act, HIPAA, PCI, FedRAMP, SOC 2, CCM, CMMC..."

What interviews actually ask: "Walk me through how you would scope an AI security program." Or "What framework would you map your controls to?"

Why to cut: 80% of interviews are answered by 3 frameworks: NIST AI RMF, OWASP LLM Top 10, ISO 42001. Add OWASP MCP Top 10 and ATLAS for AI-specific roles. Going deep on the rest before the core 5 is wasted compression.

What to do instead: Master the core 5. Know the others exist and roughly what they cover (one paragraph each). Refresh the ones a specific role requires *before that interview*, not in advance.

---

### 5. Becoming a Kubernetes wizard

What hype says: "Container security is critical, you need CKS-level fluency."

What interviews actually ask: It depends entirely on the role. Roles with K8s in the JD ask deeply. Roles without K8s rarely touch it.

Why to cut: K8s mastery is 100+ hours of investment. It is highly valuable for the right role and dead weight for the wrong one. Pre-investing without a K8s-heavy target is bad ROI.

What to do instead: Know the K8s security model conceptually (RBAC, NetworkPolicy, Pod Security Standards, secrets management, image signing). If a target role is K8s-heavy, then commit to CKA + CKS. Otherwise, skip.

---

### 6. Tool fluency without substance behind it

What hype says: "Get certified in every vendor: Snyk, Wiz, Lacework, CrowdStrike, Splunk..."

What interviews actually ask: "Tell me about the last time you investigated a real alert in [tool]." Or "How did you tune detection rules?"

Why to cut: Vendor tool training without a story to tell is interview kryptonite. The interviewer wants the narrative arc (alert -> triage -> investigation -> finding -> remediation -> improvement), not vendor certification badges.

What to do instead: Pick ONE tool per category (one SIEM, one SAST, one DAST, one cloud security, one EDR) and have a story. Real alert, real investigation, real fix. The story beats the badge every time.

---

## Categories where hype and interview reality diverge

### "AI/ML expertise required"
JDs frequently inflate AI/ML expertise as required when the actual day-to-day is web app security with AI thrown in. Read JDs adversarially. If the bullets are "implement Snyk, deploy CrowdStrike, write Sigma rules, and also some AI", treat it as a security role with AI seasoning. Don't over-invest in PhD-level ML for a role that needs OWASP LLM Top 10 fluency.

### "Production agent experience"
Some JDs ask for years of production agent experience that does not exist outside FAANG and a few startups. If you've built and shipped a working LangGraph agent, deployed it, monitored it, and broken it on purpose, you can credibly claim the experience even if it was on your own infrastructure. Frame it as "production-grade" not "production at $bigCorp".

### "Hands-on red teaming required"
Garak + Promptfoo + a documented attack chain against your own LLM agent counts as red teaming for entry-to-mid roles. You do not need a SANS GIAC purple team cert for this signal.

---

## What to over-invest in

Things worth more time than the average curriculum allots:

1. **Writing.** Hiring managers read your resume, your LinkedIn, your blog posts, your PR descriptions. Strong writing signals strong thinking. Invest in writing publicly about what you build.
2. **Building one working artifact end-to-end.** A vulnerable LangGraph agent + Garak probes + a writeup beats 5 half-finished GitHub repos. One thing, fully shipped, that an interviewer can look at.
3. **Story preparation for behavioral interviews.** STAR stories about real events: an alert you investigated, a control you improved, a vulnerability you found, a system you designed. Senior interviews are 60% behavioral. Most candidates under-prepare here.
4. **Asking strong questions in interviews.** The questions you ask the panel telegraph seniority. Spend an hour preparing role-specific questions per interview round.

---

## The cut list, summarized

| Cut | Keep |
|-----|------|
| Memorize Transformer math | Build LLM agents and break them |
| Multi-cloud expert (3 clouds) | AWS deep, Azure conversational |
| CVE numbers | Incident narratives |
| Every NIST/ISO/regulation | Core 5 (NIST AI RMF, OWASP LLM, ISO 42001, OWASP MCP, ATLAS) |
| K8s wizardry without target | K8s concepts; CKS only if role demands |
| Vendor cert collection | One tool per category with real stories |
| 5 half-finished side projects | One fully shipped artifact |
| Reading about it | Building it and writing about it |

The candidate's biggest time-amplifier in May 2026: ship one public artifact (vulnerable LangGraph agent + Garak red-team writeup + LinkedIn post) and stop adding curriculum until that ships.

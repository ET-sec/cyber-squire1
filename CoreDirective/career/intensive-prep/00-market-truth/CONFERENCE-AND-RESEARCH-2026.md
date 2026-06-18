# Conference and Research Map: AI Security, January 2025 to May 2026

State of AI security research and what is real versus hype as of May 2026. Every claim sourced. Where a claim could not be verified, marked [UNVERIFIED].

## Active research venues

### USENIX Security 2025 (the big four for AI security papers)

Source: https://www.usenix.org/conference/usenixsecurity25

Notable AI security papers at USENIX Security 2025 with publicly available PDFs:

1. Defending Against Prompt Injection with Structured Queries (Sizhe Chen et al.). Reduced attack success rate of TAP from 97% to 9% on Llama, GCG from 97% to 58%. Uses a structured separator between prompt and data. https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf

2. SelfDefend: LLMs Can Defend Themselves Against Jailbreaking. GPT-3.5 attack success ranges 0.256 to 0.980 (avg 0.655). GPT-4 0.047 to 0.330. Mechanism: harmful-portion identification by a defender LLM. https://www.usenix.org/system/files/usenixsecurity25-wang-xunguang.pdf

3. TwinBreak: Jailbreaking LLM Security Alignments via Parameter Pruning. Activation-difference analysis identifies and prunes safety parameters. White-box attack. https://www.usenix.org/system/files/usenixsecurity25-krauss.pdf

4. PoisonedRAG: Knowledge Corruption Attacks on RAG. <30 seconds to optimize each malicious text in white-box settings. High attack success across multiple datasets and LLMs. https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf

USENIX Security 2024 carryover that 2026 interviewers still cite:
- Formalizing and Benchmarking Prompt Injection Attacks and Defenses (Liu et al.). https://www.usenix.org/conference/usenixsecurity24/presentation/liu-yupei

### Black Hat USA 2025

Source: https://i.blackhat.com/BH-USA-25/Presentations/US-25-Lynch-From-Prompts-to-Pwns.pdf, https://www.promptfoo.dev/events/blackhat-2025/

Headline talks:
- "From Prompts to Pwns: Exploiting and Securing AI Agents" (Becca Lynch, Rich Harang, NVIDIA). Headline take: assume prompt injection. Architectural recommendation for agentic apps.
- SPIKEE (Reversec). Modular toolkit for testing LLM apps for prompt injection.
- A.I.G. Agent-based scanner for MCP server source code or remote MCP URLs across 9 risk categories (tool poisoning, RCE, indirect prompt injection).

Vendor demo focus: Promptfoo, Lakera Guard, NeMo Guardrails were all on the show floor demonstrating real workflows.

### Black Hat Europe 2025

Source: https://www.security.com/expert-perspectives/inside-defenders-ai-advantage, https://corelight.com/blog/black-hat-europe-2025-agentic-ai

Themes: prompt injection demos, jailbreaking, data exfiltration. Defender-focused agentic-AI threat-hunting demos became prominent.

### DEF CON 32 AI Village (August 2024)

Source: https://aivillage.org/events/defcon32/, https://tldrsec.com/p/2024-defcon-ai-talks

Highlights still cited in 2026 interviews:

- FuzzLLM (UC Irvine). Automated jailbreak fuzzing via templates plus constraint isolation plus combo attacks.
- Meta Llama 3 red team writeup. Multi-turn adversarial AI agents. Automated scaling. Safety benchmarks across high-risk areas.
- CyberSecEval Prompt Injection (Meta). PromptGuard model for direct jailbreak and indirect injection detection.
- Cognitive Attack Taxonomy (Psyber Labs). 350+ cognitive vulns and TTPs.
- DEF CON Generative AI Hacking Challenge. Public red team event with the goal of breaking ChatGPT and similar in 50-minute heats. https://cyberscoop.com/def-con-ai-hacking-red-team/

### DEF CON 33 (August 2025) AI Village

Source: https://aivillage.org

[UNVERIFIED specific 2025 talk list. AI Village ran. Themes per public summaries: agentic exploitation, multi-modal jailbreaks, adversarial fine-tuning attacks. Continuation of GenAI bug bounty challenge.]

### Emerging in 2026: ATLAS Rapid Response Reports

Source: https://ctid.mitre.org/blog/2026/05/06/secure-ai-v2-release

Center for Threat-Informed Defense expanded MITRE ATLAS in May 2026 with rapid-response and emulation capabilities. The first ATLAS Rapid Response Report establishes a faster model for analyzing emerging AI security incidents.

## Frameworks the candidate must know cold

### OWASP LLM Top 10 (2025 baseline)

Source: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/, https://owasp.org/www-project-top-10-for-large-language-model-applications/

LLM01 Prompt Injection. LLM02 Sensitive Information Disclosure. LLM03 Supply Chain. LLM04 Data and Model Poisoning. LLM05 Improper Output Handling. LLM06 Excessive Agency. LLM07 System Prompt Leakage. LLM08 Vector and Embedding Weaknesses. LLM09 Misinformation. LLM10 Unbounded Consumption.

PDF: https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf

### OWASP Top 10 for Agentic Applications 2026

Source: https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications, https://www.bleepingcomputer.com/news/security/the-real-world-attacks-behind-owasp-agentic-ai-top-10/

First framework dedicated to autonomous agents. Focus on autonomy: agents that plan, decide, and act across systems. New risk categories beyond LLM Top 10 cover delegated authority, multi-agent collusion, persistent state and memory exploitation, tool ecosystem trust boundaries.

### MITRE ATLAS

Source: https://atlas.mitre.org/

Feb 2026 v5.4.0: 16 tactics, 84 techniques, 56 sub-techniques, 32 mitigations, 42 case studies. Nov 2025 v5.1.0 added agentic AI techniques. 2026 strategic shift: from model-centric to execution-layer focus. https://zenity.io/blog/current-events/mitre-atlas-ai-security

### NIST AI RMF Generative AI Profile (NIST AI 600-1)

Source: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf, https://www.nist.gov/itl/ai-risk-management-framework

Released July 26, 2024. 13 risks. 400+ actions. Mapped to GOVERN, MAP, MEASURE, MANAGE.

### OWASP AI Exchange

Source: https://owaspai.org/, https://owasp.org/www-project-ai-security-and-privacy-guide/

300+ pages. 70+ contributors. Feeds into ISO/IEC 27090 (70 pages contributed), 27091, EU AI Act technical guidance (70 pages contributed), OpenCRE.

The single best free reference for engineers mapping controls to threats coherently.

### ISO/IEC 42001:2023

Source: https://www.iso.org/standard/42001

AI Management System standard. By 2026 in first real growth wave. Plan-Do-Check-Act methodology. Buyer-side adoption pressure: Fortune 500 increasingly require certification or roadmap.

### EU AI Act

Source: https://artificialintelligenceact.eu/implementation-timeline/

Enforcement timeline:
- February 2, 2025: Prohibited practices in force.
- August 2, 2025: AI Office operational. GPAI obligations. Penalty regime in force.
- August 2, 2026: High-risk Annex III enforceable. GPAI enforcement powers.
- August 2, 2027: Full compliance for high-risk including medical devices.

Penalty bands: EUR 35M or 7% turnover (prohibited), EUR 15M or 3% (other), EUR 7.5M or 1% (incorrect reporting).

## Significant AI security incidents and CVEs (2024 to May 2026)

### MCP and agent infrastructure

- CVE-2025-6515. Prompt hijacking via session ID memory reuse. https://jfrog.com/blog/mcp-prompt-hijacking-vulnerability/
- CVE-2025-6514. mcp-remote OS command injection (437,000+ npm downloads). https://github.com/advisories/GHSA-6xpm-ggf7-wc3p
- CVE-2025-53107. @cyanheads/git-mcp-server command injection. https://github.com/advisories/GHSA-3q26-f695-pp76
- CVE-2025-53818. GitHub Kanban MCP Server command injection. https://github.com/advisories/GHSA-6jx8-rcjx-vmwf
- CVE-2025-54136. Cursor MCPoison.
- Anthropic Git MCP server prompt injection chain. https://www.infosecurity-magazine.com/news/prompt-injection-bugs-anthropic/
- MCP STDIO architectural RCE (150M+ downloads exposed). https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/

### AI IDE and coding assistants

- CVE-2025-53773. GitHub Copilot YOLO mode RCE via prompt injection. CVSS 7.8 HIGH. Reported by Johann Rehberger. https://gbhackers.com/ai-developer-tools/
- CVE-2025-64660. Additional GitHub Copilot vuln in same patch wave.
- CVE-2025-49150, 54130, 54135, 54136, 61590. Cursor.
- IDEsaster attack chain: 24 CVEs assigned. 100% of tested AI IDEs vulnerable. https://www.helpnetsecurity.com/2026/05/05/ai-agent-security-skills-blind-spots/
- Hidden Unicode rules-file backdoors (Mar 2025). .cursorrules and copilot-instructions.md. GitHub responded with Unicode-warning UI. https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents

### Agentic AI in active operations

Source: https://github.com/webpro255/awesome-ai-agent-attacks

- GTG-1002 (China APT) Sept to Nov 2025. Claude Code executed 80 to 90% of tactical operations against ~30 orgs.
- CyberStrikeAI FortiGate campaign (Russian-speaking actor) Jan to Feb 2026. 600+ FortiGate devices, 55 countries, no CVE exploited.
- HexagonalRodent (Famous Chollima subgroup) Q1 2026. Cursor, ChatGPT, Anima used. ~$12M crypto theft. 26,584 wallets exfiltrated from 2,726 dev systems.

### AI-generated code surge

- 35 new CVEs in March 2026 directly attributable to AI-generated code (up from 6 in January, 15 in February). https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-generated-code-vulnerability-surge-2026/
- Veracode: 45% of AI-generated code samples introduce OWASP Top 10 vulns. https://www.infosecurity-magazine.com/news/ai-generated-code-vulnerabilities/
- GitGuardian: 28.65M new hardcoded secrets in public GitHub commits in 2025 (34% YoY increase). AI-assisted commits 3.2% secret-leak rate vs 1.5% baseline.

### Voice cloning and deepfake operations

- 1,600%+ surge in deepfake-enabled vishing Q1 2025 vs Q4 2024 in the US. https://deepstrike.io/blog/deepfake-statistics-2025
- Voice deepfake incidents up 680% YoY in 2025.
- 100,000+ US voice deepfake attacks in 2025.
- $25.6M wire fraud at Hong Kong-based finance team (Feb 2024) via deepfake video conf. Still the canonical case.
- Marco Rubio impersonation (July 2025) via Signal voice messages to foreign ministers, sitting senator, governor. https://cybelangel.com/blog/deepfake-ceo-fraud-how-voice-cloning-targets-us-executives/
- Detection accuracy collapse: AI deepfake detectors lose 45 to 50% accuracy in real-world conditions. Human accuracy on high-quality drops to 24.5%.

### Empirical scale of agent ecosystem vulnerabilities

- Among 2,614 MCP implementations: 82% file-op path-traversal vulnerable, two-thirds code-injection risk, >1/3 command-injection risk. https://gentic.news/article/mcp-security-crisis-43-of-servers
- 25,187 Skills from 3,217 GitHub repos studied. Widespread vulnerability across Skills ecosystem. https://arxiv.org/html/2601.10338v1

## What is real versus hype

### Real

- Prompt injection. Real, exploitable, hard to fully mitigate. Ranks as the top OWASP LLM risk for a reason.
- MCP server attack surface. Real. Multiple CVEs in the past 12 months. Architectural issues that won't be patched away.
- RAG poisoning. Real. PoisonedRAG paper demonstrates feasibility in <30 seconds per malicious entry.
- Agentic AI as offensive multiplier. Real. GTG-1002 and CyberStrikeAI demonstrate operational use by APTs.
- Voice cloning fraud. Real and growing. $25.6M case is a real loss event.
- AI-generated code vulnerabilities. Real. 35 March 2026 CVEs attributable to AI-generated code.
- Multimodal jailbreaks. Real. Demonstrated at DEF CON 32 and Black Hat 2025. Most text-only scanners miss.
- ISO 42001 buyer-side pressure. Real. Fortune 500 is asking.
- EU AI Act enforcement. Real. August 2026 high-risk deadline is binding.

### Mostly real, sometimes overhyped

- Constitutional AI vs RLHF as a security distinction. The labs use both for different reasons. The security implications are nuanced and not as differentiated as marketing implies.
- "AI BOM is the new SBOM." Conceptually correct, but adoption is real-but-slow. OWASP AIBOM v0.1 milestone was Nov 2025. CycloneDX ML-BOM exists. Buyer-side pressure is patchy.
- "AI replaces analysts." Hype. Augmentation pattern is real, replacement claims are vendor marketing. Robinhood's role is "AI Vuln Mgmt" not "no analyst needed."
- LLM red team certifications. Real but young. HTB AI Red Teamer path, Learn Prompting AI Red Teaming Pro Cert, Practical DevSecOps AI Sec Pro. Treat as nice-to-have, not validated career signal.

### Hype to discount

- "Quantum AI threats." Cited in vendor marketing. Real research direction. Not a 2026 interview gate.
- "AGI safety as a security topic." Real research, but if a security engineer interview goes there, it is usually because the candidate brought it up. Stick to deployed-system risks.
- "Self-healing AI security." Vendor pitch. Demonstrated at booths. Operational reality is much messier.
- "Zero-trust for AI" as a slogan. The underlying architectures (network egress, identity for non-human, API allowlists) are real and sound. The slogan layer is filler.

## Buzzword decoder for the candidate

| Buzzword | What it actually is | Interview-worthy? |
|---|---|---|
| Agentic AI | Multi-step autonomous LLM workflow | Yes. Know MCP, agent frameworks, attack patterns. |
| Constitutional AI | Anthropic alignment approach using a "constitution" of principles | Soft. Know it exists. |
| RLHF | Reinforcement learning from human feedback | Yes. Foundational. |
| RLAIF | RL from AI feedback | Soft. Know it exists. |
| Guardrails | Runtime classifiers and policy layers around LLM I/O | Yes. Know NeMo, Lakera, Guardrails AI. |
| LLM firewall | Marketing term for guardrails plus filter | Decode it. Don't use it as a primary term. |
| AI Red Team | Adversarial testing of AI systems | Yes. Know PyRIT, Garak, Promptfoo. |
| MCP | Model Context Protocol, Anthropic Nov 2024 | Yes. Required. |
| AI BOM | Bill of materials for AI systems | Soft. Know CycloneDX ML-BOM, OWASP AIBOM. |
| AI Governance | Policy, risk, compliance for AI | Yes. Know NIST AI RMF, ISO 42001, EU AI Act. |
| Shadow AI | Unsanctioned AI use within enterprise | Yes. Know discovery patterns. |
| Model Theft | Extraction or replication of weights | Yes. Know membership inference and model inversion. |
| Prompt Engineering | Crafting prompts to elicit desired behavior | Soft. Treat as table-stakes. |
| GenAI BOM | Same as AI BOM with marketing tweak | Decode it. |
| Agentic Red Team | Red teaming of autonomous agents specifically | Yes. Top-of-market signal. |
| AI SOC | AI-augmented Security Operations Center | Yes. Know Dropzone AI archetype. |
| AISPM | AI Security Posture Management | Soft. Know Wiz, Lakera, Lasso vendor space. |

## Read-out for the candidate

Spending interview prep time on the framework canon (OWASP LLM Top 10, MITRE ATLAS, NIST AI 600-1, EU AI Act timeline) returns more than spending equal time on alignment-theory debates. Spending time on real CVE numbers (the MCP and Cursor CVEs above) and on running Garak or Promptfoo at least once against a real local target returns more than spending time on vendor demo summaries.

The single biggest gap candidates miss: knowing the difference between LLM Top 10 (a 2025 framework) and the OWASP Top 10 for Agentic Applications (a 2026 framework). The latter exists. Most candidates have not read it. Bringing it up cleanly in the threat-modeling round is differentiation.

## All sources

- https://www.usenix.org/conference/usenixsecurity25
- https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf
- https://www.usenix.org/system/files/usenixsecurity25-wang-xunguang.pdf
- https://www.usenix.org/system/files/usenixsecurity25-krauss.pdf
- https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf
- https://www.usenix.org/conference/usenixsecurity24/presentation/liu-yupei
- https://i.blackhat.com/BH-USA-25/Presentations/US-25-Lynch-From-Prompts-to-Pwns.pdf
- https://www.promptfoo.dev/events/blackhat-2025/
- https://www.security.com/expert-perspectives/inside-defenders-ai-advantage
- https://corelight.com/blog/black-hat-europe-2025-agentic-ai
- https://aivillage.org/events/defcon32/
- https://tldrsec.com/p/2024-defcon-ai-talks
- https://cyberscoop.com/def-con-ai-hacking-red-team/
- https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- https://owasp.org/www-project-top-10-for-large-language-model-applications/
- https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf
- https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications
- https://www.bleepingcomputer.com/news/security/the-real-world-attacks-behind-owasp-agentic-ai-top-10/
- https://atlas.mitre.org/
- https://zenity.io/blog/current-events/mitre-atlas-ai-security
- https://ctid.mitre.org/blog/2026/05/06/secure-ai-v2-release
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- https://www.nist.gov/itl/ai-risk-management-framework
- https://owaspai.org/
- https://owasp.org/www-project-ai-security-and-privacy-guide/
- https://www.iso.org/standard/42001
- https://artificialintelligenceact.eu/implementation-timeline/
- https://jfrog.com/blog/mcp-prompt-hijacking-vulnerability/
- https://github.com/advisories/GHSA-6xpm-ggf7-wc3p
- https://github.com/advisories/GHSA-3q26-f695-pp76
- https://github.com/advisories/GHSA-6jx8-rcjx-vmwf
- https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents
- https://www.infosecurity-magazine.com/news/prompt-injection-bugs-anthropic/
- https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/
- https://gentic.news/article/mcp-security-crisis-43-of-servers
- https://gbhackers.com/ai-developer-tools/
- https://www.helpnetsecurity.com/2026/05/05/ai-agent-security-skills-blind-spots/
- https://github.com/webpro255/awesome-ai-agent-attacks
- https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-generated-code-vulnerability-surge-2026/
- https://www.infosecurity-magazine.com/news/ai-generated-code-vulnerabilities/
- https://deepstrike.io/blog/deepfake-statistics-2025
- https://cybelangel.com/blog/deepfake-ceo-fraud-how-voice-cloning-targets-us-executives/
- https://arxiv.org/html/2601.10338v1
- https://arxiv.org/html/2602.06547v1

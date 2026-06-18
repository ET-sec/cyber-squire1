# Emerging Topics, AI Security 2026

This is the live-fire list of subjects that interviewers in 2026 expect the candidate to be able to discuss with technical specificity. Topics are sourced from CVE disclosures, primary research, vendor disclosures, and conference programs from January 2025 through May 2026. Every claim has a citation. Where a claim could not be verified, it is marked [UNVERIFIED].

## 1. Agentic security and the MCP attack surface

The Model Context Protocol shipped from Anthropic in November 2024 (https://authzed.com/blog/timeline-mcp-breaches). By May 2026 it is the most-attacked emerging surface in the AI stack. Interviewers will expect candidates to know specific CVEs and the structural reasons MCP is hard to secure.

Real CVEs and disclosed issues:

- CVE-2025-6515. Prompt hijacking via improper session ID generation. Exploits memory reuse patterns in the MCP session layer. https://jfrog.com/blog/mcp-prompt-hijacking-vulnerability/
- CVE-2025-6514. OS command injection in mcp-remote. A malicious MCP server can ship a booby-trapped authorization_endpoint to achieve RCE. 437,000+ npm downloads exposed at disclosure. https://github.com/advisories/GHSA-6xpm-ggf7-wc3p
- CVE-2025-53107. Command injection in @cyanheads/git-mcp-server across multiple tools. https://github.com/advisories/GHSA-3q26-f695-pp76
- CVE-2025-53818. GitHub Kanban MCP Server command injection. https://github.com/advisories/GHSA-6jx8-rcjx-vmwf
- CVE-2025-54136 (Cursor MCPoison). Approve-once MCP config that can be silently mutated to backdoor execution. Reported by The Hacker News and Pillar Security: https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents
- Anthropic Git MCP server. Three prompt-injection bugs allowed cross-tool exploitation chained with a filesystem MCP server, enabling arbitrary file delete or load into LLM context. https://www.infosecurity-magazine.com/news/prompt-injection-bugs-anthropic/
- Architectural RCE in MCP STDIO transport. OX Security found 150M+ downloads exposed through reference SDKs in Python, TypeScript, Java, Rust. Anthropic confirmed by-design behavior and declined to patch. https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/

Empirical scale: Among 2,614 MCP implementations surveyed, 82% use file operations vulnerable to path traversal, two-thirds have code injection risk, and over a third are vulnerable to command injection (https://gentic.news/article/mcp-security-crisis-43-of-servers).

Interview-grade talking point: MCP servers can call back to clients via sampling, reversing the typical trust direction (https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/). This breaks naive trust boundaries that put servers as data and clients as code.

## 2. Anthropic Claude Skills and Agent Skills supply chain

Claude Skills (released late 2025) ship as bundles of code, instructions, and resources that load into the agent's context. Three classes of attack are documented in the wild as of 2026:

- "--dangerously-skip-permissions" abuse to bypass Claude Code authorization gates. Documented in tweet-and-blog posts and aggregated in arxiv submissions through Q1 2026. https://arxiv.org/html/2602.06547v1
- MCP server hijacking via shipped .mcp.json in skill bundles.
- Hook-based exfiltration intercepting every tool operation.

A January 2026 academic study retrieved 25,187 skills from 3,217 GitHub repositories and 73,193 skills from 10,373 repositories, finding widespread vulnerabilities (https://arxiv.org/html/2601.10338v1). Noma Security's whitepaper draws a hard line: most enterprises govern only the observable half (MCP tool params), but Skills run inside model reasoning where current observability tools cannot see what they cause (https://blog.cyberdesserts.com/ai-agent-security-risks/).

Cited at scale: MCP Security Crisis report. 43% of servers vulnerable, 341 malicious skills found in the public ecosystem (https://gentic.news/article/mcp-security-crisis-43-of-servers).

## 3. Claude Code, Cursor, and AI IDE attack surface

GitHub Copilot CVEs:
- CVE-2025-53773 (CVSS 7.8 HIGH). YOLO-mode prompt injection RCE on developer machines without click, download, or approval. Reported by Johann Rehberger. https://gbhackers.com/ai-developer-tools/
- CVE-2025-64660. Additional Copilot vuln addressed in same patch wave.

Cursor CVEs:
- CVE-2025-49150
- CVE-2025-54130
- CVE-2025-54135. CurXecute. Config changes and malicious commands execute before the user can reject them. https://gbhackers.com/ai-developer-tools/
- CVE-2025-54136. MCPoison.
- CVE-2025-61590.

Hidden Unicode rules-file backdoors (Mar 2025): invisible characters in .cursorrules and copilot-instructions.md inject malicious code. GitHub responded with a Unicode-warning UI on github.com (https://www.pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents).

IDEsaster attack chain. 24 CVEs assigned. 100% of tested AI IDEs and integrations vulnerable (https://www.helpnetsecurity.com/2026/05/05/ai-agent-security-skills-blind-spots/).

## 4. Supply chain attacks on prompt template hubs and AI dependencies

ContextCrush attack (Q1 2026). Cursor user requests coding help. Agent fetches docs from a poisoned Context7 library. Hidden instructions tell the agent to read local files and dump contents into an attacker-controlled GitHub issue (https://blog.cyberdesserts.com/ai-agent-security-risks/).

GitHub secret leakage in AI-assisted code. GitGuardian documented 28.65 million new hardcoded secrets in public GitHub commits during 2025, a 34% YoY increase. AI-assisted commits showed 3.2% secret-leak rate vs 1.5% baseline (https://gbhackers.com/ai-developer-tools/).

AI-generated code CVEs spiked: 35 new CVEs in March 2026 directly attributable to AI-generated code, up from 6 in January and 15 in February (https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-generated-code-vulnerability-surge-2026/). Veracode found 45% of AI-generated code samples introduce OWASP Top 10 vulnerabilities (https://www.infosecurity-magazine.com/news/ai-generated-code-vulnerabilities/).

## 5. AI Bill of Materials (AIBOM) and ML-BOM

CycloneDX ML-BOM is part of CycloneDX 1.6 and the Ecma-424 standard (https://cyclonedx.org/capabilities/mlbom/). It captures model provenance, dataset lineage, training methodology, and framework configuration.

OWASP AIBOM project. v0.1 milestone targeted November 2025, on-track per OWASP communications (https://owasp.org/www-project-aibom/). Captures AI-specific components that traditional SBOM misses: model versions and provenance, training data lineage, inference API connections, agentic dependency chains, MCP server connections, external tool integrations.

SPDX 3.0 has parallel work on AI extensions. OWASP AIBOM is currently triaging both standards rather than building a third.

Why the candidate cares: Enterprise procurement and Federal procurement are starting to require AIBOMs the way SBOMs became required for federal contracts post-EO 14028. Expect this to be a midmarket and large-enterprise procurement gate by H2 2026.

## 6. ISO 42001 trend

ISO/IEC 42001:2023 is the AI Management System standard (https://www.iso.org/standard/42001). By 2026 it is in its first real growth wave. BSI, A-LIGN, Schellman, and KPMG have all done early certifications. Fortune 500 buyers are starting to require either certification or a clear roadmap from vendors (https://enactia.com/iso-42001-certification-the-2026-roadmap-for-ai-governance/).

For an engineer, the practical depth needed is: ability to map controls from NIST AI RMF and OWASP AI Exchange to ISO 42001 Annex A controls, ability to articulate the difference between an AIMS (42001) and an ISMS (27001), and ability to identify which existing 27001 evidence reuses for 42001.

Implementation timeline ranges from 6 to 9 months (existing 27001 ISMS) to 12 to 18 months (greenfield).

## 7. NIST AI RMF Generative AI Profile (NIST AI 600-1)

Released July 26, 2024 (https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). 13 risks. 400+ actions mapped to GOVERN, MAP, MEASURE, MANAGE.

Four primary considerations: Governance, Content Provenance, Pre-deployment Testing, Incident Disclosure.

Interview pattern in 2026: candidates are asked to map a real AI threat (e.g., RAG poisoning or model exfiltration) to specific MAP and MEASURE actions in 600-1. Knowing the doc number and structure is signal.

## 8. EU AI Act enforcement timeline

Source: https://artificialintelligenceact.eu/implementation-timeline/

- February 2, 2025. Prohibited AI practices in force.
- August 2, 2025. AI Office operational. GPAI provider obligations begin. Penalty regime in force. Fines up to EUR 35M or 7% of global turnover for prohibited practices.
- August 2, 2026. High-risk AI system requirements (Annex III) become enforceable: employment, credit, education, law enforcement use cases. GPAI enforcement powers in force.
- August 2, 2027. Full compliance for high-risk including medical devices and IVDs.

Penalty bands: EUR 35M or 7% turnover (prohibited), EUR 15M or 3% (other obligations), EUR 7.5M or 1% (incorrect or misleading reporting).

Interview pattern: "Walk me through what your team has to ship by August 2, 2026 if your product is an Annex III high-risk system." Candidates should be able to name post-market monitoring, conformity assessment, technical documentation, transparency obligations, and human oversight as the structural pieces.

## 9. RAG poisoning

PoisonedRAG (USENIX Security 2025) achieves high attack success rates across multiple datasets and LLMs. White-box optimization of malicious text takes <30 seconds (https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf).

Key evolution from 2024: 2025 papers move beyond static retrieval poisoning to chain-poisoning where one corrupted entry seeds multi-hop retrieval failures across the index. Evaluation now spans semantic-search retrievers (Pinecone, Weaviate) plus hybrid BM25 + dense fusion patterns.

Mitigation that interviewers want to hear: retrieval source provenance and signing, chunk-level integrity checks, retrieval diversity to limit single-source dominance, output validation against retrieved context.

## 10. Multimodal jailbreaks

Multimodal attacks combine adversarial images, audio, or video with text prompts to bypass guardrails. Black Hat USA 2025 "From Prompts to Pwns" highlighted multimodal as a persistent gap because text-only prompt injection scanners miss image-encoded payloads (https://i.blackhat.com/BH-USA-25/Presentations/US-25-Lynch-From-Prompts-to-Pwns.pdf).

Meta's CyberSecEval Prompt Injection benchmarks and PromptGuard work, presented at DEF CON 32 AI Village, demonstrated detection across direct jailbreak and indirect injection but acknowledged multimodal as out of scope for v1 (https://aivillage.org/events/defcon32/).

## 11. Voice cloning and deepfake operations

Voice cloning has crossed the indistinguishable threshold per researcher consensus (https://fortune.com/2025/12/27/2026-deepfakes-outlook-forecast/). 3-second source audio is sufficient.

Documented incidents:
- $25.6M wire fraud at a Hong Kong-based finance team via deepfake video conference. Disclosed February 2024, still cited as the canonical case.
- Marco Rubio impersonation via Signal voice messages, July 2025. Targeted foreign ministers, sitting senator, governor.
- Deepfake-enabled vishing surged >1,600% Q1 2025 vs Q4 2024 in the US.
- 100,000+ voice deepfake attacks recorded in the US in 2025.

Sources: https://www.group-ib.com/blog/voice-deepfake-scams/, https://cybelangel.com/blog/deepfake-ceo-fraud-how-voice-cloning-targets-us-executives/, https://deepstrike.io/blog/deepfake-statistics-2025

Detection note: AI deepfake detectors lose 45 to 50% accuracy in real-world conditions vs lab benchmarks. Human detection on high-quality media drops to 24.5% accuracy. Detection alone is not a strategy.

## 12. Fine-tuning and alignment attacks

TwinBreak (USENIX Security 2025). Parameter pruning attack that analyzes activation differences between safety-triggering and non-triggering prompts, then prunes parameters to produce a jailbroken model (https://www.usenix.org/system/files/usenixsecurity25-krauss.pdf).

Self-Defend (USENIX Security 2025). LLMs identify harmful portions in user queries to defend themselves. GPT-3.5 attack success: 0.256 to 0.980, average 0.655. GPT-4 typically 0.047 to 0.330. Smaller models are dramatically easier to jailbreak (https://www.usenix.org/system/files/usenixsecurity25-wang-xunguang.pdf).

Defending Against Prompt Injection with Structured Queries (USENIX Security 2025). Adapted state-of-the-art jailbreak techniques to prompt injection. Defense reduced TAP from 97% to 9% on Llama and GCG from 97% to 58%. Mechanism: structured separator format between prompt and data (https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf).

## 13. Agentic AI in active operations (the "GTG-1002" pattern)

GTG-1002 Chinese espionage (Sept to Nov 2025). Claude Code executed 80 to 90% of tactical operations against ~30 organizations after operators posed as legitimate red teamers (https://github.com/webpro255/awesome-ai-agent-attacks).

CyberStrikeAI FortiGate campaign (Jan to Feb 2026). Russian-speaking actor used commercial GenAI plus the open-source CyberStrikeAI framework to compromise 600+ FortiGate devices across 55 countries without exploiting a single CVE.

HexagonalRodent Web3 dev campaign (Q1 2026). North Korean APT subgroup (Famous Chollima) used Cursor, ChatGPT, Anima to author malware, build fake company sites, craft phishing. Estimated $12M crypto theft. 26,584 wallets exfiltrated from 2,726 dev systems.

Why interviewers raise this: It is the strongest evidence that agentic AI is now an offensive capability multiplier, not a future threat. Candidates should be able to discuss what defenses (egress filtering, agent-output policy enforcement, MCP allowlists, pinned skills) materially cut into these chains.

## 14. Constitutional AI vs RLHF debate

[UNVERIFIED with primary 2026 source.] In public discourse through 2025 and into 2026, Anthropic continues to publish Constitutional AI variants (CAI v2, RLAIF) and OpenAI continues with RLHF and instruction-following alignment work. Interviewers at frontier labs will probe whether the candidate can discuss the alignment tax tradeoff (CAI tends to over-refuse), data efficiency (CAI uses smaller human-feedback datasets), and red team implications (CAI surface-level robustness vs RLHF robustness can diverge for novel attacks).

Treat this as a soft topic: the candidate must demonstrate awareness, not deep expertise. Going past surface-level here is a research-engineer expectation, not a security-engineer expectation.

## 15. Mosaic ML attack surface and fine-tuning provider risk

[UNVERIFIED specific 2026 disclosure.] Mosaic ML (acquired by Databricks) and similar fine-tuning provider stacks expose three risk classes the candidate should know:

- Tenant isolation in multi-tenant fine-tuning: weights or training data crossing tenants.
- Stored training-data exfiltration via post-training inference (membership inference, training data extraction).
- Adapter-layer (LoRA, QLoRA) supply chain: a malicious adapter shipped via Hugging Face can carry weight-level backdoors.

Hugging Face has periodic disclosure of malicious model uploads. Treat as known-known risk class with active mitigation (model scanning, signed weights).

## 16. The Anthropic and OpenAI agent-deployment guidance

Both labs publish responsible deployment guidance. Anthropic Acceptable Use Policy and Claude Use Policy enumerate prohibited uses. OpenAI Usage Policies parallel. Interviewers expect candidates to know that the policy layer exists, that it is enforced via post-training and runtime classifiers, and that it is not a substitute for application-layer controls.

[UNVERIFIED specific 2026 policy revision dates] but the bones have been stable since 2024.

## 17. OWASP LLM Top 10 (2025 baseline, used in 2026)

Source: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/

1. LLM01 Prompt Injection
2. LLM02 Sensitive Information Disclosure
3. LLM03 Supply Chain Vulnerabilities
4. LLM04 Data and Model Poisoning
5. LLM05 Improper Output Handling
6. LLM06 Excessive Agency
7. LLM07 System Prompt Leakage
8. LLM08 Vector and Embedding Weaknesses
9. LLM09 Misinformation
10. LLM10 Unbounded Consumption

OWASP also released a Top 10 for Agentic Applications 2026, the first dedicated agentic framework focused on autonomy: planning, decision making, and multi-step action across systems (https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications).

## 18. MITRE ATLAS

Source: https://atlas.mitre.org/

As of February 2026 (v5.4.0): 16 tactics, 84 techniques, 56 sub-techniques, 32 mitigations, 42 case studies. November 2025 v5.1.0 added agentic AI techniques. Center for Threat-Informed Defense and ATLAS expanded coverage in 2026 with rapid-response and emulation capabilities, and the first Rapid Response Report process (https://ctid.mitre.org/blog/2026/05/06/secure-ai-v2-release).

The 2026 strategic shift: from model-centric attacks to execution-layer exposure. Threat modeling now must address autonomous workflow chaining, delegated authority persistence, and API-level orchestration risk (https://zenity.io/blog/current-events/mitre-atlas-ai-security).

## 19. OWASP AI Exchange

Source: https://owaspai.org/

OWASP Flagship project. 300+ pages. Built by 70+ experts. Feeds into ISO/IEC 27090 (70 pages contributed), 27091, EU AI Act technical guidance (70 pages contributed), OpenCRE.

Core threat taxonomy categories: prompt injection (direct and indirect), evasion and adversarial examples, data and model poisoning including supply chain, extraction (training data leak, model replication), output-related risks where output drives downstream attacks.

This is the single best free reference for an engineer who needs to map controls to threats coherently. Interviewers at midmarket and consulting roles often ask candidates to use AI Exchange terminology.

## 20. DEF CON 32 AI Village highlights (used as reference for 2026 interviews)

Source: https://aivillage.org/events/defcon32/

- FuzzLLM (UC Irvine, Ian G. Harris). Automated fuzzing for LLM jailbreak discovery via templates, constraint isolation, combo attacks.
- Meta Llama 3 red team (Maya Pavlova, Ivan Evtimov, Joanna Bitton, Aaron Grattafiori). Multi-turn adversarial AI agents, automated scaling, safety benchmarks.
- CyberSecEval Prompt Injection (Meta, Cyrus Nikolaidis and Faizan Ahmad). PromptGuard direct + indirect injection detector.
- Cognitive Attack Taxonomy (Psyber Labs, Matthew Canham). 350+ cognitive vulnerabilities and TTPs.

## 21. Black Hat USA 2025 highlights

Source: https://i.blackhat.com/BH-USA-25/Presentations/US-25-Lynch-From-Prompts-to-Pwns.pdf

- "From Prompts to Pwns: Exploiting and Securing AI Agents" (Becca Lynch, Rich Harang, NVIDIA). Headline take: "assume prompt injection." If you architect an agentic system without that assumption, you are wrong by default.
- SPIKEE (Reversec). Modular toolkit for testing LLM apps for prompt injection.
- A.I.G. Agent-based scanner for MCP server source code or remote MCP URLs across 9 risk categories including tool poisoning, RCE, indirect prompt injection.
- Promptfoo (vendor presence). LLM red team automation in CI.

## Read-out for the candidate

If the candidate cannot speak with specificity about at least 7 of these 21 topics, they will not test well at $200k+ AI security interviews in 2026. The minimum non-negotiable list:

1. OWASP LLM Top 10 (enumerate by ID, rank by 2025 to 2026 prevalence)
2. MITRE ATLAS (know it exists, know the 2026 shift toward execution-layer)
3. NIST AI RMF Generative AI Profile (number, structure, four primary considerations)
4. EU AI Act timeline (2025, 2026, 2027 dates and penalty bands)
5. Prompt injection (direct, indirect, multimodal, mitigations including structured queries)
6. MCP server attack surface (at least 2 named CVEs)
7. RAG poisoning (PoisonedRAG name, mitigation patterns)

Bonus differentiation comes from: a personal POV on Constitutional AI vs RLHF, the GTG-1002 pattern, and at least one real lab where the candidate has run Garak or Promptfoo against a real target.

## All sources

- https://genai.owasp.org/llm-top-10/
- https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- https://atlas.mitre.org/
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- https://artificialintelligenceact.eu/implementation-timeline/
- https://www.iso.org/standard/42001
- https://owaspai.org/
- https://owasp.org/www-project-aibom/
- https://cyclonedx.org/capabilities/mlbom/
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
- https://blog.cyberdesserts.com/ai-agent-security-risks/
- https://arxiv.org/html/2602.06547v1
- https://arxiv.org/html/2601.10338v1
- https://www.usenix.org/system/files/usenixsecurity25-zou-poisonedrag.pdf
- https://www.usenix.org/system/files/usenixsecurity25-chen-sizhe.pdf
- https://www.usenix.org/system/files/usenixsecurity25-krauss.pdf
- https://www.usenix.org/system/files/usenixsecurity25-wang-xunguang.pdf
- https://i.blackhat.com/BH-USA-25/Presentations/US-25-Lynch-From-Prompts-to-Pwns.pdf
- https://aivillage.org/events/defcon32/
- https://github.com/webpro255/awesome-ai-agent-attacks
- https://fortune.com/2025/12/27/2026-deepfakes-outlook-forecast/
- https://www.group-ib.com/blog/voice-deepfake-scams/
- https://deepstrike.io/blog/deepfake-statistics-2025
- https://ctid.mitre.org/blog/2026/05/06/secure-ai-v2-release
- https://zenity.io/blog/current-events/mitre-atlas-ai-security
- https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-generated-code-vulnerability-surge-2026/
- https://www.infosecurity-magazine.com/news/ai-generated-code-vulnerabilities/

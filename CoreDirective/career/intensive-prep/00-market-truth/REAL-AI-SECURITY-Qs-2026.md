# Real AI and LLM Security Interview Questions, 2026

Reference document. Real AI Security and LLM Security interview questions surfaced
from public sources, with senior-bar depth notes (USD 200K+ AI Security Engineer,
ML Security, AI Red Team). `[UNVERIFIED]` marks paraphrased questions without a
clean primary citation. Sources cited inline.

---

## 1. Prompt Injection (LLM01)

### Q1.1 Direct vs indirect prompt injection
- **Question:** Define prompt injection and the difference between direct and indirect
  prompt injection. Give a real-world example of each.
- **Source:** OpenAI prompt injection essay; OWASP Gen AI Security Project LLM01;
  Practical DevSecOps AI Security 50+ question set.
  https://openai.com/index/prompt-injections/
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
  https://www.practical-devsecops.com/ai-security-interview-questions/
- **Senior depth expected:** Direct = attacker types into the chat box "ignore
  previous instructions". Indirect = attacker poisons content the agent retrieves
  (a webpage, a document, an email) so the model executes attacker instructions
  hidden in data. Cite the Bing Chat Sydney leak (early 2023) as the canonical
  direct case; cite indirect via web-browsing agents and email assistants.

### Q1.2 Walk me through detection and mitigation of indirect injection in a RAG
- **Question:** A RAG pipeline retrieves documents from a vector store. Walk through
  how you detect and mitigate an indirect prompt injection in that retrieval.
- **Source:** Networkers Home AI Cyber Security Interview Q&A (2026).
  https://www.networkershome.com/ai-cyber-security-interview-questions-2026/
- **Senior depth expected:** Layered defense.
  - **Pre-retrieval:** signed and trusted sources only, content provenance, chunk
    classifier flagging imperative language and role-switching patterns.
  - **Prompt template:** treat retrieved context as untrusted data, use clear
    structural separators, never let retrieved content choose tools or override
    system instructions.
  - **Output:** semantic classifier on the response, output schema validation,
    tool call allowlist.
  - **Telemetry:** log every prompt with retrieved chunk IDs so you can replay
    and analyze.
  Strong answers explicitly say "no single layer holds. Defense in depth or you
  fail." Weak answers reach for one regex.

### Q1.3 Design a prompt injection filter
- **Question:** How would you design a filter to block prompt injection attacks?
- **Source:** Practical DevSecOps AI question Q11.
- **Senior depth expected:** Senior candidates push back. A pure filter is
  insufficient because injections can be encoded, translated, base64'd, or
  multilingual. The right design is a small classifier model running in front of
  the main LLM combined with prompt template hardening, output filtering, and
  least-privilege tool access. Tools mentioned: Lakera Guard, Rebuff, NVIDIA NeMo
  Guardrails, Promptfoo for regression testing.

### Q1.4 Prevent system prompt extraction
- **Question:** How can you prevent an LLM from revealing your company's internal
  system prompt?
- **Source:** Practical DevSecOps Q17, OWASP LLM07 (System Prompt Leakage).
- **Senior depth expected:** You cannot fully prevent leakage at the model layer.
  Architectural answer: do not put secrets in the system prompt, use external
  authorization, treat the system prompt as public, scan for accidental sensitive
  data inclusion, and run regression tests with Garak or Promptfoo. The senior tell
  is naming the assumption that prompts are leakable and designing accordingly.

---

## 2. Jailbreaks and Bypasses

### Q2.1 Common jailbreak families
- **Question:** Name jailbreak categories and how each works.
- **Source:** OWASP LLM01 v2 supplement, Lakera Gandalf challenge writeups.
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- **Senior depth expected:** Role-play (DAN, persona switch), token smuggling, low-
  resource language, encoding (base64, leet, cipher), context overflow, multi-turn
  manipulation, payload splitting (the harmful instruction is assembled across
  turns), tool-output injection. Senior candidates also mention universal adversarial
  suffixes (Zou et al., GCG attack).

### Q2.2 Walk me through red-teaming a customer-facing GenAI chatbot
- **Question:** Five-phase red team plan for a production chatbot.
- **Source:** Networkers Home Q19.
- **Senior depth expected:** Reconnaissance (system prompt, model, deployment
  layout) -> bypass (injection, encoding, language switches) -> extraction
  (system prompt, training data, customer data) -> tool abuse (excessive agency,
  privilege boundary tests) -> reasoning manipulation (chain-of-thought hijack).
  Document each finding with CVSS-style severity and reproducible POCs.

### Q2.3 Microsoft AI Red Team approach
- **Question:** How does Microsoft's AI Red Team approach LLM testing?
- **Source:** Networkers Home Q18 referencing Microsoft AI Red Team blog series.
- **Senior depth expected:** Threat modeling, adversarial probing across responsible
  AI dimensions, automation via PyRIT (Python Risk Identification Tool for AI),
  cross-disciplinary teams. Focus on context-specific harms beyond the CIA triad.

---

## 3. Supply Chain (LLM03 Data Poisoning, LLM05 Supply Chain, LLM10 Model Theft)

### Q3.1 PoisonGPT and model integrity
- **Question:** How would you detect a poisoned open-source model uploaded to
  Hugging Face?
- **Source:** Networkers Home and Practical DevSecOps cross-listed.
  Original incident: Mithril Security PoisonGPT post (2023).
- **Senior depth expected:** Threat: a maintainer uploads a model that behaves
  normally except on a triggered input. Detection: signed model checkpoints, SBOM
  for the model artifact, behavioral testing on a canary set, monitoring output
  drift on a fixed eval suite. Architectural fix: do not run unverified weights on
  privileged data paths.

### Q3.2 Detect model theft via API extraction
- **Question:** How would you detect someone trying to steal your AI model through
  the API?
- **Source:** Practical DevSecOps Q6.
- **Senior depth expected:** Per-API-key rate limits with anomaly detection for
  high-cardinality query patterns (membership inference signature), watermarked
  responses, query-cost ceilings, and TOS-tied legal posture. The honest answer
  acknowledges that for sufficiently funded attackers, distillation is hard to fully
  prevent and the focus shifts to economic and legal disincentives.

### Q3.3 Training data poisoning
- **Question:** Can attackers poison training data? How would you catch it?
- **Source:** Practical DevSecOps Q8.
- **Senior depth expected:** Yes. Two patterns: (1) adversarial samples added at
  pretraining or fine-tuning, (2) adversarial chunks added to a RAG vector store
  at runtime. Catch via data provenance, dataset hashing, anomaly detection on
  embedding distributions, and adversarial training. Mention specific research
  (Carlini et al. on data poisoning at scale).

### Q3.4 SBOM for an AI model
- **Question:** What is in an AI model's SBOM?
- **Source:** Practical DevSecOps Q52.
- **Senior depth expected:** Base model identifier and hash, fine-tuning datasets
  and licenses, training framework versions, eval results, intended use, known
  failure modes, third-party datasets. Reference OWASP CycloneDX ML extension and
  the NIST AI RMF requirement for model documentation.

---

## 4. RAG Security

### Q4.1 Top 3 RAG security risks
- **Question:** Name the top three security risks of a production RAG system.
- **Source:** Networkers Home Q9.
- **Senior depth expected:**
  1. Indirect prompt injection in indexed documents.
  2. Sensitive data leakage across tenants and roles when ACLs are not enforced
     at query time.
  3. Vector database poisoning where malicious embeddings collide with legitimate
     queries.
  Senior candidates also mention metadata leakage, where document IDs or paths in
  the response leak structure that should be hidden.

### Q4.2 Multi-tenant RAG isolation
- **Question:** Design a RAG that serves customer A and customer B from the same
  vector database without leakage.
- **Source:** Implied across OWASP LLM02 (Sensitive Information Disclosure)
  and Practical DevSecOps. `[UNVERIFIED]` exact wording.
- **Senior depth expected:** Per-tenant filtering at retrieval time enforced by the
  application layer, never the model. Per-tenant namespace or collection in the
  vector DB. Per-tenant signing key for embeddings if the threat model requires
  cryptographic isolation. Test for leakage with adversarial queries that try to
  cross the tenant boundary.

---

## 5. Agent and Tool Security

### Q5.1 Excessive Agency (LLM08)
- **Question:** Define excessive agency. Give a recent real-world incident.
- **Source:** OWASP LLM08; Reversec design patterns to secure LLM agents.
  https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
- **Senior depth expected:** The agent has tools or permissions it should not, and
  the model can be tricked into using them. Mitigation patterns: tool allowlist
  per session, per-tool input validation, human-in-the-loop on destructive
  operations, blast-radius minimization (no admin tokens for agents), action
  classifier ("is this a write operation?").

### Q5.2 Multi-agent threats
- **Question:** What new threats emerge when multiple AIs work together?
- **Source:** Practical DevSecOps Q30.
- **Senior depth expected:** Cascading errors (one agent's hallucination feeds the
  next), emergent collusion (agents converge on a goal the operator did not
  define), communication poisoning (an attacker injects into agent-to-agent
  messages), goal hijacking. Reference OWASP Top 10 for Agents 2026 and
  DeepTeam framework.
  https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications

### Q5.3 MCP server security
- **Question:** What security concerns are unique to MCP (Model Context Protocol)
  servers?
- **Source:** MITRE ATLAS January 2026 update added three case studies on MCP server
  compromise and indirect prompt injection via MCP channels.
  https://atlas.mitre.org/
- **Senior depth expected:** MCP servers are tools the model can invoke. Risks:
  the server itself is a remote-code-execution surface, the server can return
  attacker-controlled data that becomes prompt injection in the next turn, the
  server's auth boundary may not match the user's auth scope. Mitigations:
  authenticate every MCP server, sandbox tool execution, log every tool call,
  treat MCP responses as untrusted input, scope tools per session.

### Q5.4 Anthropic Claude Skills risks
- **Question:** What new risks come with shipped Claude Skills (Skill packages)?
- **Source:** Anthropic Claude documentation on Skills, surfaced in 2026 AI sec
  threat model write-ups. `[UNVERIFIED]` formal interview questions on this are
  newer than most question banks.
- **Senior depth expected:** Skills bundle code, prompts, and examples. Risks:
  malicious skill in a marketplace, skill that exfiltrates data via tool calls,
  skill that runs in a context with broader permissions than the user expected.
  Mitigations: skill signing, marketplace review, sandboxed execution, per-skill
  permission prompts, runtime audit.

---

## 6. MITRE ATLAS

### Q6.1 What is ATLAS, how is it different from ATT&CK
- **Question:** Define MITRE ATLAS and its relationship to MITRE ATT&CK.
- **Source:** Networkers Home Q16; MITRE ATLAS site.
  https://atlas.mitre.org/
- **Senior depth expected:** ATLAS is the adversarial threat landscape for AI
  systems. As of November 2025 (v5.1.0) it has 16 tactics, 84 techniques, 32
  mitigations, and 42 case studies. ATT&CK targets traditional IT, ATLAS targets
  the ML lifecycle. They complement each other: an adversary chain often crosses
  both (initial access via classic phishing, then ML model evasion or extraction).

### Q6.2 Map a jailbreak chain to ATLAS tactics
- **Question:** Map a real LLM jailbreak attack to MITRE ATLAS tactic-technique
  chain.
- **Source:** Networkers Home Q17.
- **Senior depth expected:** Example chain: AML.T0050 LLM Prompt Injection ->
  AML.T0042 Verify Attack -> AML.T0011 ML-Enabled Product Discovery -> AML.T0057
  LLM Plugin Compromise. Map mitigations to specific MITRE M-series techniques.
  Senior candidates name the ATLAS Navigator and reference how they have used the
  framework on real or training engagements.

### Q6.3 ATLAS v5.3 January 2026 additions
- **Question:** What was added in the January 2026 ATLAS update?
- **Source:** Zenity blog tracking ATLAS updates.
  https://zenity.io/blog/current-events/mitre-atlas-ai-security
- **Senior depth expected:** Three new case studies on MCP server compromise,
  indirect injection via MCP channels, and malicious AI agent deployment.
  Candidates aware of these specifics signal active engagement with the field.

---

## 7. OWASP LLM Top 10 v2 (2025 to 2026)

### Q7.1 Name the OWASP LLM Top 10 and rank by severity
- **Question:** Name the OWASP Top 10 for LLM Applications, version 2025, and rank
  by observed severity.
- **Source:** Networkers Home Q5; OWASP Gen AI Security Project.
  https://owasp.org/www-project-top-10-for-large-language-model-applications/
- **Senior depth expected:** LLM01 Prompt Injection, LLM02 Sensitive Information
  Disclosure, LLM03 Supply Chain, LLM04 Data and Model Poisoning, LLM05 Improper
  Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM08
  Vector and Embedding Weaknesses, LLM09 Misinformation, LLM10 Unbounded
  Consumption. Note: 2025 edition reorganized the v1 list. Strong candidates note
  that LLM01 and LLM06 are the most exploited in production; LLM02 and LLM07
  next. They cite at least one real example per category.

### Q7.2 Mitigate Sensitive Information Disclosure
- **Question:** How would you mitigate LLM02 Sensitive Information Disclosure?
- **Source:** Networkers Home Q6.
- **Senior depth expected:** PII redaction pre-input, system prompt restrictions,
  output filtering, training data audits, RAG context filtering at query time,
  audit logs of inputs and outputs, periodic leakage testing with red team
  prompts. Mention legal posture: the data should not be in the training set in
  the first place.

### Q7.3 Improper Output Handling
- **Question:** Why is improper output handling dangerous? Give an example.
- **Source:** OWASP LLM05.
- **Senior depth expected:** LLM output is untrusted. If you pipe it directly into
  shell, eval, SQL, or a browser DOM, you have remote code execution. Example:
  agent generates SQL that the application executes without parameterization, the
  attacker poisons the prompt to produce a `DROP TABLE`. Mitigation: never trust
  LLM output as code, parameterize, sandbox.

---

## 8. Evaluation Frameworks and Testing Tools

### Q8.1 NeMo Guardrails vs Garak
- **Question:** What is NeMo Guardrails, what is Garak, when do you use each?
- **Source:** Networkers Home Q14.
- **Senior depth expected:** NeMo Guardrails is runtime, YAML/Colang-defined rules
  that wrap the LLM call. Garak is offline vulnerability scanning, you point it
  at an LLM and it runs probes. Use both: Garak in CI to gate model promotions,
  NeMo or equivalent runtime guard in production.

### Q8.2 Promptfoo
- **Question:** How would you use Promptfoo in a CI pipeline?
- **Source:** Promptfoo docs and OWASP Gen AI tooling references.
- **Senior depth expected:** Define a YAML test suite that runs against every model
  or prompt change. Categories: jailbreak resistance, hallucination on factual
  questions, refusal on disallowed topics, structured output schema compliance.
  Block model promotion on regression. Senior candidates discuss test case
  generation strategies, cost ceilings, and how to handle non-deterministic
  outputs in CI.

### Q8.3 Red-team a fraud detection ML model
- **Question:** Methodology to red-team a non-LLM ML classifier.
- **Source:** Networkers Home Q8.
- **Senior depth expected:** Reconnaissance, black-box probing, membership
  inference, model extraction, adversarial example generation (FGSM, PGD, Carlini
  Wagner), feature engineering evasion. Tools: Adversarial Robustness Toolbox
  (ART), Counterfit, TextAttack.

---

## 9. AI Governance (NIST AI RMF, ISO 42001, EU AI Act)

### Q9.1 NIST AI RMF four functions
- **Question:** Explain the four functions of the NIST AI RMF.
- **Source:** Networkers Home Q13; NIST AI RMF document.
- **Senior depth expected:** Govern, Map, Measure, Manage. Govern sets accountability
  and policy. Map identifies context and characteristics. Measure quantifies risks.
  Manage applies controls and monitors. Mention the July 2024 generative AI
  profile and that the framework is voluntary in the US but increasingly cited in
  contracts.

### Q9.2 ISO 42001
- **Question:** What is ISO 42001 and when would a company pursue certification?
- **Source:** AI governance industry references. `[UNVERIFIED]` no clean primary
  question source, but it is appearing in 2026 enterprise AI security RFPs.
- **Senior depth expected:** ISO 42001 is the AI management system standard
  published December 2023. Pursue when selling to enterprises that require it,
  when operating in regulated industries, or when the EU AI Act compliance
  pathway is relevant. It maps to ISO 27001 structure (PDCA cycle).

### Q9.3 EU AI Act high-risk requirements
- **Question:** What does the EU AI Act require for high-risk AI systems?
- **Source:** Networkers Home Q12.
- **Senior depth expected:** Risk management system, data governance, technical
  documentation, logging, transparency, human oversight, accuracy and robustness
  and cybersecurity, conformity assessment. Penalties up to EUR 35M or 7% of
  global revenue. High-risk includes critical infrastructure, education, law
  enforcement, employment-related uses.

### Q9.4 90-day plan to start an AI security program
- **Question:** Build a 90-day plan for starting an AI security program at a
  company that just deployed its first LLM use case.
- **Source:** Practical DevSecOps Q37.
- **Senior depth expected:** Days 0-30: inventory of AI use cases, threat model
  per use case, baseline policies (acceptable use, data handling, vendor risk).
  Days 30-60: tooling (NeMo Guardrails or equivalent, Promptfoo CI, monitoring,
  audit logs), red team baseline against the highest-risk use case. Days 60-90:
  governance (NIST AI RMF mapping, AI committee, incident response playbook for
  AI), training, metrics. Senior candidates explicitly say "do not buy a tool
  before you have a policy."

---

## 10. Behavioral and Career Questions

### Q10.1 Tell me about an AI security issue you discovered or remediated
- **Question:** STAR-format account of a real incident or finding.
- **Source:** Networkers Home Q22.
- **Senior depth expected:** Concrete: a prompt injection you found in a deployed
  agent, a vector store leak across tenants, a tool that allowed write access it
  should not have. Avoid hypothetical answers. If you have not done it in
  production, do it in a side project or a CTF and then have something to say.

### Q10.2 Why are you switching from traditional cyber to AI security
- **Question:** What's your story for the move?
- **Source:** Networkers Home Q23.
- **Senior depth expected:** Frame with prior depth, specific learning actions
  (labs, certs, contributions, code), and market reasoning. Avoid "I think AI is
  the future" without specifics. Cite Lakera Gandalf, OWASP LLM Top 10 work, an
  Anthropic prompt injection challenge, or a tool you built.

### Q10.3 How do you stay current
- **Question:** How do you stay current with AI security threats given how fast
  the field evolves?
- **Source:** Networkers Home Q21.
- **Senior depth expected:** Specific named sources. MITRE ATLAS, OWASP LLM,
  arXiv (cs.CR plus cs.LG), specific researchers (Nicholas Carlini, Florian Tramer,
  Sam Bowman, Ethan Perez), red team challenge ladders, vendor advisories. Time
  budget: 4 to 6 hours per week of focused reading, separate from doing.

---

## 11. The Single Most-Asked AI Security Question

Across this dataset, the single most-asked AI Security question is "Walk me through
detection and mitigation of prompt injection in a production system, specifically
the indirect variant in a RAG or agentic flow." It appears in some form in
Practical DevSecOps, Networkers Home, OpenAI's own essay, OWASP LLM01, and Lakera
red team material. The senior bar is not "name the attack" but "name the layered
defenses, name the limits of each, and name the architectural choice that makes
defense viable."

---

## Sources

- OpenAI: Understanding prompt injections.
  https://openai.com/index/prompt-injections/
- OWASP Gen AI Security Project, LLM Top 10 v2 (2025).
  https://genai.owasp.org/llmrisk/llm01-prompt-injection/
  https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Top 10 for Agents 2026 (DeepTeam framework).
  https://www.trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications
- Practical DevSecOps: 50+ AI Security Interview Questions and Answers for 2026.
  https://www.practical-devsecops.com/ai-security-interview-questions/
- Networkers Home: AI Cyber Security Interview Questions 2026, 25 Real Q&As.
  https://www.networkershome.com/ai-cyber-security-interview-questions-2026/
- MITRE ATLAS site and v5.3 release.
  https://atlas.mitre.org/
- Zenity: ATLAS 2026 update tracking.
  https://zenity.io/blog/current-events/mitre-atlas-ai-security
- Reversec: Design patterns to secure LLM agents in action.
  https://labs.reversec.com/posts/2025/08/design-patterns-to-secure-llm-agents-in-action
- Repello AI: OWASP LLM Top 10 2026 complete guide with real-world incidents.
  https://repello.ai/blog/owasp-llm-top-10-2026
- Vectra AI: MITRE ATLAS topic page.
  https://www.vectra.ai/topics/mitre-atlas
- NIST AI RMF documentation.
- Microsoft AI Red Team blog posts and PyRIT documentation.
- Pydantic LLM intro for structured-output validation patterns.
  https://pydantic.dev/articles/llm-intro

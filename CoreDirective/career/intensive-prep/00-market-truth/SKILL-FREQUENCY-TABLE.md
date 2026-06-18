# Skill Frequency Table: AI Security Engineer JD Sample, May 2026

Sample size: 18 JDs where the explicit required-skill bullets could be verified. Source list is the JD-FREQUENCY-ANALYSIS.md companion file in this directory. Skills below are sorted descending by JD appearance count. Synonyms are normalized in the same way as the companion file. Numbers are JD-mention counts, not weighted by seniority or comp.

## Master skill table

| Rank | Skill | Count | Pct | Tier |
|---|---|---|---|---|
| 1 | Python (production grade) | 17 | 94% | Must-have |
| 2 | Cloud security at depth (AWS, GCP, or Azure, at least one) | 16 | 89% | Must-have |
| 3 | LLM, RAG, or agent architecture knowledge | 13 | 72% | Must-have |
| 4 | Prompt injection familiarity (direct and indirect) | 13 | 72% | Must-have |
| 5 | Detection engineering or threat hunting basics | 12 | 67% | Must-have |
| 6 | Kubernetes or container security | 12 | 67% | Must-have |
| 7 | Threat modeling and secure design review | 11 | 61% | Must-have |
| 8 | Adversarial ML (data poisoning, model inversion, evasion) | 10 | 56% | Differentiator |
| 9 | Go (production) | 9 | 50% | Differentiator |
| 10 | CI or CD security tools (Snyk, Semgrep, GHA pipelines) | 9 | 50% | Differentiator |
| 11 | OWASP LLM Top 10 or MITRE ATLAS literacy | 8 | 44% | Differentiator |
| 12 | Red team or pentest background | 8 | 44% | Differentiator |
| 13 | Cloud-native vuln tools (Snyk, Wiz, TruffleHog, Endor Labs) | 7 | 39% | Differentiator |
| 14 | AI red team tools (Promptfoo, Garak, PyRIT, NeMo Guardrails) | 7 | 39% | Differentiator |
| 15 | MCP or agent protocol security awareness | 7 | 39% | Differentiator |
| 16 | Detection content (YARA, Sigma, Snort, Suricata) | 6 | 33% | Differentiator |
| 17 | AI governance (NIST AI RMF, ISO 42001, EU AI Act) | 6 | 33% | Differentiator |
| 18 | Vector DBs (FAISS, Pinecone, Weaviate, OpenSearch) | 6 | 33% | Differentiator |
| 19 | LLM orchestration (LangChain, LangGraph, AutoGen, CrewAI) | 5 | 28% | Differentiator |
| 20 | Bug bounty or CVE disclosure track record | 5 | 28% | Differentiator |
| 21 | Vulnerability scoring frameworks (CVSS, EPSS, CISA KEV) | 5 | 28% | Differentiator |
| 22 | Terraform or IaC security | 4 | 22% | Differentiator |
| 23 | SIEM tooling (Splunk, KQL, Elastic) | 4 | 22% | Differentiator |
| 24 | Multi-turn or chained jailbreak attack design | 4 | 22% | Differentiator |
| 25 | Burp Suite or Web app pentest tools | 3 | 17% | Below threshold |
| 26 | Rust | 3 | 17% | Below threshold |
| 27 | DoD 8570 cert (IAT II or higher, only fed contractor) | 1 | 6% | Vertical specific |
| 28 | Pacu (AWS pentest tool) | 0 | 0% | Not surfaced |

## Tool families with explicit JD evidence

These are skills the candidate should be able to demonstrate hands-on, not just describe:

| Tool family | JDs naming a specific tool | Specific tools called out |
|---|---|---|
| AI red team scanners | 7 | Garak, Promptfoo, PyRIT, custom LLM eval harnesses |
| LLM guardrails | 5 | NeMo Guardrails, Guardrails AI, Lakera Guard |
| Cloud or SCA vuln | 7 | Snyk, Wiz, Semgrep, Endor Labs, TruffleHog |
| Agent frameworks | 5 | LangChain, LangGraph, AutoGen, CrewAI |
| Vector DBs | 6 | FAISS, Pinecone, Weaviate, OpenSearch, Chroma |
| Observability | 3 | LangFuse, OpenTelemetry, Datadog |
| Detection languages | 6 | YARA, Sigma, Snort, Suricata, KQL, SQL |

## Read-out for QC

Anything in the candidate curriculum that does not map to a Tier A skill is a deferred priority. Tier A coverage is non-negotiable. Specifically:

1. Python is at 94%. If the curriculum does not include a Python-heavy module with security tooling output (parsers, eval harnesses, detection scripts), it will fail the bar.
2. Cloud security at 89%. If the curriculum is single-cloud, that is fine, but it must go deep on at least one. AWS is the most common single-cloud requirement in this sample.
3. LLM and agent architecture at 72%. Reading the OWASP LLM Top 10 is the entry-level signal. Building a RAG plus agent app and breaking it is the senior signal.
4. Prompt injection at 72%. The candidate must be able to describe direct, indirect, and tool-mediated prompt injection variants and demonstrate at least one mitigation pattern (structured queries, separators, output validation).
5. Detection engineering at 67%. Even AI roles want detection literacy because most of these companies treat AI security as an extension of D and R, not a separate org.

If the curriculum hits Tier A and at least four Tier B clusters, the candidate is interview-ready against the median JD in this sample. The current sample median JD has 6 Tier A skills and 4 to 5 Tier B skills called out as "required" or "must have" without splitting hairs about preferred versus required.

## Sources

Aggregated from the 25 JDs cited in JD-FREQUENCY-ANALYSIS.md in the same directory. Direct URLs are listed there.

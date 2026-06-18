# Tool Versions 2026 — AI Security Engineer Toolkit

Verified versions and install commands as of 2026-05-08. Re-verify before claiming "current" in any interview or resume context. Marked [UNVERIFIED] where exact versions could not be confirmed in the same session as this writeup.

Convention: each tool lists current version, what it does in one line, install command, and verification stamp.

---

## LLM and AI Security Tooling

### Garak — NVIDIA's LLM vulnerability scanner
- Latest: v0.14.1 (April 2026)
- License: Apache 2.0
- What: 37+ probe modules covering prompt injection, jailbreaks, encoding bypasses, data leakage, package hallucination, toxicity. Generators support OpenAI, Hugging Face, AWS Bedrock, Mistral, Ollama, NVIDIA NIM, custom REST.
- Install: `pip install garak` (or `pipx install garak`)
- Repo: https://github.com/NVIDIA/garak
- Verified: 2026-05-08

### Promptfoo
- Latest: 0.1.4 Python wrapper (April 2026); npm package versioned independently, ships weekly
- What: Prompt and agent eval, red-teaming, RAG and pipeline vuln scanning. Used by OpenAI and Anthropic per project README.
- Install (any of):
  - `npm install -g promptfoo`
  - `brew install promptfoo`
  - `pip install promptfoo`
  - `npx promptfoo@latest` (no install)
- Requires Node.js 20.20+ or 22.22+
- URL: https://www.promptfoo.dev/
- Verified: 2026-05-08

### NVIDIA NeMo Guardrails
- Latest: v0.20.0 (January 2026)
- What: Programmable guardrails for LLM-based conversational systems. v0.20 adds LangChain 1.x compatibility, BotThinking events for guarding reasoning traces, YARA-based code-injection output filter, Python 3.13 support.
- Requires Python 3.10–3.13
- Install: `pip install nemoguardrails`
- Repo: https://github.com/NVIDIA-NeMo/Guardrails
- Verified: 2026-05-08

### Lakera Guard
- Status: Acquired by Check Point September 2025; integrated into Check Point Infinity Platform, CloudGuard WAF, GenAI Protect
- What: Runtime prompt-injection, jailbreak, and data-leak protection API. 98%+ detection, sub-50ms latency, 100+ languages, 1M+ tx/app/day.
- Suite: Lakera Guard, Lakera Red (automated AI red-teaming), Lakera PII Detection
- URL: https://www.lakera.ai/lakera-guard | Docs: https://docs.lakera.ai/guard
- Verified: 2026-05-08

---

## Cloud Security Tooling

### Pacu — Rhino Security Labs AWS exploitation framework
- Latest: [UNVERIFIED specific tag]; project actively maintained on GitHub, requires Python 3.7+
- What: Modular AWS post-exploitation framework. IAM privesc, Lambda backdoor, S3 misconfig discovery, CloudTrail/GuardDuty disruption.
- Install:
  ```
  git clone https://github.com/RhinoSecurityLabs/pacu.git
  cd pacu && pip3 install -r requirements.txt
  python3 pacu.py
  ```
- Repo: https://github.com/RhinoSecurityLabs/pacu
- Verified link: 2026-05-08

### ScoutSuite — NCC Group multi-cloud auditor
- Latest: 5.13.0 last documented release [UNVERIFIED if newer minor exists; release cadence is slow, check repo]
- What: Multi-cloud security posture audit (AWS, Azure, GCP, Aliyun, Oracle Cloud).
- Install: `pip install scoutsuite`
- Repo: https://github.com/nccgroup/ScoutSuite
- Verified: 2026-05-08

### Prowler v5
- Latest: 5.25.1 (2026-04-29)
- What: AWS, Azure, GCP, Kubernetes, M365 CSPM. Maps findings to CIS, HIPAA, PCI, FedRAMP, ISO 27001, NIST 800-53, ENS, MITRE ATT&CK, AWS Foundational Security Best Practices.
- Install:
  - `pip install prowler` (open-source)
  - `brew install prowler`
- Repo: https://github.com/prowler-cloud/prowler
- Verified: 2026-05-08

### CloudSploit
- Status: Owned by Aqua Security, open-source repo at https://github.com/aquasecurity/cloudsploit. Active but slower cadence than Prowler.
- What: Multi-cloud configuration scanner, similar coverage to ScoutSuite/Prowler. AWS focus.
- Install: clone repo, `npm install`, run `node index.js`
- Verified link: 2026-05-08

---

## SCA, SAST, and Container Security

### Trivy (Aqua Security)
- Latest: v0.70.0 (2026-04-17)
- What: Vulnerability + misconfiguration + secrets + SBOM scanner for containers, K8s, code repos, IaC, cloud. The default open-source choice.
- IMPORTANT: A malicious release v0.69.4 was published 2026-03-19 by a threat actor; aquasecurity/setup-trivy and trivy-action GitHub Actions were also compromised in the same incident. Always pin by digest and verify signatures.
- Install:
  - `brew install trivy`
  - `apt-get install trivy` (after adding aquasec apt repo)
  - Docker: `docker pull aquasec/trivy:0.70.0` (verify signature)
- Repo: https://github.com/aquasecurity/trivy
- Verified: 2026-05-08

### Semgrep
- Latest: 1.162.0 (2026-05-07)
- What: Lightweight static analysis, pattern-based, multi-language. Pro tier adds AI-powered IDOR / broken-authz detection (beta), Autofix beta, Cursor and Claude Code plugins, PowerShell support.
- Install:
  - `brew install semgrep`
  - `python3 -m pip install semgrep`
  - Docker: `docker run returntocorp/semgrep`
- Repo: https://github.com/semgrep/semgrep
- Verified: 2026-05-08

### Snyk (Open Source / Code / Container / IaC)
- Pricing as of 2026: Free tier ($0, unlimited contributors, 200 SCA tests/mo, 100 SAST tests/mo on private repos, unlimited tests on public/OSS), Team $25/dev/mo (capped at 10 licenses/org), Ignite (10–50 devs), Enterprise custom. Platform Credit Consumption licensing model added 2026-01-01.
- What: Commercial SCA + SAST + container + IaC + cloud. Integrated CI/CD scanning.
- Install: `npm install -g snyk` then `snyk auth`
- URL: https://snyk.io/plans/
- Verified: 2026-05-08

---

## Web Pentest Tooling

### Burp Suite Professional / Community
- Latest: 2026.3.3 (Spring 2026)
- What: Industry-standard web app proxy and pentest IDE. 2026.3.x series adds custom CA cert support in-app, host-level SOCKS bypass, hide decoded hover tooltips, Organizer collections with secure sharing, split request/response in Intruder, Proxy search.
- Install: download from https://portswigger.net/burp/releases
- Verified: 2026-05-08

### OWASP ZAP (now "ZAP by Checkmarx")
- Latest weekly: ZAP_WEEKLY_D-2026-04-27 (2026-04-27); stable 2.17.0 series ongoing
- What: Free open-source DAST proxy and scanner. 2026 milestones include new ZAP MCP Server (AI assistants drive scans via MCP) and OWASP PTK browser add-on for combined DAST/IAST/SAST/SCA.
- Install:
  - `brew install --cask zap`
  - apt: `apt install zaproxy`
  - Docker: `docker pull zaproxy/zap-stable`
- URL: https://www.zaproxy.org/
- Verified: 2026-05-08

---

## Detection, IDS/IPS, and SIEM Content

### Sigma + pySigma + sigma-cli
- pySigma: actively maintained, last updated late March 2026. [UNVERIFIED exact pinned version, check PyPI]
- What: Generic signature format for SIEM detections. pySigma is the modern toolchain; sigmac is legacy.
- Install: `pip install pysigma sigma-cli`
- Backends: `pip install pysigma-backend-elasticsearch`, `pysigma-backend-splunk`, etc.
- Repo: https://github.com/SigmaHQ/pySigma
- Verified: 2026-05-08

### Falco
- Latest: 0.43.1 (2026-04-09)
- What: CNCF graduated runtime threat detection for hosts and containers. eBPF or kernel module probes. Used in production at scale.
- Install:
  - `helm install falco falcosecurity/falco`
  - `apt install falco`
- Repo: https://github.com/falcosecurity/falco
- Verified: 2026-05-08

### Wazuh
- Latest: 4.14.5 (2026-04-23)
- What: Open-source SIEM/XDR with HIDS, FIM, vuln scanning, log analysis. Free at any scale.
- Install: full guide at documentation.wazuh.com (apt/yum repo for manager + agents)
- URL: https://documentation.wazuh.com/current/release-notes/release-4-14-5.html
- Verified: 2026-05-08

### Suricata
- Latest stable: 8.0.4 (2026-03-17, updated 2026-04-02); also 7.0.15 LTS active
- What: High-perf network IDS/IPS/NSM. Multi-threaded, EVE-JSON output, integrates with Wazuh, Elastic, Zeek.
- Install: `apt install suricata` (after OISF PPA) or build from source
- URL: https://suricata.io/
- Verified: 2026-05-08

---

## AI Application Stack (the things you build with)

### LangChain
- Latest major: 1.0 (released October 2025), 1.x series ongoing; commitment to no breaking changes until 2.0
- What: LLM application framework. Prefer LangGraph for production agents; LangChain core for retrievers, prompt templates, integrations.
- Install: `pip install -U langchain` and the per-provider extras you need (`langchain-openai`, `langchain-anthropic`)
- URL: https://changelog.langchain.com/
- Verified: 2026-05-08

### LangGraph
- Latest: 1.1.10 (May 2026, 1.1.x series); 1.0 GA was October 2025
- What: Durable, stateful agent runtime. Type-safe streaming and invoke, Pydantic and dataclass coercion, used in production at Uber, LinkedIn, Klarna.
- Install: `pip install -U langgraph`
- Repo: https://github.com/langchain-ai/langgraph
- Verified: 2026-05-08

### Anthropic Python SDK
- Latest: 0.100.0 (2026-05-06)
- Requires Python 3.9+
- Install: `pip install anthropic`
- Repo: https://github.com/anthropics/anthropic-sdk-python
- Verified: 2026-05-08

### Pydantic v2
- Latest: 2.13.4 (2026-05-06)
- What: Data validation library. Foundation of LangChain, FastAPI, the Anthropic SDK Tools API. Knowing v2 vs v1 differences (model_validate, model_dump, ConfigDict) is table stakes.
- Install: `pip install -U pydantic`
- URL: https://docs.pydantic.dev/
- Verified: 2026-05-08

---

## Quick "as of 2026-05-08" cheat sheet

| Tool | Pinned version |
|------|----------------|
| Garak | 0.14.1 |
| Promptfoo (py wrapper) | 0.1.4 |
| NeMo Guardrails | 0.20.0 |
| Prowler | 5.25.1 |
| Trivy | 0.70.0 (avoid 0.69.4, malicious) |
| Semgrep | 1.162.0 |
| Burp Suite | 2026.3.3 |
| OWASP ZAP weekly | 2026-04-27 |
| Falco | 0.43.1 |
| Wazuh | 4.14.5 |
| Suricata | 8.0.4 |
| LangChain | 1.0+ |
| LangGraph | 1.1.10 |
| Anthropic Python SDK | 0.100.0 |
| Pydantic | 2.13.4 |

Re-verify before quoting in interviews. AI security stack moves weekly.

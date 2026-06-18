# Technical Interview Prep: Cyber Resilience N8N Engineer @ Resilience

## COMPANY INTELLIGENCE

### Resilience (formerly Arceo.ai)
- **Founded:** 2016 by U.S. military intelligence veterans (Air Force cyber warfare, NSA, Pentagon DIUx)
- **CEO:** Vishaal "V8" Hariprasad -- Air Force Academy, Bronze Star, first cohort of cyber warfare officers
- **Chairman:** Raj Shah -- F-16 pilot, ran Pentagon's DIUx, co-founded Morta Security (acquired by Palo Alto Networks)
- **Valuation:** $650M+ (Series C 2021). Total funding ~$217-231M
- **Employees:** ~273
- **HQ:** San Francisco, offices in NY, Chicago, Baltimore, LA, Toronto, London
- **What they do:** Managing General Agent (MGA) for cyber insurance. They don't hold risk directly, they partner with Intact Financial Corporation and Lloyd's of London
- **Key differentiator:** They prevent losses, not just underwrite them. Risk Operations Center monitors threats across entire policyholder portfolio
- **Edge Solution:** For companies $300M-$10B revenue. Includes BAS (AttackIQ), risk quantification in dollars, remediation roadmaps. 98% of Edge clients avoided claims with incurred costs (2022-2024)
- **Recent:** MGA of the Year (Feb 2026), CrowdStrike+AWS partnership (Jul 2025), acquired BreachQuest (Feb 2024), doubled Lloyd's limits to $20M (Jul 2024)
- **AI stance:** Use traditional ML for risk quantification (not GenAI). View AI as emerging threat vector. March 2026 Risk Briefing: "From AI Safe to AI Resilient"
- **Key stats:** Avg ransomware claim $1.18M (up from $705K), 65% of extortion is data theft only, AI phishing 54% success vs 12% traditional

---

## INTERVIEWER PROFILES

### Chris Wheeler -- CISO (VP of Information Security)
- **LinkedIn:** linkedin.com/in/cwsec
- **Career:** Navy (at sea) -> US Intelligence Community -> Arbor Networks -> Resilience (early) -> Morgan Stanley (4.5 years, VP) -> Resilience (returned)
- **At Morgan Stanley:** Led SOAR program AND managed CIRT L3 senior analyst team
- **Published:** CSO Online bylines on budget strategy, Help Net Security and Security Magazine interviews
- **Philosophy:** Financial quantification over fear. "Loss exceedance curves" and "return on controls." Compliance is the floor, not the ceiling. Enable the business, don't block. Human in the loop is non-negotiable for AI.
- **Prediction:** "2026 will see the first meaningful breaches tied directly to AI -- not attacks assisted by AI, but incidents exploiting weaknesses created by AI adoption"
- **Management style:** Ops-proven (military, SOC, SOAR, C-suite). Mentors veterans. Data-driven. Business-aligned.
- **He'll ask about:** Operational depth (walk me through an incident), risk quantification (justify a $500K investment to a CFO), AI security (unique risks of LLMs in enterprise), compliance vs proactive security

### Paragi Shah -- Senior SecOps Engineer
- **LinkedIn:** linkedin.com/in/paragi-shah
- **Location:** Princeton, NJ
- **Career:** Trustwave (12 years, engineering manager + IC) -> Northwestern University (adjunct, Digital Forensics) -> Resilience (~9 months)
- **At Trustwave:** Modernized MSSP infrastructure, built scalable threat data ingestion pipelines, SOAR platforms, perimeter defense. REST API design for SIEM-NG platform.
- **March 2026 Risk Briefing:** Presented two incidents:
  1. Autonomous agent ran `DROP DATABASE` after being told 11 times not to
  2. Prompt injection in GitHub Copilot silently disabled user confirmations and exfiltrated code
- **Quote:** "This is not just a bug; it's unintended agency"
- **She'll ask about:** AI guardrails, SOAR design, threat data ingestion, prompt injection defense, automation workflow architecture, human-in-the-loop controls, REST API security

### Jason Wright -- Likely Staff Security Engineer
- **Best match:** Staff Security Engineer, M.Sc., CISSP. SecOps, SOAR, DFIR, PKI, DevSecOps, Threat Intel
- **Previously:** Senior Cybersecurity Engineer at Convera
- **Education:** M.Sc. Cybersecurity, University of Maryland Global Campus
- **Certs:** CISSP, SANS GIAC GCIH
- **He'll focus on:** Hands-on technical depth, SOAR, DFIR, detection and response tooling

### David Meese -- Director of Security and Risk Services (may not be in interview but manages the team)
- 25 years experience, CISSP/GCIH/GDSA, ex-Army EOD, NYU M.S. Cybersecurity

---

## N8N TECHNICAL DEEP DIVE

### Architecture
- **Engine:** TypeScript, workflow is a DAG of nodes, item-based data model (arrays of JSON objects)
- **Regular mode:** Single Node.js process handles webhooks, polls, and execution. Your setup.
- **Queue mode (enterprise):** Main instance handles webhooks/triggers/UI, workers pull from Redis/Bull queue. Scale workers horizontally.
- **DB:** PostgreSQL for production (workflow_entity, execution_entity, credentials_entity, workflow_history tables)
- **Critical lesson:** n8n 2.x uses workflow_history for runtime, not just workflow_entity. CLI import updates workflow_entity but runtime may load from workflow_history.

### Sub-Workflow Patterns
- Execute Workflow node calls child workflows
- Benefits: modular design, error isolation, shared logic, concurrency control
- Your master orchestrator: webhook -> Switch node -> route to 16 service handlers
- Pattern: enrichment chain, fan-out/fan-in, shared notification sub-workflows

### Webhook Security
- n8n supports: Header Auth, Basic Auth, JWT validation
- Your setup: bound to 127.0.0.1 only, all traffic via Cloudflare Tunnel (TLS 1.3, DDoS, rate limiting)
- Production hardening: HMAC signature validation, IP allowlisting at Cloudflare, input validation in first node
- Use "Respond to Webhook" node early to return 200 immediately, process async

### Credential Management
- AES-256-CBC encrypted with N8N_ENCRYPTION_KEY in PostgreSQL
- Exports strip credential values (only IDs remain) -- safe for git
- N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS=true prevents Code nodes from reading server env vars
- Enterprise: external secrets (Vault, AWS Secrets Manager)

### Error Handling
- Error Trigger Workflow: catches all unhandled failures globally
- Per-node retry with exponential backoff
- Error output branches for conditional handling
- Dead letter pattern: write failed payloads to PostgreSQL, reprocess on cron
- Principle: in security automation, silent failure is worse than no automation

### Deployment Patterns
- **Docker Compose (your setup):** PostgreSQL backend, healthchecks, resource limits, Cloudflare Tunnel
- **AWS Fargate:** ALB -> Fargate (n8n main) -> RDS PostgreSQL, ElastiCache Redis, Fargate workers
- **Kubernetes:** Deployment with 1 replica for main, scalable Deployment for workers, Redis for queue
- **Key:** Only ONE main instance handles webhooks/triggers (or use leader election)

### Version Control
- Export via CLI or REST API as JSON (credentials stripped)
- Store in git repo, same CI/CD pipeline (Gitleaks, Trivy, Semgrep)
- n8n 2.x has built-in source control feature (enterprise)
- For team: export-to-git with CI/CD validation, tag releases, staging instance for testing

### n8n vs Competitors
| | n8n | Tines | Cortex XSOAR | Splunk SOAR |
|---|---|---|---|---|
| **Price** | Free self-hosted | $$$ per action | $$$$ | $$$$ |
| **Open source** | Yes | No | No | No |
| **AI native** | Yes (Agent, chains, RAG) | Limited | Limited | Limited |
| **Integrations** | 400+ | 100+ | 700+ | 300+ |
| **Custom code** | Full JS/Python | JS | Python | Python |

### n8n Limitations
- No built-in case management (use TheHive/Jira)
- No pre-built security playbooks (build from scratch)
- Community edition lacks RBAC and SSO
- Single-threaded in regular mode (queue mode fixes this)

---

## GCP / AI PLATFORM SECURITY

### Vertex AI
- GCP's managed ML platform for building, training, deploying models
- Security controls: CMEK via Cloud KMS, VPC Service Controls, Private Service Connect
- IAM roles scoped to ML workflow stages (data scientist, trainer, deployer)
- Audit logging via aiplatform.googleapis.com (Admin Activity always on, Data Access must be enabled)
- Model Monitoring v2 (Preview): drift detection, feature attribution

### ModelArmor
- GCP service that screens LLM prompts/responses BEFORE/AFTER they reach the model
- Stateless (processes in memory, no persistent storage unless Cloud Logging enabled)
- **Five filters:** Responsible AI Safety, Prompt Injection/Jailbreak Detection, Sensitive Data Protection, Malicious URL Detection, CSAM (always on)
- **Configuration:** Templates define policies, Floor Settings set project-level minimums
- **Enforcement:** INSPECT_ONLY (monitor) or INSPECT_AND_BLOCK (prevent)
- **Key limitations:**
  - 4 MB max file size (content beyond is SILENTLY SKIPPED)
  - 10,000 token limit for prompt injection filter (beyond = EXECUTION_SKIPPED)
  - Only first 40 URLs scanned per request
  - Does NOT detect email/password without custom templates
  - PDF prompt injection in structure/metadata is an emerging gap
- **Vertex AI integration:** Enable floor settings, grant roles/modelarmor.user to Vertex SA
- **Blocked response:** `{"promptFeedback": {"blockReason": "MODEL_ARMOR"}}`

### Snowflake Cortex
- LLM functions built into Snowflake SQL (AI_COMPLETE, AI_CLASSIFY, AI_EXTRACT, etc.)
- Data never leaves Snowflake's governed environment
- RBAC: each model is a securable object, requires USE AI FUNCTIONS privilege
- Models allowlist: CORTEX_MODELS_ALLOWLIST parameter
- n8n integration: OpenAI-compatible API (use OpenAI Chat Model node, point Base URL to Cortex endpoint)
- Logging: CORTEX_FUNCTIONS_USAGE_HISTORY, CORTEX_FUNCTIONS_QUERY_USAGE_HISTORY

### Cloud Armor (GCP WAF)
- Attaches to External Application Load Balancer (not called "ALB" in GCP)
- WAF rules based on ModSecurity CRS 3.3
- Preconfigured OWASP Top 10 rules
- Adaptive Protection: ML-based anomaly detection, auto-generates WAF rules
- Rate limiting per IP, per header, per path

### GCP IAM with Terraform
- Use `google_project_iam_member` (safest, non-authoritative)
- Grant to Google Groups, not individual accounts
- Custom roles when predefined are too broad
- Never create service account keys; use Workload Identity Federation
- IAM conditions for temporary access

---

## JAMF & IDE SECURITY

### Jamf Configuration Distribution
- Configuration Profiles for security baselines (FileVault, firewall, Gatekeeper)
- Deploy CrowdStrike Falcon: Configuration Profile for Full Disk Access + Policy for .pkg deployment
- Deploy Zscaler: Upload .pkg, create Configuration Profile with PLIST for parameters
- GenAI guardrails: push .cursorrules, CLAUDE.md, copilot-instructions.md as managed preferences
- Jamf Protect: native macOS endpoint security, MITRE ATT&CK mapping, telemetry to SIEMs

### AI IDE Security
**Claude Code:**
- 3 permission modes: Default (prompt), Auto (classifier), Plan (read-only)
- CLAUDE.md for project rules, settings.json for technical controls, managed-settings.json for org policy
- PreToolUse hooks for runtime policy enforcement
- CVEs: CVE-2025-59536 (RCE, 8.7), CVE-2026-21852 (key exfil, 5.3), CVE-2026-25725 (sandbox bypass)

**Cursor:**
- SOC 2 Type 2 certified, Privacy Mode (zero retention)
- CVEs: CVE-2025-54135 (MCP RCE, 8.6), CVE-2025-54136 (MCPoison, 7.2), CVE-2025-59944 (persistent RCE)
- Rules File Backdoor: hidden malicious instructions in .cursorrules

** GitHub Copilot **
- Enterprise: code excluded from training, IP indemnification
- CVEs: CVE-2025-62449 (path traversal, 6.8), CVE-2025-62453 (code injection, 5.0), CamoLeak (9.6)
- Stats: 35.8% of Copilot-generated code contains security weaknesses, 40% higher secret leakage rate

### MCP Security 
- Major vulns: prompt injection, tool poisoning, credential theft, supply chain
- Real incidents: Supabase/Cursor SQL injection, Postmark npm backdoor, Anthropic's mcp-server-git RCE chain
- 30+ CVEs filed against MCP servers in 60 days (Jan-Feb 2026)
- Best practices: SAST/SCA on build pipelines, sandboxed execution, least privilege, version pinning

### CrowdStrike ##
- Falcon MCP Server (public preview): detections, threat intel, MITRE reports, host management, CSPM, Spotlight, custom IOA, firewall rules
- Rate limit: 6,000 requests/minute per client ID
- FQL queries should be tested before production

### Zscaler ##
- MCP Server (preview): ZPA, ZIA, ZDX, ZCC, ZMS. 300+ tools
- Default read-only. Write ops require --enable-write-tools AND explicit allowlist
- HMAC-SHA256 confirmation tokens with 5-minute expiration for destructive actions
- Nine layers of defense-in-depth

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 25 TECHNICAL Q&A (SUMMARY)

### N8N Questions (1-10)
1. **Architect n8n for SecOps:** Docker Compose, PostgreSQL backend, 3 Docker networks (core/ai/monitoring), Cloudflare Tunnel, resource limits, N8N_RESTRICT_ENVIRONMENT_VARIABLES_ACCESS
2. **Error handling:** 3 layers -- global error handler, per-node retry with backoff, conditional error paths. Dead letter pattern for critical workflows
3. **Version control:** Export to JSON (creds stripped), git-track, CI/CD pipeline validates. n8n Enterprise has built-in git integration
4. **AI workload response playbook:** Webhook intake -> classification Switch -> 4 scenarios (injection/agency/exfil/supply chain) -> automated containment -> enrichment -> notification -> evidence preservation
5. **Secure webhooks:** Bind 127.0.0.1 only, Cloudflare Tunnel, Header Auth, rate limiting, input validation, IP allowlisting via Cloudflare Access
6. **Credential management:** AES-256-CBC encrypted, env var restriction, Vault integration planned, rotation workflow automation
7. **Testing:** Manual execution with test data, test fixtures, error path testing, credential verification, canary deployments
8. **SIEM integration:** Bidirectional -- SIEM webhook -> n8n for response, n8n HTTP Request -> SIEM for enrichment. Dedup alerts via PostgreSQL
9. **Sub-workflow architecture:** Shared logic, error isolation, reusability, concurrency control. Master orchestrator -> Switch -> sub-workflows
10. **Monitoring:** Docker healthcheck, Datadog metrics, API Health Check cron, Error Handler -> Telegram, Falco syscall monitoring

### GCP/AI Questions (11-15)
11. **Terraform for GCP IAM:** google_project_iam_member (safest), custom roles, OPA policy enforcement, Workload Identity Federation
12. **ModelArmor validation:** Terraform for drift detection, test suite of known-bad prompts, Cloud Audit Logs for config changes, red team validation
13. **Prompt injection detection:** Multi-layer (input pattern, output anomaly, behavioral monitoring, model-level guardrails). Response via n8n automation
14. **Model endpoint security:** Private VPC/network, IAM auth, rate limiting, ModelArmor, input/output filtering, supply chain verification (Cosign, SBOMs)
15. **Snowflake Cortex logging:** ACCESS_HISTORY, QUERY_HISTORY, prompt I/O audit table, SIEM export via Snowflake tasks, Cortex Alerts, credit monitoring

### Architecture Questions (16-20)
16. **GenAI guardrails:** Config as code (CLAUDE.md), Gitleaks in CI/CD, Doppler secrets, scope limitations, output monitoring via Semgrep
17. **Jamf distribution:** Configuration profiles for baselines, smart groups by role, compliance enforcement, update distribution, audit trail to SIEM
18. **Agentic IDE security:** Config lockdown (CLAUDE.md, settings.json), credential isolation (Doppler), scope containment, network controls, MCP security
19. **MCP monitoring:** Server inventory, network monitoring, permission auditing, I/O logging, version pinning, Falco for syscall detection
20. **Backtesting:** Historical attack replay, gap documentation in POA&M, automated regression testing (25 test cases), tabletop exercises

### General Security Questions (21-25)
21. **IR methodology:** NIST 800-61, 5 IR playbooks, Falco/Datadog/Teleport detection, containerized containment, evidence preservation
22. **Risk prioritization in AI:** NIST 800-30 5x5 matrix + AI dimensions (blast radius, data sensitivity, supply chain). Priority: LLM01 > LLM08 > LLM06 > LLM05
23. **Zero trust:** Cloudflare Tunnel (no open ports), Keycloak RBAC, Teleport JIT access with MFA, network segmentation, container hardening, Doppler secrets
24. **Productivity vs security:** Shift left (6 scanners in <3 min), policy as code (OPA), guardrails not gates, self-service secrets, transparent monitoring
25. **Frameworks:** NIST 800-53 (controls), AI RMF (AI governance), OWASP LLM Top 10 (threats), MITRE ATT&CK/ATLAS (adversary), ISO 42001 (AI management), CIS Docker (hardening), 800-30 (risk scoring)

---

## YOUR NUMBERS (KNOW COLD)

| Metric | Value |
|---|---|
| n8n production workflows | 14 |
| Master orchestrator services | 16 |
| Managed credential sets | 20+ |
| Webhook endpoints | 10+ |
| Gmail inboxes monitored | 4 |
| Manual ops reduction | ~80% |
| Falco alerts: before | 200+ daily |
| Falco alerts: after | 12 actionable |
| Red team vulns found | 8 across all skills |
| OWASP LLM categories addressed | LLM01, 02, 06, 07, 08 |
| CI/CD tools | Trivy, Semgrep, Gitleaks, OPA |
| Terraform files / resources | 16 files, 30+ resources |
| OPA/Rego policies | 8 |
| Containers in production | 13 + 1 standalone |
| GRC documents | 37 total |
| IR playbooks | 5 |
| Policies | 10 |
| IR runbook improvement | 8 hours -> 90 minutes |
| AD audit findings | 14 -> 2 |
| PCI devices managed | 45+ |
| SIEM detection improvement | 48 hours -> under 4 |
| Automation time saved | ~12 hours/week |
| VLANs created | 4 |
| Locations managed | 3 |

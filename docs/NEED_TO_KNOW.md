# Need to Know: Interview & Camera Readiness Guide

## Tier 1: Must Know Cold (Every Interview)

### OWASP LLM Top 10 (2025)
1. LLM01: Prompt Injection (direct vs indirect)
2. LLM02: Insecure Output Handling
3. LLM03: Training Data Poisoning
4. LLM04: Model Denial of Service
5. LLM05: Supply Chain Vulnerabilities
6. LLM06: Sensitive Information Disclosure
7. LLM07: Insecure Plugin Design
8. LLM08: Excessive Agency
9. LLM09: Overreliance
10. LLM10: Model Theft

Your answer: "In my production stack, I mitigate prompt injection through input validation on the OpenClaw gateway, output filtering before SOAR workflow triggers, and behavioral monitoring through Falco eBPF runtime detection."

### OWASP Top 10 Web (2021)
- A01: Broken Access Control (IDOR, privilege escalation)
- A02: Cryptographic Failures (weak TLS, cleartext storage)
- A03: Injection (SQLi, NoSQLi, OS command, LDAP)
- A04: Insecure Design (threat modeling gaps)
- A05: Security Misconfiguration (default creds, open cloud storage)
- A06: Vulnerable and Outdated Components (unpatched libraries)
- A07: Identification and Authentication Failures (broken auth, session management)
- A08: Software and Data Integrity Failures (unsigned updates, CI/CD compromise)
- A09: Security Logging and Monitoring Failures (no alerts, no audit trail)
- A10: Server-Side Request Forgery (SSRF)

Key concepts:
- Reflected vs Stored vs DOM-based XSS
- Parameterized queries vs string concatenation (why SQLi works)
- What a WAF catches vs what it misses (WAF catches known patterns, misses logic flaws)

### API Security (OWASP API Security Top 10)
- BOLA/IDOR (Broken Object Level Authorization): user A accesses user B's data by changing an ID
- Broken Authentication: weak tokens, no expiration, no rotation
- Excessive Data Exposure: API returns more data than the client needs
- Rate Limiting: preventing brute force and enumeration
- JWT validation: signature verification, expiration checks, algorithm confusion attacks
- OAuth 2.0: authorization code flow vs implicit flow, why implicit is deprecated

Your answer: "My n8n webhooks use authentication tokens, rate limiting, and I restrict which actions each webhook can trigger. The master orchestrator validates action types before execution."

---

## Tier 2: Should Know Well (Differentiates You)

### Prompt Engineering for Defense
- System prompt hardening: clear boundaries, role definition, output constraints
- Guardrails: input classifiers that detect injection attempts before they reach the model
- Output classifiers: check model output for PII, credentials, or harmful content before returning
- Constitutional AI: training models to follow rules by having them critique their own outputs
- Red teaming LLMs: systematic adversarial testing (encoding bypass, context manipulation, multi-turn attacks)

Your answer: "I approach AI security the same way I approach infrastructure security. Define the trust boundary, enumerate the attack surface, implement controls at each boundary, and monitor for anomalies."

### Supply Chain Security
- SBOMs (Software Bill of Materials): what's in your container images (you use Syft)
- Image signing (you use Cosign): cryptographic proof that the image wasn't tampered with
- SLSA levels: 1 = documented build, 2 = hosted build, 3 = hardened build, 4 = hermetic build
- SCA vs SAST vs DAST:
  - SCA (Software Composition Analysis): scans dependencies for known CVEs (Trivy)
  - SAST (Static Application Security Testing): scans source code for vulnerabilities (Semgrep)
  - DAST (Dynamic Application Security Testing): scans running application from outside (ZAP, Burp)

Your answer: "In my CI/CD pipeline, Trivy handles SCA at the container level, Semgrep handles SAST on the code, Gitleaks prevents secret leaks, and Cosign signs every image. OPA policies gate the deployment."

### Cloud Security Architecture
- Shared responsibility model: cloud provider secures the infrastructure, you secure everything on top
- IAM: least privilege, no long-lived credentials, service accounts scoped per service
- Network: VPCs, subnets, security groups (stateful) vs NACLs (stateless)
- Your story: "I migrated from AWS EC2 to DigitalOcean, cutting costs 65%. The architecture is cloud-agnostic because everything runs in Docker Compose with Terraform IaC. I can redeploy to any provider."

---

## Tier 3: Good to Reference (Shows Breadth)

### Zero Trust (NIST SP 800-207)
7 tenets: never trust, always verify. Your implementation:
- Cloudflare Tunnel = no exposed ports (verify network)
- Keycloak = verify identity (3-tier RBAC)
- Teleport = verify access (JIT, session recording)
- Vault = verify secrets (dynamic, auto-rotate)
- Falco = verify behavior (runtime detection)

### MITRE ATT&CK + ATLAS
- ATT&CK = traditional adversary TTPs (14 tactics from recon to impact)
- ATLAS = AI/ML specific adversary TTPs (data poisoning, model evasion, inference attacks)
- Walk through one: "Initial Access via prompt injection (T1190/AML.T0051) leads to Execution through tool-use skill chaining, Discovery through GitHub repo enumeration, and Impact through unauthorized SOAR workflow triggers."

### Incident Response (NIST SP 800-61)
6 phases: Preparation, Detection, Containment, Eradication, Recovery, Lessons Learned
Your IR story: "Falco detects a syscall anomaly in the n8n container. Falcosidekick routes the alert to Datadog and Telegram in under 30 seconds. I assess if the container is internet-facing. If yes, network disconnect immediately. Capture forensic snapshot. Rebuild from clean image. Rotate exposed secrets via Vault. Post-incident review within 48 hours. Update detection rules."

---

## 5 Questions to Practice on Camera (60 seconds each)

1. "What is prompt injection and why does it matter?"
   Hook: It's the SQL injection of AI systems. Direct injection manipulates the model through user input. Indirect injection poisons the context through fetched content. In my stack, I defend against both with input validation, output filtering, and behavioral monitoring.

2. "How do you secure an AI agent that has tool-use capabilities?"
   Hook: The attack surface is multiplicative, not additive. 6 skills times 16 integrations equals 96 potential chain paths. I use skill allowlisting, output validation before workflow triggers, air-gapped AI networks, and Falco runtime detection for behavioral anomalies.

3. "Walk me through your incident response process"
   Hook: Detection to alert in under 30 seconds. Falco eBPF catches the syscall anomaly, Falcosidekick routes to Datadog and Telegram, I assess blast radius, isolate if internet-facing, forensic capture before remediation, rebuild from clean image, rotate secrets, post-incident review, update detection rules.

4. "What's the difference between SAST, DAST, and SCA?"
   Hook: SAST reads the code (Semgrep), DAST attacks the running app (ZAP/Burp), SCA checks your dependencies (Trivy). I run all three in CI/CD. SAST and SCA block the PR. DAST runs on staging. Together they catch code bugs, known CVEs, and runtime vulnerabilities.

5. "How do you implement zero trust in a containerized environment?"
   Hook: Zero exposed ports via Cloudflare Tunnel. Three isolated Docker networks so AI models can't reach the internet. Keycloak for identity with 3-tier RBAC. Teleport for JIT SSH access with session recording. Vault for dynamic secrets that auto-rotate. Falco for runtime behavior monitoring at the kernel level.

---

## The Golden Rule for Every Answer
Never explain in abstract. Always say: "In my environment, I did X because Y."

This connects theory to practice and proves you're not just reciting definitions.

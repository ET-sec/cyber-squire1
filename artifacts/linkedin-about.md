AI Security Engineer running a working AI Security Operations Center (SOC) on real infrastructure. Built Squire, a LangGraph agent with human in loop approval gates that cut Datadog alert triage by 80 percent. Sitting for the Certified Information Systems Security Professional (CISSP) exam this month.

CoreDirective is my AI security practice in Atlanta. The stack below runs in production.

What it does:
. Falco eBPF runtime detection tuned to MITRE ATT&CK container tactics. Cut Datadog alerts from 200+ to 12 daily.
. 6 n8n Security Orchestration, Automation, and Response (SOAR) workflows running Claude-backed triage across 16 services.
. Squire AI SOC analyst on LangGraph with NeMo Guardrails, GLiNER Personally Identifiable Information (PII) redaction, Langfuse tracing, pgvector Retrieval Augmented Generation (RAG). Freed senior triage hours on baseline alert volume.
. Zero Trust perimeter via Cloudflare Web Application Firewall (WAF) and mutual TLS (mTLS) tunnels. Zero public ingress.
. Teleport Just In Time Privileged Access Management (JIT PAM) with session recording, Keycloak Single Sign On (SSO). Standing admin eliminated.
. 19 Terraform files, 30+ resources across AWS, DigitalOcean, Cloudflare. 8 Open Policy Agent (OPA) Rego gates enforce KMS encryption, key rotation, least privilege, and zero public ingress.

What it runs:
. 18 containers: PostgreSQL, n8n, Falco, Teleport, Keycloak SSO, HashiCorp Vault, Ollama, OpenClaw AI gateway on Claude Opus 4.7, Cloudflare Tunnel, Datadog, Langfuse.
. Shift left Continuous Integration and Continuous Deployment (CI/CD): Trivy, Semgrep, Gitleaks, OPA Conftest, Cosign, Syft Software Bill of Materials (SBOM), OWASP ZAP Dynamic Application Security Testing (DAST). Unsigned images blocked at the registry.

GRC: 54 sanitized documents covering 169 NIST 800-53 controls across the main System Security Plan (SSP) and Squire AI SSP. Frameworks: NIST 800-53, HIPAA, SOC 2, ISO 27001, NIST AI Risk Management Framework (RMF), ISO 42001, FedRAMP Moderate. 5 Incident Response (IR) playbooks with a Promptfoo eval harness.

Prior: 4 years IT Security and Operations Manager at Texaco, Atlanta, GA. Splunk Security Information and Event Management (SIEM), PCI DSS audits, Active Directory hardening, 4 VLAN segmentation, Python and PowerShell automation.

Certs: CISSP (in progress, May 2026), SecurityX (CASP+), DoD 8140, SSCP, CCNA, Security+. Eligible for Security Clearance.
Education: BBA in Computer Information Systems (Cybersecurity) and BBA in Business Economics, Georgia State University. GPA 3.7, Dean's List, May 2026.

<!-- generated: 2026-05-25T10:31:08Z -->
<!-- source-sha256: 9005439cd33dd0c8cfd648a531ec72ecccd93c22383aefe1914dfda4c1c2d76d -->
<!-- generator: render-artifacts.py v0.1.0 -->
<!-- git-rev: 2756d3f -->

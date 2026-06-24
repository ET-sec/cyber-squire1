# Security Policy

This repository hosts security tooling, GRC documentation, and agentic AI infrastructure. Security reports are taken seriously.

## Supported versions

| Component | Supported |
|---|---|
| Latest commit on `main` | Yes |
| Tagged releases | Yes (latest two) |
| Other branches | Best effort |

## Reporting a vulnerability

**Do not open a public issue for security vulnerabilities.** Use one of the following private channels:

- **Email**: `security@tigouetheory.com`
- **GitHub Private Vulnerability Reporting**: https://github.com/ET-sec/cyber-squire1/security/advisories/new

Include:
- A description of the vulnerability
- Steps to reproduce
- Impact assessment (data exposure, privilege escalation, denial of service, etc.)
- Suggested remediation if you have one
- Whether you intend to publish disclosure and on what timeline

## Response targets

| Severity | Acknowledge | Initial assessment | Fix or mitigation |
|---|---|---|---|
| Critical | 24 hours | 48 hours | 7 days |
| High | 72 hours | 7 days | 30 days |
| Medium | 7 days | 14 days | 90 days |
| Low | 14 days | 30 days | next scheduled release |

Severity is assessed using CVSS 3.1 base scoring.

## Scope

In scope:
- Code in this repository
- CI/CD workflows in `.github/workflows/`
- Container images built from this repository
- Documentation that could mislead operators into insecure configurations

Out of scope:
- Third-party services referenced in the documentation (Doppler, Cloudflare, DigitalOcean, Anthropic, etc.), report to those vendors directly
- Vulnerabilities in upstream dependencies, please report to upstream first, then notify us if not addressed
- Social engineering, physical attacks, or denial of service through resource exhaustion of free-tier services

## Disclosure

We follow a 90-day coordinated disclosure timeline by default. Earlier disclosure can be negotiated if a fix is shipped sooner.

## Security tooling in this repository

For transparency, the following automated scans run on this repository:

- **Trivy** (container and dependency scanning)
- **Semgrep** (static analysis)
- **Gitleaks** (secret detection)
- **Checkov** (Terraform and IaC scanning)
- **OPA / Rego** (policy-as-code gates)
- **Cosign** (container image signing via Sigstore keyless OIDC)
- **DAST via OWASP ZAP** (dynamic application security testing on n8n endpoints)
- **Promptfoo + custom red-team suite** (AI guardrail testing on the Squire agent)

Results from these scans inform the POA&M maintained at `docs/grc/POAM_PLAN_OF_ACTION.md`.

## AI / agent security

This repository operates AI agents. Specific AI security guarantees:

- All LLM calls route through a controlled gateway (OpenClaw) with logging
- Human-in-the-loop policy at `docs/grc/HITL_POLICY.md`
- AI Governance policy at `docs/grc/POLICY_AI_GOVERNANCE.md`
- Threat model with MITRE ATLAS mappings at `docs/grc/SQUIRE_THREAT_MODEL.md`
- Red team results at `docs/grc/REDTEAM_RESULTS.md`
- AI incident playbook at `docs/grc/PLAYBOOK_AI_INCIDENT.md`

If you discover a prompt injection, jailbreak, model exfiltration, or other AI-specific vulnerability, please follow the reporting process above. Include the prompt or scenario that triggered the issue.

## Hall of fame

Security researchers who responsibly disclose vulnerabilities will be credited here with their permission.

_(Empty as of 2026-06-24)_

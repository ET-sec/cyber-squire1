# QGenda Technical Study List

**Goal:** Be panel-ready inside 7 days. Cover the AWS-native gaps without faking depth.

## GREEN ZONE (real, ready to demo)
- DevSecOps pipeline: Trivy, Semgrep, Gitleaks, Cosign, Syft SBOM, OPA Gatekeeper
- GRC: NIST 800-53, NIST AI RMF, ISO 27001, ISO 42001, SOC 2, HIPAA Security Rule
- Threat modeling: STRIDE, OWASP LLM Top 10, MITRE ATLAS, MITRE ATT&CK containers
- Runtime: Falco eBPF, Datadog, Cloudflare WAF + Zero Trust
- IaC: Terraform + OPA/Rego policy gates
- IAM: Active Directory, Keycloak SSO, Teleport JIT PAM
- Vuln management lifecycle: Nessus authenticated scans, CVSS triage, risk-based SLAs (PCI scope)

## YELLOW ZONE (used, not at scale — study before panel)

### MUST KNOW (cover in 4 hrs)
1. **AWS Security Hub + GuardDuty + Inspector + Config** — finding aggregation, suppression, auto-remediation via EventBridge + Lambda. Read AWS Security Reference Architecture (SRA) chapter on multi-account.
   - Time: 90 min
   - Resource: https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html
2. **AWS Organizations + SCPs + Control Tower** — delegated admin, centralized logging, account factory.
   - Time: 60 min
   - Resource: AWS Well-Architected Security pillar, Organizations chapter
3. **KMS key policies + grants + rotation** — multi-account KMS, envelope encryption, BYOK vs AWS-managed.
   - Time: 45 min
4. **HIPAA Security Rule technical safeguards** — access control, audit, integrity, transmission. Map each to AWS services.
   - Time: 45 min
   - Resource: HHS HIPAA Security Rule guidance + AWS HIPAA whitepaper

### HIGH PROBABILITY (cover in 3 hrs)
5. **CNAPP landscape** — Wiz vs Sysdig vs Orca vs Lacework. Know the agentless inventory model, posture vs runtime, attack path graphs.
   - Time: 60 min
   - Resource: Wiz "Cloud Security 101" + Gartner CNAPP report summary
6. **Container security depth** — Docker daemon hardening, K8s admission, Pod Security Standards, image signing, distroless.
   - Time: 60 min
7. **Vulnerability management at SaaS scale** — Qualys, Tenable, Rapid7. SLA bands, exception workflow, risk acceptance.
   - Time: 30 min
8. **SOC 2 Type II evidence work** — control families CC1-CC9, common evidence asks, drift between policy and reality.
   - Time: 30 min

### NICE TO HAVE (cover in 2 hrs)
9. **FedRAMP moderate** — 17 control families, 3PAO process, ATO timeline, GovCloud vs commercial.
   - Time: 30 min
10. **Generative AI on AWS** — Bedrock Guardrails (already in skills line), agent governance, customer data isolation.
    - Time: 30 min
11. **AWS Lambda + EventBridge auto-remediation patterns** — common SecHub finding -> Lambda fix loop.
    - Time: 30 min
12. **Healthcare SaaS context** — provider scheduling, on-call rotations, credentialing. Why PHI exposure matters.
    - Time: 30 min

## RED ZONE (skip, do not bluff)
- Wiz / Sysdig / Orca / Lacework hands-on — you have not deployed any of these. If asked, say you have evaluated CNAPP solutions and know the model, not the UI.
- Splunk Enterprise Security — Texaco was vanilla Splunk, not ES. If they probe, say so.
- AWS Security Specialty cert content beyond what overlaps with the role.

## Total time budget
- Green zone: 0 hrs (already ready)
- Yellow MUST: 4 hrs
- Yellow HIGH: 3 hrs
- Yellow NICE: 2 hrs
- **Total: 9 hrs over 7 days = 75 min/day**

## Drill: write a 1-page threat model

Build a STRIDE + LINDDUN model for a fake "QGenda-style" healthcare scheduling API: provider auth (OAuth + MFA), PHI lookup endpoint, multi-tenant AWS, Aurora PostgreSQL backend, S3 for documents. Walk in with this on day one of the technical screen. No mid-level candidate does this.

Time: 90 min. Worth more than any cert.

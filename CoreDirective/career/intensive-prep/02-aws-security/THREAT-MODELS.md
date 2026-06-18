---
document_id: TM-AWS-001
title: AWS Architecture Threat Models - STRIDE + MITRE ATLAS
doc_type: threat_model
classification: PREP-INTERNAL
version: "1.0"
last_updated: 2026-05-08
owner: Emmanuel Tigoue (interview prep)
review_cadence: Update as new pipeline roles emerge
frameworks:
  - STRIDE
  - MITRE ATLAS (AML.T codes 2026-04 release)
  - AWS Well-Architected Security Pillar
related:
  - ROADMAP.md
  - INTERVIEW-Qs.md
  - CHEATSHEET.md
  - labs/
---

# AWS Architecture Threat Models

Six common architectures, threat-modeled the same way. STRIDE per component, plus MITRE ATLAS where adversarial ML applies. Each model has assets, trust boundaries, threats, mitigations, residual risk.

**Use this in interviews:** when asked "how would you secure X", pick the closest model and walk through it.

---

## TM-1: Public web app on EC2 behind ALB

### Architecture

```
Internet
   |
   v
[CloudFront] (optional CDN, OAC to ALB)
   |
   v
[WAF on ALB]
   |
   v
[ALB] (public subnet, AZ-redundant)
   |
   v
[EC2 ASG] (private subnet, AZ-redundant)
   |
   v
[RDS Multi-AZ] (isolated subnet)

Logging: ALB access logs -> S3 (log archive acct)
         EC2 OS logs -> CloudWatch
         CloudTrail -> S3 (log archive acct)
         VPC Flow -> S3 (log archive acct)
         GuardDuty -> SecurityHub
```

### Assets
- Application code on EC2
- User data in RDS (PII, credentials)
- TLS private keys (ACM-managed)
- IAM role for EC2 (S3 read for app config, KMS decrypt)

### Trust boundaries
- Internet to CloudFront/ALB
- ALB to EC2 (within VPC)
- EC2 to RDS (within VPC)
- EC2 to AWS APIs (via VPC endpoints)

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| ALB | Spoofing | Forged Host header | ALB listener rules + WAF host validation | LOW |
| ALB | Tampering | TLS downgrade | ALB security policy ELBSecurityPolicy-TLS13-1-2 | LOW |
| ALB | Information disclosure | Verbose errors | ALB redirect on 5xx, custom error pages | LOW |
| ALB | DoS | Layer 7 flood | WAF rate-based rules, Shield Standard, optional CloudFront | LOW |
| EC2 | Spoofing | IMDS theft via SSRF | IMDSv2 required, hop limit 1, account-level enforcement | LOW |
| EC2 | Tampering | Drift on instance | Immutable AMIs, ASG replace on policy update, Config drift detection | LOW |
| EC2 | Repudiation | Action without log | OS audit log to CloudWatch Agent, CloudTrail | LOW |
| EC2 | Info disclosure | Memory dump via RCE | Patches via SSM Patch Manager, Inspector v2 | MEDIUM |
| EC2 | DoS | App-level resource exhaustion | ALB request timeout, ASG scaling, app-level rate limit | LOW |
| EC2 | EoP | Privilege escalation via app vuln | Least-privilege instance role, no admin policies attached, Falco runtime detection | LOW |
| RDS | Spoofing | Connection from non-app | SG locks RDS port to ALB->EC2 SG only, IAM auth for DB users | LOW |
| RDS | Tampering | SQL injection | Parameterized queries, app-level review, WAF SQLi rules | MEDIUM |
| RDS | Info disclosure | Backup leak | Snapshots encrypted with KMS CMK, snapshot copy denied across accts via SCP | LOW |
| RDS | DoS | Slow query exhaustion | Query timeout, RDS Performance Insights | LOW |
| Secrets path | Spoofing | Hardcoded creds in AMI | Secrets Manager fetch via task IAM, no creds in user data | LOW |
| TLS | Info disclosure | Cert exposure | ACM-managed cert, no private key on EC2, automatic renewal | LOW |

### Mitigations summary
- WAF managed rules + rate limiting
- IMDSv2 required at account default
- VPC endpoints for S3, KMS, Secrets Manager
- Least-privilege IAM on EC2
- Multi-AZ RDS in isolated subnet
- Multi-region trail to log archive
- GuardDuty + SecurityHub on

### Residual risk
- App-layer SQL injection (MEDIUM): depends on dev practices, mitigated by code review and SQLi rule group, not eliminated
- EC2 RCE leading to memory dump (MEDIUM): patches reduce, do not eliminate. Compensating: short-lived ASG instances, daily replacement.

### Real attack pattern this model defends against
Capital One 2019. The architecture above with IMDSv2 required would have prevented credential theft via SSRF.

---

## TM-2: Lambda + API Gateway + DynamoDB serverless API

### Architecture

```
Internet
   |
   v
[CloudFront] (optional)
   |
   v
[WAF on API Gateway]
   |
   v
[API Gateway REST or HTTP] (Lambda authorizer / Cognito)
   |
   v
[Lambda] (in VPC if needed, otherwise outside)
   |
   v
[DynamoDB] (encryption with KMS CMK)

Auth: Cognito user pool or API Gateway custom authorizer
Logging: API Gateway -> CloudWatch
         Lambda -> CloudWatch
         CloudTrail data events on Lambda invokes
```

### Assets
- API endpoints (logic)
- DynamoDB items (per-tenant data)
- Lambda execution role permissions
- API Gateway API keys (if used)

### Trust boundaries
- Internet to API Gateway
- API Gateway to Lambda (AWS-managed)
- Lambda to DynamoDB
- Lambda to other AWS APIs (KMS, Secrets Manager)

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| API Gateway | Spoofing | Forged JWT | Cognito JWT validation in authorizer, audience + issuer pinning | LOW |
| API Gateway | Tampering | Body modification | TLS-only, request validation schema | LOW |
| API Gateway | Repudiation | No log of caller | Access logs to CloudWatch + execution logs, X-Ray tracing | LOW |
| API Gateway | Info disclosure | Stack trace in error | Custom error responses, no error mapping leakage | LOW |
| API Gateway | DoS | Burst traffic | Throttling: account quota, per-key quota, per-route burst | LOW |
| API Gateway | EoP | Authorizer bypass | Test authorizer with negative cases, CodeReview on auth code | MEDIUM |
| Lambda | Spoofing | Cross-tenant invoke | Per-tenant claim in JWT, function reads from claim not body | LOW |
| Lambda | Tampering | Code injection in deps | Lambda code signing required, supply chain (npm audit, pip-audit) | MEDIUM |
| Lambda | Repudiation | Anonymous invocation | CloudTrail invoke events, X-Ray context | LOW |
| Lambda | Info disclosure | Logging secrets | No secret logging policy, Secrets Manager native env injection (so secrets are not in logs) | LOW |
| Lambda | DoS | Concurrency exhaustion | Reserved concurrency per function, account limit headroom | LOW |
| Lambda | EoP | Function role abuse | Least-privilege execution role, session policy at upstream invoke time, no PassRole on broad roles | LOW |
| DynamoDB | Spoofing | Item read by wrong tenant | IAM condition: dynamodb:LeadingKeys = ${aws:PrincipalTag/tenant} | LOW |
| DynamoDB | Tampering | Cross-tenant write | Same condition + per-tenant table or partition | LOW |
| DynamoDB | Info disclosure | Stream leakage | DynamoDB Streams encrypted with same KMS key, IAM scoped | LOW |
| DynamoDB | DoS | Hot partition | Composite keys, on-demand billing or auto-scaling | LOW |

### Mitigations summary
- API Gateway throttling at multiple tiers
- Cognito JWT with strict aud/iss/exp validation
- Lambda execution role per function (no shared "all-functions" role)
- DynamoDB IAM with LeadingKeys condition for tenant isolation
- KMS CMK for DynamoDB encryption
- Code signing for Lambda
- npm audit / pip-audit / Snyk in CI

### Residual risk
- Authorizer logic bug (MEDIUM): test coverage required, code review mandatory
- Supply chain compromise (MEDIUM): code signing helps, doesn't eliminate. Pin versions, audit deps.

---

## TM-3: EKS multi-tenant cluster

### Architecture

```
[Internet] -> [Route 53] -> [ALB Ingress Controller] -> [EKS Cluster]
                                                            |
                                                            v
                                                    [Pods in namespaces]
                                                       (per-tenant)

EKS authentication: aws-auth ConfigMap or EKS Access Entries (newer)
Pod identity: IRSA or EKS Pod Identity
Network policy: Calico or Cilium
Pod security: Pod Security Standards (restricted)
Runtime: Falco (DaemonSet) for runtime detection
```

### Assets
- Tenant workloads (containers)
- Persistent volumes (EBS or EFS)
- Cluster control plane secrets
- Service account tokens

### Trust boundaries
- Internet to ALB
- ALB to pod
- Pod to AWS API (via IRSA/Pod Identity)
- Pod to pod (within cluster)
- Pod to cluster control plane
- Worker node OS to cluster

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| Control plane | Spoofing | kubectl with stolen token | EKS access via Identity Center, no static kubeconfig long-lived | LOW |
| Control plane | Info disclosure | etcd snapshot leak | EKS-managed encryption, KMS CMK on etcd | LOW |
| Worker node | Spoofing | Node role abuse via IMDS | Pod-level IRSA/Pod Identity, IMDS hop limit 1, network policy denying 169.254.169.254 from non-system pods | LOW |
| Worker node | Tampering | Container escape via runc CVE | Pod Security Standards (restricted), AppArmor/seccomp, runtime detection (Falco) | MEDIUM |
| Worker node | EoP | Container with hostPath | PSS restricted blocks hostPath, OPA/Gatekeeper as backstop | LOW |
| Pod | Spoofing | Cross-namespace API call | NetworkPolicy default-deny + per-namespace policies, mTLS (Istio/Linkerd) for service-to-service | MEDIUM |
| Pod | Tampering | Image injection | ECR scanning, image signing (cosign), admission control verifying signatures | LOW |
| Pod | Repudiation | No audit of pod actions | Kubernetes audit log to CloudWatch, EKS control plane logs on, GuardDuty for EKS | LOW |
| Pod | Info disclosure | Service account token in logs | Don't mount SA token unless needed (automountServiceAccountToken: false), use IRSA/Pod Identity | LOW |
| Pod | DoS | One pod consumes node | Resource requests + limits, LimitRange per namespace, ResourceQuota | LOW |
| Service mesh | EoP | mTLS bypass | If using Istio: PeerAuthentication=STRICT, AuthorizationPolicy default-deny | MEDIUM |

### MITRE ATLAS (if running ML workloads in EKS)
| Tactic | Technique | Mitigation | Residual |
|---|---|---|---|
| Initial Access | AML.T0049 (Exploit public-facing application) | WAF + ingress controller hardening | LOW |
| Discovery | AML.T0035 (ML Artifact discovery) | Per-tenant namespace, NetworkPolicy denying cross-tenant scrape | LOW |
| Collection | AML.T0036 (Data from local system) | Restrict pod hostPath, no persistent debugging shells | MEDIUM |
| Exfiltration | AML.T0024 (Exfiltration via ML inference API) | Output rate limiting + content filtering | MEDIUM |

### Mitigations summary
- EKS access entries (modern) or aws-auth ConfigMap with Identity Center groups
- IRSA or Pod Identity for every pod that needs AWS access
- Network policies default-deny, explicit allow rules
- Pod Security Standards: restricted enforced via labels
- ECR scanning + image signing
- Falco DaemonSet for runtime detection
- Cluster autoscaler with scoped IAM
- VPC endpoints for ECR, S3, STS, EKS

### Residual risk
- Container escape (MEDIUM): kernel CVEs are real, runtime detection is reactive
- Service mesh complexity (MEDIUM): misconfigured Istio can fail-open
- Supply chain on container images (MEDIUM): signing helps, doesn't eliminate compromised base images

---

## TM-4: S3 data lake with Athena

### Architecture

```
[Sources: app logs, vendor data, batch ETL]
   |
   v
[S3 raw bucket] -> [AWS Glue Crawler] -> [Glue Data Catalog]
   |                                            |
   v                                            v
[S3 processed bucket] <- [Glue ETL job] -> [Athena queries]
   |                                            |
   v                                            v
[S3 reports bucket]                      [QuickSight]

Encryption: KMS CMK per bucket
Access: Lake Formation for fine-grained
Audit: CloudTrail data events on each bucket, S3 Server Access Logs
```

### Assets
- Raw customer data (PII, financial, sensitive)
- Processed analytics data
- Glue Data Catalog metadata (schema = sensitive too)
- Athena query history (reveals what was being asked)

### Trust boundaries
- Source -> S3 (varies per source)
- S3 -> Glue (in-VPC)
- Glue -> S3 (across-bucket)
- Athena -> S3 (read-only queries)
- QuickSight / analyst tools -> Athena

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| S3 raw | Spoofing | Unauthorized writer | Bucket policy restricting PutObject to specific source role ARNs, VPC endpoint policy with org ID | LOW |
| S3 raw | Tampering | Modification of historical data | Versioning + Object Lock, separate retention bucket | LOW |
| S3 raw | Info disclosure | Public bucket | BPA at account + bucket level, SCP forbids disabling | LOW |
| S3 processed | Tampering | Glue job writes incorrect data | Glue job IAM scoped to one prefix, separate KMS key per stage | MEDIUM |
| Glue Catalog | Spoofing | Wrong schema published | Lake Formation permissions on table-create, signed catalog deployments | LOW |
| Glue Catalog | Info disclosure | Schema reveals PII fields | Lake Formation column-level access control, redacted views | LOW |
| Athena | Spoofing | Query as another user | Per-user workgroups, IAM scoped to workgroup | LOW |
| Athena | Info disclosure | Query result has PII | Lake Formation column masking, post-query redaction in tools | MEDIUM |
| Athena | Repudiation | Untraced query | Athena query logs to CloudWatch, S3 access logs | LOW |
| Athena | DoS | Expensive query | Workgroup query limits, per-query data scanned cap | LOW |

### Mitigations summary
- KMS CMK per stage (raw, processed, reports), grants for cross-stage automation
- Lake Formation for fine-grained access (not just bucket-level)
- BPA on every bucket, SCP enforcing
- Bucket policy denying non-org principals
- VPC endpoint for S3 with PrincipalOrgID condition
- Macie scanning for PII in unexpected places
- CloudTrail data events on PII-bearing buckets

### Residual risk
- Glue job logic bug producing wrong outputs (MEDIUM): test coverage in CI
- Analyst exfil via Athena (MEDIUM): depends on user trust, mitigated by query logging and DLP on download tools

---

## TM-5: Multi-account landing zone with SSO

### Architecture

```
[Identity Provider: Okta or Entra]
   |
   v (SCIM provisioning)
[AWS Identity Center in management account]
   |
   v
[Permission sets assigned to groups -> accounts]
   |
   v
[Workload accounts in OUs]

Org structure:
  Root
    Management
    Security (log-archive, security-tooling)
    Workloads (Production, Non-Production)
    Sandbox

SCPs at OU level
GuardDuty + SecurityHub aggregator in security-tooling
CloudTrail trail in every account -> log-archive bucket
Config recorder in every account -> security-tooling aggregator
```

### Assets
- Org root account (highest blast radius)
- Identity Center directory
- Account credentials (root)
- Workload data
- CloudTrail logs

### Trust boundaries
- Engineer to IdP
- IdP to Identity Center
- Identity Center to target account (assume role)
- Account to account (cross-acct roles for shared services)

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| Org root acct | Spoofing | Root user phish | MFA on root, no access keys on root, alarm on root login | LOW |
| Identity Center | Spoofing | IdP compromise | IdP MFA, SCIM SCIM token rotation, EventBridge on IC user creation | MEDIUM |
| Permission set | EoP | PS modified to add admin | SCP forbids ssoadmin:* outside management, CloudTrail alerting on UpdatePermissionSet | LOW |
| Workload acct | Spoofing | Cross-acct role assumption forged | aws:SourceAccount + ExternalId on every cross-acct trust policy | LOW |
| Workload acct | Tampering | SCP bypass | SCPs are AWS-evaluated, cannot be bypassed; alarm on Org-level changes | LOW |
| CloudTrail | Repudiation | StopLogging | SCP denies cloudtrail:Stop*, log archive bucket has Object Lock, multi-region trail | LOW |
| Log archive | Tampering | Delete from log bucket | Object Lock compliance mode, separate account, MFA delete | LOW |
| GuardDuty | EoP | Disable detector | SCP denies guardduty:DeleteDetector outside security-tooling | LOW |

### Mitigations summary
- AWS Org with OU-based SCPs
- Identity Center with permission sets, MFA enforced
- Multi-region CloudTrail in every account, single log archive
- Object Lock on log archive bucket
- GuardDuty + SecurityHub delegated to security-tooling
- IAM Access Analyzer in every account
- Service-linked-role-only for cross-acct access where possible

### Residual risk
- IdP compromise (MEDIUM): outside AWS control, requires IdP-level hardening
- Insider threat with break-glass access (MEDIUM): JIT access via Teleport, dual-control on production

---

## TM-6: AI/ML pipeline with SageMaker and S3 (Dropzone-aligned)

### Architecture

```
[Customer data sources]
   |
   v
[S3 raw bucket] (KMS CMK A, BPA on, Macie scanning)
   |
   v
[SageMaker Processing job in private VPC]
   - VPC endpoints for S3, ECR, STS, KMS, CloudWatch
   - No internet egress
   - Job role: read raw, write processed
   |
   v
[S3 processed bucket] (KMS CMK B)
   |
   v
[SageMaker Training job, also private VPC]
   - Training role: read processed, write models
   |
   v
[S3 model artifacts bucket] (KMS CMK C, signed)
   |
   v
[SageMaker Model Registry] (versioning + approval gates)
   |
   v
[SageMaker Endpoint] OR [Bedrock model deployment]
   - Auth: IAM SigV4
   - Bedrock Guardrails for content filtering
   - Model invocation logging to S3 (KMS CMK D)
   |
   v
[Customers calling inference]

Audit:
  - CloudTrail (control plane)
  - SageMaker logs to CloudWatch
  - Bedrock invocation logs to S3
  - Langfuse-style trace store for prompt + completion
```

### Assets
- Customer raw data (PII, classified)
- Processed training data
- Model weights (intellectual property + risk if leaked)
- Inference prompts (may contain PII or attack payloads)
- Inference outputs (may leak training data)

### Trust boundaries
- Customer source to S3 raw
- S3 to SageMaker (in-VPC)
- SageMaker to model registry
- Model registry to endpoint
- Internet to inference endpoint

### STRIDE

| Component | Threat | Vector | Mitigation | Residual |
|---|---|---|---|---|
| S3 raw | Info disclosure | Bucket misconfigured public | BPA + bucket policy + SCP, Macie scan | LOW |
| S3 raw | Tampering | Poisoned training data injected | Source attestation (signed manifests), integrity check before processing | MEDIUM |
| Processing job | EoP | Job role too broad | Role read raw, write processed; no other AWS perms | LOW |
| Processing job | Info disclosure | Egress to internet | VPC endpoints only, no NAT, deny 0.0.0.0/0 in SG | LOW |
| Training job | Tampering | Model weights manipulated post-train | Signed model artifacts (cosign), checksum in registry | LOW |
| Training job | Info disclosure | Training logs contain data samples | Sanitize logs, separate KMS key for log bucket | MEDIUM |
| Model registry | EoP | Unauthorized approval | Approval requires 2 humans (registry permission), CloudTrail alerts | LOW |
| Endpoint | Spoofing | Forged inference request | IAM SigV4 auth, IAM scoped per tenant | LOW |
| Endpoint | Info disclosure | Output reveals training data | Bedrock Guardrails or NeMo output rail with PII filter, differential privacy where applicable | MEDIUM |
| Endpoint | DoS | Cost exhaustion via giant prompts | Per-call cost ceiling, daily ceiling, rate limit | LOW |

### MITRE ATLAS (the AI-specific threats)

| Tactic | Technique | Vector | Mitigation | Residual |
|---|---|---|---|---|
| Reconnaissance | AML.T0006 (Active scanning) | Probing model with crafted prompts | Rate limiting + anomaly detection on prompt patterns | MEDIUM |
| Resource Development | AML.T0021 (Establish accounts) | Attacker creates many test accounts | Captcha, account-age requirements, billing data | LOW |
| Initial Access | AML.T0049 (Exploit public-facing app) | Endpoint API vuln | API-layer SAST, fuzzing | LOW |
| Initial Access | AML.T0051 (LLM Prompt Injection) | Crafted prompt overrides system instructions | Input rail (NeMo or Bedrock Guardrails), allow-list of tools, system prompt isolation | MEDIUM |
| Persistence | AML.T0011 (Backdoor ML model) | Compromised training data plants backdoor trigger | Data integrity checks, training data lineage, red-team eval before deployment | MEDIUM |
| Defense Evasion | AML.T0015 (Evade ML model) | Adversarial inputs cause misclassification | Robustness testing, ensemble models, runtime anomaly detection | MEDIUM |
| Credential Access | AML.T0055 (LLM Plugin Compromise) | Plugin with broad IAM exfiltrates secrets | Plugin allow-list, plugin role least-privilege, audit on plugin invocations | MEDIUM |
| Discovery | AML.T0035 (ML Artifact Collection) | Model weight extraction via repeated queries | Output rate limiting, query budget per principal, watermarking | MEDIUM |
| Collection | AML.T0036 (Data from local system) | Training data extraction from model | Differential privacy in training, watermark detection on suspect outputs | MEDIUM |
| Impact | AML.T0048 (External harms) | Model produces harmful output | Output rail filtering (toxicity, PII, instructions for harm), human review for high-stakes | MEDIUM |

### Mitigations summary
- Per-stage KMS keys with grants for narrow service access
- VPC endpoints, no internet egress for compute
- Signed model artifacts, two-person approval for production deployment
- Bedrock Guardrails or NeMo Guardrails on input + output
- Per-tenant rate limit + cost ceiling on inference
- Training data integrity checks
- Red-team evaluation before deployment, periodic re-eval
- Langfuse-equivalent prompt/completion audit trail

### Residual risk
- Prompt injection (MEDIUM): no perfect defense, layer multiple rails
- Model theft via repeated queries (MEDIUM): rate limit + watermark, accept some residual
- Training data leakage (MEDIUM): inherent to ML, mitigate with redaction + DP

### Real reference for this model
This maps to Emmanuel's SQUIRE_THREAT_MODEL.md format. The SOC triage agent threat model in the cyber-squire-ops repo applies the same STRIDE + ATLAS approach to a real production agent.

---

## How to use these in interviews

When asked "design security for X":
1. Identify which TM-1 through TM-6 most closely matches.
2. State the assets and trust boundaries first (shows you think in those terms).
3. Walk through 3-4 high-impact threats with their mitigations.
4. End with residual risk and how you'd monitor it.

Senior interviewers want to hear "I'd accept residual risk on X because Y, with mitigation Z and detection W". Junior candidates pretend everything is mitigated to LOW. Real engineers admit MEDIUMs and show how they catch them.

---

## How to use these in real work

These are templates. Copy one, adjust the components for your actual system, walk through STRIDE per component. Add ATLAS rows if any ML is in the loop. Pin to a residual risk register and review every quarter or on architecture change.

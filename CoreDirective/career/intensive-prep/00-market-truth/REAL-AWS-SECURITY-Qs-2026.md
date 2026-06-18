# Real AWS Security Interview Questions, 2026

Reference document. Real AWS Security interview questions surfaced from public
sources, with depth notes for the senior bar (USD 200K+ Cloud Security and AWS
Security Engineer roles). `[UNVERIFIED]` marks paraphrased questions without a clean
primary citation. Sources cited inline.

---

## 1. IAM Privilege Escalation and Trust Policies

### Q1.1 Lambda role plus Administrator path
- **Question:** A Lambda function has `AdministratorAccess` attached. The function
  fetches a third-party dependency at runtime. What is the privilege escalation
  path and how would you stop it?
- **Source:** ThinkCloudly Advanced AWS Security questions.
  https://thinkcloudly.com/blog/advanced-aws-security-interview-questions-for-senior-it-security-engineers/
- **Senior depth expected:** Walk through dependency-confusion or transitive-supply
  chain compromise that gives the attacker code execution inside Lambda, then full
  account control via the role. Mitigations: scoped IAM, permission boundaries,
  artifact pinning with hashes, signed builds, no internet egress unless required.

### Q1.2 IMDSv1 SSRF and IMDSv2 fix
- **Question:** Explain how IMDSv1 enables key theft via SSRF. How does IMDSv2 close
  the hole?
- **Source:** jassics/security-interview-questions AWS list.
  https://github.com/jassics/security-interview-questions/blob/main/aws-security-interview-questions.md
- **Senior depth expected:** SSRF bypass relies on the metadata endpoint accepting
  unauthenticated GETs. IMDSv2 requires a session token via PUT first, breaking the
  GET-only SSRF chain. Senior candidates also mention `HttpEndpoint=disabled` on
  workloads that do not need IMDS, organization-wide enforcement via `aws:Ec2InstanceMetadataTags`
  conditions, and detection via VPC flow logs or GuardDuty.

### Q1.3 Read this trust policy and tell me what is wrong
- **Question:** Interviewer presents a trust policy with a wildcard principal or a
  missing `aws:SourceAccount` condition on a cross-account role. Find the issue.
- **Source:** jassics list. The interview presents a policy and asks the candidate
  to read it.
- **Senior depth expected:** Confused-deputy attack. Trust policies that allow a
  service principal without conditions can be assumed by any account that can get
  the service to call assume-role on the principal's behalf. Fix with
  `aws:SourceAccount` plus `aws:SourceArn` or a unique `sts:ExternalId` for
  third-party roles.

### Q1.4 Cross-account access design
- **Question:** What comes to mind when a service in account A needs to access an
  S3 bucket in account B?
- **Source:** jassics list.
- **Senior depth expected:** Two patterns. (1) Resource-based bucket policy plus IAM
  role in account A that allows reading. (2) Cross-account role with a trust policy
  that requires `ExternalId`. Discuss why bucket policies alone leak control to
  bucket owners and why role chaining can break CloudTrail attribution.

### Q1.5 NotResource policy gotcha
- **Question:** Read this policy with an `NotResource` clause and find the bug.
- **Source:** jassics list.
- **Senior depth expected:** `NotResource` with a deny that is meant to block "all
  except X" frequently misfires. The classic bug is using `Effect: Allow` with
  `NotResource: arn:aws:s3:::sensitive`. That allows everything except the
  sensitive bucket, which is the opposite of intent.

### Q1.6 IAM role chaining
- **Question:** What is role chaining, what are the security implications, and what
  is the maximum chain duration?
- **Source:** k9 Security AWS IAM interview question pack.
  https://www.k9security.io/docs/aws-iam-interview-questions/
- **Senior depth expected:** Chaining is `assume-role` then `assume-role` again from
  the resulting credentials. Max session duration drops to 1 hour for chained
  sessions. Implications: CloudTrail still logs the chain but it makes attribution
  noisier, and missing `aws:SourceIdentity` makes it harder to tie human identity
  to actions.

### Q1.7 ABAC vs RBAC at scale
- **Question:** When would you choose ABAC (tag-based) over RBAC for IAM?
- **Source:** ThinkCloudly senior question set.
- **Senior depth expected:** ABAC scales when teams or projects are dynamic and tags
  drive access. Risks: tag tampering, tag drift, requires SCP-level controls on
  who can change tags. The honest answer is hybrid, RBAC for coarse roles plus
  ABAC for resource-level scoping.

### Q1.8 Permission boundaries vs SCPs
- **Question:** Difference between an IAM permission boundary and an SCP. When does
  each apply?
- **Source:** k9 Security IAM list and ThinkCloudly senior set.
- **Senior depth expected:** SCPs apply at the Organization or OU level, set the max
  available permissions for any principal in the account, and do not grant
  permissions on their own. Permission boundaries cap what an IAM user or role can
  do regardless of attached identity policy. Senior candidates also flag the SCP
  not-quite-deny gotcha for the management account.

---

## 2. KMS Deep Questions

### Q2.1 Customer-managed key rotation cadence
- **Question:** Should you enable key rotation? What rotation period, and why?
- **Source:** jassics list.
- **Senior depth expected:** Annual rotation is the AWS managed default. CMK rotation
  rotates the backing key but old ciphertext stays decryptable with the old key
  version, which is intended. Senior candidates discuss data-key-level rotation,
  envelope encryption, and the difference between rotating the CMK and re-encrypting
  data in place.

### Q2.2 S3 bucket with KMS, file uploads but downloads return AccessDenied
- **Question:** A user can put objects but cannot decrypt them. Where do you look?
- **Source:** jassics list.
- **Senior depth expected:** Three-way join. The user needs (1) S3 GetObject on the
  bucket, (2) `kms:Decrypt` on the CMK, (3) the CMK key policy must allow that
  principal. The most common bug is that the bucket policy is fine but the CMK key
  policy was edited and dropped the user. Walk through `kms:ViaService` conditions
  and grants for cross-account access.

### Q2.3 Encryption at rest "by default", do you agree
- **Question:** Should we enable data encryption at rest by default for all
  services?
- **Source:** jassics list.
- **Senior depth expected:** Yes for compliance and defense in depth, but the more
  important question is the threat model. At-rest encryption defeats stolen disk
  threats, not credential-compromise threats. Senior candidates explain that the
  real lever is key access policy, not the encryption flag.

---

## 3. VPC and Network Security

### Q3.1 Default security group with ports 22, 25, 53, 80, 443, 3679, 3306, 9001
- **Question:** Do you see any issues with this security group?
- **Source:** jassics list.
- **Senior depth expected:** Multiple issues. SSH and database (3306) on a default
  group is a major leak. Default groups should be empty. Mail port 25 on a default
  group hints at outbound spam pivot. Discuss security group as zoning, not as a
  firewall, and the importance of denying all by default plus reviewing changes via
  Config rules.

### Q3.2 Public API endpoint exposure
- **Question:** What issues arise when an API endpoint is exposed to the public
  internet?
- **Source:** jassics list.
- **Senior depth expected:** DDoS, credential stuffing, scraping, abuse. Senior
  candidates name CloudFront plus AWS WAF managed rules, request signing, rate-based
  rules, IP reputation lists, plus how to use API Gateway resource policies for
  identity-aware access.

### Q3.3 Transit Gateway, when and why
- **Question:** When should you use TGW? Is there a security benefit?
- **Source:** jassics list.
- **Senior depth expected:** TGW centralizes VPC peering and is the right answer at
  scale. Security benefit is centralized inspection, route-table-based segmentation,
  and a single place to apply network firewalls. The miss: assuming TGW alone
  segments traffic. It does not, you need explicit route-table separation per
  attachment.

### Q3.4 Should the database be exposed publicly
- **Question:** Should we expose database access publicly or directly to the web
  application?
- **Source:** jassics list.
- **Senior depth expected:** Never expose RDS publicly. The web app should be in a
  private subnet where possible, with an ALB front. Discuss IAM database
  authentication, TLS to the database, and rotating the master credential via
  Secrets Manager.

---

## 4. GuardDuty, Security Hub, Inspector

### Q4.1 GuardDuty false positives, how do you reduce
- **Question:** GuardDuty has lots of false positives. Suggestions?
- **Source:** jassics list.
- **Senior depth expected:** Suppression rules tied to known-good IPs and behaviors.
  Use `Threat IP` and `Trusted IP` lists. Pipe findings to Security Hub for severity
  normalization. Tune by finding type, not blanket suppression. The mature answer:
  GuardDuty is the trigger, not the verdict. Findings feed an enrichment and
  triage pipeline.

### Q4.2 GuardDuty data sources
- **Question:** What are the different data sources GuardDuty consumes?
- **Source:** jassics list.
- **Senior depth expected:** VPC flow logs, DNS logs, CloudTrail management events,
  CloudTrail S3 data events, EKS audit logs, RDS login activity, EBS malware scans,
  Lambda network activity, and S3 protection. Each source has its own findings.

### Q4.3 GuardDuty vs Security Hub vs Inspector
- **Question:** What is the responsibility of each?
- **Source:** ThinkCloudly question set and AWS docs.
  https://thinkcloudly.com/blog/advanced-aws-security-interview-questions-for-senior-it-security-engineers/
- **Senior depth expected:** GuardDuty is threat detection on telemetry. Security
  Hub is the aggregator for findings (GuardDuty, Inspector, Macie, Config) and is
  where compliance standards (CIS, AWS FSBP, PCI) are evaluated. Inspector is
  vulnerability scanning for EC2, ECR, Lambda. Senior candidates mention that
  Security Hub findings normalize via the AWS Security Finding Format (ASFF) and
  flow into one EventBridge bus for routing.

### Q4.4 Custom 5xx alert
- **Question:** I need an alert in Slack or email whenever my backend APIs start
  returning 5xx in CloudWatch. How would you build it?
- **Source:** jassics list.
- **Senior depth expected:** CloudWatch metric filter on the API Gateway or ALB
  access logs, alarm on the count, EventBridge rule fires Lambda or SNS. Senior
  candidates mention alarm tuning to avoid pager fatigue and using composite alarms
  to avoid noise during deploys.

---

## 5. EKS Pod Identity vs IRSA

### Q5.1 IRSA, what does it solve
- **Question:** What is IAM Roles for Service Accounts and what problem does it
  solve?
- **Source:** AWS docs and community guides referenced in
  https://thinkcloudly.com/blog/advanced-aws-security-interview-questions-for-senior-it-security-engineers/
- **Senior depth expected:** IRSA federates the Kubernetes service account JWT
  through STS so a pod can assume an IAM role without static credentials. It uses
  the OIDC provider on the EKS cluster. The problem it solves: avoid IAM keys on
  nodes, scope per-pod access.

### Q5.2 EKS Pod Identity vs IRSA
- **Question:** When would you choose EKS Pod Identity over IRSA?
- **Source:** AWS docs, surfaced via 2026 EKS interview question banks.
  `[UNVERIFIED]` exact wording varies.
- **Senior depth expected:** Pod Identity is simpler, agent-based, no OIDC provider
  required, simpler trust policy. Better for new clusters and for workloads that
  span clusters because the trust does not depend on a per-cluster OIDC issuer URL.
  IRSA is still the right answer when the cluster is fronting a long-lived, complex
  cross-account role chain.

---

## 6. S3 Attack Patterns

### Q6.1 How would you find evidence of malicious activity in S3
- **Question:** How would you find evidence of malicious activity in services like
  EBS or applications using Lambda? S3 by extension.
- **Source:** jassics list.
- **Senior depth expected:** S3 server access logs plus CloudTrail S3 data events.
  Look for `GetObject` storms, public ACL set, presigned URL abuse, copy operations
  to attacker-controlled buckets, and changes to bucket policy or block-public-access
  settings. GuardDuty `S3` finding family covers many of these.

### Q6.2 Public S3 prevention
- **Question:** How would you prevent public S3 bucket exposure?
- **Source:** Exponent security engineer prep.
  https://www.tryexponent.com/blog/security-engineer-interview-prep
- **Senior depth expected:** Account-level Block Public Access plus bucket-level
  BPA. SCP that denies disabling BPA. Config rule for continuous evaluation. Macie
  for content-aware findings. Discuss why ACLs are deprecated in favor of bucket
  policies, and the trap of presigned URLs being a public-by-design feature.

### Q6.3 Cross-account S3 takeover
- **Question:** Walk through how a misconfigured bucket policy plus a CMK key policy
  bug enables read access from another account. `[UNVERIFIED]` reported across red
  team write-ups, exact phrasing varies.
- **Senior depth expected:** Three checks: bucket policy `Principal: *` with weak
  conditions, missing `aws:PrincipalOrgID`, and CMK key policy that allows the same
  external account or `Principal: AWS: *`. Senior candidates mention `s3:RequireKMS`
  and IAM Access Analyzer findings.

---

## 7. Lambda Execution Role Security

### Q7.1 IAM check for "Lambda triggered, did the action work"
- **Question:** A Lambda is triggered by an event and is supposed to perform an
  action. To make sure it works, what do you check in IAM?
- **Source:** jassics list.
- **Senior depth expected:** Two roles to check. The execution role on the Lambda,
  and any resource policy on the target service. CloudWatch logs role policy must
  allow the function to write logs. Walk through how to debug AccessDenied via
  CloudTrail and how to check `iam:PassRole` if the function is configuring other
  resources.

### Q7.2 Dependency confusion in Lambda
- **Question:** Your Lambda installs Python packages at deploy time. How do you
  defend against dependency confusion?
- **Source:** Pattern from ThinkCloudly advanced set and AWS prescriptive guidance.
- **Senior depth expected:** Pin all transitive deps with hashes, mirror in CodeArtifact,
  SCP that blocks public PyPI, scan on deploy, sign artifacts via Signer. Senior
  candidates also mention runtime SBOM tooling and that the most damaging supply
  chain attack vector at AWS is still package compromise on common libraries.

---

## 8. Multi-Account Landing Zone Design

### Q8.1 Design a secure multi-account environment for a SaaS startup
- **Question:** Design a Landing Zone for a SaaS startup that needs prod, staging,
  dev, plus log archive and audit accounts.
- **Source:** AWS Prescriptive Guidance landing zones.
  https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-aws-environment/understanding-landing-zones.html
  Cloudsoft top 50 SCP and Landing Zone questions.
  https://cloudsoftsol.com/interview-questions/top-50-aws-landing-zone-scp-interview-qa-2025/
- **Senior depth expected:**
  - Control Tower as the bootstrap or AFT for IaC. Identify the three required
    shared accounts: Management, Log Archive, Audit.
  - OU structure: Security OU (audit, log archive), Workloads OU (prod, staging),
    Sandbox OU (devs).
  - SCPs: deny disabling CloudTrail, deny disabling Config, deny root user actions
    except for break-glass, deny access keys for IAM users, deny regions outside
    approved list.
  - Identity: AWS IAM Identity Center as the SSO front door, federated to the
    company IdP. No IAM users in workload accounts.
  - Logging: Org-trail to Log Archive, S3 with Object Lock, KMS CMK in the Log
    Archive account that prevents deletion.
  - Detection: Security Hub aggregator in Audit account, GuardDuty delegated admin
    in Audit, EventBridge bus pattern.
  - Network: Either centralized egress via Transit Gateway with a shared inspection
    VPC, or per-account egress with consistent firewall posture.
- **What weak candidates miss:** Treating multi-account as "just spin up an
  account per env" without naming the OU, the SCPs, the SSO, or the logging fan-in.

### Q8.2 SCP that prevents disabling CloudTrail
- **Question:** Write the SCP that prevents disabling CloudTrail across the org.
- **Source:** Cloudsoft 50 question set and AWS docs.
- **Senior depth expected:** Deny `cloudtrail:StopLogging`, `cloudtrail:DeleteTrail`,
  and `cloudtrail:UpdateTrail` for trail names matching the org trail. Pair with a
  permission boundary on any role that has admin to make sure the deny chain works.

---

## 9. The "Design a Secure SaaS on AWS" System Design Prompt

### Q9.1 Prompt
- **Question:** Design a secure SaaS application on AWS for an enterprise customer.
  Multi-tenant, regulated data, customer expects SOC 2.
- **Source:** Habitat3 secure landing zone design article.
  https://www.habitat3.com.au/single-post/designing-a-secure-aws-landing-zone-for-compliance-focused-saas-applications
  Plus Practical DevSecOps and Exponent SE prep guides.

### Q9.2 What a USD 200K answer covers
1. **Tenancy model:** Pool, silo, or hybrid. Trade-offs in blast radius, isolation,
   compliance scope. Per-tenant KMS keys for crypto-shredding.
2. **Identity:** Cognito or IAM Identity Center for staff. Per-tenant identity pool
   with row-level filtering. Short-lived tokens, refresh rotation.
3. **Network:** ALB plus WAF, private subnets, VPC endpoints for S3 and DynamoDB to
   keep traffic off the public internet, no NAT egress where avoidable.
4. **Compute:** Containers on ECS Fargate or EKS with Pod Identity. Read-only
   filesystem. No `--privileged`. Image scanning in ECR via Inspector.
5. **Data:** S3 with BPA, default encryption with per-tenant CMK. RDS or DynamoDB
   with encryption, point-in-time recovery, cross-account read-only replica for
   the Audit account.
6. **Secrets:** Secrets Manager with rotation. No env-var secrets in CI logs.
7. **Logging and monitoring:** Org-trail to log archive, GuardDuty, Security Hub,
   Macie for sensitive data discovery. CloudWatch metric filters for security
   events. EventBridge fan-out to SOC.
8. **CI/CD:** OIDC federation from GitHub Actions to AWS roles, no static keys.
   SLSA L2 minimum, signed artifacts, Cosign verification at deploy.
9. **Customer evidence:** SOC 2 evidence pulled automatically from Security Hub,
   Config, and Audit Manager. Customer data isolation tested with chaos drills.

### Q9.3 What a USD 150K answer sounds like
- Names services correctly but does not articulate the threat model.
- Says "encryption at rest" without naming the key, the policy, or the rotation.
- Does not bring up SCPs, OU structure, or the audit account.
- Does not separate data plane from control plane.
- Treats "use IAM" as the answer to authorization design.

---

## 10. Other High-Frequency Topics

### Q10.1 RTO vs RPO
- **Question:** Define RTO and RPO and how each affects backup design.
- **Source:** jassics list.
- **Senior depth expected:** RTO is recovery time, RPO is acceptable data loss.
  RTO drives compute strategy (warm standby, pilot light, multi-region active).
  RPO drives backup cadence and replication. Discuss cost-vs-risk and that "1 hour
  RPO" really means "tolerate 60 minutes of data loss".

### Q10.2 SSH to EC2 fails, debug
- **Question:** You are trying to SSH into an EC2 instance and it is failing. Walk
  through your diagnosis.
- **Source:** jassics list.
- **Senior depth expected:** Layered diagnosis: (1) network reachability (route
  table, IGW, subnet ACL, security group), (2) SSH service running and listening,
  (3) key pair correct and `0600` perms, (4) host key not changed, (5) failed-login
  rate limits, (6) IMDS or SSM Session Manager as alternative. Senior candidates
  mention turning off SSH entirely in favor of SSM Session Manager.

### Q10.3 Backup security
- **Question:** Have you worked on backup security and monitoring? Explain.
- **Source:** jassics list.
- **Senior depth expected:** AWS Backup with vault locks (governance vs compliance
  mode), cross-account vaults so a compromise of the workload account cannot delete
  backups, immutable S3 with Object Lock, alarms on `BackupJobFailed`. Mention 3-2-1
  but adapt it to cloud (3 copies, 2 storage classes or accounts, 1 offsite or
  cold).

### Q10.4 SSO plus a third-party tool integration
- **Question:** We want SSO and Trello integration in our AWS environment. Posture?
- **Source:** jassics list.
- **Senior depth expected:** Federate via IAM Identity Center to the IdP, then SAML
  to Trello. Conditional access via the IdP, no shared accounts. For OAuth
  applications discuss limiting scopes and using a per-tenant service account when
  Trello pulls data via API. Mention SCIM provisioning so deprovisioning is
  consistent.

### Q10.5 Secure RDS posture
- **Question:** What comes to mind when you have to secure an RDS instance?
- **Source:** jassics list.
- **Senior depth expected:** No public access. IAM database auth or Secrets Manager
  rotation. TLS in transit. KMS at rest. Snapshots encrypted. Read replicas and
  automated backups. Audit logging enabled and shipped to S3 or CloudWatch. Database
  Activity Streams for sensitive RDS engines. Performance Insights with appropriate
  retention.

---

## 11. The "Recites Buzzwords vs Reasons from First Principles" Tell

Across multiple sources, including the Yuva Surya Konatham Amazon write-up, a
hiring manager's strongest signal is the candidate moving from a service name to
the underlying mechanism. Saying "I would use GuardDuty" is undergrad. Saying
"I would route GuardDuty findings via EventBridge into a triage pipeline because
the raw findings have a 30 percent false positive rate on common workloads, and
the value is the trigger plus enrichment, not the alert itself" is senior.

Source: https://medium.com/@yuvasurya1998/what-i-learned-from-getting-rejected-by-amazon-a-security-engineers-interview-experience-293e65a2f942

---

## Sources

- jassics/security-interview-questions AWS list.
  https://github.com/jassics/security-interview-questions/blob/main/aws-security-interview-questions.md
- ThinkCloudly Advanced AWS Security questions.
  https://thinkcloudly.com/blog/advanced-aws-security-interview-questions-for-senior-it-security-engineers/
- k9 Security AWS IAM interview questions.
  https://www.k9security.io/docs/aws-iam-interview-questions/
- Cloudsoft top 50 AWS Landing Zone and SCP interview Q&A.
  https://cloudsoftsol.com/interview-questions/top-50-aws-landing-zone-scp-interview-qa-2025/
- AWS Prescriptive Guidance landing zones.
  https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-aws-environment/understanding-landing-zones.html
- Habitat3 secure landing zone for SaaS.
  https://www.habitat3.com.au/single-post/designing-a-secure-aws-landing-zone-for-compliance-focused-saas-applications
- Exponent security engineer interview prep.
  https://www.tryexponent.com/blog/security-engineer-interview-prep
- Yuva Surya Konatham, Amazon SE rejection write-up. Medium.
  https://medium.com/@yuvasurya1998/what-i-learned-from-getting-rejected-by-amazon-a-security-engineers-interview-experience-293e65a2f942
- AWS official documentation for KMS, IAM, Security Hub, GuardDuty, EKS Pod Identity,
  Inspector, Backup, IAM Identity Center.

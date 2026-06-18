# AWS Security Mastery: 21-Day Roadmap

**Owner:** Emmanuel Tigoue
**Target:** Defend AWS architecture in 1-hour senior security interview
**Pipeline driver:** Dropzone AI (AWS detection heavy), OneDigital, Resilience, Insight Global
**Constraint:** ADHD, 4hr sleep, learns by building. Each topic gets a working lab.
**Cadence:** 60 to 90 minutes per topic, 7 days a week, 21 topics.

---

## How to use this roadmap

1. Read the topic concept block (10 min). Just the AWS docs URL plus the bullet anchors here.
2. Run the lab (30 to 60 min). The lab is the exam. If you cannot run it, you do not know it.
3. Write the answer to the interview question at the bottom of each day in your own words. 90 seconds spoken.
4. End each day by adding one new bullet to your CHEATSHEET.md.

If a day slides, do not catch up. Push the rest one day. Skipping a lab means you do not know the topic.

---

## Week 1: Identity, network, crypto. The foundation.

### Day 1: IAM identities and policies
- Concepts: users, groups, roles, federated principals, service-linked roles
- Policy types: identity, resource, SCP, permission boundary, session policy
- Evaluation order: explicit deny > SCP > resource > identity > permission boundary > session
- Trust policy vs permissions policy on a role
- Lab: `labs/iam_privesc_via_passrole.sh`
- Real attack reference: Capital One 2019 breach used IAM role with overly broad S3 permissions
- Docs: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- Interview question: "Walk me through how IAM evaluates a request when SCP says deny but identity policy says allow."

### Day 2: IAM advanced patterns
- Permission boundaries (delegate without giving away the kingdom)
- ABAC with tags vs RBAC with groups
- Condition keys: aws:SourceIp, aws:PrincipalOrgID, aws:RequestTag, aws:ResourceTag
- Cross account access via role chaining
- Lab: `labs/iam_abac_with_tags.sh`
- Interview question: "Design a system where a developer can manage their own EC2 but cannot touch anyone else's. No hardcoded IDs."

### Day 3: IAM common attack paths
- iam:PassRole abuse (most common privesc)
- sts:AssumeRole with no condition keys
- Confused deputy when external ID is missing
- Lambda function with admin role attached
- CloudFormation with iam:PassRole to admin
- Lab: `labs/iam_privesc_via_passrole.sh` (re-run, focus on detection)
- Reference: Rhino Security Labs "AWS IAM Privilege Escalation" 21+ paths
- Docs: https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/
- Interview question: "An attacker phished a developer with iam:PassRole on lambda functions. What can they do?"

### Day 4: VPC architecture
- Public, private, isolated subnets
- Route tables, IGW vs NAT GW vs VPC endpoint
- Why a NAT in every AZ unless you accept cross-AZ data charges
- Transit Gateway vs VPC peering
- Lab: `labs/vpc_layered_subnets.tf`
- Interview question: "Why is putting RDS in a public subnet a finding even with no public IP?"

### Day 5: VPC controls
- Security groups (stateful, allow only)
- NACLs (stateless, allow and deny, last line)
- VPC Flow Logs to CloudWatch or S3
- VPC Endpoints (gateway: S3, DynamoDB; interface: everything else)
- Endpoint policies as a kill switch for data exfiltration
- Lab: `labs/vpc_flow_log_hunting.sh`
- Interview question: "How would VPC Endpoint policies stop a compromised EC2 from exfiltrating data to an attacker S3 bucket?"

### Day 6: KMS fundamentals
- Symmetric keys (CMK, AWS-managed, customer-managed)
- Envelope encryption (data key encrypts data, KMS key encrypts data key)
- Key policy is the root authority. IAM is layered on top.
- aws:ViaService condition for service-only access
- Key rotation: AWS-managed keys auto-rotate, CMKs you opt in
- Lab: `labs/kms_key_grant_abuse.sh`
- Docs: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
- Interview question: "If I have kms:Decrypt on the key policy and IAM denies it, can I decrypt? What if it is reversed?"

### Day 7: KMS advanced
- Grants (temporary, programmatic permission)
- Multi-region keys (replicas share material, separate ARNs)
- KMS key context (additional auth data baked into encryption)
- Cross account KMS use (key policy must allow, IAM on the consumer side must allow)
- Lab: `labs/kms_envelope_encryption_demo.sh`
- Interview question: "An S3 bucket uses SSE-KMS with a customer-managed key. The key policy denies the bucket owner. Can the bucket owner read objects?"

---

## Week 2: Compute, storage, detection.

### Day 8: EC2 and IMDS
- IMDSv1 SSRF through web app proxies (Capital One breach pattern)
- IMDSv2 session-token requirement, hop limit, why hop limit 1
- Account-level IMDSv2 enforcement (modify-instance-metadata-defaults)
- Instance profile is just a role wrapper
- Lab: `labs/imds_v1_attack.sh`
- Reference: Capital One 2019 breach ($190M settlement, 100M records)
- Docs: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-IMDS-options.html
- Interview question: "Walk me through the Capital One breach. What was the misconfig and what would have stopped it?"

### Day 9: Lambda security
- Execution role (what the function can do)
- Resource-based policy (who can invoke)
- Environment variables: never put secrets there in plaintext, use Secrets Manager + KMS
- Concurrency limits as a DoS control
- Lambda in VPC vs not (cold start tradeoff)
- Code signing for Lambda (signed deployments only)
- Lab: `labs/lambda_role_assumption.sh`
- Interview question: "How do you stop one tenant in a multi-tenant Lambda app from reading another tenant's S3 prefix?"

### Day 10: ECS task security
- Task role vs execution role (task = what your code does, execution = what ECS agent does pulling images)
- Fargate vs EC2 launch type (kernel sharing risk on EC2)
- Read-only root filesystem on container
- Secrets injection from Secrets Manager via task definition
- Lab: `labs/ecs_task_role_isolation.tf`
- Interview question: "What is the difference between task role and execution role on Fargate? Give me a concrete example where mixing them up causes a vuln."

### Day 11: EKS pod security
- IRSA (IAM Roles for Service Accounts) using OIDC provider on EKS
- Pod Identity (newer, simpler, since 2023)
- Why never give the node IAM role pod-level permissions
- Network policies inside the cluster (Calico, Cilium)
- Pod Security Standards (privileged, baseline, restricted)
- Lab: `labs/eks_pod_identity_walkthrough.sh`
- Docs: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- Interview question: "Walk me through what happens cryptographically when a pod calls AWS APIs using IRSA."

### Day 12: S3 security
- Block Public Access at account and bucket level (the kill switch)
- Bucket policy vs ACL vs IAM (modern: bucket policy + IAM, ACLs disabled by default since 2023)
- SSE-S3 vs SSE-KMS vs SSE-C
- Object Lock for ransomware resilience (compliance mode is irrevocable)
- Replication with replication time control
- S3 Access Points for sharing
- Lab: `labs/s3_bucket_takeover.tf`
- Real attack: Code Spaces 2014 wiped by S3 + EC2 takeover via stolen creds
- Reference: thousands of public S3 leaks (Accenture 2017, Verizon 2017, etc)
- Interview question: "Walk me through securing an S3 bucket holding PII. Layer by layer."

### Day 13: CloudTrail
- Management events (default, control plane)
- Data events (S3 GetObject, Lambda Invoke - separate cost, off by default)
- Insight events (anomaly detection)
- Multi-region trail with log file validation
- Logs to S3 with bucket policy that prevents deletion + Object Lock
- Lake (CloudTrail Lake) vs S3 plus Athena
- Lab: `labs/cloudtrail_log_analysis_queries.md`
- Interview question: "An attacker has admin in your account. They want to delete CloudTrail. Tell me four ways to stop them or at least detect it."

### Day 14: GuardDuty + SecurityHub
- GuardDuty: behavioral threat detection from CloudTrail + VPC Flow + DNS + EKS audit logs
- Common findings: CryptoCurrency:EC2/BitcoinTool, UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration, Recon:IAMUser/AnomalousASN
- SecurityHub: aggregator for GuardDuty + Inspector + Macie + Config + 50 partners (Snyk, CrowdStrike, etc)
- AWS Foundational Best Practices, CIS, PCI standards in SecurityHub
- Findings dedup with AWS Security Finding Format (ASFF)
- Lab: `labs/guardduty_finding_triage.md` + `labs/securityhub_aggregation.md`
- Interview question: "GuardDuty fires UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS. What are the first five things you do?"

---

## Week 3: Edge, secrets, governance, advanced.

### Day 15: WAF, Shield, CloudFront
- WAF: managed rule groups (AWS Core, AWS Known Bad Inputs, Anonymous IP), custom rules, rate limiting per IP or per header
- WAF rule order matters (first match wins, count vs block actions)
- Shield Standard (free, on every account) vs Shield Advanced ($3K/mo, DDoS Response Team)
- CloudFront origin access control (OAC), signed URLs, signed cookies
- Geo-blocking at CloudFront vs WAF
- Lab: `labs/waf_rate_limiting.tf`
- Interview question: "Customer is being layer-7 DDoS'd. Walk me through what you turn on in the next 30 minutes."

### Day 16: Secrets Manager vs Parameter Store
- Secrets Manager: rotation built in, $0.40/secret/mo, native integration with RDS/Redshift/DocumentDB
- Parameter Store: free for standard, KMS encryption optional, no rotation
- When to pick each (cost vs rotation)
- Cross account secret sharing via resource policy
- Versioning and staging labels (AWSCURRENT, AWSPREVIOUS, AWSPENDING)
- Lab: `labs/secrets_manager_vs_parameter_store.md`
- Docs: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- Interview question: "When would you pick Parameter Store over Secrets Manager? Give me three concrete cases."

### Day 17: Identity Center (formerly AWS SSO)
- Permission sets vs IAM roles (permission set provisions a role per account)
- SCIM from Okta or Entra ID for user lifecycle
- Session duration, MFA enforcement
- Account assignment vs group assignment (group always wins for scale)
- Customer Managed Policies in permission sets (the underrated feature)
- Lab: `labs/identity_center_permission_sets.tf`
- Interview question: "Design SSO for a 50-account org with three teams. How do you keep blast radius small?"

### Day 18: Multi-account landing zone
- AWS Organizations with management, log archive, security tooling, workload OUs
- SCPs as preventive guardrails (deny what should never happen)
- Common SCP patterns: deny region, deny IAM user creation, deny CloudTrail disable, deny root user
- Control Tower vs DIY landing zone
- AWS Config aggregator in security tooling account
- Lab: `labs/multi_account_scp_examples.md`
- Reference: AWS Well-Architected Security Pillar
- Interview question: "Design a multi-account AWS landing zone for a startup with 20 engineers. What guardrails do you set?"

### Day 19: Config + Inspector + Macie
- AWS Config: resource configuration history, conformance packs, custom rules in Lambda
- Inspector v2: agentless EC2 + ECR + Lambda vulnerability scanning, free tier 15 days
- Macie: S3 PII discovery via ML classifiers, expensive at scale
- Auto-remediation via Config + Lambda or SSM Automation
- Lab: `labs/config_custom_rule.py`
- Interview question: "How would you build a control that auto-remediates a public S3 bucket within 60 seconds?"

### Day 20: Detection engineering on AWS
- Building detections from CloudTrail (Athena queries, Lake SQL)
- High-signal events: ConsoleLogin without MFA, GetCallerIdentity from new IP, root user activity, IAM policy changes
- Detection-as-code with cdk-nag, prowler, ScoutSuite
- Threat intel correlation (GuardDuty + Datadog + custom IOCs)
- Lab: `labs/cloudtrail_log_analysis_queries.md` (re-run, write 5 of your own queries)
- Interview question: "Tell me about a time you detected something subtle in CloudTrail logs."

### Day 21: AI/ML pipeline security on AWS
- SageMaker IAM (notebook role vs training job role vs endpoint role)
- S3 data lake encryption with bucket key + SSE-KMS
- Bedrock guardrails and model invocation logging
- VPC endpoints for SageMaker training (no internet egress = no data exfil)
- Model registry + signing for supply chain
- This is the Dropzone AI alignment day. Connect everything to AI workloads.
- Lab: revisit `labs/s3_bucket_takeover.tf` and `labs/iam_privesc_via_passrole.sh` framed as "what if the role belongs to a SageMaker notebook"
- Interview question: "Design end-to-end security for an AI training pipeline that ingests customer PII, trains a model in SageMaker, and serves inference via Bedrock. Walk me through every trust boundary."

---

## Daily checklist

Each day:
- [ ] 60 to 90 min on topic. Phone in another room.
- [ ] Lab runs end-to-end. If it fails, fix it before moving on.
- [ ] One sentence written: "the most dangerous thing about this service is X"
- [ ] One bullet added to CHEATSHEET.md
- [ ] Interview question answered out loud, 90 sec, recorded if possible

## Skip rules

- Cannot run the lab? Topic stays open. Move tomorrow back one day.
- Tired? Do the concept read only. Lab the next morning.
- Interview that day? Use the relevant THREAT-MODELS.md section as the prep doc.

## Stop criteria

You are ready when:
- You can answer 35 of 40 questions in INTERVIEW-Qs.md cold without notes
- You can draw a multi-account landing zone on a whiteboard with SCPs and explain blast radius
- You can name three IAM privesc paths and the conditions that block them
- You can explain envelope encryption to a non-technical interviewer in 60 seconds

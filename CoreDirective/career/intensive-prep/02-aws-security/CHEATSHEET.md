# AWS Security Cheatsheet

One-page reference. Print it, tape it next to your interview station.

---

## Top 20 IAM action verbs to know cold

| Action | What it does | Why it matters |
|---|---|---|
| `iam:PassRole` | Hand a role to a service | #1 privesc path. Always scope tightly. |
| `sts:AssumeRole` | Assume a role for temp creds | Cross-account, trust policy controls who. |
| `sts:AssumeRoleWithWebIdentity` | OIDC federation (IRSA, GitHub Actions) | EKS, CI/CD, no long-lived creds. |
| `sts:AssumeRoleWithSAML` | SAML federation (corp IdP) | Old-school SSO, mostly replaced by Identity Center. |
| `iam:CreateAccessKey` | Mint long-lived creds | Should be denied for humans (force SSO). |
| `iam:AttachUserPolicy` | Add a managed policy to a user | Privesc step 2. Audit closely. |
| `iam:PutUserPolicy` | Inline policy to a user | Same risk as AttachUserPolicy. |
| `iam:CreatePolicyVersion` | New version of a managed policy | Sneaky privesc - replace existing policy with broader version. |
| `iam:SetDefaultPolicyVersion` | Activate a policy version | Pair with CreatePolicyVersion for stealth privesc. |
| `iam:UpdateAssumeRolePolicy` | Change who can assume a role | Tampering with trust policy = back door. |
| `iam:CreateLoginProfile` | Set console password for a user | Hijack a user. |
| `iam:UpdateLoginProfile` | Change console password | Lockout target user. |
| `kms:Decrypt` | Decrypt ciphertext | The crown jewel. Audit Decrypt calls in CloudTrail. |
| `kms:CreateGrant` | Programmatic temporary key permission | Watch for service principals creating grants. |
| `kms:ScheduleKeyDeletion` | Mark CMK for deletion | Ransomware playbook step. SCP forbids this. |
| `secretsmanager:GetSecretValue` | Read a secret | Audit closely, scope to specific secrets. |
| `s3:PutBucketPublicAccessBlock` | Disable BPA | SCP forbids except for SecurityAdmin. |
| `cloudtrail:StopLogging` | Disable a trail | Attacker step 1 with admin. SCP forbids. |
| `lambda:UpdateFunctionCode` | Replace function code | Backdoor a Lambda silently. |
| `ec2:ModifyInstanceAttribute` | Change instance properties | Including disabling IMDSv2 enforcement. |

---

## Top 10 misconfigs in real audits

1. **S3 Block Public Access disabled.** Set at account + bucket. SCP forbids disabling.
2. **IMDSv1 still enabled on EC2.** Account-default to required, hop limit 1.
3. **iam:PassRole on `*` Resource.** Scope to specific safe-to-pass roles.
4. **Security group allowing 0.0.0.0/0 on 22 or 3389.** Use SSM Session Manager, no SSH ports open.
5. **RDS in public subnet with `publicly_accessible=true`.** Move to isolated subnet.
6. **CloudTrail single-region or off.** Multi-region with log file validation.
7. **Default VPC still in use.** Delete it. Use purpose-built VPCs only.
8. **No SCPs at the org level.** At minimum: deny region, deny IAM user creation, deny CloudTrail disable.
9. **MFA not enforced on console.** SCP-level deny if `aws:MultiFactorAuthPresent` is false.
10. **No Identity Center, IAM users with long-lived keys.** Migrate to Identity Center.

---

## Common privesc paths (Rhino Labs research)

1. **PassRole + Lambda CreateFunction** -> create Lambda with admin role -> invoke -> admin
2. **PassRole + ec2:RunInstances** -> launch EC2 with admin instance profile -> SSH or SSM -> admin
3. **PassRole + CloudFormation** -> deploy stack with admin role -> stack creates new admin user
4. **PassRole + Glue** -> Glue dev endpoint with admin role -> notebook gets creds
5. **iam:CreatePolicyVersion + SetDefaultPolicyVersion** -> craft new version with admin -> activate
6. **iam:UpdateAssumeRolePolicy** -> add yourself as trusted -> assume -> admin
7. **iam:AttachUserPolicy** -> attach AdministratorAccess to self
8. **iam:PutUserPolicy** -> inline admin policy on self
9. **iam:CreateAccessKey on another user** -> get their creds
10. **iam:AddUserToGroup** -> add self to admin group
11. **CodePipeline with admin role** -> source repo -> push code that calls admin APIs
12. **iam:UpdateLoginProfile on another user** -> hijack their console session
13. **sts:AssumeRole with no MFA condition** -> assume admin role from compromised low-priv user
14. **Lambda function URL with NONE auth + admin role** -> invoke from anywhere -> admin

Reference: https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/

---

## AWS service security analogs (memorize the layers)

| Service | Layer 1 (resource) | Layer 2 (network) | Layer 3 (data) |
|---|---|---|---|
| S3 | Bucket policy + IAM | BPA, VPC endpoint policy | SSE-KMS with CMK |
| KMS | Key policy + IAM + grants | VPC endpoint policy | Material in HSMs |
| Secrets Manager | Resource policy + IAM | VPC endpoint | KMS-encrypted |
| Lambda | Resource policy + IAM | VPC config (optional) | Env vars + Secrets Manager injection |
| EC2 | Instance profile (IAM) | Security group + NACL | EBS encryption, IMDSv2 |
| RDS | IAM auth (optional) + DB user/pass | Security group + isolated subnet | KMS encryption, snapshot encryption |
| DynamoDB | IAM + condition keys | VPC endpoint | KMS encryption |
| ECR | Repository policy + IAM | VPC endpoint | KMS encryption, image scanning |
| EKS | Access entries / aws-auth | Security groups + Network policies | KMS for etcd, signed images |
| API Gateway | Resource policy + auth (Cognito/IAM/Lambda) | Private API endpoint option | TLS 1.3 |

---

## Detection finding triage one-liners

| Finding | First action |
|---|---|
| InstanceCredentialExfiltration.OutsideAWS | Quarantine instance with deny-all SG, look at CloudTrail for that key |
| ConsoleLogin without MFA | Disable user, force MFA reset, audit session activity |
| CryptoCurrency:EC2/BitcoinTool.B!DNS | SSM Run Command top processes, kill miner, find entry vector, rebuild |
| Stealth:IAMUser/CloudTrailLoggingDisabled | Re-enable, treat as full compromise, rotate all creds |
| Discovery:S3/MaliciousIPCaller | Check bucket policy, look at access via S3 access logs |
| Recon:IAMUser/AnomalousASN | Verify with user, treat as compromise if not confirmed |
| Backdoor:EC2/C&CActivity.B!DNS | Network isolate, memory dump, rebuild |
| Persistence:IAMUser/AnomalousBehavior | Audit specific anomalous APIs, check for sensitive ops |

---

## CLI commands for fast triage during incidents

```bash
# Who am I?
aws sts get-caller-identity

# What did this access key do in the last 24 hours?
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIA... \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \
  --max-results 50

# What roles can this user/role assume?
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:user/suspect \
  --action-names sts:AssumeRole \
  --resource-arns "*"

# List all access keys older than 90 days
aws iam list-users --query 'Users[].UserName' --output text | \
  xargs -I {} aws iam list-access-keys --user-name {} \
    --query 'AccessKeyMetadata[?CreateDate<`'"$(date -u -d '90 days ago' +%Y-%m-%d)"'`]'

# What S3 buckets are public?
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  xargs -I {} aws s3api get-bucket-policy-status --bucket {} 2>/dev/null

# Find EC2 instances without IMDSv2 required
aws ec2 describe-instances \
  --filters "Name=metadata-options.http-tokens,Values=optional" \
  --query 'Reservations[].Instances[].InstanceId'

# Find security groups allowing 0.0.0.0/0 on sensitive ports
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.cidr,Values=0.0.0.0/0" \
            "Name=ip-permission.from-port,Values=22,3389" \
  --query 'SecurityGroups[].GroupId'

# Check if root has access keys (bad)
aws iam get-account-summary --query 'SummaryMap.AccountAccessKeysPresent'

# What is in this CloudTrail trail's S3 bucket?
aws cloudtrail describe-trails --query 'trailList[].S3BucketName'

# Quick GuardDuty findings dump
aws guardduty list-findings \
  --detector-id $(aws guardduty list-detectors --query 'DetectorIds[0]' --output text) \
  --finding-criteria '{"Criterion":{"severity":{"Gte":7.0}}}' \
  --max-results 50

# Find unused IAM roles (90+ days)
aws iam list-roles --query 'Roles[].[RoleName,RoleLastUsed.LastUsedDate]' --output text | \
  awk '$2 == "None" || $2 < "'"$(date -u -d '90 days ago' +%Y-%m-%d)"'"'

# Force-rotate an EC2 instance role's credentials (no instance restart)
aws ec2 disassociate-iam-instance-profile \
  --association-id $(aws ec2 describe-iam-instance-profile-associations \
    --filters Name=instance-id,Values=i-... --query 'IamInstanceProfileAssociations[0].AssociationId' \
    --output text)
aws ec2 associate-iam-instance-profile \
  --instance-id i-... --iam-instance-profile Name=<profile>
```

---

## Mental models to keep in your head

**IAM evaluation order:** explicit deny -> SCP -> resource policy -> identity policy -> permission boundary -> session policy. Any deny anywhere = denied.

**Three-tier VPC:** public (NAT, ALB), private (compute), isolated (databases, no internet).

**Envelope encryption:** KMS key encrypts the data key. Data key encrypts the data. KMS never sees the data.

**Defense in depth on data:** BPA + bucket policy + IAM + KMS + Object Lock + VPC endpoint policy + Macie + CloudTrail data events. Stack them.

**Detection chain:** CloudTrail (control plane) + VPC Flow (network) + GuardDuty (correlation) + SecurityHub (aggregation) + EventBridge (routing) + SOAR (response).

**Multi-account:** Org -> OU -> Account. SCPs at OU = guardrails. Identity Center = humans. CloudTrail aggregator + SecurityHub aggregator = single pane.

**Capital One pattern:** SSRF -> IMDSv1 -> role creds -> S3 GetObject. Mitigations at every step (input validation, IMDSv2, least-priv role, endpoint policy, GuardDuty).

---

## Real CVE / breach references

- **Capital One 2019**: SSRF + IMDSv1 + over-permissioned role -> 100M records. $190M settlement.
- **Code Spaces 2014**: stolen AWS creds + no MFA on root -> attacker deleted everything in 12h, killed the company.
- **Accenture 2017**: 4 buckets without BPA -> plaintext creds public. Quietly remediated.
- **Verizon 2017**: misconfigured S3 -> 6M customer records.
- **Imperva 2019**: unsecured snapshot in cloud -> API keys leaked.
- **Ubiquiti 2021**: rotated keys then re-used; insider downloaded backups -> 100GB exfil.

---

## Senior-engineer answer skeleton

When asked "how would you secure X":
1. Threats first: "the assets are X, the boundaries are Y, the realistic threats are Z."
2. Layered controls: "I'd defend with prevent (IAM, SCP), detect (GuardDuty, Config), respond (SOAR, runbook)."
3. Residual risk: "I'd accept risk on X because Y, with mitigation Z and detection W."
4. Cost / blast radius tradeoff: "this costs $A/month for B accounts, blast radius is C."

Avoid:
- Pretending everything is LOW
- Naming services without explaining why
- Skipping detection (juniors only talk about prevention)
- Forgetting cost (CFOs love a security engineer who knows the price)

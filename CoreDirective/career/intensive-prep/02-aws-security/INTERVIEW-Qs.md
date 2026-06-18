# AWS Security Interview Questions: 40 with answers

**Purpose:** Cold-call practice. Read the question, answer out loud in 60 to 120 seconds, then check against the answer. Each answer is in real-engineer voice, not LinkedIn slop.

**Drill rule:** if you cannot answer in 90 seconds without reading, you do not know it. Re-run the lab, then come back.

---

## IAM (10 questions)

### Q1. How does IAM evaluate permissions when an explicit deny and an explicit allow conflict?

Explicit deny always wins. The full evaluation order is:

1. Explicit deny anywhere (SCP, resource policy, identity policy, permission boundary, session policy) -> denied.
2. Service Control Policy at the org level. If SCP doesn't allow it, denied.
3. Resource-based policy. If it allows, allowed (unless SCP denies).
4. Identity-based policy. If neither resource nor identity policy allows, denied.
5. Permission boundary. The boundary further constrains identity policy.
6. Session policy (for STS-issued temp creds). Further constrains.

The mental model: you start with everything denied. SCPs set the ceiling. Resource and identity policies grant. Permission boundary trims the grant. Session policy trims further. Any explicit deny at any layer kills the request.

### Q2. Difference between an IAM role and a resource policy?

IAM role is an identity that can be assumed by a principal. The role has a permissions policy (what it can do) and a trust policy (who can assume it). It's the credential-issuing layer.

Resource policy is attached to a resource (S3 bucket, KMS key, Lambda function). It defines who can do what with that resource. It's the access-control layer on the resource side.

A request to a resource like an S3 bucket is allowed if the principal's identity policy allows AND the resource policy allows (or doesn't deny). They are evaluated together.

### Q3. What is iam:PassRole and why does it matter?

iam:PassRole is the IAM action you need to "hand" a role to an AWS service. Example: creating a Lambda function with an execution role requires you to PassRole that execution role to the Lambda service.

Why it matters: it's the most common privesc path. If a low-privilege user has iam:PassRole on an admin role plus the ability to create a service that runs with that role (Lambda, EC2, ECS), they escalate to admin. Fix: scope iam:PassRole to specific safe-to-pass roles, use the iam:PassedToService condition to constrain the service, never grant PassRole on wildcard.

### Q4. Permission boundary vs SCP?

Both restrict. Different scope.

SCP: applied at the AWS Org / OU level. Affects every principal in every account in that OU including root. Cannot grant, only restrict. The org admin sets these.

Permission boundary: applied to a specific IAM user or role. Caps what that principal can do, regardless of their identity policy. Used to delegate IAM admin without giving away the kingdom. Example: I let team leads create roles for their team, but with a permission boundary that prevents them from creating roles with admin power.

The combination is "intersection of all": the principal can only do what the SCP allows AND the permission boundary allows AND the identity policy grants AND the resource policy doesn't deny.

### Q5. Walk me through ABAC in AWS.

Attribute-Based Access Control = authorization decisions based on tags rather than hardcoded resource lists.

The pattern:
1. Tag the principal (user or role) with attributes like team=alpha.
2. Tag resources with the same attributes.
3. Write IAM policies using condition keys that compare principal tag to resource tag:
   `"Condition": {"StringEquals": {"aws:ResourceTag/team": "${aws:PrincipalTag/team}"}}`

One policy scales to N teams. New team = new tag value, no policy change needed.

The pitfall: if principals can self-edit their own tags, ABAC is broken. Mitigation: tag values come from the IdP (SAML or SCIM), not from self-service IAM tagging.

### Q6. What is the confused deputy problem in AWS, and how do conditions like aws:SourceArn fix it?

A trusted third party (like a vendor's AWS service) gets convinced to perform an action against your account that the third party has no right to. Classic example: AWS Cognito, AWS Backup, or a vendor that assumes a role in your account using a static external ID. If the third party's role can be assumed by anyone, an attacker forges the assumption and acts as the deputy.

Fix:
- aws:SourceAccount condition: only allow assumption if the source account matches the expected one
- aws:SourceArn condition: only allow assumption if the calling resource ARN matches an expected pattern
- ExternalId for cross-account vendor scenarios: a shared secret that the vendor must include

Example trust policy condition:
```json
"Condition": {
  "StringEquals": {"aws:SourceAccount": "123456789012"},
  "ArnLike": {"aws:SourceArn": "arn:aws:s3:::my-bucket-*"}
}
```

### Q7. Difference between IAM Federation (AssumeRoleWithSAML) and Identity Center?

IAM Federation: you set up a SAML or OIDC IdP in IAM, define IAM roles, and users in your IdP assume those roles. You manage the IAM roles per account. Each account has its own role definitions. SCIM is not integrated.

Identity Center: a service that sits above IAM. You sync users/groups from your IdP via SCIM. You define permission sets centrally. Identity Center auto-provisions IAM roles in target accounts when you assign permission sets. Single place to manage access across all accounts in your org.

Identity Center is the modern way for org-wide access. IAM Federation is still used for per-app or vendor-specific federation.

### Q8. How would you delegate IAM administration without letting admins escalate themselves?

Permission boundaries.

Pattern:
1. Create a permission boundary policy that defines the maximum power the delegated admins can grant. Example: deny iam:CreateUser, deny iam:AttachRolePolicy with admin-tagged policies, deny iam:DeleteRole on roles tagged sensitivity=high.
2. Grant the delegated admin iam:CreateRole, iam:AttachRolePolicy, iam:PutRolePolicy with a condition that requires the new role to have that boundary attached.
3. The delegated admin can create roles for their team, but every role they create is capped by the boundary.

Example condition:
```json
"Condition": {
  "StringEquals": {
    "iam:PermissionsBoundary": "arn:aws:iam::123:policy/team-boundary"
  }
}
```

### Q9. What is the difference between aws:PrincipalArn and aws:userId in conditions?

aws:PrincipalArn: the ARN of the calling principal. Stable, human-readable. Use for deny conditions ("deny if principal is not from this approved list").

aws:userId: the unique principal identifier including the session. For an assumed role, it includes a session token. Use when you need to allow a specific assumption session, not just "anyone who can assume this role".

Critical detail: aws:PrincipalArn for an assumed role is the role ARN, not the user who assumed it. To restrict by the underlying user, you need aws:userId or aws:RoleSessionName.

### Q10. Tell me about a time you found an IAM misconfig.

[Emmanuel's voice answer template, rewrite for your real story]

> "We had a Lambda that was supposed to only update items in a specific DynamoDB table. The execution role had `dynamodb:*` on `*`. CloudTrail showed the Lambda had never used anything beyond UpdateItem on that one table, but the policy permitted DeleteTable, CreateTable, and full access to every other table in the account. I tightened the policy to just `dynamodb:UpdateItem` and `dynamodb:GetItem` on the specific table ARN. Wrote a Config rule to flag any Lambda execution role with `dynamodb:*` action wildcards. The lesson was that the gap between intended permissions and granted permissions is where lateral movement starts."

---

## VPC and network (5 questions)

### Q11. Why is putting RDS in a public subnet a finding even with no public IP assigned?

Defense in depth. Even with no public IP today, the subnet has a route to the IGW. One Terraform apply that flips publicly_accessible to true (intentionally or by accident) and the database is internet-reachable. The subnet's route table is the security boundary, not the resource flag.

Best practice: RDS goes in an isolated subnet (no IGW route, no NAT route). Even if someone fat-fingers publicly_accessible=true, the subnet has nowhere to route the public traffic.

### Q12. Difference between security group, NACL, and VPC endpoint policy?

Security Group (SG):
- Stateful (return traffic auto-allowed)
- Allow rules only (no deny)
- Attached to ENI (instance, ECS task, RDS)
- Evaluated per-flow

NACL (Network ACL):
- Stateless (must allow both directions explicitly)
- Allow and deny rules
- Attached to subnet
- Evaluated per-packet
- Use for emergency blocks ("block this CIDR right now") since SGs cannot deny

VPC Endpoint Policy:
- IAM-style policy on the endpoint resource
- Limits who and what can use the endpoint
- Use to prevent data exfil ("only allow my org's principals through this S3 endpoint")

### Q13. How does VPC Flow Log help with detection? What does it miss?

Flow logs capture metadata: srcaddr, dstaddr, srcport, dstport, protocol, bytes, packets, action (ACCEPT/REJECT), tcp-flags. Useful for:
- Anomalous egress (instance shouldn't be talking to that IP)
- Reconnaissance (high REJECT count from one source)
- Data exfil (large bytes to a single external destination)

Flow logs miss:
- Payload (no HTTP headers, no DNS query names, no TLS SNI)
- DNS queries (separate Route 53 Resolver query log)
- IMDS traffic (169.254.169.254 doesn't generate flow log entries)
- Some VPC-internal traffic depending on traffic type config

GuardDuty consumes flow logs + DNS logs + CloudTrail and produces correlated findings, which is usually what you want unless you have a custom reason.

### Q14. What is a VPC endpoint and when do you use a gateway vs interface endpoint?

VPC endpoint = private connectivity from your VPC to AWS services without traversing the internet.

Gateway endpoint:
- S3 and DynamoDB only
- Free
- Routes added to your route tables, traffic stays inside AWS network

Interface endpoint (PrivateLink):
- Most other AWS services (KMS, Secrets Manager, ECR, STS, etc)
- Costs ~$0.01/hr per endpoint per AZ + data charges
- Creates an ENI in your subnet, traffic uses private IP

Use gateway endpoints always (they're free). Interface endpoints when you need control plane services from a no-internet-egress workload (e.g., compliance-isolated environments) or when you want endpoint policies on the service.

### Q15. How would VPC endpoint policies stop a compromised EC2 from exfiltrating data?

If your VPC has a gateway endpoint to S3 and you set the endpoint policy to require aws:PrincipalOrgID = your-org, every S3 call from inside the VPC must be from a principal in your AWS Organization. A compromised instance trying to upload data to an attacker's S3 bucket in a different AWS account fails at the endpoint policy.

Pair with: deny `0.0.0.0/0` outbound on the security group (so the compromised instance can't reach the public internet), force all S3 traffic through the endpoint. The data is now physically unable to leave your org's S3.

---

## KMS and crypto (4 questions)

### Q16. Explain envelope encryption to a non-technical interviewer in 60 seconds.

You don't ask the safe to encrypt your file. You ask the safe to give you a key to encrypt your file. The safe gives you that key in two forms: a plaintext copy you use right now, and an encrypted copy you store next to the file. You encrypt the file with the plaintext key, then immediately throw the plaintext key away. You keep the encrypted copy.

Later, when you need the file, you ask the safe to decrypt the encrypted key. The safe returns the plaintext key. You decrypt the file. You throw the plaintext key away again.

Why this is better than handing the safe the file: the safe has a small input limit (4 KB on KMS). Files are gigabytes. And you don't pay per gigabyte to use the safe, you only pay per key request.

### Q17. If kms:Decrypt is denied in IAM but allowed in the key policy, can I decrypt?

Depends on the key policy. KMS evaluation:

Customer-managed keys: the key policy is the root authority. If the key policy enables IAM to grant access (the default "Enable IAM User Permissions" statement), then IAM can grant Decrypt. If the key policy does NOT have that statement, only the key policy itself controls access, regardless of IAM.

So:
- Key policy allows + IAM denies = denied (explicit deny wins)
- Key policy denies + IAM allows = denied (key policy is root authority)
- Key policy delegates to IAM + IAM allows = allowed
- Key policy delegates to IAM + IAM is silent = denied (IAM didn't grant)
- Key policy explicit allow on principal = allowed regardless of IAM (in many setups)

The trap: if you remove the "Enable IAM User Permissions" statement from a key policy by accident, suddenly all your IAM grants stop working on that key. You need a key admin to put it back.

### Q18. What is a KMS grant?

A grant is a programmatic, temporary permission on a KMS key. Created with kms:CreateGrant API call. Allows specific operations (Decrypt, Encrypt, GenerateDataKey, ReEncrypt) by a specific grantee principal, optionally constrained by encryption context.

Why grants exist: services like S3 SSE-KMS, EBS encryption, RDS encryption need ad-hoc, scoped access to your CMK. They create grants programmatically to do their work without needing static IAM permissions.

Difference from key policy:
- Grants are created at runtime, not declarative
- Grants can be retired (immediate, by retiring principal) or revoked (by anyone with kms:RevokeGrant)
- Grants live for hours to days, then can be cleaned up
- Grants have constraints (EncryptionContextEquals) for fine-grained scoping

Limitation: grants cannot grant kms:* admin operations. Just data plane ops.

### Q19. What is encryption context in KMS and why does it matter?

Encryption context is additional authenticated data (AAD) bound to the encryption operation. AES-GCM uses it as part of the ciphertext authentication.

You provide it on Encrypt:
```
aws kms encrypt --plaintext "..." --encryption-context "tenant=acme,record_id=123"
```

You must provide the same context on Decrypt:
```
aws kms decrypt --ciphertext-blob ... --encryption-context "tenant=acme,record_id=123"
```

Why it matters:
- Authorization: grant constraints can require specific context, so a Decrypt only works if the context matches
- Tamper detection: if context is changed, decrypt fails
- Audit: CloudTrail logs the context, so you see what was decrypted, not just that something was

Common use: tenant=ID, record_type=PII, environment=prod. Pin context to the data attributes that should not be confused at decryption time.

---

## Compute (5 questions)

### Q20. What is IMDSv2 and why does it matter?

IMDSv1: send a GET to 169.254.169.254/latest/meta-data/ from inside an EC2 instance, get back instance metadata including the role's temp credentials. No auth, no headers.

IMDSv2: must first PUT /latest/api/token with X-aws-ec2-metadata-token-ttl-seconds header, get back a session token. Then use that token in subsequent GETs as X-aws-ec2-metadata-token header.

Why this kills SSRF attacks: most SSRF vulns let an attacker make a GET from the server but not a PUT with custom headers. IMDSv2's token requirement breaks the attack chain.

Plus IMDSv2 has a hop limit (default 1) so the response packet's IP TTL is 1, preventing it from reaching containers running through the host network.

Capital One was hacked in 2019 because IMDSv1 was on, an SSRF in the WAF let attackers fetch role creds, and they used those creds to read S3.

Enforce account-wide:
```
aws ec2 modify-instance-metadata-defaults \
  --http-tokens required \
  --http-put-response-hop-limit 1
```

### Q21. How does EKS IRSA work cryptographically?

1. EKS cluster has an OIDC identity provider URL.
2. You register that OIDC provider with IAM (or use the eksctl helper).
3. You create an IAM role with a trust policy that says: "trust this OIDC provider, and only when the JWT's `sub` claim equals system:serviceaccount:my-ns:my-sa".
4. You annotate a Kubernetes ServiceAccount with the role ARN.
5. Pods using that ServiceAccount get a projected JWT mounted at /var/run/secrets/eks.amazonaws.com/serviceaccount/token. The JWT is signed by the cluster's OIDC keys.
6. AWS SDK in the pod reads two env vars EKS injected: AWS_ROLE_ARN and AWS_WEB_IDENTITY_TOKEN_FILE.
7. SDK calls sts:AssumeRoleWithWebIdentity, passing the JWT.
8. STS verifies the JWT signature using the OIDC provider's public keys, checks the trust policy condition (sub claim must match), and returns temp credentials.
9. SDK uses temp creds for AWS API calls. Refreshes when JWT rotates (every hour by default).

The newer alternative is EKS Pod Identity (since 2023), which uses an agent on the node and a simpler trust policy with Service: pods.eks.amazonaws.com.

### Q22. Difference between ECS task role and execution role?

Execution role: used by the ECS agent (the platform) to manage the task. Pulls images from ECR, pushes logs to CloudWatch, fetches secrets from Secrets Manager to inject as env vars.

Task role: used by your application code at runtime. The role your container's AWS SDK calls assume.

Common mistake: putting all permissions on execution role. Result: your container has all the platform permissions plus its own permissions. Always split them.

Real world: execution role gets AmazonECSTaskExecutionRolePolicy plus the specific Secrets Manager / KMS access for secrets injection. Task role gets only what your code does (read this S3 prefix, write this DynamoDB table).

### Q23. How do you stop one tenant in a multi-tenant Lambda app from reading another tenant's S3 prefix?

Three layers:

1. Authorize at the API layer. Lambda authorizer in API Gateway pulls tenant from JWT. The Lambda function code uses tenant from the validated JWT, not from request body.

2. Use session policy. The upstream invoker assumes a role and includes a session policy scoped to the specific tenant prefix. Even if the function has broad S3 permissions, the assumed session is scoped tighter.

3. Use ABAC. Tag S3 objects or buckets with tenant=X. Function role has access only when aws:ResourceTag/tenant matches a session tag set at invocation time.

Defense in depth: do all three. JWT validation as the primary control, session policy as a backstop, ABAC as the third layer.

### Q24. What is a Lambda function URL and what is the auth model?

A function URL is a built-in HTTPS endpoint for a Lambda function. No API Gateway needed. Two auth types:

- AWS_IAM: every request must be SigV4 signed. Requires the caller to have lambda:InvokeFunctionUrl on the function. Use for service-to-service calls.

- NONE: no auth, anyone on the internet can call it. Use only when the function is behind another auth layer (CloudFront with signed URLs, custom auth in the function code) or for true public webhooks.

Pitfall: people set NONE and forget to add auth in the function. Treat NONE like making a public S3 bucket: deliberate, documented, monitored.

---

## Storage and data (5 questions)

### Q25. How would you secure an S3 bucket holding PII?

Layered:

1. Block Public Access at account AND bucket level. The kill switch.
2. ACLs disabled (bucket ownership = BucketOwnerEnforced). Modern S3 doesn't need ACLs.
3. Bucket policy enforcing TLS (deny aws:SecureTransport=false), KMS encryption (deny PutObject without x-amz-server-side-encryption=aws:kms), and aws:PrincipalOrgID = my-org so the bucket only answers to principals in my AWS Organization.
4. Encryption at rest with a customer-managed KMS key, bucket key enabled to reduce KMS API costs.
5. Versioning ON. Object Lock in compliance mode if regulated (irreversible retention).
6. Server access logs to a separate log bucket in a separate account.
7. CloudTrail data events on the bucket so I see every GetObject.
8. Macie scanning weekly to detect PII drift into unexpected prefixes.
9. SCP at the org level forbidding s3:PutBucketPublicAccessBlock unless the principal is the SecurityAdmin role.

If it's a static site bucket: in front of CloudFront with OAC (Origin Access Control), bucket policy allows only that CloudFront distribution.

### Q26. Walk me through the Capital One breach.

Capital One had a web application protected by a WAF. The WAF (ModSecurity-based on EC2) had an SSRF vulnerability. An attacker, Paige Thompson, used the SSRF to make the WAF instance fetch http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name> from itself.

That's the EC2 metadata service (IMDS). With IMDSv1 enabled, any GET returns the instance role's temp credentials. The attacker got back the role's AccessKey, SecretKey, and SessionToken.

The role had broad S3 permissions. The attacker used the credentials to call ListBuckets, then GetObject across multiple buckets. They exfiltrated 100 million customer records, applications for credit, social security numbers, bank account numbers.

Detection failed because GetCallerIdentity from an outside IP didn't fire any alarm at the time. The breach was found weeks later when the attacker bragged about it on GitHub and Slack.

What would have stopped it:
1. IMDSv2 required (the SSRF would have failed on the PUT requirement)
2. Tighter role permissions (the WAF didn't need read on those S3 buckets)
3. GuardDuty would have flagged InstanceCredentialExfiltration.OutsideAWS
4. VPC endpoint for S3 with aws:PrincipalOrgID condition would have blocked the data movement

Capital One paid an $80M civil money penalty to the OCC in 2020, settled the consumer class action for $190M in 2022, and consented to a separate Federal Reserve order. There was no FTC settlement. The lesson: misconfig of three things compounded. Defense in depth would have stopped it at any layer.

### Q27. What is S3 Object Lock and when do you use it?

Object Lock = WORM (write once read many) for S3 objects. Two modes:

- Governance mode: most users cannot delete, but root or principals with bypass-governance permissions can. Good for legal hold.
- Compliance mode: nobody can delete, not even root, until the retention period expires. Irreversible.

Use cases:
- Backup vaults (ransomware resilience)
- Audit logs (CloudTrail, VPC Flow logs) requiring tamper-proof retention
- Legal/regulatory holds

Pitfall: in compliance mode, you cannot delete the bucket until every object's retention has passed. If you set 7-year retention, you cannot delete for 7 years. Misconfigured Object Lock is a real billing risk.

### Q28. Difference between SSE-S3, SSE-KMS, and SSE-C?

SSE-S3 (now called SSE with Amazon S3-managed keys, or AES-256):
- AWS manages the key entirely
- No KMS API calls, no extra cost
- No granular access control on the encryption itself
- Use when you just need encryption-at-rest checkbox

SSE-KMS:
- Uses a KMS key (AWS-managed default or a CMK you control)
- Each object gets envelope-encrypted under a KMS data key
- KMS Decrypt API calls are logged in CloudTrail (audit win)
- Costs more (KMS API calls, although bucket key reduces this 99%)
- Use when you need access control via the KMS key policy

SSE-C (customer-provided keys):
- You provide the key on every PutObject and GetObject call
- AWS doesn't store the key
- Niche use case: extreme key custody requirements

Default in 2026: SSE-S3 if compliance is checkbox. SSE-KMS with a CMK if compliance demands key custody and audit.

### Q29. Tell me about a famous S3 leak and how to prevent it.

Multiple to choose from:
- Accenture (2017): 4 buckets containing plaintext credentials publicly readable
- Verizon (2017): 6M customer records exposed via misconfigured bucket
- Pentagon contractor (2017): 1.8B social media posts in a public bucket
- Capital One (2019): IMDS chain rather than public bucket
- Imperva (2019): API keys in a publicly exposed snapshot

Pattern is the same: developer creates bucket "for testing", forgets to set BPA, leaves it public, dumps real data, walks away.

Prevention:
- Block Public Access ON at account level (s3control put-public-access-block)
- SCP denying s3:PutBucketPublicAccessBlock and s3:DeletePublicAccessBlock for non-security roles
- Macie continuously scanning for PII in S3
- Config rule s3-bucket-public-read-prohibited
- AWS Foundational Security Best Practices control [S3.1] Block Public Access

---

## Detection and response (6 questions)

### Q30. What does CloudTrail not capture?

- Data events by default (S3 object access, Lambda invokes, DynamoDB queries). Must enable explicitly. Cost extra.
- Network traffic. Use VPC Flow Logs.
- DNS queries. Use Route 53 Resolver query logs.
- OS-level activity (file access, process exec inside an EC2 instance).
- IMDS access (169.254.169.254 requests don't show in CloudTrail).
- Console session activity within a service (the click-by-click in the console).
- Some service internals: SSM Run Command shows up well-instrumented, but Glue ETL step-by-step does not.
- Sub-second timing precision.

### Q31. How does GuardDuty differ from SecurityHub?

GuardDuty: detection. Generates findings from telemetry it consumes (CloudTrail, VPC Flow, DNS, EKS audit, S3 data events, RDS Aurora login monitoring). Behavioral and signature-based.

SecurityHub: aggregation. Pulls findings from GuardDuty, Inspector, Macie, Config, IAM Access Analyzer, and 50+ partners (Snyk, CrowdStrike, Wiz, Trend Micro). Normalizes to ASFF. Runs compliance standards (CIS, AWS FSBP, PCI DSS, NIST 800-53).

Relationship: GuardDuty produces. SecurityHub aggregates and adds compliance.

### Q32. How would you detect credential exfiltration?

Multiple signals layered:

1. GuardDuty UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS - fires when an instance role's credentials are used from outside AWS.

2. CloudTrail-based detections: GetCallerIdentity from a new IP for a given principal. New ASN for a principal. Multiple AccessDenied in a short window from one access key (suggests credential testing).

3. VPC Flow Logs spike on egress to a single external destination from one instance.

4. SecurityHub aggregates and de-dupes the above into one finding.

5. Detection-as-code: write a Lambda that runs every 5 min, queries CloudTrail Lake for sessions with mfaAuthenticated=false on assumed roles that should always have MFA, alerts on hits.

The fast-path in incident response: pull all CloudTrail events for the suspected access key in the last 24 hours, look for IAM operations (CreateUser, AttachRolePolicy, CreateAccessKey), KMS Decrypt of suspicious resources, and S3 GetObject from non-baseline IPs.

### Q33. An attacker has admin in your account. They want to delete CloudTrail. How do you stop or detect that?

Layers:

1. Multi-region trail: you'd have to delete all of them. More events for the attacker, more chance of detection.

2. Log file integrity: CloudTrail digest files are signed by AWS. If logs are tampered with after delivery, validation fails.

3. Log destination: ship CloudTrail logs to a dedicated log archive account with a one-way write pattern. Workload accounts cannot delete the log bucket.

4. S3 Object Lock on the log bucket in compliance mode: even root cannot delete logs once written.

5. SCP at the org level: deny cloudtrail:StopLogging, cloudtrail:DeleteTrail, cloudtrail:UpdateTrail for everyone except a specific break-glass role pattern.

6. Real-time alerting: EventBridge rule on cloudtrail:StopLogging events fires PagerDuty. By the time the attacker logs back in 2 minutes later to delete more, you're paged.

7. GuardDuty Stealth:IAMUser/CloudTrailLoggingDisabled fires automatically.

The combo: SCP prevents the action, log archive plus Object Lock prevents the destruction, alerting catches attempt.

### Q34. Tell me about a time you found something subtle in CloudTrail.

[Real story Emmanuel should fill in. Template below.]

> "We had a Lambda triggering off SQS that was supposed to write to one DynamoDB table. CloudTrail showed the function role was also doing PutItem on a different table once a week. Turned out an old config in S3 was being read by the Lambda for backwards-compat, and someone had updated that config to point to the wrong table. The signal was the DynamoDB target mismatch with the function's intended output. The fix was tightening the Lambda role to dynamodb:PutItem on a single table ARN, plus a CloudWatch alarm on cross-table writes. The lesson: 'authorized' and 'intended' aren't the same. Most low-and-slow attacks hide in the gap."

### Q35. How do you build an AWS landing zone for compliance audit (SOC 2, HIPAA)?

Foundation:
1. AWS Organizations with management, security (log-archive + security-tooling), workload OUs.
2. Identity Center for human access. No IAM users.
3. CloudTrail multi-region trail in every account, log destination is the log archive account, Object Lock on the log bucket.
4. Config recording all resources in every account, aggregated to security tooling.
5. GuardDuty on in every account, delegated admin to security tooling.
6. SecurityHub on in every account with AWS FSBP and (for HIPAA) HIPAA Security standard.
7. Macie for PII scanning on S3 buckets in workload accounts.

Required for HIPAA specifically:
- BAA signed with AWS (legal)
- All HIPAA data in HIPAA-eligible services only (list at aws.amazon.com/compliance/hipaa-eligible-services-reference)
- Encryption at rest and in transit, no exceptions
- Access logging on every PHI bucket and database

For SOC 2:
- Documented access reviews quarterly (Identity Center reports, IAM Access Analyzer)
- Change management evidence (CloudTrail + git history of Terraform)
- Incident response runbooks tested at least annually (tabletop exercises)
- Backup and recovery proven via Restore tests

Make the auditor's life easy: give them read-only Identity Center access scoped to relevant accounts, point them at SecurityHub findings tagged compliance.

---

## AI/ML and edge cases (5 questions)

### Q36. Design end-to-end security for an AI training pipeline that ingests customer PII, trains in SageMaker, and serves via Bedrock.

This is the Dropzone AI / OneDigital style question. Trust boundaries:

1. Ingest: customer data lands in an S3 bucket with KMS-CMK encryption, Block Public Access on, bucket policy denies non-org principals, Macie scans for PII classification, server access logs to log archive account.

2. Pre-processing: SageMaker Processing job in a VPC with no internet egress (private subnets, S3 + ECR + STS + KMS endpoints only). Job role has read on the input bucket, write on a processed-data bucket (separate prefix), no other AWS permissions.

3. Training: SageMaker Training job, also no-internet-egress. Training role can read processed data, write model artifacts to a model bucket. KMS keys for both buckets are different so that compromise of one role doesn't cascade.

4. Model registry: model artifacts go to SageMaker Model Registry, signed with code signing (or a separate signing pipeline). Models are versioned and tagged with the data lineage (training-data-version=X).

5. Serving via Bedrock or SageMaker endpoint:
   - If Bedrock: VPC endpoint for Bedrock, enable model invocation logging, use Bedrock Guardrails for content filtering and PII redaction at output.
   - If SageMaker: private endpoint, IAM auth on the endpoint, request logging.

6. Governance:
   - SageMaker notebook execution role separate from training role (notebooks can read sample data, not production data)
   - All API calls logged via CloudTrail
   - Bedrock model invocation logs to S3 with field-level redaction
   - Drift detection on model performance (Model Monitor)

7. Detection:
   - CloudTrail on Bedrock InvokeModel for unusual prompt sizes
   - GuardDuty for IAM anomalies
   - Custom detection: prompt injection attempts (large input, unusual tokens) flagged for review

Reference: my SQUIRE_THREAT_MODEL approach maps STRIDE per component plus MITRE ATLAS for adversarial ML attacks.

### Q37. How do you stop prompt injection from extracting customer data through an AWS-hosted LLM?

Multiple layers (none alone is sufficient):

1. Input validation: Bedrock Guardrails or custom NeMo Guardrails sidecar. Filter prompts containing system-instruction-overrides, "ignore previous instructions" patterns, role injection attempts.

2. Output filtering: Presidio or Bedrock Guardrails on output. Strip PII patterns (SSN, CC, email) from model outputs before they hit the user.

3. Privilege minimization: the model itself has no IAM credentials. The orchestrator code does. The model produces structured tool-use requests; the orchestrator validates those against an allowlist before executing.

4. Tool allowlists: never let the model call arbitrary AWS APIs. Define a small set of tools (search, lookup_user, email_send) and reject anything else.

5. Context isolation: per-tenant retrieval. The RAG layer only retrieves chunks from the requesting tenant's namespace. Cross-tenant retrieval is blocked at the vector DB query.

6. Audit: log every prompt, every tool call, every output to a tamper-resistant trail (Langfuse + S3 with Object Lock). Required for incident review.

7. Rate limit and cost ceiling: per-call cost cap, daily cost ceiling. Stops a runaway prompt-injection loop from emptying your AWS bill.

8. Red-team: regular adversarial testing with MITRE ATLAS techniques (Prompt Injection AML.T0051, Evade ML Model AML.T0015).

### Q38. What is AWS Verified Access and where does it fit in Zero Trust?

AWS Verified Access (formerly AWS Apps2VPC) is a Zero Trust application access service. It evaluates every request against trust providers (IAM Identity Center, OIDC IdPs like Okta, plus device trust providers like Jamf, CrowdStrike, JumpCloud) before allowing access to private apps.

Architecture: app sits in a VPC, AVA endpoint sits in front. User browser hits AVA endpoint, AVA evaluates trust signals (user identity, device posture, IP, time), forwards to app if approved.

Use case: replace VPN for engineering app access. No more "be on the corporate VPN". Just "be authenticated via Identity Center AND have a managed device".

Where it fits: it's AWS's answer to Cloudflare Access, Tailscale Funnel, Google BeyondCorp. For workloads where you control AWS, AVA is the path of least friction. For multi-cloud, Cloudflare Access is more flexible.

### Q39. How do you secure CrowdStrike telemetry on AWS?

Two patterns:

1. CrowdStrike Falcon agent on EC2 / EKS nodes:
   - Agent installed via SSM or DaemonSet
   - Outbound HTTPS to CrowdStrike cloud (allow-listed in egress policy)
   - Falcon connects via API to CrowdStrike SaaS, no inbound to your VPC

2. CrowdStrike Cloud Security (CSPM) reading AWS Config / CloudTrail:
   - Cross-account IAM role created in your AWS Organization
   - Trust policy allows CrowdStrike's AWS account to AssumeRole
   - External ID required (prevents confused deputy)
   - Role has SecurityAudit and CloudTrailReadOnlyAccess managed policies

For Dropzone AI specifically: the AI agent ingests CrowdStrike alerts via API. Securing that flow:
- API token stored in Secrets Manager with rotation
- Agent runs in a private VPC, calls CrowdStrike API via NAT or VPC endpoint
- All ingestion logged for audit
- Output (the AI's analysis) gates on a human-in-the-loop policy for high-severity alerts

### Q40. Tell me about a time you found a misconfig in AWS.

[Emmanuel real story template]

> "Running a security review for a client, I noticed their Terraform was provisioning RDS instances with publicly_accessible=true because the team thought it was needed for the bastion host. The bastion was on a public subnet, the database was on a public subnet, both had security groups locking access by IP, but anyone who learned the bastion's CIDR or guessed it could potentially connect to the database directly because they had matching SG rules. I migrated the database to an isolated subnet, removed publicly_accessible, locked the SG to only the bastion's SG (not its IP), and added an SCP at the org level forbidding rds:CreateDBInstance with PubliclyAccessible=true. Wrote a Terraform validation rule (cdk-nag for them) so the same misconfig couldn't be re-introduced. The lesson was that 'works fine' and 'secure' often diverge in cloud, and you have to look at the routing table, not just the resource flag."

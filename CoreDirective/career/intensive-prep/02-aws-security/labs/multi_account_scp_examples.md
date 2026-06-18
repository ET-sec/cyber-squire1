# Lab: Multi-account landing zone SCPs

**Objective:** Walk through the SCPs every production AWS Org should run. Understand the difference between preventive (SCP) and detective (Config) controls.

**What an interviewer will ask:**
1. "Design a multi-account AWS landing zone for a startup with 20 engineers."
2. "What is an SCP and how does it differ from an IAM policy?"
3. "Give me four SCPs every account should have."

---

## Org structure

```
Root
|-- Management (billing, AWS Org root, IAM Identity Center)
|-- Security
|   |-- log-archive (immutable CloudTrail + Config destination)
|   |-- security-tooling (GuardDuty, SecurityHub, Macie aggregator)
|-- Workloads
|   |-- Production OU
|   |   |-- prod-payments
|   |   |-- prod-platform
|   |-- Non-Production OU
|   |   |-- staging
|   |   |-- dev
|-- Sandbox (developer playgrounds, isolated)
|-- Suspended (decommissioning accounts)
```

Place SCPs at OU level, not account level. Move accounts between OUs to change their guardrails.

---

## SCP 1: Region restriction (everyone except security tooling)

Reduces blast radius. Attackers cannot spin up resources in regions you do not monitor.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideApprovedRegions",
    "Effect": "Deny",
    "NotAction": [
      "iam:*",
      "organizations:*",
      "sts:*",
      "cloudfront:*",
      "route53:*",
      "support:*",
      "trustedadvisor:*",
      "waf:*"
    ],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "us-west-2"]
      }
    }
  }]
}
```

The NotAction list covers global services (IAM, Org, IAM Identity Center, CloudFront) which do not have a region. Without that exception, even an IAM CreateUser would be denied.

---

## SCP 2: Protect security tooling

Stop anyone except a designated break-glass role from disabling CloudTrail, GuardDuty, Config, SecurityHub.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ProtectSecurityServices",
    "Effect": "Deny",
    "Action": [
      "cloudtrail:DeleteTrail",
      "cloudtrail:StopLogging",
      "cloudtrail:UpdateTrail",
      "cloudtrail:PutEventSelectors",
      "guardduty:DeleteDetector",
      "guardduty:DisassociateFromMasterAccount",
      "guardduty:StopMonitoringMembers",
      "guardduty:UpdateDetector",
      "config:DeleteConfigRule",
      "config:DeleteConfigurationRecorder",
      "config:DeleteDeliveryChannel",
      "config:StopConfigurationRecorder",
      "securityhub:DeleteHub",
      "securityhub:DisableSecurityHub",
      "securityhub:DisassociateFromMasterAccount"
    ],
    "Resource": "*",
    "Condition": {
      "ArnNotLike": {
        "aws:PrincipalArn": [
          "arn:aws:iam::*:role/AWSReservedSSO_SecurityBreakGlass_*"
        ]
      }
    }
  }]
}
```

Note: a determined attacker with admin can still create a new role with that name pattern. Mitigation: combine with iam:CreateRole denial, monitoring on role creation events, and an out-of-band SAML/STS path for emergency security team access.

---

## SCP 3: Block IAM user creation

Force everyone through Identity Center. No long-lived users with passwords.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyIAMUserCreation",
    "Effect": "Deny",
    "Action": [
      "iam:CreateUser",
      "iam:CreateAccessKey",
      "iam:CreateLoginProfile"
    ],
    "Resource": "*",
    "Condition": {
      "ArnNotLike": {
        "aws:PrincipalArn": [
          "arn:aws:iam::*:role/IAMBootstrap"
        ]
      }
    }
  }]
}
```

Exception: the bootstrap role used during account creation. Once provisioned, it should be deleted and the SCP enforced.

---

## SCP 4: Block root user

Root should never be used. Period.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyRootActions",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringLike": {
        "aws:PrincipalArn": "arn:aws:iam::*:root"
      }
    }
  }]
}
```

Some account-level actions still require root (closing the account, changing root password, certain support cases). For those, use the AWS Org payer account's emergency procedure.

---

## SCP 5: Require encryption on EBS volumes

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyUnencryptedEBS",
    "Effect": "Deny",
    "Action": [
      "ec2:RunInstances",
      "ec2:CreateVolume"
    ],
    "Resource": "*",
    "Condition": {
      "Bool": {"ec2:Encrypted": "false"}
    }
  }]
}
```

Pair with account-level default encryption setting:
```
aws ec2 enable-ebs-encryption-by-default
```

---

## SCP 6: Deny disabling Block Public Access on S3

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyDisablingPublicAccessBlock",
    "Effect": "Deny",
    "Action": [
      "s3:PutAccountPublicAccessBlock",
      "s3:PutBucketPublicAccessBlock"
    ],
    "Resource": "*",
    "Condition": {
      "ArnNotLike": {
        "aws:PrincipalArn": [
          "arn:aws:iam::*:role/AWSReservedSSO_SecurityBreakGlass_*"
        ]
      }
    }
  }]
}
```

---

## SCP 7: Sandbox-only resource cap

Apply this only to the Sandbox OU. Stops developers from running expensive resources.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "SandboxInstanceTypeLimit",
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {
      "StringNotEquals": {
        "ec2:InstanceType": ["t3.micro", "t3.small", "t3.medium"]
      }
    }
  }, {
    "Sid": "SandboxNoExpensiveServices",
    "Effect": "Deny",
    "Action": [
      "rds:Create*",
      "redshift:Create*",
      "sagemaker:CreateTrainingJob",
      "elasticmapreduce:RunJobFlow"
    ],
    "Resource": "*"
  }]
}
```

---

## SCP vs IAM policy

This is a high-frequency interview question.

| Aspect | SCP | IAM policy |
|---|---|---|
| Where attached | OU or account | User, group, role |
| Effect on root user | Yes (root is constrained by SCPs) | No (root bypasses IAM denials except SCPs) |
| Default behavior when no SCP attached | All allowed | All denied |
| Can grant permissions | No (only restrict) | Yes |
| Can deny permissions | Yes | Yes |
| Inheritance | Yes (child OU inherits parent SCPs, intersection applied) | No |
| Evaluation order | First (before IAM) | After SCP |

**SCPs are guardrails. They cannot grant. They define the maximum possible permission set within an account.**

If SCP says deny: nothing else matters, the action is denied.
If SCP says allow (or no statement): IAM is then evaluated normally.

---

## Common interview answer

> "For a 50-account org, I structure it as Management, Security (log-archive + security-tooling), Workloads OU split into prod and non-prod, Sandbox, and Suspended for decommissioning. SCPs at OU level: region restriction to keep blast radius tight, protection for CloudTrail and GuardDuty so attackers can't disable detection, deny IAM user creation to force everyone through Identity Center, deny root actions, deny disabling S3 Block Public Access, and require EBS encryption. Sandbox gets an extra SCP capping instance types and expensive services. Every workload account has Config, GuardDuty, SecurityHub on, all aggregating to the security-tooling account. Identity Center with permission sets: Auditor, Developer (with ABAC tag matching), and SecurityBreakGlass with 1-hour sessions. For the SOC, all GuardDuty/SecurityHub findings event-bridged to the SOAR. The pattern keeps it simple: prevent in SCPs, detect in Config and GuardDuty, route in SecurityHub, respond in SOAR."

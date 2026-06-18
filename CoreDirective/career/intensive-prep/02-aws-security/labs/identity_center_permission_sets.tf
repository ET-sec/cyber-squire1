###############################################################################
# Lab: Identity Center (formerly AWS SSO) permission sets
# Objective: Build a small landing zone with three permission sets across two
#   accounts. Demonstrate group-based assignment, session duration, MFA.
#
# What an interviewer will ask:
#   1. "Design SSO for a 50-account org with three teams. Blast radius?"
#   2. "What is the difference between a permission set and an IAM role?"
#   3. "Difference between Identity Center and IAM Federation?"
#
# Note: this assumes Identity Center is already enabled in the management
# account and an external IdP (Okta or Entra) is provisioning users via SCIM.
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = "us-east-1" }

variable "ic_instance_arn" {
  description = "Identity Center instance ARN. Get with: aws sso-admin list-instances"
}
variable "identity_store_id" {
  description = "Identity Store ID for group lookups."
}
variable "workload_account_ids" {
  type    = list(string)
  default = ["111111111111", "222222222222"]
}

###############################################################################
# Permission set 1: ReadOnly auditors
###############################################################################
resource "aws_ssoadmin_permission_set" "auditor" {
  name             = "Auditor"
  description      = "Read-only across all services. 4-hour session."
  instance_arn     = var.ic_instance_arn
  session_duration = "PT4H"
}

resource "aws_ssoadmin_managed_policy_attachment" "auditor_readonly" {
  instance_arn       = var.ic_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.auditor.arn
}

# Even auditors should not see secrets
resource "aws_ssoadmin_permission_set_inline_policy" "auditor_deny_secrets" {
  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Action = [
        "secretsmanager:GetSecretValue",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "kms:Decrypt"
      ]
      Resource = "*"
    }]
  })
  instance_arn       = var.ic_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.auditor.arn
}

###############################################################################
# Permission set 2: Developer (read-write within tagged resources)
###############################################################################
resource "aws_ssoadmin_permission_set" "developer" {
  name             = "Developer"
  description      = "Read-write on resources tagged team={dev-team}, MFA required."
  instance_arn     = var.ic_instance_arn
  session_duration = "PT8H"
}

# Developer permissions limited via ABAC - the principal's team tag must match
resource "aws_ssoadmin_permission_set_inline_policy" "developer" {
  inline_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyWithoutMFA"
        Effect = "Deny"
        NotAction = ["sts:GetSessionToken", "iam:ChangePassword", "iam:GetUser",
                     "sso:*", "signin:*"]
        Resource = "*"
        Condition = {
          BoolIfExists = { "aws:MultiFactorAuthPresent" = "false" }
        }
      },
      {
        Sid    = "ReadAll"
        Effect = "Allow"
        Action = [
          "ec2:Describe*", "s3:Get*", "s3:List*", "lambda:Get*", "lambda:List*",
          "logs:*", "cloudwatch:Get*", "cloudwatch:List*", "cloudwatch:Describe*"
        ]
        Resource = "*"
      },
      {
        Sid    = "WriteWithMatchingTag"
        Effect = "Allow"
        Action = ["ec2:StartInstances", "ec2:StopInstances", "ec2:RebootInstances",
                  "ec2:TerminateInstances", "lambda:Invoke*", "lambda:Update*"]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/team" = "${aws:PrincipalTag/team}"
          }
        }
      }
    ]
  })
  instance_arn       = var.ic_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer.arn
}

###############################################################################
# Permission set 3: SecurityAdmin (break-glass for security team)
###############################################################################
resource "aws_ssoadmin_permission_set" "security_admin" {
  name             = "SecurityAdmin"
  description      = "Full admin. 1-hour session. Logged and alerted."
  instance_arn     = var.ic_instance_arn
  session_duration = "PT1H"
}

resource "aws_ssoadmin_managed_policy_attachment" "security_admin" {
  instance_arn       = var.ic_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.security_admin.arn
}

###############################################################################
# Group lookups (groups are managed by SCIM from the IdP)
###############################################################################
data "aws_identitystore_group" "auditors" {
  identity_store_id = var.identity_store_id
  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = "auditors"
    }
  }
}

data "aws_identitystore_group" "developers" {
  identity_store_id = var.identity_store_id
  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = "developers"
    }
  }
}

data "aws_identitystore_group" "security" {
  identity_store_id = var.identity_store_id
  alternate_identifier {
    unique_attribute {
      attribute_path  = "DisplayName"
      attribute_value = "security"
    }
  }
}

###############################################################################
# Assignments: which group gets which permission set in which account
###############################################################################
locals {
  assignments = flatten([
    for acct in var.workload_account_ids : [
      { group = data.aws_identitystore_group.auditors.group_id,
        ps    = aws_ssoadmin_permission_set.auditor.arn,
        acct  = acct },
      { group = data.aws_identitystore_group.developers.group_id,
        ps    = aws_ssoadmin_permission_set.developer.arn,
        acct  = acct },
      { group = data.aws_identitystore_group.security.group_id,
        ps    = aws_ssoadmin_permission_set.security_admin.arn,
        acct  = acct }
    ]
  ])
}

resource "aws_ssoadmin_account_assignment" "this" {
  for_each = { for i, a in local.assignments : "${a.group}-${a.acct}-${md5(a.ps)}" => a }

  instance_arn       = var.ic_instance_arn
  permission_set_arn = each.value.ps
  principal_id       = each.value.group
  principal_type     = "GROUP"
  target_id          = each.value.acct
  target_type        = "AWS_ACCOUNT"
}

###############################################################################
# WHAT TO STUDY
###############################################################################
# Identity Center vs old IAM federation:
#   - Old way: SAML/OIDC -> IAM identity provider -> AssumeRoleWithSAML to
#     specific IAM roles you defined in each account.
#   - New way: Identity Center has its own user store (or syncs via SCIM from
#     Okta/Entra). Permission sets are templates that get materialized as IAM
#     roles in target accounts when assigned. The role naming follows
#     AWSReservedSSO_<PermissionSetName>_<hash>.
#
# Permission set vs IAM role:
#   - Permission set = abstract template. Defines policies, session duration.
#   - When assigned to a group + account, Identity Center creates an actual
#     IAM role in that account with those policies.
#   - One permission set assigned to N accounts = N actual IAM roles.
#   - Updating the permission set updates all materialized roles.
#
# Group vs user assignment:
#   - Always assign to groups, never users. Even for one person, make a group
#     of one. Otherwise, when they leave or change teams, the cleanup is manual.
#
# Session duration:
#   - Auditors: 4h. They are reading and reviewing.
#   - Developers: 8h. Workday session.
#   - SecurityAdmin: 1h. Force re-auth often. Pair with alerting on
#     CreateRole, AttachRolePolicy, DeleteUser etc when the actor is a
#     SecurityAdmin role assumption.
#
# Customer-managed policies in permission sets:
#   - You can attach a policy that is created and maintained in the target
#     account, not in the management account. This is the underrated feature.
#     Use case: "all developers in account 222 also get access to this app's
#     policy that lives in account 222". Avoids cross-account policy ARNs.
#
# Blast radius design:
#   - SecurityAdmin permission set in EVERY account is broad blast radius.
#     Mitigations:
#     a. Short session (1h)
#     b. Require MFA (forced via Identity Center settings)
#     c. CloudTrail alerting on assumption events
#     d. SCP at OU level that denies anything destructive (CreateUser,
#        DeleteAccount, billing, root activity) for all roles except a single
#        break-glass role provisioned out-of-band
#     e. Privileged Access Management (Teleport, AWS SSM Session Manager)
#        for any production console use
###############################################################################

# Workload identity, the first-class way.
#
# On OCI this same trust required a hand-built RFC 8693 token exchange
# through an Identity Domain (see cd-oci-infrastructure and DR-02). AWS
# supports GitHub's OIDC issuer natively: one provider, one role, one
# condition block. Both implementations are pinned to this repo and main,
# so a fork or feature branch cannot mint cloud credentials on either cloud.

data "aws_caller_identity" "current" {}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  # Thumbprint is ignored for issuers fronted by trusted CAs but the field
  # is required by the API; this is GitHub's published root.
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "ci_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/${var.github_branch}"]
    }
  }
}

resource "aws_iam_role" "ci_drift" {
  name                 = "cd-ci-drift-readonly"
  assume_role_policy   = data.aws_iam_policy_document.ci_trust.json
  max_session_duration = 3600
}

# Read-only, scoped to what the nightly drift plan needs to refresh state:
# the security-plane resources themselves. No mutation anywhere.
data "aws_iam_policy_document" "ci_drift_read" {
  statement {
    sid    = "ReadEvidenceVaultConfig"
    effect = "Allow"
    actions = [
      "s3:GetBucket*",
      "s3:GetEncryptionConfiguration",
      "s3:GetLifecycleConfiguration",
      "s3:GetAccelerateConfiguration",
      "s3:ListBucket",
      "s3:ListBucketVersions",
    ]
    resources = [aws_s3_bucket.evidence.arn]
  }

  statement {
    sid       = "ReadVaultKeyConfig"
    effect    = "Allow"
    actions   = ["kms:DescribeKey", "kms:GetKeyPolicy", "kms:GetKeyRotationStatus", "kms:ListResourceTags", "kms:Decrypt"]
    resources = [aws_kms_key.evidence.arn]
  }

  statement {
    # ListAliases supports no resource scoping.
    sid       = "ListKeyAliases"
    effect    = "Allow"
    actions   = ["kms:ListAliases"]
    resources = ["*"]
  }

  statement {
    sid    = "ReadOwnIamConfig"
    effect = "Allow"
    actions = [
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListRolePolicies",
      "iam:ListAttachedRolePolicies",
      "iam:GetUser",
      "iam:GetUserPolicy",
      "iam:ListUserPolicies",
      "iam:ListAttachedUserPolicies",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/cd-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/cd-*",
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/cd-*",
    ]
  }

  statement {
    sid       = "ReadOidcProvider"
    effect    = "Allow"
    actions   = ["iam:GetOpenIDConnectProvider"]
    resources = [aws_iam_openid_connect_provider.github.arn]
  }

  statement {
    sid       = "ReadBreakglassConfig"
    effect    = "Allow"
    actions   = ["secretsmanager:DescribeSecret", "secretsmanager:GetResourcePolicy"]
    resources = [aws_secretsmanager_secret.breakglass_oci.arn]
  }

  statement {
    sid       = "ReadTrailConfig"
    effect    = "Allow"
    actions   = ["cloudtrail:GetTrail", "cloudtrail:GetTrailStatus", "cloudtrail:GetEventSelectors", "cloudtrail:ListTags"]
    resources = ["arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/cd-*"]
  }

  statement {
    sid       = "ReadEventRuleConfig"
    effect    = "Allow"
    actions   = ["events:DescribeRule", "events:ListTargetsByRule", "events:ListTagsForResource"]
    resources = ["arn:aws:events:${var.aws_region}:${data.aws_caller_identity.current.account_id}:rule/cd-*"]
  }

  statement {
    sid       = "ReadAlertLambdaConfig"
    effect    = "Allow"
    actions   = ["lambda:GetFunction", "lambda:GetPolicy", "lambda:ListVersionsByFunction", "lambda:GetFunctionCodeSigningConfig"]
    resources = ["arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:cd-*"]
  }

  statement {
    sid       = "ReadAlertTopicConfig"
    effect    = "Allow"
    actions   = ["sns:GetTopicAttributes", "sns:ListTagsForResource"]
    resources = ["arn:aws:sns:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cd-*"]
  }
}

resource "aws_iam_role_policy" "ci_drift_read" {
  name   = "cd-ci-drift-readonly"
  role   = aws_iam_role.ci_drift.id
  policy = data.aws_iam_policy_document.ci_drift_read.json
}

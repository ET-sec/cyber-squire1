# Region guard: this account runs in one region on purpose.
#
# Every principal Terraform creates here carries an explicit deny for any
# request outside the home region (IAM, STS, Route53, and Support are
# global control planes and stay exempt). An
# attacker's first move with stolen credentials is usually a quiet region
# nobody looks at; this turns that move into AccessDenied. The CloudTrail
# trail stays multi-region for the same reason: it watches the regions
# where nothing should ever appear.

data "aws_iam_policy_document" "region_guard" {
  statement {
    sid    = "DenyOutsideHomeRegion"
    effect = "Deny"

    # Global services are exempt: their control planes resolve through
    # us-east-1 regardless of where a request originates.
    not_actions = [
      "iam:*",
      "sts:*",
      "route53:*",
      "support:*",
    ]
    resources = ["*"]

    condition {
      test     = "StringNotEquals"
      variable = "aws:RequestedRegion"
      values   = [var.aws_region]
    }
  }
}

resource "aws_iam_policy" "region_guard" {
  name        = "cd-region-guard"
  description = "Explicit deny outside the home region for cd principals"
  policy      = data.aws_iam_policy_document.region_guard.json
}

resource "aws_iam_role_policy_attachment" "ci_region_guard" {
  role       = aws_iam_role.ci_drift.name
  policy_arn = aws_iam_policy.region_guard.arn
}

resource "aws_iam_role_policy_attachment" "lambda_region_guard" {
  role       = aws_iam_role.alert_lambda.name
  policy_arn = aws_iam_policy.region_guard.arn
}

resource "aws_iam_user_policy_attachment" "uploader_region_guard" {
  #checkov:skip=CKV_AWS_40:Same single machine identity as the uploader policy; the region deny must bind to it directly (DR-05)
  user       = aws_iam_user.evidence_uploader.name
  policy_arn = aws_iam_policy.region_guard.arn
}

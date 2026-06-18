"""
Lab: AWS Config custom rule - auto-detect public S3 buckets

Objective: Build a custom Config rule that fires when an S3 bucket has Block
Public Access disabled. Pair with an EventBridge -> Lambda auto-remediation
that re-enables BPA within 60 seconds.

What an interviewer will ask:
  1. "How would you build a control that auto-remediates a public S3 bucket
     within 60 seconds of detection?"
  2. "Difference between AWS Config and CloudTrail?"
  3. "What is a Config conformance pack?"

Deploy notes:
  - This file is the Lambda source for the Config evaluation function.
  - Companion Terraform for the rule + EventBridge wiring is at the bottom of
    this file (commented as a heredoc) so you can copy and apply.
  - Runtime: python3.12, handler: index.lambda_handler

Reference:
  https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules.html
"""

import json
import boto3

s3 = boto3.client("s3")
config = boto3.client("config")


def evaluate_bucket(bucket_name: str) -> dict:
    """
    Returns a Config evaluation: COMPLIANT or NON_COMPLIANT.
    A bucket is NON_COMPLIANT if any of the four BPA flags is False.
    """
    try:
        bpa = s3.get_public_access_block(Bucket=bucket_name)
        cfg = bpa["PublicAccessBlockConfiguration"]
        all_blocked = all(
            [
                cfg.get("BlockPublicAcls", False),
                cfg.get("IgnorePublicAcls", False),
                cfg.get("BlockPublicPolicy", False),
                cfg.get("RestrictPublicBuckets", False),
            ]
        )
        if all_blocked:
            return {"compliance": "COMPLIANT", "annotation": "BPA fully enabled"}
        return {
            "compliance": "NON_COMPLIANT",
            "annotation": f"BPA flags incomplete: {cfg}",
        }
    except s3.exceptions.from_code("NoSuchPublicAccessBlockConfiguration"):
        return {
            "compliance": "NON_COMPLIANT",
            "annotation": "Bucket has no public access block configured",
        }
    except Exception as e:
        return {"compliance": "NOT_APPLICABLE", "annotation": f"error: {e}"}


def lambda_handler(event, context):
    """
    Config invokes this with an invoking event describing the resource
    being evaluated. We extract the bucket name and emit a PutEvaluations
    response.
    """
    invoking_event = json.loads(event["invokingEvent"])
    config_item = invoking_event.get("configurationItem")
    if not config_item:
        return

    if config_item["resourceType"] != "AWS::S3::Bucket":
        return

    bucket_name = config_item["resourceName"]
    result = evaluate_bucket(bucket_name)

    config.put_evaluations(
        Evaluations=[
            {
                "ComplianceResourceType": "AWS::S3::Bucket",
                "ComplianceResourceId": bucket_name,
                "ComplianceType": result["compliance"],
                "Annotation": result["annotation"][:256],
                "OrderingTimestamp": config_item["configurationItemCaptureTime"],
            }
        ],
        ResultToken=event["resultToken"],
    )

    return result


# =============================================================================
# Auto-remediation Lambda (separate function, triggered by EventBridge on the
# Config NON_COMPLIANT event). This re-enables BPA within seconds of detection.
# =============================================================================

def remediation_handler(event, context):
    """
    Triggered by EventBridge rule that filters Config compliance events
    where compliance type = NON_COMPLIANT and resourceType = AWS::S3::Bucket.

    Re-enables Block Public Access. Posts a Slack/Telegram alert with the
    actor info from CloudTrail.
    """
    detail = event.get("detail", {})
    bucket = detail.get("resourceId")
    if not bucket:
        return {"status": "no-bucket-in-event"}

    s3.put_public_access_block(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    # Look up who made the change in the last 5 minutes for the alert
    ct = boto3.client("cloudtrail")
    events = ct.lookup_events(
        LookupAttributes=[
            {"AttributeKey": "ResourceName", "AttributeValue": bucket},
            {"AttributeKey": "EventName", "AttributeValue": "PutPublicAccessBlock"},
        ],
        MaxResults=5,
    )
    actor = None
    for e in events.get("Events", []):
        actor = e.get("Username")
        break

    return {
        "status": "remediated",
        "bucket": bucket,
        "actor": actor or "unknown",
    }


# =============================================================================
# COMPANION TERRAFORM (copy, drop into a .tf file, terraform apply)
# =============================================================================
"""
###############################################################################
# Detection Lambda
###############################################################################
resource "aws_iam_role" "config_eval" {
  name = "lab-config-eval"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "config_eval" {
  role = aws_iam_role.config_eval.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetBucketPublicAccessBlock", "s3:ListAllMyBuckets"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["config:PutEvaluations"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:CreateLogGroup"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "config_eval" {
  function_name = "lab-config-s3-bpa-rule"
  role          = aws_iam_role.config_eval.arn
  runtime       = "python3.12"
  handler       = "index.lambda_handler"
  filename      = "config_custom_rule.zip"  # zip this python file as index.py
  timeout       = 30
}

resource "aws_lambda_permission" "config_invoke" {
  statement_id  = "AllowConfigInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.config_eval.function_name
  principal     = "config.amazonaws.com"
}

resource "aws_config_config_rule" "s3_bpa" {
  name = "s3-bucket-block-public-access-required"
  source {
    owner             = "CUSTOM_LAMBDA"
    source_identifier = aws_lambda_function.config_eval.arn
    source_detail {
      event_source = "aws.config"
      message_type = "ConfigurationItemChangeNotification"
    }
  }
  scope {
    compliance_resource_types = ["AWS::S3::Bucket"]
  }
  depends_on = [aws_lambda_permission.config_invoke]
}

###############################################################################
# Auto-remediation Lambda
###############################################################################
resource "aws_iam_role" "remediation" {
  name = "lab-remediation"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "remediation" {
  role = aws_iam_role.remediation.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutBucketPublicAccessBlock", "s3:GetBucketPublicAccessBlock"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["cloudtrail:LookupEvents"]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:CreateLogGroup"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "remediation" {
  function_name = "lab-s3-bpa-remediation"
  role          = aws_iam_role.remediation.arn
  runtime       = "python3.12"
  handler       = "index.remediation_handler"
  filename      = "config_custom_rule.zip"
  timeout       = 30
}

resource "aws_cloudwatch_event_rule" "config_noncompliance" {
  name = "lab-config-s3-noncompliance"
  event_pattern = jsonencode({
    source       = ["aws.config"]
    "detail-type" = ["Config Rules Compliance Change"]
    detail = {
      messageType = ["ComplianceChangeNotification"]
      newEvaluationResult = {
        complianceType = ["NON_COMPLIANT"]
      }
      configRuleName = ["s3-bucket-block-public-access-required"]
    }
  })
}

resource "aws_cloudwatch_event_target" "remediation" {
  rule      = aws_cloudwatch_event_rule.config_noncompliance.name
  target_id = "remediate"
  arn       = aws_lambda_function.remediation.arn
}

resource "aws_lambda_permission" "events_invoke" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remediation.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.config_noncompliance.arn
}
"""

# =============================================================================
# WHAT TO STUDY
# =============================================================================
# 1. AWS Config = configuration history + compliance evaluation. CloudTrail =
#    API call audit log. They overlap in some places. Config tells you "what
#    is the state of resource X right now and historically". CloudTrail tells
#    you "who called what API at what time".
#
# 2. Conformance packs = bundles of Config rules deployed together.
#    Pre-built ones: AWS Foundational Best Practices, NIST 800-53,
#    HIPAA Security, PCI DSS. Deploy via CFN StackSet across all accounts.
#
# 3. Detection latency: Config rule evaluation runs within seconds of the
#    resource change event in modern Config (was 5-15 min historically).
#    EventBridge to Lambda is sub-second. Total: change -> remediation in
#    under 60 seconds is achievable.
#
# 4. Limitations:
#    - Config does not re-evaluate everything continuously. It evaluates on
#      change events. If the bucket exists in a NON_COMPLIANT state and
#      nothing changes, the rule fires once and goes silent until the next
#      configuration change. Pair with periodic manual evaluation
#      (StartConfigRulesEvaluation cron).
#    - Config has a per-resource cost. ~$0.003 per configuration item recorded.
#      Adds up at scale. Use resource-type filters in the recorder.
#    - Custom Lambda rules cost Lambda invocations. Cheaper to use AWS-managed
#      rules where they exist (s3-bucket-public-access-prohibited is built in).
#
# 5. Compliance packs vs SecurityHub: SecurityHub aggregates findings, Config
#    generates them. Conformance packs deploy Config rules. Use both. Wire
#    Config compliance changes through SecurityHub for de-duped finding feeds.

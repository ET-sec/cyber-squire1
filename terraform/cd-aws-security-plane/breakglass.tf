# Cross-cloud break-glass with alert-on-use.
#
# The sealed OCI emergency credential lives here, in the OTHER cloud, so a
# compromise or outage of either vendor alone can neither lock the operator
# out nor expose the credential silently. Break-glass nobody watches is a
# backdoor: any read of this secret raises a Telegram alert within minutes
# via CloudTrail management events -> EventBridge -> Lambda.

resource "aws_secretsmanager_secret" "breakglass_oci" {
  #checkov:skip=CKV2_AWS_57:Break-glass is a sealed, manually rotated credential by design; automatic rotation of an OCI credential has no managed rotation path, and rotation is triggered on any use via the alert below
  name        = "cd/breakglass/oci-emergency"
  description = "Sealed OCI emergency credential. Any access alerts the operator."
  kms_key_id  = aws_kms_key.evidence.arn

  # The secret VALUE is set out-of-band at apply time, never through
  # Terraform state.
}

resource "aws_sns_topic" "breakglass" {
  name              = var.breakglass_alert_topic_name
  kms_master_key_id = aws_kms_key.evidence.id
}

# CloudTrail as the account audit log, archived into the evidence vault
# under its own prefix. GetSecretValue is a management event, so the trail
# carries the break-glass reads with no data selector needed; S3 data events
# cover object activity in the vault's evidence prefix.
resource "aws_s3_bucket_policy" "evidence_cloudtrail" {
  bucket = aws_s3_bucket.evidence.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "CloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = aws_s3_bucket.evidence.arn
      },
      {
        Sid       = "CloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.evidence.arn}/cloudtrail/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          StringEquals = { "s3:x-amz-acl" = "bucket-owner-full-control" }
        }
      }
    ]
  })
}

resource "aws_cloudtrail" "security_plane" {
  #checkov:skip=CKV_AWS_252:Alerting is EventBridge to Lambda to Telegram; SNS delivery notices on every log file add noise, not signal
  #checkov:skip=CKV2_AWS_10:The immutable S3 copy with log file validation is the record; CloudWatch Logs ingest duplicates it at ongoing cost
  name                       = "cd-security-plane"
  s3_bucket_name             = aws_s3_bucket.evidence.id
  s3_key_prefix              = "cloudtrail"
  kms_key_id                 = aws_kms_key.evidence.arn
  enable_log_file_validation = true
  is_multi_region_trail      = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    # Scoped to the evidence prefix: data-eventing the trail's own
    # cloudtrail/ delivery prefix would log every log delivery forever.
    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.evidence.arn}/evidence/"]
    }
  }

  depends_on = [aws_s3_bucket_policy.evidence_cloudtrail]
}

# CloudTrail needs to use the CMK.
resource "aws_kms_key_policy" "evidence" {
  key_id = aws_kms_key.evidence.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AccountAdmin"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action    = "kms:*"
        Resource  = "*"
      },
      {
        Sid       = "CloudTrailEncrypt"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = ["kms:GenerateDataKey*", "kms:DescribeKey"]
        Resource  = "*"
      }
    ]
  })
}

# EventBridge rule: any GetSecretValue against the break-glass secret.
resource "aws_cloudwatch_event_rule" "breakglass_access" {
  name        = "cd-breakglass-access"
  description = "Fires on any read of the break-glass secret"

  # GetSecretValue is a READ-ONLY management event; EventBridge excludes
  # those unless the rule opts in with this state. Without it the alert
  # never fires and break-glass becomes a silent backdoor.
  state = "ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS"

  event_pattern = jsonencode({
    source      = ["aws.secretsmanager"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["secretsmanager.amazonaws.com"]
      eventName   = ["GetSecretValue"]
      requestParameters = {
        secretId = [{ wildcard = "*breakglass*" }]
      }
    }
  })
}

data "archive_file" "alert_lambda" {
  type        = "zip"
  source_file = "${path.module}/lambda/breakglass_alert.py"
  output_path = "${path.module}/lambda/breakglass_alert.zip"
}

data "aws_iam_policy_document" "lambda_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "alert_lambda" {
  name               = "cd-breakglass-alert-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json
}

resource "aws_iam_role_policy_attachment" "alert_lambda_logs" {
  role       = aws_iam_role.alert_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "breakglass_alert" {
  #checkov:skip=CKV_AWS_117:The function needs outbound internet to reach the Telegram API; there is no VPC in this account and a NAT gateway is paid standing infrastructure for a 40-line alerter
  #checkov:skip=CKV_AWS_272:Source ships in the public repo and the deployment hash is pinned by archive_file; AWS Signer adds a service for no additional trust here
  function_name                  = var.telegram_alert_lambda_name
  role                           = aws_iam_role.alert_lambda.arn
  runtime                        = "python3.12"
  handler                        = "breakglass_alert.handler"
  filename                       = data.archive_file.alert_lambda.output_path
  source_code_hash               = data.archive_file.alert_lambda.output_base64sha256
  timeout                        = 15
  reserved_concurrent_executions = 5
  kms_key_arn                    = aws_kms_key.evidence.arn

  tracing_config {
    mode = "Active"
  }

  dead_letter_config {
    target_arn = aws_sns_topic.breakglass.arn
  }

  # Only the non-secret SSM parameter path lives in the environment; the
  # Lambda fetches Telegram credentials from SSM at invoke time.
  environment {
    variables = {
      TELEGRAM_PARAM_PATH = "/cd/alerts/telegram"
    }
  }
}

resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.breakglass_alert.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.breakglass_access.arn
}

resource "aws_cloudwatch_event_target" "breakglass_lambda" {
  rule = aws_cloudwatch_event_rule.breakglass_access.name
  arn  = aws_lambda_function.breakglass_alert.arn
}

# The Lambda reads Telegram bot credentials from SSM at invoke time.
data "aws_iam_policy_document" "lambda_ssm" {
  statement {
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cd/alerts/telegram*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.evidence.arn]
  }
}

data "aws_iam_policy_document" "lambda_dlq" {
  statement {
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.breakglass.arn]
  }
  statement {
    # The topic is CMK-encrypted; publishing needs the key.
    effect    = "Allow"
    actions   = ["kms:GenerateDataKey"]
    resources = [aws_kms_key.evidence.arn]
  }
  statement {
    effect    = "Allow"
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    resources = ["*"] #checkov:skip=CKV_AWS_356:X-Ray trace ingestion does not support resource scoping
  }
}

resource "aws_iam_role_policy" "lambda_dlq" {
  name   = "cd-breakglass-alert-dlq"
  role   = aws_iam_role.alert_lambda.id
  policy = data.aws_iam_policy_document.lambda_dlq.json
}

resource "aws_iam_role_policy" "lambda_ssm" {
  name   = "cd-breakglass-alert-ssm"
  role   = aws_iam_role.alert_lambda.id
  policy = data.aws_iam_policy_document.lambda_ssm.json
}

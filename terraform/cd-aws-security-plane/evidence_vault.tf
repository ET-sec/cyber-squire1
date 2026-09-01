# Evidence vault: the off-cloud copy of everything that proves the platform's
# behavior. Nightly the OCI instance ships pg_dump replicas, drift reports,
# POA&M snapshots, and audit log bundles here. Object Lock compliance mode
# means nobody, including the account root, can delete inside the window:
# OCI retention defeats ransomware on the workload cloud, this bucket defeats
# the vendor-death case, which is the failure that actually happened.

resource "aws_kms_key" "evidence" {
  description             = "CMK for the cd security plane evidence vault"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "evidence" {
  name          = "alias/cd-evidence-vault"
  target_key_id = aws_kms_key.evidence.key_id
}

resource "aws_s3_bucket" "evidence" {
  #checkov:skip=CKV_AWS_18:Object-level access auditing is CloudTrail S3 data events on this bucket (tamper-evident, in-vault); server access logs would need a second unlocked bucket and add no integrity
  #checkov:skip=CKV_AWS_144:This bucket IS the cross-cloud replica; its primaries live on OCI. Replicating the replica doubles cost for no new failure domain
  bucket = var.evidence_bucket_name

  # Object Lock must be enabled at creation; it cannot be retrofitted.
  object_lock_enabled = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = var.evidence_retention_days
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.evidence.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle: evidence ages into cheaper storage instead of growing the bill.
resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    id     = "age-evidence"
    status = "Enabled"

    filter {}

    transition {
      days          = 35
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# S3 events onto the default event bus; the CloudTrail data events above are
# the audit record, this makes bucket activity routable for future detections.
resource "aws_s3_bucket_notification" "evidence" {
  bucket      = aws_s3_bucket.evidence.id
  eventbridge = true
}

# Uploader identity for the OCI instance: write-only, no read of other
# objects, no delete (Object Lock refuses anyway; the policy makes intent
# explicit). Credentials for this user are scoped, rotated via Doppler,
# and are the only long-lived AWS material in the design; the tradeoff is
# recorded in DR-05 (OCI instance principals cannot federate into AWS).
resource "aws_iam_user" "evidence_uploader" {
  #checkov:skip=CKV_AWS_273:Single-purpose machine identity for the OCI uploader; OCI instance principals cannot federate into AWS, so SSO does not apply (tradeoff in DR-05)
  name = "cd-evidence-uploader"
}

data "aws_iam_policy_document" "evidence_upload" {
  statement {
    sid       = "WriteEvidenceOnly"
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.evidence.arn}/*"]
  }

  statement {
    sid       = "ListOwnPrefix"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.evidence.arn]
  }

  statement {
    sid       = "UseVaultKey"
    effect    = "Allow"
    actions   = ["kms:GenerateDataKey"]
    resources = [aws_kms_key.evidence.arn]
  }
}

resource "aws_iam_user_policy" "evidence_upload" {
  #checkov:skip=CKV_AWS_40:Deliberate single-user inline policy; a group wrapping one machine identity adds indirection, not safety (DR-05)
  name   = "cd-evidence-upload-only"
  user   = aws_iam_user.evidence_uploader.name
  policy = data.aws_iam_policy_document.evidence_upload.json
}

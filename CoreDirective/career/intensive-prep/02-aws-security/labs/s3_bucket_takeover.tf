###############################################################################
# Lab: S3 bucket misconfig vs hardened bucket policy
# Objective: Side by side, the vulnerable bucket and the hardened bucket. Apply
#   the vulnerable one, see how easy takeover is, then apply the hardened one
#   and prove the same attack fails.
#
# What an interviewer will ask:
#   1. "Walk me through securing an S3 bucket holding PII."
#   2. "What is the difference between Block Public Access at the account level
#      vs the bucket level?"
#   3. "What is the difference between bucket policy, ACL, and IAM?"
#   4. "Tell me about a famous S3 leak."
#
# Real attack history:
#   - Accenture (2017): 4 unsecured S3 buckets exposed plaintext credentials
#   - Verizon (2017): 6M customer records leaked via misconfigured S3
#   - Capital One (2019): SSRF -> EC2 IMDS -> S3 read access
#   - Code Spaces (2014): attacker took over AWS, deleted S3 backups, killed company in 12 hours
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1"
}

variable "name_prefix" {
  default = "lab-s3-takeover"
}

###############################################################################
# VULNERABLE BUCKET (the misconfig)
###############################################################################

resource "aws_s3_bucket" "vuln" {
  bucket        = "${var.name_prefix}-vuln-${random_string.s.result}"
  force_destroy = true
  tags = { lab = "s3-vuln", classification = "DO-NOT-USE-IN-PROD" }
}

resource "random_string" "s" {
  length  = 8
  special = false
  upper   = false
}

# Vuln 1: Block Public Access disabled
resource "aws_s3_bucket_public_access_block" "vuln" {
  bucket                  = aws_s3_bucket.vuln.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Vuln 2: bucket policy allows anyone to GetObject (the classic misconfig)
resource "aws_s3_bucket_policy" "vuln" {
  bucket = aws_s3_bucket.vuln.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadAllowByMistake"
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject", "s3:ListBucket"]
      Resource  = [
        aws_s3_bucket.vuln.arn,
        "${aws_s3_bucket.vuln.arn}/*"
      ]
    }]
  })
  depends_on = [aws_s3_bucket_public_access_block.vuln]
}

# Vuln 3: no encryption enforcement, no SSL enforcement, no logging, no versioning
# (deliberately omitted to show what is missing)

###############################################################################
# HARDENED BUCKET (the fix)
###############################################################################

resource "aws_s3_bucket" "safe" {
  bucket        = "${var.name_prefix}-safe-${random_string.s.result}"
  force_destroy = false
  tags = { lab = "s3-safe", classification = "INTERNAL" }
}

# Fix 1: Block Public Access ON. This is the kill switch. Even if the bucket
# policy says "Principal: *", BPA blocks it.
resource "aws_s3_bucket_public_access_block" "safe" {
  bucket                  = aws_s3_bucket.safe.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Fix 2: ownership controls (ACLs disabled, bucket owner enforced)
resource "aws_s3_bucket_ownership_controls" "safe" {
  bucket = aws_s3_bucket.safe.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Fix 3: KMS encryption at rest with customer-managed key + bucket key
resource "aws_kms_key" "safe" {
  description             = "S3 bucket key for ${var.name_prefix}-safe"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "safe" {
  name          = "alias/${var.name_prefix}-safe"
  target_key_id = aws_kms_key.safe.key_id
}

resource "aws_s3_bucket_server_side_encryption_configuration" "safe" {
  bucket = aws_s3_bucket.safe.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.safe.arn
    }
    bucket_key_enabled = true
  }
}

# Fix 4: versioning + MFA delete (versioning is required for object lock)
resource "aws_s3_bucket_versioning" "safe" {
  bucket = aws_s3_bucket.safe.id
  versioning_configuration { status = "Enabled" }
}

# Fix 5: bucket policy enforcing TLS, blocking unencrypted uploads, restricting
# to org principals
resource "aws_s3_bucket_policy" "safe" {
  bucket = aws_s3_bucket.safe.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.safe.arn, "${aws_s3_bucket.safe.arn}/*"]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      },
      {
        Sid       = "DenyUnencryptedObjectUploads"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.safe.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }
        }
      },
      {
        Sid       = "DenyOutsideOrg"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.safe.arn, "${aws_s3_bucket.safe.arn}/*"]
        Condition = {
          StringNotEqualsIfExists = {
            "aws:PrincipalOrgID" = data.aws_organizations_organization.this.id
          }
        }
      }
    ]
  })
  depends_on = [aws_s3_bucket_public_access_block.safe]
}

data "aws_organizations_organization" "this" {}

# Fix 6: server access logging to a dedicated log bucket
resource "aws_s3_bucket" "logs" {
  bucket        = "${var.name_prefix}-logs-${random_string.s.result}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "safe" {
  bucket        = aws_s3_bucket.safe.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "access-logs/"
}

# Fix 7: lifecycle to expire old versions and abort incomplete multipart uploads
resource "aws_s3_bucket_lifecycle_configuration" "safe" {
  bucket = aws_s3_bucket.safe.id
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration { noncurrent_days = 90 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}

###############################################################################
# OUTPUT - run after apply
###############################################################################

output "vuln_test_command" {
  value = <<EOT
# After apply, this will succeed (proving the vuln):
curl -s https://${aws_s3_bucket.vuln.bucket}.s3.${var.region}.amazonaws.com/
# Returns ListBucketResult XML to ANY anonymous caller

# After apply on the safe bucket, this returns 403 (proving the fix):
curl -s https://${aws_s3_bucket.safe.bucket}.s3.${var.region}.amazonaws.com/
EOT
}

###############################################################################
# WHAT TO STUDY FROM THIS LAB
###############################################################################
# 1. Block Public Access is the kill switch. Turn it on at the account level
#    (aws s3control put-public-access-block --account-id X) plus per-bucket.
#
# 2. Bucket policy with Principal: "*" is the most common s3 leak pattern. Any
#    AWS Config rule worth its salt flags this.
#
# 3. ACLs are disabled by default since 2023 (BucketOwnerEnforced). Stop using
#    them. New code: bucket policy + IAM only.
#
# 4. Encryption alone is not enough. SSE-S3 vs SSE-KMS matters for the key
#    policy boundary. SSE-KMS with a CMK gives you a second auth check
#    (the KMS key policy) which can require kms:Decrypt.
#
# 5. aws:SecureTransport = false denial blocks plaintext HTTP. AWS Foundational
#    Security Best Practices control [S3.5].
#
# 6. aws:PrincipalOrgID condition stops cross-account exfiltration if creds
#    leak. The condition refuses any principal not in your AWS Organization.
#
# 7. Object Lock in compliance mode is irrevocable. Turn it on for ransomware
#    resilience. In governance mode the root user can still delete (do not use
#    governance mode for backups).
#
# Real engineer answer to "secure an S3 bucket holding PII":
#   "Layer it. Block Public Access at account and bucket. ACLs off. Bucket
#    policy enforcing TLS, KMS encryption with a CMK, and aws:PrincipalOrgID
#    so the bucket only answers to my org. Versioning on, lifecycle to expire
#    old versions, Object Lock if it is regulated. Logging to a separate log
#    bucket in a separate account. Macie scanning weekly to confirm no PII is
#    leaking out into other prefixes. CloudTrail data events on for write and
#    optionally read if budget allows. Alerts in GuardDuty for
#    Policy:S3/BucketBlockPublicAccessDisabled."
###############################################################################

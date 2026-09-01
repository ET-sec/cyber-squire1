output "ci_drift_role_arn" {
  description = "Role the drift workflow assumes via GitHub OIDC."
  value       = aws_iam_role.ci_drift.arn
}

output "evidence_bucket" {
  description = "Evidence vault bucket name."
  value       = aws_s3_bucket.evidence.id
}

output "evidence_kms_key_arn" {
  description = "CMK protecting the vault and break-glass secret."
  value       = aws_kms_key.evidence.arn
}

output "breakglass_secret_arn" {
  description = "ARN of the sealed OCI emergency credential."
  value       = aws_secretsmanager_secret.breakglass_oci.arn
  sensitive   = true
}

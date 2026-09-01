variable "aws_region" {
  description = "Home region for the security plane."
  type        = string
  default     = "us-east-1"
}

variable "github_repo" {
  description = "GitHub repository allowed to assume the CI role (owner/name)."
  type        = string
  default     = "ET-sec/cyber-squire1"
}

variable "github_branch" {
  description = "Branch whose OIDC tokens may assume the CI role. Pinned to main: every cloud credential traces to a reviewed commit."
  type        = string
  default     = "main"
}

variable "evidence_bucket_name" {
  description = "Globally unique name for the evidence vault bucket. Set in tfvars, never committed."
  type        = string
}

variable "evidence_retention_days" {
  description = "Object Lock retention window for evidence objects."
  type        = number
  default     = 30
}

variable "breakglass_alert_topic_name" {
  description = "SNS topic name for break-glass access alerts."
  type        = string
  default     = "cd-breakglass-alerts"
}

variable "telegram_alert_lambda_name" {
  description = "Name of the Lambda that forwards CloudTrail break-glass events to Telegram."
  type        = string
  default     = "cd-breakglass-telegram-alert"
}

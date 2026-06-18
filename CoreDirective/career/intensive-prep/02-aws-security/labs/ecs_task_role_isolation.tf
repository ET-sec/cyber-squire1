###############################################################################
# Lab: ECS task role vs execution role
# Objective: Prove the difference. Execution role pulls the image. Task role is
#   what the running container code can do. Mixing these up is a common vuln.
#
# What an interviewer will ask:
#   1. "Difference between task role and execution role on ECS Fargate?"
#   2. "Can you mount a Secrets Manager secret into an ECS task without code changes?"
#   3. "What kernel sharing risk does Fargate eliminate compared to ECS on EC2?"
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = var.region }

variable "region" { default = "us-east-1" }
variable "name"   { default = "lab-ecs-roles" }

###############################################################################
# Secrets to inject (the demo data)
###############################################################################
resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.name}-db-pass"
}
resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({ password = "demo-only-not-real" })
}

resource "aws_kms_key" "secrets" {
  description             = "ECS demo secrets KMS"
  enable_key_rotation     = true
  deletion_window_in_days = 7
}

###############################################################################
# EXECUTION ROLE - what the ECS agent does on behalf of the task
# Permissions: pull image from ECR, write logs, fetch secrets to inject as env vars
###############################################################################
resource "aws_iam_role" "execution" {
  name = "${var.name}-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution_managed" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow execution role to read the secret AT TASK START (for env injection)
resource "aws_iam_role_policy" "execution_secrets" {
  name = "read-injection-secrets"
  role = aws_iam_role.execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.db_password.arn
    }, {
      Effect   = "Allow"
      Action   = ["kms:Decrypt"]
      Resource = aws_kms_key.secrets.arn
    }]
  })
}

###############################################################################
# TASK ROLE - what the application code calls AWS APIs as
# Permissions: only what the app actually needs (read app data from S3, etc)
###############################################################################
resource "aws_iam_role" "task" {
  name = "${var.name}-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:ecs:${var.region}:${data.aws_caller_identity.current.account_id}:*"
        }
      }
    }]
  })
}

data "aws_caller_identity" "current" {}

# Application data access
resource "aws_iam_role_policy" "task_app" {
  name = "app-data-access"
  role = aws_iam_role.task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::${var.name}-app-data/*"
    }]
  })
}

###############################################################################
# Task definition demonstrating injection from Secrets Manager
###############################################################################
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.name}"
  retention_in_days = 30
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = aws_iam_role.execution.arn
  task_role_arn      = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name      = "app"
    image     = "public.ecr.aws/docker/library/nginx:1.27-alpine"
    essential = true
    readonlyRootFilesystem = true
    user      = "101"  # nginx user, not root
    portMappings = [{ containerPort = 80 }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "ecs"
      }
    }
    secrets = [
      {
        name      = "DB_PASSWORD"
        valueFrom = "${aws_secretsmanager_secret.db_password.arn}:password::"
      }
    ]
    linuxParameters = {
      capabilities = {
        drop = ["ALL"]
      }
    }
  }])
}

###############################################################################
# WHAT TO STUDY
###############################################################################
# THE ROLE SPLIT:
#
# EXECUTION ROLE: assumed by the ECS agent (the platform) when starting your
# task. It needs:
#   - ecr:GetAuthorizationToken, ecr:BatchGetImage, ecr:GetDownloadUrlForLayer
#     (to pull the container image)
#   - logs:CreateLogStream, logs:PutLogEvents (to ship logs)
#   - secretsmanager:GetSecretValue + kms:Decrypt (to inject secrets as env vars)
#   - ssm:GetParameters (to inject Parameter Store values as env vars)
#
# Critical: the execution role's secrets access is used at TASK START, before
# your code is running. Your code never has those credentials.
#
# TASK ROLE: assumed by your application code when it makes AWS API calls.
# Permissions = exactly what the app does. Should be the principle of least
# privilege scoped to the application's logic.
#
# ============================================================================
#
# THE COMMON MISTAKE: putting both sets of permissions on the execution role
# and leaving the task role empty. The container then has too much (everything
# the platform needs). Always set both, scoped tightly.
#
# ============================================================================
#
# THE INJECTION TRICK: container_definitions[].secrets injects a secret as an
# environment variable. The container code reads $DB_PASSWORD without any AWS
# SDK call. Only the execution role needs secretsmanager:GetSecretValue.
#
# Limitation: env vars are visible to anyone with ECS read access (DescribeTask)
# or container introspection (kubectl exec equivalent on ECS Exec). For real
# secrets, mount via a sidecar that calls Secrets Manager on demand.
#
# ============================================================================
#
# FARGATE VS EC2:
#
# Fargate: AWS manages the kernel. You cannot share kernels between tasks.
# Each task gets its own micro-VM (Firecracker). Container escape -> attacker
# is in a micro-VM, not on a host with other customers.
#
# ECS on EC2: tasks share the kernel of the host EC2. A container escape
# (e.g., dirtyCOW or a Docker runtime CVE) gives the attacker host access,
# which means access to all other tasks on that host. Use Fargate unless
# you have a real reason for EC2 (GPU workloads, custom kernel, etc).
#
# ============================================================================
#
# CONFUSED DEPUTY ON ECS:
#
# Without aws:SourceAccount and aws:SourceArn conditions in the task role's
# trust policy, any ECS service in any account could potentially assume the
# role. The conditions force the assumption to come from your own account's
# ECS service. Always set both.
#
# Reference: https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html
###############################################################################

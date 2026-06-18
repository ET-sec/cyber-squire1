###############################################################################
# Lab: layered VPC with public, private, isolated subnets + endpoints
# Objective: Build the standard 3-tier VPC the way every senior engineer should
#   draw on a whiteboard. Verify with route tables.
#
# What an interviewer will ask:
#   1. "Draw a production VPC. Where do RDS, ALB, EC2, NAT GW, IGW go?"
#   2. "Why use a NAT GW per AZ instead of one shared NAT GW?"
#   3. "What is the difference between an interface endpoint and a gateway endpoint?"
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}

provider "aws" { region = var.region }

variable "region" { default = "us-east-1" }
variable "name"   { default = "lab-vpc" }
variable "azs"    { default = ["us-east-1a", "us-east-1b"] }
variable "cidr"   { default = "10.20.0.0/16" }

###############################################################################
# VPC
###############################################################################
resource "aws_vpc" "main" {
  cidr_block           = var.cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = var.name }
}

# Public subnets: ALB, NAT GW, bastion
resource "aws_subnet" "public" {
  count                   = length(var.azs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.cidr, 8, count.index)
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = false
  tags = { Name = "${var.name}-public-${var.azs[count.index]}", tier = "public" }
}

# Private subnets: app servers, ECS tasks, EKS nodes (egress to internet via NAT)
resource "aws_subnet" "private" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr, 8, count.index + 10)
  availability_zone = var.azs[count.index]
  tags = { Name = "${var.name}-private-${var.azs[count.index]}", tier = "private" }
}

# Isolated subnets: RDS, ElastiCache, anything that must never reach the internet
resource "aws_subnet" "isolated" {
  count             = length(var.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr, 8, count.index + 20)
  availability_zone = var.azs[count.index]
  tags = { Name = "${var.name}-isolated-${var.azs[count.index]}", tier = "isolated" }
}

###############################################################################
# Internet Gateway + NAT Gateway per AZ (cost vs availability tradeoff)
###############################################################################
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.name}-igw" }
}

resource "aws_eip" "nat" {
  count  = length(var.azs)
  domain = "vpc"
  tags   = { Name = "${var.name}-nat-${var.azs[count.index]}" }
}

resource "aws_nat_gateway" "nat" {
  count         = length(var.azs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  tags          = { Name = "${var.name}-nat-${var.azs[count.index]}" }
  depends_on    = [aws_internet_gateway.igw]
}

###############################################################################
# Route tables
###############################################################################
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.name}-public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = length(var.azs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  count  = length(var.azs)
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index].id
  }
  tags = { Name = "${var.name}-private-rt-${var.azs[count.index]}" }
}

resource "aws_route_table_association" "private" {
  count          = length(var.azs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Isolated subnets have NO internet route. The only egress is via VPC endpoints.
resource "aws_route_table" "isolated" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.name}-isolated-rt" }
}

resource "aws_route_table_association" "isolated" {
  count          = length(var.azs)
  subnet_id      = aws_subnet.isolated[count.index].id
  route_table_id = aws_route_table.isolated.id
}

###############################################################################
# VPC Endpoints (the security tightening)
###############################################################################
# Gateway endpoints for S3 + DynamoDB (free, route-table based)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(aws_route_table.private[*].id, [aws_route_table.isolated.id])

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource  = "*"
      Condition = {
        StringEquals = { "aws:PrincipalOrgID" = data.aws_organizations_organization.this.id }
      }
    }]
  })
}

data "aws_organizations_organization" "this" {}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(aws_route_table.private[*].id, [aws_route_table.isolated.id])
}

# Interface endpoints for control plane services (cost: $0.01/hr per endpoint per AZ)
resource "aws_security_group" "endpoints" {
  name        = "${var.name}-endpoints-sg"
  description = "Allow VPC traffic to interface endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.name}-endpoints-sg" }
}

# Common interface endpoints. Add more as needed (sts, kms, secretsmanager, ecr.api,
# ecr.dkr, logs, monitoring, ssm, ssmmessages, ec2messages).
locals {
  interface_endpoints = ["sts", "kms", "secretsmanager", "logs", "ssm", "ssmmessages", "ec2messages", "ecr.api", "ecr.dkr"]
}

resource "aws_vpc_endpoint" "interface" {
  for_each            = toset(local.interface_endpoints)
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true
  tags = { Name = "${var.name}-${replace(each.key, ".", "-")}-vpce" }
}

###############################################################################
# Outputs
###############################################################################
output "vpc_id"            { value = aws_vpc.main.id }
output "public_subnets"    { value = aws_subnet.public[*].id }
output "private_subnets"   { value = aws_subnet.private[*].id }
output "isolated_subnets"  { value = aws_subnet.isolated[*].id }
output "interface_vpces"   { value = { for k, v in aws_vpc_endpoint.interface : k => v.id } }

###############################################################################
# WHAT TO STUDY
###############################################################################
# 1. Three subnet tiers, not two. The third tier (isolated) has no internet
#    route at all. Database tier lives there. If you ever see RDS in a public
#    subnet, that is a finding.
#
# 2. NAT Gateway per AZ. The alternative (one NAT in one AZ) costs less but
#    creates an availability dependency: if that AZ dies, all your private
#    subnets in other AZs lose internet. NAT GW is also a data-charge bottleneck.
#
# 3. Gateway endpoints (S3, DynamoDB) are free. Add them everywhere. Without
#    them, S3 traffic goes out the NAT GW and you pay egress on it.
#
# 4. Interface endpoints cost ~$7.20/mo per endpoint per AZ. Worth it if you
#    want to enforce "no internet egress at all" (no NAT GW, just endpoints).
#    For most workloads, gateway endpoints + a handful of interface endpoints.
#
# 5. Endpoint policies are a kill switch for data exfil. If a compromised EC2
#    tries to PUT to an attacker-owned S3 bucket, the endpoint policy with
#    aws:PrincipalOrgID denies the call. The traffic never leaves your VPC.
#
# 6. Security groups are stateful (return traffic auto-allowed). NACLs are
#    stateless (must allow both directions explicitly). Use SGs for
#    instance-level controls, NACLs for subnet-level emergency blocks.
###############################################################################

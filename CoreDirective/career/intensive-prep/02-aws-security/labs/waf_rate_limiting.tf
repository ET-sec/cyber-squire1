###############################################################################
# Lab: WAF rate limiting + managed rule groups for layer 7 DDoS
# Objective: Build a production-shaped WAF in front of an ALB. Demonstrate
#   rate-based rules, managed rule groups, geo blocking, and the order in
#   which rules evaluate.
#
# What an interviewer will ask:
#   1. "Customer is being layer-7 DDoS'd. What do you turn on in the next 30 min?"
#   2. "Difference between Shield Standard and Shield Advanced?"
#   3. "How does WAF rule order affect cost and false positives?"
#
# Reference: AWS WAF docs https://docs.aws.amazon.com/waf/
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = var.region }

variable "region" { default = "us-east-1" }
variable "name"   { default = "lab-waf" }
variable "blocked_countries" {
  default = ["KP", "RU", "IR"]  # adjust per your business needs
}

###############################################################################
# WAF Web ACL (regional, attaches to ALB or API Gateway)
###############################################################################
resource "aws_wafv2_web_acl" "main" {
  name  = var.name
  scope = "REGIONAL"

  default_action { allow {} }

  ###########################################################################
  # Priority 0: Rate-based rule. First line for layer 7 DDoS.
  # 2000 requests per 5 minutes per IP. Block for 5 min after threshold.
  ###########################################################################
  rule {
    name     = "rate-limit-per-ip"
    priority = 0
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "rate-limit-per-ip"
    }
  }

  ###########################################################################
  # Priority 1: Geo-block (cheap, run before paying for managed rules)
  ###########################################################################
  rule {
    name     = "block-geo"
    priority = 1
    action { block {} }
    statement {
      geo_match_statement { country_codes = var.blocked_countries }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "block-geo"
    }
  }

  ###########################################################################
  # Priority 2: AWS Managed Core Rule Set (OWASP Top 10 baseline)
  # COUNT mode initially. Watch CloudWatch for false positives, then flip
  # to BLOCK once you have a clean week.
  ###########################################################################
  rule {
    name     = "aws-core-rules"
    priority = 2
    override_action { count {} }  # change to none {} when ready to block
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-core-rules"
    }
  }

  ###########################################################################
  # Priority 3: AWS Known Bad Inputs (specific exploit signatures)
  ###########################################################################
  rule {
    name     = "aws-known-bad-inputs"
    priority = 3
    override_action { none {} }  # block from day one
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-known-bad-inputs"
    }
  }

  ###########################################################################
  # Priority 4: Anonymous IP list (Tor, VPN, hosting providers)
  # Block if your business does not legitimately serve those.
  ###########################################################################
  rule {
    name     = "aws-anonymous-ip"
    priority = 4
    override_action { count {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesAnonymousIpList"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-anonymous-ip"
    }
  }

  ###########################################################################
  # Priority 5: SQL injection on URI + body
  ###########################################################################
  rule {
    name     = "aws-sqli"
    priority = 5
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesSQLiRuleSet"
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-sqli"
    }
  }

  ###########################################################################
  # Priority 6: custom rule for /admin path - allow only office IP
  ###########################################################################
  rule {
    name     = "admin-allowlist"
    priority = 6
    action { block {} }
    statement {
      and_statement {
        statement {
          byte_match_statement {
            field_to_match { uri_path {} }
            positional_constraint = "STARTS_WITH"
            search_string         = "/admin"
            text_transformation { priority = 0, type = "LOWERCASE" }
          }
        }
        statement {
          not_statement {
            statement {
              ip_set_reference_statement {
                arn = aws_wafv2_ip_set.office.arn
              }
            }
          }
        }
      }
    }
    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "admin-allowlist"
    }
  }

  visibility_config {
    sampled_requests_enabled   = true
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name}-acl"
  }
}

resource "aws_wafv2_ip_set" "office" {
  name               = "${var.name}-office-ips"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = ["203.0.113.0/24"]  # replace with your office CIDR
}

###############################################################################
# Logging: WAF logs to CloudWatch Logs (or Kinesis Firehose for higher volume)
###############################################################################
resource "aws_cloudwatch_log_group" "waf" {
  name              = "aws-waf-logs-${var.name}"  # MUST start with aws-waf-logs-
  retention_in_days = 30
}

resource "aws_wafv2_web_acl_logging_configuration" "main" {
  log_destination_configs = [aws_cloudwatch_log_group.waf.arn]
  resource_arn            = aws_wafv2_web_acl.main.arn

  redacted_fields {
    single_header { name = "authorization" }
  }
  redacted_fields {
    single_header { name = "cookie" }
  }
}

###############################################################################
# THE INTERVIEW QUESTION: "30 minutes to stop a layer 7 DDoS"
###############################################################################
# In order:
#
# 1. Turn on rate-based rule, 2000 per 5 min per IP, block. (Most attacks die here)
#    aws wafv2 update-web-acl --add-rule ...
#
# 2. Identify attack signature in CloudWatch logs:
#    - Same User-Agent? Block it.
#    - Same path? Block requests to that path from non-office IPs.
#    - Same country? Geo-block.
#
# 3. If attack persists, use AWS Managed Rules:
#    - Core Rule Set in BLOCK mode
#    - Bot Control rule group ($10/mo + $1/M requests, but it works)
#
# 4. If volume is overwhelming WAF, escalate to Shield Advanced if customer has
#    it ($3000/mo, includes DRT). Without Shield Advanced, you have:
#    - CloudFront in front of ALB (CloudFront has built-in volumetric protection)
#    - Route 53 with health checks failing over to a static page
#    - Origin protection by setting ALB security group to only accept
#      CloudFront's IP ranges (managed prefix list AWS::CloudFront::OriginFacing)
#
# 5. Long-term: review and tune managed rules, add custom rules per attack
#    pattern observed, tune rate limits per route (login = 10/min, search = 200/min).
#
###############################################################################
# SHIELD STANDARD VS SHIELD ADVANCED
###############################################################################
#
# Shield Standard:
#   - Free, automatic, on every account
#   - Protects against L3/L4 attacks (SYN flood, UDP reflection, etc)
#   - Always-on, you do not configure it
#
# Shield Advanced:
#   - $3000/mo per organization + data charges
#   - Layer 7 protection (works with WAF)
#   - DDoS Response Team (DRT) - 24/7 phone support
#   - Cost protection: AWS refunds traffic charges from a DDoS
#   - Shield Advanced metrics in CloudWatch
#   - Application Layer DDoS automatic mitigation (ML-driven)
#   - Worth it if you serve high-stakes traffic (gaming, finance, news during events)
#
# Most workloads: Shield Standard + WAF + CloudFront is enough.
###############################################################################

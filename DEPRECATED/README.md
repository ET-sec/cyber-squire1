# Deprecated / Archived Files

This directory contains files from previous iterations of the CoreDirective platform that are no longer current but are preserved for reference.

## Why These Files Are Here

The CoreDirective platform migrated from AWS EC2 (RHEL 9) to DigitalOcean (Ubuntu 24.04) in March 2026. Documentation, Terraform configs, and tools that reference the old AWS architecture have been moved here to keep the active repository clean and accurate.

## Contents

### AWS-Era Documentation

| File | Description |
|------|-------------|
| `CD_AE_COMPLETE_STACK_OVERVIEW.md` | Original AWS EC2 architecture overview |
| `CD_AWS_AUTOMATION.md` | AWS automation workflows |
| `DEPLOYMENT_READINESS_CHECKLIST.md` | EC2-specific deployment checklist |
| `RHEL_System_Init.md` | RHEL 9 system initialization guide |
| `Rclone_Google_Drive_Setup.md` | Google Drive mount (not in current stack) |
| `TERRAFORM_DEPLOYMENT_GUIDE.md` | EC2-specific Terraform deployment guide |
| `TERRAFORM_QUICKREF.md` | EC2 Terraform quick reference |
| `SECURITY_STACK_BUILD_PLAN.md` | Original security stack build plan (AWS) |
| `DOCUMENTATION_STRATEGY.md` | Documentation strategy (AWS-era metrics) |
| `ARCHITECTURE_DIAGRAMS.md` | Architecture diagram descriptions (AWS references) |
| `Systematic_Cartography.md` / `.png` | Early system mapping |

### Legacy Compose Configuration

| Directory | Description |
|-----------|-------------|
| `CD_ENGINE_MASTER/` | Original Docker Compose with old naming conventions |
| `old_workflows/` | n8n workflows referencing deprecated Qwen 2.5 models |

### Legacy Code

| Directory | Description |
|-----------|-------------|
| `standalone_tools/` | Early Node.js automation tools (finance_manager.js, security_scanner.js, etc.) |

### Meta

| File | Description |
|------|-------------|
| `CHANGELOG_DEPRECATIONS.md` | Deprecation changelog |

## Current Architecture

The active stack runs on DigitalOcean with 14 containers (13 Compose + 1 standalone). See:

- Root `CLAUDE.md` for full infrastructure reference
- `docs/grc/` for the 20-document NIST 800-53 compliance library
- `docs/Technical_Vault.md` for architecture deep-dive
- `docs/Employment_Proof.md` for business case overview

---

**Last Updated:** 2026-03-12
**Maintained By:** Emmanuel Tigoue

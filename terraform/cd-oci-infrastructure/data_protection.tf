# --- DATA PROTECTION (CD-OCI-INFRASTRUCTURE) ---
# Phase 20.1-03. Customer-managed encryption + ransomware-resistant backups.
#
# Design notes:
# - Vault type DEFAULT (shared partition). Virtual private vaults are outside
#   this tenancy's entitlement; do not change vault_type.
# - protection_mode SOFTWARE: unlimited free key versions. HSM would bill past
#   20 versions. Do not change without a costed decision record.
# - Envelope model: this key (the KEK) wraps per-object data keys inside the
#   Object Storage service. Rotation re-wraps DEKs; it never re-encrypts data.
# - The backup bucket carries a retention rule: objects are undeletable and
#   unmodifiable for 30 days, even by the writer. The rule itself is left
#   UNLOCKED on purpose (locking is irreversible); tradeoff documented in
#   DR-03. Retention requires versioning to stay Disabled on this bucket.
# - The instance authenticates by instance principal (dynamic group), so the
#   backup job on the host holds no stored cloud credential at all.

resource "oci_kms_vault" "cd" {
  compartment_id = local.compartment
  display_name   = "cd-vault"
  vault_type     = "DEFAULT"
  freeform_tags  = var.tags
}

resource "oci_kms_key" "storage" {
  compartment_id      = local.compartment
  display_name        = "cd-storage-cmk"
  management_endpoint = oci_kms_vault.cd.management_endpoint
  protection_mode     = "SOFTWARE"
  freeform_tags       = var.tags

  key_shape {
    algorithm = "AES"
    length    = 32
  }
}

data "oci_objectstorage_namespace" "ns" {
  compartment_id = local.compartment
}

# Existing state bucket (created 2026-08-31 via CLI during 20.1-01), imported
# so encryption moves to the customer-managed key and config stops being
# hand-managed. Versioning stays Enabled: it is the state-recovery layer.
# Bucket name comes from a variable (gitignored tfvars locally, secret in CI):
# the name is part of the state backend address and stays out of the public
# repo alongside the namespace, same boundary as backend.hcl.
resource "oci_objectstorage_bucket" "tfstate" {
  compartment_id        = local.compartment
  namespace             = data.oci_objectstorage_namespace.ns.namespace
  name                  = var.tfstate_bucket_name
  access_type           = "NoPublicAccess"
  versioning            = "Enabled"
  kms_key_id            = oci_kms_key.storage.id
  object_events_enabled = true # CKV_OCI_7: future Events-service detection hook
  freeform_tags         = var.tags
}

resource "oci_objectstorage_bucket" "backups" {
  # checkov:skip=CKV_OCI_8: OCI forbids object versioning on buckets with
  # retention rules, and the retention lock is the stronger control here
  # (ransomware cannot delete what the service refuses to delete). Versioned
  # recovery is the state bucket's job; immutability is this bucket's job.
  compartment_id        = local.compartment
  namespace             = data.oci_objectstorage_namespace.ns.namespace
  name                  = "cd-backups"
  access_type           = "NoPublicAccess"
  kms_key_id            = oci_kms_key.storage.id
  object_events_enabled = true # CKV_OCI_7
  freeform_tags         = var.tags

  retention_rules {
    display_name = "ransomware-guard-30d"
    duration {
      time_amount = 30
      time_unit   = "DAYS"
    }
  }
}

# Object Storage encrypts/decrypts bucket objects with the CMK on our behalf;
# the service principal needs use-keys, scoped to this one key.
resource "oci_identity_policy" "objectstorage_kms" {
  compartment_id = local.compartment
  name           = "cd-objectstorage-use-cmk"
  description    = "Object Storage service may use the storage CMK (scoped to the key)"
  freeform_tags  = var.tags
  statements = [
    "Allow service objectstorage-${var.oci_region} to use keys in compartment id ${local.compartment} where target.key.id = '${oci_kms_key.storage.id}'",
  ]
}

# The instance IS the identity: no stored credential on the host.
resource "oci_identity_dynamic_group" "backup_agents" {
  compartment_id = var.oci_tenancy_ocid
  name           = "cd-backup-agents"
  description    = "cd_alpha instance principal, used by the backup/restore jobs"
  freeform_tags  = var.tags
  matching_rule  = "instance.id = '${oci_core_instance.cd_alpha.id}'"
}

resource "oci_identity_policy" "backup_agents" {
  compartment_id = local.compartment
  name           = "cd-backup-agents-policy"
  description    = "Least privilege: create/read/list objects in cd-backups only. No delete: the retention rule is the delete guard anyway, and the writer holding delete rights is the ransomware scenario."
  freeform_tags  = var.tags
  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_agents.name} to read buckets in compartment id ${local.compartment} where target.bucket.name = 'cd-backups'",
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_agents.name} to manage objects in compartment id ${local.compartment} where all {target.bucket.name = 'cd-backups', any {request.permission = 'OBJECT_CREATE', request.permission = 'OBJECT_READ', request.permission = 'OBJECT_INSPECT'}}",
  ]
}

# --- Vault seal key (plan 24-02) ---
# A second AES key in the same vault, for the secrets manager's auto-unseal and
# nothing else. The storage key is never reused for a second purpose, and the
# dynamic group's use of this key is scoped to its id: the instance principal
# can wrap and unwrap the seal, and cannot touch the storage key or any other.
resource "oci_kms_key" "vault_seal" {
  compartment_id      = local.compartment
  display_name        = "cd-vault-seal"
  management_endpoint = oci_kms_vault.cd.management_endpoint
  protection_mode     = "SOFTWARE"
  freeform_tags       = var.tags

  key_shape {
    algorithm = "AES"
    length    = 32
  }
}

resource "oci_identity_policy" "vault_seal_agents" {
  compartment_id = local.compartment
  name           = "cd-vault-seal-use-key"
  description    = "The instance principal may use the seal key (scoped to the key id); no key management, no other key"
  freeform_tags  = var.tags
  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.backup_agents.name} to use keys in compartment id ${local.compartment} where target.key.id = '${oci_kms_key.vault_seal.id}'",
  ]
}

output "backup_bucket" {
  description = "Retention-locked backup bucket"
  value       = oci_objectstorage_bucket.backups.name
}

output "storage_cmk_id" {
  description = "Customer-managed key OCID (rotation target)"
  value       = oci_kms_key.storage.id
}

output "vault_seal_key_id" {
  description = "Seal key OCID for the secrets manager (read into the host environment file, never tracked)"
  value       = oci_kms_key.vault_seal.id
}

output "kms_crypto_endpoint" {
  description = "Crypto endpoint of the vault that holds the seal key"
  value       = oci_kms_vault.cd.crypto_endpoint
}

output "kms_management_endpoint" {
  description = "Management endpoint of the vault that holds the seal key"
  value       = oci_kms_vault.cd.management_endpoint
}

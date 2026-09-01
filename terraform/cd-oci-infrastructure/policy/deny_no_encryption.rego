# DENY: Require a customer managed key on every object storage bucket
#
# Intent: every oci_objectstorage_bucket must reference a kms_key_id,
# meaning it is encrypted with our customer managed key (CMK) out of
# the cd-vault, not just Oracle's default key. The enemy is losing key
# custody: with Oracle managed keys we cannot rotate, revoke, or prove
# control of the encryption key that guards backups and terraform state.

package main

import rego.v1

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_objectstorage_bucket"
	not enc_is_delete(rc)
	bucket := rc.change.after
	not bucket_has_cmk(bucket)
	msg := sprintf(
		"DENY: Bucket '%s' has no kms_key_id. All buckets must use the customer managed key from cd-vault.",
		[bucket.name],
	)
}

bucket_has_cmk(bucket) if {
	bucket.kms_key_id != null
	bucket.kms_key_id != ""
}

enc_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

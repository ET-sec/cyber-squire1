# DENY: Block deletion of stateful and key custody resources
#
# Intent: buckets (backups, terraform state), the KMS key, and the KMS
# vault must never be casually destroyable. The enemy is the accidental
# `terraform destroy` or an attribute change that forces replacement and
# quietly deletes the data or the key that decrypts it. Losing the CMK
# is unrecoverable: everything it encrypted becomes ciphertext forever.
#
# Enforcement happens at plan level because lifecycle.prevent_destroy
# does not appear in plan JSON attributes. We inspect the planned
# actions instead: any change whose actions include "delete" is blocked,
# unless it is a create before destroy replacement (actions ordered
# ["create", "delete"]), where the successor exists before the old
# resource goes away.

package main

import rego.v1

protected_types := {
	"oci_objectstorage_bucket",
	"oci_kms_key",
	"oci_kms_vault",
}

deny contains msg if {
	some rc in input.resource_changes
	rc.type in protected_types
	"delete" in rc.change.actions
	not create_before_destroy(rc)
	msg := sprintf(
		"DENY: Plan destroys protected resource '%s' (type: %s). Stateful and key custody resources must not be deleted.",
		[rc.address, rc.type],
	)
}

create_before_destroy(rc) if {
	rc.change.actions == ["create", "delete"]
}

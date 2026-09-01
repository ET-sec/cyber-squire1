# WARN: The plan must keep a retention rule on object storage
#
# Intent: at least one oci_objectstorage_bucket in the plan must carry
# a retention_rules block. The cd-backups bucket holds the ransomware
# guard copies, and its retention rule is what stops an attacker (or a
# bad script) with write access from deleting or overwriting the
# backups. The enemy is ransomware that encrypts the host and then
# reaches for the backups; retention makes those objects immutable for
# the retention window. If a plan drops the last retention rule, the
# guard is gone even though every individual resource still looks fine.

package main

import rego.v1

warn contains msg if {
	count(planned_buckets) > 0
	not some_bucket_has_retention
	msg := "WARN: No object storage bucket in this plan carries a retention rule. The ransomware guard backup bucket must keep its retention_rules block."
}

planned_buckets contains rc.address if {
	some rc in input.resource_changes
	rc.type == "oci_objectstorage_bucket"
	not bk_is_delete(rc)
}

some_bucket_has_retention if {
	some rc in input.resource_changes
	rc.type == "oci_objectstorage_bucket"
	not bk_is_delete(rc)
	count(rc.change.after.retention_rules) > 0
}

bk_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

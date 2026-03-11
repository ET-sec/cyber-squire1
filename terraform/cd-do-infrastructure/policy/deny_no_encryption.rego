# DENY: Require versioning on Spaces buckets
#
# DigitalOcean encrypts all block storage at rest by default.
# This policy enforces versioning on Spaces buckets as a data
# integrity and recovery safeguard (our proxy for encryption-at-rest
# assurance on object storage).

package main

import rego.v1

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_spaces_bucket"
	not action_is_delete(rc)
	bucket := rc.change.after
	not versioning_enabled(bucket)
	msg := sprintf(
		"DENY: Spaces bucket '%s' must have versioning enabled for data integrity.",
		[bucket.name],
	)
}

versioning_enabled(bucket) if {
	some v in bucket.versioning
	v.enabled == true
}

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_volume"
	not action_is_delete(rc)
	vol := rc.change.after
	not has_filesystem_type(vol)
	msg := sprintf(
		"DENY: Volume '%s' must have filesystem_type set (ext4 or xfs).",
		[vol.name],
	)
}

has_filesystem_type(vol) if {
	vol.filesystem_type != null
	vol.filesystem_type != ""
}

# DENY: Require key based SSH on compute instances
#
# Intent: every oci_core_instance must launch with ssh_authorized_keys
# in its metadata. The enemy is an instance that falls back to password
# authentication or console only access, which invites credential
# guessing and leaves no per user key to audit or revoke.
#
# Companion WARN: the legacy IMDSv1 endpoint must be disabled
# (instance_options.are_legacy_imds_endpoints_disabled = true). The
# enemy there is SSRF style credential theft: any process that can make
# an HTTP request to the metadata service can steal instance principal
# credentials when the unauthenticated v1 endpoint is left on.

package main

import rego.v1

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_core_instance"
	not ssh_is_delete(rc)
	inst := rc.change.after
	not has_ssh_keys(inst)
	msg := sprintf(
		"DENY: Instance '%s' has no ssh_authorized_keys in metadata. Key based SSH is required.",
		[inst.display_name],
	)
}

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_core_instance"
	not ssh_is_delete(rc)
	inst := rc.change.after
	not imds_hardened(inst)
	msg := sprintf(
		"WARN: Instance '%s' does not set instance_options.are_legacy_imds_endpoints_disabled = true. Legacy IMDSv1 enables credential theft via SSRF.",
		[inst.display_name],
	)
}

has_ssh_keys(inst) if {
	keys := inst.metadata.ssh_authorized_keys
	is_string(keys)
	trim_space(keys) != ""
}

imds_hardened(inst) if {
	some opt in inst.instance_options
	opt.are_legacy_imds_endpoints_disabled == true
}

ssh_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

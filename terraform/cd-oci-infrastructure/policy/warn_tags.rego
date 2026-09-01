# WARN: Taggable resources must carry project and env freeform tags
#
# Intent: every taggable resource sets freeform_tags with at least the
# project and env keys. The enemy is the untraceable resource: without
# tags, cost attribution, environment scoping, and automated cleanup
# all break, and a stray production resource can hide as lab clutter.

package main

import rego.v1

taggable_types := {
	"oci_core_instance",
	"oci_core_vcn",
	"oci_core_subnet",
	"oci_core_security_list",
	"oci_core_route_table",
	"oci_core_internet_gateway",
	"oci_objectstorage_bucket",
	"oci_kms_key",
	"oci_kms_vault",
	"oci_identity_dynamic_group",
	"oci_identity_policy",
}

required_tag_keys := {"project", "env"}

warn contains msg if {
	some rc in input.resource_changes
	rc.type in taggable_types
	not tg_is_delete(rc)
	some key in required_tag_keys
	not has_tag(rc.change.after, key)
	msg := sprintf(
		"WARN: Resource '%s' is missing freeform tag '%s'. Tag with project and env for cost tracking and scoping.",
		[rc.address, key],
	)
}

has_tag(after, key) if {
	after.freeform_tags[key] != ""
}

tg_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

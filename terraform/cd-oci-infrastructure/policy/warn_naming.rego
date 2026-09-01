# WARN: Resources should follow the cd- prefix naming convention
#
# Intent: every CoreDirective resource with a display_name or name
# attribute starts with "cd-". The enemy is the anonymous resource:
# when something is named "test" or "instance1" nobody can tell at a
# glance whether it belongs to this stack, which slows incident
# response and lets orphans survive cost reviews.
#
# OCI shape note: core and KMS resources use display_name, while
# buckets and identity resources use name. Whichever exists is checked.

package main

import rego.v1

warn contains msg if {
	some rc in input.resource_changes
	not nm_is_delete(rc)
	label := resource_label(rc.change.after)
	not startswith(label, "cd-")
	msg := sprintf(
		"WARN: Resource '%s' name '%s' does not follow the 'cd-' prefix convention.",
		[rc.address, label],
	)
}

resource_label(after) := after.display_name if {
	is_string(after.display_name)
}

resource_label(after) := after.name if {
	not is_string(after.display_name)
	is_string(after.name)
}

nm_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

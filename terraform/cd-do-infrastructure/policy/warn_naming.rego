# WARN: Resources should follow cd- prefix naming convention
#
# All CoreDirective infrastructure resources should use the cd-
# prefix for consistent identification and cost tracking.

package main

import rego.v1

naming_checked_types := {
	"digitalocean_droplet",
	"digitalocean_firewall",
}

warn contains msg if {
	some rc in input.resource_changes
	rc.type in naming_checked_types
	not action_is_delete(rc)
	name := rc.change.after.name
	not startswith(name, "cd-")
	msg := sprintf(
		"WARN: Resource '%s' name '%s' does not follow 'cd-' prefix convention.",
		[rc.address, name],
	)
}

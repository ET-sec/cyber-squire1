# DENY: Block SSH keys with "root" in the name
#
# SSH keys should be named after individual users for audit trail.
# Keys named "root" indicate shared credential anti-pattern.

package main

import rego.v1

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_ssh_key"
	not action_is_delete(rc)
	key := rc.change.after
	contains(lower(key.name), "root")
	msg := sprintf(
		"DENY: SSH key '%s' contains 'root' in name. Use named user keys only.",
		[key.name],
	)
}

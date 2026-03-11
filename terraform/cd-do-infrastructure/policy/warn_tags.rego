# WARN: Droplets should have tags for cost tracking and filtering
#
# Tags enable resource filtering in the DO console and API,
# cost attribution, and automated operations.

package main

import rego.v1

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_droplet"
	not action_is_delete(rc)
	droplet := rc.change.after
	not has_tags(droplet)
	msg := sprintf(
		"WARN: Droplet '%s' has no tags. Add tags for cost tracking and filtering.",
		[droplet.name],
	)
}

has_tags(droplet) if {
	count(droplet.tags) > 0
}

# WARN: Droplets should have backups enabled
#
# DigitalOcean weekly backups provide disaster recovery at
# 20% of droplet cost. Recommended for all production workloads.

package main

import rego.v1

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_droplet"
	not action_is_delete(rc)
	droplet := rc.change.after
	not droplet.backups
	msg := sprintf(
		"WARN: Droplet '%s' does not have backups enabled. Consider enabling for disaster recovery.",
		[droplet.name],
	)
}

# WARN: Flag expensive droplet sizes for cost review
#
# Large droplet sizes should be explicitly justified.
# This warns on sizes that exceed typical workload needs
# to prevent accidental over-provisioning.

package main

import rego.v1

expensive_sizes := {
	"s-8vcpu-16gb",
	"s-16vcpu-32gb",
	"s-24vcpu-48gb",
	"s-32vcpu-64gb",
	"g-2vcpu-8gb",
	"g-4vcpu-16gb",
	"g-8vcpu-32gb",
	"gd-2vcpu-8gb",
	"gd-4vcpu-16gb",
	"gd-8vcpu-32gb",
	"m-2vcpu-16gb",
	"m-4vcpu-32gb",
	"so-2vcpu-16gb",
	"so-4vcpu-32gb",
}

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_droplet"
	not action_is_delete(rc)
	droplet := rc.change.after
	droplet.size in expensive_sizes
	msg := sprintf(
		"WARN: Droplet '%s' uses size '%s'. Verify this is cost-appropriate.",
		[droplet.name, droplet.size],
	)
}

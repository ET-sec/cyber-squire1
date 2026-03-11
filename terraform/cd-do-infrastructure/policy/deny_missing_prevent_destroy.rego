# DENY: Block deletion of production resources
#
# Critical production resource types must not be destroyed via
# Terraform apply. This catches accidental `terraform destroy` or
# resource replacement that would delete production data.

package main

import rego.v1

production_types := {
	"digitalocean_droplet",
	"digitalocean_spaces_bucket",
	"digitalocean_volume",
	"digitalocean_database_cluster",
}

deny contains msg if {
	some rc in input.resource_changes
	rc.type in production_types
	action_includes_delete(rc)
	msg := sprintf(
		"DENY: Attempted deletion of production resource '%s' (type: %s). Must have lifecycle.prevent_destroy.",
		[rc.address, rc.type],
	)
}

action_includes_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

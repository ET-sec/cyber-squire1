# WARN: Flag instance shapes that leave the Always Free tier
#
# Intent: the compute footprint stays inside Oracle's Always Free
# A1.Flex allowance of 4 OCPUs and 24 GB memory total. The enemy is
# the silent bill: one extra OCPU or GB in shape_config and the tenancy
# starts metering charges. Exceeding the limit is allowed only as an
# explicit, reviewed decision.

package main

import rego.v1

free_tier_max_ocpus := 4

free_tier_max_memory_gbs := 24

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_core_instance"
	not sz_is_delete(rc)
	inst := rc.change.after
	some cfg in inst.shape_config
	over_free_tier(cfg)
	msg := sprintf(
		"WARN: Instance '%s' shape_config (%v OCPUs, %v GB) exceeds Always Free limits (%v OCPUs, %v GB). This starts billing.",
		[inst.display_name, cfg.ocpus, cfg.memory_in_gbs, free_tier_max_ocpus, free_tier_max_memory_gbs],
	)
}

over_free_tier(cfg) if {
	cfg.ocpus > free_tier_max_ocpus
}

over_free_tier(cfg) if {
	cfg.memory_in_gbs > free_tier_max_memory_gbs
}

sz_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

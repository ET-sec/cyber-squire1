# DENY: Block public internet access on non-HTTPS ports
#
# Any digitalocean_firewall inbound_rule allowing 0.0.0.0/0 or ::/0
# MUST be restricted to port 443 (HTTPS) only.
#
# NOTE: The existing cd-alpha-firewall has SSH (22) open to 0.0.0.0/0
# as a break-glass emergency access path (CKV_DIO_4 intentionally skipped).
# This policy will flag it -- the violation is an accepted risk documented
# in the security risk register, not an oversight.

package main

import rego.v1

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "digitalocean_firewall"
	not action_is_delete(rc)
	fw := rc.change.after
	some rule in fw.inbound_rule
	rule.protocol != "icmp"
	has_public_source(rule)
	not port_is_https(rule)
	msg := sprintf(
		"DENY: Firewall '%s' allows public inbound on port %s. Only HTTPS (443) permitted from 0.0.0.0/0.",
		[fw.name, rule.port_range],
	)
}

action_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

has_public_source(rule) if {
	some addr in rule.source_addresses
	addr == "0.0.0.0/0"
}

has_public_source(rule) if {
	some addr in rule.source_addresses
	addr == "::/0"
}

port_is_https(rule) if {
	rule.port_range == "443"
}

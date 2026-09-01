# DENY: Block SSH open to the whole internet on OCI security lists
#
# Intent: no oci_core_security_list ingress rule may expose TCP port 22
# to 0.0.0.0/0 or ::/0. The enemy is the drive-by SSH brute forcer that
# scans the entire IPv4 space within minutes of a port opening. SSH must
# only be reachable from the pinned operator /32 addresses.
#
# Any other broad-source ingress rule (public source, port other than 22)
# is surfaced as a WARN naming the rule, so intentional exposure is a
# reviewed decision instead of a silent one.
#
# OCI plan shape notes: protocol is a string IANA number ("6" TCP,
# "17" UDP, "1" ICMP, "58" ICMPv6, "all"). An empty tcp_options list
# means every TCP port, which includes 22.

package main

import rego.v1

public_sources := {"0.0.0.0/0", "::/0"}

icmp_protocols := {"1", "58"}

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_core_security_list"
	not fw_is_delete(rc)
	sl := rc.change.after
	some rule in sl.ingress_security_rules
	rule.source in public_sources
	rule_reaches_ssh(rule)
	msg := sprintf(
		"DENY: Security list '%s' allows SSH (TCP 22) from '%s'. SSH must be restricted to operator /32 CIDRs.",
		[sl.display_name, rule.source],
	)
}

warn contains msg if {
	some rc in input.resource_changes
	rc.type == "oci_core_security_list"
	not fw_is_delete(rc)
	sl := rc.change.after
	some rule in sl.ingress_security_rules
	rule.source in public_sources
	not rule.protocol in icmp_protocols
	not rule_reaches_ssh(rule)
	msg := sprintf(
		"WARN: Security list '%s' has a broad ingress rule (protocol %s, ports %s) open to '%s'. Confirm this exposure is intentional.",
		[sl.display_name, rule.protocol, rule_port_summary(rule), rule.source],
	)
}

# Rule reaches port 22 when the protocol is "all",
# or it is TCP with no port filter (all ports),
# or it is TCP with a range that covers 22.
rule_reaches_ssh(rule) if {
	rule.protocol == "all"
}

rule_reaches_ssh(rule) if {
	rule.protocol == "6"
	count(rule.tcp_options) == 0
}

rule_reaches_ssh(rule) if {
	rule.protocol == "6"
	some opt in rule.tcp_options
	opt.min <= 22
	opt.max >= 22
}

rule_port_summary(rule) := out if {
	count(rule.tcp_options) > 0
	ranges := [sprintf("%v-%v", [opt.min, opt.max]) | some opt in rule.tcp_options]
	out := concat(",", ranges)
}

rule_port_summary(rule) := "all" if {
	count(rule.tcp_options) == 0
}

fw_is_delete(rc) if {
	some action in rc.change.actions
	action == "delete"
}

# DENY: Services must not use host network mode
#
# network_mode: host removes container network isolation. The container
# binds directly on the host's network namespace, exposing every listening
# port and bypassing Docker network policies.
#
# Exception: tunnel-cyber-squire (Cloudflare Tunnel) requires host network
# mode to forward traffic from the host's loopback interfaces to Cloudflare.
# This is the only documented exception.

package main

import rego.v1

deny contains msg if {
	some name, svc in input.services
	svc.network_mode == "host"
	not host_network_allowed(name)
	msg := sprintf(
		"DENY: service '%s' uses network_mode: host. Only tunnel-cyber-squire is permitted host network.",
		[name],
	)
}

host_network_allowed(name) if {
	name in {
		"tunnel-cyber-squire",
	}
}

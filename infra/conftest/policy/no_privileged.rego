# DENY: Containers must not run with privileged: true
#
# Privileged containers can access all host devices, escape namespace
# boundaries, and modify kernel modules. There is no service in the
# CoreDirective stack that requires privileged mode. Falco needs
# capabilities, not privileged. Cloudflare Tunnel needs network host,
# not privileged.

package main

import rego.v1

deny contains msg if {
	some name, svc in input.services
	svc.privileged == true
	msg := sprintf(
		"DENY: service '%s' uses privileged: true. Use cap_add for specific capabilities instead.",
		[name],
	)
}

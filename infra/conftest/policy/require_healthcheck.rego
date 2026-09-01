# WARN: Services should declare a healthcheck
#
# Without a healthcheck, Docker cannot tell whether a container is
# functioning or just sitting in a broken state. Compose dependency
# ordering (depends_on with condition: service_healthy) requires this.
# Operational visibility and auto-restart on failure both depend on it.
#
# Some images ship a built-in HEALTHCHECK directive in their Dockerfile.
# This policy warns rather than denies because of that overlap; promote
# to deny once the inventory is verified.

package main

import rego.v1

warn contains msg if {
	some name, svc in input.services
	not svc.healthcheck
	not has_image_builtin_healthcheck(name)
	msg := sprintf(
		"WARN: service '%s' declares no healthcheck. Add one or confirm the base image ships one.",
		[name],
	)
}

# Allow list: services whose base image ships a verified HEALTHCHECK directive.
# Keep this list small and audited.
has_image_builtin_healthcheck(name) if {
	name in {
		"cd-service-datadog",
	}
}

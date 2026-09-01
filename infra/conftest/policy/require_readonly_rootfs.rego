# WARN: Containers should run with read_only: true root filesystem
#
# A read-only root filesystem stops attackers from writing webshells,
# persisting backdoors, or modifying binaries inside a compromised
# container. Services that need writable paths declare them explicitly
# via tmpfs or named volumes.
#
# Stateful services (postgres, n8n, vault, ollama, whisper, langfuse,
# squire app) need a writable rootfs or a writable data path. They are
# the documented exceptions.

package main

import rego.v1

warn contains msg if {
	some name, svc in input.services
	not svc.read_only
	not stateful_service(name)
	msg := sprintf(
		"WARN: service '%s' has no read_only: true. Set it or document the writable-rootfs requirement.",
		[name],
	)
}

stateful_service(name) if {
	name in {
		"cd-service-db",
		"cd-service-n8n",
		"cd-service-vault",
		"cd-service-ollama",
		"cd-service-whisper",
		"cd-service-langfuse",
		"cd-service-squire",
		"cd-service-keycloak",
	}
}

# DENY: Services must declare memory limits
#
# An unbounded container can OOM-kill the entire droplet. The CoreDirective
# stack runs on a single 8GB droplet hosting 14 containers. Without limits,
# one runaway service (Ollama loading a too-large model, n8n stuck workflow,
# Datadog memory leak) takes the whole platform down.
#
# Accepts both Compose v2 syntax (mem_limit) and v3 syntax (deploy.resources.limits.memory).

package main

import rego.v1

deny contains msg if {
	some name, svc in input.services
	not has_memory_limit(svc)
	msg := sprintf(
		"DENY: service '%s' has no memory limit. Set mem_limit or deploy.resources.limits.memory.",
		[name],
	)
}

has_memory_limit(svc) if {
	svc.mem_limit
}

has_memory_limit(svc) if {
	svc.deploy.resources.limits.memory
}

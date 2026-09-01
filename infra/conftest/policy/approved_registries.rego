# DENY: Container images must come from an approved registry
#
# Pulling from an arbitrary registry exposes the supply chain to
# typosquatting, registry compromise, and unverified maintainers.
# The CoreDirective allow list covers Docker Hub official, GitHub
# Container Registry, Quay (HashiCorp + Red Hat), Google Container
# Registry (Falco), and Datadog's registry.

package main

import rego.v1

# Explicit registry hosts (anything before the first slash).
allowed_registry_hosts := [
	"docker.io",
	"registry-1.docker.io",
	"ghcr.io",
	"quay.io",
	"gcr.io",
	"public.ecr.aws",
]

# Docker Hub vendor namespaces (used when the image is in shorthand form
# `<vendor>/<image>` with no explicit registry host).
allowed_dockerhub_vendors := [
	"datadog",
	"falcosecurity",
	"hashicorp",
	"keycloak",
	"langfuse",
	"clickhouse",
	"n8nio",
	"ollama",
	"pgvector",
	"fedirz",
	"cloudflare",
	"library",
]

# Locally-built images use the `cd-service-` prefix and are pinned to a
# digest or commit SHA via CI. They have no registry component.
allowed_local_build_prefixes := [
	"cd-service-",
]

deny contains msg if {
	some name, svc in input.services
	svc.image
	not image_from_approved_source(svc.image)
	msg := sprintf(
		"DENY: service '%s' image '%s' is not from an approved registry. See infra/conftest/policy/approved_registries.rego.",
		[name, svc.image],
	)
}

# Locally-built image: matches one of the approved prefixes with no slash.
image_from_approved_source(image) if {
	not contains(image, "/")
	some prefix in allowed_local_build_prefixes
	startswith(image, prefix)
}

# Explicit registry host: `<host>/<path>:<tag>` where <host> contains a dot.
image_from_approved_source(image) if {
	parts := split(image, "/")
	count(parts) >= 2
	contains(parts[0], ".")
	some host in allowed_registry_hosts
	parts[0] == host
}

# Docker Hub shorthand: `<vendor>/<image>:<tag>` with no dot in vendor.
image_from_approved_source(image) if {
	parts := split(image, "/")
	count(parts) >= 2
	not contains(parts[0], ".")
	some vendor in allowed_dockerhub_vendors
	parts[0] == vendor
}

# Docker Hub library shorthand: `<image>:<tag>` (e.g. `postgres:16`, `redis:7`).
image_from_approved_source(image) if {
	not contains(image, "/")
	contains(image, ":")
	not startswith(image, "cd-service-")
}

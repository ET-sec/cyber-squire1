# DENY: Container images must not use the :latest tag or omit the tag
#
# An image without a pinned tag is non-reproducible. The same compose file
# that deploys cleanly today can deploy a vulnerable or breaking image
# tomorrow. Pin every image to a specific version or digest so deploys
# are deterministic and rollbacks are possible.

package main

import rego.v1

deny contains msg if {
	some name, svc in input.services
	svc.image
	endswith(svc.image, ":latest")
	msg := sprintf(
		"DENY: service '%s' uses image '%s' with :latest tag. Pin to a specific version.",
		[name, svc.image],
	)
}

deny contains msg if {
	some name, svc in input.services
	svc.image
	not contains(svc.image, ":")
	not contains(svc.image, "@sha256:")
	msg := sprintf(
		"DENY: service '%s' uses image '%s' with no tag (defaults to :latest). Pin to a specific version.",
		[name, svc.image],
	)
}

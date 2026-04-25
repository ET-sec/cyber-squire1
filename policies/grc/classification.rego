package main

import rego.v1

allowed_classifications := {"PUBLIC", "INTERNAL", "CONFIDENTIAL"}

deny contains msg if {
  not data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  cls := input[doc].classification
  cls != null
  not allowed_classifications[cls]
  msg := sprintf("doc %s has invalid classification %q (allowed: %v)", [doc, cls, allowed_classifications])
}

warn contains msg if {
  data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  cls := input[doc].classification
  cls != null
  not allowed_classifications[cls]
  msg := sprintf("[soft-fail] doc %s has invalid classification %q", [doc, cls])
}

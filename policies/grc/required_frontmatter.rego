package main

import rego.v1

required := {"title", "version", "classification", "owner", "last_reviewed", "residual_risk"}

deny contains msg if {
  not data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  some key in required
  not input[doc][key]
  msg := sprintf("doc %s missing required frontmatter key: %s", [doc, key])
}

warn contains msg if {
  data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  some key in required
  not input[doc][key]
  msg := sprintf("[soft-fail] doc %s missing required frontmatter key: %s", [doc, key])
}

deny contains msg if {
  not data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  v := input[doc].version
  v != null
  not is_string(v)
  msg := sprintf("doc %s version must be string (got %v)", [doc, v])
}

warn contains msg if {
  data.config.soft_fail
  some doc
  input[doc]
  not startswith(doc, "_")
  v := input[doc].version
  v != null
  not is_string(v)
  msg := sprintf("[soft-fail] doc %s version must be string (got %v)", [doc, v])
}

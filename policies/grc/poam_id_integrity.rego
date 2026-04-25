package main

import rego.v1

valid_poam_ids contains id if {
  id := input["POAM_PLAN_OF_ACTION.md"].poam_ids[_]
}

deny contains msg if {
  not data.config.soft_fail
  some doc
  input[doc].referenced_poam_ids
  pid := input[doc].referenced_poam_ids[_]
  not valid_poam_ids[pid]
  msg := sprintf("%s references %s which is not in POAM_PLAN_OF_ACTION.md", [doc, pid])
}

warn contains msg if {
  data.config.soft_fail
  some doc
  input[doc].referenced_poam_ids
  pid := input[doc].referenced_poam_ids[_]
  not valid_poam_ids[pid]
  msg := sprintf("[soft-fail] %s references %s not in POAM_PLAN_OF_ACTION.md", [doc, pid])
}

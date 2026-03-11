# TFLint configuration for CoreDirective DO infrastructure
# Runs via pre-commit hook on every commit touching .tf files

plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

# Disable terraform_unused_declarations -- produces false positives
# on locals used inside join() string interpolation (e.g., cost_str
# locals referenced as ${local.droplet_cost_str} inside join() lists).
# TFLint cannot detect references inside interpolated strings within
# function arguments, so it incorrectly flags them as unused.
rule "terraform_unused_declarations" {
  enabled = false
}

config {
  # No modules in this project -- flat file layout
  call_module_type = "none"
}

# Lab 12: Falco Runtime Triage

## Setup

This lab uses Falco's actual JSON output schema. Falco runs on the cd-alpha droplet over the COREDIRECTIVE_ENGINE container set (n8n, postgres, vault, ollama, etc.). Each event has the standard Falco fields: `time`, `priority`, `rule`, `output`, `output_fields`.

Real Falco JSON: https://falco.org/docs/alerts/output-formats/

## What This Lab Trains

Triage speed under volume. 10 alerts, 5 min cap each, decisive output. Sequence pattern recognition: alerts cluster into incidents, isolated alerts are usually noise.

## Run It

```bash
cd labs/lab_12_falco_runtime_anomaly

# Show all alerts
jq -c '{ts: .time, rule, priority, container: .output_fields["container.name"]}' falco.json

# Group by container to see incident clusters
jq -r '"\(.time) \(.output_fields["container.name"]) \(.rule)"' falco.json | sort

# Critical alerts only
jq 'select(.priority == "Critical" or .priority == "Warning")' falco.json
```

Then open `triage.md` and triage each one. The answer key is at the bottom of `triage.md`. Do not read it first.

## Triage Outcome

Across the 10 alerts, two incidents and one tuning candidate:

1. cd-service-n8n compromise (alerts 1-4): shell, /etc/shadow read, C2 connection, persistence drop. Auto-page incident.
2. cd-service-vault compromise (alerts 6-7): shell in Vault, privileged container spawned. Auto-page incident.
3. Prometheus container start (alert 9): noise. Tune Falco config.

The senior signal is correlation. Each Falco rule fires correctly. The SIEM has to stitch them into incidents.

## Interviewer Questions

- "What is Falco?" Open source runtime security engine. Reads kernel events via eBPF (modern) or kernel module (legacy), evaluates them against YAML rules, emits alerts. Default ruleset covers hundreds of TTPs. Custom rules for your environment. Standard for K8s and container runtime detection.
- "What is the difference between Falco rule priorities?" Emergency, Alert, Critical, Error, Warning, Notice, Informational, Debug. Map to syslog levels. By convention, Critical and above page, Warning escalates, Notice goes to ticketing, Informational goes to a dashboard only.
- "Why is shell-in-container so commonly noisy?" Because dev environments shell into containers all day. Production should not. The rule needs context: image, namespace, node label, and user. A shell in `dev-*` namespace is fine. A shell in `prod-payments` is a page.
- "How do you tune Falco?" YAML override files. `rules.d/custom-rules.yaml` for additions, `rules.d/overrides.yaml` for tuning. Use `macros` to abstract reusable predicates (`known_user_pods`, `legit_admin_users`).
- "How does Falco compare to commercial runtime?" Aqua, Sysdig (the commercial company behind Falco), Sysdig Secure, StackRox (now part of Red Hat), Wiz Runtime, Datadog Cloud Workload Security. Commercial tools add management UI, reporting, integrations, scale features. Falco is the open core. Most of them ARE Falco under the hood.
- "What about eBPF directly?" If Falco rules cannot express what you need, write the eBPF probe yourself with Tracee, BCC, or libbpf-based tools. Higher engineering cost, more flexibility. Tracee specifically is a Falco-alternative with a modern eBPF stack.

## Variant: Production Detection Stack on the Droplet

```yaml
# Falco custom rule for Vault container — never spawn anything but vault
- rule: Vault Container Anomalous Process
  desc: Any process other than vault running in the Vault container
  condition: container.name = "cd-service-vault" and not proc.name in (vault, runc)
  output: "Vault container ran %proc.name (cmd=%proc.cmdline user=%user.name)"
  priority: CRITICAL
  tags: [vault, runtime, t1078]
```

This is detection-as-code in Falco. Lives in git, deployed via configuration management, tested by spawning a shell in the Vault container during a maintenance window and verifying the alert fires.

The full mature stack on cd-alpha:
1. Falco eBPF probe + custom rules per service
2. Falco Sidekick routes alerts to Datadog and Telegram
3. Datadog dashboard groups alerts by container, shows incident clusters
4. SOAR playbook on n8n: any 3+ critical Falco alerts in same container within 60s = auto-isolate container, page Telegram, snapshot for forensics
5. Detection-as-code repo for Falco custom rules with pytest fixtures simulating attacker behavior

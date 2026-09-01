# Sigma Detection Rules

Sigma 2.0 ruleset for the platform. Each rule maps to one or more existing Falco detections that ship with the runtime image overlay, and a subset of new Squire specific rules cover AI security telemetry that the host based Falco engine cannot see.

## Layout

```
detections/sigma/
  infra/         Infrastructure rules. Source category: process_creation, file_event, network_connection.
  squire/        AI security rules. Source product: squire (Langfuse + Squire FastAPI traces).
  cloudflare/    Edge perimeter rules. Source product: cloudflare (firewall, access, audit).
```

## Conversion

Convert Sigma to vendor query languages with `sigma-cli`:

```
pip install sigma-cli pysigma-backend-splunk pysigma-backend-elasticsearch pysigma-backend-loki
sigma convert -t splunk detections/sigma/infra/
sigma convert -t lucene detections/sigma/infra/
sigma convert -t loki detections/sigma/squire/
```

## Mapping

| Sigma rule file | Falco rule | MITRE ATT&CK | Severity |
|---|---|---|---|
| infra/container-shell-spawn-restricted.yml | CD PostgreSQL Shell Access, CD Vault Shell Access, CD Tunnel Shell Access, CD Keycloak Shell Access, CD Falco Shell Access, CD OpenClaw Shell Access | T1059 | high |
| infra/vault-unseal-key-access.yml | CD Vault Unseal Key Access | T1552.001 | critical |
| infra/sensitive-file-read.yml | CD Sensitive File Read Any Container, CD n8n Sensitive File Read | T1003.008 | high |
| infra/n8n-unexpected-binary.yml | CD n8n Unexpected Binary | T1059.004, T1105 | medium |
| infra/postgres-outbound-public.yml | CD PostgreSQL Unexpected Outbound | T1041 | medium |
| infra/privilege-escalation-attempt.yml | CD Privilege Escalation Attempt | T1068 | high |
| infra/etc-directory-modification.yml | CD Etc Directory Modification | T1565 | high |
| squire/ai-prompt-injection-rail-block.yml | (new, source: NeMo rail logs) | ATLAS AML.T0051 | high |
| squire/ai-pii-pre-graph-block.yml | (new, source: Squire app logs) | ATLAS AML.T0041 | high |
| squire/ai-cost-ceiling-breach.yml | (new, source: Squire cost middleware) | ATLAS AML.T0029 | medium |
| squire/ai-injection-volume-anomaly.yml | (new, source: Langfuse aggregate) | ATLAS AML.T0024 | medium |
| cloudflare/access-brute-force.yml | (new, source: Cloudflare Access logs) | T1110.003 | high |
| cloudflare/honeytoken-path-hit.yml | (new, source: Cloudflare firewall events) | T1595.003 | high |
| cloudflare/waf-block-burst.yml | (new, source: Cloudflare firewall events) | T1190 | high |
| cloudflare/geo-fence-violation.yml | (new, source: Cloudflare firewall events) | T1078 | high |
| cloudflare/audit-log-change.yml | (new, source: Cloudflare audit logs) | T1098, T1562 | critical |
| cloudflare/scanner-ua-detected.yml | (new, source: Cloudflare firewall events) | T1595.002 | medium |

## Validation

Each rule is validated against the Sigma 2.0 schema:

```
sigma check detections/sigma/
```

## Contributing

When adding a Falco rule, also add a Sigma rule. The Falco engine watches host syscalls in real time. Sigma rules let SIEM analysts pivot on the same logical signal across Falco emitted events, application logs, and network telemetry.

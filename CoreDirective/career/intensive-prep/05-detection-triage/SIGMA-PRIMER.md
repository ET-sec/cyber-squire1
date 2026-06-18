# Sigma Primer

Sigma is the open YAML-based detection format. SigmaHQ maintains the spec at github.com/SigmaHQ/sigma. The point is portability: you write logic once and convert to Splunk SPL, Elastic KQL, Sentinel KQL, Chronicle YARA-L, Panther Python, Wazuh rules, etc. via `sigma-cli`.

Install: `pip install sigma-cli` and the backends you need (`pySigma-backend-splunk`, `pySigma-backend-elasticsearch`, `pySigma-backend-microsoft365`).

Convert: `sigma convert -t splunk -p sysmon rule.yml`

---

## The Mandatory Fields

```yaml
title: short human title
id: a UUID, unique across all Sigma rules
status: experimental | test | stable | deprecated | unsupported
description: 1 to 3 sentences explaining intent
references:
  - url to blog or report
author: name or handle
date: YYYY/MM/DD
modified: YYYY/MM/DD
tags:
  - attack.initial_access
  - attack.t1078.004
logsource:
  product: aws | windows | linux | kubernetes
  service: cloudtrail | sysmon | auth | audit
  category: process_creation | network_connection | file_event
detection:
  selection:
    field: value
  condition: selection
falsepositives:
  - admin scripts
  - vulnerability scanners
level: low | medium | high | critical
```

The detection block is where the logic lives. The condition expresses how the named selection blocks combine.

---

## Modifiers (the Sigma superpower)

Append `|modifier` to a field name:

- `contains`: substring match
- `startswith` / `endswith`
- `re`: regex
- `cased`: case-sensitive (default is case-insensitive)
- `base64` / `base64offset`: match the base64 form, including chunked offsets
- `windash`: matches both `-flag` and `/flag` and `--flag`
- `lt`, `lte`, `gt`, `gte`: numeric
- `all`: the field must contain all values in the list (default is any)

Example:
```yaml
CommandLine|contains|all:
  - 'whoami'
  - '/all'
```

---

## 10 Progressively Complex Examples

### 1. Trivial: SSH login failure on Linux

```yaml
title: SSH Authentication Failure
id: 7b4d3f2a-1e0c-4f9a-bd11-9f0aab9d1a01
status: experimental
description: Detects a single SSH authentication failure. Noisy on its own. Use as building block.
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: linux
  service: auth
detection:
  selection:
    Image|endswith: '/sshd'
    Message|contains: 'Failed password'
  condition: selection
falsepositives:
  - users mistyping passwords
  - decommissioned service accounts
level: low
tags:
  - attack.credential_access
  - attack.t1110.001
```

### 2. Threshold: SSH brute force (multiple failures from one IP)

Sigma proper does not do thresholding by itself. The `count()` aggregation is in the older spec and is partially supported by some backends. The modern pattern: write the atomic event detection, then add a correlation rule (Sigma v2 correlations).

```yaml
title: SSH Brute Force from Single Source
id: 8a2c1d3e-4f55-4a1b-9b22-1234567890ab
status: experimental
description: Five or more SSH auth failures from same source IP within 1 minute.
author: Emmanuel Tigoue
date: 2026/05/08
correlation:
  type: event_count
  rules:
    - 7b4d3f2a-1e0c-4f9a-bd11-9f0aab9d1a01
  group-by:
    - SourceIP
  timespan: 1m
  condition:
    gte: 5
level: medium
tags:
  - attack.credential_access
  - attack.t1110.001
```

### 3. AWS CloudTrail: STS GetCallerIdentity from non-corporate IP

```yaml
title: STS GetCallerIdentity from Unexpected IP
id: 9c3d2e4f-5a66-4b2c-8d33-0987654321cd
status: experimental
description: GetCallerIdentity is the first call attackers make after stealing creds. Watch for it from non-corporate networks.
references:
  - https://aws.amazon.com/blogs/security/
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: aws
  service: cloudtrail
detection:
  selection:
    eventSource: 'sts.amazonaws.com'
    eventName: 'GetCallerIdentity'
  filter_corporate:
    sourceIPAddress|startswith:
      - '10.'
      - '172.16.'
      - '192.168.'
  filter_aws_internal:
    sourceIPAddress|endswith: '.amazonaws.com'
  condition: selection and not (filter_corporate or filter_aws_internal)
falsepositives:
  - Cloud Custodian or other tooling running outside the VPC
  - SaaS integrations with AWS
level: medium
tags:
  - attack.discovery
  - attack.t1087.004
```

### 4. Kubernetes: pod exec into a privileged namespace

```yaml
title: Kubernetes Pod Exec into kube-system
id: aabb1122-3344-5566-7788-99aabbccddee
status: test
description: Detects a kubectl exec or attach into kube-system or other privileged namespaces. Indicator of lateral movement post initial access to the cluster.
references:
  - https://kubernetes.io/docs/tasks/debug/debug-application/get-shell-running-container/
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: kubernetes
  service: audit
detection:
  selection:
    verb:
      - 'create'
    objectRef.subresource:
      - 'exec'
      - 'attach'
    objectRef.namespace:
      - 'kube-system'
      - 'kube-public'
      - 'cattle-system'
  filter_serviceaccount:
    user.username|startswith: 'system:serviceaccount:'
  condition: selection and not filter_serviceaccount
falsepositives:
  - cluster admins debugging
  - sanctioned automation, allowlist by user.username
level: high
tags:
  - attack.lateral_movement
  - attack.t1609
```

### 5. Windows: PowerShell with encoded command (base64offset modifier)

```yaml
title: PowerShell Encoded Command
id: bbcc2233-4455-6677-8899-aabbccddeeff
status: stable
description: PowerShell launched with -EncodedCommand. Common in fileless malware and red team tooling.
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: windows
  category: process_creation
detection:
  selection_image:
    Image|endswith:
      - '\powershell.exe'
      - '\pwsh.exe'
  selection_args:
    CommandLine|windash|contains:
      - ' -encodedcommand '
      - ' -enc '
      - ' -ec '
  condition: selection_image and selection_args
falsepositives:
  - legitimate admin scripts using -enc to avoid quoting issues
  - SCCM and similar agents
level: high
tags:
  - attack.execution
  - attack.t1059.001
  - attack.defense_evasion
  - attack.t1027
```

### 6. DNS exfil: long subdomain with high entropy (heuristic, computed upstream)

Sigma cannot compute entropy itself. The pattern: a parser or enrichment pipeline (Cribl, Elastic ingest pipeline, Vector, Logstash) computes `subdomain_length` and `subdomain_entropy` and writes them as fields. Sigma then matches on the computed fields.

```yaml
title: DNS Tunneling via Long High-Entropy Subdomain
id: ccdd3344-5566-7788-99aa-bbccddeeff00
status: experimental
description: DNS query with subdomain length over 50 chars and Shannon entropy over 4.0. Suggests data exfil or C2 over DNS.
references:
  - https://www.sans.org/white-papers/34152/
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: zeek
  service: dns
detection:
  selection:
    subdomain_length|gte: 50
    subdomain_entropy|gte: 4.0
  filter_known_cdns:
    query|endswith:
      - '.cloudfront.net'
      - '.akamaiedge.net'
      - '.fastly.net'
      - '.azureedge.net'
  condition: selection and not filter_known_cdns
falsepositives:
  - antivirus and EDR cloud lookups (allowlist by parent domain)
  - some SaaS telemetry (Datadog, Sentry) uses long subdomain identifiers
level: high
tags:
  - attack.exfiltration
  - attack.t1048.003
  - attack.command_and_control
  - attack.t1071.004
```

### 7. Webshell drop on Apache: file write to webroot followed by execution

This is a sequence detection. Use Sigma correlation `temporal` type.

```yaml
title: Webshell File Write to Apache DocumentRoot
id: dd445566-6677-8899-aabb-ccddeeff0011
status: experimental
description: A new .php, .jsp, or .aspx file appears in the webroot.
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: linux
  service: auditd
detection:
  selection:
    syscall: 'open'
    a2: '0x441'
    name|startswith: '/var/www/'
    name|endswith:
      - '.php'
      - '.jsp'
      - '.aspx'
  filter_legit_users:
    auid:
      - '0'
      - '1000'
  condition: selection and not filter_legit_users
falsepositives:
  - CMS auto-updates (WordPress core, plugin updates) — allowlist by parent process
level: high
tags:
  - attack.persistence
  - attack.t1505.003
```

### 8. Living off the land: whoami plus net user plus net group within 60 sec

```yaml
title: Recon Burst (whoami + net user + net group)
id: ee556677-7788-99aa-bbcc-ddeeff001122
status: experimental
description: Three classic recon commands within 60 seconds from same parent process. Hands-on-keyboard activity post-exploit.
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: windows
  category: process_creation
detection:
  selection_whoami:
    Image|endswith: '\whoami.exe'
  selection_net_user:
    Image|endswith: '\net.exe'
    CommandLine|contains: ' user '
  selection_net_group:
    Image|endswith: '\net.exe'
    CommandLine|contains: ' group '
  condition: 1 of selection_*
correlation:
  type: temporal
  rules:
    - selection_whoami
    - selection_net_user
    - selection_net_group
  group-by:
    - ParentProcessId
    - User
  timespan: 60s
level: high
tags:
  - attack.discovery
  - attack.t1033
  - attack.t1087.001
  - attack.t1069.001
```

### 9. LLM gateway: prompt injection in user-supplied content

```yaml
title: LLM Prompt Injection Indicators in Gateway Logs
id: ff667788-8899-aabb-ccdd-eeff00112233
status: experimental
description: User-supplied prompt fields contain known prompt injection patterns. Anchored on the OWASP LLM Top 10 LLM01 indicators.
references:
  - https://owasp.org/www-project-top-10-for-large-language-model-applications/
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: openclaw
  service: gateway
detection:
  selection_ignore:
    prompt|contains:
      - 'ignore previous instructions'
      - 'ignore all prior'
      - 'disregard the system prompt'
  selection_role:
    prompt|contains:
      - 'you are now'
      - 'pretend you are'
      - 'system: '
      - 'developer mode'
  selection_exfil:
    prompt|contains:
      - 'print your instructions'
      - 'reveal your prompt'
      - 'what is your system message'
  condition: 1 of selection_*
falsepositives:
  - red team exercises
  - prompt engineering tutorials being processed legitimately
level: medium
tags:
  - attack.initial_access
  - attack.t1190
```

### 10. Agentic tool abuse: anomalous tool sequence in n8n

```yaml
title: n8n Agent Anomalous Tool Sequence
id: 00778899-99aa-bbcc-ddee-ff0011223344
status: experimental
description: An LLM agent invokes a sensitive write tool (gmail send, github push, drive share) within 30 seconds of a fetch tool that pulled untrusted external content. Anchor for indirect prompt injection.
references:
  - https://embracethered.com/blog/posts/2024/llm-agentic-injection/
author: Emmanuel Tigoue
date: 2026/05/08
logsource:
  product: n8n
  service: execution_log
detection:
  selection_untrusted_fetch:
    node_type:
      - 'n8n-nodes-base.httpRequest'
      - 'n8n-nodes-base.gmailReadTool'
      - 'tavily.search'
    status: 'success'
  selection_sensitive_action:
    node_type:
      - 'n8n-nodes-base.gmail'
      - 'n8n-nodes-base.github'
      - 'n8n-nodes-base.googleDrive'
    operation:
      - 'send'
      - 'createIssue'
      - 'shareFile'
  condition: 1 of selection_*
correlation:
  type: temporal
  rules:
    - selection_untrusted_fetch
    - selection_sensitive_action
  group-by:
    - workflow_id
    - execution_id
  timespan: 30s
level: high
tags:
  - attack.initial_access
  - attack.t1190
  - attack.execution
```

---

## Conversion Cheats

```bash
# Splunk SPL
sigma convert -t splunk -p sysmon rule.yml

# Elastic KQL (Lucene)
sigma convert -t elasticsearch -f lucene rule.yml

# Sentinel KQL (Microsoft 365 Defender)
sigma convert -t microsoft365defender rule.yml

# Panther (Python)
sigma convert -t panther rule.yml

# Test all rules in a directory
sigma check rules/
```

Pipelines (`-p`) inject field name mappings for the source. Without a pipeline, `Image` stays `Image`. With `-p sysmon`, it becomes `process.executable.path` or whatever the pipeline maps it to.

## Common Conversion Gotchas

- Sigma `contains` becomes `*foo*` in Splunk (wildcards). Slow on large indexes. Prefer `tstats` data models in production.
- KQL is case-sensitive by default. The `cased` modifier in Sigma flips the meaning. Read the converted query before deploying.
- Correlation rules are not universally supported. Splunk supports via `tstats`, Sentinel via `bin()`, Elastic via EQL `sequence`. Some backends will refuse to convert.
- `re` modifier syntax differs across backends. Test on real logs before trusting the conversion.

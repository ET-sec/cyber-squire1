# Detection Engineering Cheatsheet

One pager. Print it. Tape it to the wall.

---

## Top 20 Linux Log Paths

| Path | Contents |
|---|---|
| `/var/log/auth.log` | Auth events (Debian/Ubuntu): SSH, sudo, su, login |
| `/var/log/secure` | Auth events (RHEL/CentOS/Rocky) |
| `/var/log/syslog` | General system messages (Debian/Ubuntu) |
| `/var/log/messages` | General system messages (RHEL family) |
| `/var/log/kern.log` | Kernel messages |
| `/var/log/dmesg` | Boot messages |
| `/var/log/audit/audit.log` | auditd subsystem (compliance gold) |
| `/var/log/wtmp` | Login history (binary, read with `last`) |
| `/var/log/btmp` | Failed login history (binary, read with `lastb`) |
| `/var/log/utmp` | Currently logged in users (binary, read with `who`) |
| `/var/log/cron` or `/var/log/cron.log` | Cron job execution |
| `/var/log/apache2/access.log` | Apache HTTP access |
| `/var/log/apache2/error.log` | Apache HTTP errors |
| `/var/log/nginx/access.log` | Nginx HTTP access |
| `/var/log/nginx/error.log` | Nginx HTTP errors |
| `/var/log/mysql/error.log` | MySQL errors |
| `/var/log/postgresql/postgresql-*.log` | Postgres logs |
| `/var/log/journal/*` | Persistent journald (binary, read with `journalctl`) |
| `/var/log/docker.log` or `journalctl -u docker` | Docker daemon |
| `/var/log/falco/falco.log` | Falco runtime alerts |

`journalctl -u <service> -o json --since "1 hour ago"` for structured queries on systemd services.

---

## Top CloudTrail Event Names Worth Knowing

| Event | What it signals |
|---|---|
| `ConsoleLogin` | Console auth, watch for failures and unusual geo |
| `GetCallerIdentity` | First call after stolen creds |
| `AssumeRole` | Role chaining, watch source IP transitions |
| `GetSessionToken` | STS token mint, watch lifetime and use |
| `CreateAccessKey` | New long-lived creds, often persistence |
| `DeactivateMFADevice` | MFA tampering |
| `DeleteTrail` / `StopLogging` | Anti-forensics |
| `PutBucketPolicy` / `PutBucketAcl` | S3 exposure changes |
| `ListBuckets` / `GetObject` (data event) | Capital One pattern |
| `RunInstances` | New compute, watch for crypto miners |
| `AuthorizeSecurityGroupIngress` | Network exposure |
| `CreateUser` / `AttachUserPolicy` | Persistence via new IAM principals |
| `PutObject` to public bucket | Data placement for exfil staging |
| `UpdateAssumeRolePolicy` | Trust policy tampering |
| `CreateFunction` (Lambda) | Persistence and execution |
| `ModifyDBInstance` | RDS tampering |
| `GenerateDataKey` (KMS) | Crypto key use, normal but watch volume |
| `GetParameter` (SSM) | Secrets retrieval, watch principals |
| `PutKeyPolicy` (KMS) | Key access control changes |
| `Decrypt` (KMS, data event) | Volume spikes signal exfil |

Always pair with `userIdentity.type`, `sourceIPAddress`, `userAgent`, `errorCode`. The errorCode field is gold: `AccessDenied` bursts mean someone is fishing.

---

## MITRE ATT&CK Top 20 Techniques to Memorize

| ID | Name | Tactic |
|---|---|---|
| T1078 | Valid Accounts | Initial Access / Persistence |
| T1078.004 | Cloud Accounts | Initial Access |
| T1190 | Exploit Public-Facing Application | Initial Access |
| T1566 | Phishing | Initial Access |
| T1059.001 | PowerShell | Execution |
| T1059.003 | Windows Command Shell | Execution |
| T1059.004 | Unix Shell | Execution |
| T1027 | Obfuscated Files or Information | Defense Evasion |
| T1110 | Brute Force | Credential Access |
| T1110.003 | Password Spraying | Credential Access |
| T1003 | OS Credential Dumping | Credential Access |
| T1552 | Unsecured Credentials | Credential Access |
| T1087 | Account Discovery | Discovery |
| T1033 | System Owner/User Discovery | Discovery |
| T1018 | Remote System Discovery | Discovery |
| T1021 | Remote Services | Lateral Movement |
| T1071 | Application Layer Protocol | C2 |
| T1071.004 | DNS | C2 |
| T1041 | Exfiltration Over C2 Channel | Exfiltration |
| T1486 | Data Encrypted for Impact | Impact (ransomware) |

ATT&CK Cloud-specific add-ons: T1078.004 (Cloud Accounts), T1098.001 (Additional Cloud Credentials), T1530 (Data from Cloud Storage), T1538 (Cloud Service Dashboard), T1580 (Cloud Infrastructure Discovery).

---

## jq One-Liners for Triage

```bash
# Top source IPs in CloudTrail
jq -r '.Records[].sourceIPAddress' trail.json | sort | uniq -c | sort -rn | head

# All events for a specific user
jq '.Records[] | select(.userIdentity.arn | contains("alice"))' trail.json

# Failed events only
jq '.Records[] | select(.errorCode != null)' trail.json

# Events from non-corporate IPs (everything except 10.0.0.0/8)
jq '.Records[] | select(.sourceIPAddress | startswith("10.") | not)' trail.json

# Group by event name and count
jq -r '.Records[].eventName' trail.json | sort | uniq -c | sort -rn

# Time window filter (last hour)
jq --arg cutoff "$(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ)" \
  '.Records[] | select(.eventTime > $cutoff)' trail.json

# K8s audit: all exec calls
jq 'select(.objectRef.subresource == "exec")' audit.log

# K8s audit: who created pods in kube-system
jq 'select(.verb == "create" and .objectRef.resource == "pods" and .objectRef.namespace == "kube-system") | .user.username' audit.log

# Falco alerts by rule
jq -r '.rule' falco.log | sort | uniq -c | sort -rn

# Pretty-print specific fields
jq '{time: .eventTime, user: .userIdentity.arn, action: .eventName, ip: .sourceIPAddress}' trail.json
```

---

## Splunk SPL Basics

```spl
# Top failed SSH sources, last 1 hour
index=linux sourcetype=auth "Failed password" 
| stats count by src_ip 
| sort -count

# CloudTrail: GetCallerIdentity from non-corp IPs
index=aws sourcetype=cloudtrail eventName=GetCallerIdentity
| where NOT cidrmatch("10.0.0.0/8", sourceIPAddress)
| table _time, userIdentity.arn, sourceIPAddress, userAgent

# Anomalous user volume (per-user 95th percentile)
index=app sourcetype=audit
| bucket _time span=1h
| stats count by user, _time
| eventstats p95(count) as p95_count by user
| where count > p95_count * 2

# Sequence detection via transaction
index=windows sourcetype=sysmon EventCode=1
| transaction ParentProcessGuid maxspan=60s 
  startswith="whoami.exe" endswith="net.exe user"

# Faster: tstats on accelerated data model
| tstats count from datamodel=Authentication where Authentication.action=failure 
  by Authentication.src_ip _time span=1h
```

Splunk pro tips: prefer `tstats` over `stats` on accelerated data models. Use `cidrmatch` for IP ranges. `eventstats` adds aggregates without losing rows.

---

## KQL Basics (Sentinel, Defender, Azure)

```kql
// Top failed sign-ins, last 1 hour
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType != 0
| summarize count() by IPAddress, UserPrincipalName
| sort by count_ desc

// Anomalous geography
SigninLogs
| where TimeGenerated > ago(7d)
| summarize Locations = make_set(Location) by UserPrincipalName
| where array_length(Locations) > 3

// CloudTrail in Sentinel via AWSCloudTrail table
AWSCloudTrail
| where EventName == "GetCallerIdentity"
| where SourceIpAddress !startswith "10."
| project TimeGenerated, UserIdentityArn, SourceIpAddress, UserAgent

// Sequence detection (PowerShell -enc followed by network)
DeviceProcessEvents
| where ProcessCommandLine has_any ("-enc ", "-encodedcommand ")
| project DeviceId, ProcessId=InitiatingProcessId, T1=TimeGenerated
| join kind=inner (
    DeviceNetworkEvents
    | project DeviceId, T2=TimeGenerated, RemoteIP, RemotePort
  ) on DeviceId
| where T2 between (T1 .. T1 + 5m)

// Bin aggregation for time-series
SigninLogs
| where TimeGenerated > ago(24h)
| summarize count() by bin(TimeGenerated, 5m), UserPrincipalName
```

KQL pro tips: `has` is faster than `contains` (token-based vs substring). `ago(1h)` for relative time. `summarize ... by bin(time, 5m)` for time-series. `extend` adds columns, `project` selects them.

---

## Falco vs auditd vs eBPF: When to Use Which

| Need | Use |
|---|---|
| Container runtime behavior detection (Kubernetes) | Falco (eBPF or kmod driver) |
| Compliance-grade host audit (HIPAA, PCI, FedRAMP) | auditd |
| Custom runtime detection logic that Falco cannot express | Raw eBPF (Tracee, BCC, custom) |
| Network detection at scale | NDR (Suricata, Zeek) or eBPF network probes |
| Universal portable host audit across many distros | auditd |
| Quick start with hundreds of pre-built behavioral rules | Falco |
| Fileless and in-memory detection | EDR (CrowdStrike, SentinelOne) plus eBPF for gaps |

The mental model. eBPF is the kernel mechanism. Falco is one consumer of eBPF, with a high-level rule language. Auditd is a separate kernel mechanism with its own consumer (the auditd daemon). They are not exclusive. Most regulated container hosts run all three.

---

## Vendor Naming Quick Reference

| Capability | Splunk | Elastic | Sentinel | Chronicle | Panther |
|---|---|---|---|---|---|
| Query language | SPL | KQL / EQL | KQL | YARA-L 2.0 | Python rules |
| Data model | Data models | ECS | ASIM | UDM | Native schemas |
| Detection content | ESCU | Detection Rules repo | Analytics rules | Curated rule packs | Native rules |
| Correlation | `transaction`, `tstats` | EQL `sequence` | `bin` + joins | YARA-L windows | Python state |
| Pricing model | Ingest GB/day | Ingest GB/day | Ingest GB/day | Flat per user/asset | Flat per user |

ECS is Elastic Common Schema. UDM is Google's Unified Data Model. ASIM is Microsoft's Advanced Security Information Model. All are attempts at field name normalization. None are universal.

---

## The 30-Second Triage Decision

When an alert fires, this is the order in your head:

1. Rule precision history (if I trust this rule, take it seriously)
2. Asset criticality (crown jewel, prod, dev)
3. Identity (real human, service account, external)
4. Geographic and time context
5. Concurrent alerts (correlation increases confidence)

If 3 out of 5 are red, escalate. If 0 of 5 are red, suppress. If 1 to 2, dig deeper for 5 minutes.

That is the senior shortcut. Memorize it.

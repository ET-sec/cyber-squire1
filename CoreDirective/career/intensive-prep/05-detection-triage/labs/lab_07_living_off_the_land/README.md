# Lab 07: Living Off the Land

## Attack Narrative

Continuation of lab_04. Same workstation `FIN-WKS-042`, same user `jmiller`. After the macro-launched PowerShell beacon got a foothold, the attacker uses Windows-native binaries for recon, persistence, and lateral movement. No malware to detect. Just ordinary admin tools used in unordinary sequences.

The chain in the log:

1. whoami /all (T1033)
2. net user /domain (T1087.002)
3. net group "Domain Admins" /domain (T1069.002)
4. nltest /dclist (T1018, find domain controllers)
5. quser (T1087.001, see other logged-in users)
6. rundll32 evil.dll,DllMain (T1218.011, execution via signed binary)
7. schtasks /create (T1053.005, persistence)
8. reg query (T1012, registry recon)
9. bitsadmin transfer (T1197, ingress tool transfer via signed Windows utility)
10. wmic /node:DC-01 process call create (T1047, remote execution against DC)

Every binary in this chain is signed by Microsoft. Every binary has legitimate uses. The signal is the sequence, the parent (powershell.exe), and the velocity (10 distinct LOLBins in 6 minutes).

## Detection Logic

Three layers of rule.

1. Single LOLBin with high-risk arguments. `bitsadmin /transfer http://`. `schtasks /create /ru SYSTEM`. `wmic /node:`. Each is its own focused rule.
2. Burst correlation. 3+ distinct recon LOLBins within 60s from same parent.
3. Sequence correlation. Recon then persistence then lateral movement. Hard to write, high precision when it fires.

LOLBAS Project (lolbas-project.github.io) maintains the canonical list. ATT&CK Sub-techniques map to most.

## Run It

```bash
cd labs/lab_07_living_off_the_land

# Show the recon burst grouped by parent
jq -c 'select(.image | test("(whoami|net|nltest|quser|systeminfo|hostname)\\.exe$"))' process.log

# Show the LOLBin abuse with high-risk args
jq 'select((.cmdline | contains("/transfer http://")) or (.cmdline | contains("/create")) or (.cmdline | contains("/node:")))' process.log

# Map each to ATT&CK
jq -r '"\(.ts) \(.image | sub(".*\\\\";"")) :: \(.cmdline)"' process.log
```

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Isolate FIN-WKS-042. Force jmiller cred rotation. Pull the schtask: it is the persistence. Disable and remove. Pull the rundll32 child: evil.dll is the second-stage payload, image and analyze. The wmic /node:DC-01 command is the lateral move attempt: review DC-01 logs for incoming WMI from this host within the window. If lateral move succeeded, the DC is also in scope. Hunt for similar parent-of-multiple-LOLBins patterns across the fleet for the last 30 days. Prioritize hosts with recent macro-launched PowerShell.

## Interviewer Questions

- "What is LOLBAS?" Living Off The Land Binaries And Scripts. Project at lolbas-project.github.io tracks signed Microsoft binaries that can be abused for execution, defense evasion, persistence. Examples: rundll32, regsvr32, certutil, mshta, bitsadmin, msiexec.
- "Why is detection on these so hard?" The binaries are signed and used legitimately every day. You cannot block them. Signature-based detection cannot help. You need behavioral: who is running what, with what arguments, in what sequence, under what parent.
- "What is the value of the parent process?" PowerShell launching whoami is suspicious. cmd.exe launching whoami because the user typed it is normal. services.exe launching whoami via a backup agent is normal. The parent gives intent context.
- "What about scripts that run a lot of these legitimately, like login scripts?" Allowlist by Group Policy origin (parent path) or by ParentImage being `gpscript.exe` or `userinit.exe`. The Sigma rule's `falsepositives` block documents this.
- "How does CrowdStrike or Defender detect LOLBin abuse?" Both ship with hundreds of behavioral indicators tracking exactly this pattern. EDRs are the natural home for LOLBin detection because they have the parent chain and command line at scale. SIEM gets it via the EDR alert feed plus its own backstop rules.
- "Living off the land in cloud?" Cloud LOLBin equivalent is using AWS APIs themselves: aws cli, boto3, terraform. Detection moves to CloudTrail and the API call sequence. Same principle, different binaries.

## Variant: Combine With Burst from Lab_04

Lab_04 detects PowerShell with -enc spawned by Office. Lab_07 detects LOLBin recon burst from PowerShell parent. Chain them: a single workstation hitting both rules within 5 minutes is an automatic page-oncall. That is correlation.

Build the chain with a SIEM correlation engine: Sentinel Fusion, Splunk ES correlations, Elastic Detection rule with `risk_score_mapping`. The pair detection has near-zero false positive rate.

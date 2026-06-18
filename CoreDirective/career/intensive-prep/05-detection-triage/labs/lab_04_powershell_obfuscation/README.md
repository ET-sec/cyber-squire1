# Lab 04: PowerShell Obfuscation (Phishing Macro)

## Attack Narrative

J. Miller in Finance opened `Invoice_2026Q2.docm` from their Downloads folder. The macro launched PowerShell with `-nop -w hidden -ep bypass -enc <base64>`. The base64 decodes to a download cradle pointing to `http://45.135.232.8/payload.ps1`.

The cradle ran. Within seconds:
- `whoami /all` (T1033)
- `net user /domain` (T1087.002)
- `net group "Domain Admins" /domain` (T1069.002)

This is the textbook initial-access-to-recon chain. The encoded command is the entry signal. The recon burst is the secondary signal.

## Detection Logic

Two layers.

Layer 1: PowerShell with `-enc` or `-encodedcommand` whose parent is an Office app. Critical severity, page immediately.

Layer 2: PowerShell child spawning whoami + net.exe within 60 seconds. This is the recon burst rule from Sigma example 8 in the primer.

Either layer alone is signal. Both layers from the same workstation is incident.

## Run It

```bash
cd labs/lab_04_powershell_obfuscation
python3 decode.py sysmon.json
```

Decoded output reveals the download cradle.

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Isolate `FIN-WKS-042` from the network via EDR (CrowdStrike network containment, Defender isolation, etc.). Force credential rotation for `EXAMPLE\jmiller` plus any cached creds on the host. Investigate lateral movement: did the PowerShell child make outbound connections, did it pull additional payloads, did jmiller's session reach domain controllers. Pull the `.docm` from Downloads for malware analysis. Block 45.135.232.8 at egress. Hunt for the same hash across the fleet and the same C2 IP across NetFlow.

## Interviewer Questions

- "Why is `-enc` an indicator?" Legitimate admin scripts rarely use `-enc`. The flag exists to handle quoting/escaping in scheduled tasks but most legit automation uses signed `.ps1` files. `-enc` plus base64 plus an Office parent is high signal.
- "What about `-w hidden` and `-nop`?" Window hidden plus no-profile is a defensive evasion combo. Either alone is mild. Together with `-enc` and `-ep bypass` is unmistakable.
- "How do you decode encoded commands at scale?" The base64 is UTF-16LE encoded PowerShell. A simple `base64 -d | iconv -f UTF-16LE` works in a shell. Better: a SIEM detection that fires on the regex AND a downstream enrichment pipeline that decodes and re-runs detection on the decoded content (looking for IEX, DownloadString, Invoke-WebRequest patterns).
- "What about PowerShell logging?" Module logging (4103), script block logging (4104), transcription (4106). Script block logging at level Verbose captures the deobfuscated content even when launched with `-enc`. Critical for IR.
- "AMSI?" Antimalware Scan Interface. Windows hooks PowerShell content right before execution and submits to registered AV/EDR. AMSI bypass attempts are themselves a detection: look for `AmsiUtils`, `AmsiInitFailed`, reflective patches.
- "How does this map to ATT&CK?" T1566.001 (Phishing: Spearphishing Attachment), T1059.001 (PowerShell), T1027 (Obfuscated Files), T1140 (Deobfuscate). After the initial chain: T1033, T1087.002, T1069.002 for the recon.

## Variant: Hardening

1. Group Policy: disable Office macros from internet for all users.
2. Microsoft Defender Attack Surface Reduction rules: "Block Office applications from creating child processes" (single rule kills this whole chain).
3. AppLocker or WDAC to constrain PowerShell to constrained language mode for non-admins.
4. Conditional Access requiring MFA on any privileged action even from authenticated sessions.

The detection is the floor. The hardening is the ceiling. Senior engineers ship both.

# Lab 05: DNS Exfil

## Attack Narrative

Host `10.0.10.55` is exfiltrating data via DNS TXT queries to `*.exfil.attacker-c2.xyz`. Each query carries 48 to 49 hex characters of base32 or hex-encoded payload in the leftmost label. Burst rate is roughly one query every 2.5 seconds.

Egress firewall allows DNS to the corporate resolver. Resolver forwards to public DNS. Attacker controls the authoritative server for `attacker-c2.xyz`. Each query reaches them with a chunk of the stolen data.

DNS over port 53 is the universal allowed protocol. Almost every network permits it. That is why DNS C2 and exfil persists.

## Detection Logic

Statistical, not signature-based. Two features per query, one threshold per feature, one burst correlation.

- subdomain length >= 40 chars
- Shannon entropy >= 4.0 (random-looking)
- 5+ queries from same src to same parent domain within 60 seconds

Filter out known-good high-entropy parents (CloudFront subdomains, S3 endpoints, Akamai). Production refinement: maintain an allowlist of parent domains seen in baseline.

## Run It

```bash
cd labs/lab_05_dns_exfil
python3 detect.py dns.log
```

Expected: 8 candidate events for `attacker-c2.xyz`, one burst alert.

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Block `attacker-c2.xyz` and any related domains at the resolver and egress. Isolate `10.0.10.55`. Pull packet captures for the host. Determine what data was exfiltrated by analyzing the encoded payload (decode the base32/hex, see what came out). Investigate initial access on this host. Hunt for the same parent domain across all DNS logs over the last 90 days. Roll the detection up to alert at 3 queries instead of 5 if attacker rate-limits.

## Interviewer Questions

- "What is the Shannon entropy of `www`?" Roughly 1.6. The Shannon entropy of random hex is ~4.0. The threshold separates encoded payloads from human-readable subdomains.
- "What about Domain Generation Algorithms?" DGAs produce gibberish second-level domains, not long subdomains. The detection is similar (entropy on the SLD instead of the subdomain) but the logsource and the threshold differ. Often flagged together but they are distinct techniques.
- "What about CDNs that legitimately use long entropy subdomains?" Allowlist their parent domains. CloudFront, Fastly, S3, Azure Edge are the big ones. Refresh the allowlist quarterly because new CDNs and new subdomain patterns emerge.
- "Why does this still work in 2026?" DNS is universally permitted. Even orgs with sophisticated egress filtering allow DNS. The fix is requiring DNS over the corporate resolver only (block direct port 53 to internet) plus enabling resolver query logging plus running the detection on those logs.
- "How does Cisco Umbrella or Cloudflare Gateway help?" Both maintain reputational blocklists for known C2 and DGA domains. Umbrella in particular has a "Newly Seen Domains" category that catches first-time-seen domains for blocking. Useful but not a replacement for behavioral detection.
- "How does this map to ATT&CK?" T1048.003 (Exfiltration Over Alternative Protocol: Exfiltration Over Unencrypted Non-C2 Protocol) for the data motion. T1071.004 (Application Layer Protocol: DNS) for the C2 channel.

## Variant: Production Tuning

1. Compute the entropy and length at ingest, not at query time. Saves CPU, makes the rule a simple field comparison.
2. Use Zeek dns.log as source if available. Field names differ slightly (query, qtype, answer) but semantics are the same.
3. Enrich with NX/SERVFAIL response counts. Exfil tools often see high NX rates if the C2 server is offline.
4. Pair with NetFlow: same source IP making outbound DNS to a public resolver instead of corporate DNS is itself a signal.

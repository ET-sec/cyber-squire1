# STIX 2.1 Bundle: Squire Threats

Canonical export of the Squire threat surface in STIX 2.1 format. Consumes from SQUIRE_THREAT_MODEL, AI_THREAT_CATALOG, REDTEAM_RESULTS.

Generated: 2026-04-24T00:00:00+00:00
Bundle file: `squire-threats.stix.json`
Object count: 107

## Object inventory

- Identity: 2 (Organization, svc-squire system)
- AttackPattern (ATLAS tactics): 5
- AttackPattern (OWASP LLM ATC entries): 10
- CourseOfAction (Squire controls): 9
- Vulnerability (residual risks): 6
- Indicator (red team cases): 20
- Note (findings): 7
- Report: 1

## ATLAS coverage

| ATLAS ID | Name | OWASP LLM | Residual |
|----------|------|-----------|----------|
| AML.T0051 | LLM Prompt Injection | LLM01 Prompt Injection | MEDIUM |
| AML.T0024 | Model Stealing | n/a | LOW |
| AML.T0029 | Model Denial of Service | LLM10 Unbounded Consumption | LOW |
| AML.T0041 | Exfiltration via Inference API | LLM06 Sensitive Information Disclosure | MEDIUM |
| AML.T0010 | ML Supply Chain Compromise | LLM03 Supply Chain Vulnerabilities | MEDIUM |

## OWASP LLM 2025 coverage

| ATC ID | Name | OWASP LLM | Residual |
|--------|------|-----------|----------|
| ATC-01 | Prompt Injection (Direct) | LLM01 | Medium |
| ATC-02 | Prompt Injection (Indirect) | LLM01 | Medium |
| ATC-03 | Insecure Output Handling | LLM02 | Medium |
| ATC-04 | Model Supply Chain Compromise | LLM03 | Medium |
| ATC-05 | Sensitive Information Disclosure | LLM06 | Medium |
| ATC-06 | Insecure Skill or Plugin Execution | LLM07 | Low |
| ATC-07 | Excessive Autonomous Agency | LLM08 | Medium |
| ATC-08 | Overreliance on AI Outputs | LLM09 | Medium |
| ATC-09 | Unbounded Resource Consumption | LLM10 | Low |
| ATC-10 | AI Enabled Lateral Movement | n/a | Medium |

## Validation

Bundle constructed via the python `stix2` library, which raises on schema deviation at object construction time. To re validate offline:

```
python -m stix2.equivalence.test docs/grc/stix/squire-threats.stix.json
```

## Source documents

- [SQUIRE_THREAT_MODEL.md](../SQUIRE_THREAT_MODEL.md)
- [AI_THREAT_CATALOG.md](../AI_THREAT_CATALOG.md)
- [REDTEAM_RESULTS.md](../REDTEAM_RESULTS.md)
- [SQUIRE_AI_RISK_ASSESSMENT.md](../SQUIRE_AI_RISK_ASSESSMENT.md)

## Regeneration

```
python scripts/grc/build_stix_bundle.py
```

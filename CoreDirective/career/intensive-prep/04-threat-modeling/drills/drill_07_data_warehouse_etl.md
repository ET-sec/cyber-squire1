# Drill 07: Data Warehouse ETL (S3 + Glue + Redshift)

## Prompt
"Threat model an ETL pipeline. Raw events land in S3, AWS Glue jobs transform them, Redshift hosts the warehouse. Analysts query Redshift via BI tools."

## Scope (Phase 1)

Assets:
- Raw event data (clickstream, app events, may include hashed user ids and PII)
- Curated tables in Redshift
- Glue jobs and the code that defines them
- IAM roles for Glue and Redshift
- KMS keys for S3 and Redshift

Actors:
- Application services producing events
- Data engineers (write Glue jobs)
- Analysts (read Redshift)
- BI tool service account
- External attacker
- Compromised supply chain (Python libraries in Glue)

Data classes:
- Raw events (medium-high, may include PII before scrubbing)
- Curated marts (varies)
- PII tables (high)
- Logs (medium)

Assumptions:
- Single AWS account, multi-region not required
- Lake Formation governs table-level access
- BI tools use IAM federation
- Engineers deploy Glue jobs via CI

## DFD

```
                                  AWS ACCOUNT BOUNDARY
[ App Services ] --> ===== S3: raw/ =====
                          | KMS-CMK-A   |
                          ===============
                                |
                                | (event)
                                v
                          ( Glue Job )
                                |     \ uses IAM role glue-etl-role
                                v      \-- KMS-CMK-A decrypt, KMS-CMK-B encrypt
                          ===== S3: curated/ =====
                                | KMS-CMK-B            |
                                =======================
                                |
                                | COPY
                                v
                          ===== Redshift =====
                          |  cluster-prod    |
                          |  KMS-CMK-C       |
                          ====================
                                ^
                                |
- - - - - - - - - - - - - - - -|- - - - - - - - - VPC BOUNDARY
                                |
                          ( BI Tool ) <-- [ Analyst ]
                                ^
                                |
                          ( Lake Formation ) <-- access policy

[ Data Eng ] --git push--> ( CI ) --> deploy Glue script to s3://glue-scripts/
```

Trust boundaries:
1. App service to S3 raw bucket (TB1)
2. S3 raw to Glue job (TB2, KMS key A boundary)
3. Glue to S3 curated (TB3, KMS key B boundary)
4. Glue to Redshift COPY (TB4)
5. Redshift to BI tool (TB5, VPC boundary)
6. CI to Glue script bucket (TB6, supply chain)
7. Lake Formation policy plane (TB7)
8. KMS key boundaries themselves (TB8, TB9, TB10 for keys A, B, C)

## STRIDE matrix

| # | Boundary | STRIDE | Threat | L | I | Risk |
|---|----------|--------|--------|---|---|------|
| 1 | TB1 | S | App service writes to wrong bucket key, attacker reads via misconfigured bucket policy | L | H | M |
| 2 | TB1 | I | Public bucket exposure (the classic S3 mistake) | L | H | M |
| 3 | TB2 | E | glue-etl-role over-permissioned (`s3:*` cluster-wide) | M | H | H |
| 4 | TB2 | T | Poisoned event payload exploits a parsing bug in Glue script | M | M | M |
| 5 | TB3 | I | Glue script writes PII to a curated bucket without redaction | H | H | H |
| 6 | TB4 | E | Redshift COPY from S3 uses long-lived IAM keys instead of role | L | H | M |
| 7 | TB5 | E | Lake Formation policy missing on a sensitive table, all analysts see PII | M | H | H |
| 8 | TB5 | I | Analyst exfiltrates a sensitive table via BI tool extract | M | H | H |
| 9 | TB6 | T | Compromised CI deploys a malicious Glue script that exfiltrates raw bucket | L | H | M |
| 10 | TB6 | T | Python dep in Glue (e.g. malicious package) executes in job context | M | H | H |
| 11 | TB8 | E | KMS key policy too permissive, principals outside the pipeline can decrypt | L | H | M |
| 12 | TB7 | R | No row-level audit of who queried what in Redshift | M | M | M |
| 13 | TB1 | T | Event tampering: app service was compromised and uploaded forged events to skew dashboards | M | M | M |
| 14 | TB3 | I | Curated bucket lifecycle moves data to cheaper tier with weaker access controls | L | M | L |
| 15 | TB5 | D | Redshift query queue exhausted by one analyst's runaway query | M | M | M |
| 16 | TB4 | T | Glue job writes data with unintended schema, downstream tables corrupted | M | M | M |

## Top 10

1. (#5) PII written to curated without redaction
2. (#3) Glue role over-permissioned
3. (#7) Missing Lake Formation policy
4. (#10) Malicious Python dep in Glue
5. (#8) Analyst exfil via BI extract
6. (#9) CI compromise into Glue scripts
7. (#11) KMS key policy too broad
8. (#6) COPY with long-lived keys
9. (#13) Event tampering at source
10. (#2) Public bucket exposure

## Mitigations

| # | Primary | Compensating | Cost |
|---|---------|--------------|------|
| 1 | PII detection in Glue job (Macie, Presidio, or custom) before write to curated; fail job on detection | Macie continuous scan on curated buckets, alert on findings | M |
| 2 | glue-etl-role scoped to specific bucket prefixes per job, conditions on `aws:SourceArn` | IAM Access Analyzer, monthly review | L |
| 3 | Lake Formation tag-based access control mandatory, curated tables default-deny | Quarterly audit of effective permissions | M |
| 4 | Pin Python deps with hashes, internal mirror, dependency scanning in CI | OSV scanner on Glue scripts at PR time | L |
| 5 | BI tool egress logged to Datadog, row-level limits, large extracts gated through DLP | Per-analyst extract quota | M |
| 6 | CI uses OIDC to AWS, no static credentials, deploy role scoped to script bucket | Cosign-signed Glue scripts, verified before run | M |
| 7 | KMS key policies scoped: only specific roles in specific accounts can decrypt, no `Principal: *` | CloudTrail data event on KMS, alert on unexpected principal | L |
| 8 | Redshift uses IAM auth, COPY via role with `aws:RequestedRegion` condition | Rotate any lingering long-lived keys, set creation alerts | L |
| 9 | S3 bucket public access block enforced at account level, no exceptions | Macie public-access alerts, AWS Config rules | L |
| 10 | Source events signed by producing service, Glue verifies signature before transform | Outlier detection on event volume per source | M |

## Residual risk

After mitigations: 0 HIGH, 4 MEDIUM, 12 LOW.

MEDIUMs:
- Event tampering at source: accepted because mitigation is signing plus producer trust; if producer is compromised we have a bigger problem.
- Schema corruption: accepted with schema registry plus testing in pre-prod.
- Redshift query DoS: accepted with WLM (workload management) queues per group.
- Lifecycle to cheaper tier: accepted as long as ACLs follow data, not the storage class.

I would not ship without: PII detection in Glue and Lake Formation tag-based access. Without those, every analyst is a data breach waiting.

## Detections

- PII in curated: Macie continuous scan, alert on any finding above MEDIUM.
- Unauthorized KMS use: CloudTrail KMS Decrypt events from unexpected principals, alert.
- Mass extract: BI tool query log alert on result row count above threshold per query.
- Glue script drift: nightly diff between deployed scripts and signed git refs.
- Long-lived key creation: AWS Config rule, alert on any access key created in pipeline accounts.
- Public bucket: AWS Config compliance check, page on noncompliance.

Closing line:
"In analytics pipelines the threat is rarely external attackers. It is data sprawl. PII flows from raw to curated to BI extracts and at every hop a control can fail. The threat surface widens because the pipeline is built for breadth of access, not narrowness. The compensating control is to put data classifiers at every write step, not just at the source. Residual risk is bounded by how well Lake Formation tags match reality, which is why I would automate that mapping."

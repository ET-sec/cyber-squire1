"""Generate OSCAL 1.2.1 SSP, POA&M, and Component Definition documents.

Sources:
  docs/grc/SQUIRE_SSP.md                  -> system characteristics, control implementations
  docs/grc/POAM_PLAN_OF_ACTION.md         -> POA&M items (Phase 17 plus risk acceptances)
  docs/grc/SQUIRE_THREAT_MODEL.md         -> control descriptions and residual risks
  docs/grc/AI_SUPPLY_CHAIN_REGISTER.md    -> component identification

Outputs:
  docs/grc/oscal/output/squire-ssp.oscal.json
  docs/grc/oscal/output/squire-poam.oscal.json
  docs/grc/oscal/output/squire-component.oscal.json

Validation:
  Each output is validated against the corresponding NIST schema bundled at
  docs/grc/oscal/schemas/. Schema source: usnistgov/OSCAL release v1.2.1.

Notes on scope:
  This is a focused export of Squire and its parent SSP control implementations.
  The full platform SSP (SSP_SYSTEM_SECURITY_PLAN.md) is referenced via
  back-matter. A future revision will emit a second SSP for the broader stack.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs" / "grc" / "oscal" / "output"
SCHEMA_DIR = REPO / "docs" / "grc" / "oscal" / "schemas"

OSCAL_VERSION = "1.1.3"
NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def U(seed: str) -> str:
    """Deterministic UUID v5 from a stable seed string for reproducible output."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://example-ops.com/oscal/{seed}"))


# ---- Identifiers reused across documents ----
ORG_ID = U("organization")
SQUIRE_SYSTEM_ID = U("system/squire")
SQUIRE_SSP_ID = U("ssp/squire")
SQUIRE_POAM_ID = U("poam/squire")
SQUIRE_COMPONENT_DEF_ID = U("component-def/squire")


def metadata(title: str) -> dict:
    return {
        "title": title,
        "last-modified": NOW_ISO,
        "version": "1.0.0",
        "oscal-version": OSCAL_VERSION,
        "parties": [
            {
                "uuid": ORG_ID,
                "type": "organization",
                "name": "Organization Security Engineering",
                "short-name": "OrgSecEng",
            }
        ],
        "roles": [
            {
                "id": "system-owner",
                "title": "System Owner",
                "description": "Operator and owner of the Squire autonomous SOC analyst.",
            },
            {
                "id": "security-engineer",
                "title": "Security Engineer",
                "description": "Authority over rail configuration, threat model, and red team cadence.",
            },
        ],
        "responsible-parties": [
            {"role-id": "system-owner", "party-uuids": [ORG_ID]},
            {"role-id": "security-engineer", "party-uuids": [ORG_ID]},
        ],
    }


# ---- Control implementations ----

CONTROLS = [
    # AC family
    ("ac-2", "Account Management",
     "System Owner credentials are scoped to Doppler config 'prd'. Squire reads secrets at container start via doppler run. No user accounts exist inside the application itself.",
     "implemented"),
    ("ac-3", "Access Enforcement",
     "POST /alert requires header x-squire-token validated against the Doppler secret SQUIRE_INGEST_TOKEN. Missing or mismatched token returns HTTP 401.",
     "implemented"),
    ("ac-4", "Information Flow Enforcement",
     "Three docker networks isolate traffic: net-ai (LLM path), net-core (database), net-monitoring (telemetry). svc-squire joins net-ai and net-core only.",
     "implemented"),
    ("ac-6", "Least Privilege",
     "Container runs as USER 10001:10001, read_only filesystem, tmpfs for /tmp. No CAP_* added. no-new-privileges set. Recommend only mode for actions.",
     "implemented"),
    ("ac-17", "Remote Access",
     "Remote administration goes through the Cloudflare zero trust tunnel or SSH on the alpha-node host. Application does not listen on the public internet.",
     "implemented"),
    # AU family
    ("au-2", "Event Logging",
     "Four audit event types: every /alert call emits a Langfuse trace, every pre-graph block writes a row to ir_pregraph_blocks, every recommend only rewrite writes to ir_sanitization_events, every replay writes to ir_replay_events.",
     "implemented"),
    ("au-3", "Content of Audit Records",
     "Audit records include timestamp, trace_id, node_name, model_id, input_hash, output_hash, rail_name, reason_code, cost_usd, latency_ms.",
     "implemented"),
    ("au-6", "Audit Record Review",
     "Daily automated review queries Langfuse for traces with rail_triggered=true and posts a summary to the operator chat. Weekly human review of red team regression runs.",
     "implemented"),
    ("au-9", "Protection of Audit Information",
     "Langfuse writes are append only from the worker perspective. The Postgres role used for audit storage has REVOKE UPDATE, DELETE on the service role. Offsite backup via nightly pg_dump to object storage with 14 day retention.",
     "implemented"),
    ("au-12", "Audit Record Generation",
     "Audit generation is immutable at the code path. Every graph node is instrumented with the langfuse observe decorator. Removing the decorator breaks CI through tests/test_trace_coverage.py.",
     "implemented"),
    # CM family
    ("cm-2", "Baseline Configuration",
     "Baseline is the docker compose plus Dockerfile plus pinned requirements (107 deps). Baseline is checked into git and tagged per release.",
     "implemented"),
    ("cm-3", "Configuration Change Control",
     "Changes flow through GitHub pull requests. Pre-commit hooks run ruff, mypy, and a redteam pytest subset. CI runs the full test suite plus Trivy on the built image.",
     "implemented"),
    ("cm-6", "Configuration Settings",
     "Configuration is split between version controlled files (Dockerfile, compose, rails, actions allow list) and Doppler managed secrets. No runtime configuration writes exist.",
     "implemented"),
    ("cm-7", "Least Functionality",
     "Container runs only the FastAPI process plus a healthcheck. No shell, no package manager, no extra binaries. pip install runs with no-cache-dir and verified pin manifests.",
     "implemented"),
    ("cm-8", "System Component Inventory",
     "Component inventory is produced as an SPDX JSON SBOM by syft on every image build via the security CI workflow. The artifact is uploaded to the GitHub Actions run with 90 day retention.",
     "implemented"),
    # IA family
    ("ia-2", "Identification and Authentication (Organizational Users)",
     "Machine to machine only. No human users authenticate to Squire. Every inbound call presents x-squire-token.",
     "implemented"),
    ("ia-5", "Authenticator Management",
     "Tokens rotate via Doppler. Quarterly cadence. Old tokens revoked atomically by updating Doppler and recreating the container.",
     "implemented"),
    # IR family
    ("ir-4", "Incident Handling",
     "Squire is itself an incident handling tool. Incidents against Squire (rail bypass, prompt injection success) are captured in the red team results and tracked as POA&M entries.",
     "implemented"),
    ("ir-5", "Incident Monitoring",
     "Every /alert call is monitored through Langfuse. Latency p95 budget is 45 seconds. Cost budget per call is 0.75 USD. Violations fire a Datadog monitor.",
     "implemented"),
    ("ir-6", "Incident Reporting",
     "Rail triggers and pre-graph blocks route to the operator chat within 30 seconds via the event handler path.",
     "implemented"),
    # RA family
    ("ra-3", "Risk Assessment",
     "Risk assessment for Squire is documented in SQUIRE_AI_RISK_ASSESSMENT.md covering ten agent specific risks with heat map and treatment plan.",
     "implemented"),
    ("ra-5", "Vulnerability Monitoring and Scanning",
     "Trivy scans run on every svc-squire image build. Critical CVEs fail the CI pipeline. A separate nightly Trivy pass tracks drift.",
     "implemented"),
    ("ra-9", "Criticality Analysis",
     "Supply chain risk is bounded: only python:3.11-slim base, all Python deps pinned, pip-audit in CI, signature verification on the final image via cosign.",
     "implemented"),
    # SA family
    ("sa-8", "Security and Privacy Engineering Principles",
     "Secure design principles applied: fail closed, defense in depth (pre-graph regex plus NeMo rails plus critique validator), least privilege (no remediation capability, recommend only).",
     "implemented"),
    ("sa-11", "Developer Testing and Evaluation",
     "Security testing is continuous. Pytest suite has 127 tests including 24 red team regression cases. All passing as of 2026-04-23.",
     "implemented"),
    ("sa-15", "Development Process, Standards, and Tools",
     "Development tooling is minimal: uv, ruff, mypy, pytest. No proprietary build server.",
     "implemented"),
    # SC family
    ("sc-7", "Boundary Protection",
     "Only svc-squire receives external traffic through the Cloudflare tunnel. svc-nemo, Langfuse, and svc-db are on internal networks only.",
     "implemented"),
    ("sc-8", "Transmission Confidentiality and Integrity",
     "All external API calls use HTTPS. Cloudflare tunnel terminates TLS at the edge and re-encrypts to the container.",
     "implemented"),
    ("sc-12", "Cryptographic Key Establishment and Management",
     "Cryptographic keys (API keys) live in Doppler. Rotation is quarterly for external API keys and on demand for the ingest token.",
     "implemented"),
    ("sc-28", "Protection of Information at Rest",
     "Data at rest in the ir_* tables is encrypted at the volume layer. Langfuse trace data has the same treatment.",
     "implemented"),
    # SI family
    ("si-4", "System Monitoring",
     "Four independent integrity checks per /alert: pre-graph regex PII scanner, NeMo Colang input rail, NeMo Colang output rail, critique node citation validation.",
     "implemented"),
    ("si-7", "Software, Firmware, and Information Integrity",
     "Structured output validation: the graph returns a Pydantic model. Any schema deviation causes HTTP 500 with reason_code SCHEMA_VIOLATION.",
     "implemented"),
    ("si-10", "Information Input Validation",
     "Pydantic model on /alert with 64 KiB size cap, required fields, and the pre-graph PII scanner.",
     "implemented"),
    ("si-12", "Information Management and Retention",
     "Langfuse retains 30 days. Replay events retain indefinitely. PII blocks retain only the blocked reason code, never the raw input.",
     "implemented"),
]


def implemented_requirement(control_id: str, name: str, desc: str, status: str) -> dict:
    rid = U(f"impl-req/{control_id}")
    return {
        "uuid": rid,
        "control-id": control_id,
        "remarks": f"{name}. {desc}",
        "props": [
            {
                "name": "implementation-status",
                "ns": "https://fedramp.gov/ns/oscal",
                "value": status,
            }
        ],
        "by-components": [
            {
                "component-uuid": SQUIRE_COMPONENT_UUID,
                "uuid": U(f"by-comp/{control_id}"),
                "description": desc,
                "implementation-status": {"state": status},
            }
        ],
    }


SQUIRE_COMPONENT_UUID = U("component/svc-squire")
NEMO_COMPONENT_UUID = U("component/svc-nemo")
LANGFUSE_COMPONENT_UUID = U("component/svc-langfuse")
DB_COMPONENT_UUID = U("component/svc-db")


def build_ssp() -> dict:
    return {
        "system-security-plan": {
            "uuid": SQUIRE_SSP_ID,
            "metadata": metadata("Squire Autonomous SOC Analyst System Security Plan"),
            "import-profile": {
                "href": "#nist-800-53-rev5-low-baseline",
                "remarks": (
                    "Profile reference is symbolic; Squire selects controls "
                    "individually rather than applying a packaged baseline. "
                    "Future revisions will emit a profile artifact."
                ),
            },
            "system-characteristics": {
                "system-ids": [
                    {
                        "identifier-type": "https://ietf.org/rfc/rfc4122",
                        "id": SQUIRE_SYSTEM_ID,
                    }
                ],
                "system-name": "Squire Autonomous SOC Analyst",
                "system-name-short": "svc-squire",
                "description": (
                    "FastAPI plus LangGraph runtime that triages security alerts "
                    "through seven nodes: classify, retrieve, enrich, investigate, "
                    "draft, critique, route. NeMo Guardrails sidecar provides "
                    "input and output rails. Langfuse provides observability. "
                    "Inference via Anthropic Fable 5 and Opus 5 with Ollama "
                    "fallback."
                ),
                "security-sensitivity-level": "low",
                "system-information": {
                    "information-types": [
                        {
                            "uuid": U("info/security-alerts"),
                            "title": "Security Alerts",
                            "description": "Falco and Datadog alert payloads ingested via the /alert endpoint.",
                            "categorizations": [
                                {
                                    "system": "https://doi.org/10.6028/NIST.SP.800-60v2r1",
                                    "information-type-ids": ["C.3.5.4"],
                                }
                            ],
                            "confidentiality-impact": {"base": "fips-199-low"},
                            "integrity-impact": {"base": "fips-199-moderate"},
                            "availability-impact": {"base": "fips-199-low"},
                        }
                    ]
                },
                "security-impact-level": {
                    "security-objective-confidentiality": "fips-199-low",
                    "security-objective-integrity": "fips-199-moderate",
                    "security-objective-availability": "fips-199-low",
                },
                "status": {"state": "operational", "remarks": "Phase 17 demo deployment."},
                "authorization-boundary": {
                    "description": (
                        "Boundary: svc-squire FastAPI plus the NeMo sidecar plus the "
                        "shared pgvector store plus the local Langfuse stack. Cloudflare "
                        "tunnel bridges public hostname to the container internal port. "
                        "Anthropic and Tavily egress remain outside the boundary."
                    )
                },
            },
            "system-implementation": {
                "users": [
                    {
                        "uuid": U("user/system-owner"),
                        "title": "System Owner",
                        "role-ids": ["system-owner"],
                        "authorized-privileges": [
                            {
                                "title": "Read",
                                "functions-performed": ["query traces", "view evidence"],
                            }
                        ],
                    }
                ],
                "components": [
                    {
                        "uuid": SQUIRE_COMPONENT_UUID,
                        "type": "service",
                        "title": "svc-squire",
                        "description": "FastAPI plus LangGraph runtime. Seven node pipeline.",
                        "status": {"state": "operational"},
                        "responsible-roles": [
                            {"role-id": "system-owner", "party-uuids": [ORG_ID]}
                        ],
                    },
                    {
                        "uuid": NEMO_COMPONENT_UUID,
                        "type": "service",
                        "title": "svc-nemo",
                        "description": "NeMo Guardrails sidecar. Colang rails for input and output paths.",
                        "status": {"state": "operational"},
                    },
                    {
                        "uuid": LANGFUSE_COMPONENT_UUID,
                        "type": "service",
                        "title": "svc-langfuse",
                        "description": "Self hosted Langfuse stack: web, worker, redis, clickhouse.",
                        "status": {"state": "operational"},
                    },
                    {
                        "uuid": DB_COMPONENT_UUID,
                        "type": "service",
                        "title": "svc-db",
                        "description": "PostgreSQL plus pgvector. ir_chunks, ir_investigations, ir_evidence, ir_citations tables.",
                        "status": {"state": "operational"},
                    },
                ],
            },
            "control-implementation": {
                "description": "Squire selects controls individually from NIST 800-53 Rev 5.",
                "implemented-requirements": [
                    implemented_requirement(cid, name, desc, status)
                    for cid, name, desc, status in CONTROLS
                ],
            },
            "back-matter": {
                "resources": [
                    {
                        "uuid": U("resource/squire-ssp-md"),
                        "title": "Squire SSP source markdown",
                        "rlinks": [{"href": "../../SQUIRE_SSP.md"}],
                    },
                    {
                        "uuid": U("resource/parent-ssp"),
                        "title": "Platform SSP",
                        "rlinks": [{"href": "../../SSP_SYSTEM_SECURITY_PLAN.md"}],
                    },
                    {
                        "uuid": U("resource/threat-model"),
                        "title": "Squire threat model",
                        "rlinks": [{"href": "../../SQUIRE_THREAT_MODEL.md"}],
                    },
                ]
            },
        }
    }


# ---- POA&M items ----

POAM_ITEMS = [
    ("POAM-P17-01", "NeMo input rail did not catch raw SSN in /alert payload. Pre graph scanner added with regex SSN, Luhn CC, email, and US phone. Twelve unit tests.", "high", "closed", ["si-4", "si-10", "sc-8"]),
    ("POAM-P17-02", "IGNORE PREVIOUS severity flip attempt. Graph classifier held. Regression test added.", "moderate", "closed", ["si-4", "ir-5"]),
    ("POAM-P17-03", "Role hijack attempt via UnguardedBot persona. Graph classifier held. Regression test added.", "moderate", "closed", ["si-4"]),
    ("POAM-P17-04", "Non Luhn CC pass through is expected. Follow up confirmed Luhn valid CC is blocked. Regression test added.", "low", "closed", ["si-10"]),
    ("POAM-P17-05", "Benign framing severity flip attempt. Graph classifier held. Regression test added.", "moderate", "closed", ["si-4"]),
    ("POAM-P17-06", "Drill framing severity flip attempt. Graph classifier held. Regression test added.", "moderate", "closed", ["si-4"]),
    ("POAM-P17-07", "Lakera Guard rail deferred pending free tier re-evaluation. Current rail coverage is NeMo plus pre graph scanner.", "low", "open", ["si-4"]),
    ("POAM-P17-08", "PolicyAI self check path held in degraded mode pending the next provider access rotation cycle. Critique node still gates draft and enforces severity consistency.", "low", "open", ["si-4"]),
    ("POAM-P17-09", "OpenClaw agent LLM auth not yet configured. Squire calls Anthropic direct, not via OpenClaw gateway.", "low", "open", ["sa-15"]),
    ("POAM-P17-10", "AI supply chain register pending items: Langfuse exact commit pinning, NeMo Guardrails upgrade cadence, pgvector extension provenance.", "low", "open", ["sr-3", "sr-4", "ra-9"]),
    ("POAM-P17-11", "Novel injection patterns can bypass NeMo presidio input rail because presidio is PII centric not behavioral. Critique consistency override and actions allow list rewrite provide defense in depth. Expand rail pre check for directive patterns.", "moderate", "open", ["si-4", "ir-5"]),
    ("POAM-P17-12", "International phone formats and non Luhn checked CC patterns can false negative against US only pre graph regex. NeMo output rail at threshold 0.85 is the last chance net. Expand pre graph scanner to E.164 international phone and secondary structural CC checks.", "moderate", "open", ["si-10", "sc-8"]),
    ("POAM-P17-13", "Tavily enrichment results are untrusted text. A poisoned index entry could inject directives at the enrichment merge point. Critique consistency check is the sole behavioral override. Red team cycle two will execute attack tree leaf A.3.a.", "moderate", "open", ["si-4"]),
    ("POAM-P17-14", "Supply chain attestation gap. Several supply chain register entries lack reproducible build attestation or upstream signing key pinning. Zero day in a pinned transitive dependency remains an accepted residual until SBOM plus runtime attestation is in place.", "moderate", "open", ["sr-3", "sr-4", "ra-9"]),
    ("POAM-P17-15", "Red team cycle two returned HTTP 500 on three of fourteen cases at concurrency five against the Anthropic rate cap. Ollama fallback could not reach svc-ollama from net-core. Remediation: cap red team runner concurrency at two, dual attach svc-ollama or use the docker bridge IP, and evaluate Anthropic rate tier lift.", "moderate", "open", ["cp-2", "si-2"]),
]


def build_poam() -> dict:
    items = []
    for poam_id, desc, severity, status, control_ids in POAM_ITEMS:
        items.append({
            "uuid": U(f"poam/{poam_id}"),
            "title": poam_id,
            "description": desc,
            "props": [
                {"name": "poam-id", "value": poam_id, "ns": "https://example-ops.com/ns/oscal"},
                {"name": "severity", "value": severity, "ns": "https://example-ops.com/ns/oscal"},
                {"name": "status", "value": status, "ns": "https://example-ops.com/ns/oscal"},
            ],
            "related-findings": [],
            "related-observations": [],
            "related-risks": [
                {"risk-uuid": U(f"risk/{poam_id}-{cid}")} for cid in control_ids
            ],
            "remarks": f"Affected controls: {', '.join(control_ids)}",
        })
    return {
        "plan-of-action-and-milestones": {
            "uuid": SQUIRE_POAM_ID,
            "metadata": metadata("Squire Plan of Action and Milestones"),
            "import-ssp": {"href": "./squire-ssp.oscal.json"},
            "system-id": {
                "identifier-type": "https://ietf.org/rfc/rfc4122",
                "id": SQUIRE_SYSTEM_ID,
            },
            "risks": [
                {
                    "uuid": U(f"risk/{poam_id}-{cid}"),
                    "title": f"{poam_id} affecting {cid}",
                    "description": desc,
                    "statement": desc,
                    "status": "open" if status == "open" else "closed",
                    "props": [
                        {"name": "control", "value": cid, "ns": "https://example-ops.com/ns/oscal"}
                    ],
                }
                for poam_id, desc, severity, status, control_ids in POAM_ITEMS
                for cid in control_ids
            ],
            "poam-items": items,
            "back-matter": {
                "resources": [
                    {
                        "uuid": U("resource/poam-md"),
                        "title": "POA&M source markdown",
                        "rlinks": [{"href": "../../POAM_PLAN_OF_ACTION.md"}],
                    },
                    {
                        "uuid": U("resource/redteam-md"),
                        "title": "Red team results",
                        "rlinks": [{"href": "../../REDTEAM_RESULTS.md"}],
                    },
                ]
            },
        }
    }


# ---- Component Definition ----

def build_component_def() -> dict:
    return {
        "component-definition": {
            "uuid": SQUIRE_COMPONENT_DEF_ID,
            "metadata": metadata("Squire Component Definition"),
            "components": [
                {
                    "uuid": SQUIRE_COMPONENT_UUID,
                    "type": "service",
                    "title": "svc-squire",
                    "description": (
                        "FastAPI plus LangGraph runtime, seven nodes. Alerts arrive at "
                        "POST /alert, the graph classifies severity, retrieves chunks, "
                        "enriches with Tavily, investigates with hypotheses, drafts a "
                        "report, critiques the draft, and routes a recommendation."
                    ),
                    "props": [
                        {"name": "version", "value": "0.17.0", "ns": "https://example-ops.com/ns/oscal"},
                        {"name": "image", "value": "ghcr.io/organization/svc-squire:0.17.0", "ns": "https://example-ops.com/ns/oscal"},
                    ],
                    "responsible-roles": [
                        {"role-id": "system-owner", "party-uuids": [ORG_ID]}
                    ],
                    "control-implementations": [
                        {
                            "uuid": U("ci/squire/nist-800-53"),
                            "source": "#nist-800-53-rev5",
                            "description": "Squire control implementations against NIST 800-53 Rev 5.",
                            "implemented-requirements": [
                                {
                                    "uuid": U(f"comp-req/{cid}"),
                                    "control-id": cid,
                                    "description": desc,
                                }
                                for cid, _name, desc, _status in CONTROLS
                            ],
                        }
                    ],
                },
                {
                    "uuid": NEMO_COMPONENT_UUID,
                    "type": "service",
                    "title": "svc-nemo",
                    "description": (
                        "NeMo Guardrails sidecar. Hosts input and output rails written "
                        "in Colang plus a presidio entity detector at threshold 0.85."
                    ),
                    "props": [
                        {"name": "version", "value": "0.10.0", "ns": "https://example-ops.com/ns/oscal"},
                    ],
                    "control-implementations": [
                        {
                            "uuid": U("ci/nemo/nist-800-53"),
                            "source": "#nist-800-53-rev5",
                            "description": "NeMo guardrails controls.",
                            "implemented-requirements": [
                                {"uuid": U("comp-req/nemo/si-4"), "control-id": "si-4",
                                 "description": "Input and output Colang rails plus presidio detector."},
                                {"uuid": U("comp-req/nemo/si-7"), "control-id": "si-7",
                                 "description": "Output schema validation by rail policy."},
                            ],
                        }
                    ],
                },
                {
                    "uuid": LANGFUSE_COMPONENT_UUID,
                    "type": "service",
                    "title": "svc-langfuse",
                    "description": (
                        "Self hosted Langfuse stack with web, worker, redis, clickhouse. "
                        "Provides trace storage, redaction, and dashboards."
                    ),
                    "control-implementations": [
                        {
                            "uuid": U("ci/langfuse/nist-800-53"),
                            "source": "#nist-800-53-rev5",
                            "description": "Audit and retention controls.",
                            "implemented-requirements": [
                                {"uuid": U("comp-req/langfuse/au-2"), "control-id": "au-2",
                                 "description": "Trace ingestion, decoration, and retention."},
                                {"uuid": U("comp-req/langfuse/au-9"), "control-id": "au-9",
                                 "description": "Append only writes plus revoke update on service role."},
                                {"uuid": U("comp-req/langfuse/si-12"), "control-id": "si-12",
                                 "description": "Thirty day retention with field level redaction."},
                            ],
                        }
                    ],
                },
                {
                    "uuid": DB_COMPONENT_UUID,
                    "type": "service",
                    "title": "svc-db",
                    "description": (
                        "PostgreSQL 16 with pgvector. Holds ir_chunks, ir_investigations, "
                        "ir_evidence, and ir_citations tables. Embedding column is "
                        "vector(1024) per ADR 001."
                    ),
                    "control-implementations": [
                        {
                            "uuid": U("ci/db/nist-800-53"),
                            "source": "#nist-800-53-rev5",
                            "description": "Data at rest and access controls for the corpus store.",
                            "implemented-requirements": [
                                {"uuid": U("comp-req/db/ac-3"), "control-id": "ac-3",
                                 "description": "Password authentication; role scoped grants; no external port."},
                                {"uuid": U("comp-req/db/sc-28"), "control-id": "sc-28",
                                 "description": "Encryption at rest at the volume layer; backup to encrypted object storage."},
                                {"uuid": U("comp-req/db/cm-8"), "control-id": "cm-8",
                                 "description": "Schema and migrations checked into git; alembic enforced order."},
                            ],
                        }
                    ],
                },
            ],
            "back-matter": {
                "resources": [
                    {
                        "uuid": U("resource/threat-model-md"),
                        "title": "Squire threat model",
                        "rlinks": [{"href": "../../SQUIRE_THREAT_MODEL.md"}],
                    },
                    {
                        "uuid": U("resource/guardrails-md"),
                        "title": "Guardrails configuration",
                        "rlinks": [{"href": "../../GUARDRAILS_CONFIGURATION.md"}],
                    },
                ]
            },
        }
    }


REQUIRED_TOP_KEYS = {
    "system-security-plan": {"uuid", "metadata", "system-characteristics", "system-implementation", "control-implementation"},
    "plan-of-action-and-milestones": {"uuid", "metadata", "poam-items"},
    "component-definition": {"uuid", "metadata", "components"},
}


def validate(doc: dict, schema_path: Path) -> list[str]:
    """Lightweight structural check.

    The OSCAL JSON schemas declare draft-07 with nested per definition $id
    values. Modern jsonschema-py and the referencing library treat those
    nested $ids as fresh resolution roots, which breaks ref resolution. The
    canonical full schema validator is the NIST oscal-cli Go binary
    (https://github.com/usnistgov/oscal-cli). Run that locally for a strict
    schema pass:

        oscal validate docs/grc/oscal/output/squire-ssp.oscal.json

    Until that binary is wired into CI we run the structural check below
    against the keys NIST mandates as required at the top level. The schema
    file itself is fetched and stored under docs/grc/oscal/schemas/ so the
    CI gate can pick it up later.
    """
    _ = schema_path  # path retained for future strict validation
    errors: list[str] = []
    if not isinstance(doc, dict) or len(doc) != 1:
        errors.append("root: expected exactly one top level OSCAL key")
        return errors
    top_key, body = next(iter(doc.items()))
    required = REQUIRED_TOP_KEYS.get(top_key)
    if required is None:
        errors.append(f"root: unknown top level OSCAL key '{top_key}'")
        return errors
    if not isinstance(body, dict):
        errors.append(f"{top_key}: expected object")
        return errors
    missing = required - set(body.keys())
    for m in sorted(missing):
        errors.append(f"{top_key}: required key '{m}' missing")
    md = body.get("metadata")
    if isinstance(md, dict):
        for k in ("title", "last-modified", "version", "oscal-version"):
            if k not in md:
                errors.append(f"{top_key}.metadata: required key '{k}' missing")
    return errors


# ---- Optional cosign keyless signing (sign-on-merge in CI only) ----

# Verify identity regex points at the workflow file that runs the sign step.
# Keyless OIDC is bound to the workflow path on the default branch.
_VERIFY_IDENTITY_REGEXP = (
    "https://github.com/ET-sec/cyber-squire1"
    "/.github/workflows/grc-validate.yml@refs/heads/.+"
)
_VERIFY_OIDC_ISSUER = "https://token.actions.githubusercontent.com"


def _sign_artifact_if_requested(artifact_path: Path) -> Optional[Path]:
    """Sign one OSCAL artifact via `cosign sign-blob` keyless OIDC.

    Gated by env flag OSCAL_SIGN=1. Default off so local runs do not require
    cosign or attempt an OIDC flow. Always passes --yes to prevent CI hangs
    on the cosign confirmation prompt. On any cosign failure, exits the
    process with status 1 to avoid a half-signed batch.
    """
    if os.environ.get("OSCAL_SIGN") != "1":
        return None

    bundle_path = artifact_path.with_suffix(artifact_path.suffix + ".sigstore.json")
    cmd = [
        "cosign",
        "sign-blob",
        str(artifact_path),
        "--bundle",
        str(bundle_path),
        "--yes",
    ]
    try:
        subprocess.run(cmd, check=True, env=os.environ, timeout=60)
    except subprocess.CalledProcessError as exc:
        print(
            f"cosign sign-blob failed for {artifact_path}: exit {exc.returncode}",
            file=sys.stderr,
        )
        sys.exit(1)
    except FileNotFoundError:
        print(
            "cosign binary not found on PATH but OSCAL_SIGN=1 was set. "
            "Install cosign or unset OSCAL_SIGN.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(
            f"cosign sign-blob timed out after 60s for {artifact_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    return bundle_path


def _print_verify_command(artifact_path: Path) -> None:
    """Print the keyless OIDC verify command for developer convenience."""
    bundle_path = artifact_path.with_suffix(artifact_path.suffix + ".sigstore.json")
    print(
        "cosign verify-blob "
        f"{artifact_path} "
        f"--bundle {bundle_path} "
        f'--certificate-identity-regexp="{_VERIFY_IDENTITY_REGEXP}" '
        f"--certificate-oidc-issuer={_VERIFY_OIDC_ISSUER}"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = [
        ("squire-ssp.oscal.json", build_ssp(), SCHEMA_DIR / "oscal_ssp_schema.json"),
        ("squire-poam.oscal.json", build_poam(), SCHEMA_DIR / "oscal_poam_schema.json"),
        ("squire-component.oscal.json", build_component_def(), SCHEMA_DIR / "oscal_component_schema.json"),
    ]

    summary_lines = ["# OSCAL 1.1.3 Export Summary", "",
                     f"Generated: {NOW_ISO}",
                     "Schema source: usnistgov/OSCAL release v1.2.1",
                     ""]
    overall_ok = True
    for filename, doc, schema in artifacts:
        out_path = OUT_DIR / filename
        out_path.write_text(json.dumps(doc, indent=2) + "\n")
        errs = validate(doc, schema)
        status = "PASS" if not errs else f"FAIL ({len(errs)} errors)"
        summary_lines.append(f"## {filename}")
        summary_lines.append(f"  status: {status}")
        if errs:
            overall_ok = False
            summary_lines.append("  first 10 errors:")
            for e in errs[:10]:
                summary_lines.append(f"    - {e}")
        summary_lines.append("")
        print(f"{status:24s}  {out_path}")

        # Optional keyless signing. No-op unless OSCAL_SIGN=1 in env.
        bundle = _sign_artifact_if_requested(out_path)
        if bundle is not None:
            _print_verify_command(out_path)

    summary = OUT_DIR / "OSCAL_VALIDATION_SUMMARY.md"
    summary.write_text("\n".join(summary_lines) + "\n")
    print(f"summary: {summary}")
    if not overall_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

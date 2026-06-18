"""Configuration constants for CoreDirective proposal generation."""

import os
from pathlib import Path

import yaml


# ── Consultant Profile ──────────────────────────────────────────────────────

CONSULTANT = {
    "name": "Emmanuel Tigoue",
    "title": "Security & Automation Consultant",
    "email": "emmanueltigoue@gmail.com",
    "phone": "(404) 839-2214",
    "company": "CoreDirective",
    "certifications": [
        "SecurityX (CASP+)",
        "CCNA",
        "AWS Security Specialty",
        "SSCP",
        "Security+",
        "Network+",
        "ISC2 CC",
    ],
    "dod_8140": "IAT Level III / IAM Level III compliant",
}


# ── Pricing Matrix ──────────────────────────────────────────────────────────

PRICING = {
    "security_assessment": {"range": "$2,500 - $7,500", "timeline": "2-4 weeks"},
    "soc2_compliance": {"range": "$5,000 - $15,000", "timeline": "4-8 weeks"},
    "n8n_automation": {"range": "$500 - $5,000/workflow", "timeline": "1-3 weeks"},
    "cloud_security": {"range": "$3,000 - $10,000", "timeline": "2-4 weeks"},
    "vciso_retainer": {"range": "$2,500 - $5,000/month", "timeline": "Ongoing"},
    "hourly": {"range": "$150/hr", "timeline": "As needed"},
}

PRICING_LABELS = {
    "security_assessment": "Security Assessment",
    "soc2_compliance": "SOC2 Compliance Program",
    "n8n_automation": "n8n Workflow Automation",
    "cloud_security": "Cloud Security Hardening",
    "vciso_retainer": "vCISO Retainer",
    "hourly": "Hourly Consulting",
}


# ── Service Type Detection ──────────────────────────────────────────────────

SERVICE_KEYWORDS = {
    "soc2_compliance": [
        "soc2", "soc 2", "type ii", "type 2", "compliance audit",
        "compliance program", "audit preparation",
    ],
    "security_assessment": [
        "security assessment", "pentest", "penetration test",
        "vulnerability", "security audit", "risk assessment",
    ],
    "n8n_automation": [
        "n8n", "automation", "workflow", "automate", "onboarding",
        "integration", "orchestration",
    ],
    "cloud_security": [
        "aws", "cloud security", "cloud hardening", "azure security",
        "gcp security", "cloud assessment", "cloud architecture",
    ],
    "vciso_retainer": [
        "vciso", "ciso", "retainer", "ongoing security", "security program",
        "security leadership",
    ],
    "incident_response": [
        "incident response", "incident plan", "ir plan", "breach",
        "tabletop", "disaster recovery",
    ],
}


# ── Phase Templates ─────────────────────────────────────────────────────────

PHASE_TEMPLATES = {
    "soc2_compliance": [
        {
            "name": "Gap Assessment",
            "description": "Evaluate current security controls against SOC2 Trust Service Criteria.",
            "deliverables": [
                "Gap analysis report",
                "Control mapping matrix",
                "Risk register with severity rankings",
            ],
            "timeline": "1-2 weeks",
        },
        {
            "name": "Control Implementation",
            "description": "Design and deploy missing controls to satisfy SOC2 requirements.",
            "deliverables": [
                "Policy documentation suite",
                "Technical control configurations",
                "Evidence collection procedures",
            ],
            "timeline": "2-4 weeks",
        },
        {
            "name": "Audit Preparation",
            "description": "Prepare evidence packages and conduct readiness review before auditor engagement.",
            "deliverables": [
                "Audit-ready evidence binder",
                "Readiness assessment report",
                "Auditor coordination brief",
            ],
            "timeline": "1-2 weeks",
        },
    ],
    "security_assessment": [
        {
            "name": "Reconnaissance",
            "description": "Map the attack surface. Identify exposed services, endpoints, and data flows.",
            "deliverables": [
                "Attack surface inventory",
                "Network topology diagram",
                "Exposed service catalog",
            ],
            "timeline": "3-5 days",
        },
        {
            "name": "Vulnerability Assessment",
            "description": "Test identified targets for known vulnerabilities and misconfigurations.",
            "deliverables": [
                "Vulnerability scan results",
                "Manual testing findings",
                "Severity-ranked finding list",
            ],
            "timeline": "1-2 weeks",
        },
        {
            "name": "Reporting & Remediation",
            "description": "Deliver findings with actionable fix guidance. Prioritize by business impact.",
            "deliverables": [
                "Executive summary report",
                "Technical findings with remediation steps",
                "30/60/90 day remediation roadmap",
            ],
            "timeline": "3-5 days",
        },
    ],
    "n8n_automation": [
        {
            "name": "Workflow Design",
            "description": "Analyze current manual processes. Design automation architecture and data flows.",
            "deliverables": [
                "Process flow diagrams",
                "Integration requirements document",
                "API endpoint inventory",
            ],
            "timeline": "3-5 days",
        },
        {
            "name": "Build & Integration",
            "description": "Develop n8n workflows with error handling, credential management, and logging.",
            "deliverables": [
                "Production-ready n8n workflows",
                "Webhook configurations",
                "Database schema (if applicable)",
            ],
            "timeline": "1-2 weeks",
        },
        {
            "name": "Testing & Handoff",
            "description": "End-to-end testing, documentation, and knowledge transfer to your team.",
            "deliverables": [
                "Test results and validation report",
                "Runbook with troubleshooting guide",
                "Team training session (recorded)",
            ],
            "timeline": "2-3 days",
        },
    ],
    "cloud_security": [
        {
            "name": "Architecture Review",
            "description": "Audit current cloud infrastructure against security best practices and CIS benchmarks.",
            "deliverables": [
                "Architecture security assessment",
                "CIS benchmark compliance report",
                "IAM policy review",
            ],
            "timeline": "1 week",
        },
        {
            "name": "Hardening",
            "description": "Implement security controls: network segmentation, encryption, access policies, logging.",
            "deliverables": [
                "Security group rule optimization",
                "Encryption-at-rest and in-transit configs",
                "CloudTrail and GuardDuty setup",
            ],
            "timeline": "1-2 weeks",
        },
        {
            "name": "Monitoring Setup",
            "description": "Deploy alerting, dashboards, and automated response for ongoing security posture.",
            "deliverables": [
                "CloudWatch alarm configurations",
                "Security dashboard",
                "Automated incident response playbooks",
            ],
            "timeline": "3-5 days",
        },
    ],
    "incident_response": [
        {
            "name": "Current State Assessment",
            "description": "Evaluate existing incident response capabilities, tools, and team readiness.",
            "deliverables": [
                "IR maturity assessment",
                "Tool and capability gap analysis",
                "Stakeholder interview summary",
            ],
            "timeline": "3-5 days",
        },
        {
            "name": "IR Plan Development",
            "description": "Build a formal incident response plan with roles, escalation paths, and procedures.",
            "deliverables": [
                "Incident Response Plan document",
                "Communication templates",
                "Escalation matrix",
            ],
            "timeline": "1-2 weeks",
        },
        {
            "name": "Tabletop Exercise",
            "description": "Simulate a real incident scenario. Validate the plan and identify weak points.",
            "deliverables": [
                "Tabletop exercise scenario",
                "After-action report",
                "Improvement recommendations",
            ],
            "timeline": "1 day + prep",
        },
    ],
    "generic": [
        {
            "name": "Discovery & Planning",
            "description": "Understand your current state, goals, and constraints. Define project scope.",
            "deliverables": [
                "Discovery findings document",
                "Project scope statement",
                "Success criteria definition",
            ],
            "timeline": "3-5 days",
        },
        {
            "name": "Execution",
            "description": "Deliver the core work with regular check-ins and progress updates.",
            "deliverables": [
                "Weekly progress reports",
                "Working deliverables per milestone",
                "Issue tracking and resolution log",
            ],
            "timeline": "1-3 weeks",
        },
        {
            "name": "Handoff & Documentation",
            "description": "Transfer knowledge, document everything, and ensure your team can maintain the work.",
            "deliverables": [
                "Final deliverables package",
                "Technical documentation",
                "Knowledge transfer session",
            ],
            "timeline": "2-3 days",
        },
    ],
}


# ── Stats ───────────────────────────────────────────────────────────────────

STATS = {
    "security_group_rules": "45+",
    "aws_resources": "30+",
    "docker_services": "8",
    "alert_automation": "90%",
}


# ── Anti-Slop Words ────────────────────────────────────────────────────────

BANNED_WORDS = [
    "leverage", "delve", "comprehensive", "robust", "streamline",
    "cutting-edge", "synergy", "paradigm", "holistic", "best-in-class",
    "game-changer", "disruptive", "innovative", "world-class", "seamless",
    "turnkey",
]


# ── Config File Loading ────────────────────────────────────────────────────

def load_config(config_path: str | None = None) -> dict:
    """Load config.yaml and merge with defaults. Returns merged dict."""
    if config_path is None:
        # Look for config.yaml relative to project root
        candidates = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent.parent / "config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = str(candidate)
                break

    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}

    return {}


def detect_service_type(need: str) -> str:
    """Detect the service type from the client's stated need."""
    need_lower = need.lower()
    for service_type, keywords in SERVICE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in need_lower:
                return service_type
    return "generic"


def get_phases(service_type: str) -> list[dict]:
    """Get phase templates for a given service type."""
    return PHASE_TEMPLATES.get(service_type, PHASE_TEMPLATES["generic"])


def get_pricing_for_service(service_type: str) -> dict:
    """Get pricing info for a service type."""
    # Map incident_response to security_assessment pricing
    if service_type == "incident_response":
        return PRICING["security_assessment"]
    if service_type == "generic":
        return PRICING["hourly"]
    return PRICING.get(service_type, PRICING["hourly"])


def get_relevant_pricing(service_type: str) -> list[tuple[str, dict]]:
    """Get a list of relevant pricing entries for the proposal.

    Returns the primary service pricing plus 2-3 complementary options.
    """
    primary_key = service_type
    if service_type == "incident_response":
        primary_key = "security_assessment"
    if service_type == "generic":
        primary_key = "hourly"

    result = []

    # Primary service first
    if primary_key in PRICING:
        result.append((PRICING_LABELS.get(primary_key, primary_key), PRICING[primary_key]))

    # Add complementary services
    complementary_map = {
        "security_assessment": ["cloud_security", "vciso_retainer", "hourly"],
        "soc2_compliance": ["security_assessment", "vciso_retainer", "hourly"],
        "n8n_automation": ["cloud_security", "hourly"],
        "cloud_security": ["security_assessment", "vciso_retainer", "hourly"],
        "vciso_retainer": ["security_assessment", "cloud_security", "hourly"],
        "hourly": ["security_assessment", "cloud_security", "n8n_automation"],
    }

    extras = complementary_map.get(primary_key, ["hourly"])
    for key in extras:
        if key != primary_key and key in PRICING:
            result.append((PRICING_LABELS.get(key, key), PRICING[key]))

    return result

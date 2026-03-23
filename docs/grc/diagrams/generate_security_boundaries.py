#!/usr/bin/env python3
"""
Security Boundary Diagram - Organization Security Operations Platform
Generates: security_boundaries.png

Trust Zones:
  Zone 1 (Public)    - Internet, Cloudflare Edge
  Zone 2 (DMZ)       - Cloudflare Tunnel (host network)
  Zone 3 (Internal)  - All Docker bridge services
  Zone 4 (Sensitive) - PostgreSQL, Vault, secrets data

Authorization Boundary: Everything on the droplet + Terraform-managed resources
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.digitalocean.compute import Droplet
from diagrams.digitalocean.network import Firewall, Vpc
from diagrams.digitalocean.storage import Space
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.container import Docker
from diagrams.onprem.monitoring import Datadog
from diagrams.onprem.security import Vault
from diagrams.onprem.network import Internet
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users
from diagrams.saas.cdn import Cloudflare
from diagrams.saas.logging import Datadog as DatadogSaaS
from diagrams.saas.automation import N8N

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(OUTPUT_DIR, "security_boundaries")

# Colors for zones
ZONE1_COLOR = "#f85149"   # Red - Public
ZONE2_COLOR = "#f0883e"   # Orange - DMZ
ZONE3_COLOR = "#388bfd"   # Blue - Internal
ZONE4_COLOR = "#00FF41"   # Green - Sensitive
AUTHZ_COLOR = "#a371f7"   # Purple - Authorization Boundary

graph_attr = {
    "fontsize": "16",
    "fontname": "Helvetica",
    "bgcolor": "#0d1117",
    "fontcolor": "#e6edf3",
    "pad": "1.0",
    "dpi": "150",
    "ranksep": "1.2",
    "nodesep": "0.8",
    "splines": "spline",
}

node_attr = {
    "fontsize": "10",
    "fontname": "Helvetica",
    "fontcolor": "#e6edf3",
}

edge_attr = {
    "fontsize": "9",
    "fontname": "Helvetica",
    "fontcolor": "#8b949e",
}

with Diagram(
    "Organization - Security Boundary Model",
    filename=FILENAME,
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    outformat="png",
):
    # ===========================================
    # ZONE 1: PUBLIC (Red border)
    # ===========================================
    with Cluster("ZONE 1 - PUBLIC (Untrusted)", graph_attr={
        "fontsize": "14",
        "fontname": "Helvetica Bold",
        "fontcolor": ZONE1_COLOR,
        "bgcolor": "#1a0000",
        "style": "rounded",
        "color": ZONE1_COLOR,
        "penwidth": "3",
    }):
        users = Users("Users\nOperators")
        inet = Internet("Internet")
        cf = Cloudflare("Cloudflare Edge\nDNS + WAF + DDoS")

    # External Services (outside AuthZ boundary)
    with Cluster("External Services (Outside Authorization Boundary)", graph_attr={
        "fontsize": "12",
        "fontname": "Helvetica Bold",
        "fontcolor": "#8b949e",
        "bgcolor": "#161b22",
        "style": "rounded",
        "color": "#30363d",
        "penwidth": "1.5",
    }):
        dd_saas = DatadogSaaS("Datadog SaaS\nCloud")
        gh_actions = GithubActions("GitHub Actions\nCI/CD")
        ext_secrets = Docker("External\nSecrets Mgr")

    # ===========================================
    # AUTHORIZATION BOUNDARY (Purple dashed)
    # ===========================================
    with Cluster("AUTHORIZATION BOUNDARY - Droplet + Terraform-Managed Resources", graph_attr={
        "fontsize": "14",
        "fontname": "Helvetica Bold",
        "fontcolor": AUTHZ_COLOR,
        "bgcolor": "#0d1117",
        "style": "dashed,rounded",
        "color": AUTHZ_COLOR,
        "penwidth": "3",
    }):
        # DO managed resources inside AuthZ boundary
        fw = Firewall("Cloud Firewall\nAllow: ICMP + SSH")
        spaces = Space("DO Spaces\nTF State + Audit")

        # ===========================================
        # ZONE 2: DMZ (Orange border)
        # ===========================================
        with Cluster("ZONE 2 - DMZ (Host Network)", graph_attr={
            "fontsize": "13",
            "fontname": "Helvetica Bold",
            "fontcolor": ZONE2_COLOR,
            "bgcolor": "#1a1000",
            "style": "rounded",
            "color": ZONE2_COLOR,
            "penwidth": "2.5",
        }):
            tunnel = Docker("svc-tunnel\nCloudflare Tunnel\n(host network mode)")

        # ===========================================
        # ZONE 3: INTERNAL (Blue border)
        # ===========================================
        with Cluster("ZONE 3 - INTERNAL (Docker Networks: net-core / net-ai / net-monitoring)", graph_attr={
            "fontsize": "13",
            "fontname": "Helvetica Bold",
            "fontcolor": ZONE3_COLOR,
            "bgcolor": "#000a1a",
            "style": "rounded",
            "color": ZONE3_COLOR,
            "penwidth": "2.5",
        }):
            # Application services
            n8n = N8N("n8n SOAR\n")
            keycloak = Docker("Keycloak v26\nRBAC ")
            teleport = Docker("Teleport v18\nPAM :3080")

            # Monitoring
            dd_agent = Datadog("Datadog Agent")
            falco = Docker("Falco\neBPF Detection")
            falco_sk = Docker("Falcosidekick\nAlert Router")
            event_handler = Docker("Event Handler\nAudit Shipper")
            fluentd = Fluentd("Fluentd\nLog Shipper")

            # AI
            ollama = Docker("Ollama LLM\n")
            whisper = Docker("Whisper STT\n")
            openclaw = Docker("OpenClaw\nGateway ")

            # ===========================================
            # ZONE 4: SENSITIVE (Green border)
            # ===========================================
            with Cluster("ZONE 4 - SENSITIVE (Restricted Access)", graph_attr={
                "fontsize": "12",
                "fontname": "Helvetica Bold",
                "fontcolor": ZONE4_COLOR,
                "bgcolor": "#001a00",
                "style": "rounded,bold",
                "color": ZONE4_COLOR,
                "penwidth": "3",
            }):
                db = PostgreSQL("PostgreSQL 16\nWorkflow + Auth\nData :5432")
                vault_svc = Vault("HashiCorp Vault\nSecrets Engine\n")

    # =========================================
    # EDGES - Zone Transitions
    # =========================================

    # Zone 1 → Zone 1
    users >> Edge(color=ZONE1_COLOR, style="bold") >> inet
    inet >> Edge(color=ZONE1_COLOR, style="bold") >> cf

    # Zone 1 → AuthZ Boundary (through firewall)
    cf >> Edge(color=ZONE2_COLOR, style="bold", label="Tunnel\nProtocol") >> fw
    fw >> Edge(color=ZONE2_COLOR, style="bold") >> tunnel

    # Zone 2 → Zone 3
    tunnel >> Edge(color=ZONE3_COLOR, label="n8n.example-ops.com") >> n8n
    tunnel >> Edge(color=ZONE3_COLOR, label="ssh.example-ops.com") >> teleport

    # Zone 3 → Zone 4 (crossing trust boundary)
    n8n >> Edge(color=ZONE4_COLOR, style="bold", label="DB Access") >> db
    keycloak >> Edge(color=ZONE4_COLOR, style="bold", label="Auth Store") >> db
    teleport >> Edge(color=ZONE4_COLOR, style="bold", label="Sessions") >> db
    n8n >> Edge(color=ZONE4_COLOR, style="dashed") >> vault_svc

    # Zone 3 internal
    teleport >> Edge(color=ZONE3_COLOR) >> event_handler
    event_handler >> Edge(color=ZONE3_COLOR) >> fluentd
    falco >> Edge(color=ZONE3_COLOR) >> falco_sk

    # Zone 3 → External (outbound)
    fluentd >> Edge(color="#f0883e", style="dashed", label="Audit Logs") >> dd_saas
    falco_sk >> Edge(color="#f0883e", style="dashed", label="Alerts") >> dd_saas
    dd_agent >> Edge(color="#8b949e", style="dashed", label="Metrics") >> dd_saas

    # External → AuthZ Boundary
    gh_actions >> Edge(color=AUTHZ_COLOR, style="dotted", label="Deploy") >> fw
    ext_secrets >> Edge(color=AUTHZ_COLOR, style="dotted", label="Secrets\nInjection") >> tunnel

print(f"Generated: {FILENAME}.png")

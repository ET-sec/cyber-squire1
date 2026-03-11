#!/usr/bin/env python3
"""
Network Topology Diagram - Organization Security Operations Platform
Generates: network_topology.png
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
from diagrams.onprem.iac import Terraform
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.client import Users
from diagrams.saas.cdn import Cloudflare
from diagrams.saas.logging import Datadog as DatadogSaaS
from diagrams.saas.chat import Telegram
from diagrams.saas.automation import N8N

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(OUTPUT_DIR, "network_topology")

graph_attr = {
    "fontsize": "16",
    "fontname": "Helvetica",
    "bgcolor": "#0d1117",
    "fontcolor": "#e6edf3",
    "pad": "0.8",
    "dpi": "150",
    "ranksep": "1.2",
    "nodesep": "0.8",
    "splines": "spline",
}

cluster_attr_outer = {
    "fontsize": "14",
    "fontname": "Helvetica Bold",
    "fontcolor": "#00FF41",
    "bgcolor": "#161b22",
    "style": "rounded",
    "color": "#30363d",
    "penwidth": "2",
}

cluster_attr_inner = {
    "fontsize": "12",
    "fontname": "Helvetica",
    "fontcolor": "#8b949e",
    "bgcolor": "#0d1117",
    "style": "rounded",
    "color": "#21262d",
    "penwidth": "1.5",
}

node_attr = {
    "fontsize": "10",
    "fontname": "Helvetica",
    "fontcolor": "#e6edf3",
}

edge_attr = {
    "color": "#388bfd",
    "fontcolor": "#8b949e",
    "fontsize": "9",
    "fontname": "Helvetica",
}

with Diagram(
    "Organization — Network Topology",
    filename=FILENAME,
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    outformat="png",
):
    # External
    users = Users("Users / Operators")
    inet = Internet("Internet")
    cf = Cloudflare("Cloudflare\nEdge + DNS")
    dd_saas = DatadogSaaS("Datadog SaaS\nus5.datadoghq.com")
    gh_actions = GithubActions("GitHub Actions\nCI/CD")
    tg = Telegram("Telegram\nBots")

    with Cluster("DigitalOcean VPC — nyc1", graph_attr=cluster_attr_outer):
        fw = Firewall("Cloud Firewall\nICMP + SSH only")
        spaces = Space("DO Spaces\nState + Audit Logs")

        with Cluster("Droplet: alpha-node (4 vCPU / 8GB)", graph_attr={
            **cluster_attr_outer,
            "bgcolor": "#0d1117",
            "color": "#00FF41",
            "penwidth": "2.5",
        }):

            # Tunnel on host network
            tunnel = Docker("svc-tunnel\n(Cloudflare Tunnel)\nHost Network")

            with Cluster("Docker Bridge: internal-net", graph_attr=cluster_attr_inner):

                with Cluster("Core Services", graph_attr={
                    **cluster_attr_inner,
                    "fontcolor": "#00FF41",
                }):
                    db = PostgreSQL("svc-db\nPostgreSQL 16\n:5432")
                    n8n = N8N("svc-automation\nn8n SOAR\n:5678")

                with Cluster("Security & Monitoring", graph_attr={
                    **cluster_attr_inner,
                    "fontcolor": "#f0883e",
                }):
                    dd_agent = Datadog("svc-monitor\nDatadog Agent")
                    falco = Docker("svc-detection\nFalco eBPF")
                    falco_sk = Docker("svc-detection-router\nAlert Router")
                    fluentd = Fluentd("svc-log-router\nFluentd")
                    event_handler = Docker("svc-event-shipper\nTeleport Audit\nShipper")

                with Cluster("Access & Identity", graph_attr={
                    **cluster_attr_inner,
                    "fontcolor": "#a371f7",
                }):
                    vault_svc = Vault("svc-secrets\nHashiCorp Vault\n:8200")
                    keycloak = Docker("svc-identity\nKeycloak v26\n:8080")
                    teleport = Docker("svc-gateway\nTeleport v18\n:3080")

                with Cluster("AI & Inference", graph_attr={
                    **cluster_attr_inner,
                    "fontcolor": "#79c0ff",
                }):
                    ollama = Docker("svc-llm\nOllama LLM\n:11434")
                    whisper = Docker("svc-transcription\nWhisper STT\n:8000")

            # Standalone container on bridge
            openclaw = Docker("svc-ai-gateway\nOpenClaw Gateway\n:18789-18790")

    # --- Edges ---
    # Inbound traffic
    users >> Edge(color="#00FF41", style="bold") >> inet
    inet >> Edge(color="#00FF41", style="bold") >> cf
    cf >> Edge(color="#00FF41", style="bold", label="Tunnel") >> fw
    fw >> Edge(color="#00FF41") >> tunnel

    # Tunnel routes
    tunnel >> Edge(color="#388bfd", label="n8n.example-ops.com") >> n8n
    tunnel >> Edge(color="#388bfd", label="ssh.example-ops.com") >> teleport

    # Internal data
    n8n >> Edge(color="#8b949e") >> db
    keycloak >> Edge(color="#8b949e") >> db

    # Monitoring pipeline
    falco >> Edge(color="#f0883e") >> falco_sk
    falco_sk >> Edge(color="#f0883e") >> dd_saas
    teleport >> Edge(color="#f0883e") >> event_handler
    event_handler >> Edge(color="#f0883e") >> fluentd
    fluentd >> Edge(color="#f0883e") >> dd_saas
    dd_agent >> Edge(color="#f0883e") >> dd_saas

    # Outbound
    n8n >> Edge(color="#8b949e", style="dashed") >> tg
    openclaw >> Edge(color="#79c0ff", style="dashed", label="Anthropic API") >> inet

    # CI/CD
    gh_actions >> Edge(color="#a371f7", style="dashed", label="Deploy") >> fw

    # Terraform state
    gh_actions >> Edge(color="#8b949e", style="dotted", label="State") >> spaces

print(f"Generated: {FILENAME}.png")

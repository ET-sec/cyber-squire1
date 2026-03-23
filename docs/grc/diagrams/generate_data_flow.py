#!/usr/bin/env python3
"""
Data Flow Diagram - Organization Security Operations Platform
Generates: data_flow.png
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.container import Docker
from diagrams.onprem.monitoring import Datadog
from diagrams.onprem.security import Vault
from diagrams.onprem.network import Internet
from diagrams.onprem.aggregator import Fluentd
from diagrams.onprem.client import Users
from diagrams.saas.cdn import Cloudflare
from diagrams.saas.logging import Datadog as DatadogSaaS
from diagrams.saas.chat import Telegram
from diagrams.saas.automation import N8N

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FILENAME = os.path.join(OUTPUT_DIR, "data_flow")

graph_attr = {
    "fontsize": "16",
    "fontname": "Helvetica",
    "bgcolor": "#0d1117",
    "fontcolor": "#e6edf3",
    "pad": "0.8",
    "dpi": "150",
    "ranksep": "1.0",
    "nodesep": "0.7",
    "splines": "spline",
}

cluster_dark = {
    "fontsize": "13",
    "fontname": "Helvetica Bold",
    "fontcolor": "#00FF41",
    "bgcolor": "#161b22",
    "style": "rounded",
    "color": "#30363d",
    "penwidth": "2",
}

cluster_inner = {
    "fontsize": "11",
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
    "fontsize": "9",
    "fontname": "Helvetica",
    "fontcolor": "#8b949e",
}

# Color legend for data flows
GREEN = "#00FF41"      # Inbound user traffic
BLUE = "#388bfd"       # Internal service communication
ORANGE = "#f0883e"     # Audit / detection pipeline
PURPLE = "#a371f7"     # Secrets / identity flow
CYAN = "#79c0ff"       # AI / external API
GRAY = "#8b949e"       # Monitoring metrics

with Diagram(
    "Organization - Data Flow Diagram",
    filename=FILENAME,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    outformat="png",
):
    # === External Sources ===
    users = Users("Users\nOperators")
    inet = Internet("Internet")
    cf = Cloudflare("Cloudflare\nEdge")

    # === External Sinks ===
    dd_saas = DatadogSaaS("Datadog SaaS\nCloud")
    tg = Telegram("Telegram API")
    anthropic = Internet("Anthropic API\n(Claude)")

    # === Secrets Source ===
    ext_secrets = Docker("External\nSecrets Manager")

    with Cluster("DigitalOcean Droplet", graph_attr=cluster_dark):

        tunnel = Docker("Cloudflare\nTunnel")

        with Cluster("Inbound Traffic Flow", graph_attr={
            **cluster_inner, "fontcolor": GREEN
        }):
            n8n = N8N("n8n SOAR\n")
            keycloak = Docker("Keycloak\nRBAC ")
            teleport = Docker("Teleport\nPAM :3080")

        with Cluster("Data Store", graph_attr={
            **cluster_inner, "fontcolor": BLUE
        }):
            db = PostgreSQL("PostgreSQL 16\n:5432")
            vault_svc = Vault("HashiCorp\nVault ")

        with Cluster("Audit Log Pipeline", graph_attr={
            **cluster_inner, "fontcolor": ORANGE
        }):
            event_handler = Docker("Event Handler\n(Teleport Audit)")
            fluentd = Fluentd("Fluentd\n(Log Shipper)")

        with Cluster("Detection Pipeline", graph_attr={
            **cluster_inner, "fontcolor": "#f85149"
        }):
            falco = Docker("Falco\n(eBPF Detection)")
            falco_sk = Docker("Falcosidekick\n(Alert Router)")

        with Cluster("Monitoring Pipeline", graph_attr={
            **cluster_inner, "fontcolor": GRAY
        }):
            dd_agent = Datadog("Datadog Agent\n(Metrics)")

        with Cluster("AI Services", graph_attr={
            **cluster_inner, "fontcolor": CYAN
        }):
            ollama = Docker("Ollama\nLLM ")
            whisper = Docker("Whisper\nSTT ")
            openclaw = Docker("OpenClaw\nGateway ")

    # =========================================
    # FLOW 1: Inbound User Traffic (GREEN)
    # =========================================
    users >> Edge(color=GREEN, style="bold", label="HTTPS") >> inet
    inet >> Edge(color=GREEN, style="bold", label="DDoS\nFilter") >> cf
    cf >> Edge(color=GREEN, style="bold", label="Tunnel\nProtocol") >> tunnel
    tunnel >> Edge(color=GREEN, label="n8n.example-ops.com") >> n8n
    tunnel >> Edge(color=GREEN, label="ssh.example-ops.com") >> teleport

    # =========================================
    # FLOW 2: Internal Service Comm (BLUE)
    # =========================================
    n8n >> Edge(color=BLUE, label="Workflow\nState") >> db
    keycloak >> Edge(color=BLUE, label="Auth\nSessions") >> db
    teleport >> Edge(color=BLUE, label="Session\nRecords") >> db
    n8n >> Edge(color=BLUE, style="dashed", label="LLM\nQueries") >> ollama
    n8n >> Edge(color=BLUE, style="dashed", label="Transcribe") >> whisper
    n8n >> Edge(color=BLUE, style="dashed") >> vault_svc

    # =========================================
    # FLOW 3: Audit Log Pipeline (ORANGE)
    # =========================================
    teleport >> Edge(color=ORANGE, style="bold", label="Audit\nEvents") >> event_handler
    event_handler >> Edge(color=ORANGE, style="bold", label="Structured\nLogs") >> fluentd
    fluentd >> Edge(color=ORANGE, style="bold", label="Ship\nLogs") >> dd_saas

    # =========================================
    # FLOW 4: Detection Pipeline (RED-ORANGE)
    # =========================================
    falco >> Edge(color="#f85149", style="bold", label="Syscall\nAlerts") >> falco_sk
    falco_sk >> Edge(color="#f85149", style="bold", label="Route\nAlerts") >> dd_saas

    # =========================================
    # FLOW 5: Monitoring Pipeline (GRAY)
    # =========================================
    dd_agent >> Edge(color=GRAY, style="bold", label="Container\nMetrics") >> dd_saas

    # =========================================
    # FLOW 6: Outbound (CYAN)
    # =========================================
    openclaw >> Edge(color=CYAN, style="bold", label="Claude\nAPI") >> anthropic
    n8n >> Edge(color=CYAN, style="dashed", label="Bot\nMessages") >> tg

    # =========================================
    # FLOW 7: Secrets (PURPLE)
    # =========================================
    ext_secrets >> Edge(color=PURPLE, style="dotted", label="Env Vars\nat Deploy") >> n8n
    ext_secrets >> Edge(color=PURPLE, style="dotted") >> dd_agent
    ext_secrets >> Edge(color=PURPLE, style="dotted") >> tunnel

print(f"Generated: {FILENAME}.png")

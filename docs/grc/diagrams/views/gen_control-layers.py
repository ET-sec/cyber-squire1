# Generates control-layers.html in the topology grammar.
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "control-layers.html")

GREEN="#3dff8b"; ORANGE="#ff9b3d"; AMBER="#ffc247"; BONE="#e8dcc0"; TEXT="#e6ebe4"; DIM="#a3ada1"

BANDS = [
 dict(name="EDGE", color=GREEN, tint="rgba(61,255,139,0.03)", q="who reaches the origin",
      hero="0", desc="origin addresses in DNS",
      nodes=[("Access","login before origin",True),("WAF","custom and managed",False),("DDoS","absorbed off-host",False),
             ("rate limits","per IP, webhook path",False),("DNS proxy","no origin address",False)],
      ctl=["SC-7","SC-5","AC-3","SC-8"]),
 dict(name="HOST", color=TEXT, tint="rgba(255,255,255,0.018)", q="what listens on the host",
      hero="1", desc="inbound port, SSH only",
      nodes=[("outbound tunnel","no inbound listener",True),("loopback binds","no interface exposed",False),
             ("break-glass SSH","allowlisted, keys",False),("CIS baseline","exceptions on record",False),
             ("no-new-privileges","18 of 19 services",False),("resource limits","CPU, memory, PIDs",False)],
      ctl=["SC-7","CM-6","CM-7","AC-6","SC-6"]),
 dict(name="RUNTIME", color=AMBER, tint="rgba(255,194,71,0.025)", q="what a container can reach",
      hero="3", desc="networks, one sealed, no route out",
      nodes=[("Falco eBPF","below the workloads",True),("three networks","core, ai, monitoring",False),
             ("sealed net-ai","no internet route",False),("read-only root","tunnel, alert router",False),
             ("digest pinning","Renovate tiers",False),("alerts off-host","shipped to the SIEM",False)],
      ctl=["AC-4","SC-7","SI-3","SI-4","SI-7","CM-8","IR-4"]),
 dict(name="APPLICATION", color=ORANGE, tint="rgba(255,155,61,0.03)", q="what the agent may do",
      hero="9", desc="layers, WAF to audit trail",
      nodes=[("input rails","PII and injection",True),("output rails","policy, schema check",False),
             ("actions allowlist","deny by default",False),("spend ceiling","per alert, daily cap",False),
             ("Langfuse trace","every call recorded",False),("webhook token","shared secret",False),
             ("HITL review","high and critical",False)],
      ctl=["SI-10","SI-4","AC-3","AU-2","AU-12","SA-8"]),
 dict(name="IDENTITY", color=TEXT, tint="rgba(255,255,255,0.018)", q="who, with what, how long",
      hero="4h", desc="JIT elevation, then expiry",
      nodes=[("Keycloak OIDC","realm roles, RBAC",False),("Teleport MFA","TOTP, every session",True),
             ("JIT elevation","approved, expires",False),("session recording","to SIEM over mTLS",False),
             ("Vault AppRole","short-TTL creds",False),("lockout policy","failed logins alert",False)],
      ctl=["IA-2","IA-2(1)","AC-2","AC-12","IA-5","SC-12","AC-7"]),
 dict(name="DATA", color=TEXT, tint="rgba(255,255,255,0.018)", q="where state lives",
      hero="30d", desc="retention rule on backups",
      nodes=[("Postgres","bridge-only, no port",False),("CMK encryption","state and backups",True),
             ("object storage","state versioned",False),("nightly backup","instance principal",False),
             ("timed restore","monthly, logged",False)],
      ctl=["SC-28","SC-12","SC-13","CP-6","CP-9","CP-10","CP-4"]),
 dict(name="DELIVERY", color=BONE, tint="rgba(232,220,192,0.03)", q="how change arrives",
      hero="8", desc="gates, 4 deny, 4 warn",
      nodes=[("pull request","only path to change",False),("OIDC exchange","short-lived token",False),
             ("scanners","CVE, SAST, secrets",False),("OPA gates","4 deny, 4 warn",True),
             ("Cosign verify","upstream images",False),("human review","required to merge",False),
             ("nightly drift","re-plan, diff alerts",True)],
      ctl=["CM-3","CM-5","CM-4","SA-11","RA-5","SI-7","CA-7"]),
]

Y0=40; PITCH=106; BH=96
BX=28; BW=1644
RAIL_X=44
NODE_X0=250; NODE_W=148; NODE_PITCH=156
CHIP_X0=1356; CHIP_MAX=316

def fs(label):
    n=len(label)
    return 16 if n<=12 else (15 if n<=14 else 14)

svg=[]
a=svg.append
# column headers
a(f'<g font-size="12" font-weight="700" letter-spacing="2" fill="{DIM}">')
a(f'<text x="{RAIL_X}" y="24">LAYER</text>')
a(f'<text x="{NODE_X0}" y="24">BARRIER</text>')
a(f'<text x="{CHIP_X0}" y="24">NIST 800-53 REV 5</text>')
a('</g>')
a(f'<text x="1672" y="24" font-size="11.5" fill="{DIM}" text-anchor="end">133 controls cited</text>')

for i,b in enumerate(BANDS):
    y=Y0+PITCH*i
    c=b["color"]
    a(f'<!-- ===== {b["name"]} ===== -->')
    a(f'<rect x="{BX}" y="{y}" width="{BW}" height="{BH}" rx="7" fill="{b["tint"]}" stroke="#27342b" stroke-width="1.5"/>')
    # rail
    a(f'<text x="{RAIL_X}" y="{y+22}" font-size="12" font-weight="700" fill="{c}" letter-spacing="2">{b["name"]}</text>')
    a(f'<text x="{RAIL_X}" y="{y+38}" font-size="11.5" fill="{DIM}">{b["q"]}</text>')
    a(f'<text x="{RAIL_X}" y="{y+74}" font-size="26" font-weight="700" fill="{c}">{b["hero"]}</text>')
    a(f'<text x="{RAIL_X}" y="{y+89}" font-size="11.5" fill="{DIM}">{b["desc"]}</text>')
    # nodes
    for j,(lab,sub,hi) in enumerate(b["nodes"]):
        x=NODE_X0+NODE_PITCH*j; cx=x+NODE_W/2
        stroke = c if hi else "#2c3a30"
        a(f'<rect x="{x}" y="{y+18}" width="{NODE_W}" height="40" rx="5" fill="#141b16" stroke="{stroke}" stroke-width="1.5"/>')
        a(f'<text x="{cx:g}" y="{y+43}" font-size="{fs(lab)}" font-weight="500" fill="{TEXT}" text-anchor="middle">{lab}</text>')
        a(f'<text x="{cx:g}" y="{y+75}" font-size="11.5" fill="{DIM}" text-anchor="middle">{sub}</text>')
    # chips, wrapped
    cx=CHIP_X0; row=0
    for cid in b["ctl"]:
        w=round(12+6.9*len(cid))
        if cx+w>CHIP_X0+CHIP_MAX:
            row+=1; cx=CHIP_X0
        by=y+40+28*row
        a(f'<rect x="{cx}" y="{by-14}" width="{w}" height="20" rx="3" fill="#0d181e" stroke="#2c3a30" stroke-width="1"/>')
        a(f'<text x="{cx+w/2:g}" y="{by}" font-size="11.5" fill="{TEXT}" text-anchor="middle">{cid}</text>')
        cx+=w+8

H = Y0+PITCH*(len(BANDS)-1)+BH+16

html = f'''<title>CoreDirective Control Layers</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
  :root{{
    --ink:#0a0d0b;
    --node:#141b16;
    --line:#27342b;
    --line-soft:#1b241e;
    --text:#e6ebe4;
    --dim:#a3ada1;
    --green:#3dff8b;
    --orange:#ff9b3d;
    --amber:#ffc247;
    --bone2:#e8dcc0;
    --red:#ff6b5e;
    --bone:#e8dcc0;
    --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
    --sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  }}
  *{{box-sizing:border-box}}
  html{{background:var(--ink)}}
  body{{background:var(--ink);color:var(--text);font-family:var(--sans);margin:0;line-height:1.4;-webkit-font-smoothing:antialiased}}
  .page{{max-width:1720px;margin:0 auto;padding:16px 26px 16px}}

  .head{{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 24px;padding-bottom:10px;border-bottom:1px solid var(--line-soft)}}
  .head h1{{font-size:20px;font-weight:600;margin:0;letter-spacing:-.01em}}
  .head p{{font-family:var(--mono);font-size:12px;color:var(--dim);margin:0;letter-spacing:.02em}}
  .head .tag{{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.14em;text-transform:uppercase}}

  figure{{margin:10px 0 0}}
  svg{{display:block;width:100%;height:auto;max-width:100%;max-height:calc(100vh - 150px);margin:0 auto;color:var(--text);font-family:var(--mono)}}
  figcaption{{
    display:grid;grid-template-columns:repeat(4,1fr);gap:8px 22px;
    margin-top:10px;padding-top:10px;border-top:1px solid var(--line-soft);
    font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:.01em;
  }}
  @media (max-width:1100px){{figcaption{{grid-template-columns:repeat(2,1fr)}}}}
  figcaption b{{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px;font-weight:700}}
  .g b{{color:var(--green)}} .b b{{color:var(--orange)}} .a b{{color:var(--amber)}} .v b{{color:var(--bone)}}
</style>

<div class="page">
  <div class="head">
    <h1>CoreDirective reference architecture</h1>
    <p>seven barrier layers on one hardened host, moderate baseline, sanitized, no addresses, ports, or versions</p>
    <span class="tag">Control layers</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="Control layers view of the CoreDirective platform. Seven horizontal bands, edge, host, runtime, application, identity, data, and delivery. Each band names the barriers at that layer and the NIST 800-53 Revision 5 control identifiers they satisfy, as cited in the system security plan. Edge: identity checked before the origin, WAF with custom and managed rules, DDoS absorption, per-IP rate limits on the webhook path, and no origin address in DNS. Host: an outbound-only tunnel, services published to loopback, one inbound port, break-glass SSH from an allowlisted source, a CIS baseline with documented exceptions, no-new-privileges on 18 of 19 services, and resource limits. Runtime: a kernel sensor below the workloads, three bridge networks with one that has no internet route, read-only roots on the tunnel and alert router, digest pinning with review tiers, and alerts shipped off-host into the incident handling pipeline. Application: input and output rails, a typed actions allowlist, a per-alert spend ceiling with a daily cap, tracing of every call, a rotated shared-secret webhook token, and human review for high severity. Identity: OIDC realm roles, MFA on every session, just-in-time elevation that expires, recorded sessions, short-lived credentials from Vault, and lockout. Data: a bridge-only database, customer managed key encryption on state and backups, versioned state and retention-ruled backups in object storage, nightly backups by instance principal, and a monthly timed restore. Delivery: pull request only, OIDC token exchange, scanners, eight policy gates, signature verification of upstream images, human review, and a nightly drift check.">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="g"><b>Outside in</b>edge identity → WAF → tunnel dialed out → loopback, nothing listens publicly</div>
    <div class="a"><b>Inside</b>three networks, one sealed, kernel sensor below the workloads, 18 of 19 no-new-privileges</div>
    <div class="b"><b>Agent</b>rails → allowlist → spend cap → trace, blast radius is the allowlist</div>
    <div class="v"><b>Change</b>PR → OIDC → Trivy, Semgrep, Gitleaks → 8 gates → review → apply, drift re-plans nightly</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html)
print("wrote", OUT, "viewBox H =", H, "lines", html.count("\n"))

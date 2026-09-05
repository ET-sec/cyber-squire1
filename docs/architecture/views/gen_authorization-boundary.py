import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "authorization-boundary.html")
INK="#0a0d0b"; NODE="#141b16"; NSTROKE="#2c3a30"; LINE="#27342b"; LINESOFT="#1b241e"; TEXT="#e6ebe4"; DIM="#a3ada1"; EXT="#4a5a4e"
RED="#ff6b5e"; GREEN="#3dff8b"; BONE="#e8dcc0"; AMBER="#ffc247"; ORANGE="#ff9b3d"
def t(x,y,s,size,color,weight=None,anchor="start",ls=None,halo=False):
    a=f' font-weight="{weight}"' if weight else ''
    l=f' letter-spacing="{ls}"' if ls else ''
    h=f' paint-order="stroke" stroke="{INK}" stroke-width="4" stroke-linejoin="round"' if halo else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}"{a}{l} text-anchor="{anchor}"{h}>{s}</text>'
def node(x,y,w,label,sub=None,h=32,stroke=NSTROKE,ext=False,size=12.5):
    dash=' stroke-dasharray="5 4"' if ext else ''
    fill="none" if ext else NODE
    o=[f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>']
    if sub:
        o.append(t(x+w/2,y+18,label,size+0.5,TEXT,500,"middle")); o.append(t(x+w/2,y+34,sub,11,DIM,None,"middle"))
    else:
        o.append(t(x+w/2,y+h/2+4.5,label,size,TEXT,500,"middle"))
    return "".join(o)
def arrow(d,color,mid,dash=False,width=2.5):
    ds=' stroke-dasharray="6 5"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{ds} marker-end="url(#m-{mid})"/>'
def cross(x,y): return f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="{INK}" stroke="{BONE}" stroke-width="1.5"/>'
svg=[]; a=svg.append
a('<defs>'+"".join(f'<marker id="m-{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for n,c in [("green",GREEN),("orange",ORANGE),("amber",AMBER),("bone",BONE),("red",RED),("gray",DIM)])+'</defs>')
BX,BY,BW,BH=350,30,900,660
crossings=0
# ===== boundary =====
a(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="10" fill="rgba(232,220,192,0.015)" stroke="{BONE}" stroke-width="3" stroke-dasharray="18 9"/>')
a(t(BX+22,58,"AUTHORIZATION BOUNDARY",13,BONE,700,"start",2))
a(t(BX+22,76,"one hardened host, 19 services, three Terraform modules, the configuration that changes them; Moderate baseline, 133 controls cited in the SSP",11.5,DIM))
# ===== configuration plane =====
a(f'<rect x="370" y="88" width="860" height="88" rx="7" fill="rgba(255,255,255,0.015)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(382,106,"CONFIGURATION ITEMS",12,TEXT,700,"start",2)); a(t(382,142,"versioned here  CM-2 CM-3",11.5,DIM)); a(t(382,157,"executed by the providers",11.5,DIM))
CFG=[(560,"edge policy","Access, WAF, tokens"),(730,"workflows","14 definitions, pinned"),(900,"policy gates","8 OPA, 4 deny, 4 warn"),(1070,"drift check","nightly re-plan, alerts")]
for x,l,s in CFG:
    a(node(x,104,150,l,h=40,size=13)); a(t(x+75,161,s,11.5,DIM,None,"middle"))
# ===== host =====
a(f'<rect x="370" y="186" width="860" height="294" rx="7" fill="rgba(255,255,255,0.015)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(382,204,"HOST",12,TEXT,700,"start",2)); a(t(440,204,"one hardened VM, published to loopback only, three segments",11.5,DIM))
a(node(402,212,150,"tunnel connector",stroke=GREEN)); a(t(562,232,"host network, read-only root; dials out, listens on nothing public",11.5,DIM))
# sshd tag on the line
a(f'<rect x="358" y="300" width="80" height="22" rx="3" fill="{INK}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="4 3"/>'); a(t(398,315,"host sshd",11.5,RED,None,"middle"))
# segments
a(f'<rect x="448" y="270" width="380" height="198" rx="6" fill="rgba(255,255,255,0.015)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(460,288,"NET-CORE",11.5,TEXT,700,"start",2)); a(t(548,288,"state, identity, orchestration",11.5,DIM))
core=["n8n","Squire","Guardrails","Postgres","Vault","Keycloak","Teleport","event shipper","Langfuse web","Langfuse worker","ClickHouse","Redis"]
for i,l in enumerate(core):
    a(node(460+(i%3)*126,300+(i//3)*38,112,l,h=30,size=12))
a(f'<rect x="840" y="270" width="150" height="198" rx="6" fill="rgba(232,220,192,0.03)" stroke="{BONE}" stroke-width="1.5" stroke-dasharray="7 5"/>')
a(t(850,288,"NET-AI",11.5,BONE,700,"start",2)); a(t(917,288,"sealed",11.5,DIM))
a(node(850,300,130,"Whisper",h=30)); a(node(850,338,130,"Ollama",h=30))
a(t(915,394,"no route out",11.5,DIM,None,"middle")); a(t(915,410,"bridged by n8n",11.5,DIM,None,"middle")); a(t(915,426,"audio never leaves",11.5,DIM,None,"middle"))
a(f'<rect x="1004" y="270" width="226" height="198" rx="6" fill="rgba(255,255,255,0.015)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(1014,288,"NET-MONITORING",11.5,TEXT,700,"start",2))
for i,l in enumerate(["Falco, eBPF","Falcosidekick","Fluentd","Datadog agent"]):
    a(node(1014,300+i*38,206,l,h=30,stroke=AMBER if i==0 else NSTROKE))
a(t(1117,458,"reads the kernel below every container",11,DIM,None,"middle"))
# ===== cloud resources =====
a(f'<rect x="370" y="496" width="430" height="172" rx="7" fill="rgba(232,220,192,0.02)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(382,516,"RUNTIME CLOUD",12,BONE,700,"start",2)); a(t(382,532,"compute, network, keys, state and backups under Terraform",11.5,DIM))
for i,l in enumerate(["compute, 1 host","VCN, one port","object storage","KMS, CMK","identity domain","instance identity"]):
    a(node(382+(i%3)*142,544+(i//3)*40,130,l,h=32,stroke=(RED if l=="VCN, one port" else BONE if l=="identity domain" else NSTROKE)))
a(t(382,640,"instance identity writes backups and cannot delete them",11.5,DIM)); a(t(382,656,"state versioned, backups on a retention rule, both under the CMK",11.5,DIM))
a(f'<rect x="816" y="496" width="414" height="172" rx="7" fill="rgba(255,194,71,0.02)" stroke="{LINE}" stroke-width="1.5"/>')
a(t(828,516,"SECURITY PLANE",12,AMBER,700,"start",2)); a(t(828,532,"what must survive the runtime cloud, on a second provider",11.5,DIM))
for i,l in enumerate(["OIDC federation","evidence vault","break-glass key","alert on read","account trail","region guard"]):
    a(node(828+(i%3)*134,544+(i//3)*40,124,l,h=32,stroke=(AMBER if l in("evidence vault","alert on read") else RED if l=="break-glass key" else BONE if l=="OIDC federation" else NSTROKE)))
a(t(828,640,"evidence and backup replicas arrive one way, write-only",11.5,DIM)); a(t(828,656,"no automatic path back; a secret read pages on-call",11.5,DIM))
# ===== left column: outside =====
a(t(20,44,"OUTSIDE",12,BONE,700,"start",2)); a(t(96,44,"people and the front door",11.5,DIM))
a(node(20,106,160,"users","browsers, any network",h=44))
a(node(20,196,160,"edge platform","Access, WAF, tunnel",h=44,ext=True,stroke=EXT))
a(node(20,290,160,"operators","workstation, SSH, IaC",h=44))
a(node(20,380,160,"Telegram","bot API, on-call channel",h=44,ext=True,stroke=EXT))
# users to edge
a(arrow("M100,150 V195",GREEN,"green")); a(t(108,178,"HTTPS, one-time PIN  IA-2",11.5,GREEN,None,"start",None,True))
a(arrow("M100,290 V241",GREEN,"green")); a(t(108,270,"recorded SSH, TOTP  IA-2",11.5,GREEN,None,"start",None,True))
# tunnel: host dials out to the edge, requests ride it in
a(arrow(f"M401,228 H181",GREEN,"green")); a(cross(BX,228)); crossings+=1
a(t(190,250,"out: tunnel, TLS  SC-7 SC-8",11.5,GREEN,None,"start",None,True)); a(t(190,265,"requests ride it in",11.5,DIM,None,"start",None,True))
# edge policy configures the edge platform
a(arrow("M559,124 H290 V206 H181",DIM,"gray",width=2)); a(cross(BX,124)); crossings+=1
a(t(344,118,"configures, TLS  CM-3",11.5,DIM,None,"end",None,True))
# operators SSH break-glass
a(arrow("M181,312 H357",RED,"red",dash=True)); a(cross(BX,312)); crossings+=1
a(t(190,345,"in: break-glass, key",11.5,RED,None,"start",None,True)); a(t(190,360,"allowlist  SC-7 MA-4",11.5,DIM,None,"start",None,True))
# Telegram in and out
a(arrow("M181,392 H369",GREEN,"green")); a(cross(BX,392)); crossings+=1
a(t(190,384,"in: carve-out, IP ranges  AC-3",11.5,GREEN,None,"start",None,True))
a(arrow("M370,412 H181",ORANGE,"orange")); a(cross(BX,412)); crossings+=1
a(t(190,428,"out: notify, TLS  SC-8",11.5,ORANGE,None,"start",None,True))
# inherited list
a(t(20,470,"INHERITED",12,BONE,700,"start",2)); a(t(112,470,"controls the providers carry",11.5,DIM))
inh=[("Oracle Cloud and AWS, IaaS","physical, hypervisor, backbone, resolver","PE family  MP-4  MP-6  SC-21"),("Cloudflare, edge","DDoS, WAF engine, tunnel edge, DNS","SC-20  SC-22")]
for j,(l1,l2,l3) in enumerate(inh):
    y=494+j*58; a(t(20,y,l1,12.5,TEXT,500)); a(t(20,y+15,l2,11.5,DIM)); a(t(20,y+30,l3,11.5,DIM))
# ===== right column: external services =====
a(t(1480,44,"OUTSIDE",12,BONE,700,"start",2)); a(t(1556,44,"external services",11.5,DIM)); a(t(1480,60,"commercial, no federal data",11,DIM)); a(t(1480,74,"SA-9 providers, CA-3 documented",11,DIM))
EXTS=[(170,"image registries","upstream images, pinned",BONE,"bone","in",1230,"in: image pull, TLS, by digest","signatures checked  CM-5 SI-7"),
      (227,"secrets manager","deploy-time injection",BONE,"bone","in",1230,"in at deploy: TLS, env vars","chmod 600, none in git  IA-5"),
      (284,"Datadog","SIEM, events, logs",AMBER,"amber","out",1230,"out: TLS, agent key","audit off-host  AU-9 SI-4"),
      (341,"Claude API","frontier model",ORANGE,"orange","out",1230,"out: TLS, bearer, screened","from Guardrails  SI-10 SA-9"),
      (398,"embeddings API","index and query text",ORANGE,"orange","out",1230,"out: TLS, text to embed","chunks and queries  SA-9"),
      (455,"web search API","enrichment",ORANGE,"orange","out",1230,"out: TLS, indicator terms","two nodes, skippable  SA-9"),
      (512,"GitHub","repo, runners, OIDC issuer",BONE,"bone","in",1230,"in: signed JWT, both clouds","minutes, main only  IA-5 AC-6")]
for y,l,s,c,m,d,xin,l1,l2 in EXTS:
    a(node(1480,y,200,l,s,h=44,ext=True,stroke=EXT))
    ay=y+22
    if d=="in": a(arrow(f"M1479,{ay} H{xin+1}",c,m))
    else: a(arrow(f"M{xin},{ay} H1479",c,m))
    a(cross(BX+BW,ay)); crossings+=1
    a(t(1262,ay-7,l1,11.5,c,None,"start",None,True)); a(t(1262,ay+16,l2,11.5,DIM,None,"start",None,True))
# legend
LX,LY=1480,590
a(t(LX,LY,"READING THE PAGE",11,DIM,700,"start",2))
rows=[("line",BONE,3,"18 9","authorization boundary"),("cross",None,0,"","crossing point"),
      ("line",GREEN,2.5,"","human request path"),("line",ORANGE,2.5,"","agent path, screened"),("line",AMBER,2.5,"","audit, telemetry out"),
      ("line",BONE,2,"","machine identity"),("line",RED,2.5,"6 5","inbound exception"),("line",DIM,2,"","configures")]
for j,(k,c,w,dsh,lab) in enumerate(rows):
    y=LY+18+j*18
    if k=="line":
        ds=f' stroke-dasharray="{dsh}"' if dsh else ''
        a(f'<line x1="{LX}" y1="{y}" x2="{LX+34}" y2="{y}" stroke="{c}" stroke-width="{w}"{ds}/>')
    else: a(cross(LX+17,y))
    a(t(LX+44,y+4,lab,11.5,DIM))
H=770
html=f'''<title>CoreDirective Authorization Boundary</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
  :root{{
    --ink:{INK}; --node:{NODE}; --line:{LINE}; --line-soft:{LINESOFT}; --text:{TEXT}; --dim:{DIM};
    --green:{GREEN}; --bone:{BONE}; --amber:{AMBER}; --red:{RED}; --orange:{ORANGE};
    --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
    --sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  }}
  *{{box-sizing:border-box}}
  html{{background:var(--ink)}}
  body{{background:var(--ink);color:var(--text);font-family:var(--sans);margin:0;line-height:1.4;-webkit-font-smoothing:antialiased}}
  .page{{max-width:1720px;margin:0 auto;padding:14px 26px 10px}}
  .head{{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 24px;padding-bottom:10px;border-bottom:1px solid var(--line-soft)}}
  .head h1{{font-size:20px;font-weight:600;margin:0;letter-spacing:-.01em}}
  .head p{{font-family:var(--mono);font-size:12px;color:var(--dim);margin:0;letter-spacing:.02em}}
  .head .tag{{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.14em;text-transform:uppercase}}
  figure{{margin:10px 0 0}}
  svg{{display:block;width:100%;height:auto;max-width:100%;max-height:calc(100vh - 150px);margin:0 auto;color:var(--text);font-family:var(--mono)}}
  figcaption{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px 22px;margin-top:10px;padding-top:10px;border-top:1px solid var(--line-soft);font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:.01em}}
  @media (max-width:1100px){{figcaption{{grid-template-columns:repeat(2,1fr)}}}}
  figcaption b{{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px;font-weight:700}}
  .g b{{color:var(--green)}} .c b{{color:var(--bone)}} .a b{{color:var(--amber)}} .r b{{color:var(--red)}}
</style>

<div class="page">
  <div class="head">
    <h1>CoreDirective reference architecture</h1>
    <p>what is inside the boundary, what the providers carry, and every crossing with its control</p>
    <span class="tag">Authorization boundary</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="Authorization boundary view of the CoreDirective platform. A dashed boundary encloses one hardened host running 19 services across three segments, the cloud resources under Terraform on the runtime cloud (compute, a virtual network with one inbound port, object storage for state and backups, a customer managed key, an identity domain for pipeline tokens, and an instance identity that writes backups but cannot delete them), a security plane account on a second provider (OIDC federation, an evidence vault with object lock, a sealed break-glass key whose reads page on-call, an account trail, a region guard), and configuration items, edge policy, 14 SHA-pinned workflow definitions, 8 policy gates, and a nightly drift check, versioned inside the boundary and executed by the providers. Outside on the left: users reach the edge platform with a one-time PIN; the host dials an outbound tunnel to that edge and requests ride it in, so nothing listens publicly; operators reach the host through the edge on recorded SSH with a second factor, and hold one break-glass exception: key-based SSH from allowlisted sources straight to the host; Telegram enters through an edge carve-out scoped to its published address ranges and receives notifications. Outside on the right, seven external services, each crossing labeled with direction, protocol, and control: image registries in, pulled by digest with signatures checked; a secrets manager injecting environment variables at deploy; Datadog receiving audit records and telemetry over TLS; the Claude API receiving screened prompts from Guardrails; an embeddings API receiving corpus chunks and alert query text; a web search API receiving indicator terms from two nodes; and GitHub presenting a signed, minutes-lived JWT to both clouds. Inherited from the providers: physical, hypervisor, and backbone controls from the two cloud providers, and DDoS, WAF engine, tunnel edge, and secure DNS from the edge provider, six control rows marked inherited in the system security plan. The Teleport event shipper spans net-core and net-monitoring.">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="g"><b>Inside</b>one host, 19 services, three Terraform modules, the configuration that changes them; 133 controls cited, Moderate baseline</div>
    <div class="c"><b>Crossings</b>{crossings} drawn: direction, protocol class, control; ports and data types on the SSP copy; SA-9 providers, CA-3 links</div>
    <div class="a"><b>Inherited</b>physical, hypervisor, backbone, resolver, DDoS, edge DNS from the providers; six inherited SSP rows, PE family by note</div>
    <div class="r"><b>Exception</b>one inbound port, break-glass SSH from allowlisted sources; everything else rides a tunnel the host dials out</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html); print("wrote",OUT,"H",H,"crossings",crossings)

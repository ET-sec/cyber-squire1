import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "threat-model.html")
INK="#0a0d0b"; NODE="#141b16"; NSTROKE="#2c3a30"; LINE="#27342b"; LINESOFT="#1b241e"; TEXT="#e6ebe4"; DIM="#a3ada1"; EXT="#4a5a4e"
RED="#ff6b5e"; GREEN="#3dff8b"; BONE="#e8dcc0"; AMBER="#ffc247"
W=206; PITCH=226; X0=28; XC=lambda i: X0+i*PITCH
NY=30; NH=40; W0=122; WP=66; WH=44
def t(x,y,s,size,color,weight=None,anchor="start",ls=None,halo=False):
    a=f' font-weight="{weight}"' if weight else ''
    l=f' letter-spacing="{ls}"' if ls else ''
    h=f' paint-order="stroke" stroke="{INK}" stroke-width="4" stroke-linejoin="round"' if halo else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}"{a}{l} text-anchor="{anchor}"{h}>{s}</text>'
# columns: (node label, starts-with, [walls], tb ticks {slot_after: label}, reaches lines, residual, ids)
# wall = (kind, line1, tag, stride)  kind: p=prevent g=detect
COLS=[
 ("internet scanner","any host, no credential",
  [("p","no origin IP in DNS","EDGE   SC-7","I"),
   ("p","WAF, DDoS absorbed","EDGE   SC-5","D"),
   ("p","no ports, dials out","HOST   SC-7","S"),
   ("p","SSH allowlist only","HOST   SC-7","D")],
  {-1:"TB-1"},
  ["the edge login page and the","public webhook paths, never","the host or its address"],"LOW","D-01  S-05"),
 ("webhook caller","knows a public webhook path",
  [("p","WAF and per-IP limit","EDGE   SC-5","D"),
   ("p","edge auth, 1 carve-out","EDGE   AC-3","S"),
   ("p","token header on Squire","APP   IA-5","S"),
   ("p","typed payload, schema","APP   SI-10","T"),
   ("p","recommend-only actions","APP   AC-6","E"),
   ("g","traced, human on HIGH","APP   AU-12","R")],
  {1:"TB-2, TB-7"},
  ["one forged alert into a","recommend-only pipeline; a","human reads anything HIGH"],"MEDIUM","S-01"),
 ("hostile prompt","attacker text in an alert",
  [("p","PII scrubbed pre-graph","APP   SI-10","I"),
   ("p","jailbreak and PII rail","APP   SI-4","T"),
   ("p","output rail, citations","APP   SI-7","T"),
   ("p","forbidden-verb filter","APP   AC-6","E"),
   ("p","human gate on HIGH","APP   IR-4","E"),
   ("g","spend cap, traced","APP   AU-12","R")],
  {1:"TB-5"},
  ["the allowlist: text advice,","no action executes; 20 cases","fired, 0 bypasses"],"MEDIUM","T-01  I-01"),
 ("compromised container","code running in one service",
  [("p","three bridge networks","RUNTIME   AC-4","E"),
   ("p","no-new-privs, 1 exempt","RUNTIME   CM-7","E"),
   ("p","socket: 2 sensors only","RUNTIME   AC-6","E"),
   ("g","Falco reads the kernel","RUNTIME   SI-4","E"),
   ("p","secrets need a token","IDENTITY   IA-5","I"),
   ("p","DB needs a credential","DATA   AC-3","I")],
  {3:"TB-4"},
  ["its own segment and env;","host escape needs a kernel","zero-day and lands in Falco"],"MEDIUM","E-04  E-01  S-03"),
 ("stolen credential","a password or a laptop",
  [("p","one-time PIN at edge","EDGE   IA-2","S"),
   ("p","second factor on SSH","HOST   IA-2","S"),
   ("p","JIT expires in 4h","IDENTITY   AC-12","E"),
   ("p","quarterly role review","IDENTITY   AC-2","E"),
   ("g","recorded, shipped mTLS","IDENTITY   AU-9","R")],
  {-1:"TB-1",0:"TB-2"},
  ["a recorded session with a","four hour clock; evidence","lands beyond their reach"],"LOW","R-02  E-03"),
 ("poisoned image","a tag nobody here built",
  [("p","digest pinned, Tier 1","DELIVERY   CM-5","T"),
   ("p","reviewed PR to change","DELIVERY   CM-3","T"),
   ("p","scan, SBOM, signature","DELIVERY   RA-5","T"),
   ("p","sealed: no route home","RUNTIME   AC-4","I")],
  {},
  ["a poisoned tag needs a","reviewed PR; a bad runtime","has no route home"],"LOW","T-05  T-03"),
]
svg=[]; a=svg.append
a(f'<defs><marker id="m-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>')
RY=530
for i,(name,starts,walls,ticks,reach,res,ids) in enumerate(COLS):
    x=XC(i); xc=x+W/2; n=len(walls); lastb=W0+(n-1)*WP+WH
    # path behind walls: solid to first wall, dashed residual below
    a(f'<line x1="{xc:g}" y1="{NY+NH}" x2="{xc:g}" y2="{W0-1}" stroke="{RED}" stroke-width="2.5" marker-end="url(#m-red)"/>')
    a(f'<line x1="{xc:g}" y1="{W0+WH}" x2="{xc:g}" y2="{RY-14}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 5" opacity="0.9"/>')
    # attacker node
    a(f'<rect x="{x}" y="{NY}" width="{W}" height="{NH}" rx="5" fill="{NODE}" stroke="{RED}" stroke-width="1.5"/>')
    a(t(xc,NY+25,name,15,TEXT,500,"middle"))
    a(t(xc,NY+NH+17,starts,11.5,DIM,None,"middle",None,True))
    # walls
    for k,(kind,l1,tag,st) in enumerate(walls):
        y=W0+k*WP; col=GREEN if kind=="p" else AMBER
        a(f'<rect x="{x}" y="{y}" width="{W}" height="{WH}" rx="4" fill="{NODE}" stroke="{col}" stroke-width="1.5"/>')
        a(t(x+10,y+17,l1,12.5,TEXT,500))
        a(t(x+10,y+34,tag,11,DIM))
        if st:
            a(f'<rect x="{x+W-27}" y="{y+13}" width="18" height="18" rx="3" fill="none" stroke="{DIM}" stroke-width="1"/>')
            a(t(x+W-18,y+26,st,11,TEXT,700,"middle"))
    # trust boundary ticks
    for k,lab in ticks.items():
        y=(W0-15) if k==-1 else (W0+k*WP+WH+WP-WH)/1 if False else (W0+k*WP+WH+11)
        if k==-1: y=W0-16
        a(f'<line x1="{xc-16:g}" y1="{y:g}" x2="{xc+16:g}" y2="{y:g}" stroke="{BONE}" stroke-width="2"/>')
        a(t(xc+22,y+4,lab,12,BONE,700,"start",None,True))
    # reaches
    a(t(x,RY,"REACHES",11.5,RED,700,"start",2))
    for j,l in enumerate(reach): a(t(x,RY+19+17*j,l,12,DIM))
    cy=RY+68; rc=GREEN if res=="LOW" else AMBER
    a(f'<rect x="{x}" y="{cy}" width="64" height="20" rx="3" fill="none" stroke="{rc}" stroke-width="1.5"/>')
    a(t(x+32,cy+14,res,11,rc,700,"middle"))
    a(t(x+74,cy+14,ids,11,DIM))
# right rail
RX=1400
a(t(RX,48,"BY THE NUMBERS",11,DIM,700,"start",2))
nums=[("29","STRIDE threats across","8 trust boundaries"),("7","attack paths,","4 platform, 3 AI"),("10","AI threats cataloged,","OWASP LLM and ATLAS"),
      ("20","red-team cases fired,","0 bypasses"),("11","pentest findings,","0 critical, 4 accepted"),("0","application ports","open to the internet")]
for j,(n,l1,l2) in enumerate(nums):
    y=84+j*46
    a(t(RX,y,n,24,TEXT,700)); a(t(RX+48,y-11,l1,11.5,DIM)); a(t(RX+48,y+4,l2,11.5,DIM))
a(t(RX,372,"STRIDE",11,DIM,700,"start",2))
for j,(L,w) in enumerate([("S","spoofing"),("T","tampering"),("R","repudiation"),("I","information disclosure"),("D","denial of service"),("E","elevation of privilege")]):
    y=392+j*18; a(t(RX,y,L,11.5,TEXT,700)); a(t(RX+22,y,w,11.5,DIM))
a(t(RX,524,"READING THE PAGE",11,DIM,700,"start",2))
ly=542
a(f'<line x1="{RX}" y1="{ly}" x2="{RX+34}" y2="{ly}" stroke="{RED}" stroke-width="2.5"/>'+t(RX+44,ly+4,"the attack, top to bottom",11.5,DIM))
a(f'<line x1="{RX}" y1="{ly+20}" x2="{RX+34}" y2="{ly+20}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 5"/>'+t(RX+44,ly+24,"what remains after a wall",11.5,DIM))
a(f'<rect x="{RX}" y="{ly+33}" width="34" height="14" rx="3" fill="{NODE}" stroke="{GREEN}" stroke-width="1.5"/>'+t(RX+44,ly+44,"wall that stops it, STRIDE letter",11.5,DIM))
a(f'<rect x="{RX}" y="{ly+53}" width="34" height="14" rx="3" fill="{NODE}" stroke="{AMBER}" stroke-width="1.5"/>'+t(RX+44,ly+64,"sees it, cannot be silenced inside",11.5,DIM))
a(f'<line x1="{RX+4}" y1="{ly+80}" x2="{RX+30}" y2="{ly+80}" stroke="{BONE}" stroke-width="2"/>'+t(RX+44,ly+84,"trust boundary crossed, register ID",11.5,DIM))
a(f'<rect x="{RX}" y="{ly+93}" width="34" height="14" rx="3" fill="none" stroke="{AMBER}" stroke-width="1.5"/>'+t(RX+44,ly+104,"residual after controls, register IDs",11.5,DIM))
H=656
html=f'''<title>CoreDirective Threat Model</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
  :root{{
    --ink:{INK}; --node:{NODE}; --line:{LINE}; --line-soft:{LINESOFT}; --text:{TEXT}; --dim:{DIM};
    --green:{GREEN}; --bone:{BONE}; --amber:{AMBER}; --red:{RED};
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
  figcaption{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px 22px;margin-top:10px;padding-top:10px;border-top:1px solid var(--line-soft);font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:.01em}}
  @media (max-width:1100px){{figcaption{{grid-template-columns:repeat(2,1fr)}}}}
  figcaption b{{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px;font-weight:700}}
  .g b{{color:var(--green)}} .c b{{color:var(--bone)}} .a b{{color:var(--amber)}} .r b{{color:var(--red)}}
</style>

<div class="page">
  <div class="head">
    <h1>CoreDirective reference architecture</h1>
    <p>six attacker positions, the wall that meets each one, and what remains after the walls</p>
    <span class="tag">Threat model</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="Threat model view of the CoreDirective platform. Six attacker positions run as columns, each attack drawn top to bottom, each control drawn as a wall across the column with the layer it lives in, the NIST 800-53 control it satisfies, and the STRIDE category it answers. An internet scanner meets no origin address in DNS, WAF and DDoS absorption at the edge, no published ports because the tunnel dials out, and SSH restricted to an allowlist; it reaches the edge login page and public webhook paths, never the host. A webhook caller meets the WAF and per-IP rate limit, identity checks at the edge with one carve-out, a token header on the agent, a typed schema-checked payload, and a recommend-only action set, with every call traced and a human reading anything rated HIGH. A hostile prompt inside a real alert meets a PII scrub before the graph, a jailbreak and PII input rail, an output rail with a citation guard, a forbidden-verb filter, and a human gate on HIGH and CRITICAL, with a daily spend cap and a trace on every call; it reaches the allowlist, text advice only, twenty red-team cases fired with zero bypasses. A compromised container meets three bridge networks with a sealed AI segment, no-new-privileges with one documented exemption and PID caps, the Docker socket mounted read-only into two sensors and no application container, Falco reading syscalls from the kernel, token-gated secrets, and a credential-gated database; it reaches its own segment and environment. A stolen operator credential meets a one-time PIN at the edge, a second factor on the SSH gateway, just-in-time access that expires in four hours, roles reviewed quarterly, and session recordings shipped off-host over mTLS; it reaches a recorded session with a four hour clock. A poisoned upstream image meets digest pinning on security-boundary images, a reviewed pull request for any change, vulnerability scanning with an SBOM and signature verification, and a sealed segment with no route home. A right rail carries the counts: 29 STRIDE threats across 8 trust boundaries, 7 attack paths, 10 AI threats cataloged, 20 red-team cases with 0 bypasses, 11 pentest findings with 0 critical and 4 accepted with compensating controls, and 0 application ports open to the internet. Residual ratings come from the STRIDE register after controls.">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="g"><b>Method</b>STRIDE per trust boundary, attack trees per AI path, two red-team cycles fired at production</div>
    <div class="c"><b>Reading</b>top to bottom is the attack, each bar is a wall, dashed is what remains, chip is residual after controls</div>
    <div class="a"><b>Detection</b>Falco from the kernel, logins and sessions off-host over mTLS, every model call traced</div>
    <div class="r"><b>Residual</b>MEDIUM carries a named mitigation or acceptance; the one High in the platform register (I-02) is re-rated Moderate by the risk register; reviewed quarterly</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html); print("wrote",OUT,"H",H)

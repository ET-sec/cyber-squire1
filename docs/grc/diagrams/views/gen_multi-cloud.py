import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi-cloud.html")
INK="#0a0d0b"; NODE="#141b16"; NSTROKE="#2c3a30"; LINE="#27342b"; LINESOFT="#1b241e"; TEXT="#e6ebe4"; DIM="#a3ada1"; EXT="#4a5a4e"
RED="#ff6b5e"; GREEN="#3dff8b"; BONE="#e8dcc0"; AMBER="#ffc247"
def fs(l): n=len(l); return 16 if n<=12 else (15 if n<=14 else 14)
def node(x,y,w,label,sub=None,ext=False,stroke=NSTROKE,pitch=None):
    if ext: r=f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="none" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    else:   r=f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="{NODE}" stroke="{stroke}" stroke-width="1.5"/>'
    r+=f'<text x="{x+w/2:g}" y="{y+25}" font-size="{fs(label)}" font-weight="500" fill="{TEXT}" text-anchor="middle">{label}</text>'
    if sub: r+=f'<text x="{x+w/2:g}" y="{y+57}" font-size="11.5" fill="{DIM}" text-anchor="middle">{sub}</text>'
    return r
def lab(x,y,t,c,anchor="middle"): return f'<text x="{x:g}" y="{y}" font-size="11.5" fill="{c}" text-anchor="{anchor}" paint-order="stroke" stroke="{INK}" stroke-width="4" stroke-linejoin="round">{t}</text>'
def arrow(d,c,m,dash=False): return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.5"{" stroke-dasharray=\"6 5\"" if dash else ""} marker-end="url(#m-{m})"/>'
svg=[]; a=svg.append
mk={"red":RED,"green":GREEN,"bone":BONE,"amber":AMBER}
a('<defs>'+''.join(f'<marker id="m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>' for k,v in mk.items())+'</defs>')
PY0,PH=150,460
R=[235,335,435,535]
# planes
planes=[(28,472,"EDGE  CLOUDFLARE","identity, ingress, state","Terraform: cd-cloudflare-edge",GREEN,"rgba(61,255,139,0.03)"),
        (530,630,"RUNTIME  ORACLE CLOUD","compute, data, keys","Terraform: cd-oci-infrastructure",BONE,"rgba(232,220,192,0.03)"),
        (1190,482,"SECURITY  AWS","what must survive the other two","Terraform: cd-aws-security-plane",AMBER,"rgba(255,194,71,0.03)")]
for x,w,t,s1,s2,c,tint in planes:
    a(f'<rect x="{x}" y="{PY0}" width="{w}" height="{PH}" rx="9" fill="{tint}" stroke="{LINE}" stroke-width="2"/>')
    a(f'<text x="{x+18}" y="{PY0+24}" font-size="12" font-weight="700" fill="{c}" letter-spacing="2">{t}</text>')
    a(f'<text x="{x+18}" y="{PY0+41}" font-size="11.5" fill="{DIM}">{s1}</text>')
    a(f'<text x="{x+w-18}" y="{PY0+PH-12}" font-size="11.5" fill="{DIM}" text-anchor="end">{s2}</text>')
# top row principals
a(node(60,30,190,"users, operators"))
a(node(620,30,160,"SIEM",ext=True))
a(node(1080,30,190,"GitHub Actions",ext=True))
a(node(1450,30,190,"operator, Telegram",ext=True))
# EDGE nodes
a(node(60,R[0],190,"Access","OTP, service tokens",stroke=GREEN)); a(node(290,R[0],190,"tunnel edge","host dials out to it",stroke=GREEN))
a(node(60,R[1],190,"WAF, rate limits","managed and custom rules")); a(node(290,R[1],190,"DNS proxy","no origin address"))
a(node(60,R[2],190,"webhook carve-out","Telegram ranges, one path")); a(node(290,R[2],190,"state bucket","Terraform state, versioned"))
# RUNTIME nodes
C=[560,760,960]
a(node(C[0],R[0],150,"hardened host","compose, 19 services",stroke=BONE)); a(node(C[1],R[0],150,"VCN, one port","SSH, allowlisted sources")); a(node(C[2],R[0],150,"identity domain","JWT to token, minutes",stroke=BONE))
a(node(C[0],R[1],150,"backup bucket","retention rule, 30 days")); a(node(C[1],R[1],150,"KMS vault + key","CMK, envelope")); a(node(C[2],R[1],150,"block storage","encrypted, provider key"))
a(node(C[0],R[2],150,"instance identity","writes, cannot delete")); a(node(C[1],R[2],150,"timed restore","monthly, logged"))
# SECURITY nodes
A,B=1220,1450
a(node(A,R[0],190,"OIDC federation","repo and main, 1h max",stroke=BONE)); a(node(B,R[0],190,"break-glass secret","sealed runtime credential",stroke=RED))
a(node(A,R[1],190,"evidence vault","Object Lock, CMK, 30d",stroke=AMBER)); a(node(B,R[1],190,"alert on read","trail to Lambda to Telegram",stroke=AMBER))
a(node(A,R[2],190,"account trail","multi-region, validated")); a(node(B,R[2],190,"region guard","deny outside one region"))
a(node(A,R[3],190,"evidence uploader","write-only, no delete"))
# ARROWS green
a(arrow(f"M230,70 V{R[0]-1}",GREEN,"green")); a(lab(240,112,"one-time PIN, service tokens",GREEN,"start"))
a(arrow(f"M250,{R[0]+20} H289",GREEN,"green"))
a(arrow(f"M560,{R[0]+20} H481",GREEN,"green"))
# bone identity: one JWT, two clouds
a(arrow(f"M1110,70 V120 H1035 V{R[0]-1}",BONE,"bone")); a(lab(1100,112,"signed JWT, main only",BONE,"end"))
a(arrow(f"M1175,70 V{R[0]+20} H1219",BONE,"bone")); a(lab(1185,112,"same JWT, role pinned",BONE,"start"))
# amber evidence and telemetry
a(arrow(f"M710,{R[0]+20} H735 V{R[0]+83} H1205 V{R[1]+20} H1219",AMBER,"amber")); a(lab(970,R[0]+77,"nightly evidence, one way, write-only",AMBER))
a(arrow(f"M700,{R[0]} V71",AMBER,"amber")); a(lab(710,112,"logs, alerts, metrics",AMBER,"start"))
a(arrow(f"M1640,{R[1]+20} H1660 V50 H1641",AMBER,"amber")); a(lab(1555,126,"pages in 2 min",AMBER,"start")); a(lab(1555,141,"caller named",AMBER,"start"))
# red break-glass
a(arrow(f"M1545,70 V{R[0]-1}",RED,"red",True)); a(lab(1535,112,"emergency read only",RED,"end"))
a(arrow(f"M1545,{R[0]+40} V{R[1]-1}",RED,"red",True)); a(lab(1555,R[0]+72,"any read",RED,"start"))
# blast strip
SY=640
strip=[(28,GREEN,["the front door and its policies fall, not the host; revoke the","tunnel token and the host goes dark with its data intact"]),
       (530,BONE,["data and keys live here; the host cannot delete its own backups, and the","evidence copy and the break-glass credential sit with another vendor"]),
       (1190,AMBER,["no automation here reaches the runtime; the uploader can only","add, Object Lock refuses deletes even for root, and every","access lands on a validated trail"])]
for x,c,lines in strip:
    a(f'<text x="{x+18}" y="{SY}" font-size="12" font-weight="700" fill="{c}" letter-spacing="2">IF THIS ACCOUNT FALLS</text>')
    for k,l in enumerate(lines): a(f'<text x="{x+18}" y="{SY+18+16*k}" font-size="11.5" fill="{DIM}">{l}</text>')
# legend
ly=728; x=44
leg=[(GREEN,"request and tunnel path",False),(BONE,"pipeline identity, short-lived",False),(AMBER,"evidence and alerts, one way",False),(RED,"break-glass, alerted on read",True)]
a(f'<g font-size="12" fill="{DIM}">')
for col,t,d in leg:
    a(f'<line x1="{x}" y1="{ly}" x2="{x+40}" y2="{ly}" stroke="{col}" stroke-width="2.5"{" stroke-dasharray=\"6 5\"" if d else ""}/><text x="{x+51}" y="{ly+4}">{t}</text>'); x+=51+round(len(t)*7.2)+40
a(f'<rect x="{x}" y="{ly-7}" width="40" height="15" fill="none" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/><text x="{x+51}" y="{ly+4}">external service</text></g>')
H=750
html=f'''<title>CoreDirective Multi-Cloud Planes</title>
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
    <p>three planes, three vendors, split by blast radius, sanitized, no accounts, regions, or bucket names</p>
    <span class="tag">Multi-cloud planes</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="Multi-cloud planes view of the CoreDirective platform. Three planes on three vendors, split by blast radius. The edge plane on Cloudflare holds Access with one-time PIN and service tokens, WAF and rate limits, the tunnel edge the host dials out to, a DNS proxy with no origin address, one webhook carve-out for Telegram's published ranges, and the versioned Terraform state bucket, kept off the runtime cloud so state and compute never share a failure domain. The runtime plane on Oracle Cloud holds the hardened host with the compose stack, a VCN with one inbound port for SSH from allowlisted sources, an identity domain that trades a GitHub JWT for a token that lives minutes, a backup bucket with a 30 day retention rule, a KMS vault and customer managed key, an instance identity that can write backups but not delete them, block storage encrypted with the provider key, and a monthly timed restore. The security plane on AWS holds OIDC federation pinned to one repo and the main branch, a sealed break-glass credential for the runtime cloud whose every read pages the operator with the caller named, an evidence vault with Object Lock in compliance mode and a customer managed key, a multi-region account trail with log validation, a region guard that denies everything outside one region, and a write-only evidence uploader. What crosses: users enter at the edge and reach the host over a tunnel the host dials out; one GitHub identity federates into both clouds with no stored keys; evidence flows one way from the runtime into the vault nightly; no automation in the security plane reaches back into the runtime.">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="g"><b>Edge</b>identity → filter → tunnel, host dials out, no origin address anywhere</div>
    <div class="c"><b>Identity</b>one GitHub JWT → two clouds, pinned to main, short-lived, read-only, zero stored keys in CI</div>
    <div class="a"><b>Evidence</b>nightly, one way, write-only, Object Lock, survives the runtime cloud</div>
    <div class="r"><b>Break-glass</b>sealed credential in the other cloud, any read → page in 2 min</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html); print("wrote",OUT)

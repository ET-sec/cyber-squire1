import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "identity-access.html")
INK="#0a0d0b"; NODE="#141b16"; NSTROKE="#2c3a30"; LINE="#27342b"; LINESOFT="#1b241e"; TEXT="#e6ebe4"; DIM="#a3ada1"; EXT="#4a5a4e"
RED="#ff6b5e"; GREEN="#3dff8b"; BONE="#e8dcc0"; ORANGE="#ff9b3d"
P_X,P_W=60,190; D_X,D_W=675,200; D1_X,D1_W=600,140; D2_X,D2_W=810,140; R_X,R_W=1180,200; B_X=1410
# tier: (title, subtitle, color, tint, y, rows)
# row: (principal, decisions[(label,ext)], resource, res_ext, labels[p2d, d2d(optional), d2r], principal_ext)
TIERS=[
 dict(t="TIER 0  BREAK-GLASS", sub="static key, source-restricted, last resort, no broker in the path", c=RED, tint="rgba(255,107,94,0.035)", y=44, dash=True,
  rows=[dict(p="allowlisted source", d=[("host sshd",False)], r="host shell", rext=False, pext=False, l=["Ed25519 key, static","root path, no broker"])],
  blast=["whole host, from one source range","Falco sees the session after the fact"]),
 dict(t="TIER 1  OPERATOR", sub="humans, three realm roles: admin, operator, auditor", c=GREEN, tint="rgba(61,255,139,0.03)", y=142, dash=False,
  rows=[dict(p="operator", d=[("Access",False)], r="admin consoles", rext=False, pext=False, l=["email one-time PIN, 24h session","identity checked before origin"]),
        dict(p="operator", d=[("Keycloak",False),("Teleport",False)], r="host SSH, database", rext=False, pext=False, l=["password, lockout on failures","OIDC, 5-min token","TOTP, recorded, JIT 4h"])],
  blast=["consoles until the 24h session ends","SSH recorded, elevation ends at 4h"]),
 dict(t="TIER 2  SERVICE", sub="machines trade one bootstrap secret for a short-lived credential", c=BONE, tint="rgba(232,220,192,0.03)", y=300, dash=False,
  rows=[dict(p="n8n and services", d=[("Vault AppRole",False)], r="Postgres", rext=False, pext=False, l=["role ID and secret ID","dynamic creds, 1h lease"]),
        dict(p="CI runner", d=[("OIDC exchange",False)], r="cloud API", rext=True, pext=False, l=["signed JWT, main branch only","minutes-lived token, read-only"]),
        dict(p="Telegram", d=[("Access bypass",False)], r="one webhook path", rext=False, pext=True, l=["published egress ranges only","chat ID checked, rate limited"])],
  blast=["one database, for one hour","no stored cloud key exists to leak"]),
 dict(t="TIER 3  AGENT", sub="six agent roles in the realm, five-minute tokens, screened on the way out", c=ORANGE, tint="rgba(255,155,61,0.03)", y=518, dash=False,
  rows=[dict(p="alert source", d=[("webhook token",False)], r="Squire", rext=False, pext=True, l=["shared-secret header, rotated","typed payload, schema checked"]),
        dict(p="Squire", d=[("Guardrails",False)], r="Claude API", rext=True, pext=False, l=["no model key in the agent","API key held here, spend cap"]),
        dict(p="Squire", d=[("actions allowlist",False)], r="Telegram notify", rext=True, pext=False, l=["typed actions, deny by default","webhook token, one chat ID"])],
  blast=["an injection reaches the allowlist,","not the operator or cloud planes"]),
]
def fs(l): n=len(l); return 16 if n<=12 else (15 if n<=14 else 14)
def node(x,y,w,label,ext,stroke=NSTROKE):
    if ext: r=f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="none" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    else:   r=f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="{NODE}" stroke="{stroke}" stroke-width="1.5"/>'
    return r+f'<text x="{x+w/2:g}" y="{y+25}" font-size="{fs(label)}" font-weight="500" fill="{TEXT}" text-anchor="middle">{label}</text>'
def label(x,y,t,c): return f'<text x="{x:g}" y="{y}" font-size="11.5" fill="{c}" text-anchor="middle" paint-order="stroke" stroke="{INK}" stroke-width="4" stroke-linejoin="round">{t}</text>'
svg=[]; a=svg.append
mk={"red":RED,"green":GREEN,"bone":BONE,"orange":ORANGE}
a('<defs>'+''.join(f'<marker id="m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>' for k,v in mk.items())+'</defs>')
a(f'<g font-size="12" font-weight="700" letter-spacing="2" fill="{DIM}"><text x="{P_X}" y="24">PRINCIPAL</text><text x="{D_X}" y="24">DECISION POINT</text><text x="{R_X}" y="24">RESOURCE</text><text x="{B_X}" y="24">IF THE CREDENTIAL IS STOLEN</text></g>')
inv={v:k for k,v in mk.items()}
for T in TIERS:
    y=T["y"]; rows=T["rows"]; c=T["c"]; h=30+60*len(rows)-20+18; m=inv[c]; dash=' stroke-dasharray="6 5"' if T["dash"] else ''
    a(f'<!-- ===== {T["t"]} ===== -->')
    a(f'<rect x="28" y="{y}" width="1644" height="{h}" rx="7" fill="{T["tint"]}" stroke="{LINE}" stroke-width="1.5"/>')
    a(f'<text x="44" y="{y+18}" font-size="12" font-weight="700" fill="{c}" letter-spacing="2">{T["t"]}</text>')
    a(f'<text x="{44+round(len(T["t"])*9.2)+18}" y="{y+18}" font-size="11.5" fill="{DIM}">{T["sub"]}</text>')
    for k,r in enumerate(rows):
        top=y+30+60*k; mid=top+20
        a(node(P_X,top,P_W,r["p"],r["pext"]))
        if len(r["d"])==1:
            a(node(D_X,top,D_W,r["d"][0][0],r["d"][0][1],stroke=c)); dl,dr=D_X,D_X+D_W
            a(f'<line x1="{P_X+P_W}" y1="{mid}" x2="{dl-1}" y2="{mid}" stroke="{c}" stroke-width="2.5"{dash} marker-end="url(#m-{m})"/>')
            a(label((P_X+P_W+dl)/2,mid-9,r["l"][0],c))
            a(f'<line x1="{dr}" y1="{mid}" x2="{R_X-1}" y2="{mid}" stroke="{c}" stroke-width="2.5"{dash} marker-end="url(#m-{m})"/>')
            a(label((dr+R_X)/2,mid-9,r["l"][1],c))
        else:
            a(node(D1_X,top,D1_W,r["d"][0][0],r["d"][0][1])); a(node(D2_X,top,D2_W,r["d"][1][0],r["d"][1][1],stroke=c))
            a(f'<line x1="{P_X+P_W}" y1="{mid}" x2="{D1_X-1}" y2="{mid}" stroke="{c}" stroke-width="2.5" marker-end="url(#m-{m})"/>')
            a(label((P_X+P_W+D1_X)/2,mid-9,r["l"][0],c))
            a(f'<line x1="{D1_X+D1_W}" y1="{mid}" x2="{D2_X-1}" y2="{mid}" stroke="{c}" stroke-width="2.5" marker-end="url(#m-{m})"/>')
            a(label((D1_X+D1_W+D2_X)/2,mid+31,r["l"][1],c))
            a(f'<line x1="{D2_X+D2_W}" y1="{mid}" x2="{R_X-1}" y2="{mid}" stroke="{c}" stroke-width="2.5" marker-end="url(#m-{m})"/>')
            a(label((D2_X+D2_W+R_X)/2,mid-9,r["l"][2],c))
        a(node(R_X,top,R_W,r["r"],r["rext"]))
    bm=y+30+20
    a(f'<text x="{B_X}" y="{bm-4}" font-size="11.5" fill="{DIM}">{T["blast"][0]}</text><text x="{B_X}" y="{bm+12}" font-size="11.5" fill="{DIM}">{T["blast"][1]}</text>')
# legend
ly=756
leg=[(RED,"break-glass, static key",True),(GREEN,"human session, MFA",False),(BONE,"machine identity, short-lived",False),(ORANGE,"agent path, screened",False)]
x=44
a(f'<g font-size="12" fill="{DIM}">')
for col,t,d in leg:
    a(f'<line x1="{x}" y1="{ly}" x2="{x+40}" y2="{ly}" stroke="{col}" stroke-width="2.5"{" stroke-dasharray=\"6 5\"" if d else ""}/><text x="{x+51}" y="{ly+4}">{t}</text>'); x+=51+round(len(t)*7.2)+40
a(f'<rect x="{x}" y="{ly-7}" width="40" height="15" fill="none" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/><text x="{x+51}" y="{ly+4}">external service</text></g>')
H=790
html=f'''<title>CoreDirective Identity and Access</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
  :root{{
    --ink:{INK}; --node:{NODE}; --line:{LINE}; --line-soft:{LINESOFT}; --text:{TEXT}; --dim:{DIM};
    --green:{GREEN}; --bone:{BONE}; --orange:{ORANGE}; --red:{RED};
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
  .g b{{color:var(--green)}} .c b{{color:var(--bone)}} .o b{{color:var(--orange)}} .r b{{color:var(--red)}}
</style>

<div class="page">
  <div class="head">
    <h1>CoreDirective reference architecture</h1>
    <p>four privilege tiers, every credential named with its lifetime, sanitized, no addresses, ports, or versions</p>
    <span class="tag">Identity and access</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="Identity and access view of the CoreDirective platform. Four privilege tiers drawn as horizontal bands, each with principals on the left, decision points in the middle, resources on the right, and a note on what a stolen credential reaches. Tier 0, break-glass: an allowlisted source range reaches the host SSH daemon with a static key and lands on the host shell with no broker in the path. Tier 1, operator: humans reach admin consoles through an email one-time PIN with a 24 hour session, and reach host SSH and the database through Keycloak single sign-on into Teleport with TOTP, recorded sessions, and just-in-time elevation that expires after four hours. Tier 2, service: n8n and services fetch dynamic database credentials from Vault by AppRole on a one hour lease; the CI runner trades a signed JWT from the main branch for a cloud token that lives minutes and is read-only; Telegram reaches one webhook path through an Access bypass limited to its published ranges with a chat ID check. Tier 3, agent: alert sources reach Squire with a rotated shared-secret webhook header and a schema-checked payload; Squire reaches the Claude API only through Guardrails, which holds the API key and the spend cap; Squire notifies Telegram through a typed actions allowlist. A perfect prompt injection reaches the allowlist, never the operator or cloud planes.">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="g"><b>Human</b>one-time PIN → consoles, 24h. MFA → recorded SSH, elevation ends at 4h</div>
    <div class="c"><b>Machine</b>AppRole → 1h lease. signed JWT from main → minutes, read-only. no stored cloud key</div>
    <div class="o"><b>Agent</b>secret header in → rails → key held by guardrails → allowlist out, one chat ID</div>
    <div class="r"><b>Break-glass</b>one source range, one key, whole host, watched after the fact</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html); print("wrote",OUT)

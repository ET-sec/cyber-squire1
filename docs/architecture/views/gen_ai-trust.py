import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai-trust.html")
INK="#0a0d0b"; NODE="#141b16"; NSTROKE="#2c3a30"; LINE="#27342b"; LINESOFT="#1b241e"; TEXT="#e6ebe4"; DIM="#a3ada1"; EXT="#4a5a4e"
RED="#ff6b5e"; GREEN="#3dff8b"; BONE="#e8dcc0"; ORANGE="#ff9b3d"; GRAY="#a3ada1"
def t(x,y,s,size,color,weight=None,anchor="start",ls=None,halo=False):
    a=f' font-weight="{weight}"' if weight else ''; l=f' letter-spacing="{ls}"' if ls else ''
    h=f' paint-order="stroke" stroke="{INK}" stroke-width="4" stroke-linejoin="round"' if halo else ''
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}"{a}{l} text-anchor="{anchor}"{h}>{s}</text>'
def node(x,y,w,label,sub=None,stroke=NSTROKE,ext=False):
    r=(f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="none" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/>' if ext
       else f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="5" fill="{NODE}" stroke="{stroke}" stroke-width="1.5"/>')
    fs=15 if len(label)<=14 else 14
    r+=t(x+w/2,y+25,label,fs,TEXT,500,"middle")
    if sub: r+=t(x+w/2,y+57,sub,11.5,DIM,None,"middle",None,True)
    return r
def arrow(d,c,m,dash=False,both=False):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.5"{" stroke-dasharray=\"6 5\"" if dash else ""}{f" marker-start=\"url(#m-{m})\"" if both else ""} marker-end="url(#m-{m})"/>'
svg=[]; a=svg.append; nodes=[]; n=nodes.append
mk={"orange":ORANGE,"green":GREEN,"gray":GRAY}
a('<defs>'+''.join(f'<marker id="m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>' for k,v in mk.items())+'</defs>')
C=[48+180*i for i in range(9)]; NW=150
R1,R2,RB=272,392,580
# zones
a(f'<rect x="28" y="56" width="1644" height="118" rx="9" fill="rgba(232,220,192,0.03)" stroke="{EXT}" stroke-width="1.5" stroke-dasharray="5 4"/>')
a(t(46,78,"VENDOR MODELS, OUTSIDE THE HOST",12,BONE,700,"start",2)); a(t(46,94,"frontier reasoning and classification, embeddings, search; DPA on file for the model and embeddings vendors, terms of service for search",11.5,DIM))
a(t(1654,78,"TRUSTED VENDOR, UNTRUSTED NETWORK PATH",12,DIM,700,"end",2))
a(f'<rect x="28" y="214" width="1644" height="280" rx="9" fill="rgba(255,155,61,0.03)" stroke="{LINE}" stroke-width="2"/>')
a(t(46,236,"NET-CORE, GUARDRAILS IN FRONT OF THE MODEL CALLS",12,ORANGE,700,"start",2)); a(t(46,252,"on host, screened, traced; PII model baked into the image, offline enforced, cannot fetch at runtime",11.5,DIM))
a(f'<rect x="28" y="530" width="1644" height="118" rx="9" fill="rgba(163,173,161,0.04)" stroke="{DIM}" stroke-width="1.5" stroke-dasharray="7 5"/>')
a(t(46,552,"NET-AI, SEALED SEGMENT",12,TEXT,700,"start",2)); a(t(46,568,"local models for anything that touches raw personal data; reached only over the bridge",11.5,DIM))
a(t(1654,552,"ON HOST, NO ROUTE OUT",12,DIM,700,"end",2))
# boundaries
a(f'<line x1="28" y1="196" x2="1672" y2="196" stroke="{BONE}" stroke-width="2" stroke-dasharray="10 6"/>')
a(t(46,191,"HOST BOUNDARY",12,BONE,700,"start",2,True)); a(t(178,191,"five crossings out, each one drawn",11.5,DIM,None,"start",None,True))
a(f'<line x1="28" y1="514" x2="1672" y2="514" stroke="{DIM}" stroke-width="2" stroke-dasharray="10 6"/>')
a(t(46,509,"SEALED BOUNDARY",12,TEXT,700,"start",2,True)); a(t(190,509,"audio never comes back up; only text does",11.5,DIM,None,"start",None,True))
# vendor nodes
V=[(575,"frontier model","three reasoning nodes"),(763,"classifier","one structured call"),(1123,"embeddings","1024-dim vectors"),(1303,"web search","enrich node only")]
for x,l,s in V: n(node(x,112,160,l,s,ext=True))
# row 1
n(node(C[0],R1,NW,"alert payload","DC-1, attacker text",stroke=ORANGE))
n(node(C[1],R1,NW,"token, schema","shared secret, typed"))
n(node(C[2],R1,NW,"PII scrub","regex before the graph"))
n(node(C[3],R1,NW,"input rail","NER PII, second pass"))
n(node(C[4],R1,NW,"model egress","daily cap, traced",stroke=ORANGE))
n(node(C[6],R1,NW,"embed","chunks, alert queries",stroke=ORANGE))
n(node(C[7],R1,NW,"enrich","IoCs and rule name",stroke=ORANGE))
n(node(C[8],R1,NW,"voice note","operator audio in",stroke=ORANGE))
# row 2
n(node(C[0],R2,NW,"operator","reads, decides, acts",stroke=GREEN))
n(node(C[1],R2,NW,"notify","chat ID checked"))
n(node(C[2],R2,NW,"human gate","HIGH and CRITICAL wait",stroke=GREEN))
n(node(C[3],R2,NW,"allowlist","recommend only"))
n(node(C[4],R2,NW,"output checks","PII, citations, verbs"))
n(node(C[6],R2,NW,"vector store","bridge-only Postgres"))
n(node(C[7],R2,NW,"transcript","text out, audio stays"))
# bottom
n(node(C[5],RB,NW,"local LLM","no internet route"))
n(node(C[8],RB,NW,"speech to text","no internet route"))
# arrows row 1
for i in range(4): a(arrow(f"M{C[i]+NW},{R1+20} H{C[i+1]-1}",ORANGE,"orange"))
cx=lambda i: C[i]+NW/2
a(arrow(f"M{cx(4):g},{R1-1} V153",ORANGE,"orange",both=True))
a(arrow(f"M{C[4]+32},{R1-1} V240 H655 V153",ORANGE,"orange",both=True))
a(t(858,229,"prompt up, completion down",11.5,ORANGE,None,"start",None,True))
a(arrow(f"M{cx(4):g},{R1+41} V{R2-1}",ORANGE,"orange")); a(t(858,357,"completion",11.5,ORANGE,None,"start",None,True))
a(arrow(f"M{C[4]+NW},{R1+20} H{cx(5):g} V{RB-1}",ORANGE,"orange",dash=True,both=True)); a(t(cx(5)+14,487,"fallback when the cap trips",11.5,ORANGE,None,"start",None,True))
a(arrow(f"M{cx(6):g},{R1-1} V153",ORANGE,"orange",both=True)); a(t(1217,229,"text up, vectors down",11.5,ORANGE,None,"start",None,True))
a(arrow(f"M{cx(6):g},{R1+41} V{R2-1}",GRAY,"gray")); a(t(1217,357,"vectors, DC-4",11.5,DIM,None,"start",None,True))
a(arrow(f"M{cx(7):g},{R1-1} V153",ORANGE,"orange",both=True)); a(t(1397,229,"terms up, results down",11.5,ORANGE,None,"start",None,True))
a(arrow(f"M{cx(8):g},{R1+41} V{RB-1}",ORANGE,"orange")); a(t(cx(8)-14,472,"audio, never leaves",11.5,ORANGE,None,"end",None,True))
a(arrow(f"M{C[8]},{RB+20} H{cx(7):g} V{R2+41}",GRAY,"gray")); a(t(cx(7)-14,484,"text only",11.5,DIM,None,"end",None,True))
# row 2 arrows, right to left
a(arrow(f"M{C[4]-1},{R2+20} H{C[3]+NW+1}",ORANGE,"orange"))
a(arrow(f"M{C[3]-1},{R2+20} H{C[2]+NW+1}",ORANGE,"orange"))
a(arrow(f"M{C[2]-1},{R2+20} H{C[1]+NW+1}",GREEN,"green"))
a(arrow(f"M{C[1]-1},{R2+20} H{C[0]+NW+1}",GREEN,"green"))
# legend
lx,ly=700,550
leg=[(ORANGE,"AI path, screened first",False),(ORANGE,"fallback, sealed segment",True),(GREEN,"human path, closes the loop",False),(GRAY,"data at rest, on host",False),(BONE,"trust boundary",True)]
a(f'<rect x="{lx}" y="{ly+85-7}" width="34" height="14" rx="4" fill="{NODE}" stroke="{ORANGE}" stroke-width="1.5"/>'+t(lx+44,ly+85+4,"orange box: data leaves here",11.5,DIM))
for j,(c,s,d) in enumerate(leg):
    y=ly+17*j
    a(f'<line x1="{lx}" y1="{y}" x2="{lx+34}" y2="{y}" stroke="{c}" stroke-width="2.5"{" stroke-dasharray=\"6 5\"" if d else ""}/>'+t(lx+44,y+4,s,11.5,DIM))

# OWASP Top 10 for LLM Applications 2026 (LLM) and Top 10 for Agentic Applications 2026 (ASI) tags under the screens
def chip(i,row,ids,dx=0):
    x=C[i]+NW/2+dx; y=row+72; w=len(ids)*7.2+18
    return (f'<rect x="{x-w/2:g}" y="{y-12}" width="{w:g}" height="17" rx="3" fill="none" stroke="{ORANGE}" stroke-width="1"/>'
            +t(x,y,ids,11.5,ORANGE,700,"middle"))
for i,row,ids,dx in [(2,R1,"LLM02",0),(3,R1,"LLM01, ASI01",0),(4,R1,"LLM06",-44),(4,R2,"LLM10, LLM07",0),(3,R2,"LLM03, ASI02",0),(2,R2,"LLM03, ASI09",0),(6,R2,"LLM09, ASI06",0)]:
    n(chip(i,row,ids,dx))
a(chr(10).join(nodes))
H=664
html=f'''<title>CoreDirective AI Trust</title>
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
  .g b{{color:var(--green)}} .o b{{color:var(--orange)}} .c b{{color:var(--bone)}} .d b{{color:var(--dim)}}
</style>

<div class="page">
  <div class="head">
    <h1>CoreDirective reference architecture</h1>
    <p>five models, one search API, three trust levels; every crossing out of the host drawn with what stands in front of it</p>
    <span class="tag">AI trust</span>
  </div>

  <figure>
  <svg viewBox="0 0 1700 {H}" role="img" aria-label="AI trust view of the CoreDirective platform. Three trust levels drawn as bands. Outside the host, vendor models: a frontier model for the three reasoning nodes, a classifier for one structured call, an embeddings model, and a web search API; a data processing agreement is on file for the model and embeddings vendors, terms of service for search. A host boundary line separates them; five crossings go out, each one drawn: the prompt, alert queries and corpus chunks to the embeddings model, search terms, and a text notification. Inside net-core, guardrails stand in front of the model calls, with the PII model baked into the guardrails image and offline enforced: an alert payload, attacker-influenced by definition, passes a shared-secret token check and typed schema, a regex PII scrub before the graph, and an input rail with NER PII detection as a second pass, then reaches the model egress point with a daily spend cap and a trace on every call. The completion returns through output checks for PII, citations, and verbs, a recommend-only allowlist, and a human gate where HIGH and CRITICAL findings wait, then a notification with the chat ID checked reaches the operator, who reads, decides, and acts. The embed step sends corpus chunks at ingest and alert queries per run to the embeddings model and stores vectors in a bridge-only Postgres. The enrich node sends indicators and the rule name to web search. A voice note from the operator goes down to speech to text on the sealed segment; the audio never comes back up, only the transcript does. Below a sealed boundary, net-ai holds a local LLM used as fallback when the spend cap trips and the speech to text model, both with no internet route. Tags under the screens are the OWASP Top 10 for LLM Applications 2026 (LLM) and the OWASP Top 10 for Agentic Applications 2026 (ASI).">
{chr(10).join("    "+s for s in svg)}
  </svg>

  <figcaption>
    <div class="o"><b>Screened</b>regex and NER PII before the model; citation guard and verb rewrite after; daily spend cap; every call traced; tags are the OWASP Top 10 for LLM Applications 2026 (LLM) and for Agentic Applications 2026 (ASI)</div>
    <div class="c"><b>Crossings</b>prompt, alert queries, chunks, search terms, notification go out; audio never does; DPA for the model and embeddings vendors, terms of service for search</div>
    <div class="g"><b>Human</b>nothing acts on its own; HIGH and CRITICAL wait for a person; the operator closes the loop</div>
    <div class="d"><b>Sealed</b>raw personal data stays on a segment with no internet route; the fallback keeps working with the vendor gone</div>
  </figcaption>
  </figure>
</div>
'''
open(OUT,"w",encoding="utf-8").write(html); print("wrote",OUT,"H",H)

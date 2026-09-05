#!/usr/bin/env python3
"""sync_views.py: publish the architecture views into the portfolio site.

Source of truth: docs/architecture/views/<slug>.html (listed in views.yaml), plus an optional node table per view at
docs/architecture/views/nodes/<slug>.yaml (what each box is, its 800-53 controls, its status today, the files that prove it).
Targets in the portfolio repo:
  views/<slug>.html                 standalone page (viewport, CSP, back link, packet flow, node panel)
  index.html  <!-- VIEW:slug -->...<!-- /VIEW -->      inline figure (svg, node data, caption)
  index.html  /* NODES:css */ ... /* /NODES:css */     node panel styles (inside the first <style>)
  index.html  // NODES:js ... // /NODES:js             node panel script (inside the last <script>)

A node table is validated before anything is written: every control id must have a row in SSP section 5, every evidence
path must be tracked on main, every label must appear exactly once as a <text> in the SVG, status must be live, partial,
or designed. The SSP row (name, status, line) is attached to each control at sync time, never typed by hand.
An entry may say `from: <slug>/<id>` to inherit every field from another table's entry and override some (label and zone
at least). A table may carry `chips: {zone: ...}`: every box whose label is a control id then gets a generated entry from
its SSP row (name, status, implementation text) and every occurrence on the drawing is wrapped.

Usage:
  python3 scripts/sync_views.py            # dry run, report drift
  python3 scripts/sync_views.py --apply    # write targets
  python3 scripts/sync_views.py --check    # exit 1 on drift (CI)
Options: --portfolio PATH (default ~/portfolio)
"""
import argparse, html, json, os, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
VIEWS = ROOT / "docs" / "architecture" / "views"
NODES = VIEWS / "nodes"
SSP = ROOT / "docs" / "grc" / "SSP_SYSTEM_SECURITY_PLAN.md"
STATUS = {"live": "Live", "partial": "Partial", "designed": "Designed"}
HINT = "Click a box for what it is, the controls it carries, its status today, and the file that proves it."
FLOW_CSS = """.cd-packet { pointer-events: none; opacity: .9; stroke-dashoffset: var(--cdlen); }
@keyframes cdpacket { to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) { .cd-packet { display: none; } }"""
FLOW_JS = """// ANIMATED FLOW: packets ride every arrow in the architecture views
(function() {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.cd-view-frame svg, figure > svg').forEach(function(svg) {
    svg.querySelectorAll('line[marker-end], path[marker-end], polyline[marker-end]').forEach(function(el, i) {
      var len = el.getTotalLength ? el.getTotalLength() : 0; if (!len || len < 24) return;
      var c = el.cloneNode(false);
      ['marker-end', 'marker-start', 'stroke-dasharray', 'id'].forEach(function(a) { c.removeAttribute(a); });
      c.setAttribute('class', 'cd-packet');
      c.setAttribute('stroke-width', String(parseFloat(el.getAttribute('stroke-width') || '1.5') + 1.2));
      c.setAttribute('stroke-linecap', 'round');
      c.setAttribute('stroke-dasharray', '5 ' + Math.ceil(len + 5));
      c.style.setProperty('--cdlen', String(Math.ceil(len + 10)));
      c.style.animation = 'cdpacket ' + Math.max(1.8, len / 80).toFixed(2) + 's linear ' + (-(i % 9) * 0.4).toFixed(2) + 's infinite';
      el.parentNode.insertBefore(c, el.nextSibling);
    });
  });
})();"""
NODES_CSS = """.cd-node { cursor: pointer; outline: none; }
.cd-node rect { pointer-events: all; transition: stroke .15s, stroke-width .15s; }
.cd-node:hover rect, .cd-node:focus-visible rect, .cd-node.active rect { stroke: #3dff8b; stroke-width: 3; }
.cd-view-hint { flex-basis: 100%; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #e8dcc0; }
.cd-node-panel { display: none; position: fixed; top: var(--cd-panel-top, 84px); right: 16px; bottom: 16px; width: min(420px, calc(100vw - 32px)); overflow: auto; z-index: 900; background: #0a0d0b; border: 1px solid #3dff8b; padding: 16px 20px 20px; color: #e6ebe4; font-family: 'IBM Plex Sans', sans-serif; font-size: 14px; line-height: 1.55; }
.cd-node-panel.open { display: block; }
.cd-node-panel.left { right: auto; left: 16px; }
.cd-node-bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
.cd-node-zone { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: #a3ada1; }
.cd-node-close { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #3dff8b; background: none; border: 1px solid #27342b; padding: 4px 10px; cursor: pointer; }
.cd-node-close:hover, .cd-node-close:focus-visible { border-color: #3dff8b; outline: none; }
.cd-node-title { font-family: 'IBM Plex Sans', sans-serif; font-size: 20px; font-weight: 600; margin: 0 0 8px; color: #e6ebe4; line-height: 1.25; }
.cd-node-what { margin: 0 0 14px; color: #e6ebe4; }
.cd-node-status { display: grid; grid-template-columns: auto 1fr; gap: 4px 8px; align-items: center; margin: 0 0 14px; padding: 10px 12px; border: 1px solid #27342b; }
.cd-node-status b { font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: #e6ebe4; }
.cd-node-dot { width: 9px; height: 9px; border-radius: 50%; background: #a3ada1; display: inline-block; }
.cd-node-dot.live, .cd-node-dot.implemented { background: #3dff8b; } .cd-node-dot.partial, .cd-node-dot.partially-implemented { background: #ffc247; } .cd-node-dot.designed, .cd-node-dot.planned { background: #e8dcc0; }
.cd-node-status .cd-node-note { grid-column: 1 / -1; color: #a3ada1; font-size: 13px; }
.cd-node-panel h5 { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: #a3ada1; margin: 14px 0 6px; font-weight: 700; }
.cd-node-panel ul { list-style: none; margin: 0; padding: 0; }
.cd-node-panel li { padding: 5px 0; border-top: 1px solid #1b241e; font-size: 13px; }
.cd-node-panel a { color: #3dff8b; text-decoration: none; } .cd-node-panel a:hover, .cd-node-panel a:focus-visible { text-decoration: underline; }
.cd-node-id { font-family: 'JetBrains Mono', monospace; font-weight: 700; margin-right: 6px; }
.cd-node-controls em { display: block; font-style: normal; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a3ada1; }
.cd-node-path { display: block; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #a3ada1; word-break: break-all; }
html.light .cd-node-panel { background: #0a0d0b; color: #e6ebe4; } html.light .cd-node-panel a { color: #3dff8b; } html.light .cd-node-title, html.light .cd-node-what, html.light .cd-node-status b { color: #e6ebe4; } html.light .cd-view-hint { color: #e8dcc0; }
@media (max-width: 900px) { .cd-node-panel, .cd-node-panel.left { top: auto; right: 0; left: 0; bottom: 0; width: auto; max-height: 62vh; border-width: 1px 0 0; padding: 14px 16px 18px; } }"""
NODES_JS = """// NODE PANEL: click a box on a view for what it is, its controls, its status today, and the file that proves it
(function() {
  var REPO = 'https://github.com/ET-sec/cyber-squire1/blob/main/', SSP = REPO + 'docs/grc/SSP_SYSTEM_SECURITY_PLAN.md';
  var LABEL = { live: 'Live', partial: 'Partial', designed: 'Designed' };
  var panel = null, parts = null, active = null;
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function link(href, text, cls) { var a = el('a', cls, text); a.href = href; a.target = '_blank'; a.rel = 'noopener'; return a; }
  function anchor(line) { var s = String(line).split('-'); return '#L' + s[0] + (s[1] ? '-L' + s[1] : ''); }
  function build() {
    panel = el('aside', 'cd-node-panel'); panel.id = 'cd-node-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-labelledby', 'cd-node-title');
    var bar = el('div', 'cd-node-bar'), zone = el('span', 'cd-node-zone'), close = el('button', 'cd-node-close', 'Close');
    close.type = 'button'; close.setAttribute('aria-label', 'Close details'); bar.appendChild(zone); bar.appendChild(close);
    var title = el('h4', 'cd-node-title'); title.id = 'cd-node-title';
    var what = el('p', 'cd-node-what');
    var status = el('div', 'cd-node-status'), dot = el('span', 'cd-node-dot'), slabel = el('b'), note = el('span', 'cd-node-note');
    status.appendChild(dot); status.appendChild(slabel); status.appendChild(note);
    var controls = el('ul', 'cd-node-controls'), evidence = el('ul', 'cd-node-evidence'), hc = el('h5', null, 'Controls');
    [bar, title, what, status, hc, controls, el('h5', null, 'Evidence'), evidence].forEach(function(n) { panel.appendChild(n); });
    parts = { zone: zone, title: title, what: what, dot: dot, slabel: slabel, note: note, controls: controls, hc: hc, evidence: evidence, close: close };
    close.addEventListener('click', hide);
    document.body.appendChild(panel);
  }
  function show(node, g) {
    if (!panel) build();
    parts.zone.textContent = node.zone; parts.title.textContent = node.title || node.label; parts.what.textContent = node.what;
    parts.dot.className = 'cd-node-dot ' + node.status; parts.slabel.textContent = node.status_label || LABEL[node.status] || node.status; parts.note.textContent = node.status_note;
    parts.controls.textContent = ''; parts.hc.style.display = node.controls.length ? '' : 'none';
    node.controls.forEach(function(c) {
      var li = el('li'); li.appendChild(link(SSP + '#L' + c.line, c.id, 'cd-node-id')); li.appendChild(el('span', null, c.name)); li.appendChild(el('em', null, 'SSP: ' + c.status)); parts.controls.appendChild(li);
    });
    parts.evidence.textContent = '';
    node.evidence.forEach(function(e) {
      var li = el('li'); li.appendChild(link(REPO + e.path + anchor(e.line), e.label)); li.appendChild(el('span', 'cd-node-path', e.path + ':' + e.line)); parts.evidence.appendChild(li);
    });
    if (active) active.classList.remove('active');
    // open on the side away from the box, so the box and its neighbours stay visible
    var r = g.getBoundingClientRect(); panel.classList.toggle('left', (r.left + r.width / 2) > window.innerWidth / 2);
    active = g; g.classList.add('active'); panel.classList.add('open'); parts.close.focus();
  }
  function hide() {
    if (!panel || !panel.classList.contains('open')) return;
    panel.classList.remove('open'); var g = active; if (g) g.classList.remove('active'); active = null; if (g && g.focus) g.focus();
  }
  document.querySelectorAll('script[type="application/json"][id^="cd-nodes-"]').forEach(function(s) {
    var data; try { data = JSON.parse(s.textContent); } catch (e) { return; }
    var fig = s.closest('figure'); if (!fig) return;
    var byId = {}; data.forEach(function(n) { byId[n.id] = n; });
    fig.querySelectorAll('.cd-node').forEach(function(g) {
      var n = byId[g.getAttribute('data-node')]; if (!n) return;
      function toggle(e) { e.preventDefault(); e.stopPropagation(); if (active === g) hide(); else show(n, g); }
      g.addEventListener('click', toggle);
      g.addEventListener('keydown', function(e) { if (e.key === 'Enter' || e.key === ' ') toggle(e); });
    });
  });
  document.addEventListener('keydown', function(e) { if (e.key === 'Escape') hide(); });
  document.addEventListener('click', function(e) { if (panel && panel.classList.contains('open') && !panel.contains(e.target) && !(active && active.contains(e.target))) hide(); });
})();"""
CSP = ("default-src 'self'; script-src 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; base-uri 'none';")

def manifest():
    views, cur = [], None
    for line in (VIEWS / "views.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*slug:\s*(\S+)", line)
        if m:
            cur = {"slug": m.group(1)}; views.append(cur); continue
        m = re.match(r"^\s+(title|generator|section):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    for v in views:
        assert {"title", "generator"} <= v.keys(), f"views.yaml: {v['slug']} is missing title or generator"
    return [(v["slug"], v["title"]) for v in views]

def parse(slug):
    src = (VIEWS / f"{slug}.html").read_text(encoding="utf-8")
    assert "</style>" in src and "<title>" in src and 'class="tag"' in src, f"{slug}.html: missing head anchors"
    head_end = src.index("</style>") + len("</style>")
    head, body = src[:head_end], src[head_end:]
    m_sub = re.search(r'<div class="head">.*?<p>(.*?)</p>', body, re.S); assert m_sub, f"{slug}.html: no head subtitle"
    m_svg = re.search(r"<svg.*?</svg>", body, re.S); assert m_svg, f"{slug}.html: no <svg>"
    m_cap = re.search(r"<figcaption>(.*?)</figcaption>", body, re.S); assert m_cap, f"{slug}.html: no <figcaption>"
    return head, body, m_sub.group(1).strip(), m_svg.group(0), m_cap.group(1).strip()

# ---- node tables ----
def ssp_rows():
    rows, inside = {}, False
    for n, line in enumerate(SSP.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## 5."): inside = True
        elif line.startswith("## 6."): break
        elif inside:
            m = re.match(r"^\| \**([A-Z]{2}-\d+(?:\(\d+\))?)\**\s*\| ([^|]+?)\s*\| ([^|]+?)\s*\|\s*([^|]*?)\s*\|", line)
            if m: rows[m.group(1)] = {"name": m.group(2), "status": m.group(3), "line": n, "text": m.group(4).replace("`", "")}
    assert len(rows) > 100, f"SSP section 5 parsed {len(rows)} rows, expected the full control table"
    return rows

def tracked():
    return set(subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n"))

def read_table(slug):
    import yaml
    return yaml.safe_load((NODES / f"{slug}.yaml").read_text(encoding="utf-8"))

def resolve_from(n, slug, cache):
    """Merge an entry over the entry it names in `from: <slug>/<id>`; local fields win."""
    ref = n.get("from")
    if not ref: return n
    src_slug, _, src_id = ref.partition("/")
    if src_slug not in cache: cache[src_slug] = {e["id"]: e for e in read_table(src_slug)["nodes"]}
    base = cache[src_slug].get(src_id)
    if base is None: raise SystemExit(f"nodes/{slug}.yaml: {n.get('id')}: from {ref!r} not found")
    base = resolve_from(base, src_slug, cache)
    merged = dict(base); merged.update({k: v for k, v in n.items() if k != "from"}); return merged

def chip_entries(svg, rows, chips):
    """One generated entry per control id printed as a box label on the drawing, straight from its SSP row."""
    out = []
    for cid in sorted({t for t in re.findall(r"<text\b[^>]*>([^<]*)</text>", svg) if t in rows}, key=lambda c: (c[:2], int(re.search(r"\d+", c).group()), c)):
        r = rows[cid]; status = re.sub(r"[^a-z]+", "-", r["status"].lower()).strip("-")
        out.append({"id": f"ctl-{cid}", "label": cid, "title": f"{cid} {r['name']}", "zone": chips.get("zone", "NIST 800-53 Rev 5"), "chip": True,
                    "what": r["text"] or r["name"],
                    "status": status, "status_label": r["status"], "status_note": chips.get("note", "Status as recorded in the System Security Plan, section 5; open items sit on the POA&M."),
                    "controls": [], "evidence": [{"label": f"SSP row {cid}", "path": "docs/grc/SSP_SYSTEM_SECURITY_PLAN.md", "line": r["line"]}]})
    return out

def load_nodes(slug, svg):
    f = NODES / f"{slug}.yaml"
    if not f.exists(): return None, None
    table = read_table(f.stem); cache = {}
    nodes = [resolve_from(n, slug, cache) for n in table["nodes"]]
    rows, repo, errs, seen = ssp_rows(), tracked(), [], set()
    for n in nodes:
        nid = n.get("id", "?")
        missing = {"id", "label", "zone", "what", "controls", "status", "status_note", "evidence"} - set(n)
        if missing: errs.append(f"{nid}: missing {sorted(missing)}"); continue
        if n["status"] not in STATUS: errs.append(f"{nid}: status {n['status']!r} not in {sorted(STATUS)}")
        if nid in seen: errs.append(f"{nid}: duplicate id")
        seen.add(nid)
        for c in n["controls"]:
            if c not in rows: errs.append(f"{nid}: control {c} has no row in SSP section 5")
        for e in n["evidence"]:
            if e.get("path") not in repo: errs.append(f"{nid}: evidence path {e.get('path')} is not tracked on main")
            if not re.fullmatch(r"\d+(-\d+)?", str(e.get("line", ""))): errs.append(f"{nid}: evidence line {e.get('line')!r} must be N or N-M")
        k = svg.count(">" + html.escape(n["label"], quote=False) + "</text>")
        if k != 1: errs.append(f"{nid}: label {n['label']!r} appears {k} times as a <text> in the SVG, need exactly 1")
    if errs:
        print(f"nodes/{slug}.yaml: {len(errs)} problem(s)\n  " + "\n  ".join(errs), file=sys.stderr); sys.exit(2)
    if table.get("chips"): nodes += chip_entries(svg, rows, table["chips"])
    return nodes, rows

def inject_nodes(svg, nodes):
    for n in nodes:
        lab = re.escape(html.escape(n["label"], quote=False))
        open_tag = (f'<g class="cd-node" data-node="{n["id"]}" tabindex="0" role="button" '
                    f'aria-label="{html.escape(n["label"])}: details">')
        # the box is the rect plus its label; a dim sub-label that immediately follows the label joins the group so a
        # click anywhere on the box opens the panel (the topology keeps its sub-labels in separate groups, unaffected)
        pat = re.compile(rf'(<rect\b[^>]*/>)(\s*)(<text\b[^>]*>{lab}</text>(?:\s*<text\b[^>]*font-size="11(?:\.5)?"[^>]*>[^<]*</text>)?|<g text-anchor="middle">\s*<text\b[^>]*>{lab}</text>.*?</g>)', re.S)
        svg, k = pat.subn(lambda m: open_tag + m.group(1) + m.group(2) + m.group(3) + "</g>", svg, count=0 if n.get("chip") else 1)
        assert k >= 1, f"node {n['id']}: no rect followed by the label {n['label']!r} in the SVG"
    return svg

def nodes_json(slug, nodes, rows):
    data = [{"id": n["id"], "label": n["label"], "title": n.get("title", ""), "zone": n["zone"], "what": n["what"], "status": n["status"], "status_label": n.get("status_label", ""), "status_note": n["status_note"],
             "controls": [{"id": c, "name": rows[c]["name"], "status": rows[c]["status"], "line": rows[c]["line"]} for c in n["controls"]],
             "evidence": [{"label": e["label"], "path": e["path"], "line": str(e["line"])} for e in n["evidence"]]} for n in nodes]
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="cd-nodes-{slug}">{js}</script>'

# ---- targets ----
def standalone(slug, title, head, body, node_block):
    head = head.replace("<title>", '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
                        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">\n<link rel="icon" href="../favicon.svg">\n<title>', 1)
    extra = ("\n  .head .back{margin-left:18px;font-family:var(--mono);font-size:12px;color:var(--green);text-decoration:none;letter-spacing:.02em;display:inline-block;padding:12px 0}"
             "\n  .head .back:hover{text-decoration:underline}"
             "\n  @media (max-width:900px){svg{max-height:none;min-width:1100px} figure{overflow-x:auto;-webkit-overflow-scrolling:touch} .head{gap:6px 14px} .head p::after{content:\". Scroll sideways to see the whole drawing.\";color:var(--bone)}}"
             "\n  @media (max-width:600px){figcaption{grid-template-columns:1fr}}\n")
    if node_block: extra += "  body{--cd-panel-top:16px}\n" + NODES_CSS + "\n"
    head = head.replace("</style>", extra + FLOW_CSS + "\n</style>")
    body = re.sub(r'(<span class="tag">[^<]*</span>)', r'\1<a class="back" href="../#view-' + slug + '">Back to portfolio</a>', body, count=1)
    if node_block:
        body = body.replace('Back to portfolio</a>', 'Back to portfolio</a><span class="cd-view-hint">' + HINT + '</span>', 1)
        body = body.replace("<figcaption>", node_block + "\n  <figcaption>", 1)
    js = FLOW_JS + ("\n" + NODES_JS if node_block else "")
    return f'<!doctype html>\n<html lang="en">\n<head>\n{head}\n</head>\n<body>{body}\n<script>\n{js}\n</script>\n</body>\n</html>\n'

def figure(slug, title, sub, svg, cap, node_block):
    href = f"views/{slug}.html"
    sub_clean = re.sub(r",?\s*sanitized,\s*no [a-z, ]+$", "", sub)
    # six views share marker ids (m-green, m-red, ...); prefix per view so one page holds them all
    svg = svg.replace('id="m-', f'id="m-{slug}-').replace('url(#m-', f'url(#m-{slug}-')
    hint = f'<span class="cd-view-hint">{HINT}</span>' if node_block else ""
    # with clickable nodes the frame is a plain block; the "Open full view" link in the head still reaches the standalone page
    frame_open = ('<div class="cd-view-frame">' if node_block else
                  f'<a class="cd-view-frame" href="{href}" aria-label="Open the {html.escape(title.lower())} view full size">')
    frame_close = "</div>" if node_block else "</a>"
    data = ("\n" + node_block) if node_block else ""
    return (f'<!-- VIEW:{slug} -->\n<figure class="cd-view" id="view-{slug}">\n'
            f'  <div class="cd-view-head"><h3 class="cd-view-title">{html.escape(title)}</h3>'
            f'<span class="cd-view-sub">{sub_clean}</span>'
            f'<a class="cd-view-open" href="{href}">Open full view</a>{hint}</div>\n'
            f'  {frame_open}\n{svg}\n  {frame_close}{data}\n'
            f'  <figcaption class="cd-view-cap">\n{cap}\n  </figcaption>\n</figure>\n<!-- /VIEW -->')

def sync_marked(site, start, end, content, label):
    i, j = site.find(start), site.find(end)
    if i < 0 or j < 0 or j < i:
        print(f"missing marker in index.html: {label}"); return site, 1
    cur, new = site[i + len(start):j], "\n" + content + "\n"
    if cur == new: return site, 0
    print(f"drift: index.html {label}"); return site[:i + len(start)] + new + site[j:], 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--portfolio", default=os.path.expanduser("~/portfolio"))
    a = ap.parse_args()
    pf = pathlib.Path(a.portfolio); index = pf / "index.html"
    views = manifest()
    missing = [slug for slug, _ in views if not (VIEWS / f"{slug}.html").exists()]
    if missing or not index.exists():
        print(f"config error: missing rendered view(s) {missing} or index {index}", file=sys.stderr); sys.exit(2)
    if a.check: a.apply = False
    site = index.read_text(encoding="utf-8"); drift = 0; any_nodes = False
    if a.apply: (pf / "views").mkdir(exist_ok=True)
    for slug, title in views:
        head, body, sub, svg, cap = parse(slug)
        nodes, rows = load_nodes(slug, svg); node_block = None
        if nodes:
            any_nodes = True
            svg_nodes = inject_nodes(svg, nodes); body = body.replace(svg, svg_nodes, 1); svg = svg_nodes
            node_block = nodes_json(slug, nodes, rows)
            print(f"nodes: {slug} {len(nodes)} boxes, {sum(len(n['controls']) for n in nodes)} control refs, {sum(len(n['evidence']) for n in nodes)} evidence links")
        page = standalone(slug, title, head, body, node_block); target = pf / "views" / f"{slug}.html"
        if not target.exists() or target.read_text(encoding="utf-8") != page:
            drift += 1; print(f"drift: views/{slug}.html")
            if a.apply: target.write_text(page, encoding="utf-8")
        block = figure(slug, title, sub, svg, cap, node_block)
        pat = re.compile(rf"<!-- VIEW:{re.escape(slug)} -->.*?<!-- /VIEW -->", re.S)
        m = pat.search(site)
        if not m:
            print(f"missing marker in index.html: <!-- VIEW:{slug} -->"); drift += 1; continue
        if m.group(0) != block:
            drift += 1; print(f"drift: index.html VIEW:{slug}")
            site = site[:m.start()] + block + site[m.end():]
    if any_nodes:
        site, d1 = sync_marked(site, "/* NODES:css */", "/* /NODES:css */", NODES_CSS, "NODES:css"); drift += d1
        site, d2 = sync_marked(site, "// NODES:js", "// /NODES:js", NODES_JS, "NODES:js"); drift += d2
    if a.apply and site != index.read_text(encoding="utf-8"):
        index.write_text(site, encoding="utf-8")
    print(f"summary: {len(views)} views, {drift} drift(s){' written' if a.apply else ''}")
    if a.check and drift: sys.exit(1)

if __name__ == "__main__":
    main()

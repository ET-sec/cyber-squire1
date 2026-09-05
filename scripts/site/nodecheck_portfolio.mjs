// Node panel QC: 31 clickable boxes on the topology, panel opens on click and on Enter, closes on Escape and outside click,
// focus returns to the box, no navigation, panel inside the viewport, no console errors. Page and standalone, 1440 and 390.
// Usage: node scripts/site/nodecheck_portfolio.mjs [outdir]   (PORTFOLIO=/path/to/portfolio to override)
import pkg from '/Users/et/cyber-squire-ops/node_modules/playwright/index.js'; const { chromium } = pkg;
import fs from 'fs'; import os from 'os';
const out = (process.argv[2] || '/tmp/portfolio-shots') + '/'; fs.mkdirSync(out, { recursive: true });
const pf = process.env.PORTFOLIO || os.homedir() + '/portfolio';
const b = await chromium.launch(); const errs = []; let fails = 0;
const fail = (m) => { console.log('FAIL', m); fails++; };
for (const [u, w, h, tag] of [['file://' + pf + '/index.html', 1440, 900, 'd1440'], ['file://' + pf + '/index.html', 390, 844, 'd390'],
                              ['file://' + pf + '/views/topology.html', 1470, 830, 'v1470'], ['file://' + pf + '/views/topology.html', 390, 844, 'v390']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  p.on('pageerror', e => errs.push(tag + ': ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(tag + ' console: ' + m.text()); });
  await p.goto(u); await p.waitForTimeout(400); await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  const fig = u.endsWith('index.html') ? '#view-topology' : 'figure';
  const n = await p.evaluate(sel => document.querySelectorAll(sel + ' .cd-node').length, fig);
  const frameIsLink = await p.evaluate(sel => { const f = document.querySelector(sel + ' .cd-view-frame'); return f ? f.tagName : 'none'; }, fig);
  console.log(tag, 'nodes', n, 'frame', frameIsLink); if (n !== 31) fail('expected 31 nodes'); if (frameIsLink === 'A') fail('frame is still a link');
  await p.evaluate(sel => document.querySelector(sel).scrollIntoView({ block: 'start' }), fig); await p.waitForTimeout(300);
  await p.click(fig + ' .cd-node[data-node="squire"] rect'); await p.waitForTimeout(300);
  const open = await p.evaluate(() => { const pn = document.getElementById('cd-node-panel'); if (!pn || !pn.classList.contains('open')) return null; const r = pn.getBoundingClientRect();
    return { title: pn.querySelector('.cd-node-title').textContent, status: pn.querySelector('.cd-node-status b').textContent, controls: pn.querySelectorAll('.cd-node-controls li').length,
             evidence: pn.querySelectorAll('.cd-node-evidence li').length, focus: document.activeElement.className, top: Math.round(r.top), right: Math.round(r.right), bottom: Math.round(r.bottom), w: innerWidth, h: innerHeight,
             firstHref: pn.querySelector('.cd-node-evidence a').href, ctrlHref: pn.querySelector('.cd-node-controls a').href }; });
  console.log(tag, 'panel', JSON.stringify(open));
  if (!open || open.title !== 'Squire') fail('panel did not open on Squire');
  if (open && (open.right > open.w + 0.5 || open.bottom > open.h + 0.5 || open.top < 0)) fail('panel outside viewport');
  if (open && open.focus !== 'cd-node-close') fail('focus not on close button');
  if (!p.url().endsWith(u.split('/').pop())) fail('navigation happened ' + p.url());
  await p.screenshot({ path: out + tag + '_node_open.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  const after = await p.evaluate(() => ({ open: document.getElementById('cd-node-panel').classList.contains('open'), focus: document.activeElement.getAttribute('data-node') }));
  console.log(tag, 'after escape', JSON.stringify(after)); if (after.open || after.focus !== 'squire') fail('escape did not close or focus did not return');
  const kb = await p.evaluate(() => { const g = document.querySelector('.cd-node[data-node="access"]'); g.focus(); return document.activeElement === g; });
  await p.keyboard.press('Enter'); await p.waitForTimeout(200);
  const kbOpen = await p.evaluate(() => document.getElementById('cd-node-panel').classList.contains('open') && document.querySelector('#cd-node-panel .cd-node-title').textContent);
  console.log(tag, 'keyboard focus', kb, 'enter opened', kbOpen); if (!kb || kbOpen !== 'Access') fail('keyboard open');
  await p.mouse.click(2, Math.round(h * 0.25)); await p.waitForTimeout(200);
  // a box on the right half opens the panel on the left at desktop widths
  await p.click(fig + ' .cd-node[data-node="object-storage"] rect'); await p.waitForTimeout(250);
  const side = await p.evaluate(() => { const r = document.getElementById('cd-node-panel').getBoundingClientRect(); return { left: Math.round(r.left), right: Math.round(r.right), w: innerWidth, title: document.querySelector('#cd-node-panel .cd-node-title').textContent }; });
  console.log(tag, 'right-side box', JSON.stringify(side)); if (side.title !== 'Object storage') fail('right-side box did not open'); if (w > 900 && side.left > w / 2) fail('panel did not switch sides');
  if (w > 900) await p.screenshot({ path: out + tag + '_node_open_left.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(150);
  const closed = await p.evaluate(() => !document.getElementById('cd-node-panel').classList.contains('open'));
  console.log(tag, 'outside click closed', closed); if (!closed) fail('outside click');
  await p.close();
}
console.log('errors:', errs.length ? errs.join(' | ').slice(0, 500) : 'none'); if (errs.length) fails++;
await b.close(); process.exit(fails ? 1 : 0);

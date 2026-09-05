// Node panel QC: 31 clickable boxes on the topology, panel opens on click and on Enter, closes on Escape and outside click,
// focus returns to the box, no navigation, panel inside the viewport, no console errors. Page and standalone, 1440 and 390.
// Usage: node scripts/site/nodecheck_portfolio.mjs [outdir] [slug=count ...]   default topology=31   (PORTFOLIO=/path/to/portfolio to override)
import pkg from '/Users/et/cyber-squire-ops/node_modules/playwright/index.js'; const { chromium } = pkg;
import fs from 'fs'; import os from 'os';
const out = (process.argv[2] || '/tmp/portfolio-shots') + '/'; fs.mkdirSync(out, { recursive: true });
const pf = process.env.PORTFOLIO || os.homedir() + '/portfolio';
const specs = process.argv.slice(3).length ? process.argv.slice(3).map(a => a.split('=')) : [['topology', '31']];
const b = await chromium.launch(); const errs = []; let fails = 0;
const fail = (m) => { console.log('FAIL', m); fails++; };
for (const [slug, want] of specs) for (const [u, w, h, tag] of [['file://' + pf + '/index.html', 1440, 900, slug + '_d1440'], ['file://' + pf + '/index.html', 390, 844, slug + '_d390'],
                              ['file://' + pf + '/views/' + slug + '.html', 1470, 830, slug + '_v1470'], ['file://' + pf + '/views/' + slug + '.html', 390, 844, slug + '_v390']]) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  p.on('pageerror', e => errs.push(tag + ': ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(tag + ' console: ' + m.text()); });
  await p.goto(u); await p.waitForTimeout(400); await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  const fig = u.endsWith('index.html') ? '#view-' + slug : 'figure';
  const n = await p.evaluate(sel => document.querySelectorAll(sel + ' .cd-node').length, fig);
  const frameIsLink = await p.evaluate(sel => { const f = document.querySelector(sel + ' .cd-view-frame'); return f ? f.tagName : 'none'; }, fig);
  console.log(tag, 'nodes', n, 'frame', frameIsLink); if (n !== Number(want)) fail('expected ' + want + ' nodes'); if (frameIsLink === 'A') fail('frame is still a link');
  const ids = await p.evaluate(sel => Array.from(document.querySelectorAll(sel + ' .cd-node')).map(g => g.getAttribute('data-node')), fig);
  const first = ids[0], second = ids[1], last = ids[ids.length - 1];
  const labelOf = async id => p.evaluate(([sel, id]) => document.querySelector(sel + ' .cd-node[data-node="' + id + '"]').getAttribute('aria-label').replace(/: details$/, ''), [fig, id]);
  await p.evaluate(sel => document.querySelector(sel).scrollIntoView({ block: 'start' }), fig); await p.waitForTimeout(300);
  await p.click(fig + ' .cd-node[data-node="' + first + '"] rect'); await p.waitForTimeout(300);
  const open = await p.evaluate(() => { const pn = document.getElementById('cd-node-panel'); if (!pn || !pn.classList.contains('open')) return null; const r = pn.getBoundingClientRect();
    return { title: pn.querySelector('.cd-node-title').textContent, status: pn.querySelector('.cd-node-status b').textContent, controls: pn.querySelectorAll('.cd-node-controls li').length,
             evidence: pn.querySelectorAll('.cd-node-evidence li').length, focus: document.activeElement.className, top: Math.round(r.top), right: Math.round(r.right), bottom: Math.round(r.bottom), w: innerWidth, h: innerHeight }; });
  console.log(tag, 'panel', JSON.stringify(open));
  if (!open || open.title !== await labelOf(first)) fail('panel did not open on ' + first);
  if (open && (open.right > open.w + 0.5 || open.bottom > open.h + 0.5 || open.top < 0)) fail('panel outside viewport');
  if (open && open.focus !== 'cd-node-close') fail('focus not on close button');
  if (open && open.evidence < 1) fail('no evidence links');
  if (!p.url().endsWith(u.split('/').pop())) fail('navigation happened ' + p.url());
  await p.screenshot({ path: out + tag + '_node_open.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  const after = await p.evaluate(() => ({ open: document.getElementById('cd-node-panel').classList.contains('open'), focus: document.activeElement.getAttribute('data-node') }));
  console.log(tag, 'after escape', JSON.stringify(after)); if (after.open || after.focus !== first) fail('escape did not close or focus did not return');
  const kb = await p.evaluate(([sel, id]) => { const g = document.querySelector(sel + ' .cd-node[data-node="' + id + '"]'); g.focus(); return document.activeElement === g; }, [fig, second]);
  await p.keyboard.press('Enter'); await p.waitForTimeout(200);
  const kbOpen = await p.evaluate(() => document.getElementById('cd-node-panel').classList.contains('open') && document.querySelector('#cd-node-panel .cd-node-title').textContent);
  console.log(tag, 'keyboard focus', kb, 'enter opened', kbOpen); if (!kb || kbOpen !== await labelOf(second)) fail('keyboard open');
  await p.mouse.click(2, Math.round(h * 0.25)); await p.waitForTimeout(200);
  const closed = await p.evaluate(() => !document.getElementById('cd-node-panel').classList.contains('open'));
  console.log(tag, 'outside click closed', closed); if (!closed) fail('outside click');
  await p.click(fig + ' .cd-node[data-node="' + last + '"] rect'); await p.waitForTimeout(250);
  const side = await p.evaluate(() => { const r = document.getElementById('cd-node-panel').getBoundingClientRect(); return { left: Math.round(r.left), right: Math.round(r.right), w: innerWidth, title: document.querySelector('#cd-node-panel .cd-node-title').textContent }; });
  const lastBox = await p.evaluate(([sel, id]) => { const r = document.querySelector(sel + ' .cd-node[data-node="' + id + '"] rect').getBoundingClientRect(); return (r.left + r.width / 2) > innerWidth / 2; }, [fig, last]);
  console.log(tag, 'last box', last, 'on right half', lastBox, JSON.stringify(side)); if (side.title !== await labelOf(last)) fail('last box did not open');
  if (w > 900 && lastBox && side.left > w / 2) fail('panel did not switch sides'); if (w > 900 && !lastBox && side.left < w / 2) fail('panel switched sides for a left-half box');
  if (w > 900) await p.screenshot({ path: out + tag + '_node_open_last.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(150);
  await p.close();
}
console.log('errors:', errs.length ? errs.join(' | ').slice(0, 500) : 'none'); if (errs.length) fails++;
await b.close(); process.exit(fails ? 1 : 0);

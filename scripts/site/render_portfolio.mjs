// Renders every section of the portfolio at 1440, 390, 820 (dark) and 1440 light, hides the fixed nav during section shots,
// reports document height, horizontal overflow (with the overflowing elements), and console errors.
// Usage: node scripts/site/render_portfolio.mjs [outdir]   (PORTFOLIO=/path/to/portfolio to override)
import { createRequire } from "module"; const require = createRequire(import.meta.url);
import pkg from '/Users/et/cyber-squire-ops/node_modules/playwright/index.js'; const { chromium } = pkg;
const out = (process.argv[2] || '/tmp/portfolio-shots') + '/';
import fs from 'fs'; fs.mkdirSync(out, { recursive: true });
const site = 'file://' + (process.env.PORTFOLIO || require('os').homedir() + '/portfolio') + '/index.html';
const browser = await chromium.launch();
const errors = [];
async function shoot(width, height, tag, light) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  page.on('pageerror', e => errors.push(tag + ': ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  await page.goto(site); await page.waitForTimeout(300); await page.keyboard.press('Escape'); await page.waitForTimeout(600);
  if (light) await page.evaluate(() => document.documentElement.classList.add('light'));
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); await page.waitForTimeout(300);
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log(tag, 'height', h, 'horizontal overflow px', overflow);
  if (overflow > 0) { const wide = await page.evaluate(() => { const W = document.documentElement.clientWidth; const out = []; document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect(); if (r.right > W + 1 && r.width > 0 && r.width < 5000) out.push((el.id ? '#' + el.id : el.tagName.toLowerCase() + '.' + (el.className && el.className.baseVal === undefined ? String(el.className).split(' ')[0] : 'svg')) + ' right=' + Math.round(r.right) + ' w=' + Math.round(r.width)); }); return out.slice(0, 12); }); console.log('  overflowing:', wide.join(' | ')); }
  const secs = ['section.hero', '#proof', '#certs', '#experience', '#education', '#threat-modeling', '#ai-security', '#grc', '#blog', '#contact', 'nav'];
  await page.locator('nav').screenshot({ path: out + tag + '_nav.png' });
  if (width < 500) { await page.click('.menu-toggle'); await page.waitForTimeout(200); await page.screenshot({ path: out + tag + '_menu.png' }); await page.click('.menu-toggle'); }
  await page.addStyleTag({ content: 'nav, .scroll-progress { visibility: hidden !important; }' });
  for (const sel of secs) {
    if (sel === 'nav') continue;
    const loc = page.locator(sel).first();
    try { await loc.screenshot({ path: out + tag + '_' + sel.replace(/[#.]/g, '') + '.png' }); } catch (e) { console.log('shot failed', tag, sel, e.message.split('\n')[0]); }
  }
  await page.close();
}
await shoot(1440, 900, 'd1440', false);
await shoot(390, 844, 'd390', false);
await shoot(1440, 900, 'l1440', true);
await shoot(820, 1180, 'd820', false);
for (const [w, h, tag] of [[1470, 830, 'v1470'], [390, 844, 'v390']]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', e => errors.push(tag + ': ' + e.message));
  await page.goto('file:///Users/et/portfolio/views/topology.html'); await page.waitForTimeout(800);
  await page.screenshot({ path: out + tag + '_topology.png', fullPage: false }); await page.close();
}
console.log('errors:', errors.length ? errors.join('\n') : 'none');
await browser.close();

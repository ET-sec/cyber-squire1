import pkg from '/Users/et/cyber-squire-ops/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 820, height: 1180 } });
await p.goto('file:///Users/et/portfolio/index.html'); await p.waitForTimeout(300); await p.keyboard.press('Escape'); await p.waitForTimeout(500);
const r = await p.evaluate(() => { const W = document.documentElement.clientWidth; const out = []; 
  const walk = (el, depth) => { for (const c of el.children) { const cs = getComputedStyle(c); if (['fixed'].includes(cs.position)) continue; const rect = c.getBoundingClientRect(); const over = (c.scrollWidth > c.clientWidth + 1) && cs.overflowX !== 'auto' && cs.overflowX !== 'scroll' && cs.overflowX !== 'hidden'; if (rect.right > W + 0.5 && rect.width > 0 && !(c.closest('.cd-view-frame'))) out.push(depth + ' ' + c.tagName.toLowerCase() + (c.id ? '#' + c.id : '') + '.' + String(c.className).split(' ')[0] + ' right=' + Math.round(rect.right) + ' sw=' + c.scrollWidth + ' cw=' + c.clientWidth); if (depth < 6) walk(c, depth + 1); } };
  walk(document.body, 0); return { W, sw: document.documentElement.scrollWidth, bodysw: document.body.scrollWidth, out: out.slice(0, 15) }; });
console.log(JSON.stringify(r, null, 1)); await b.close();

import pkg from '/Users/et/cyber-squire-ops/node_modules/playwright/index.js'; const { chromium } = pkg;
const b = await chromium.launch(); const errs = [];
for (const u of ['file:///Users/et/portfolio/index.html', 'file:///Users/et/portfolio/views/topology.html']) {
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } }); p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  await p.goto(u); await p.waitForTimeout(400); await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  const n = await p.evaluate(() => document.querySelectorAll('.cd-packet').length); console.log(u.split('/').pop(), 'packets', n);
  if (u.endsWith('index.html')) { await p.evaluate(() => document.querySelector('#view-topology').scrollIntoView()); await p.waitForTimeout(500); await p.locator('#view-topology').screenshot({ path: '/private/tmp/claude-501/-Users-et-cyber-squire-ops/cac0963c-c640-4478-b7d0-070073dfa0e4/scratchpad/shots/flow_topology.png' }); }
  await p.close();
}
console.log('errors:', errs.length ? errs.join(' | ').slice(0, 300) : 'none'); await b.close();

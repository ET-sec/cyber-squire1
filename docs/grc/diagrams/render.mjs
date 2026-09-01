// Render the HTML chart sources in this directory to PNG via Playwright.
// Usage: cd docs/grc/diagrams && node render.mjs [name ...]
// With no args, renders every chart in TARGETS.
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const TARGETS = [
  'control_coverage',
  'poam_summary',
  'risk_heat_map',
  'risk_summary_dashboard',
  'github_actions_pipeline',
];
const names = process.argv.slice(2).length ? process.argv.slice(2) : TARGETS;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 2160, height: 1200 }, deviceScaleFactor: 1 });
for (const name of names) {
  await page.goto('file://' + path.join(dir, name + '.html'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(dir, name + '.png'), fullPage: true });
  console.log('rendered', name + '.png');
}
await browser.close();

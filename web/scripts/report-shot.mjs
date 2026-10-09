// The report's decision block as a PNG, for the pitch deck. Only the decision block: the comparables table below it pairs
// WLDD creators with the prices WLDD paid, which must never reach a slide. Uses the installed Chrome and the demo cookie.
// usage: node web/scripts/report-shot.mjs <analysis id> [out.png]   (API and web running)
import { chromium } from 'playwright-core';

const [id = 'demo-go', out = '../data/pitch/report.png'] = process.argv.slice(2);
const base = process.env.BASE ?? 'http://localhost:3000';
const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
await page.context().addCookies([{ name: 'truerate_session', value: 'demo', url: base }]);
await page.goto(`${base}/analyses/${id}`, { waitUntil: 'networkidle' });
await page.waitForSelector('section[aria-label="Decision"]');
await page.locator('section[aria-label="Decision"]').screenshot({ path: out });
await browser.close();
console.log(`Saved ${out}`);

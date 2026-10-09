// The report has no primary button: its job is the decision block. audit.mjs takes the first .btn as the primary
// action, so for the report this checks the price and the Go/Negotiate/Avoid chip instead.
// usage: node first-screen.mjs <base> <report path>
import { chromium } from 'playwright';
const [base = 'http://localhost:3000', route = '/analyses/demo-fake'] = process.argv.slice(2);
const MATRIX = [[390,844],[414,896],[768,1024],[1024,640],[1280,720],[1366,768],[1440,900],[1512,850],[1728,1000],[1920,1080],[2560,1440]];
const browser = await chromium.launch({ channel: 'chrome' });
let bad = 0;
for (const [w, h] of MATRIX) {
  const p = await browser.newPage({ viewport: { width: w, height: h } });
  await p.context().addCookies([{ name: 'truerate_session', value: 'demo', url: base }]);
  await p.goto(base + route, { waitUntil: 'networkidle' });
  const m = await p.evaluate(() => {
    const block = document.querySelector('section[aria-label="Decision"]');
    const price = block.querySelector('p.figure');
    const chip = block.querySelector('span.rounded-lg.font-bold');
    return { price: Math.round(price.getBoundingClientRect().bottom), chip: Math.round(chip.getBoundingClientRect().bottom),
             overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1 };
  });
  const ok = m.price <= h && m.chip <= h && !m.overflow;
  if (!ok) bad++;
  console.log(`${w}x${h}: price bottom ${m.price}, decision chip bottom ${m.chip}, overflow ${m.overflow} ${ok ? 'ok' : 'PROBLEM'}`);
  await p.close();
}
await browser.close();
console.log(bad ? `FAIL  ${bad} problem(s)` : 'PASS  price and decision on the first screen at all 11 sizes');
process.exit(bad ? 1 : 0);

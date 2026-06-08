import { chromium } from 'playwright';
const B = 'http://localhost:8899';
const OUT = '_audit/qa';
const PAGES = ['index.html','contact.html','portfolio.html','support-services.html','impact.html','resources.html','about.html'];
const WIDTHS = [1440, 1280, 1024, 768, 390];
const benign = (t) => t.includes('cdn.tailwind') || t.includes('tailwindcss.com') || t.toLowerCase().includes('favicon');

const browser = await chromium.launch();
const results = {};
for (const page of PAGES) {
  const errs = [], broken = new Set(), failed = [];
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  p.on('console', m => { if (m.type() === 'error' && !benign(m.text())) errs.push(m.text().slice(0, 140)); });
  p.on('pageerror', e => errs.push('PE:' + e.message.slice(0, 140)));
  p.on('response', r => { if (r.status() >= 400 && !benign(r.url())) failed.push(r.status() + ' ' + r.url().replace(B, '')); });
  await p.goto(`${B}/${page}`, { waitUntil: 'networkidle' }).catch(e => errs.push('GOTO:' + e.message.slice(0,80)));
  await p.waitForTimeout(500);
  const b = await p.$$eval('img', els => els.filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.src));
  b.forEach(x => broken.add(x.split('/').slice(-2).join('/')));
  // overflow + nav check across widths
  const overflow = {};
  for (const w of WIDTHS) {
    await p.setViewportSize({ width: w, height: 900 });
    await p.waitForTimeout(150);
    const o = await p.evaluate(() => ({
      doc: document.documentElement.scrollWidth,
      win: window.innerWidth,
      navWrap: (() => { const n = document.querySelector('#mainNav .nav-inner') || document.querySelector('#mainNav'); if (!n) return null; return n.scrollWidth > n.clientWidth + 1; })()
    }));
    overflow[w] = { xover: o.doc - o.win, navWrap: o.navWrap };
  }
  // screenshots: full page at 1440 + 390, nav strip at 1024
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.waitForTimeout(150);
  await p.screenshot({ path: `${OUT}/${page.replace('.html','')}-1440.png`, fullPage: true }).catch(()=>{});
  results[page] = { errs, broken: [...broken], failed: [...new Set(failed)].slice(0,8), overflow };
  await ctx.close();
}
// focused homepage shots
const ctx = await browser.newContext({ viewport: { width: 1024, height: 768 } });
const p = await ctx.newPage();
await p.goto(`${B}/index.html`, { waitUntil: 'networkidle' });
await p.waitForTimeout(400);
await (await p.$('#mainNav')).screenshot({ path: `${OUT}/nav-1024.png` }).catch(()=>{});
await (await p.$('#services')).screenshot({ path: `${OUT}/services-1024.png` }).catch(()=>{});
await (await p.$('#book')).screenshot({ path: `${OUT}/cta-deglass.png` }).catch(()=>{});
await ctx.close();
await browser.close();
console.log(JSON.stringify(results, null, 1));

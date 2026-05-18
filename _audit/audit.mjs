#!/usr/bin/env node
// Pre-ship audit: crawl all top-level pages at desktop/tablet/mobile.
// Collects console errors, failed network requests, broken images, anchor link 404s,
// missing alt text, viewport overflow, and verifies key interactions (scroll-nav,
// mobile menu, impact filters, resources filters).
//
// Usage:  node _audit/audit.mjs [base-url]   (default http://localhost:8788)

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const BASE = process.argv[2] || 'http://localhost:8788';
const PAGES = [
  '/index.html',
  '/about.html',
  '/portfolio.html',
  '/resources.html',
  '/impact.html',
  '/contact.html',
  '/blog.html',
];
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet',  width: 768,  height: 1024 },
  { name: 'mobile',  width: 390,  height: 844 },
];

mkdirSync(join(HERE, 'screens'), { recursive: true });

const report = {
  base: BASE,
  ranAt: new Date().toISOString(),
  pages: {},
  interactionTests: {},
  summary: { errors: 0, warnings: 0, info: 0 },
};

function add(level, where, msg, detail) {
  const bucket = report.pages[where] ||= { errors: [], warnings: [], info: [] };
  bucket[level + 's'].push(detail ? { msg, detail } : { msg });
  report.summary[level + 's']++;
}

async function auditPage(browser, path, vp) {
  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 1,
    userAgent: 'AventarioAudit/1.0',
  });
  const page = await ctx.newPage();
  const where = `${path} @ ${vp.name}`;

  // Capture console + network errors
  const consoleErrors = [];
  const failedRequests = [];
  page.on('console', m => {
    if (m.type() === 'error') consoleErrors.push(m.text());
    if (m.type() === 'warning') add('warning', where, 'console.warn', m.text().slice(0, 200));
  });
  page.on('pageerror', e => consoleErrors.push('pageerror: ' + e.message));
  page.on('requestfailed', r => failedRequests.push({ url: r.url(), reason: r.failure()?.errorText }));
  page.on('response', r => {
    if (r.status() >= 400) failedRequests.push({ url: r.url(), status: r.status() });
  });

  let loadErr = null;
  try {
    await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 30_000 });
  } catch (e) {
    loadErr = e.message;
    add('error', where, 'page load failed', loadErr);
  }

  if (!loadErr) {
    // Console + network
    consoleErrors.forEach(t => add('error', where, 'console.error', t.slice(0, 240)));
    failedRequests.forEach(r => {
      // Skip third-party CDN noise that's unrelated to our site
      if (r.url.startsWith(BASE)) {
        add('error', where, 'request failed', `${r.status || r.reason || '?'} ${r.url}`);
      } else if (r.status >= 500) {
        add('warning', where, '3rd-party 5xx', `${r.status} ${r.url}`);
      }
    });

    // Broken images
    const brokenImgs = await page.$$eval('img', imgs => imgs
      .filter(i => i.complete && i.naturalWidth === 0)
      .map(i => ({ src: i.getAttribute('src'), alt: i.getAttribute('alt'), rect: i.getBoundingClientRect().width }))
    );
    brokenImgs.forEach(i => add('error', where, 'broken img', `${i.src} (rendered ${Math.round(i.rect)}px)`));

    // Missing alt text on visible non-decorative imgs
    const missingAlt = await page.$$eval('img', imgs => imgs
      .filter(i => i.getBoundingClientRect().width > 40 && (i.getAttribute('alt') === null || i.getAttribute('alt') === undefined))
      .map(i => i.getAttribute('src'))
    );
    missingAlt.forEach(s => add('warning', where, 'img missing alt', s));

    // Empty alt on visible content imgs (only flag if image is large enough to seem important)
    const emptyAlt = await page.$$eval('img', imgs => imgs
      .filter(i => i.getBoundingClientRect().width > 200 && i.getAttribute('alt') === '')
      .map(i => i.getAttribute('src'))
    );
    emptyAlt.forEach(s => add('info', where, 'large img has empty alt (decorative?)', s));

    // Viewport horizontal overflow
    const overflowX = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflowX > 1) add('warning', where, `horizontal overflow ${overflowX}px`);

    // Same-origin anchor link integrity (skip on tablet/mobile to avoid 3x cost)
    if (vp.name === 'desktop') {
      const links = await page.$$eval('a[href]', as => as
        .map(a => a.getAttribute('href'))
        .filter(h => h && !h.startsWith('http') && !h.startsWith('mailto:') && !h.startsWith('tel:') && !h.startsWith('#') && !h.startsWith('javascript:'))
      );
      const unique = [...new Set(links)];
      for (const href of unique) {
        try {
          const target = new URL(href, BASE + path).toString();
          let r = await page.request.fetch(target);
          // vercel.json has cleanUrls: true → /foo resolves to /foo.html on production.
          // Retry the .html variant before flagging so we don't false-flag on the local server.
          if (r.status() >= 400 && !target.endsWith('.html') && !target.endsWith('/')) {
            const r2 = await page.request.fetch(target + '.html');
            if (r2.status() < 400) continue; // clean-URL link, fine on Vercel
          }
          if (r.status() >= 400) add('error', where, 'internal link 404', `${r.status()} ${href}`);
        } catch (e) {
          add('error', where, 'internal link fetch error', `${href}: ${e.message}`);
        }
      }
    }

    // Headings — there should be exactly one <h1> per page
    const h1Count = await page.$$eval('h1', els => els.length);
    if (h1Count === 0) add('warning', where, 'no <h1> on page');
    if (h1Count > 1) add('warning', where, `multiple <h1>s (${h1Count})`);

    // Anchor hrefs that point to ids that don't exist on the page
    if (vp.name === 'desktop') {
      const dangling = await page.evaluate(() => {
        const out = [];
        document.querySelectorAll('a[href^="#"]').forEach(a => {
          const id = a.getAttribute('href').slice(1);
          if (id && !document.getElementById(id)) out.push(a.getAttribute('href'));
        });
        return [...new Set(out)];
      });
      dangling.forEach(h => add('warning', where, 'dangling in-page anchor', h));
    }

    // Screenshot
    try {
      const safe = path.replace(/[^a-z0-9]+/gi, '_').replace(/^_+|_+$/g, '') || 'home';
      const file = join(HERE, 'screens', `${safe}__${vp.name}.png`);
      await page.screenshot({ path: file, fullPage: false, timeout: 10_000 });
    } catch (e) {
      // Screenshots aren't critical, skip silently if they time out
    }
  }

  await ctx.close();
}

async function interactionTests(browser) {
  // 1) Mobile menu opens
  const t = report.interactionTests;
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p = await ctx.newPage();
  await p.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
  const btn = await p.$('#mobileMenuBtn');
  let mobileMenuOk = false;
  if (btn) {
    await btn.click();
    await p.waitForTimeout(150);
    mobileMenuOk = await p.$eval('#mobileMenu', m => !m.classList.contains('hidden'));
  }
  t.mobileMenuOpens = mobileMenuOk;
  await ctx.close();

  // 2) Nav hide on scroll down / show on scroll up
  const ctx2 = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p2 = await ctx2.newPage();
  await p2.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
  // Scroll down 1000
  await p2.evaluate(() => window.scrollTo({ top: 1200, behavior: 'instant' }));
  await p2.waitForTimeout(350);
  const hiddenAfterDown = await p2.evaluate(() => document.getElementById('mainNav')?.classList.contains('nav-hidden'));
  // Scroll up
  await p2.evaluate(() => window.scrollTo({ top: 600, behavior: 'instant' }));
  await p2.waitForTimeout(350);
  const hiddenAfterUp = await p2.evaluate(() => document.getElementById('mainNav')?.classList.contains('nav-hidden'));
  t.navHidesOnScrollDown = !!hiddenAfterDown;
  t.navShowsOnScrollUp = !hiddenAfterUp;
  await ctx2.close();

  // 3) Impact page area + sub-topic filter intersection
  const ctx3 = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p3 = await ctx3.newPage();
  await p3.goto(BASE + '/impact.html', { waitUntil: 'networkidle' });
  const total = await p3.$$eval('.impact-card', c => c.length);
  await p3.click('#impact-filter-area button[data-area="savings"]');
  await p3.click('#impact-filter-solution button[data-solution="requirements"]');
  await p3.waitForTimeout(150);
  const intersect = await p3.$$eval('.impact-card', cards => cards.filter(c => c.style.display !== 'none').length);
  t.impactFilters = { total, savingsAndRequirements: intersect, ok: total > 0 && intersect > 0 && intersect < total };
  await ctx3.close();

  // 4) Resources filter chip behaviour
  const ctx4 = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p4 = await ctx4.newPage();
  await p4.goto(BASE + '/resources.html', { waitUntil: 'networkidle' });
  const totalRes = await p4.$$eval('.res-card', c => c.length);
  const webinarChip = await p4.$('#res-filter button[data-filter="webinar"]');
  let webinarOnly = -1;
  if (webinarChip) {
    await webinarChip.click();
    await p4.waitForTimeout(150);
    webinarOnly = await p4.$$eval('.res-card', cards => cards.filter(c => c.style.display !== 'none').length);
  }
  t.resourcesFilter = { total: totalRes, webinarOnly, chipFound: !!webinarChip };
  await ctx4.close();

  // 5) HubSpot scheduler iframe present on landing
  const ctx5 = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const p5 = await ctx5.newPage();
  await p5.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
  const hubspotSrc = await p5.$eval('#book iframe', i => i.src).catch(() => null);
  t.hubspotIframe = { present: !!hubspotSrc, src: hubspotSrc };
  await ctx5.close();
}

const browser = await chromium.launch();
console.log(`Crawling ${PAGES.length} pages × ${VIEWPORTS.length} viewports against ${BASE} ...`);
for (const path of PAGES) {
  for (const vp of VIEWPORTS) {
    process.stdout.write(`  ${path} @ ${vp.name} ... `);
    const t0 = Date.now();
    await auditPage(browser, path, vp);
    console.log(`${Date.now() - t0}ms`);
  }
}
console.log('\nRunning interaction tests ...');
await interactionTests(browser);
await browser.close();

writeFileSync(join(HERE, 'report.json'), JSON.stringify(report, null, 2));

// Print summary
console.log('\n========================== AUDIT SUMMARY ==========================');
console.log(`Errors:   ${report.summary.errors}`);
console.log(`Warnings: ${report.summary.warnings}`);
console.log(`Info:     ${report.summary.infos || 0}`);
console.log('\nInteraction tests:');
for (const [k, v] of Object.entries(report.interactionTests)) {
  console.log(`  ${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`);
}
console.log('\nPer-page issue counts (errors + warnings):');
const issuePages = Object.entries(report.pages)
  .map(([k, v]) => [k, v.errors.length + v.warnings.length, v.errors.length])
  .sort((a, b) => b[1] - a[1])
  .filter(([, total]) => total > 0);
for (const [k, total, errs] of issuePages) console.log(`  ${k}  →  ${errs} errors / ${total - errs} warnings`);
console.log('\nFull report → _audit/report.json');
console.log('Screens     → _audit/screens/');

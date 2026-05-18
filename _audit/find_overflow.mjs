// Find the element causing horizontal overflow at 768px
import { chromium } from 'playwright';

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 768, height: 1024 } });
const p = await ctx.newPage();

for (const path of ['/index.html', '/about.html', '/portfolio.html']) {
  await p.goto('http://localhost:8788' + path, { waitUntil: 'networkidle' });
  const offenders = await p.evaluate((vw) => {
    const out = [];
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.right > vw + 0.5 || r.left < -0.5) {
        // Skip if children also overflow (we want the innermost cause)
        out.push({
          tag: el.tagName.toLowerCase(),
          id: el.id || '',
          cls: (el.className || '').toString().slice(0, 80),
          left: Math.round(r.left),
          right: Math.round(r.right),
          width: Math.round(r.width),
        });
      }
    });
    // Keep only the widest few — descendants typically inherit overflow from a parent
    return out.sort((a, b) => b.right - a.right).slice(0, 6);
  }, 768);
  console.log(`\n=== ${path} ===`);
  console.log(`viewport=768, docScrollWidth=${await p.evaluate(() => document.documentElement.scrollWidth)}`);
  for (const o of offenders) console.log(`  ${o.tag}${o.id ? '#' + o.id : ''}.${o.cls}  left=${o.left} right=${o.right} w=${o.width}`);
}
await b.close();

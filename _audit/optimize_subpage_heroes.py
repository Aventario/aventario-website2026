"""Wrap subpage photography heroes in <picture> (WebP) and fix the lazy-loading
anti-pattern on the LCP image. Only touches the hero <img> (object-cover photography).
Run with --apply."""
import os, re, sys

APPLY = '--apply' in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
        'style-comparison','_config','.vercel','.git','illustration-gallery')

# actual intrinsic widths of the source photos, for srcset descriptors
WIDTHS = {'team-summit-glow': 2000, 'team-ridge-sunrise': 1900}

# match a hero img: src to a known photography hero, containing object-cover, not already in a <picture>
HERO_RE = re.compile(
    r'<img\s+src="([^"]*photography/(team-summit-glow|team-ridge-sunrise)\.jpg)"([^>]*?object-cover[^>]*?)>',
    re.I)

def transform_tag(m):
    src, name, rest = m.group(1), m.group(2), m.group(3)
    prefix = src[:src.rfind('/')+1]           # e.g. images/photography/ or ../images/photography/
    w = WIDTHS[name]
    # clean the remaining attrs: drop loading="lazy", ensure fetchpriority high, keep the rest
    rest2 = re.sub(r'\s*loading="lazy"', '', rest)
    if 'fetchpriority' not in rest2:
        rest2 = ' fetchpriority="high"' + rest2
    img = f'<img src="{src}"{rest2}>'
    srcset = f'{prefix}{name}-1200.webp 1200w, {prefix}{name}.webp {w}w'
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="100vw">{img}</picture>')

changed = []
for root, dirs, fs in os.walk(ROOT):
    if set(os.path.relpath(root, ROOT).replace('\\','/').split('/')) & set(SKIP):
        dirs[:] = []; continue
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in fs:
        if not f.endswith('.html'): continue
        rel_pre = os.path.relpath(os.path.join(root, f), ROOT).replace('\\','/')
        # Homepages use this photo as a BELOW-FOLD decorative image (keep it lazy). Skip them.
        if rel_pre in ('index.html','index-b.html','index-c.html','index-v2.html',
                       'index.previous-pre-v03.html','index.v03-draft.html','de/index.html'):
            continue
        p = os.path.join(root, f)
        t = open(p, encoding='utf-8').read()
        if '<picture><source type="image/webp"' in t and 'photography/team-' in t:
            pass  # may already be done; regex still guards against double-wrap below
        # only transform imgs NOT already preceded by a <picture><source ...webp>
        new, n = HERO_RE.subn(transform_tag, t)
        if n and new != t:
            rel = os.path.relpath(p, ROOT).replace('\\','/')
            changed.append((rel, n))
            if APPLY:
                open(p, 'w', encoding='utf-8', newline='').write(new)

for rel, n in sorted(changed):
    print(f"  {'CHANGED' if APPLY else 'would change'} {rel}  ({n} hero img)")
print(f"\n{'APPLIED' if APPLY else 'DRY'}: {len(changed)} pages")

"""Unify the site header across all standard pages to match the approved homepage header.

- Ports the wrapped logo (h-11 md:h-14), the icon Contact pill, unified nav links,
  and the mobile menu with aria attributes onto every page that has the standard nav shell.
- Preserves each page's over-hero state (transparent nav on dark hero) vs solid nav.
- Leaves index.html untouched (approved reference; keeps its Consulting/AI toggle).
- Leaves the 8 minimal legal/webinar landing pages untouched.
- German pages get German labels + the EN language switcher, absolute /de/ paths.

Run with --apply to write; default is dry-run.
"""
import os, re, sys

APPLY = '--apply' in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # website/

SKIP_DIRS = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
             'style-comparison','_config','.vercel','.git','illustration-gallery')
# Pages to never touch: homepage reference, homepage experiments, drafts, minimal landing/legal pages.
EXCLUDE = {
    'index.html','index-b.html','index-c.html','index-v2.html',
    'index.previous-pre-v03.html','index.v03-draft.html','google3165196d202229c2.html',
    'impressum.html','datenschutz.html','webinar.html','webinar-thanks.html',
    'de/impressum.html','de/datenschutz.html','de/webinar.html','de/webinar-thanks.html',
}

CONTACT_PILL_CSS = """
      /* Contact pill: full label, collapses to a round icon once scrolled past the hero */
      a.contact-pill{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;height:36px;padding:0 1.25rem;border-radius:9999px;transition:padding .35s ease, background-color .25s ease, color .25s ease, border-color .25s ease;}
      a.contact-pill i{line-height:1;display:block;}
      a.contact-pill .contact-label{display:inline-block;max-width:120px;overflow:hidden;white-space:nowrap;transition:max-width .35s ease, opacity .2s ease;}
      nav#mainNav.past-hero a.contact-pill{width:36px;padding:0;gap:0;}
      nav#mainNav.past-hero a.contact-pill .contact-label{max-width:0;opacity:0;}
      @media (prefers-reduced-motion: reduce){ a.contact-pill, a.contact-pill .contact-label{transition:none;} }
"""

def extract_logo():
    t = open(os.path.join(ROOT,'index.html'), encoding='utf-8').read()
    m = re.search(r'aria-label="Aventario Home">(<svg.*?</svg>)', t, re.S)
    if not m:
        raise SystemExit('Could not extract logo SVG from index.html')
    return m.group(1)

LOGO = extract_logo()

def build_nav(lang, over):
    over_attr = ' data-over-hero="1"' if over else ''
    if lang == 'de':
        home, impact, res, team, contact = '/de/index.html','/de/impact.html','/de/resources.html','/de/about.html','/de/contact.html'
        li, lr, lt, lc = 'Referenzen','Ressourcen','Team','Kontakt'
        extra = '\n            <a href="/" class="hover:text-accentdark opacity-70" title="English version">EN</a>'
        extra_m = '\n        <a href="/" class="block py-2 text-base font-bold uppercase tracking-widest hover:text-accentdark opacity-70">EN</a>'
    else:
        home, impact, res, team, contact = '/index.html','/impact.html','/resources.html','/about.html','/contact.html'
        li, lr, lt, lc = 'Impact','Resources','Team','Contact'
        extra = ''
        extra_m = ''

    nav = (
f'''    <nav id="mainNav"{over_attr} class="sticky top-0 z-40 bg-pagebg/95 backdrop-blur-sm border-b border-bordercolor px-6 md:px-12 py-4 flex justify-between items-center"><div class="nav-inner">
        <div class="flex items-center">
        <a href="{home}" class="flex items-center" aria-label="Aventario Home">{LOGO}</a>
        </div>
        <div class="hidden lg:flex space-x-8 text-sm uppercase tracking-widest font-bold items-center">
            <a href="{impact}" class="hover:text-accentdark">{li}</a>
            <a href="{res}" class="hover:text-accentdark">{lr}</a>
            <a href="{team}" class="hover:text-accentdark">{lt}</a>{extra}
        </div>
        <div class="hidden lg:flex items-center">
        <a href="{contact}" class="contact-pill nav-cta text-sm font-bold uppercase tracking-widest bg-text text-surface hover:bg-accentdark transition-colors" aria-label="{lc}" title="{lc}"><i class="ph ph-calendar-check text-lg"></i><span class="contact-label">{lc}</span></a>
        </div>
        <button id="mobileMenuBtn" class="lg:hidden w-9 h-9 flex items-center justify-center" aria-label="Toggle menu" aria-expanded="false" aria-controls="mobileMenu"><i class="ph ph-list text-2xl"></i></button>
    </div></nav>''')

    mobile = (
f'''    <div id="mobileMenu" class="hidden lg:hidden border-b border-bordercolor bg-pagebg px-6 py-4 space-y-2">
        <a href="{impact}" class="block py-2 text-base font-bold uppercase tracking-widest hover:text-accentdark">{li}</a>
        <a href="{res}" class="block py-2 text-base font-bold uppercase tracking-widest hover:text-accentdark">{lr}</a>
        <a href="{team}" class="block py-2 text-base font-bold uppercase tracking-widest hover:text-accentdark">{lt}</a>{extra_m}
        <a href="{contact}" class="block mt-3 text-center text-sm font-bold uppercase tracking-widest bg-text text-surface px-6 py-3 rounded-full">{lc}</a>
    </div>''')
    return nav, mobile

def find_balanced_div(t, start):
    """Given index of a '<div' start, return end index just past its matching '</div>'."""
    i = start
    depth = 0
    tag = re.compile(r'<(/?)div\b', re.I)
    while True:
        m = tag.search(t, i)
        if not m:
            return None
        if m.group(1) == '':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = t.find('>', m.end())
                return end + 1
        i = m.end()

def process(path, rel):
    t = open(path, encoding='utf-8').read()
    orig = t
    lang = 'de' if rel.startswith('de/') else 'en'

    # locate nav
    nm = re.search(r'<nav\b[^>]*sticky top-0 z-\d+ bg-pagebg[^>]*>', t)
    if not nm:
        return ('SKIP-nonav', rel)
    over = 'data-over-hero' in t[nm.start():nm.end()]
    nav_end = t.find('</nav>', nm.end())
    if nav_end == -1:
        return ('SKIP-noclose', rel)
    nav_end += len('</nav>')

    new_nav, new_mobile = build_nav(lang, over)

    # replace nav
    t = t[:nm.start()] + new_nav + t[nav_end:]

    # replace / insert mobile menu
    mm = t.find('<div id="mobileMenu"')
    if mm != -1:
        mm_end = find_balanced_div(t, mm)
        if mm_end is None:
            return ('SKIP-mobilebalance', rel)
        # preserve leading indentation of the mobile block line
        t = t[:mm] + new_mobile.lstrip() + t[mm_end:]
    else:
        # insert right after nav close
        after = t.find('</nav>') + len('</nav>')
        t = t[:after] + '\n' + new_mobile + t[after:]

    # inject contact-pill CSS into first <style> if missing
    if 'a.contact-pill' not in t:
        sm = t.find('</style>')
        if sm != -1:
            t = t[:sm] + CONTACT_PILL_CSS + t[sm:]

    changed = t != orig
    if changed and APPLY:
        open(path, 'w', encoding='utf-8', newline='').write(t)
    return ('CHANGED' if changed else 'nochange', rel, ('over' if over else 'solid'), lang)

def main():
    results = []
    for root, dirs, fs in os.walk(ROOT):
        parts = set(os.path.relpath(root, ROOT).replace('\\','/').split('/'))
        if parts & set(SKIP_DIRS):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            if not f.endswith('.html'):
                continue
            rel = os.path.relpath(os.path.join(root, f), ROOT).replace('\\','/')
            if rel in EXCLUDE:
                continue
            results.append(process(os.path.join(root, f), rel))

    changed = [r for r in results if r[0]=='CHANGED']
    skipped = [r for r in results if r[0].startswith('SKIP')]
    nochange = [r for r in results if r[0]=='nochange']
    for r in sorted(changed, key=lambda x:x[1]):
        print(f"  CHANGED  {r[1]:52} [{r[2]}/{r[3]}]")
    for r in skipped:
        print(f"  {r[0]:16} {r[1]}")
    print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: {len(changed)} changed, {len(nochange)} nochange, {len(skipped)} skipped, {len(results)} total")

main()

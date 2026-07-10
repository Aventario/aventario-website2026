"""Ensure every unified-header page has the nav layout CSS (.nav-inner flex + over-hero rules).
Pages that already had the mainNav shell (impact/about/de homepages) already contain it;
solid pages (blog/services/etc.) that never used nav-inner need it injected."""
import os, re, sys

APPLY = '--apply' in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
             'style-comparison','_config','.vercel','.git','illustration-gallery')
EXCLUDE = {'index.html','index-b.html','index-c.html','index-v2.html','index.previous-pre-v03.html',
           'index.v03-draft.html','google3165196d202229c2.html','impressum.html','datenschutz.html',
           'webinar.html','webinar-thanks.html','de/impressum.html','de/datenschutz.html',
           'de/webinar.html','de/webinar-thanks.html'}

NAV_CSS = """
      nav#mainNav { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); will-change: transform; }
      nav#mainNav.nav-hidden { transform: translateY(-100%); }
      nav#mainNav .nav-inner { display: flex; justify-content: space-between; align-items: center; width: 100%; }
      nav#mainNav[data-over-hero] { transition: background-color 0.25s ease, border-color 0.25s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
      nav#mainNav[data-over-hero] .nav-inner a.nav-link { color: rgba(250,250,247,0.95); text-shadow: 0 1px 8px rgba(0,0,0,0.5); transition: color 0.25s ease, text-shadow 0.25s ease; }
      nav#mainNav[data-over-hero].past-hero .nav-inner a.nav-link { color: #334b60; text-shadow: none; }
      nav#mainNav[data-over-hero] .nav-inner a.nav-cta { background-color: rgba(250,250,247,0.18) !important; border: 1px solid rgba(250,250,247,0.7) !important; color: #FAFAF7 !important; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease; }
      nav#mainNav[data-over-hero].past-hero .nav-inner a.nav-cta { background-color: #334b60 !important; border-color: #334b60 !important; color: #FAFAF7 !important; -webkit-backdrop-filter: none; backdrop-filter: none; }
      nav#mainNav[data-over-hero] #mobileMenuBtn { color: #FAFAF7; text-shadow: 0 1px 8px rgba(0,0,0,0.5); transition: color 0.25s ease, text-shadow 0.25s ease; }
      nav#mainNav[data-over-hero].past-hero #mobileMenuBtn { color: #334b60; text-shadow: none; }
"""

n_inject = 0; n_have = 0; n_nostyle = 0
for root, dirs, fs in os.walk(ROOT):
    parts = set(os.path.relpath(root, ROOT).replace('\\','/').split('/'))
    if parts & set(SKIP_DIRS):
        dirs[:] = []; continue
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in fs:
        if not f.endswith('.html'): continue
        rel = os.path.relpath(os.path.join(root, f), ROOT).replace('\\','/')
        if rel in EXCLUDE: continue
        p = os.path.join(root, f)
        t = open(p, encoding='utf-8').read()
        if 'nav#mainNav .nav-inner' in t:
            n_have += 1; continue
        sm = t.find('</style>')
        if sm == -1:
            # no style block: add one before </head>
            hm = t.find('</head>')
            if hm == -1:
                n_nostyle += 1; print('  NO HEAD/STYLE', rel); continue
            block = '    <style>' + NAV_CSS + '    </style>\n'
            t = t[:hm] + block + t[hm:]
        else:
            t = t[:sm] + NAV_CSS + t[sm:]
        n_inject += 1
        if APPLY:
            open(p, 'w', encoding='utf-8', newline='').write(t)

print(f"{'APPLIED' if APPLY else 'DRY'}: injected {n_inject}, already-had {n_have}, no-style {n_nostyle}")

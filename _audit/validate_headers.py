import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
             'style-comparison','_config','.vercel','.git','illustration-gallery')
EXCLUDE = {'index.html','index-b.html','index-c.html','index-v2.html','index.previous-pre-v03.html',
           'index.v03-draft.html','google3165196d202229c2.html','impressum.html','datenschutz.html',
           'webinar.html','webinar-thanks.html','de/impressum.html','de/datenschutz.html',
           'de/webinar.html','de/webinar-thanks.html'}

problems = 0
checked = 0
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
        t = open(os.path.join(root, f), encoding='utf-8').read()
        checked += 1
        issues = []
        if t.count('<nav id="mainNav"') != 1: issues.append(f'mainNav x{t.count(chr(60)+"nav id=" + chr(34)+"mainNav"+chr(34))}')
        if t.count('id="mobileMenu"') != 1: issues.append(f'mobileMenu x{t.count(chr(34)+"mobileMenu"+chr(34))}')
        if 'contact-pill' not in t: issues.append('no contact-pill')
        if 'a.contact-pill{' not in t: issues.append('no pill CSS')
        if t.count('</nav>') < 1: issues.append('no /nav')
        if 'ph-calendar-check' not in t: issues.append('no icon')
        if 'aria-controls="mobileMenu"' not in t: issues.append('no aria-controls')
        # unbalanced div sanity: nav-inner present
        if 'nav-inner' not in t: issues.append('no nav-inner')
        # German pages must not say Impact/Resources/Contact label in nav; EN must not say Referenzen
        lang = 'de' if rel.startswith('de/') else 'en'
        navblock = t[t.find('<nav id="mainNav"'): t.find('</nav>')+6]
        if lang=='de' and 'Referenzen' not in navblock: issues.append('DE missing Referenzen')
        if lang=='en' and '>Impact<' not in navblock: issues.append('EN missing Impact')
        if lang=='en' and 'Referenzen' in navblock: issues.append('EN has German')
        if issues:
            problems += 1
            print(f'  PROBLEM {rel}: {", ".join(issues)}')

print(f'\nChecked {checked}, problems {problems}')

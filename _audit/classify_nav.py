import os, re

SKIP = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
        'style-comparison','_config','.vercel','.git','illustration-gallery')
EXCLUDE = {'index-b.html','index-c.html','index-v2.html','index.previous-pre-v03.html',
           'index.v03-draft.html','google3165196d202229c2.html'}

files=[]
for root,dirs,fs in os.walk('.'):
    parts = set(root.replace('\\','/').split('/'))
    if parts & set(SKIP):
        continue
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in fs:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(root,f)).replace('\\','/')
            files.append(rel)

files=sorted(set(files))
rows=[]
for fp in files:
    if fp in EXCLUDE:
        continue
    t=open(fp,encoding='utf-8').read()
    has_mainNav='id="mainNav"' in t
    over='data-over-hero' in t
    pill='contact-pill' in t
    toggle=('svcToggle' in t) or ('svc-tab' in t)
    mdbug = bool(re.search(r'contact\.html"[^>]*hidden md:inline-flex', t))
    m=re.search(r'aria-label="Aventario Home"><svg[^>]*class="([^"]*)"', t)
    logo=m.group(1) if m else '??'
    depth=fp.count('/')
    lang='de' if fp.startswith('de/') else 'en'
    rows.append((fp, lang, depth,
                 'mainNav' if has_mainNav else '-',
                 'over' if over else 'solid',
                 'pill' if pill else 'txt',
                 'TOG' if toggle else '-',
                 'mdbug' if mdbug else '', logo))

print("%-54s %-3s %-2s %-8s %-6s %-5s %-4s %-6s %s" % ('file','lg','d','nav','hero','btn','tog','bug','logo'))
for r in rows:
    print("%-54s %-3s %-2s %-8s %-6s %-5s %-4s %-6s %s" % r)
print("TOTAL", len(rows))

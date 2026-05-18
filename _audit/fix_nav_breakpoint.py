"""Move the mobile/desktop nav switch from md (768px) to lg (1024px).

At md exactly, the desktop nav + Contact Us pill exceeded the viewport by ~50px.
Bumping the breakpoint so tablet users (768-1023) use the burger menu fixes it without
shrinking anything on real desktop. Only touches the four nav-specific class strings;
all other md: utilities elsewhere on the page are left alone.
"""
from pathlib import Path

ROOT = Path(r"C:\Users\robid\Desktop\Aventario Claude\Aventario-Website-Draft\Aventario-Website")

# (old, new) pairs — uniquely identify nav classes by their wider context so we don't
# touch unrelated md:flex / md:hidden / md:inline-flex utilities elsewhere.
PATTERNS = [
    # Desktop horizontal menu row
    ('hidden md:flex space-x-8',
     'hidden lg:flex space-x-8'),
    # Contact Us pill at right of nav
    ('hidden md:inline-flex text-sm font-bold uppercase tracking-widest bg-text',
     'hidden lg:inline-flex text-sm font-bold uppercase tracking-widest bg-text'),
    # Mobile burger button
    ('md:hidden w-9 h-9 flex items-center justify-center',
     'lg:hidden w-9 h-9 flex items-center justify-center'),
    # Mobile menu drawer
    ('hidden md:hidden border-b border-bordercolor bg-base',
     'hidden lg:hidden border-b border-bordercolor bg-base'),
]

changes = {}
for p in ROOT.rglob('*.html'):
    if '_audit' in p.parts or 'style-comparison' in p.parts:
        continue
    src = p.read_text(encoding='utf-8')
    new = src
    for old, repl in PATTERNS:
        new = new.replace(old, repl)
    if new != src:
        n = sum(src.count(o) for o, _ in PATTERNS) - sum(new.count(o) for o, _ in PATTERNS)
        changes[str(p.relative_to(ROOT))] = n
        p.write_text(new, encoding='utf-8')

print(f"Patched {len(changes)} files")
for f, n in sorted(changes.items()):
    print(f"  {f}: {n} replacements")
print(f"Total replacements: {sum(changes.values())}")

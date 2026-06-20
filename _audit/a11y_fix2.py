#!/usr/bin/env python3
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = ('.vercel', '_staging', '_audit')
SKIP_NAMES = {'index-v2.html', 'index.previous-pre-v03.html', 'index.v03-draft.html'}

def is_prod(p):
    parts = p.parts
    if any(s in parts for s in SKIP_DIRS): return False
    if any(part.startswith('_backup') for part in parts): return False
    return p.name not in SKIP_NAMES

files = [p for p in ROOT.rglob('*.html') if is_prod(p)]
st = {'orange':0,'step_teal':0,'rgba_faint':0,'muted_text':0,'muted_white':0,'files':0}

for p in files:
    h = p.read_text(encoding='utf-8'); o = h
    # orange TEXT on light + white-on-orange BUTTON bg (both contain "color: #f19a51")
    # -> accessible deep amber. Gradients (no "color:" prefix) untouched.
    h, n = re.subn(r'color:(\s*)#f19a51', r'color:\1#B45309', h, flags=re.I); st['orange'] += n
    # step-num teal numbers on light -> accessible teal
    h, n = re.subn(r'(\.step-num\s*\{[^}]*color:\s*)#88C9BE', r'\g<1>#2C7A6B', h, flags=re.I); st['step_teal'] += n
    # ONLY faint rgba eyebrow labels (alpha <= 0.6, which fail) -> 0.7
    h, n = re.subn(r'rgba\(250,250,247,0\.([1-5][05]?|6)\)', 'rgba(250,250,247,0.7)', h); st['rgba_faint'] += n
    # muted secondary text on white -> darker to pass 4.5:1
    h, n = re.subn(r'\btext-text/60\b', 'text-text/80', h); st['muted_text'] += n
    h, n = re.subn(r'\btext-white/(40|50)\b', 'text-white/70', h); st['muted_white'] += n
    if h != o:
        p.write_text(h, encoding='utf-8'); st['files'] += 1

for k,v in st.items(): print(f"  {k}: {v}")

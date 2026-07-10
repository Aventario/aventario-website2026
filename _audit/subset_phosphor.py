"""Subset the Phosphor icon font + CSS to only the icons the site actually uses.
Original: phosphor.css 249KB + Phosphor.woff2 147KB + Phosphor-Fill.woff2 131KB = ~527KB.
The site uses ~75 icons. Output: a minimal CSS + two subset woff2 (~15-20KB total).

Backs up originals to _audit/phosphor-backup/. Overwrites in place so no page edits needed.
Run with --apply to write; default dry-run reports the plan + would-be sizes.
"""
import os, re, sys, shutil, io
from fontTools import subset
from fontTools.ttLib import TTFont

APPLY = '--apply' in sys.argv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PH = os.path.join(ROOT, 'assets', 'vendor', 'phosphor')
CSS = os.path.join(PH, 'phosphor.css')
BACKUP = os.path.join(ROOT, '_audit', 'phosphor-backup')

SKIP_DIRS = ('node_modules','_staging','_backup-legal-sweep-2026-06-15','_audit','_design',
             'style-comparison','_config','.vercel','.git','illustration-gallery')

# Safety margin: common icons that could be added dynamically; include even if not detected now.
SAFETY = {'ph-arrow-right','ph-arrow-left','ph-arrow-up','ph-arrow-down','ph-caret-right',
          'ph-caret-left','ph-caret-up','ph-caret-down','ph-check','ph-check-circle','ph-x',
          'ph-plus','ph-minus','ph-list','ph-arrow-up-right','ph-arrow-bend-down-right'}

# 1) collect used ph- names from ALL deployable HTML (captures static + inline JS) + site JS
used = set()
for root, dirs, fs in os.walk(ROOT):
    if set(os.path.relpath(root, ROOT).replace('\\','/').split('/')) & set(SKIP_DIRS):
        dirs[:] = []; continue
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in fs:
        if f.endswith('.html') or f.endswith('.js'):
            t = open(os.path.join(root, f), encoding='utf-8', errors='ignore').read()
            for m in re.findall(r'ph-[a-z0-9-]+', t):
                used.add(m)
# drop weight modifiers (not icon names)
weights = {'ph-fill','ph-bold','ph-thin','ph-light','ph-duotone','ph-regular'}
used -= weights
used |= SAFETY

# 2) map icon-name -> codepoint from the regular section of phosphor.css
css = open(CSS, encoding='utf-8').read()
name_cp = {}
for m in re.finditer(r'\.ph\.(ph-[a-z0-9-]+):before\s*\{\s*content:\s*"\\([0-9a-fA-F]+)"', css):
    name_cp[m.group(1)] = int(m.group(2), 16)

used_named = sorted(n for n in used if n in name_cp)
missing = sorted(n for n in used if n not in name_cp)
codepoints = sorted({name_cp[n] for n in used_named})

print(f"Used icon names detected: {len(used)}; mapped to codepoints: {len(used_named)}; unmapped: {missing}")
print(f"Distinct codepoints to keep: {len(codepoints)}")

# 3) build minimal CSS
def font_face(family, woff2):
    return (f'@font-face{{font-family:"{family}";'
            f'src:url("./{woff2}") format("woff2");'
            f'font-weight:normal;font-style:normal;font-display:block;}}\n')

base = ('.ph,.ph-fill,.ph-bold{speak:never;font-style:normal;font-weight:normal;font-variant:normal;'
        'text-transform:none;line-height:1;-webkit-font-smoothing:antialiased;'
        '-moz-osx-font-smoothing:grayscale;display:inline-block;}\n'
        '.ph{font-family:"Phosphor"!important;}\n'
        '.ph-fill{font-family:"Phosphor-Fill"!important;}\n'
        '.ph-bold{font-family:"Phosphor-Bold"!important;}\n')

rules = []
for n in used_named:
    rules.append(f'.ph.{n}:before,.ph-fill.{n}:before,.ph-bold.{n}:before{{content:"\\{name_cp[n]:x}";}}')
min_css = ('/* Phosphor subset — only site-used icons. Original backed up in _audit/phosphor-backup/. */\n'
           + font_face('Phosphor','Phosphor.woff2')
           + font_face('Phosphor-Fill','Phosphor-Fill.woff2')
           + font_face('Phosphor-Bold','Phosphor-Bold.woff2')
           + base + '\n'.join(rules) + '\n')

# 4) subset the two fonts
def subset_font(src, unicodes):
    ss = subset.Subsetter()
    font = TTFont(src)
    ss.populate(unicodes=unicodes)
    ss.subset(font)
    buf = io.BytesIO()
    font.flavor = 'woff2'
    font.save(buf)
    return buf.getvalue()

reg_src = os.path.join(PH,'Phosphor.woff2')
fill_src = os.path.join(PH,'Phosphor-Fill.woff2')
bold_src = os.path.join(PH,'Phosphor-Bold.woff2')
reg_new = subset_font(reg_src, codepoints)
fill_new = subset_font(fill_src, codepoints)
bold_new = subset_font(bold_src, codepoints)

print("\n== size report ==")
print(f"  phosphor.css : {os.path.getsize(CSS)//1024}KB -> {len(min_css.encode())/1024:.1f}KB")
print(f"  Phosphor.woff2     : {os.path.getsize(reg_src)//1024}KB -> {len(reg_new)/1024:.1f}KB")
print(f"  Phosphor-Fill.woff2: {os.path.getsize(fill_src)//1024}KB -> {len(fill_new)/1024:.1f}KB")
print(f"  Phosphor-Bold.woff2: {os.path.getsize(bold_src)//1024}KB -> {len(bold_new)/1024:.1f}KB")

if APPLY:
    os.makedirs(BACKUP, exist_ok=True)
    for fn in ['phosphor.css','Phosphor.woff2','Phosphor-Fill.woff2','Phosphor-Bold.woff2']:
        p = os.path.join(PH, fn)
        if os.path.exists(p) and not os.path.exists(os.path.join(BACKUP, fn)):
            shutil.copy2(p, os.path.join(BACKUP, fn))
    open(CSS,'w',encoding='utf-8',newline='').write(min_css)
    open(reg_src,'wb').write(reg_new)
    open(fill_src,'wb').write(fill_new)
    open(bold_src,'wb').write(bold_new)
    print("\nAPPLIED. Originals backed up to _audit/phosphor-backup/")
else:
    print("\nDRY-RUN (pass --apply to write)")

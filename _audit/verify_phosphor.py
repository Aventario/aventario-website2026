import re
from fontTools.ttLib import TTFont

css = open('assets/vendor/phosphor/phosphor.css', encoding='utf-8').read()
cps = sorted({int(m, 16) for m in re.findall(r'content:"\\([0-9a-fA-F]+)"', css)})
print("codepoints referenced in minimal css:", len(cps))
ok = True
for fn in ['Phosphor.woff2', 'Phosphor-Fill.woff2', 'Phosphor-Bold.woff2']:
    f = TTFont('assets/vendor/phosphor/' + fn)
    cmap = f.getBestCmap()
    missing = [hex(c) for c in cps if c not in cmap]
    if missing:
        ok = False
    print(f"  {fn:22} glyphs: {len(cmap):3}  missing-from-used: {missing if missing else 'NONE'}")
print("ALL COVERED" if ok else "!!! MISSING GLYPHS !!!")

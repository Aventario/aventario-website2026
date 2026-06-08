#!/usr/bin/env python3
# Idempotent site-wide pass: (1) add "Services" -> portfolio.html nav entry
# before the Impact link (desktop + mobile, prefix-aware), (2) inject a
# :focus-visible outline into each page's first <style>, (3) tighten the
# desktop nav spacing from space-x-8 to space-x-6 to absorb the 5th item.
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent  # website/
EXCLUDE_DIRS = {"node_modules", "_staging", ".vercel", "_audit",
                "style-comparison", "illustration-gallery", "_build", "logos"}
EXCLUDE_FILES = {"index-v2.html", "index.v03-draft.html",
                 "index.previous-pre-v03.html"}

FOCUS_CSS = (
    "\n        /* Keyboard focus visibility (a11y) */\n"
    "        :focus-visible { outline: 2px solid #5FA99D; outline-offset: 2px; border-radius: 3px; }\n"
    "        :focus:not(:focus-visible) { outline: none; }\n"
)

# desktop nav link: <a href="{P}impact.html" class="hover:text-accentdark">Impact</a>
DESKTOP_RE = re.compile(
    r'(<a href="((?:\.\./)*)impact\.html" class="hover:text-accentdark">Impact</a>)')
# mobile nav link
MOBILE_RE = re.compile(
    r'(<a href="((?:\.\./)*)impact\.html" class="block py-2 text-base font-bold '
    r'uppercase tracking-widest hover:text-accentdark">Impact</a>)')

def process(path: pathlib.Path):
    src = path.read_text(encoding="utf-8")
    orig = src
    notes = []

    # 1a. desktop Services link (skip if a portfolio.html Services link already there)
    if 'portfolio.html" class="hover:text-accentdark">Services</a>' not in src:
        def d(m):
            p = m.group(2)
            return f'<a href="{p}portfolio.html" class="hover:text-accentdark">Services</a>\n            ' + m.group(1)
        src, n = DESKTOP_RE.subn(d, src, count=1)
        if n: notes.append("nav-desktop")

    # 1b. mobile Services link
    if 'portfolio.html" class="block py-2 text-base font-bold' not in src:
        def mob(m):
            p = m.group(2)
            return (f'<a href="{p}portfolio.html" class="block py-2 text-base font-bold '
                    f'uppercase tracking-widest hover:text-accentdark">Services</a>\n        ' + m.group(1))
        src, n = MOBILE_RE.subn(mob, src, count=1)
        if n: notes.append("nav-mobile")

    # 2. tighten desktop nav spacing
    nav_cls = 'class="hidden lg:flex space-x-8 text-sm uppercase tracking-widest font-bold items-center"'
    if nav_cls in src:
        src = src.replace(nav_cls,
            'class="hidden lg:flex space-x-6 text-sm uppercase tracking-widest font-bold items-center"')
        notes.append("nav-spacing")

    # 3. focus-visible into first <style>
    if ":focus-visible" not in src and "<style>" in src:
        src = src.replace("<style>", "<style>" + FOCUS_CSS, 1)
        notes.append("focus-visible")

    if src != orig:
        path.write_text(src, encoding="utf-8")
        return notes
    return None

def main():
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts): continue
        if path.name in EXCLUDE_FILES: continue
        notes = process(path)
        if notes:
            changed += 1
            print(f"  {rel}  ->  {', '.join(notes)}")
    print(f"\n{changed} files updated.")

if __name__ == "__main__":
    main()

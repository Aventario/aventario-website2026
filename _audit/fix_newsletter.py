#!/usr/bin/env python3
# Fix pre-existing tablet (1024px) horizontal overflow: the footer newsletter
# email input is flex-1 with default min-width:auto, so it won't shrink and
# pushes the whitespace-nowrap "Subscribe" button past the narrow footer
# column. Add min-w-0 so the flex item can shrink. Idempotent, live pages only.
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"node_modules", "_staging", ".vercel", "_audit",
                "style-comparison", "illustration-gallery", "_build", "logos"}
EXCLUDE_FILES = {"index-v2.html", "index.v03-draft.html",
                 "index.previous-pre-v03.html"}

# match an <input type="email" ...> whose class contains flex-1 but not min-w-0
INPUT_RE = re.compile(r'(<input type="email"[^>]*?class=")([^"]*?)(")')

def fix(m):
    pre, cls, post = m.group(1), m.group(2), m.group(3)
    if "min-w-0" in cls or "flex-1" not in cls:
        return m.group(0)
    cls = cls.replace("flex-1", "flex-1 min-w-0", 1)
    return pre + cls + post

def main():
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(p in EXCLUDE_DIRS for p in rel.parts): continue
        if path.name in EXCLUDE_FILES: continue
        src = path.read_text(encoding="utf-8")
        new = INPUT_RE.sub(fix, src)
        if new != src:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"{changed} files updated.")

if __name__ == "__main__":
    main()

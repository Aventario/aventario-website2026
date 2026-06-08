#!/usr/bin/env python3
# Idempotent AA-contrast pass on live pages:
#  - darken cross-functional label #b97228 -> #8a5214 (passes 4.5:1 on light)
#  - lift footer section-label opacity rgba(250,250,247,0.6) -> 0.74 on navy
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"node_modules", "_staging", ".vercel", "_audit",
                "style-comparison", "illustration-gallery", "_build", "logos"}
EXCLUDE_FILES = {"index-v2.html", "index.v03-draft.html",
                 "index.previous-pre-v03.html"}
SUBS = [
    ("#b97228", "#8a5214"),
    ("rgba(250,250,247,0.6)", "rgba(250,250,247,0.74)"),
    ("rgba(250, 250, 247, 0.6)", "rgba(250, 250, 247, 0.74)"),
]

def main():
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if any(p in EXCLUDE_DIRS for p in rel.parts): continue
        if path.name in EXCLUDE_FILES: continue
        src = path.read_text(encoding="utf-8")
        orig = src
        hits = []
        for a, b in SUBS:
            if a in src:
                src = src.replace(a, b)
                hits.append(a)
        if src != orig:
            path.write_text(src, encoding="utf-8")
            changed += 1
            print(f"  {rel}  ->  {', '.join(hits)}")
    print(f"\n{changed} files updated.")

if __name__ == "__main__":
    main()

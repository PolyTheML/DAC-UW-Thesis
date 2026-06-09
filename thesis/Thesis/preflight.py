#!/usr/bin/env python3
"""Pre-flight checks on the converted chapters (run before an Overleaf upload).
Catches compile-killers we cannot test locally (no TeX installed):
  - brace { } imbalance
  - longtable \caption placed before \toprule (not inside the column spec)
  - \fg{} figures whose image file is missing from images/
  - leftover [FIGURE / [@ placeholders
Run from repo root:  python thesis/Thesis/preflight.py
"""
import glob, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
CH = sorted(glob.glob(os.path.join(ROOT, "Chapters", "ch[1-6]-*.tex")))
IMG = os.path.join(ROOT, "images")

problems = 0

def flag(msg):
    global problems
    problems += 1
    print("  PROBLEM:", msg)

for fp in CH:
    name = os.path.basename(fp)
    t = open(fp, encoding="utf-8").read()
    lines = t.split("\n")

    bal = t.count("{") - t.count("}")
    if bal:
        flag(f"{name}: brace imbalance {bal:+d}")

    caps = before = 0
    for i, l in enumerate(lines):
        if l.startswith("\\caption{"):
            caps += 1
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if nxt.startswith("\\toprule"):
                before += 1
            else:
                flag(f"{name}:{i+1}: \\caption NOT before \\toprule -> {nxt[:50]!r}")

    for m in re.finditer(r"\\fg\{[^}]*\}\{.*?\}\{images/([^}]+)\}", t):
        img = m.group(1)
        if not os.path.exists(os.path.join(IMG, img)):
            flag(f"{name}: missing image images/{img}")

    for ph in ("[FIGURE", "[@"):
        if ph in t:
            flag(f"{name}: leftover placeholder {ph!r}")

    figs = t.count("\\fg{")
    print(f"  {name:26s} braces={'ok' if not bal else bal:>3} "
          f"tables={caps:2d} (caption_ok={before}) figs={figs}")

print(f"\n{'PASS' if problems == 0 else str(problems)+' PROBLEM(S)'}")

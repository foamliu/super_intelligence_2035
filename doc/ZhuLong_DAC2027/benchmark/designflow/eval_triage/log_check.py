#!/usr/bin/env python3
"""Parse a LaTeX main.log: page count, Overfull boxes, undefined refs/cites, warning list.

Read-only w.r.t. the paper dir (log lives in a temp copy).

Usage:  python log_check.py <path to main.log>
"""
import re
import sys
from pathlib import Path

log = Path(sys.argv[1] if len(sys.argv) > 1 else "main.log")
txt = log.read_text(encoding="utf-8", errors="replace")
lines = txt.splitlines()

print(f"log: {log}   size={log.stat().st_size} bytes   lines={len(lines)}")

# ---- output / pages
m = re.search(r"Output written on .*?\((\d+) pages?, (\d+) bytes\)", txt)
print(f"Output written: {m.group(0) if m else 'NOT FOUND'}")

# ---- hard errors
errs = [l for l in lines if l.startswith("!")]
print(f"\n'!' hard errors: {len(errs)}")
for e in errs[:10]:
    print("  " + e)

# ---- overfull / underfull
over = []
for i, l in enumerate(lines):
    mm = re.match(r"Overfull \\hbox \((\d+\.\d+)pt too wide\)(.*)", l)
    if mm:
        over.append((float(mm.group(1)), l.strip(), lines[i + 1].strip() if i + 1 < len(lines) else ""))
over.sort(reverse=True)
print(f"\nOverfull \\hbox total: {len(over)}   >20pt: {sum(1 for o in over if o[0] > 20)}")
for pt, l, ctx in over[:12]:
    print(f"  {pt:6.1f}pt  {l[:110]}")
uh = sum(1 for l in lines if l.startswith("Underfull \\hbox"))
uv = sum(1 for l in lines if l.startswith("Underfull \\vbox"))
print(f"\nUnderfull \\hbox: {uh}")
print(f"Underfull \\vbox: {uv}")

# ---- undefined refs / citations
cites = re.findall(r"Citation `([^']+)' on page (\d+) undefined", txt)
refs = re.findall(r"Reference `([^']+)' on page (\d+) undefined", txt)
print(f"\nUndefined citations: {len(cites)} unique={sorted(set(c[0] for c in cites))}")
print(f"Undefined references: {len(refs)} unique={sorted(set(r[0] for r in refs))}")
print("  'There were undefined citations' present:",
      "There were undefined citations" in txt)
print("  'There were undefined references' present:",
      "There were undefined references" in txt)

# ---- first 10 warnings (in order)
warns = [(i + 1, l.strip()) for i, l in enumerate(lines) if l.startswith("LaTeX Warning")
         or l.startswith("Package ") and "Warning" in l]
print(f"\nTotal warning lines: {len(warns)}; first 10:")
for ln, w in warns[:10]:
    print(f"  L{ln}: {w[:130]}")

#!/usr/bin/env python3
"""Read-only ledger scan of the paper .tex/.py sources for key numbers.

Emits  file:line: <tok> :: <trimmed source line>
so the audit report can quote exact locations.  Never writes to the paper dir.

Usage:  python ledger_scan.py
"""
import re
from pathlib import Path

PAPER = Path(r"D:\Users\Administrator\code\super_intelligence_2035\doc\ZhuLong_DAC2027"
             r"\EDA-LiveFlow-Bench_ICML2027")
FILES = ["main.tex", "sections/0_abstract.tex", "sections/1_intro.tex",
         "sections/2_benchmark.tex", "sections/3_harness.tex",
         "sections/4_experiments.tex", "sections/5_analysis.tex",
         "sections/6_related.tex", "sections/7_conclusion.tex",
         "sections/8_ethics.tex", "sections/9_reproducibility.tex",
         "appendix/A_benchmark_details.tex", "appendix/B_additional_results.tex",
         "appendix/C_experimental_details.tex", "figures/make_figs.py"]

# (label, regex).  Boundary-aware so 620 does not fire inside 1620 etc.
TOKENS = [
    ("696",  r"(?<![0-9.])696(?![0-9])"),
    ("620",  r"(?<![0-9.])620(?![0-9])"),
    ("626",  r"(?<![0-9.])626(?![0-9])"),
    ("62",   r"(?<![0-9.])62(?![0-9])"),
    ("558",  r"(?<![0-9.])558(?![0-9])"),
    ("70",   r"(?<![0-9.])70(?![0-9])"),
    ("6",    r"(?<![0-9.])6(?![0-9.])"),
    ("10.0", r"10\.0"),
    ("9.9",  r"9\.9(?!\d)"),
    ("76.5", r"76\.5"),
    ("76",   r"(?<![0-9.])76(?![0-9%.])"),
    ("1007", r"(?<![0-9.])1007(?![0-9])"),
]

total = 0
for rel in FILES:
    p = PAPER / rel
    if not p.exists():
        print(f"!! missing: {rel}")
        continue
    hits = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        found = [lab for lab, rx in TOKENS if re.search(rx, line)]
        if found:
            hits.append((i, ",".join(found), line.strip()[:180]))
    if not hits:
        continue
    print(f"\n===== {rel}  ({len(hits)} lines with hits) =====")
    for i, toks, snippet in hits:
        total += 1
        print(f"{rel}:{i}: [{toks}] {snippet}")
print(f"\nTOTAL matching lines = {total}")

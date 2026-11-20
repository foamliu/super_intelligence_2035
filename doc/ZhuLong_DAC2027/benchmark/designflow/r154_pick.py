#!/usr/bin/env python3
"""Round 154 candidate picker: prioritize pg_layout, fallback layout."""
import re, sys, subprocess

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
LEDGER  = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_C.tsv"

# load ledger anchors (col 1 session_file base)
used = set()
with open(LEDGER) as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if not p or not p[0]: continue
        used.add(p[0].replace(".messages.json",""))

PG_KW = re.compile(r"pg|power|ground|stripe|mesh|\bring\b|prRoute|specialRoute|addStripe|editPower|fplan|floorplan| PG |vdd|vss|gnd", re.I)
LAY_KW = re.compile(r"calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pex|cellview|dbCreate", re.I)

cands_pg = []
cands_lay = []
with open(SUMMARY) as f:
    header = next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 7: continue
        try: mc = int(p[4])
        except: continue
        if mc < 30: continue
        sess = p[3].replace(".messages.json","")
        if sess in used: continue
        tools_field = p[6]
        if not LAY_KW.search(tools_field):
            continue
        row = (mc, sess, p[2], p[1], tools_field[:200])
        if PG_KW.search(tools_field):
            cands_pg.append(row)
        else:
            cands_lay.append(row)

cands_pg.sort(reverse=True)
cands_lay.sort(reverse=True)
print("=== pg_layout candidates (top 15) ===")
for r in cands_pg[:15]:
    print("\t".join(map(str,r)))
print("=== layout (non-pg) candidates (top 5) ===")
for r in cands_lay[:5]:
    print("\t".join(map(str,r)))
print(f"\nTOTAL: pg={len(cands_pg)} lay={len(cands_lay)}")

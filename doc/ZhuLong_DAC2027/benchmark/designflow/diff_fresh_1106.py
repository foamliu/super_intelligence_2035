#!/usr/bin/env python3
"""Diff spice_candidates_NEW.tsv (from .75 19:2x rescan) against ledger_B anchors.
Output fresh candidates not yet in ledger, sorted by match_count desc."""
import sys, csv, re

LEDGER = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_B.tsv"
CANDS = sys.argv[1] if len(sys.argv) > 1 else "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/_cands_b_1106.tsv"

# Collect ledger anchors (strip .messages.json / .json / .messages.archive.json suffixes for robust match)
anchors = set()
with open(LEDGER) as f:
    next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4: continue
        sess = parts[0]
        # strip suffixes
        for suf in (".messages.archive.json", ".messages.json", ".json"):
            if sess.endswith(suf):
                sess = sess[:-len(suf)]
                break
        anchors.add(sess)

print(f"# ledger anchors: {len(anchors)}", file=sys.stderr)

fresh = []
seen_sess = set()
with open(CANDS) as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        sess = row["session_file"]
        base = sess
        for suf in (".messages.archive.json", ".messages.json", ".json"):
            if base.endswith(suf):
                base = base[:-len(suf)]
                break
        if base in anchors: continue
        if base in seen_sess: continue  # dedup across hosts
        seen_sess.add(base)
        mc = int(row["match_count"])
        row["_base"] = base
        fresh.append((mc, row))

fresh.sort(key=lambda x: -x[0])
print(f"# fresh candidates: {len(fresh)}", file=sys.stderr)
print("# match_count\tsession_base\tuser\thost\tip\tspice_count\tspice_ratio")
for mc, row in fresh:
    print(f"{mc}\t{row['_base']}\t{row['user']}\t{row['host']}\t{row['ip']}\t{row['spice_count']}\t{row['spice_ratio']}")

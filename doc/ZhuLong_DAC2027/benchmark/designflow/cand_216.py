#!/usr/bin/env python3
"""Shard D candidate picker #214: read summary.tsv on .75, exclude 296 anchors
from all 5 ledgers, score by netlist/schematic/waveform/analog keywords,
dedup-by-anchor, print top N live candidates with high match_count.
"""
import sys, re

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
EXCL_FILE = "excl_216.txt"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 25
MC_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 150

EXCL = set()
with open(EXCL_FILE) as f:
    for line in f:
        a = line.strip()
        if a:
            EXCL.add(a)

KW = {
    "waveview": 4, "cosmos": 3, "spectrum": 3,
    "netlist": 5, "spiros": 4, "schematic": 5,
    "analog": 4, "skill": 2, "hspice": 5, "spice": 4,
    "cdl": 4, "spectre": 4, "waveform": 5,
    "transistor": 2, "opamp": 2, "inverter": 2, "comparator": 2,
    "delay": 2, "duty": 1, "trtf": 2, "toggle": 2,
}
PENALTY = {
    "layout": 3, "calibre": 2, "drc": 2, "lvs": 2, "innovus": 4,
    "pnr": 4, "physical": 3, "gds": 3, "place": 2, "route": 2,
    "verilog": 1, "systemverilog": 2, "rtl": 2, "synthesis": 2,
}

cands = []
seen_anchor = set()
with open(SUMMARY) as f:
    header = next(f, None)
    for line in f:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue
        ip, host, user, sf, mc, kws, tools = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]
        try:
            mcn = int(mc)
        except ValueError:
            continue
        if mcn < MC_MIN:
            continue
        anc = re.sub(r"\.messages\.json$", "", sf)
        if anc in EXCL or anc in seen_anchor:
            continue
        toks = (kws + " " + tools).lower()
        if not any(k in toks for k in ("waveview", "cosmos", "spectrum", "netlist",
                                        "spiros", "schematic", "analog", "hspice",
                                        "spice", "cdl", "spectre", "waveform")):
            continue
        score = sum(w for k, w in KW.items() if k in toks)
        score -= sum(w for k, w in PENALTY.items() if k in toks)
        seen_anchor.add(anc)
        cands.append((mcn, score, anc, user, host, kws, tools, ip))

cands.sort(key=lambda c: (-c[1], -c[0]))
for mcn, score, anc, user, host, kws, tools, ip in cands[:N]:
    print(f"{mcn}\t{score}\t{anc}\t{user}\t{host}\t{ip}\t{kws}|{tools}")
print(f"# total eligible: {len(cands)}")

#!/usr/bin/env python3
"""Shard B (spice_char) candidate picker #220: read summary.tsv on .75, exclude
anchors from excl_B_220.txt (shard B ledger anchors), keep only spice/sim tools,
score by spice-char keywords, dedup-by-anchor, print top N live candidates.
"""
import sys, re

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
EXCL_FILE = "excl_B_220.txt"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
MC_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 30

EXCL = set()
with open(EXCL_FILE) as f:
    for line in f:
        a = line.strip()
        if a:
            EXCL.add(a)

# Spice/characterization core keywords (shard B = characterization + spice_sim)
SPICE_TOOLS = ("hspice", "finesim", "siliconsmart", "spectre", "ngspice",
               "simulator", "spice", "custom_sim", "waveview")

KW = {
    "hspice": 6, "finesim": 6, "spectre": 5, "ngspice": 5,
    "siliconsmart": 6, "spice": 4, "custom_sim": 5, "simulator": 3,
    "waveview": 4, "measure": 3, "tran": 2, "ac": 1, "dc": 1,
    "netlist": 4, "cdl": 3, "modelcard": 4, "pdk": 2,
    "characterization": 5, "char": 3, "vth": 3, "gm": 2, "id": 1,
    "montecarlo": 4, "mc": 2, "alter": 3, "corner": 3, "pvt": 3,
    "opamp": 3, "inverter": 2, "comparator": 3, "sram": 2, "ring": 2,
    "oscillator": 3, "pll": 3, "cp": 2, "charge": 2, "strongarm": 3,
    "sense": 2, "latch": 2, "jitter": 3, "noise": 3, "psm": 2,
    "trtf": 3, "duty": 2, "delay": 2, "setup": 2, "hold": 2,
    "stimulus": 2, "testbench": 3, "tb": 1, "deck": 2, "subckt": 3,
}
PENALTY = {
    "layout": 4, "calibre": 4, "drc": 3, "lvs": 3, "innovus": 5,
    "pnr": 5, "physical": 4, "gds": 4, "place": 3, "route": 3,
    "verilog": 3, "systemverilog": 4, "rtl": 3, "synthesis": 3,
    "apr": 4, "cts": 3, "sta": 2, "lef": 3, "def": 3, "spef": 2,
    "aether": 1, "virtuoso": 1, "skill": 2, "pyaether": 3,
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
        # Must contain at least one spice/sim tool
        if not any(k in toks for k in SPICE_TOOLS):
            continue
        # Reject if dominant physical/layout (penalty overwhelms spice)
        score = sum(w for k, w in KW.items() if k in toks)
        score -= sum(w for k, w in PENALTY.items() if k in toks)
        if score <= 0:
            continue
        seen_anchor.add(anc)
        cands.append((mcn, score, anc, user, host, kws, tools, ip))

cands.sort(key=lambda c: (-c[1], -c[0]))
for mcn, score, anc, user, host, kws, tools, ip in cands[:N]:
    print(f"{mcn}\t{score}\t{anc}\t{user}\t{host}\t{ip}\t{kws}|{tools}")
print(f"# total eligible: {len(cands)}")
print(f"# EXCL size: {len(EXCL)}")

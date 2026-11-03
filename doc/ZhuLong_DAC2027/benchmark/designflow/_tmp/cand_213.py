#!/usr/bin/env python3
# Candidate scoring for shard D (analog_context, schematic_netlist, waveform)
# Reads exclusion set, scores summary.tsv by D-core keywords, dedup by anchor.
import sys, re
from collections import defaultdict

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv"
EXCL = "excl_213.txt"

# load exclusion set (anchors without .messages.json suffix)
excl = set()
with open(EXCL) as f:
    for line in f:
        a = line.strip()
        if a:
            excl.add(a)

# D-core keyword weights (analog_context / schematic_netlist / waveform)
KW_NN = {  # netlist/schematic core
    "netlist": 3, "schematic": 3, "cdl": 3, "spice": 3, "hspice": 3,
    "subckt": 3, "instance": 2, "verilog": 2, "module": 2,
    "lvs": 3, "erc": 2, "calibre": 2,
}
KW_NS = {  # analog/sim
    "analog": 3, "cmos": 2, "opamp": 3, "bandgap": 3, " comparator": 3,
    "waveview": 4, "waveform": 4, "cosmos": 3, "spiros": 3, "spectrum": 3,
    "tran": 2, "ac": 1, "dc": 1, "pwl": 3, "stimulus": 3, "stim": 3,
    "pyaether": 2, "aether": 2, "virtuoso": 2,
}
KW_BOOST = {"waveview": 6, "waveform": 6, "pwl": 5, "stimulus": 5, "netlist": 4, "hspice": 4, "schematic": 4}
KW_DEMOTE = {"layout": -5, "drc": -3, "innovus": -8, "pnr": -8, "place": -5, "route": -5, "rtl": -3, "dc_shell": -6, "pt_shell": -6, "formality": -6, "conformal": -6}

def score(tools_str):
    s = 0
    tl = tools_str.lower()
    for k, w in KW_NN.items():
        if k in tl: s += w
    for k, w in KW_NS.items():
        if k in tl: s += w
    for k, w in KW_BOOST.items():
        if k in tl: s += w
    for k, w in KW_DEMOTE.items():
        if k in tl: s += w
    return s

# parse summary.tsv
# columns: ip host user session_file match_count keywords tools
best = {}  # anchor -> (score, match, session, user, host, tools, keywords)
with open(SUMMARY) as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 7: continue
        ip, host, user, sf, mc, kw, tools = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
        try:
            mcv = int(mc)
        except:
            continue
        if mcv < 150: continue
        anchor = sf
        anchor_bare = re.sub(r"\.messages\.json$", "", anchor)
        if anchor_bare in excl: continue
        # D-domain filter: tools must contain D-core
        tl = tools.lower()
        if not any(k in tl for k in ("netlist","schematic","waveview","waveform","analog","spice","hspice","cosmos","spiros","spectrum","cdl","opamp","bandgap","pwl","stimulus")):
            continue
        sc = score(tools) + min(mcv, 800)//50  # mild match_count boost
        # dedup by anchor keep best
        if anchor_bare not in best or sc > best[anchor_bare][0]:
            best[anchor_bare] = (sc, mcv, anchor, user, host, tools, kw)

ranked = sorted(best.values(), key=lambda x: -x[0])
print(f"# total fresh eligible: {len(ranked)}")
print("# rank\tscore\tmatch\tsession\tuser\thost\ttools")
for i, (sc, mcv, sf, user, host, tools, kw) in enumerate(ranked[:40]):
    print(f"{i+1}\t{sc}\t{mcv}\t{sf}\t{user}\t{host}\t{tools}")

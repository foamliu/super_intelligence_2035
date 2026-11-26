#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-SacapSpfCouplingExtract-001 (shard C, r262).
Generates assets (A + hidden B), reference (golden_solution + golden_B + check + negatives).
Grounded on real rongtaoy sacap_extract.py (vtz09 trace, /home/rongtaoy/Documents/python/coupling_compare/).
"""
import os, sys, re, json, csv, zipfile, shutil, subprocess, hashlib, io

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SacapSpfCouplingExtract-001"
ADIR = os.path.join(BASE, "assets", CID)
RDIR = os.path.join(BASE, "reference", CID)

def reset_dir(d):
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

# ============================================================
# 1. Synthetic StarRC .spf_CC generator
# ============================================================
# Format:
#   *|NET <netname> <pincap>     -- node row (pincap in fF, written as <val>e-15PF)
#   C<id> <net1> <net2> <cap>    -- coupling cap row (cap in fF, written as <val>e-15PF)
# Group formula (mirrors real sacap_extract.py v1.7a):
#   cn<col>bla|blb<n>  col<=7 -> col*256+n+0 ;  col>=8 -> col*256+n+320
#   cec<col>bla|blb<n>          -> col*256+n+2048

def group_of(net):
    m = re.fullmatch(r'cn(\d+)bl([ab])<(\d+)>', net, re.I)
    if m:
        col, n = int(m.group(1)), int(m.group(3))
        return col*256 + n + (0 if col <= 7 else 320)
    m = re.fullmatch(r'cec(\d+)bl([ab])<(\d+)>', net, re.I)
    if m:
        return int(m.group(1))*256 + int(m.group(3)) + 2048
    return None

def ff_str(val_fF):
    # write cap as scientific notation farads (no PF suffix); to_ff does float(s)*1e15 -> fF
    return "%.6e" % (val_fF * 1e-15)

def make_spf(top_bl_defs, couplings, pincaps, extra_nets=None):
    """top_bl_defs: list of (netname) for top-level bitlines.
    couplings: list of (net1, net2, cap_fF).
    pincaps: dict netname -> pin_cap_fF (for *|NET rows of bitlines).
    extra_nets: list of (netname, pincap_fF) for signal nets (NCSin_0 etc.) pin rows.
    Returns SPF text."""
    lines = []
    lines.append("*|SPF_FILE msaq_U_CCR_fBcc_int.spf_CC")
    lines.append("*|EXTRACTION:C")
    # NET rows for top-level bitlines
    for net in top_bl_defs:
        pc = pincaps.get(net, 0.0)
        lines.append("*|NET %s %s" % (net, ff_str(pc)))
    # NET rows for signal/other nets
    if extra_nets:
        for net, pc in extra_nets:
            lines.append("*|NET %s %s" % (net, ff_str(pc)))
    # Coupling C rows
    for i, (n1, n2, cap) in enumerate(couplings):
        lines.append("C%d %s %s %s" % (i+1, n1, n2, ff_str(cap)))
    return "\n".join(lines) + "\n"

# ---- A input (visible to SUT) ----
# Groups: 0,1 (cn00 col0), 256 (cn01 col1), 2368 (cn08 col8 +320), 4096,4097 (cec08 col8 +2048)
A_top = [
    "cn00bla<0>", "cn00blb<0>",   # group 0
    "cn00bla<1>", "cn00blb<1>",   # group 1
    "cn01bla<0>", "cn01blb<0>",   # group 256
    "cn08bla<0>", "cn08blb<0>",   # group 2368
    "cec08bla<0>", "cec08blb<0>", # group 4096
    "cec08bla<1>", "cec08blb<1>", # group 4097
]
A_pincaps = {
    "cn00bla<0>":10.0, "cn00blb<0>":9.0,
    "cn00bla<1>":11.0, "cn00blb<1>":8.5,
    "cn01bla<0>":12.0, "cn01blb<0>":10.5,
    "cn08bla<0>":13.0, "cn08blb<0>":11.5,
    "cec08bla<0>":14.0, "cec08blb<0>":12.5,
    "cec08bla<1>":9.5,  "cec08blb<1>":8.0,
}
A_couplings = [
    # intra-group (group0: cn00bla<0><->cn00bla<1> is NOT intra; cn00bla<0> is g0, cn00bla<1> is g1)
    # group0 <-> group1
    ("cn00bla<0>","cn00bla<1>",1.5),
    # group0 <-> group256
    ("cn00bla<0>","cn01bla<0>",2.0),
    ("cn00bla<0>","cn01blb<0>",1.0),
    ("cn00blb<0>","cn01bla<0>",0.8),
    ("cn00blb<0>","cn01blb<0>",1.2),
    # group0 <-> group2368
    ("cn00bla<0>","cn08bla<0>",3.0),
    # group0 <-> group4096
    ("cn00bla<0>","cec08bla<0>",2.5),
    # group256 <-> group2368
    ("cn01bla<0>","cn08bla<0>",1.8),
    # group2368 <-> group4096
    ("cn08bla<0>","cec08bla<0>",2.2),
    # group4096 <-> group4097
    ("cec08bla<0>","cec08bla<1>",1.1),
    # signals
    ("cn00bla<0>","NCSin_0",0.5),
    ("cn00blb<0>","NCSin_0",0.4),
    ("cn00bla<0>","PCSin_0",0.6),
    ("cn00blb<0>","PCSin_0",0.3),
    ("cn00bla<0>","SanEnA0",0.2),
    ("cn00bla<0>","SapEnA0",0.25),
    ("cn00bla<0>","Iso0",0.7),
    ("cn01bla<0>","NCSin_0",0.45),
    ("cn01blb<0>","NCSin_0",0.35),
    ("cn08bla<0>","PCSin_0",0.55),
    ("cec08bla<0>","SanEnA0",0.18),
    ("cec08bla<0>","SapEnA0",0.22),
    ("cec08bla<0>","Iso0",0.65),
]
A_extra = [("NCSin_0",0.0),("PCSin_0",0.0),("SanEnA0",0.0),("SapEnA0",0.0),("Iso0",0.0)]

# ---- Hidden B input (NOT in SUT sandbox) ----
# Different cols: cn02,cn03 (col<=7), cn10,cn11 (col>=8 +320), cec10,cec11 (+2048)
B_top = [
    "cn02bla<0>", "cn02blb<0>",   # group 512
    "cn02bla<2>", "cn02blb<2>",   # group 514
    "cn03bla<0>", "cn03blb<0>",   # group 768
    "cn10bla<0>", "cn10blb<0>",   # group 2880 (10*256+0+320)
    "cn10bla<1>", "cn10blb<1>",   # group 2881
    "cec10bla<0>","cec10blb<0>",  # group 4608 (10*256+0+2048)
    "cec11bla<0>","cec11blb<0>",  # group 4864 (11*256+0+2048)
]
B_pincaps = {
    "cn02bla<0>":8.0,  "cn02blb<0>":7.5,
    "cn02bla<2>":9.0,  "cn02blb<2>":6.5,
    "cn03bla<0>":10.5, "cn03blb<0>":9.5,
    "cn10bla<0>":11.0, "cn10blb<0>":10.0,
    "cn10bla<1>":8.5,  "cn10blb<1>":7.0,
    "cec10bla<0>":12.5,"cec10blb<0>":11.0,
    "cec11bla<0>":13.5,"cec11blb<0>":12.0,
}
B_couplings = [
    # group512 <-> group514
    ("cn02bla<0>","cn02bla<2>",1.3),
    ("cn02bla<0>","cn02blb<2>",0.9),
    ("cn02blb<0>","cn02bla<2>",0.7),
    ("cn02blb<0>","cn02blb<2>",1.1),
    # group512 <-> group768
    ("cn02bla<0>","cn03bla<0>",2.2),
    ("cn02blb<0>","cn03blb<0>",1.4),
    # group512 <-> group2880
    ("cn02bla<0>","cn10bla<0>",2.8),
    # group768 <-> group2880
    ("cn03bla<0>","cn10bla<0>",1.9),
    # group2880 <-> group2881
    ("cn10bla<0>","cn10bla<1>",1.6),
    # group2880 <-> group4608
    ("cn10bla<0>","cec10bla<0>",2.4),
    # group4608 <-> group4864
    ("cec10bla<0>","cec11bla<0>",2.0),
    ("cec10bla<0>","cec11blb<0>",0.8),
    ("cec10blb<0>","cec11bla<0>",0.6),
    # signals
    ("cn02bla<0>","NCSin_0",0.42),
    ("cn02blb<0>","NCSin_0",0.38),
    ("cn02bla<0>","PCSin_0",0.58),
    ("cn02blb<0>","PCSin_0",0.28),
    ("cn02bla<0>","SanEnB0",0.19),
    ("cn02bla<0>","SapEnB0",0.24),
    ("cn02bla<0>","OcEn0",0.66),
    ("cn03bla<0>","NCSin_0",0.48),
    ("cn03blb<0>","PCSin_0",0.32),
    ("cn10bla<0>","PCSin_0",0.52),
    ("cec10bla<0>","SanEnB0",0.17),
    ("cec10bla<0>","SapEnB0",0.21),
    ("cec11bla<0>","OcEn0",0.61),
    ("cec11blb<0>","NCSin_0",0.33),
]
B_extra = [("NCSin_0",0.0),("PCSin_0",0.0),("SanEnB0",0.0),("SapEnB0",0.0),("OcEn0",0.0)]

# Verify group numbers
print("A groups:", sorted(set(group_of(n) for n in A_top)))
print("B groups:", sorted(set(group_of(n) for n in B_top)))

reset_dir(ADIR)
os.makedirs(os.path.join(ADIR, "hidden"), exist_ok=True)
with open(os.path.join(ADIR, "spf_A.spf_CC"), "w") as f:
    f.write(make_spf(A_top, A_couplings, A_pincaps, A_extra))
with open(os.path.join(ADIR, "hidden", "spf_B.spf_CC"), "w") as f:
    f.write(make_spf(B_top, B_couplings, B_pincaps, B_extra))
with open(os.path.join(ADIR, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump({"hidden_inputs": ["spf_B.spf_CC"], "purpose": "judge-only; not in SUT sandbox",
               "diff_from_A": "different cols (cn02/03/10/11, cec10/11), different coupling values, different signals (SanEnB0/SapEnB0/OcEn0)"}, f, indent=2)

print("Assets written:", ADIR)

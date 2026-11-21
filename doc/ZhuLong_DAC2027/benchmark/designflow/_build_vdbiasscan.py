#!/usr/bin/env python3
# Builder for EDA-Eval-DesignFlow-VdbiasScanProduce-001
# Generates: assets (aging_A), reference (scan_vdbias.py, check.py, hidden B, hidden_a A', negatives, reference_submit.zip)
import os, io, zipfile, json, textwrap

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-VdbiasScanProduce-001"
AST = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)

def wr(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

# ---------------- si.inp fixture generator ----------------
# A si.inp: active vdbias + .param pvdias=<val>
# C si.inp: commented vdbias (not used)
# M si.inp: active vdbias but NO .param pvdias (used, but not in pvdias_values)
# other nets use dataset-specific prefix for token disjointness
def si_inp(kind, pvdias, prefix, idx):
    lines = [
        "* SPICE stimulus file for aging simulation (si.inp)",
        "* corner configuration and stimulus vector",
    ]
    if kind == 'A':
        lines.append(".param pvdias=%s" % pvdias)
    elif kind == 'M':
        pass  # active vdbias but no .param pvdias
    lines += [
        "vdd vdd! 0 dc=1.1",
        "vss vss! 0 dc=0",
    ]
    if kind in ('A', 'M'):
        lines.append("vdbias vdbias! 0 dc=pvdias power=0")
    else:  # C = commented
        lines.append("* vdbias vdbias! 0 dc=pvdias power=0")
    lines += [
        "v_clk %s_clk%d 0 PULSE(0 1.1 0 1n 1n 5n 10n)" % (prefix, idx),
        "v_data %s_data%d 0 1.1" % (prefix, idx),
        "x_top %s_clk%d %s_data%d vdbias! vdd! vss! top_cell" % (prefix, idx, prefix, idx),
        ".tran 1n 100n",
        ".end",
    ]
    return "\n".join(lines) + "\n"

# Dataset spec: list of (folder, [(si_name, kind, pvdias), ...])
# A (visible): 4 folders, 8 si.inp, used=6, no_vdbias=2, pv={0.9102:4, 0.8800:2}
A_SPEC = [
    ("AgingRun_Aa01_step1", [("si_Aa01_001", 'A', '0.9102'), ("si_Aa01_002", 'A', '0.9102')]),
    ("AgingRun_Aa02_step2", [("si_Aa02_001", 'A', '0.9102'), ("si_Aa02_002", 'C', None)]),
    ("AgingRun_Aa03_step1", [("si_Aa03_001", 'A', '0.8800'), ("si_Aa03_002", 'C', None)]),
    ("AgingRun_Aa04_step2", [("si_Aa04_001", 'A', '0.9102'), ("si_Aa04_002", 'A', '0.8800')]),
]
# B (hidden): 5 folders, 12 si.inp, used=9, no_vdbias=3, pv={0.7700:4, 0.8100:2, 0.9200:2}
B_SPEC = [
    ("AgingRun_Bb05_step1", [("si_Bb05_001", 'A', '0.7700'), ("si_Bb05_002", 'A', '0.7700'), ("si_Bb05_003", 'A', '0.8100')]),
    ("AgingRun_Bb06_step2", [("si_Bb06_001", 'A', '0.7700'), ("si_Bb06_002", 'A', '0.9200'), ("si_Bb06_003", 'C', None)]),
    ("AgingRun_Bb07_step1", [("si_Bb07_001", 'M', '0.8100'), ("si_Bb07_002", 'C', None)]),
    ("AgingRun_Bb08_step2", [("si_Bb08_001", 'A', '0.9200'), ("si_Bb08_002", 'A', '0.7700')]),
    ("AgingRun_Bb09_step1", [("si_Bb09_001", 'A', '0.8100'), ("si_Bb09_002", 'C', None)]),
]
# A' (hidden): 3 folders, 7 si.inp, used=5, no_vdbias=2, pv={0.6600:3, 0.7100:2}
AP_SPEC = [
    ("AgingRun_Cc10_step1", [("si_Cc10_001", 'A', '0.6600'), ("si_Cc10_002", 'A', '0.7100'), ("si_Cc10_003", 'C', None)]),
    ("AgingRun_Cc11_step2", [("si_Cc11_001", 'A', '0.6600'), ("si_Cc11_002", 'A', '0.7100')]),
    ("AgingRun_Cc12_step1", [("si_Cc12_001", 'A', '0.6600'), ("si_Cc12_002", 'C', None)]),
]

def gen_dataset(root, spec, prefix):
    for folder, files in spec:
        fd = os.path.join(root, folder)
        os.makedirs(fd, exist_ok=True)
        for i, (name, kind, pv) in enumerate(files):
            wr(os.path.join(fd, name + ".si.inp"), si_inp(kind, pv, prefix, i))

# A -> assets (visible to SUT)
gen_dataset(os.path.join(AST, "aging_A"), A_SPEC, "A")

# B -> reference/hidden/aging_B (SUT-invisible)
gen_dataset(os.path.join(REF, "hidden", "aging_B"), B_SPEC, "B")
# A' -> reference/hidden_a/aging_Ap (SUT-invisible)
gen_dataset(os.path.join(REF, "hidden_a", "aging_Ap"), AP_SPEC, "C")

# hidden_manifest.json
manifest = {
    "purpose": "hidden inputs not shipped to SUT sandbox; check() runs candidate on these only",
    "hidden_B": {"path": "hidden/aging_B", "folders": 5, "si_inp": 12, "used": 9, "no_vdbias": 3},
    "hidden_A_prime": {"path": "hidden_a/aging_Ap", "folders": 3, "si_inp": 7, "used": 5, "no_vdbias": 2,
                       "note": "anti-hardcode cross-check; token-disjoint from A and B in folder names, pvdias values, other net prefixes"},
}
wr(os.path.join(REF, "hidden", "hidden_manifest.json"), json.dumps(manifest, indent=2))

print("fixtures created")

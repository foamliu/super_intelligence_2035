#!/usr/bin/env python3
"""Shard C candidate selector (physical_layout): excludes ledger_C sids,
filters mc>=MC_MIN, matches shard-C tool keywords, prints top candidates with
layout-affinity score (lay - 0.6*sim) for domain assessment.

Shard C domains: layout_aether, layout_virtuoso, pg_layout, physical_verify.
"""
import sys, re, os

SUMMARY = sys.argv[1] if len(sys.argv) > 1 else "/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv"
LEDGER = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_ledger_C.tsv")
MC_MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 30
TOPN = int(sys.argv[4]) if len(sys.argv) > 4 else 25

# shard C tool keywords (physical layout / verification)
TOOL_RE = re.compile(r"calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pexivirtuoso|pex|gds|oas|lef|def|skill")

# excluded sids from ledger_C (col0, strip .messages.json)
excl = set()
with open(LEDGER) as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        sid = line.split("\t")[0]
        if sid.endswith(".messages.json"):
            sid = sid[:-len(".messages.json")]
        excl.add(sid)

LAY_KW = ("calibre", "virtuoso", "aether", "ipcustom", "layout", "lvs", "drc",
          "pexivirtuoso", "pex", "gds", "oas", "lef", "def", "skill",
          "erc", "antenna", "dfm", "fill", "via", "metal", "floorplan",
          "placement", "routing", "innovus", " Encounter".strip().lower())
SIM_KW = ("verilog", "systemverilog", "rtl", "sdc", "synthesis", "dc_shell",
          "design_compiler", "pt_shell", "primetime", "vcs", "verdi",
          "formality", "netlist", "spice", "spectre", "hspice", "finesim",
          "schematic", "cmos", "analog", "model", "char", "pdk", "em",
          "simulation", "sim", "testbench", "tb", "stimulus")

cands = []
with open(SUMMARY) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        c = line.split("\t")
        if len(c) < 7:
            continue
        ip, host, user, sess, mc_s, kw, tools = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
        try:
            mc = int(mc_s)
        except ValueError:
            continue
        if mc < MC_MIN:
            continue
        sid = sess[:-len(".messages.json")] if sess.endswith(".messages.json") else sess
        if sid in excl:
            continue
        if not TOOL_RE.search(tools):
            continue
        lay = 0
        sim = 0
        for kv in kw.split(";"):
            kv = kv.strip()
            if not kv:
                continue
            k = kv.split(":")[0].lower()
            n = 0
            try:
                n = int(kv.split(":")[1])
            except (IndexError, ValueError):
                pass
            if k in LAY_KW:
                lay += n
            elif k in SIM_KW:
                sim += n
        score = lay - 0.6 * sim
        cands.append((mc, sid, user, host, ip, kw, tools, lay, sim, score))

cands.sort(key=lambda x: (-x[9], -x[0]))
print("# header: mc\tsid\tuser\thost\tip\tkeywords\ttools\tlay\tsim\tscore")
for c in cands[:TOPN]:
    print("\t".join(str(z) for z in c))
print("# total fresh:", len(cands))

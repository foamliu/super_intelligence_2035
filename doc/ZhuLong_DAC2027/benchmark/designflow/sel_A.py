#!/usr/bin/env python3
"""Shard A candidate selector: excludes ledger sids, filters mc>=SHARD_MC[A],
matches shard-A tool keywords, prints top candidates with keyword profile
for domain assessment."""
import sys, re, os

SUMMARY = sys.argv[1] if len(sys.argv) > 1 else "/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv"
LEDGER = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace_ledger_A.tsv")
MC_MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 15
TOPN = int(sys.argv[4]) if len(sys.argv) > 4 else 15

# shard A tool keywords (11/06 widened)
TOOL_RE = re.compile(r"verdi|vcs|dc_shell|verilint|formality|innovus|primetime|design_compiler|rc|pt_shell|synthesis|synopsys|tcl|verilog|systemverilog|rtl|sdc|vivado|yosys|openroad")

# excluded sids from ledger (col0, strip .messages.json)
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
        # digital dominance: count digital-ish kw vs analog-ish kw
        digi = 0
        ana = 0
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
            if k in ("verilog", "systemverilog", "rtl", "sdc", "synthesis", "dc_shell",
                     "design_compiler", "pt_shell", "primetime", "innovus", "vcs",
                     "verdi", "formality", "tcl", "vivado", "yosys", "openroad",
                     "netlist", "gate", "logic", "clock", "timing", "sta", "dft",
                     "scan", "upf", "cpf", "power", "fsp", "lint"):
                digi += n
            elif k in ("analog", "cmos", "schematic", "layout", "drc", "lvs",
                       "erc", "spice", "spectre", "hspice", "finesim", "calibre",
                       "pdk", "char", "model", "virtuoso", "aether", "skill",
                       "cdl", "gds", "oas", "lef", "def", "rcx", "starrc",
                       "em", "ir", "pa", "aspec", "mixed"):
                ana += n
        cands.append((mc, sid, user, host, ip, kw, tools, digi, ana))

cands.sort(key=lambda x: (-x[0], -x[7]))
print("# header: mc\tsid\tuser\thost\tip\tkeywords\tdigi\tana")
for c in cands[:TOPN]:
    print("\t".join(str(z) for z in (c[0], c[1], c[2], c[3], c[4], c[5], c[7], c[8])))
print("# total fresh:", len(cands))

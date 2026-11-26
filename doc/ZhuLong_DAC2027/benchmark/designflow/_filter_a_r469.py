#!/usr/bin/env python3
# r469 A-dominant candidate filter (count-based, mc>=10)
import re, sys
from collections import defaultdict

SUM = "summary_1113.tsv"
A_KW = {"verilog","systemverilog","rtl","sdc","vcs","verdi","dc_shell","synthesis",
        "synopsys","primetime","pt_shell","innovus","formality","yosys","vivado",
        "openroad","verilint","genus","tcl","design_compiler","rc"}
B_KW = {"hspice","spice","spectre","eldo","finesim","smartspice","siliconsmart",
        "cmos","analog","pex","waveview","netlist","transistor","cdl"}
C_KW = {"drc","calibre","aether","virtuoso","pdk","lvs","gds","cellview","schematic",
        "pyaether","lib.defs","cadence","ipcustom","layout","pexivirtuoso","skipper",
        "dbopencv"}

def norm_sid(s):
    s = s.split("/")[-1]
    for suf in (".messages.json",".messages.archive.json",".json"):
        if s.endswith(suf): s = s[:-len(suf)]
    return s

# build 4-shard exclusion set
excl = set()
for s in ("A","B","C","D"):
    try:
        with open(f"trace_ledger_{s}.tsv") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if parts:
                    excl.add(norm_sid(parts[0]))
    except FileNotFoundError: pass

def parse_kw(col):
    d = {}
    for tok in col.split(";"):
        tok = tok.strip()
        if not tok: continue
        if ":" in tok:
            k,v = tok.rsplit(":",1)
            try: d[k.strip()] = int(v)
            except: pass
    return d

rows = []
with open(SUM) as f:
    header = next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 6: continue
        try: mc = int(parts[4])
        except: continue
        if mc < 10: continue
        sid = norm_sid(parts[3])
        if sid in excl: continue
        kw = parse_kw(parts[5])
        a = sum(v for k,v in kw.items() if k in A_KW)
        b = sum(v for k,v in kw.items() if k in B_KW)
        c = sum(v for k,v in kw.items() if k in C_KW)
        strict = a > 2*c and a > 2*b and a >= 15
        relaxed = a > c and a > b and a >= 10
        if strict or relaxed:
            rows.append((mc, sid, parts[2], parts[1], parts[0], a, b, c, strict, relaxed, parts[5]))

rows.sort(key=lambda r: (-r[0], -r[5]))
strict_rows = [r for r in rows if r[8]]
relaxed_only = [r for r in rows if r[9] and not r[8]]
print(f"# total fresh A-dominant: {len(rows)} (strict {len(strict_rows)} / relaxed-only {len(relaxed_only)})")
print(f"# 4-shard excl: {len(excl)} anchors")
print("# === STRICT (a>2c,2b,a>=15) top 25 ===")
for r in strict_rows[:25]:
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\tA={r[5]}/B={r[6]}/C={r[7]}\t{r[10][:80]}")
print("# === RELAXED-ONLY (a>c,b,a>=10) top 25 ===")
for r in relaxed_only[:25]:
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\tA={r[5]}/B={r[6]}/C={r[7]}\t{r[10][:80]}")

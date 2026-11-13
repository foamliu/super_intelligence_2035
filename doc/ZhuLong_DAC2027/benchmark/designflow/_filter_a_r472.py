#!/usr/bin/env python3
"""r472 A-dominant fresh filter on summary_1113.tsv with 4-shard ledger excl."""
import sys, re
from collections import defaultdict

SUMMARY = "summary_1113.tsv"
LEDGERS = ["trace_ledger_A.tsv", "trace_ledger_B.tsv", "trace_ledger_C.tsv", "trace_ledger_D.tsv"]

# keyword token sets (exact token match within keyword field)
A_KW = {"verilog","systemverilog","rtl","sdc","vcs","verdi","dc_shell","synthesis",
        "synopsys","primetime","pt_shell","innovus","formality","yosys","vivado",
        "openroad","verilint","genus","tcl","design_compiler","rc"}
B_KW = {"hspice","spice","cmos","analog","pex","waveview","netlist","transistor",
        "cdl","finesim","eldo","spectre","smartspice","siliconsmart"}
C_KW = {"drc","calibre","aether","virtuoso","pdk","lvs","gds","cellview","schematic",
        "pyaether","dbopencv","skipper","cadence","lib.defs","def"}

def norm_sess(s):
    s = s.strip()
    s = re.sub(r'\.messages\.json$','',s)
    s = re.sub(r'\.json$','',s)
    return s

# build 4-shard excl anchor set
excl = set()
for L in LEDGERS:
    try:
        with open(L) as f:
            for line in f:
                if not line.strip(): continue
                col0 = line.split('\t')[0]
                excl.add(norm_sess(col0))
    except FileNotFoundError:
        pass

print(f"# 4-shard excl anchors: {len(excl)}", file=sys.stderr)

def parse_kw(kw_field):
    """field like 'verilog:2393;lvs:1560' -> dict token->count"""
    d = {}
    if not kw_field: return d
    for tok in kw_field.split(';'):
        tok=tok.strip()
        if not tok: continue
        if ':' in tok:
            name, cnt = tok.rsplit(':',1)
            try: c = int(cnt)
            except: c = 1
            d[name.strip()] = c
        else:
            d[tok] = 1
    return d

rows = []
with open(SUMMARY) as f:
    next(f)  # header
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < 6: continue
        ip, host, user, sess, mc, kw = p[0], p[1], p[2], p[3], p[4], p[5]
        try: mc = int(mc)
        except: continue
        if mc < 10: continue
        anchor = norm_sess(sess)
        if anchor in excl: continue
        kd = parse_kw(kw)
        a = sum(c for k,c in kd.items() if k in A_KW)
        b = sum(c for k,c in kd.items() if k in B_KW)
        c = sum(c for k,c in kd.items() if k in C_KW)
        rows.append((mc, a, b, c, anchor, user, host, kw))

# strict: a>2c and a>2b and a>=15 ; relaxed: a>c and a>b and a>=10
strict = [r for r in rows if r[1] > 2*r[3] and r[1] > 2*r[2] and r[1] >= 15]
relaxed = [r for r in rows if r[1] > r[3] and r[1] > r[2] and r[1] >= 10 and r not in strict]

strict.sort(key=lambda r: (-r[1], -r[0]))
relaxed.sort(key=lambda r: (-r[1], -r[0]))

print(f"# total fresh mc>=10 A-keyword: {len(rows)}", file=sys.stderr)
print(f"# strict: {len(strict)}  relaxed: {len(relaxed)}", file=sys.stderr)

with open("_cands_r472_strict.tsv","w") as f:
    f.write("mc\ta\tb\tc\tanchor\tuser\thost\tkw\n")
    for r in strict:
        f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}\t{r[6]}\t{r[7]}\n")
with open("_cands_r472_relaxed.tsv","w") as f:
    f.write("mc\ta\tb\tc\tanchor\tuser\thost\tkw\n")
    for r in relaxed:
        f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}\t{r[6]}\t{r[7]}\n")

print("strict top40:")
for r in strict[:40]:
    print(f"  mc={r[0]} a={r[1]} b={r[2]} c={r[3]} {r[4]} {r[5]}@{r[6]} kw={r[7][:60]}")
print("relaxed top30:")
for r in relaxed[:30]:
    print(f"  mc={r[0]} a={r[1]} b={r[2]} c={r[3]} {r[4]} {r[5]}@{r[6]} kw={r[7][:60]}")

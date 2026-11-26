#!/usr/bin/env python3
"""r474 A-domain-primary fresh filter on summary_1113.tsv.
Strategy (r473 slice): A-domain-primary = first keyword token is an A-domain
signal (verilog/systemverilog/netlist/rtl/synopsys/sdc/vcs/verdi/dc_shell/
synthesis/primetime/innovus/formality/yosys/vivado/openroad/verilint/genus/
tcl/design_compiler/rc/pt_shell), NOT keyword-count dominance (which mislabels
C-domain high-mc as A). 4-shard ledger excl.
"""
import sys, re

SUMMARY = "summary_1113.tsv"
LEDGERS = ["trace_ledger_A.tsv", "trace_ledger_B.tsv", "trace_ledger_C.tsv", "trace_ledger_D.tsv"]

A_KW = {"verilog","systemverilog","rtl","sdc","vcs","verdi","dc_shell","synthesis",
        "synopsys","primetime","pt_shell","innovus","formality","yosys","vivado",
        "openroad","verilint","genus","tcl","design_compiler","rc","netlist"}
B_KW = {"hspice","spice","cmos","analog","pex","waveview","transistor",
        "cdl","finesim","eldo","spectre","smartspice","siliconsmart"}
C_KW = {"drc","calibre","aether","virtuoso","pdk","lvs","gds","cellview","schematic",
        "pyaether","dbopencv","skipper","cadence","lib.defs","def"}

# A-domain-primary signal tokens (first keyword = one of these => user-side
# content is A-domain produce-task material: RTL / netlist / synth scripts)
A_PRIMARY = {"verilog","systemverilog","netlist","rtl","synopsys","sdc","vcs","verdi",
             "dc_shell","synthesis","primetime","pt_shell","innovus","formality",
             "yosys","vivado","openroad","verilint","genus","tcl","design_compiler",
             "rc"}

def norm_sess(s):
    s = s.strip()
    s = re.sub(r'\.messages\.json$','',s)
    s = re.sub(r'\.json$','',s)
    return s

excl = set()
for L in LEDGERS:
    try:
        with open(L) as f:
            for line in f:
                if not line.strip(): continue
                excl.add(norm_sess(line.split('\t')[0]))
    except FileNotFoundError:
        pass
print(f"# 4-shard excl anchors: {len(excl)}", file=sys.stderr)

def parse_kw(kw_field):
    d = {}
    if not kw_field: return d, None
    toks = []
    for tok in kw_field.split(';'):
        tok=tok.strip()
        if not tok: continue
        if ':' in tok:
            name, cnt = tok.rsplit(':',1)
            try: c = int(cnt)
            except: c = 1
            d[name.strip()] = c
            toks.append((name.strip(), c))
        else:
            d[tok] = 1
            toks.append((tok, 1))
    first = toks[0][0] if toks else None
    return d, first

rows = []
with open(SUMMARY) as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < 6: continue
        ip, host, user, sess, mc, kw = p[0], p[1], p[2], p[3], p[4], p[5]
        try: mc = int(mc)
        except: continue
        if mc < 10: continue
        anchor = norm_sess(sess)
        if anchor in excl: continue
        kd, first = parse_kw(kw)
        a = sum(c for k,c in kd.items() if k in A_KW)
        b = sum(c for k,c in kd.items() if k in B_KW)
        c = sum(c for k,c in kd.items() if k in C_KW)
        a_primary = 1 if (first in A_PRIMARY) else 0
        rows.append((mc, a, b, c, a_primary, first, anchor, user, host, kw))

print(f"# total fresh mc>=10 A-keyword: {len(rows)}", file=sys.stderr)
primary = [r for r in rows if r[4]==1]
print(f"# A-domain-primary (first kw is A signal): {len(primary)}", file=sys.stderr)

# sort primary by mc desc
primary.sort(key=lambda r: (-r[0], -r[1]))

with open("_cands_r474_primary.tsv","w") as f:
    f.write("mc\ta\tb\tc\tfirst\tanchor\tuser\thost\tkw\n")
    for r in primary:
        f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[5]}\t{r[6]}\t{r[7]}\t{r[8]}\t{r[9]}\n")

print("A-domain-primary top30 (by mc desc):")
for r in primary[:30]:
    print(f"  mc={r[0]} a={r[1]} b={r[2]} c={r[3]} first={r[5]} {r[6]} {r[7]}@{r[8]} kw={r[9][:70]}")

# also relaxed A-dominant (count-based) for fallback
relaxed = [r for r in rows if r[1] > r[3] and r[1] > r[2] and r[1] >= 10 and r[4]==0]
relaxed.sort(key=lambda r: (-r[0], -r[1]))
print(f"\n# relaxed A-dominant non-primary: {len(relaxed)} (fallback)")
print("relaxed top15 (by mc desc):")
for r in relaxed[:15]:
    print(f"  mc={r[0]} a={r[1]} b={r[2]} c={r[3]} first={r[5]} {r[6]} {r[7]}@{r[8]} kw={r[9][:70]}")

#!/usr/bin/env python3
import sys, re, os
# Build EXCL from current ledger A (col1 = session id)
EXCL = set()
led = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/trace_ledger_A.tsv"
if os.path.exists(led):
    with open(led) as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if not p or not p[0]: continue
            s = p[0]
            if s.endswith(".messages.json"): s = s[:-len(".messages.json")]
            EXCL.add(s)
SHARD_A_TOOLS = re.compile(r'verdi|vcs|dc_shell|verilint|formality|innovus|primetime|design_compiler|rc|pt_shell|synthesis|synopsys|tcl|verilog|systemverilog|rtl|sdc|vivado|yosys|openroad', re.I)
SUM = sys.argv[1] if len(sys.argv) > 1 else "/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv"
rows = []
with open(SUM) as f:
    header = f.readline()
    for ln in f:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 7: continue
        ip, host, user, sess, mc, kw, tools = p[0], p[1], p[2], p[3], p[4], p[5], p[6]
        try: mci = int(mc)
        except: continue
        if mci < 15: continue
        s = sess
        if s.endswith(".messages.json"): s = s[:-len(".messages.json")]
        if s in EXCL: continue
        if not SHARD_A_TOOLS.search(tools): continue
        rows.append((mci, s, user, host, tools))
rows.sort(key=lambda r: -r[0])
print("mc\tsession\tuser\thost\ttools")
for r in rows[:25]:
    print("\t".join(str(x) for x in r))
print("# total fresh:", len(rows), file=sys.stderr)
print("# EXCL size:", len(EXCL), file=sys.stderr)

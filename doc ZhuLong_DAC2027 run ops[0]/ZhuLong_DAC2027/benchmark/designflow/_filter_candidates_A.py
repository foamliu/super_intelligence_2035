#!/usr/bin/env python3
import json, re, sys, os
EXCL = set(json.load(open(os.path.join(os.path.dirname(__file__), '_exclude_A_list.json'))))
KW = re.compile(r'verdi|vcs|dc_shell|verilint|formality|innovus|primetime|design_compiler|rc|pt_shell|synthesis|synopsys|tcl|verilog|systemverilog|rtl|sdc|vivado|yosys|openroad')
rows = []
with open('/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv') as f:
    next(f)
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 7: continue
        mc, sess, user, host, kw = parts[4], parts[3].replace('.messages.json',''), parts[2], parts[1], parts[6]
        try: mcn = int(mc)
        except: continue
        if mcn < 15: continue
        if sess in EXCL: continue
        if not KW.search(kw): continue
        rows.append((mcn, sess, user, host, kw))
rows.sort(key=lambda r: -r[0])
for r in rows[:10]:
    print('\t'.join(str(x) for x in r))

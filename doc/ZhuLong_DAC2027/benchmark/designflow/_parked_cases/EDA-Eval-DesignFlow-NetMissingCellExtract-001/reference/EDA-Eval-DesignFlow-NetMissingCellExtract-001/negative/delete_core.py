#!/usr/bin/env python3
# negative: delete_core -- a real parser that finds all 12 missing instances
# with correct line/cell/instance, but DROPS the port map (emits ports={}).
# Counts (g/h/i/j/k) pass; the exact-match cond (m) fails because ports do
# not match the oracle.
import re, json, sys
KEYWORDS = {'module','endmodule','input','output','inout','wire','reg',
            'parameter','assign','always','initial'}
sim = open(sys.argv[2]).read()
known = set(re.findall(r'\bmodule\s+(\w+)\s*\(', sim))
net = open(sys.argv[1]).read()
mi = []; tot = 0; av = 0; mc = set(); ac = set()
for i, line in enumerate(net.split('\n')):
    s = line.strip()
    if not s or s.startswith('`'): continue
    m = re.match(r'(\w+)\s+(\w+)\s*\(', s)
    if not m: continue
    cell, inst = m.group(1), m.group(2)
    if cell in KEYWORDS: continue
    tot += 1
    if cell in known:
        av += 1; ac.add(cell)
    else:
        # BUG: ports deliberately emptied
        mi.append({"line": i+1, "cell": cell, "instance": inst, "ports": {}})
        mc.add(cell)
print(json.dumps({
    "missing_instances": mi,
    "summary": {"total_instances": tot, "missing_count": len(mi),
                "available_count": av, "missing_cells": sorted(mc),
                "available_cells_used": sorted(ac)}
}))

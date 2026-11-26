#!/usr/bin/env python3
"""Build 4-shard exclusion anchor list for r456 selection.
Combines all 4 shard ledgers (col 0 = session anchor) + dedups."""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGERS = [os.path.join(HERE, f"trace_ledger_{s}.tsv") for s in "ABCD"]
def norm(sf):
    return re.sub(r'\.(messages\.)?json$','',sf.strip())
anchors = set()
for L in LEDGERS:
    if not os.path.exists(L): continue
    with open(L) as f:
        header = f.readline()
        for line in f:
            p = line.split('\t')
            if len(p) < 1: continue
            a = norm(p[0])
            if a: anchors.add(a)
# also add bare suffix
with open(os.path.join(HERE, "_excl_4shard_r456.txt"), "w") as out:
    for a in sorted(anchors):
        out.write(a + "\n")
print(f"wrote {len(anchors)} anchors to _excl_4shard_r456.txt")

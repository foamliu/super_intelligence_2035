#!/usr/bin/env python3
import re, sys

EXCL = set()
with open('excl_short.txt') as f:
    for line in f:
        a = line.strip()
        if a:
            EXCL.add(a)

SUMMARY = '/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv'
KW_RE = re.compile(r'waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic')

cands = []
with open(SUMMARY) as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 6: continue
        ip, host, user, sf, mc, kw = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        try: mcn = int(mc)
        except: continue
        if mcn < 30: continue
        if not KW_RE.search(kw or ''): continue
        m = re.match(r'^\d+_(.+)$', sf)
        short = m.group(1) if m else sf
        short2 = re.sub(r'\.messages(\.archive)?\.json$','',short)
        short2 = re.sub(r'\.json$','',short2)
        if short2 in EXCL: continue
        cands.append((mcn, sf, user, host, kw))

cands.sort(key=lambda x: -x[0])
print('# total fresh D-domain candidates mc>=30:', len(cands))
for c in cands[:25]:
    print('\t'.join(str(x) for x in c))

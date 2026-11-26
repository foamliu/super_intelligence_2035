#!/usr/bin/env python3
# Filter summary.tsv for shard D fresh candidates (mc>=10, D-keywords), exclude ledgered.
import re, sys

SUMMARY = "/home/t0002965/log/ssh_eda_search_20261113_131349/summary.tsv"
EXCL = "excl_anchors_r620.txt"

# load exclusion anchors
excl = set()
with open(EXCL) as f:
    for line in f:
        a = line.strip()
        if a:
            excl.add(a)
            excl.add(a + ".messages.json")
            excl.add(a + ".json")
            excl.add(a + ".messages.archive")

# D keywords (shard D: analog_context, schematic_netlist, waveform)
D_KW = re.compile(r'waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic', re.I)

def norm(s):
    s = re.sub(r'\.messages\.json$','',s)
    s = re.sub(r'\.messages\.archive$','',s)
    s = re.sub(r'\.json$','',s)
    return s

cands = []
with open(SUMMARY) as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 7: continue
        ip, host, user, session_file, match_count, keywords, tools = parts[:7]
        try:
            mc = int(match_count)
        except ValueError:
            continue
        if mc < 10: continue
        if not D_KW.search(keywords): continue
        anchor = norm(session_file)
        if anchor in excl: continue
        # d_ratio: fraction of D-keyword tokens
        kw_tokens = [t for t in keywords.split(';') if t.strip()]
        d_tokens = [t for t in kw_tokens if D_KW.search(t)]
        # extract mc from token like "netlist:4326"
        d_mc = 0
        for t in kw_tokens:
            m = re.match(r'([a-zA-Z_]+):(\d+)', t)
            if m and D_KW.search(m.group(1)):
                d_mc += int(m.group(2))
        total_mc = 0
        for t in kw_tokens:
            m = re.match(r'([a-zA-Z_]+):(\d+)', t)
            if m: total_mc += int(m.group(2))
        d_ratio = d_mc/total_mc if total_mc else 0
        cands.append((mc, d_ratio, d_mc, session_file, user, host, keywords))

# sort by mc desc; show d_ratio too
cands.sort(key=lambda x: -x[0])
print(f"# fresh D candidates: {len(cands)}")
print("# mc\td_ratio\td_mc\tsession\tuser\thost\tkeywords")
for c in cands[:40]:
    print(f"{c[0]}\t{c[1]:.2f}\t{c[2]}\t{c[3]}\t{c[4]}\t{c[5]}\t{c[6]}")

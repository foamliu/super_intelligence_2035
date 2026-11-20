#!/usr/bin/env python3
"""Build fresh shard-B candidates from summary_1113.tsv, 3-way dedup:
(1) 4 shard ledgers, (2) main merged jsonl, (3) slug-normalize (.messages.json/.json/.messages.archive.json stripped)."""
import json, re, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def norm_slug(s):
    s = os.path.basename(s)
    s = re.sub(r'\.messages\.archive\.json$', '', s)
    s = re.sub(r'\.messages\.json$', '', s)
    s = re.sub(r'\.json$', '', s)
    return s

# 1. collect ledgered slugs (4 shards)
ledgered = set()
for shard in ['A','B','C','D']:
    p = f'trace_ledger_{shard}.tsv'
    if not os.path.exists(p): continue
    with open(p) as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if not parts or not parts[0]: continue
            ledgered.add(norm_slug(parts[0]))

# 2. collect slugs from main merged jsonl (trace_source.session_file)
jsonl = '/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl'
with open(jsonl) as f:
    for line in f:
        line=line.strip()
        if not line: continue
        try: o=json.loads(line)
        except: continue
        ts = (o.get('metadata') or {}).get('trace_source')
        sf = ts.get('session_file') if isinstance(ts, dict) else None
        if sf: ledgered.add(norm_slug(sf))

print(f"# ledgered slugs (3-way): {len(ledgered)}", file=sys.stderr)

# 3. filter summary_1113.tsv
BKW = re.compile(r'hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim', re.I)
rows = {}  # slug -> (mc, session, user, host, keywords)
with open('summary_1113.tsv') as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 7: continue
        ip,host,user,sf,mc,kw,tools = parts[0],parts[1],parts[2],parts[3],parts[4],parts[5],parts[6]
        try: mci=int(mc)
        except: continue
        if mci < 10: continue
        slug = norm_slug(sf)
        if slug in ledgered: continue
        if not BKW.search(kw or ''): continue
        # dedup by slug, keep max mc
        if slug in rows and rows[slug][0] >= mci: continue
        rows[slug] = (mci, sf, user, host, kw)

cands = sorted(rows.values(), key=lambda r: -r[0])
print(f"# fresh B-keyword mc>=10 candidates: {len(cands)}", file=sys.stderr)
print("# mc\tsession\tuser\thost\tkeywords")
for r in cands[:25]:
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}")

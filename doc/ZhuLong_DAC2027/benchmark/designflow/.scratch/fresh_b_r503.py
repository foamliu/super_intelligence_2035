#!/usr/bin/env python3
"""Compute fresh shard-B keyword candidates from summary_1113.tsv with cross-shard dedup."""
import re, sys, os, json

DF = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow"
SRC = os.path.join(DF, "summary_1113.tsv")

def norm_slug(sf):
    s = sf
    for suf in (".messages.archive.json", ".messages.json", ".archive.json", ".json"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s

# 1. Load all 4 shard ledgers -> exclusion slugs
excl = set()
for sh in ("A", "B", "C", "D"):
    p = os.path.join(DF, f"trace_ledger_{sh}.tsv")
    if not os.path.exists(p):
        continue
    with open(p) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            slug = norm_slug(line.split("\t")[0])
            excl.add(slug)

# 2. (ledger already tracks jsonl cases; skip extra parse)

# 3. Parse summary_1113.tsv, dedup by slug keep max mc, filter mc>=10 + B keywords
B_KW = re.compile(r"hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim", re.I)
best = {}  # slug -> (mc, row)
with open(SRC) as f:
    header = next(f)
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        c = line.split("\t")
        if len(c) < 7:
            continue
        ip, host, user, sf, mc, kw, tools = c[0], c[1], c[2], c[3], c[4], c[5], c[6]
        try:
            mc_i = int(mc)
        except ValueError:
            continue
        slug = norm_slug(sf)
        if slug in best:
            if mc_i > best[slug][0]:
                best[slug] = (mc_i, (ip, host, user, sf, kw, tools))
        else:
            best[slug] = (mc_i, (ip, host, user, sf, kw, tools))

# 4. Filter mc>=10, B keywords, not excluded
cands = []
for slug, (mc_i, row) in best.items():
    if mc_i < 10:
        continue
    ip, host, user, sf, kw, tools = row
    if not B_KW.search(kw):
        continue
    if slug in excl:
        continue
    # spice-dominance: count spice-ish kw vs total kw
    toks = [t for t in kw.split(";") if t]
    sp = sum(int(t.split(":")[1]) for t in toks if t.split(":")[0].lower() in
             ("hspice", "finesim", "siliconsmart", "spectre", "ngspice", "simulator", "spice", "custom_sim"))
    tot = sum(int(t.split(":")[1]) for t in toks if ":" in t)
    dom = sp / tot if tot else 0
    cands.append((mc_i, dom, sp, tot, slug, user, host, kw))

cands.sort(key=lambda x: (-x[0], -x[1]))
print(f"# fresh B-keyword mc>=10 candidates (cross-shard dedup): {len(cands)}")
print(f"# excl slugs (4-shard ledger): {len(excl)}")
print("# mc\tdom\tsp\ttot\tslug\tuser\thost\tkeywords")
for mc_i, dom, sp, tot, slug, user, host, kw in cands[:45]:
    print(f"{mc_i}\t{dom:.2f}\t{sp}\t{tot}\t{slug}\t{user}\t{host}\t{kw[:80]}")

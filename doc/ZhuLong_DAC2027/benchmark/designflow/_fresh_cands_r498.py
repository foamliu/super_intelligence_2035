#!/usr/bin/env python3
"""Get fresh B-domain candidates from summary_1113.tsv with 3-way dedup
(4 shard ledgers + main jsonl). Outputs top-N by match_count."""
import re, sys, json, os

DESIGNFLOW = os.path.dirname(os.path.abspath(__file__))
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
SUP = os.path.dirname(DESIGNFLOW)  # benchmark/

def slug(s):
    for suf in (".messages.json", ".messages.archive.json", ".archive.json", ".json"):
        if s.endswith(suf):
            return s[: -len(suf)]
    return s

# B-domain keyword filter (shard B: spice_sim / characterization)
B_KW = re.compile(r"hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim")

# --- collect excluded slugs from all 4 shard ledgers ---
excluded = set()
for shard in "ABCD":
    p = os.path.join(DESIGNFLOW, f"trace_ledger_{shard}.tsv")
    if not os.path.exists(p):
        continue
    with open(p) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            cols = line.split("\t")
            if not cols:
                continue
            excluded.add(slug(cols[0]))

# --- also exclude slugs referenced in main jsonl (trace_source.session_file) ---
main_jsonl = os.path.join(BENCH, "EDA-Eval-DesignFlow.jsonl")
if os.path.exists(main_jsonl):
    with open(main_jsonl) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ts = obj.get("metadata", {}).get("trace_source", {})
            if isinstance(ts, dict):
                sf = ts.get("session_file", "")
            else:
                sf = ""
            if sf:
                excluded.add(slug(sf))

# shard B jsonl too
for fn in ("EDA-Eval-DesignFlow_B.jsonl",):
    p = os.path.join(BENCH, fn)
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ts = obj.get("metadata", {}).get("trace_source", {})
                if isinstance(ts, dict):
                    sf = ts.get("session_file", "")
                else:
                    sf = ""
                if sf:
                    excluded.add(slug(sf))

print(f"# excluded slugs (4 ledger + main/B jsonl): {len(excluded)}", file=sys.stderr)

# --- read summary_1113.tsv, filter, dedup by slug (keep max mc) ---
src = os.path.join(DESIGNFLOW, "summary_1113.tsv")
best = {}  # slug -> (mc, row)
n_in = 0
n_b = 0
with open(src) as f:
    header = f.readline()
    for line in f:
        line = line.rstrip("\n")
        if not line:
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue
        n_in += 1
        mc = int(cols[4]) if cols[4].isdigit() else 0
        sf = cols[3]
        sl = slug(sf)
        kw = cols[5]
        if not B_KW.search(kw):
            continue
        if mc < 10:
            continue
        n_b += 1
        if sl not in best or mc > best[sl][0]:
            best[sl] = (mc, cols, sf, sl)

print(f"# input rows={n_in}  B-keyword+mc>=10 rows={n_b}  dedup slugs={len(best)}", file=sys.stderr)

# --- filter excluded, sort by mc desc ---
fresh = [(mc, cols, sf, sl) for sl, (mc, cols, sf, sl) in best.items() if sl not in excluded]
fresh.sort(key=lambda x: -x[0])
print(f"# fresh (after 3-way dedup): {len(fresh)}", file=sys.stderr)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
print("# mc\tsession_file\tuser\thost\tkeywords\tslug")
for mc, cols, sf, sl in fresh[:N]:
    print(f"{mc}\t{cols[3]}\t{cols[2]}\t{cols[1]}\t{cols[5]}\t{sl}")

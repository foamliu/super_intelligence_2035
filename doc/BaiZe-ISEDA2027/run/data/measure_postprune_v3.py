#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_postprune_v3.py — post-prune measurements for inventory report v3."""
import os, json, glob

TEXT = "/nas_train/app.e0031982/datasets/baize-data/text"
NENV = "/nas_env/app.e0031982/baize-data"

def grp(pat):
    bins = sorted(glob.glob(os.path.join(TEXT, pat + "*.bin")))
    idxs = sorted(glob.glob(os.path.join(TEXT, pat + "*.idx")))
    jss  = sorted(glob.glob(os.path.join(TEXT, pat + "*.json")))
    b = sum(os.path.getsize(f) for f in bins)
    t = 0
    for j in jss:
        try:
            d = json.load(open(j))
            t += int(d.get("num_tokens", 0))
        except Exception:
            pass
    return len(bins), len(idxs), len(jss), b, t

print("=== post-prune text/ groups ===")
for p in ["env14_CC-MAIN", "l3_s", "math_s"]:
    nbin, nidx, njs, b, t = grp(p)
    print(f"{p}: bin={nbin} idx={nidx} json={njs} bytes={b} tokens={t}")

print("\n=== /nas_env full_* token totals ===")
envtot = 0
for d in sorted(glob.glob(NENV + "/full_*")):
    tot = 0
    for j in glob.glob(d + "/*.json"):
        try:
            dd = json.load(open(j))
            tot += int(dd.get("num_tokens", 0))
        except Exception:
            pass
    print(f"{os.path.basename(d)}: tokens={tot}")
    envtot += tot
print(f"NAS_ENV_TOTAL={envtot}")

# env14 from summary
sj = os.path.join(TEXT, "env14_fullsource_summary.json")
if os.path.isfile(sj):
    s = json.load(open(sj))
    print(f"\nENV14_TOTAL={s.get('total_tokens',0)}")

# du text
import subprocess
du = subprocess.run(["du","-sb",TEXT], capture_output=True, text=True).stdout.split()[0]
print(f"TEXT_DU_BYTES={du}")

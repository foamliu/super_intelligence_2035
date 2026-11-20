#!/usr/bin/env python3
"""One-shot dedup of resolved/failed/infra_or_quota in all eval_glm53_*.json (R2689)."""
import json
from pathlib import Path
REP = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports")
for h in ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]:
    ef = REP / f"eval_glm53_{h}.json"
    d = json.load(open(ef))
    changed = False
    for k in ["resolved","failed","infra_or_quota"]:
        lst = d.get(k, [])
        seen = set(); out = []
        for x in lst:
            if x not in seen:
                seen.add(x); out.append(x)
        if len(out) != len(lst):
            print(f"{h} {k}: {len(lst)}->{len(out)} (removed {len(lst)-len(out)} dups)")
            d[k] = out; changed = True
    if changed:
        d["n"] = len(d["resolved"]) + len(d["failed"]) + len(d["infra_or_quota"])
        ef.write_text(json.dumps(d, indent=2))
        print(f"  -> wrote {ef.name} n={d['n']}")
print("--- post-dedup unique counts ---")
for h in ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]:
    d = json.load(open(REP / f"eval_glm53_{h}.json"))
    r = len(set(d["resolved"])); f = len(set(d["failed"])); i = len(set(d["infra_or_quota"]))
    print(f"{h}: resolved={r} failed={f} infra={i} n={d['n']} consistent={r+f+i==d['n']}")

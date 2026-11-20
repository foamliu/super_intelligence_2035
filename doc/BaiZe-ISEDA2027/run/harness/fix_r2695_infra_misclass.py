#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correct R2695 incr_eval misclassification: 3 real-patch evals were marked
infra due to path bug (script looked in logs/run_evaluation, results in
logs/evaluation). Per results.json all 3 are UNRESOLVED (failed=ability, not infra).
Move them from infra_or_quota -> failed and recompute n."""
import json
from pathlib import Path
REP = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports")
CORRECTIONS = {
    "cline-patched": "django__django-15280",
    "pi": "django__django-11848",
    "deepseek-harness": "django__django-12308",
}
for h, iid in CORRECTIONS.items():
    f = REP / f"eval_glm53_{h}.json"
    d = json.loads(f.read_text())
    moved = False
    for fld in ["infra_or_quota"]:
        if iid in d.get(fld, []):
            d[fld].remove(iid)
            moved = True
    if moved and iid not in d.get("failed", []):
        d.setdefault("failed", []).append(iid)
    d["n"] = len(d.get("resolved", [])) + len(d.get("failed", [])) + len(d.get("infra_or_quota", []))
    f.write_text(json.dumps(d, indent=2))
    print(f"{h}: moved {iid} infra->failed | resolved={len(d['resolved'])} "
          f"failed={len(d['failed'])} infra={len(d['infra_or_quota'])} n={d['n']}")
print("correction DONE")

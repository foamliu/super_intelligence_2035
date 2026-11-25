#!/usr/bin/env python3
"""Check cumulative eval status for R2292."""
import json, os

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}

total_resolved = 0
total_n = 0
for h in HARNESSES:
    ef = os.path.join(REPORT_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        r = len(d.get("resolved", []))
        f = len(d.get("failed", []))
        i = len(d.get("infra_or_quota", []))
        n = d.get("n", r + f + i)
        disp = DISPLAY.get(h, h)
        print(f"{disp}: n={n} resolved={r} failed={f} infra={i}")
        total_resolved += r
        total_n += n
    else:
        print(f"{DISPLAY.get(h,h)}: no file")
print(f"\nTOTAL: resolved={total_resolved} n={total_n}")

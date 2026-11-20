#!/usr/bin/env python3
"""Quick contamination check for v2 SFT corpus."""
import json, os

eval_path = os.path.expanduser("~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
eval_apis = set()
eval_entry_points = set()
with open(eval_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            task = json.loads(line)
            for api in task.get("metadata", {}).get("apis_used", []):
                eval_apis.add(api)
            ep = task.get("entry_point", "")
            if ep:
                eval_entry_points.add(ep)
        except Exception:
            pass

print("Eval APIs (blacklist): %d" % len(eval_apis))
print("Eval entry_points: %d" % len(eval_entry_points))

api_hits = 0
ep_hits = 0
total = 0
with open("/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/sft_pyaether_corpus_v2.jsonl") as f:
    for line in f:
        d = json.loads(line)
        total += 1
        for api in d.get("api_used", []):
            if api in eval_apis:
                api_hits += 1
        comp = d.get("completion", "")
        for ep in eval_entry_points:
            if ep and ep in comp:
                ep_hits += 1
                break

print("Total pairs: %d" % total)
print("API contamination hits: %d  Status: %s" % (api_hits, "PASS" if api_hits == 0 else "FAIL"))
print("Entry_point contamination hits: %d  Status: %s" % (ep_hits, "PASS" if ep_hits == 0 else "CHECK"))

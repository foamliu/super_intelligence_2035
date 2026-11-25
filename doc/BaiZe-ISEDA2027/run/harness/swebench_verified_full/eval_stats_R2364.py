#!/usr/bin/env python3
import json

harnesses = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
total_resolved = 0
total_evaluated = 0
total_pred = 0
for h in harnesses:
    f = f"reports/eval_glm53_{h}.json"
    try:
        d = json.load(open(f))
        rc = d["resolved_count"]
        ev = d["evaluated"]
        tp = d["total_predictions"]
        total_resolved += rc
        total_evaluated += ev
        total_pred += tp
        print(f"{h}: resolved={rc}/{ev} (total_pred={tp})")
    except Exception as e:
        print(f"{h}: error {e}")
print(f"TOTAL: resolved={total_resolved}/{total_evaluated} (total_pred={total_pred})")

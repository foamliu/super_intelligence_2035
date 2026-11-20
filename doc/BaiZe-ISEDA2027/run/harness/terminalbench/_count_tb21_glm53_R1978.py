#!/usr/bin/env python3
"""Count TB-2.1 glm53 7-way pass rates from /tmp/tb21_glm53_jobs."""
import json, os
from pathlib import Path

JOBS = Path("/tmp/tb21_glm53_jobs")
harnesses = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
total_all = 0
passed_all = 0
for h in harnesses:
    d = JOBS / h
    if not d.exists():
        print(f"{h}: dir not found")
        continue
    total = 0
    passed = 0
    errors = 0
    for f in d.rglob("result.json"):
        if "/20" not in str(f):
            continue
        total += 1
        try:
            r = json.loads(f.read_text())
            reward = r.get("verifier_result",{}).get("rewards",{}).get("reward",0)
            if reward == 1.0:
                passed += 1
            if r.get("exception_info"):
                errors += 1
        except:
            pass
    total_all += total
    passed_all += passed
    print(f"{h}: {passed} passed / {total} total (errors={errors})")
print(f"TOTAL: {passed_all} passed / {total_all} total")

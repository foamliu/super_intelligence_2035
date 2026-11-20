#!/usr/bin/env python3
"""R1981 monitoring stats."""
import json, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== EVAL REPORTS (reports/eval_glm53_*.json) ===")
for r in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']:
    ef = f"reports/eval_glm53_{r}.json"
    if os.path.isfile(ef):
        d = json.load(open(ef))
        n = d.get("n", 0)
        resolved = len(d.get("resolved", []))
        failed = len(d.get("failed", []))
        infra = len(d.get("infra_or_quota", []))
        print(f"  {r}: n={n} resolved={resolved} failed={failed} infra={infra} pass={resolved/max(n,1)*100:.1f}%")
    else:
        print(f"  {r}: no eval report (eval pending)")

print()
print("=== PREDICTIONS (predictions_glm53/) ===")
for r in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']:
    files = glob.glob(f"predictions_glm53/{r}__*.json")
    real = 0; empty = 0; err = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list) and d:
                p = d[0].get("model_patch", "") or ""
            elif isinstance(d, dict):
                p = d.get("model_patch", "") or ""
            else:
                p = ""
            if p.strip():
                real += 1
            else:
                empty += 1
        except:
            err += 1
    print(f"  {r}: total={len(files)} real={real} empty={empty} err={err}")

print()
print("=== TB-2.1 ===")
tb21_dir = "/tmp/tb21_glm53_jobs"
for r in ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']:
    rdir = os.path.join(tb21_dir, r)
    if not os.path.isdir(rdir):
        print(f"  {r}: no dir")
        continue
    done = 0; passed = 0
    for task_dir in os.listdir(rdir):
        task_path = os.path.join(rdir, task_dir)
        if not os.path.isdir(task_path):
            continue
        result_file = os.path.join(task_path, "verifier_result.json")
        if os.path.isfile(result_file):
            done += 1
            try:
                rd = json.load(open(result_file))
                rewards = rd.get("rewards", [])
                if rewards and any(v > 0 for v in rewards if v is not None):
                    passed += 1
            except:
                pass
    print(f"  {r}: done={done} passed={passed}")

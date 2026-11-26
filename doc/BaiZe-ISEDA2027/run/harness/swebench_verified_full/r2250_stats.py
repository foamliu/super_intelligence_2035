#!/usr/bin/env python3
"""R2250 stats: prediction counts + eval status + backlog."""
import json, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, 'predictions_glm53')
EVAL_DIR = os.path.join(BASE, 'reports')

HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']

print("=== PREDICTION FILES ===")
total_files = 0
total_real = 0
total_empty = 0
for h in HARNESSES:
    fs = sorted(glob.glob(os.path.join(PRED_DIR, h + '__*.json')))
    real = 0
    empty = 0
    for f in fs:
        try:
            j = json.load(open(f))
            # prediction file might be a list or dict
            if isinstance(j, list):
                # find the item with model_patch
                mp = ''
                for item in j:
                    if isinstance(item, dict) and 'model_patch' in item:
                        mp = (item.get('model_patch', '') or '').strip()
                        break
                if mp:
                    real += 1
                else:
                    empty += 1
            elif isinstance(j, dict):
                mp = (j.get('model_patch', '') or '').strip()
                if mp:
                    real += 1
                else:
                    empty += 1
        except Exception as e:
            empty += 1
    total_files += len(fs)
    total_real += real
    total_empty += empty
    print(f"  {h}: {len(fs)} files / {real} real / {empty} empty")

print(f"  TOTAL: {total_files} files / {total_real} real / {total_empty} empty")

print()
print("=== EVAL STATUS ===")
total_resolved = 0
total_evaluated = 0
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f'eval_glm53_{h}.json')
    if not os.path.exists(ef):
        print(f"  {h}: NO eval file")
        continue
    j = json.load(open(ef))
    evaluated = j.get('evaluated', 0)
    resolved_count = j.get('resolved_count', 0)
    n = j.get('n', 0)
    run_id = j.get('run_id', '?')
    resolved_list = j.get('resolved', [])
    failed_list = j.get('failed', [])
    infra_list = j.get('infra_or_quota', [])
    total_resolved += resolved_count
    total_evaluated += evaluated
    print(f"  {h}: evaluated={evaluated} resolved={resolved_count} n={n} run_id={run_id} (resolved_list={len(resolved_list)} failed_list={len(failed_list)} infra_list={len(infra_list)})")

print(f"  TOTAL: evaluated={total_evaluated} resolved={total_resolved}")

print()
print("=== BACKLOG (real patches not yet evaluated) ===")
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f'eval_glm53_{h}.json')
    eval_ids = set()
    if os.path.exists(ef):
        j = json.load(open(ef))
        for key in ['resolved', 'failed', 'infra_or_quota']:
            vals = j.get(key, [])
            if isinstance(vals, list):
                for v in vals:
                    if isinstance(v, str):
                        eval_ids.add(v)
    fs = sorted(glob.glob(os.path.join(PRED_DIR, h + '__*.json')))
    backlog = 0
    real = 0
    for f in fs:
        try:
            j = json.load(open(f))
            mp = ''
            iid = ''
            if isinstance(j, list):
                for item in j:
                    if isinstance(item, dict) and 'model_patch' in item:
                        mp = (item.get('model_patch', '') or '').strip()
                        iid = item.get('instance_id', '')
                        break
            elif isinstance(j, dict):
                mp = (j.get('model_patch', '') or '').strip()
                iid = j.get('instance_id', '')
            if mp:
                real += 1
                if iid and iid not in eval_ids:
                    backlog += 1
        except:
            pass
    print(f"  {h}: real={real} evaluated_ids={len(eval_ids)} backlog={backlog}")

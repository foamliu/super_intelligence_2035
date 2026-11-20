#!/usr/bin/env python3
"""Quick round status: predict counts + eval counts for all 7 routes."""
import glob, json, os, sys

ROUTES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
PRED_DIR = 'predictions_glm53'
EVAL_DIR = 'reports'

total_real = total_empty = total_files = 0
print("=== PREDICT (real/empty/total) ===")
for h in ROUTES:
    files = sorted(glob.glob(f'{PRED_DIR}/{h}__*.json'))
    real = empty = 0
    for f in files:
        try:
            d = json.load(open(f))
            patch = d[0].get('model_patch', '') if isinstance(d, list) and d else d.get('model_patch', '')
            if patch.strip():
                real += 1
            else:
                empty += 1
        except Exception:
            pass
    total_real += real; total_empty += empty; total_files += len(files)
    print(f"  {h:20s}: {real:4d} real / {empty:4d} empty / {len(files):4d} total")
pct = round(100 * total_real / total_files, 1) if total_files else 0
print(f"  {'TOTAL':20s}: {total_real:4d} real / {total_empty:4d} empty / {total_files:4d} total ({pct}%)")

total_res = total_eval = 0
print("\n=== EVAL (resolved/evaluated/infra) ===")
for h in ROUTES:
    f = f'{EVAL_DIR}/eval_glm53_{h}.json'
    try:
        d = json.load(open(f))
        res = d.get('resolved_count', 0)
        ev = d.get('evaluated', 0)
        nfail = len(d.get('failed', []))
        ninfra = len(d.get('infra_or_quota', []))
        total_res += res; total_eval += ev
        print(f"  {h:20s}: {res:4d} resolved / {ev:4d} evaluated / {nfail:4d} failed / {ninfra:3d} infra")
    except Exception as e:
        print(f"  {h:20s}: no eval ({e})")
print(f"  {'TOTAL':20s}: {total_res:4d} resolved / {total_eval:4d} evaluated")

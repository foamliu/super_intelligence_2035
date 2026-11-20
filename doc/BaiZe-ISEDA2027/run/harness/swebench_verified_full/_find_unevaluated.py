#!/usr/bin/env python3
"""Find unevaluated real-patch instances per route for incr_eval."""
import glob, json, os

ROUTES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
PRED_DIR = 'predictions_glm53'
EVAL_DIR = 'reports'

for h in ROUTES:
    # Load eval JSON to get already-evaluated instance IDs
    eval_file = f'{EVAL_DIR}/eval_glm53_{h}.json'
    try:
        ed = json.load(open(eval_file))
        done = set(ed.get('resolved', []) + ed.get('failed', []) + ed.get('infra_or_quota', []))
    except:
        done = set()

    # Find real-patch predictions not yet evaluated
    unevaluated = []
    for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
        try:
            d = json.load(open(pf))
            pred = d[0] if isinstance(d, list) and d else d
            iid = pred.get('instance_id', '')
            patch = pred.get('model_patch', '').strip()
            if patch and iid and iid not in done:
                unevaluated.append(iid)
        except:
            pass
    if unevaluated:
        print(f"{h}: {len(unevaluated)} unevaluated real-patch instances")
        for iid in unevaluated[:10]:
            print(f"  {iid}")
        if len(unevaluated) > 10:
            print(f"  ... and {len(unevaluated)-10} more")
    else:
        print(f"{h}: 0 unevaluated (all caught up)")

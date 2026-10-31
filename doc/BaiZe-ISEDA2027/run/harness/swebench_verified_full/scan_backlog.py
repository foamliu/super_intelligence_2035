#!/usr/bin/env python3
"""Scan for BACKLOG: predictions with a real (non-empty) patch but no eval report.json yet."""
import json, os, glob

pred_dir = 'predictions'
eval_base = 'logs/run_evaluation'
harnesses = ['cline-patched', 'opencode', 'pi', 'claude-code', 'codex', 'hermes', 'deepseek-harness']
backlog = []

for h in harnesses:
    for pf in sorted(glob.glob(f'{pred_dir}/{h}__*.json')):
        inst_id = os.path.basename(pf).replace(f'{h}__', '').replace('.json', '')
        try:
            d = json.load(open(pf))
        except Exception:
            continue
        # prediction files are a list with one dict, or a dict
        if isinstance(d, list):
            if not d:
                continue
            d = d[0]
        if not isinstance(d, dict):
            continue
        patch = d.get('model_patch', '') or d.get('patch', '')
        if not patch or patch.strip() == '':
            continue  # empty patch, skip
        # check if eval report exists
        found = False
        for ed in glob.glob(f'{eval_base}/verified_full_{h}/*/{inst_id}/report.json'):
            found = True
            break
        if not found:
            backlog.append((h, inst_id, len(patch)))

print(f'Total BACKLOG items (real patch, no report.json): {len(backlog)}')
for h, iid, plen in sorted(backlog):
    print(f'  {h:20s} {iid:50s} patchlen={plen}')

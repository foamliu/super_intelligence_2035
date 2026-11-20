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
        # check if eval report exists — dual-path (swebench v5.0.2 writes to
        # logs/evaluation/{run_id}/, older full evals wrote to logs/run_evaluation/{run_id}/)
        found = False
        for base in ('logs/evaluation', 'logs/run_evaluation'):
            for ed in glob.glob(f'{base}/verified_full_{h}*/{h}-kimi-k2.6-cloud/{inst_id}/report.json'):
                found = True
                break
            # also match model_dir variants (e.g. cline-kimi-k2.6-cloud)
            if not found:
                for ed in glob.glob(f'{base}/verified_full_{h}*/*/{inst_id}/report.json'):
                    found = True
                    break
            if found:
                break
        if not found:
            backlog.append((h, inst_id, len(patch)))

print(f'Total BACKLOG items (real patch, no report.json): {len(backlog)}')
for h, iid, plen in sorted(backlog):
    print(f'  {h:20s} {iid:50s} patchlen={plen}')

#!/usr/bin/env python3
"""Quick status counts for R1229."""
import json, glob, os

harnesses = ['cline-patched', 'opencode', 'pi', 'claude-code', 'codex', 'hermes', 'deepseek-harness']
total_pred = total_real = total_eval = total_resolved = 0
for h in harnesses:
    pred_files = sorted(glob.glob(f'predictions/{h}__*.json'))
    real = 0
    for pf in pred_files:
        try:
            d = json.load(open(pf))
        except Exception:
            continue
        if isinstance(d, list):
            d = d[0] if d else {}
        if isinstance(d, dict):
            patch = d.get('model_patch', '') or d.get('patch', '')
            if patch and patch.strip():
                real += 1
    reports = sorted(glob.glob(f'logs/run_evaluation/verified_full_{h}/*/*/report.json'))
    resolved = 0
    for rf in reports:
        try:
            d = json.load(open(rf))
        except Exception:
            continue
        # report.json = { "<instance_id>": { "resolved": bool, ... } }
        for iid, rec in d.items():
            if isinstance(rec, dict) and rec.get('resolved', False):
                resolved += 1
    print(f'  {h:20s} pred={len(pred_files):4d} real_patch={real:4d} eval={len(reports):4d} resolved={resolved:4d}')
    total_pred += len(pred_files); total_real += real
    total_eval += len(reports); total_resolved += resolved
print(f'  {"TOTAL":20s} pred={total_pred:4d} real_patch={total_real:4d} eval={total_eval:4d} resolved={total_resolved:4d}')

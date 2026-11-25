#!/usr/bin/env python3
"""Genuine backlog check R1610: real patch AND no report.json in ANY verified_full_<h>* run dir."""
import json, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
harnesses = ['cline-patched','opencode','pi','claude-code','codex','hermes','deepseek-harness']
eval_base = 'logs/run_evaluation'
genuine = []
for h in harnesses:
    for pf in sorted(glob.glob(f'predictions/{h}__*.json')):
        iid = os.path.basename(pf).replace(f'{h}__','').replace('.json','')
        try:
            d = json.load(open(pf))
            if isinstance(d, list):
                if not d: continue
                d = d[0]
            patch = d.get('model_patch','') or d.get('patch','')
            if not patch.strip(): continue
        except Exception:
            continue
        found = False
        for ed in (glob.glob(f'{eval_base}/verified_full_{h}*/{iid}/report.json')
                   + glob.glob(f'{eval_base}/verified_full_{h}*/*/{iid}/report.json')):
            found = True
            break
        if not found:
            genuine.append((h, iid, len(patch)))
print(f'GENUINE backlog (no report.json in ANY run dir): {len(genuine)}')
for h, iid, pl in sorted(genuine):
    print(f'  {h:20s} {iid:50s} patchlen={pl}')

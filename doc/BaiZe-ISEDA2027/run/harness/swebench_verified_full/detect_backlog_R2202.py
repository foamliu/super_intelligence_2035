#!/usr/bin/env python3
"""Detect eval backlog R2202: real patches not yet in eval report."""
import json, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
PRED_DIR = 'predictions_glm53'
EVAL_DIR = 'reports'
HARNESSES = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']

def real_patch(pf):
    try:
        d = json.load(open(pf))
        if isinstance(d, list):
            d = d[0] if d else {}
        p = (d.get('model_patch') or d.get('patch') or '').strip()
        return len(p) > 50, p
    except:
        return False, ''

for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f'eval_glm53_{h}.json')
    done = set()
    if os.path.exists(ef):
        ed = json.load(open(ef))
        done = set(ed.get('resolved',[])) | set(ed.get('failed',[])) | set(ed.get('infra_or_quota',[]))
    total = 0; real = 0; empty = 0; backlog = []
    for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
        total += 1
        isreal, patch = real_patch(pf)
        # extract instance id from filename: <h>__<repo>__<iid>.json
        base = os.path.basename(pf)
        iid = base[len(h)+2:-5]  # strip h__ prefix and .json suffix
        if isreal:
            real += 1
            if iid not in done:
                backlog.append((iid, len(patch)))
        else:
            empty += 1
    print(f'{h}: total={total} real={real} empty={empty} evaluated={len(done)} backlog={len(backlog)}')
    if backlog:
        for iid, plen in backlog[:8]:
            print(f'  BACKLOG {iid} patchlen={plen}')
        if len(backlog) > 8:
            print(f'  ... +{len(backlog)-8} more')

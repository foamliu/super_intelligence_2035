#!/usr/bin/env python3
"""Collect stats for R2183 heartbeat."""
import json, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

HARNESSES = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
DISPLAY = {'cline-patched':'cline','deepseek-harness':'deepseek'}

total_resolved = 0
total_pred_real = 0
cline_empty_ids = []

for h in HARNESSES:
    files = glob.glob(f'predictions_glm53/{h}__*.json')
    real = 0; empty = 0
    for f in sorted(files):
        try:
            d = json.load(open(f))
            if isinstance(d, list):
                p = d[0] if d else {}
            else:
                p = d
            if p.get('model_patch', '').strip():
                real += 1
            else:
                empty += 1
                if h == 'cline-patched':
                    iid = os.path.basename(f).replace('cline-patched__','').replace('.json','')
                    cline_empty_ids.append(iid)
        except:
            pass
    ef = f'reports/eval_glm53_{h}.json'
    ed = json.load(open(ef))
    resolved = len(ed.get('resolved',[]))
    failed = len(ed.get('failed',[]))
    infra = len(ed.get('infra_or_quota',[]))
    total_resolved += resolved
    total_pred_real += real
    name = DISPLAY.get(h, h)
    print(f'{name}: files={len(files)} real={real} empty={empty} resolved={resolved} failed={failed} infra={infra}')

print(f'\nTOTAL resolved = {total_resolved}')
print(f'TOTAL pred_real = {total_pred_real}')
print(f'cline empty_ids ({len(cline_empty_ids)}): {cline_empty_ids}')

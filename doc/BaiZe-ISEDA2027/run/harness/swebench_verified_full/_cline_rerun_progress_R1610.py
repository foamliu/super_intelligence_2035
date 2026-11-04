#!/usr/bin/env python3
"""Count cline rerun progress: how many of 58 rerun ids now have a non-empty patch."""
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ids = [l.strip() for l in open('cline_rerun_ids.txt') if l.strip()]
patch = 0; nopatch = 0; missing = 0
nopatch_ids = []
for iid in ids:
    f = 'predictions/cline-patched__' + iid + '.json'
    if not os.path.exists(f):
        missing += 1; continue
    d = json.load(open(f))
    if isinstance(d, list):
        d = d[0] if d else {}
    p = d.get('model_patch', '') or ''
    if p.strip():
        patch += 1
    else:
        nopatch += 1
        nopatch_ids.append(iid)
print(f'cline rerun 58: patch={patch} no_patch={nopatch} missing={missing}')
print(f'no_patch_ids: {nopatch_ids}')

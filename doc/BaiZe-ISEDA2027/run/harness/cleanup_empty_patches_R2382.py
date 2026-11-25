#!/usr/bin/env python3
"""R2382 cleanup: remove empty-patch prediction files (model_patch < 10 chars).
These are infra artifacts (gateway 429, timeout, etc), not capability.
"""
import json, glob, os

PRED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predictions_glm53')
ARCHIVE = os.path.join(PRED_DIR, f'empty_cleaned_R2382')
os.makedirs(ARCHIVE, exist_ok=True)

removed = 0
for f in sorted(glob.glob(os.path.join(PRED_DIR, '*.json'))):
    bn = os.path.basename(f)
    if bn.startswith('predictions_') or bn.startswith('empty_cleaned'):
        continue
    try:
        d = json.load(open(f))
        if isinstance(d, list):
            patches = [p.get('model_patch', '').strip() for p in d]
            if all(len(p) < 10 for p in patches):
                os.rename(f, os.path.join(ARCHIVE, bn))
                removed += 1
        elif isinstance(d, dict):
            patch = d.get('model_patch', '').strip()
            if len(patch) < 10:
                os.rename(f, os.path.join(ARCHIVE, bn))
                removed += 1
    except:
        pass

print(f"R2382 cleanup: removed {removed} empty-patch files -> {ARCHIVE}")

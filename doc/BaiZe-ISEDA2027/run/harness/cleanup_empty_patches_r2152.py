#!/usr/bin/env python3
"""R2152: cleanup empty-patch prediction files (429 infra). Re-predicted when quota recovers."""
import json, glob, os

d = 'swebench_verified_full/predictions_glm53'
harnesses = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
delc = 0
details = []
for h in harnesses:
    hc = 0
    for f in sorted(glob.glob(os.path.join(d, h + '__*.json'))):
        try:
            dd = json.load(open(f))
            mp = dd[0].get('model_patch', '') if isinstance(dd, list) and dd else ''
            if not mp.strip():
                os.remove(f)
                hc += 1
                delc += 1
        except Exception:
            pass
    if hc:
        details.append(h + ':' + str(hc))
print('R2152 DELETED %d empty-patch files: %s' % (delc, ', '.join(details)))

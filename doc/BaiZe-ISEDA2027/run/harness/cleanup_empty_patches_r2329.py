#!/usr/bin/env python3
"""R2329 cleanup: remove empty-patch prediction files.

R2329 wake: gateway 200 (all functional), 10 new empty patches found
(not in-progress, age > 120s). Skipped 4 in-progress/recent empties.
Empty to clean: 1 cline + 4 codex + 4 cc + 1 pi = 10 empty.
After cleanup: real patches unchanged (no new real this round).
"""
import glob, json, os, time

PRED_DIR = 'harness/swebench_verified_full/predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
RUNNING = {'cline-patched__django__django-13794', 'codex__sympy__sympy-15345'}
now = time.time()

removed = 0; skipped = 0
for h in HARNESSES:
    for f in glob.glob(f'{PRED_DIR}/{h}__*.json'):
        try:
            d = json.load(open(f))
            patch = ''
            if isinstance(d, list):
                for item in d:
                    if isinstance(item, dict):
                        patch = item.get('model_patch', '') or item.get('patch', '') or ''
                        if patch.strip():
                            break
            elif isinstance(d, dict):
                patch = d.get('model_patch', '') or d.get('patch', '')
            if not patch.strip():
                name = os.path.basename(f).replace('.json', '')
                age = now - os.path.getmtime(f)
                if name in RUNNING or age < 120:
                    skipped += 1
                    continue
                os.remove(f)
                removed += 1
        except Exception:
            pass

print(f'R2329 cleanup: removed {removed} empty patches, skipped {skipped} (in-progress/recent)')

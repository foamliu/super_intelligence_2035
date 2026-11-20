#!/usr/bin/env python3
"""R2332 cleanup: remove empty-patch prediction files.

R2332 wake: gateway 200 (all functional), 13 empty patches found.
Running instances (skip): cline django-14007, codex sympy-18199,
cc scikit-learn-25747.
After cleanup: remaining empties = those still running.
"""
import glob, json, os, time

PRED_DIR = 'harness/swebench_verified_full/predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
RUNNING = {
    'cline-patched__django__django-14007',
    'codex__sympy__sympy-18199',
    'claude-code__scikit-learn__scikit-learn-25747',
}
now = time.time()

removed = 0; skipped = 0; detail = []
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
                detail.append(name)
        except Exception:
            pass

print(f'R2332 cleanup: removed {removed} empty patches, skipped {skipped} (in-progress/recent)')
if detail:
    print('  removed:', ', '.join(detail))

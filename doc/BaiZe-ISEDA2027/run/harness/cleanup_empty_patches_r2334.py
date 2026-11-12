#!/usr/bin/env python3
"""R2334 cleanup: remove empty-patch prediction files.

R2334 wake: gateway functional (predict 4/7 alive and progressing),
Running instances (skip):
  cline-patched django-14053, codex sympy-19783, cc sphinx-7757, pi sphinx-11445.
After cleanup: remaining empties = those still running (not yet written to disk).
"""
import glob, json, os, time

PRED_DIR = 'harness/swebench_verified_full/predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
RUNNING = {
    'cline-patched__django__django-14053',
    'codex__sympy__sympy-19783',
    'claude-code__sphinx-doc__sphinx-7757',
    'pi__sphinx-doc__sphinx-11445',
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

print(f'R2334 cleanup: removed {removed} empty patches, skipped {skipped} (in-progress/recent)')
if detail:
    print('  removed:', ', '.join(detail))

#!/usr/bin/env python3
"""incr cleanup R2321: remove empty-patch prediction files.

R2321 wake: gateway 200. Found 4 empty patches:
2 claude-code (django__django-16454, matplotlib__matplotlib-20826) +
2 pi (scikit-learn__scikit-learn-11578, scikit-learn__scikit-learn-12682).
After cleanup: all real patches.
"""
import glob, json, os

PRED_DIR = 'predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']

removed = 0
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
                print(f'  removing empty: {os.path.basename(f)}')
                os.remove(f)
                removed += 1
        except Exception:
            pass

print(f'R2321 cleanup: removed {removed} empty patches')

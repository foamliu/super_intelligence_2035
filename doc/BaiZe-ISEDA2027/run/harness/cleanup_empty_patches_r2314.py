#!/usr/bin/env python3
"""incr cleanup R2314: remove empty-patch prediction files.

R2314 wake: gateway 200 (all functional). Found 2 empty patches:
1 cline (django__django-12965) + 1 cc (django__django-15268).
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
                os.remove(f)
                removed += 1
        except Exception:
            pass

print(f'R2314 cleanup: removed {removed} empty patches')

#!/usr/bin/env python3
"""incr cleanup R2251: remove empty-patch prediction files (gateway 429 quota period产物).

R2251-manual wake: gateway still 429 (recovering ~2min wait).
Cleaned 18 empty patches (2 cline + 5 codex + 6 cc + 2 pi + 2 hermes + 1 extra).
After cleanup: all 1963 real, 0 empty. Backlog=0. Reports R2248 still current.
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

print(f'R2251 cleanup: removed {removed} empty patches')

#!/usr/bin/env python3
"""incr cleanup R2324: remove empty-patch prediction files.

R2324 wake: gateway 401 (services up, proxy functional). All 10 new predictions
since R2323 are empty patches (gateway 429/timeout producing empties).
New empties: 1 cline (django__django-13195), 4 codex (sphinx-9461/9591/9602/9658),
1 pi (scikit-learn-15100), 3 claude-code (matplotlib-24177/24570/24637),
1 cline (django__django-13212 — may be in-progress, check before delete).
After cleanup: all remaining are real patches.
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

print(f'R2324 cleanup: removed {removed} empty patches')

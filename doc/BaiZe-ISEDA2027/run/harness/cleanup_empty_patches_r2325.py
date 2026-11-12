#!/usr/bin/env python3
"""incr cleanup R2325: remove empty-patch prediction files.

R2325 wake: gateway 200 (functional). 13 empty patches found across 4 active
predict routes (cline/codex/claude-code/pi). All empties are gateway 429/timeout
producing empties. After cleanup: remaining real patches ready for incr_eval
(0 new real this round, eval fully caught up).
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

print(f'R2325 cleanup: removed {removed} empty patches')

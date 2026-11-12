#!/usr/bin/env python3
"""incr cleanup R2305: remove empty-patch prediction files (gateway 429 quota period产物).

R2305 wake: gateway 200 (all functional), but 9 new empty patches appeared
since R2304 (all 429/timeout products from predict processes hitting rate limits).
Empty: 3 codex + 3 cc + 1 cline + 1 pi + 1 hermes = 9 empty patches.
After cleanup: all real patches, 0 empty. No new real patches → no incr_eval needed.
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

print(f'R2305 cleanup: removed {removed} empty patches')

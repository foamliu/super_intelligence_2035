#!/usr/bin/env python3
"""incr cleanup R2304: remove empty-patch prediction files (gateway 429 quota period产物).

R2304 wake: gateway 200 (all functional), but 12 new empty patches appeared
since R2303 (all 429 quota period products from predict processes hitting rate limits).
Cleaned: 2 cline + 4 codex + 4 cc + 1 pi + 1 hermes = 12 empty patches.
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

print(f'R2304 cleanup: removed {removed} empty patches')

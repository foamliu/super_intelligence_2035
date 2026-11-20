#!/usr/bin/env python3
"""R2358 cleanup: remove empty-patch prediction files (429/quota products).

R2358 wake: gateway 200 stable. 6 empty patches found:
  codex: django-11728, 11790, 11815, 11820 (4)
  pi:    sphinx-8621, 9230 (2)
  KEEP: codex/django-11848 (in-flight, codex predict currently working on it)
After cleanup: all remaining files are real patches (or in-flight 11848).
"""
import glob, json, os

PRED_DIR = 'swebench_verified_full/predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
KEEP = {'codex__django__django-11848.json'}  # in-flight

removed = 0
kept_inflight = 0
for h in HARNESSES:
    for f in glob.glob(f'{PRED_DIR}/{h}__*.json'):
        basename = os.path.basename(f)
        if basename in KEEP:
            kept_inflight += 1
            continue
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
                print(f'  removed: {basename}')
        except Exception:
            pass

print(f'R2358 cleanup: removed {removed} empty patches, kept {kept_inflight} in-flight')

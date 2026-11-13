#!/usr/bin/env python3
"""R2363 cleanup: remove empty-patch prediction files.

R2363 wake: gateway 200 stable. 1 empty patch found:
  codex: django-12858 (completed with empty patch, codex now on django-12965)
After cleanup: all remaining files are real patches.
"""
import glob, json, os

PRED_DIR = 'swebench_verified_full/predictions_glm53'
HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
# codex django-12965 is in-flight (codex predict currently working on it)
KEEP = {'codex__django__django-12965.json'}

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

print(f'R2363 cleanup: removed {removed} empty patches, kept {kept_inflight} in-flight')

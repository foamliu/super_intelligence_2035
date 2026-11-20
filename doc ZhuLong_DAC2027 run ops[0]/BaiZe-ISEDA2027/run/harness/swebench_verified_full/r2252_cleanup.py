#!/usr/bin/env python3
"""R2250 cleanup: remove empty model_patch prediction files (gateway 429 quota products)."""
import json, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, 'predictions_glm53')

HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']

total_removed = 0
for h in HARNESSES:
    fs = sorted(glob.glob(os.path.join(PRED_DIR, h + '__*.json')))
    removed = 0
    for f in fs:
        try:
            j = json.load(open(f))
            mp = ''
            if isinstance(j, list):
                for item in j:
                    if isinstance(item, dict) and 'model_patch' in item:
                        mp = (item.get('model_patch', '') or '').strip()
                        break
            elif isinstance(j, dict):
                mp = (j.get('model_patch', '') or '').strip()
            if not mp:
                os.remove(f)
                removed += 1
        except Exception as e:
            print(f"  ERROR reading {f}: {e}")
    if removed > 0:
        print(f"  {h}: removed {removed} empty patches")
    total_removed += removed

print(f"TOTAL removed: {total_removed}")

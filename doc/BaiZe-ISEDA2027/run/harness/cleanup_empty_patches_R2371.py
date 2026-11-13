#!/usr/bin/env python3
"""Clean up empty patches for R2364."""
import json, glob, os
from pathlib import Path

PRED_DIR = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53")
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]
removed = 0
for h in HARNESSES:
    for f in sorted(glob.glob(str(PRED_DIR / f"{h}__*.json"))):
        try:
            d = json.loads(Path(f).read_text())
            if isinstance(d, dict):
                d = [d]
            if not any((p.get("model_patch") or "").strip() for p in d):
                os.remove(f)
                removed += 1
                print(f"  removed empty: {os.path.basename(f)}")
        except Exception as e:
            print(f"  error reading {f}: {e}")
print(f"Total removed: {removed}")

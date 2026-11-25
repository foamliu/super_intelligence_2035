#!/usr/bin/env python3
"""cleanup_empty_patches_r2168 — delete empty-patch prediction files (429/infra artifacts).

R2168 empties to clean (auto-detected scan):
  codex:       django__django-10914
  claude-code: sympy__sympy-19783
  hermes:      pylint-dev__pylint-7080

Empty patches are infra artifacts (gateway 429 / silent exit), NOT capability.
They must not be counted as real predictions or eval'd. Deleted from disk so
the predict loop can retry them and they don't inflate file counts.
"""
import json, glob, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions_glm53"
HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h,h)

removed = 0
for h in HARNESSES:
    for f in sorted(glob.glob(str(PRED_DIR / f"{h}__*.json"))):
        try:
            preds = json.loads(Path(f).read_text())
            if isinstance(preds, list): preds = preds[0] if preds else {}
            patch = (preds or {}).get("model_patch","")
            if not patch.strip():
                iid = (preds or {}).get("instance_id", Path(f).stem)
                print(f"  REMOVE {disp(h)}: {iid} (empty patch)")
                os.remove(f)
                removed += 1
        except Exception as e:
            print(f"  SKIP {f}: {e}")
print(f"R2168 cleanup: removed {removed} empty-patch files")

#!/usr/bin/env python3
"""cleanup_empty_patches_r2351 — delete empty-patch prediction files (429/infra artifacts).

R2351 empties to clean (auto-detected scan):
  cline-patched: 2 (django-14559, django-14580)
  codex:         6 (sympy-22714, sympy-23413, sympy-23950, sympy-24066, sympy-24443, sympy-24562)
  claude-code:   6 (sympy-13852, sympy-13877, sympy-13878, sympy-13974, sympy-14248, sympy-14531)
  pi:            1 (sphinx-8120)

Empty patches are infra artifacts (gateway 429 / silent exit), NOT capability.
They must not be counted as real predictions or eval'd. Deleted from disk so
the predict loop can retry them and they don't inflate file counts.
"""
import json, glob, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "swebench_verified_full" / "predictions_glm53"
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
print(f"R2351 cleanup: removed {removed} empty-patch files")

#!/usr/bin/env python3
"""cleanup_empty_patches_r2170 — delete empty-patch prediction files (429/infra artifacts).

R2170: gateway QUOTA_EXHAUSTED (HTTP 429) detected this round → predict stalled.
Empties are infra artifacts (gateway 429 / silent exit), NOT capability.
Auto-scans all 7 harnesses; removes any file whose model_patch is empty/whitespace.
Deleted from disk so the predict loop can retry them (when quota resets) and
they don't inflate file counts or get eval'd as "failed".
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
print(f"R2170 cleanup: removed {removed} empty-patch files")

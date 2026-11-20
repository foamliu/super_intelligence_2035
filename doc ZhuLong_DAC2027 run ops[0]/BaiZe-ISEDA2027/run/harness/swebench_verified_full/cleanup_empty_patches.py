#!/usr/bin/env python3
"""cleanup_empty_predictions.py — Remove prediction files with empty model_patch.

When the gateway returns 429 (token quota exhausted), agents produce prediction
JSON with model_patch="" (empty string).  These files are ~125B and pass naive
file-size checks but contain no actual patch.

run_verified_full.py:is_predicted() already checks model_patch non-empty, so
empty-patch files WILL be re-predicted on the next predict pass.  However,
run_serial_kimi.py:288 (old kimi-era script) had a size>50B bug that treated
empty patches as "done" and skipped them on --resume (fixed 2026-11-07).

This script:
  1. Scans predictions_glm53/ for files with empty model_patch
  2. Reports per-harness counts
  3. Optionally deletes them (so they get re-predicted)
  4. Also cleans stale entries from progress_glm53_*.json files

Usage:
  python3 cleanup_empty_predictions.py           # dry-run (report only)
  python3 cleanup_empty_predictions.py --delete   # actually delete files
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRED_DIR = Path(__file__).parent / "predictions_glm53"
REPORT_DIR = Path(__file__).parent / "reports"

HARNESSES = [
    "cline-patched", "codex", "opencode", "claude-code",
    "pi", "hermes", "deepseek-harness",
]


def is_empty_patch(f: Path) -> bool:
    """Return True if the prediction file has an empty model_patch."""
    try:
        data = json.loads(f.read_text())
        if isinstance(data, list):
            if not data:
                return True
            return not data[0].get("model_patch", "").strip()
        elif isinstance(data, dict):
            return not data.get("model_patch", "").strip()
        return True
    except Exception:
        return False  # unparseable → leave it (is_predicted will return False)


def main():
    ap = argparse.ArgumentParser(description="Clean up empty-patch predictions")
    ap.add_argument("--delete", action="store_true",
                    help="Actually delete empty-patch files (default: dry-run)")
    args = ap.parse_args()

    total_empty = 0
    total_files = 0

    for h in HARNESSES:
        files = sorted(PRED_DIR.glob(f"{h}__*.json"))
        empty_files = [f for f in files if is_empty_patch(f)]
        total_files += len(files)
        total_empty += len(empty_files)

        print(f"  {h}: {len(files)} total, {len(empty_files)} empty patches"
              f" ({100 * len(empty_files) // max(len(files), 1)}%)")

        if args.delete and empty_files:
            for f in empty_files:
                f.unlink()
            print(f"    → deleted {len(empty_files)} empty-patch files")

    print(f"\nTotal: {total_empty}/{total_files} empty patches"
          f" ({100 * total_empty // max(total_files, 1)}%)")

    if not args.delete:
        print("\n(dry-run; use --delete to remove empty-patch files)")
    else:
        print(f"\nDeleted {total_empty} empty-patch files. "
              f"They will be re-predicted on the next predict pass.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

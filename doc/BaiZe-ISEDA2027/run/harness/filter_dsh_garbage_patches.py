#!/usr/bin/env python3
"""
Filter deepseek-harness garbage patches (>1MB = git diff of entire venv directory).
Sets model_patch="" for any prediction file >1MB, making them effectively empty patches.

Usage:
    cd swebench_verified_full
    python3 filter_dsh_garbage_patches.py --pred-dir predictions_doubao_pro --dry-run
    python3 filter_dsh_garbage_patches.py --pred-dir predictions_doubao_pro

This should be run BEFORE eval (incremental_eval_merge.py) to ensure garbage patches
don't waste eval time or produce misleading results.
"""
import json
import glob
import os
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Filter DSH garbage patches (>1MB venv diffs)')
    parser.add_argument('--pred-dir', default='predictions_doubao_pro',
                        help='Prediction directory (default: predictions_doubao_pro)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Only report, do not modify files')
    parser.add_argument('--size-threshold', type=int, default=1_000_000,
                        help='File size threshold in bytes (default: 1MB)')
    args = parser.parse_args()

    pred_dir = args.pred_dir
    if not os.path.isdir(pred_dir):
    print(f"ERROR: directory not found: {pred_dir}")
        sys.exit(1)

    pattern = os.path.join(pred_dir, 'deepseek-harness__*.json')
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} deepseek-harness prediction files in {pred_dir}")

    garbage_files = []
    for f in files:
        fsize = os.path.getsize(f)
        if fsize > args.size_threshold:
            garbage_files.append((f, fsize))

    print(f"Garbage patches (>{args.size_threshold/1e6:.1f}MB): {len(garbage_files)}")
    for f, sz in garbage_files:
        print(f"  {os.path.basename(f)}: {sz/1e6:.1f}MB")

    if not garbage_files:
        print("No garbage patches found. Nothing to do.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would set model_patch='' for {len(garbage_files)} files")
        return

    modified = 0
    for f, sz in garbage_files:
        try:
            d = json.load(open(f))
            if isinstance(d, list) and d:
                d[0]['model_patch'] = ''
                d[0]['_garbage_filtered'] = True
                d[0]['_original_size_bytes'] = sz
            elif isinstance(d, dict):
                d['model_patch'] = ''
                d['_garbage_filtered'] = True
                d['_original_size_bytes'] = sz
            else:
                print(f"  SKIP {os.path.basename(f)}: unknown format")
                continue
            with open(f, 'w') as fout:
                json.dump(d, fout, indent=2)
            modified += 1
        except Exception as e:
            print(f"  ERROR {os.path.basename(f)}: {e}")

    print(f"\nDone: filtered {modified}/{len(garbage_files)} garbage patches (set model_patch='')")
    print("These will now be treated as empty patches in eval.")


if __name__ == '__main__':
    main()

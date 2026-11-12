#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stackv3_tokenize_rerun_failed.py — Re-run tokenization for failed shards.

Reads failed shard IDs from /tmp/stackv3_failed_shard_ids.txt, maps them to
original parquet paths, and calls process_shard with correct shard indices.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
from multiprocessing import Pool

PARQUET_DIR = "/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data"
OUTPUT_DIR = "/nas_train/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train"
FAILED_IDS_FILE = "/tmp/stackv3_failed_shard_ids.txt"

def main():
    from stackv3_tokenize import process_shard, get_all_parquets
    all_parquets = get_all_parquets()
    print(f"Total parquets: {len(all_parquets)}")

    # Read failed shard IDs
    with open(FAILED_IDS_FILE) as f:
        failed_ids = [int(l.strip()) for l in f if l.strip()]
    print(f"Failed shard IDs to re-run: {len(failed_ids)}")

    # Build tasks with ORIGINAL shard indices
    tasks = [(sid, str(all_parquets[sid]), OUTPUT_DIR) for sid in failed_ids if sid < len(all_parquets)]
    print(f"Tasks prepared: {len(tasks)}")

    t0 = time.time()
    all_stats = []
    with Pool(min(4, len(tasks))) as pool:
        for i, stats in enumerate(pool.imap_unordered(process_shard, tasks)):
            all_stats.append(stats)
            si = stats.get('shard_idx', '?')
            nt = stats.get('num_tokens', 0)
            dt = time.time() - t0
            done = i + 1
            status = 'SKIP' if stats.get('skipped') else ('ERR' if stats.get('error') else 'OK')
            print(f"  [{done}/{len(tasks)}] shard={si} {status} tokens={nt:,} elapsed={dt:.0f}s", flush=True)

    total_time = time.time() - t0
    total_tokens = sum(s.get('num_tokens', 0) for s in all_stats)
    n_errors = sum(1 for s in all_stats if s.get('error'))
    n_skipped = sum(1 for s in all_stats if s.get('skipped'))
    print(f"\nDone: {len(tasks)} shards in {total_time:.0f}s")
    print(f"  Tokens: {total_tokens:,}  Errors: {n_errors}  Skipped: {n_skipped}")

if __name__ == '__main__':
    main()

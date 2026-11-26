#!/usr/bin/env python3
"""Read all NCCL benchmark JSON results and print a summary table."""
import json
import os
import glob

files = sorted(glob.glob("nccl_bench_*.json"))
print(f"{'Config':<20} {'1M busbw':>10} {'10M busbw':>10} {'100M busbw':>11} {'500M busbw':>11} {'1G busbw':>10}")
print("-" * 75)

for f in files:
    name = f.replace("nccl_bench_", "").replace(".json", "")
    try:
        d = json.load(open(f))
        row = {}
        for r in d["results"]:
            row[r["size_mb"]] = r["busbw_gbs"]
        vals = []
        for sz in [1.0, 10.0, 100.0, 500.0, 1024.0]:
            if sz in row:
                vals.append(f"{row[sz]:>10.2f}")
            else:
                vals.append(f"{'--':>10}")
        print(f"{name:<20} {'  '.join(vals)}")
    except Exception as e:
        print(f"{name:<20} ERROR: {e}")

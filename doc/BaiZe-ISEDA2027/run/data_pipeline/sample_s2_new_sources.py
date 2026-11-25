#!/usr/bin/env python3
"""sample_s2_new_sources.py — Sample text from S2 new sources for contamination scan.

Extracts text from the 4 S2 zero-overlap sources, handling different parquet
schemas, and writes a representative sample (≥10K docs) to a single .jsonl per
source for check_contamination.py to scan.

Schemas:
  - stack-v3:      nested files[].content  (1 row = 1 repo with N files)
  - finemath:      top-level text column
  - nemotron:      top-level text column
  - megamath-web-pro: top-level text column

Usage:
  python sample_s2_new_sources.py --out-dir /tmp/contam_s2_samples --docs-per-source 12000
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import pyarrow.parquet as pq


SOURCES = {
    "stack-v3": {
        "dir": "/nas_user/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/data",
        "mode": "nested_files",  # files[].content
    },
    "finemath": {
        "dir": "/nas_user/app.e0031982/datasets/HuggingFaceTB/finemath/finemath-3plus",
        "mode": "text_col",
    },
    "nemotron": {
        "dir": "/nas_user/app.e0031982/datasets/nvidia/Nemotron-CC-Math-v1/3",
        "mode": "text_col",
    },
    "megamath-web-pro": {
        "dir": "/nas_user/app.e0031982/datasets/IFM/MegaMath/megamath-web-pro",
        "mode": "text_col",
    },
}

# How many parquet files to sample from (evenly spaced)
N_FILES = 12


def list_parquets(d: str) -> list[Path]:
    return sorted(Path(d).glob("*.parquet"))


def pick_evenly(files: list[Path], n: int) -> list[Path]:
    """Pick n evenly-spaced files from the sorted list."""
    if len(files) <= n:
        return files
    step = len(files) / n
    idxs = [int(i * step) for i in range(n)]
    # Deduplicate while preserving order
    seen = set()
    result = []
    for i in idxs:
        if i not in seen:
            seen.add(i)
            result.append(files[i])
    return result


def extract_text_col(pf, max_docs: int):
    """Yield text from a parquet file with a top-level 'text' column."""
    for batch in pf.iter_batches(batch_size=256, columns=["text"]):
        for row in batch.to_pylist():
            t = row.get("text")
            if t and isinstance(t, str) and len(t) >= 8:
                yield t


def extract_nested_files(pf, max_docs: int):
    """Yield text from stack-v3 parquet (files[].content per row)."""
    for batch in pf.iter_batches(batch_size=64, columns=["files"]):
        for row in batch.to_pylist():
            files_list = row.get("files")
            if not files_list:
                continue
            for f in files_list:
                content = f.get("content") if isinstance(f, dict) else None
                if content and isinstance(content, str) and len(content) >= 8:
                    yield content


def sample_source(name: str, info: dict, target_docs: int, out_path: Path):
    files = list_parquets(info["dir"])
    if not files:
        print(f"  [{name}] WARNING: no parquet files in {info['dir']}")
        return 0
    picked = pick_evenly(files, N_FILES)
    docs_per_file = math.ceil(target_docs / len(picked))

    mode = info["mode"]
    extractor = extract_nested_files if mode == "nested_files" else extract_text_col

    written = 0
    with open(out_path, "w", encoding="utf-8") as fout:
        for fp in picked:
            try:
                pf = pq.ParquetFile(str(fp))
                for text in extractor(pf, docs_per_file):
                    if written >= target_docs:
                        break
                    # Cap individual doc size to avoid memory issues (1MB)
                    if len(text) > 1_048_576:
                        text = text[:1_048_576]
                    fout.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
                    written += 1
                if written >= target_docs:
                    break
            except Exception as e:
                print(f"  [{name}] ERROR reading {fp.name}: {e}")
    print(f"  [{name}] sampled {written} docs from {len(picked)} files → {out_path}")
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/tmp/contam_s2_samples")
    ap.add_argument("--docs-per-source", type=int, default=12000)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for name, info in SOURCES.items():
        out_path = out_dir / f"{name}.jsonl"
        n = sample_source(name, info, args.docs_per_source, out_path)
        total += n
    print(f"\n[done] total {total} docs sampled across {len(SOURCES)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())

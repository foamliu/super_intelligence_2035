#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convert_idx_format.py — Convert simple text .idx to MMapIndexedDataset binary .idx.

Some tokenization scripts wrote .idx as text (token count only) instead of
proper Megatron MMapIndexedDataset binary format. This script scans .bin files
for EOD tokens (id=129280) to reconstruct document boundaries and writes proper .idx.

Usage:
    python convert_idx_format.py --src-dir <dir> [--dry-run] [--verify-only]
"""
from __future__ import annotations
import argparse, json, os, re, struct, sys, time
import numpy as np

MAGIC = b"MMIDIDX\x00\x00"
VERSION = 1
DTYPE_CODE_INT32 = 4
INT32_BYTES = 4
INT64_BYTES = 8
HEADER_SIZE = 34
EOD_TOKEN_ID = 129280


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def natkey(p):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", os.path.basename(p))]

def is_proper_idx(idx_path):
    try:
        with open(idx_path, "rb") as f:
            return f.read(9) == MAGIC
    except Exception:
        return False

def write_idx(idx_path, seq_lens, seq_ptrs, doc_idx):
    with open(idx_path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<Q", VERSION))
        f.write(struct.pack("<B", DTYPE_CODE_INT32))
        f.write(struct.pack("<Q", len(seq_lens)))
        f.write(struct.pack("<Q", len(doc_idx)))
        f.write(np.asarray(seq_lens, dtype=np.int32).tobytes())
        f.write(np.asarray(seq_ptrs, dtype=np.int64).tobytes())
        f.write(np.asarray(doc_idx, dtype=np.int64).tobytes())

def read_idx_header(idx_path):
    with open(idx_path, "rb") as f:
        magic = f.read(9)
        if magic != MAGIC:
            return None
        version = struct.unpack("<Q", f.read(8))[0]
        dtype_code = struct.unpack("<B", f.read(1))[0]
        seq_count = struct.unpack("<Q", f.read(8))[0]
        doc_count = struct.unpack("<Q", f.read(8))[0]
        return {"version": version, "dtype_code": dtype_code,
                "seq_count": seq_count, "doc_count": doc_count}

def convert_shard(bin_path, idx_path, json_path, dry_run=False):
    if is_proper_idx(idx_path):
        return {"skipped": True, "reason": "already_proper_format"}

    meta = {}
    if os.path.isfile(json_path):
        with open(json_path) as f:
            meta = json.load(f)
    expected_tokens = meta.get("num_tokens", 0)
    expected_docs = meta.get("num_documents", 0)

    bin_size = os.path.getsize(bin_path)
    arr = np.memmap(bin_path, dtype=np.int32, mode="r")
    total_tokens = len(arr)

    eod_positions = np.where(arr == EOD_TOKEN_ID)[0]

    if len(eod_positions) == 0:
        log(f"  WARN: no EOD found, treating entire .bin as one document")
        seq_lens = np.array([total_tokens], dtype=np.int32)
        seq_ptrs = np.array([0], dtype=np.int64)
        num_docs = 1
    else:
        num_docs = len(eod_positions)
        last_eod = eod_positions[-1]
        if last_eod < total_tokens - 1:
            log(f"  WARN: {total_tokens - 1 - last_eod} tokens after last EOD")
            starts = np.concatenate([[0], eod_positions[:-1] + 1])
            ends = eod_positions + 1
            ends = np.append(ends, total_tokens)
            starts = np.append(starts, eod_positions[-1] + 1)
            num_docs = len(ends)
        else:
            starts = np.concatenate([[0], eod_positions[:-1] + 1])
            ends = eod_positions + 1
        seq_lens = (ends - starts).astype(np.int32)
        seq_ptrs = (starts * INT32_BYTES).astype(np.int64)

    total_from_lens = int(seq_lens.sum())
    if total_from_lens != total_tokens:
        log(f"  WARN: seq_lens sum={total_from_lens} != bin_size={total_tokens}")

    if expected_docs > 0 and num_docs != expected_docs:
        log(f"  WARN: doc count .json={expected_docs} vs computed={num_docs}")

    doc_idx = np.arange(num_docs + 1, dtype=np.int64)

    if dry_run:
        log(f"  DRY RUN: {num_docs} docs, {total_tokens} tokens")
        return {"dry_run": True, "num_docs": num_docs, "num_tokens": total_tokens}

    old_idx = idx_path + ".old"
    if os.path.isfile(idx_path):
        os.rename(idx_path, old_idx)

    write_idx(idx_path, seq_lens, seq_ptrs, doc_idx)

    header = read_idx_header(idx_path)
    if header is None or header["seq_count"] != num_docs:
        return {"error": "verification failed: seq_count mismatch"}

    return {"num_docs": num_docs, "num_tokens": total_tokens, "bin_bytes": bin_size,
            "seq_count": header["seq_count"], "doc_count": header["doc_count"]}


def main():
    ap = argparse.ArgumentParser(description="Convert text .idx to MMapIndexedDataset binary .idx")
    ap.add_argument("--src-dir", required=True, help="Source directory with .bin/.idx/.json triplets")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    src_dir = args.src_dir
    if not os.path.isdir(src_dir):
        print(f"FAIL: {src_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    bins = sorted([f for f in os.listdir(src_dir) if f.endswith(".bin")], key=natkey)
    if not bins:
        print(f"FAIL: no .bin files in {src_dir}", file=sys.stderr)
        sys.exit(1)

    log(f"Found {len(bins)} .bin files in {src_dir}")

    if args.verify_only:
        proper = sum(1 for bn in bins if is_proper_idx(os.path.join(src_dir, bn[:-4] + ".idx")))
        log(f"  Proper MMapIndexedDataset: {proper}/{len(bins)}")
        log(f"  Text/other format: {len(bins) - proper}/{len(bins)}")
        return

    total = len(bins)
    converted = skipped = errors = 0
    start_time = time.time()

    for i, bn in enumerate(bins):
        prefix = bn[:-4]
        bin_path = os.path.join(src_dir, prefix + ".bin")
        idx_path = os.path.join(src_dir, prefix + ".idx")
        json_path = os.path.join(src_dir, prefix + ".json")

        if not os.path.isfile(idx_path):
            skipped += 1
            continue

        log(f"  [{i+1}/{total}] {prefix}...")
        try:
            result = convert_shard(bin_path, idx_path, json_path, args.dry_run)
            if result.get("skipped"):
                skipped += 1
            elif result.get("error"):
                errors += 1
                log(f"    ERROR: {result['error']}")
            else:
                converted += 1
                log(f"    OK: {result.get('num_docs', '?')} docs, {result.get('num_tokens', '?')} tokens")
        except Exception as e:
            errors += 1
            log(f"    EXCEPTION: {e}")

        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (total - i - 1) / rate if rate > 0 else 0
            log(f"  Progress: {i+1}/{total} ({rate:.1f}/s, ETA {eta:.0f}s)")

    elapsed = time.time() - start_time
    log(f"\n=== DONE: {total} shards, {converted} converted, {skipped} skipped, {errors} errors, {elapsed:.0f}s ===")
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

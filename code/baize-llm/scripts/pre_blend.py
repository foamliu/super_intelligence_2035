#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-blend: merge many small Megatron tokenized shards into fewer large shards.

Usage::

    python pre_blend.py --src-dir <source_dir> --out-dir <output_dir> \
        --prefix <name> [--target-shards 16] [--verify] [--dry-run]

Reads all .bin/.idx/.json triplets from --src-dir (sorted by natural key),
groups them into --target-shards groups, and writes merged .bin/.idx/.json
to --out-dir.

Rationale: 628 small shards x N DataLoader workers -> fork-COW page table
explosion -> OOM at nw>0 -> forced nw=0 -> data/compute serialization -> 308K
tok/s (50% of 613K baseline).  Pre-blending into ~16 large shards per source
shrinks the mmap index -> COW negligible -> restore nw=8 -> 613K tok/s.

Megatron MMapIndexedDataset .idx format (all integers little-endian):
  offset  size     field
  0       9        magic  = b'MMIDIDX\x00\x00'
  9       8        version (uint64) = 1
  17      1        dtype_code (uint8) = 4 (int32)
  18      8        seq_count (uint64) = num_documents
  26      8        doc_count (uint64) = num_documents + 1
  34      4*N      seq_lens (int32 array, N = seq_count)
  34+4N   8*N      seq_ptrs (int64 array, byte offsets into .bin)
  34+12N  8*(N+1)  doc_idx (int64 array, document boundary seq indices)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import time

MAGIC = b"MMIDIDX\x00\x00"
VERSION = 1
DTYPE_CODE_INT32 = 4
INT32_BYTES = 4
INT64_BYTES = 8
COPY_BUF = 256 * 1024 * 1024  # 256 MB
HEADER_SIZE = 34  # 9+8+1+8+8


def die(msg, code=1):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(code)


def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def natkey(p):
    return [int(t) if t.isdigit() else t
            for t in re.split(r"(\d+)", os.path.basename(p))]


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"


def read_idx(idx_path):
    import numpy as np
    with open(idx_path, "rb") as f:
        magic = f.read(9)
        if magic != MAGIC:
            die(f"{idx_path}: bad magic {magic!r}", 2)
        version = struct.unpack("<Q", f.read(8))[0]
        if version != 1:
            die(f"{idx_path}: unsupported version {version}", 2)
        dtype_code = struct.unpack("<B", f.read(1))[0]
        if dtype_code != DTYPE_CODE_INT32:
            die(f"{idx_path}: unsupported dtype_code {dtype_code}", 2)
        seq_count = struct.unpack("<Q", f.read(8))[0]
        doc_count = struct.unpack("<Q", f.read(8))[0]
        seq_lens = np.frombuffer(f.read(seq_count * INT32_BYTES), dtype=np.int32)
        seq_ptrs = np.frombuffer(f.read(seq_count * INT64_BYTES), dtype=np.int64)
        remaining = f.read()
        expected = doc_count * INT64_BYTES
        if len(remaining) != expected:
            die(f"{idx_path}: truncated doc_idx", 2)
    return {"seq_count": seq_count, "doc_count": doc_count,
            "seq_lens": seq_lens, "seq_ptrs": seq_ptrs}


def group_shards(shard_names, target_count):
    n = len(shard_names)
    if target_count >= n:
        return [[s] for s in shard_names]
    groups = [[] for _ in range(target_count)]
    for i, s in enumerate(shard_names):
        groups[i % target_count].append(s)
    return groups


def merge_group(src_dir, shard_names, out_prefix, verify):
    import numpy as np
    all_seq_lens = []
    all_seq_ptrs = []
    total_seq_count = 0
    total_tokens = 0
    total_bin_bytes = 0
    shard_infos = []

    for sname in shard_names:
        idx_path = os.path.join(src_dir, sname + ".idx")
        bin_path = os.path.join(src_dir, sname + ".bin")
        if not os.path.isfile(idx_path) or not os.path.isfile(bin_path):
            die(f"missing .bin or .idx for {sname}", 2)
        idx = read_idx(idx_path)
        bin_size = os.path.getsize(bin_path)
        expected_bin = int(idx["seq_lens"].sum()) * INT32_BYTES
        if bin_size < expected_bin:
            die(f"{sname}: .bin truncated ({fmt_bytes(bin_size)} < {fmt_bytes(expected_bin)})", 2)
        shard_infos.append({"name": sname, "seq_count": idx["seq_count"],
                            "bin_size": bin_size, "seq_lens": idx["seq_lens"],
                            "seq_ptrs": idx["seq_ptrs"]})
        total_seq_count += idx["seq_count"]
        total_tokens += int(idx["seq_lens"].sum())
        total_bin_bytes += bin_size

    log(f"  Merging {len(shard_names)} shards -> {out_prefix} "
        f"({total_seq_count:,} docs, {total_tokens:,} tokens, {fmt_bytes(total_bin_bytes)})")

    merged_seq_lens = np.empty(total_seq_count, dtype=np.int32)
    merged_seq_ptrs = np.empty(total_seq_count, dtype=np.int64)
    offset_seq = 0
    offset_bytes = 0
    for si in shard_infos:
        n = si["seq_count"]
        merged_seq_lens[offset_seq:offset_seq + n] = si["seq_lens"]
        merged_seq_ptrs[offset_seq:offset_seq + n] = si["seq_ptrs"] + offset_bytes
        offset_seq += n
        offset_bytes += si["bin_size"]

    out_bin = out_prefix + ".bin"
    out_idx = out_prefix + ".idx"
    out_json = out_prefix + ".json"

    written_bytes = 0
    with open(out_bin, "wb") as fout:
        buf = bytearray(COPY_BUF)
        for si in shard_infos:
            src_bin = os.path.join(src_dir, si["name"] + ".bin")
            with open(src_bin, "rb") as fin:
                while True:
                    n = fin.readinto(buf)
                    if n == 0:
                        break
                    fout.write(buf[:n])
                    written_bytes += n
            log(f"    copied {si['name']}.bin ({fmt_bytes(si['bin_size'])}, cum {fmt_bytes(written_bytes)})")

    if written_bytes != total_bin_bytes:
        die(f"bin write mismatch: {written_bytes} != {total_bin_bytes}")

    doc_count = total_seq_count + 1
    with open(out_idx, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<Q", VERSION))
        f.write(struct.pack("<B", DTYPE_CODE_INT32))
        f.write(struct.pack("<Q", total_seq_count))
        f.write(struct.pack("<Q", doc_count))
        f.write(merged_seq_lens.tobytes())
        f.write(merged_seq_ptrs.tobytes())
        doc_idx = np.arange(doc_count, dtype=np.int64)
        f.write(doc_idx.tobytes())

    idx_size = os.path.getsize(out_idx)
    expected_idx = HEADER_SIZE + total_seq_count * (INT32_BYTES + INT64_BYTES) + doc_count * INT64_BYTES
    if idx_size != expected_idx:
        die(f"idx size mismatch: {idx_size} != {expected_idx}")

    first_json = os.path.join(src_dir, shard_names[0] + ".json")
    meta = {}
    if os.path.isfile(first_json):
        with open(first_json) as f:
            meta = json.load(f)
    meta["num_documents"] = total_seq_count
    meta["num_tokens"] = total_tokens
    meta["dtype"] = "int32"
    meta["source_shards"] = shard_names
    meta["pre_blend"] = True
    with open(out_json, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    if verify:
        log(f"  verifying {out_prefix}...")
        actual_bin = os.path.getsize(out_bin)
        if actual_bin != total_bin_bytes:
            die(f"verify: .bin size mismatch")
        idx_check = read_idx(out_idx)
        if idx_check["seq_count"] != total_seq_count:
            die(f"verify: seq_count mismatch")
        if int(idx_check["seq_lens"].sum()) != total_tokens:
            die(f"verify: token count mismatch")
        max_ptr = int(idx_check["seq_ptrs"][-1]) + int(idx_check["seq_lens"][-1]) * INT32_BYTES
        if max_ptr > actual_bin:
            die(f"verify: ptr overflow {max_ptr} > {actual_bin}")
        log(f"  verify PASS: {total_seq_count:,} docs, {total_tokens:,} tokens")

    return {"shards_merged": len(shard_names), "seq_count": total_seq_count,
            "num_tokens": total_tokens, "bin_bytes": total_bin_bytes}


def main():
    ap = argparse.ArgumentParser(
        description="Pre-blend Megatron tokenized shards into fewer large shards")
    ap.add_argument("--src-dir", required=True, help="source dir with .bin/.idx/.json")
    ap.add_argument("--out-dir", required=True, help="output dir for merged shards")
    ap.add_argument("--prefix", required=True, help="output shard name prefix")
    ap.add_argument("--target-shards", type=int, default=16, help="target output shards")
    ap.add_argument("--verify", action="store_true", help="verify each output shard")
    ap.add_argument("--dry-run", action="store_true", help="show plan only")
    ap.add_argument("--exclude", default="", help="comma-separated shard names to skip")
    ap.add_argument("--output-start", type=int, default=0,
                    help="start output shard index (for parallel split across machines)")
    ap.add_argument("--output-end", type=int, default=-1,
                    help="end output shard index (exclusive); -1 = all remaining")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip output shards that already have .bin+.idx+.json")
    args = ap.parse_args()

    import numpy as np

    src_dir = os.path.abspath(args.src_dir)
    out_dir = os.path.abspath(args.out_dir)
    if not os.path.isdir(src_dir):
        die(f"src-dir not found: {src_dir}", 2)

    all_bins = sorted(
        [f[:-4] for f in os.listdir(src_dir) if f.endswith(".bin")], key=natkey)
    exclude_set = set()
    if args.exclude:
        exclude_set = {e.strip() for e in args.exclude.split(",") if e.strip()}
    shards = [s for s in all_bins if s not in exclude_set]
    excluded = [s for s in all_bins if s in exclude_set]
    if excluded:
        log(f"Excluded {len(excluded)} shards: {', '.join(excluded)}")
    if not shards:
        die(f"no .bin shards in {src_dir}", 2)
    for s in shards:
        if not os.path.isfile(os.path.join(src_dir, s + ".idx")):
            die(f"missing .idx for {s}", 2)

    log(f"Source: {src_dir}")
    log(f"Found {len(shards)} shards, target = {args.target_shards} output shards")

    groups = group_shards(shards, args.target_shards)
    output_end = args.output_end if args.output_end >= 0 else len(groups)
    total_bytes_all = 0
    for i, g in enumerate(groups):
        g_bytes = sum(os.path.getsize(os.path.join(src_dir, s + ".bin")) for s in g)
        total_bytes_all += g_bytes
        marker = ""
        if i < args.output_start or i >= output_end:
            marker = " (OUT OF RANGE)"
        log(f"  shard {i:03d}: {len(g)} input -> {fmt_bytes(g_bytes)}{marker}")
    selected = [(i, g) for i, g in enumerate(groups) if args.output_start <= i < output_end]
    log(f"Total: {len(shards)} input -> {len(groups)} output, {fmt_bytes(total_bytes_all)}")
    log(f"Selected range: [{args.output_start}, {output_end}) = {len(selected)} output shards")

    if args.dry_run:
        log("DRY RUN - not writing.")
        return

    os.makedirs(out_dir, exist_ok=True)
    stat = os.statvfs(out_dir)
    avail = stat.f_bavail * stat.f_frsize
    log(f"Output free space: {fmt_bytes(avail)}")
    if avail < total_bytes_all * 1.1:
        die(f"insufficient space: need ~{fmt_bytes(total_bytes_all)}, have {fmt_bytes(avail)}")

    results = {}
    start_time = time.time()
    for i, group in selected:
        out_prefix = os.path.join(out_dir, f"{args.prefix}_s{i:03d}")
        out_bin_check = out_prefix + ".bin"
        out_idx_check = out_prefix + ".idx"
        out_json_check = out_prefix + ".json"
        if args.skip_existing and os.path.isfile(out_bin_check) and \
           os.path.isfile(out_idx_check) and os.path.isfile(out_json_check):
            log(f"=== Output shard {i:03d}/{len(groups)-1} — SKIP (already exists) ===")
            idx_existing = read_idx(out_idx_check)
            r = {"shards_merged": len(group), "seq_count": idx_existing["seq_count"],
                 "num_tokens": int(idx_existing["seq_lens"].sum()),
                 "bin_bytes": os.path.getsize(out_bin_check)}
            results[i] = r
            continue
        log(f"=== Output shard {i:03d}/{len(groups)-1} ===")
        r = merge_group(src_dir, group, out_prefix, args.verify)
        results[i] = r
        elapsed = time.time() - start_time
        done_bytes = sum(r["bin_bytes"] for r in results.values())
        rate = done_bytes / elapsed if elapsed > 0 else 0
        pct = done_bytes / total_bytes_all * 100 if total_bytes_all else 100
        log(f"  Progress: {pct:.1f}% ({fmt_bytes(done_bytes)}/{fmt_bytes(total_bytes_all)}) "
            f"at {fmt_bytes(rate)}/s, elapsed {elapsed:.0f}s")

    elapsed = time.time() - start_time
    total_tokens = sum(r["num_tokens"] for r in results.values())
    total_bytes = sum(r["bin_bytes"] for r in results.values())
    log(f"\n=== DONE (range [{args.output_start}, {output_end})) ===")
    log(f"  {len(results)} output shards processed")
    log(f"  {total_tokens:,} tokens, {fmt_bytes(total_bytes)}")
    if elapsed > 0:
        log(f"  Elapsed: {elapsed:.0f}s ({fmt_bytes(total_bytes/elapsed)}/s)")

    # Only write MANIFEST if all target shards are covered
    if len(results) == len(groups):
        manifest = {"source_dir": src_dir, "prefix": args.prefix,
                    "input_shards": len(shards), "output_shards": len(results),
                    "total_tokens": total_tokens, "total_bytes": total_bytes,
                    "target_shards": args.target_shards,
                    "shards": [{"name": f"{args.prefix}_s{i:03d}", **results[i]}
                               for i in sorted(results)]}
        with open(os.path.join(out_dir, "MANIFEST.json"), "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        log(f"  Manifest: {os.path.join(out_dir, 'MANIFEST.json')}")
    else:
        log(f"  Partial run ({len(results)}/{len(groups)} shards) — MANIFEST not written (run all shards to generate)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""validate_data.py — 数据完整性校验（phase1 validate，可复现脚本）。

设计原则：默认**轻 I/O**（只读 parquet footer / tar 成员名 / jsonl 前若干行 / 目录元数据），
避免在 HF 下载与 GPU 训练仍在进行时全量扫盘抢带宽（任务书 §5「下载期间不要做重 I/O / 全量扫描」）。
需要全量校验时显式传 --deep。

子命令（--mode）：
  parquet  <glob|dir>  逐个 parquet 用 pyarrow.ParquetFile 打开（只读 footer：行组数/行数/schema）
                       判损坏/截断（缺 footer 或读不到元数据）。--deep 时额外读第一行组抽样校验。
  tar      <glob|dir>  逐个 tar 判 is_tarfile + 迭代成员名（不解压），判截断/损坏；--deep 时逐成员读 1 字节。
  jsonl    <glob|dir>  逐行 json.loads；默认每文件只校验前 --max-lines 行 + 末行（2GB/shard 场景轻量），
                       --deep 时全量。用于 SFT 语料（UltraData-SFT-Agent-2609 等 jsonl）同格式校验。
  shards   <glob>      校验 shard-XXXXX.tar 编号连续无缺号（0..N-1）。
  census   <dir>       轻量格式普查：各扩展名文件数 + 总字节（find + du，不读文件内容）。
                       用于确认「疑似 jsonl/parquet」类数据线的真实落盘格式。

用法：
  python validate_data.py --mode parquet --input '/path/qa/*.snappy.parquet'
  python validate_data.py --mode tar     --input '/path/en500k/shard-*.tar'
  python validate_data.py --mode jsonl   --input '/path/SFT/*.jsonl' --max-lines 2000
  python validate_data.py --mode shards  --input '/path/en500k/shard-*.tar'
  python validate_data.py --mode census  --input /path/SFT-dir
  python validate_data.py --mode parquet --input '/path/*.parquet' --deep
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path


def _files(inp: str) -> list:
    """把 --input（glob 或目录）归一化成文件列表；目录时按扩展名递归收集。"""
    if os.path.isdir(inp):
        return sorted(
            f for f in glob.glob(os.path.join(inp, "**", "*"), recursive=True)
            if os.path.isfile(f)
        )
    return sorted(glob.glob(inp))


def _human(n: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024.0
    return f"{n}B"


def check_parquet(files, deep, max_lines):
    ok = bad = 0
    for f in files:
        try:
            import pyarrow.parquet as pq
            pf = pq.ParquetFile(f)
            meta = pf.metadata
            n_rg = meta.num_row_groups
            n_rows = meta.num_rows
            if deep and n_rows:
                tbl = pf.read_row_group(0)
                n = min(max_lines or 16, tbl.num_rows)
                _ = tbl.slice(0, n).to_pydict()
            print(f"[OK]   parquet {f}  rows={n_rows}  row_groups={n_rg}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] parquet {f}  -> {type(e).__name__}: {e}")
            bad += 1
    return ok, bad


def check_tar(files, deep):
    import tarfile
    ok = bad = 0
    for f in files:
        try:
            if not tarfile.is_tarfile(f):
                raise ValueError("not a tarfile (truncated / corrupt header)")
            with tarfile.open(f, "r:") as t:
                members = t.getmembers()
                if deep:
                    for m in members:
                        if m.isfile():
                            fp = t.extractfile(m)
                            if fp is not None:
                                fp.read(1)
            print(f"[OK]   tar {f}  members={len(members)}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] tar {f}  -> {type(e).__name__}: {e}")
            bad += 1
    return ok, bad


def check_jsonl(files, deep, max_lines):
    ok = bad = 0
    for f in files:
        try:
            n = 0
            with open(f, "r", encoding="utf-8") as fh:
                it = iter(fh)
                limit = max_lines or 1000
                for line in it:
                    if not line.strip():
                        continue
                    if not deep and n >= limit:
                        break
                    json.loads(line)
                    n += 1
                # 默认校验末行，确保文件尾部完整（截断检测）
                if not deep:
                    last = None
                    for line in it:
                        last = line
                    if last is not None and last.strip():
                        json.loads(last)
            print(f"[OK]   jsonl {f}  lines={n}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] jsonl {f}  -> {type(e).__name__}: {e}")
            bad += 1
    return ok, bad


def check_shards(files):
    nums = []
    unmatched = []
    for f in files:
        m = re.search(r"shard-(\d+)\.tar", os.path.basename(f))
        if m:
            nums.append(int(m.group(1)))
        else:
            unmatched.append(f)
    if not nums:
        print(f"[FAIL] shards 未匹配到 shard-XXXXX.tar 命名（{len(files)} 文件）")
        return 0, len(files), []
    nums = sorted(set(nums))
    missing = [i for i in range(min(nums), max(nums) + 1) if i not in nums]
    if missing:
        print(f"[FAIL] shards 缺号 {len(missing)} 个："
              f"{missing[:20]}{'...' if len(missing) > 20 else ''}")
    else:
        print(f"[OK]   shards {min(nums)}..{max(nums)} 连续无缺号（{len(nums)} 个）")
    if unmatched:
        print(f"[WARN] {len(unmatched)} 个文件不匹配 shard 命名：{unmatched[:5]}")
    return len(nums), len(missing), missing


def census(d):
    ext_count = {}
    total_bytes = 0
    total_files = 0
    for root, _dirs, fs in os.walk(d):
        for fn in fs:
            p = os.path.join(root, fn)
            try:
                total_bytes += os.path.getsize(p)
            except OSError:
                pass
            total_files += 1
            ext = os.path.splitext(fn)[1].lower() or "(noext)"
            ext_count[ext] = ext_count.get(ext, 0) + 1
    print(f"[census] {d}")
    print(f"  文件总数 {total_files} / 总字节 {_human(total_bytes)}")
    for ext in sorted(ext_count, key=lambda e: ext_count[e], reverse=True):
        print(f"  {ext:10s} {ext_count[ext]}")
    return total_files, total_bytes


def main():
    ap = argparse.ArgumentParser(description="phase1 数据完整性校验（默认轻 I/O）")
    ap.add_argument("--mode", required=True,
                    choices=["parquet", "tar", "jsonl", "shards", "census"])
    ap.add_argument("--input", required=True, help="glob 或目录")
    ap.add_argument("--deep", action="store_true", help="全量校验（默认关闭，只做轻 I/O）")
    ap.add_argument("--max-lines", type=int, default=None,
                    help="jsonl 轻量模式下每文件校验前 N 行（默认 1000）")
    args = ap.parse_args()

    if args.mode == "census":
        total, size = census(args.input)
        print(f"[done] census {total} 文件 / {_human(size)}")
        return 0

    files = _files(args.input)
    if not files:
        print(f"[FAIL] --input 未匹配到任何文件：{args.input}")
        return 2

    bad = 0
    if args.mode == "parquet":
        _, bad = check_parquet(files, args.deep, args.max_lines)
    elif args.mode == "tar":
        _, bad = check_tar(files, args.deep)
    elif args.mode == "jsonl":
        _, bad = check_jsonl(files, args.deep, args.max_lines)
    elif args.mode == "shards":
        _, missing, _ = check_shards(files)
        bad = missing

    print(f"[done] {args.mode}：{len(files)} 文件，损坏/缺失 {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
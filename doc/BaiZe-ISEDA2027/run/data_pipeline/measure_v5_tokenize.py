#!/usr/bin/env python3
"""measure_v5_tokenize.py — 抽样测 en_v1_4 分词吞吐（单进程），口径与 preprocess_data.py 一致。

用途（2026-10-18② 令）：对 en_v1_4（CC-MAIN 110 快照，56,461 parquet / 6.75TB）已下部分
抽 2–3 个 shard，单进程测：
  - tokens/s（tok/s）：DeepSeek BPE 真实分词吞吐（含逐文档 tokenize + 结尾 EOD，与
    mamba2_hybrid_2b/preprocess_data.py 的 _tokenize_document 同口径）；
  - bytes→tokens 比例：raw 文本字节 → tokens（每字节多少 token），以及
    parquet 落盘字节（snappy 压缩）→ tokens（每字节多少 token，用于把 6.75TB 换算成总 token）。

依赖：py310 env（transformers + pyarrow + megatron-core + torch）。
用法：
  python measure_v5_tokenize.py --shard-dirs <dir1> <dir2> ... [--files-per-shard N] \
      [--max-docs-per-file M] [--rows-per-batch 1024] [--tokenizer PATH]
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b")
from preprocess_data import _add_eod_token, _tokenize_document  # noqa: E402

import pyarrow.parquet as pq  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

DEFAULT_TOKENIZER = "/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash"


def measure_parquet_file(pf: Path, tokenizer, eod_id: int,
                         max_docs: int | None, batch_size: int) -> dict:
    """单文件吞吐测量，逐 batch 读 content 列，逐文档 tokenize（含 EOD）。"""
    parrot = pq.ParquetFile(str(pf))
    n_docs = 0
    n_tokens = 0
    n_raw_bytes = 0
    t0 = time.time()
    for batch in parrot.iter_batches(batch_size=batch_size):
        texts = batch.column("content").to_pylist()
        for text in texts:
            if max_docs is not None and n_docs >= max_docs:
                break
            ids = _tokenize_document(text, tokenizer, eod_id)
            n_docs += 1
            n_tokens += len(ids)
            n_raw_bytes += len(text.encode("utf-8"))
        if max_docs is not None and n_docs >= max_docs:
            break
    elapsed = time.time() - t0
    return {
        "file": str(pf),
        "file_bytes": os.path.getsize(pf),
        "n_docs": n_docs,
        "n_tokens": n_tokens,
        "n_raw_bytes": n_raw_bytes,
        "elapsed_s": elapsed,
        "tok_per_s": n_tokens / elapsed if elapsed > 0 else 0.0,
        "tokens_per_raw_byte": n_tokens / n_raw_bytes if n_raw_bytes > 0 else 0.0,
        "tokens_per_file_byte": n_tokens / os.path.getsize(pf) if os.path.getsize(pf) > 0 else 0.0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-dirs", nargs="+", required=True,
                    help="en_v1_4 的 CC-MAIN-* 目录（每目录 512 个 *.parquet）")
    ap.add_argument("--files-per-shard", type=int, default=2)
    ap.add_argument("--max-docs-per-file", type=int, default=None,
                    help="每文件只处理前 N 文档（冒烟用）；默认全文件")
    ap.add_argument("--rows-per-batch", type=int, default=1024)
    ap.add_argument("--tokenizer", default=DEFAULT_TOKENIZER)
    ap.add_argument("--eod-token", default="<|endoftext|>")
    args = ap.parse_args()

    print("[tokenizer] 加载 ...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    src_vocab = len(tokenizer)
    eod_id = _add_eod_token(tokenizer, args.eod_token)
    print(f"[tokenizer] 源词表 {src_vocab} -> 追加 EOD 后 {len(tokenizer)} (eod_id={eod_id})", flush=True)

    agg = {"n_docs": 0, "n_tokens": 0, "n_raw_bytes": 0, "file_bytes": 0, "elapsed_s": 0.0}
    t_all = time.time()
    for d in args.shard_dirs:
        shard = Path(d)
        files = sorted(shard.glob("*.parquet"))[: args.files_per_shard]
        print(f"\n[shard] {shard.name}  ({len(files)} 文件)", flush=True)
        for pf in files:
            r = measure_parquet_file(pf, tokenizer, eod_id,
                                     args.max_docs_per_file, args.rows_per_batch)
            for k in ("n_docs", "n_tokens", "n_raw_bytes", "file_bytes", "elapsed_s"):
                agg[k] += r[k]
            print(f"  {Path(pf).name}: {r['n_docs']} docs / {r['n_tokens']:,} tok / "
                  f"{r['n_raw_bytes']:,} rawB / {r['file_bytes']:,} parquetB / "
                  f"{r['elapsed_s']:.1f}s → {r['tok_per_s']:,.0f} tok/s, "
                  f"{r['tokens_per_raw_byte']:.4f} tok/rawB, "
                  f"{r['tokens_per_file_byte']:.4f} tok/parquetB", flush=True)

    wall = time.time() - t_all
    print("\n===== AGGREGATE =====", flush=True)
    print(f"shards={len(args.shard_dirs)} files_per_shard={args.files_per_shard}", flush=True)
    print(f"docs={agg['n_docs']:,}  tokens={agg['n_tokens']:,}  raw_bytes={agg['n_raw_bytes']:,}  "
          f"parquet_bytes={agg['file_bytes']:,}", flush=True)
    print(f"wall={wall:.1f}s  process_elapsed={agg['elapsed_s']:.1f}s", flush=True)
    print(f"tok/s (进程内) = {agg['n_tokens']/agg['elapsed_s'] if agg['elapsed_s']>0 else 0:,.0f}", flush=True)
    print(f"tokens/raw_byte   = {agg['n_tokens']/agg['n_raw_bytes'] if agg['n_raw_bytes']>0 else 0:.5f}", flush=True)
    print(f"tokens/parquet_byte = {agg['n_tokens']/agg['file_bytes'] if agg['file_bytes']>0 else 0:.5f}", flush=True)


if __name__ == "__main__":
    main()
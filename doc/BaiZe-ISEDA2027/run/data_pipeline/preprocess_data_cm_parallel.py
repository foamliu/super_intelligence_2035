#!/usr/bin/env python3
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
#
# preprocess_data_cm_parallel.py — Parallel version of preprocess_data_cm.py
#
# Uses multiprocessing.Pool for parallel tokenization WITHIN a single shard.
# Each worker loads its own tokenizer copy; the main process reads parquet
# files and writes .bin/.idx in order.  Output format is identical to the
# serial version (.bin/.idx/.json).
#
# Key parameters:
#   --num-workers N  : spawn N tokenizer worker processes (default 1 = serial)
#   --batch-size  B  : documents per Pool task (default 256)
#
# Safety: max_chars (default 50000) is the primary BPE death-loop guard.
# With max_chars set, per-document timeout is unnecessary (the 2026-10-22
# root-cause fix established that max_chars prevents the Rust fast-tokenizer
# infinite loop on pathological CC-MAIN pages).

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import time
from collections import deque
from pathlib import Path
from typing import Iterator, List, Optional

import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoTokenizer

from megatron.core.datasets.indexed_dataset import IndexedDatasetBuilder

_VOCAB_DIVISIBLE_BY = 128

# ── worker globals (set by pool initializer) ────────────────────────
_w_tok = None
_w_eod = 0
_w_mc = None
_w_col = "content"


def _w_init(tokenizer_path, eod_token, max_chars, text_column):
    """Pool initializer: load tokenizer once per worker process."""
    global _w_tok, _w_eod, _w_mc, _w_col
    _w_tok = AutoTokenizer.from_pretrained(tokenizer_path)
    _w_tok.add_special_tokens({"eos_token": eod_token})
    _w_eod = _w_tok.eos_token_id
    _w_mc = max_chars
    _w_col = text_column


def _w_tokenize_batch(texts):
    """Tokenize a batch of texts. Returns list of token-id lists (each + EOD)."""
    out = []
    for text in texts:
        if text is None:
            text = ""
        if _w_mc is not None and len(text) > _w_mc:
            text = text[:_w_mc]
        try:
            ids = _w_tok(text, add_special_tokens=False, truncation=False)["input_ids"]
            out.append(ids + [_w_eod])
        except Exception:
            out.append([_w_eod])
    return out


def iter_parquet_batches(input_dir, text_column, batch_size, max_docs=None):
    """Yield batches of text documents from parquet files in input_dir."""
    pfs = sorted(Path(input_dir).glob("*.snappy.parquet"))
    if not pfs:
        pfs = sorted(Path(input_dir).glob("*.parquet"))
    if not pfs:
        raise FileNotFoundError(f"No parquet files in {input_dir}")
    batch = []
    total = 0
    n_files = len(pfs)
    for i, pf in enumerate(pfs):
        pqf = pq.ParquetFile(str(pf))
        for rb in pqf.iter_batches(batch_size=1024):
            texts = rb.column(text_column).to_pylist()
            for t in texts:
                batch.append(t)
                total += 1
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                if max_docs is not None and total >= max_docs:
                    if batch:
                        yield batch
                    return
        if (i + 1) % 50 == 0:
            print(f"[data] {i+1}/{n_files} parquet files read, {total} docs",
                  flush=True)
    if batch:
        yield batch
    print(f"[data] done: {n_files} files, {total} docs", flush=True)


def _turns_to_text(turns):
    segs = []
    for t in turns:
        if isinstance(t, dict):
            u = (t.get("user") or "").strip()
            a = (t.get("assistant") or "").strip()
            if u:
                segs.append(u)
            if a:
                segs.append(a)
        else:
            segs.append(str(t or "").strip())
    return "\n\n".join(s for s in segs if s)


def iter_parquet_turns_batches(input_dir, batch_size, max_docs=None):
    pfs = sorted(Path(input_dir).glob("*.parquet"))
    if not pfs:
        raise FileNotFoundError(f"No parquet files in {input_dir}")
    batch = []
    total = 0
    for pf in pfs:
        pqf = pq.ParquetFile(str(pf))
        for rb in pqf.iter_batches(batch_size=1024):
            for turns in rb.column("texts").to_pylist():
                batch.append(_turns_to_text(turns))
                total += 1
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                if max_docs is not None and total >= max_docs:
                    if batch:
                        yield batch
                    return
    if batch:
        yield batch

def main():
    parser = argparse.ArgumentParser(
        description="Parallel tokenization: parquet -> .bin/.idx (multiprocessing.Pool)"
    )
    parser.add_argument("--input-dir", required=True, help="parquet directory")
    parser.add_argument("--output-prefix", required=True, help="output .bin/.idx prefix")
    parser.add_argument("--tokenizer", required=True, help="source tokenizer directory")
    parser.add_argument("--tokenizer-output-dir", default=None)
    parser.add_argument("--max-docs", type=int, default=None)
    parser.add_argument("--text-column", default="content")
    parser.add_argument("--mode", default="content", choices=["content", "turns"])
    parser.add_argument("--dtype", default="int32", choices=["int16", "int32", "int64"])
    parser.add_argument("--eod-token", default="<|endoftext|>", help="EOD special token to append")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="truncate each doc to N chars (prevents BPE death-loop)")
    parser.add_argument("--num-workers", type=int, default=1,
                        help="parallel tokenizer worker processes (default 1)")
    parser.add_argument("--batch-size", type=int, default=256,
                        help="documents per Pool task (default 256)")
    args = parser.parse_args()

    t0 = time.time()

    # 1) Load tokenizer in main process (for metadata + save copy)
    print("[tokenizer] loading ...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    src_vocab = len(tokenizer)
    tokenizer.add_special_tokens({"eos_token": args.eod_token})
    eod_id = tokenizer.eos_token_id
    vocab_size = len(tokenizer)
    padded_vocab = ((vocab_size + _VOCAB_DIVISIBLE_BY - 1) //
                    _VOCAB_DIVISIBLE_BY) * _VOCAB_DIVISIBLE_BY
    toks_out = (args.tokenizer_output_dir or
                os.path.join(os.path.dirname(args.output_prefix), "tokenizer_eod"))
    tokenizer.save_pretrained(toks_out)
    print(f"[tokenizer] {src_vocab} -> {vocab_size}, padded={padded_vocab}, "
          f"eod_id={eod_id}", flush=True)

    # 2) Create parquet batch iterator
    if args.mode == "turns":
        batches = iter_parquet_turns_batches(args.input_dir, args.batch_size, args.max_docs)
    else:
        batches = iter_parquet_batches(args.input_dir, args.text_column,
                                       args.batch_size, args.max_docs)

    # 3) Tokenize -> .bin/.idx
    dtype = getattr(np, args.dtype)
    builder = IndexedDatasetBuilder(bin_path=f"{args.output_prefix}.bin", dtype=dtype)
    n_docs = 0
    n_tokens = 0
    n_truncated = 0

    if args.num_workers <= 1:
        # serial fallback
        print(f"[tokenize] serial mode (num_workers=1), max_chars={args.max_chars}", flush=True)
        for batch in batches:
            for text in batch:
                if text is None:
                    text = ""
                raw_len = len(text)
                if args.max_chars is not None and raw_len > args.max_chars:
                    text = text[:args.max_chars]
                    n_truncated += 1
                ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
                ids = ids + [eod_id]
                builder.add_item(torch.tensor(ids, dtype=torch.long))
                builder.end_document()
                n_docs += 1
                n_tokens += len(ids)
                if n_docs % 50000 == 0:
                    print(f"[tokenize] {n_docs} docs / {n_tokens} tokens ({time.time() - t0:.1f}s)", flush=True)
    else:
        # parallel mode: Pool with bounded in-flight tasks
        nw = args.num_workers
        print(f"[tokenize] parallel: {nw} workers, batch={args.batch_size}, "
              f"max_chars={args.max_chars}", flush=True)
        ctx = mp.get_context("fork")
        pool = ctx.Pool(nw, initializer=_w_init,
                        initargs=(args.tokenizer, args.eod_token, args.max_chars, args.text_column))
        max_outstanding = nw * 2
        pending = deque()
        try:
            for batch in batches:
                while len(pending) >= max_outstanding:
                    ar = pending.popleft()
                    batch_tokens = ar.get()
                    for ids in batch_tokens:
                        builder.add_item(torch.tensor(ids, dtype=torch.long))
                        builder.end_document()
                        n_docs += 1
                        n_tokens += len(ids)
                    if n_docs % 50000 == 0:
                        print(f"[tokenize] {n_docs} docs / {n_tokens} tokens ({time.time() - t0:.1f}s)", flush=True)
                ar = pool.apply_async(_w_tokenize_batch, (batch,))
                pending.append(ar)
            while pending:
                ar = pending.popleft()
                batch_tokens = ar.get()
                for ids in batch_tokens:
                    builder.add_item(torch.tensor(ids, dtype=torch.long))
                    builder.end_document()
                    n_docs += 1
                    n_tokens += len(ids)
                if n_docs % 50000 == 0:
                    print(f"[tokenize] {n_docs} docs / {n_tokens} tokens ({time.time() - t0:.1f}s)", flush=True)
        finally:
            pool.close()
            pool.join()
        print(f"[tokenize] all workers done: {n_docs} docs / {n_tokens} tokens ({time.time() - t0:.1f}s)", flush=True)

    builder.finalize(idx_path=f"{args.output_prefix}.idx")

    # 4) Write metadata JSON
    meta = {
        "source_tokenizer": args.tokenizer,
        "tokenizer_output_dir": toks_out,
        "eod_token": args.eod_token,
        "eod_id": eod_id,
        "vocab_size": vocab_size,
        "padded_vocab_size": padded_vocab,
        "num_documents": n_docs,
        "num_tokens": n_tokens,
        "num_truncated_docs": n_truncated,
        "num_timeout_skips": 0,
        "num_errors": 0,
        "max_chars": args.max_chars,
        "doc_timeout": 0,
        "num_workers": args.num_workers,
        "dtype": args.dtype,
        "input_dir": args.input_dir,
    }
    with open(f"{args.output_prefix}.json", "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    elapsed = time.time() - t0
    print(f"[done] {n_docs} docs / {n_tokens} tokens in {elapsed:.1f}s "
          f"({n_tokens / elapsed:.0f} tok/s); output: {args.output_prefix}.bin/.idx/.json", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
#
# BaiZe ~2B Mamba2-hybrid 预训练数据预处理：把 Ultra-FineWeb-L3 (snappy.parquet) 用
# DeepSeek-V4.1-Flash tokenizer 切词，产出 NVIDIA GPT dataset 的 .bin/.idx（MMap 索引）
# 供 `megatron.bridge.training.pretrain.pretrain(pretrain_config(...))` 直接读取。
#
# 为什么不直接用 swift 流式 tokenize：
#   swift `megatron pt` 走 swift 自己的 dataset/tokenizer 栈（MiniCPM5 模板），与
#   NVIDIA/NeMo recipe 路径（路径 A）的数据格式（blend JSON -> .bin/.idx）不通用。
#   所以这里单独落地一个脚本，把原始 parquet -> .bin/.idx，并配齐 tokenizer 元数据。
#
# 依赖：transformers (AutoTokenizer) + megatron-core (core.datasets.indexed_dataset) + torch。
# 运行示例（小样本冒烟）：
#   python preprocess_data.py \
#       --input-dir .../Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa \
#       --output-prefix /path/to/ultrafineweb_l3_qa_text_document \
#       --tokenizer /nas_train/app.e0031982/models/DeepSeek-V4.1-Flash \
#       --tokenizer-output-dir /path/to/tokenizer_eod \
#       --max-docs 2000
# 完整数据（1.8T / 约 31 个 part 文件）需在充足磁盘与算力的节点上跑，见 FEASIBILITY.md。

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import queue as _queue
import time
from pathlib import Path
from typing import Iterator, List, Optional

import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoTokenizer

from megatron.core.datasets.indexed_dataset import IndexedDatasetBuilder

# 由 8B hybrid 沿用：make_vocab_size_divisible_by
_VOCAB_DIVISIBLE_BY = 128


def _add_eod_token(tokenizer, eod_token: str = "<|endoftext|>"):
    """给 DeepSeek BPE tokenizer 挂一个真实的 EOD token，并返回其 id。

    原 DeepSeek 词表 129280 个 token；追加该特殊 token 后 vocab=129281，
    eos_id=129280（训练时 HuggingFaceTokenizer.eod 取 eos_token_id）。
    """
    tokenizer.add_special_tokens({"eos_token": eod_token})
    assert tokenizer.eos_token_id == len(tokenizer) - 1, (
        f"EOD token {eod_token!r} 未追加到词表末尾 (eos_id={tokenizer.eos_token_id})"
    )
    return tokenizer.eos_token_id


def _tokenize_document(
    text: str, tokenizer, eod_id: int, add_special_tokens: bool = False,
    max_chars: Optional[int] = None
) -> List[int]:
    """单条文档 -> token id 序列，末尾附 EOD token。

    若 max_chars 不为 None，则先将 text 截断到 max_chars 个字符再分词。
    这是为了防止 CC-MAIN 等原始网页爬取数据中极少数超长/病态文档
    导致 BPE 分词器陷入 CPU 死循环（2026-10-22 实测 13 个 en_v1_4
    worker 100% CPU 0 I/O 空转 8h+ 的根因）。
    """
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars]
    ids = tokenizer(text, add_special_tokens=add_special_tokens, truncation=False)["input_ids"]
    return ids + [eod_id]


# ── 子进程 tokenization worker（用于硬超时保护） ──────────────────────────
def _worker_tokenize(input_q: mp.Queue, output_q: mp.Queue,
                     tokenizer_path: str, eod_token: str,
                     max_chars: Optional[int]):
    """持久子进程：加载 tokenizer，循环从 input_q 取文本，分词后放 output_q。

    收到 None 时退出。若分词抛异常，放 ("error", msg)。
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        tokenizer.add_special_tokens({"eos_token": eod_token})
        eod_id = tokenizer.eos_token_id
    except Exception as e:
        output_q.put(("fatal", f"tokenizer load failed: {e}"))
        return
    while True:
        try:
            text = input_q.get()
        except Exception:
            break
        if text is None:
            break
        try:
            if max_chars is not None and len(text) > max_chars:
                text = text[:max_chars]
            ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"]
            output_q.put(("ok", ids + [eod_id]))
        except Exception as e:
            output_q.put(("error", str(e)))


class TokenizerWorker:
    """封装子进程 tokenizer，提供带超时的 tokenize 方法。

    若文档分词超过 doc_timeout 秒，杀掉子进程并重启，返回 None（跳过该文档）。
    这是应对 Rust-based fast tokenizer 在某些 CC-MAIN 网页上陷入死循环
    的终极手段——signal.alarm 无法中断 Rust 代码，只能用进程级 kill。
    """

    def __init__(self, tokenizer_path: str, eod_token: str,
                 max_chars: Optional[int], doc_timeout: int = 120):
        self.tokenizer_path = tokenizer_path
        self.eod_token = eod_token
        self.max_chars = max_chars
        self.doc_timeout = doc_timeout
        self._start_worker()

    def _start_worker(self):
        self.input_q = mp.Queue(maxsize=1)
        self.output_q = mp.Queue(maxsize=1)
        self.process = mp.Process(
            target=_worker_tokenize,
            args=(self.input_q, self.output_q,
                  self.tokenizer_path, self.eod_token, self.max_chars),
        )
        self.process.daemon = True
        self.process.start()

    def tokenize(self, text: str) -> Optional[List[int]]:
        """提交文本并等待分词结果，超时则杀进程返回 None。"""
        if not self.process.is_alive():
            self._start_worker()
        try:
            self.input_q.put(text, timeout=5)
        except _queue.Full:
            # Worker stuck from previous doc — restart
            self._restart()
            return None
        try:
            status, payload = self.output_q.get(timeout=self.doc_timeout)
            if status == "ok":
                return payload
            elif status == "fatal":
                raise RuntimeError(f"worker fatal: {payload}")
            else:
                print(f"[WARN] tokenization error: {payload}", flush=True)
                return None
        except _queue.Empty:
            print(f"[WARN] tokenization timeout after {self.doc_timeout}s "
                  f"(doc ~{len(text)} chars), killing worker", flush=True)
            self._restart()
            return None

    def _restart(self):
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=5)
        self._start_worker()

    def close(self):
        try:
            self.input_q.put(None, timeout=2)
        except Exception:
            pass
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=5)


def iter_parquet_texts(input_dir: str, max_docs: Optional[int] = None,
                       text_column: str = "content") -> Iterator[str]:
    """流式遍历 parquet 目录下所有 *.snappy.parquet 或 *.parquet 的指定文本列。"""
    parquet_files = sorted(Path(input_dir).glob("*.snappy.parquet"))
    if not parquet_files:
        parquet_files = sorted(Path(input_dir).glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"目录 {input_dir} 下没有 *.parquet 或 *.snappy.parquet 文件")
    count = 0
    for pf in parquet_files:
        parrot = pq.ParquetFile(str(pf))
        for batch in parrot.iter_batches(batch_size=1024):
            texts = batch.column(text_column).to_pylist()
            for text in texts:
                if max_docs is not None and count >= max_docs:
                    return
                yield text
                count += 1
    print(f"[data] 遍历完成，共 {count} 条文档来自 {len(parquet_files)} 个文件")


def _turns_to_text(turns: list) -> str:
    """把 list-of-dict 对话 turn（键 user/assistant）拼成一段纯文本。

    S4 退火混合源（FineVision text_code_*/text_*math*）语料的 text 列均为
    list<struct<user,assistant>>，需拼成单段文本再 tokenize。
    """
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


def iter_parquet_turns(input_dir: str, max_docs: Optional[int] = None) -> Iterator[str]:
    """流式遍历 parquet 目录下所有 *.parquet（train-*.parquet），读 texts 列
    （list-of-dict 对话 turn），每份多轮对话拼成一条文档文本。

    供 S4 退火数据混合（L3 + code / L3 + code + math）的 code/math 源补切。
    """
    parquet_files = sorted(Path(input_dir).glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"目录 {input_dir} 下没有 *.parquet 文件")
    count = 0
    for pf in parquet_files:
        parrot = pq.ParquetFile(str(pf))
        for batch in parrot.iter_batches(batch_size=1024):
            turns_list = batch.column("texts").to_pylist()
            for turns in turns_list:
                if max_docs is not None and count >= max_docs:
                    return
                yield _turns_to_text(turns)
                count += 1
    print(f"[data] 遍历完成，共 {count} 条文档来自 {len(parquet_files)} 个文件")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ultra-FineWeb-L3 (snappy.parquet) -> DeepSeek tokenize -> megatron .bin/.idx"
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="parquet 目录（含 part-*.snappy.parquet）",
    )
    parser.add_argument(
        "--output-prefix", required=True,
        help="输出 .bin/.idx 的公共前缀（不写扩展名）",
    )
    parser.add_argument(
        "--tokenizer", required=True,
        help="源 DeepSeek tokenizer 目录（含 tokenizer.json / tokenizer_config.json）",
    )
    parser.add_argument(
        "--tokenizer-output-dir", default=None,
        help="（可选）保存追加 EOD 后 tokenizer 副本的目录；默认 output-prefix 同目录下的 tokenizer_eod",
    )
    parser.add_argument("--max-docs", type=int, default=None, help="仅处理前 N 条文档（冒烟）")
    parser.add_argument("--text-column", default="content",
                        help="parquet 文本列名（默认 content；UltraX-Preview 用 cleaned_content）")
    parser.add_argument("--mode", default="content", choices=["content", "turns"],
                        help="content=读 content 单列（L3 snappy.parquet，默认）；"
                             "turns=读 texts 对话 turn（FineVision code/math *.parquet，S4 退火混合源）")
    parser.add_argument("--dtype", default="int32", choices=["int16", "int32", "int64"],
                        help="token id 存储精度；vocab=129281 用 int32 足够")
    parser.add_argument("--eod-token", default="<|endoftext|>", help="追加的 EOD 特殊 token")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="截断每条文档到最多 N 个字符再分词（防止超长/病态网页导致 BPE 死循环；CC-MAIN 原始爬取建议 50000）")
    parser.add_argument("--doc-timeout", type=int, default=0,
                        help="每条文档分词超时秒数；>0 时启用子进程硬超时保护（超时杀子进程、跳过该文档）。"
                             "应对 Rust-based fast tokenizer 在病态 CC-MAIN 网页上死循环。建议 120")
    args = parser.parse_args()

    t0 = time.time()

    # 1) 加载源 tokenizer 并追加 EOD，保存副本
    print("[tokenizer] 加载 ...")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    src_vocab = len(tokenizer)
    eod_id = _add_eod_token(tokenizer, args.eod_token)
    vocab_size = len(tokenizer)
    padded_vocab = ((vocab_size + _VOCAB_DIVISIBLE_BY - 1) // _VOCAB_DIVISIBLE_BY) * _VOCAB_DIVISIBLE_BY
    toks_out = args.tokenizer_output_dir or os.path.join(os.path.dirname(args.output_prefix), "tokenizer_eod")
    tokenizer.save_pretrained(toks_out)
    print(
        f"[tokenizer] 源词表 {src_vocab} -> 追加 EOD 后 {vocab_size}，"
        f"padding 到 {padded_vocab} (make_vocab_size_divisible_by={_VOCAB_DIVISIBLE_BY})；"
        f"副本已存 {toks_out}"
    )

    # 2) 流式 tokenize -> .bin/.idx
    dtype = getattr(np, args.dtype)
    builder = IndexedDatasetBuilder(bin_path=f"{args.output_prefix}.bin", dtype=dtype)
    n_docs = 0
    n_tokens = 0
    if args.mode == "turns":
        iterator = iter_parquet_turns(args.input_dir, max_docs=args.max_docs)
    else:
        iterator = iter_parquet_texts(args.input_dir, max_docs=args.max_docs,
                                      text_column=args.text_column)
    n_truncated = 0
    n_timeouts = 0
    n_errors = 0

    # ── 子进程硬超时保护 ──────────────────────────────────────────────
    # 当 --doc-timeout > 0 时，用 TokenizerWorker 在子进程中分词，
    # 超时则杀子进程并跳过该文档。这是应对 Rust-based fast tokenizer
    # 在某些 CC-MAIN 网页上陷入死循环的终极手段。
    use_worker = args.doc_timeout and args.doc_timeout > 0
    if use_worker:
        worker = TokenizerWorker(
            tokenizer_path=args.tokenizer,
            eod_token=args.eod_token,
            max_chars=args.max_chars,
            doc_timeout=args.doc_timeout,
        )
        print(f"[tokenize] 子进程硬超时保护已启用：doc_timeout={args.doc_timeout}s, "
              f"max_chars={args.max_chars}", flush=True)
    else:
        worker = None

    for text in iterator:
        raw_len = len(text) if text else 0
        if use_worker:
            ids = worker.tokenize(text or "")
            if ids is None:
                n_timeouts += 1
                if n_timeouts % 10 == 1:
                    print(f"[tokenize] 超时跳过累计 {n_timeouts} 文档 "
                          f"({n_docs} 已写入 / {n_tokens} tokens / "
                          f"{time.time() - t0:.1f}s)", flush=True)
                continue
        else:
            ids = _tokenize_document(text, tokenizer, eod_id, max_chars=args.max_chars)
        if args.max_chars is not None and raw_len > args.max_chars:
            n_truncated += 1
        builder.add_item(torch.tensor(ids, dtype=torch.long))
        builder.end_document()
        n_docs += 1
        n_tokens += len(ids)
        if n_docs % 50000 == 0:
            print(f"[tokenize] 已处理 {n_docs} 文档 / {n_tokens} tokens "
                  f"({time.time() - t0:.1f}s)")
    if use_worker:
        worker.close()
    builder.finalize(idx_path=f"{args.output_prefix}.idx")

    # 3) 写轻量元信息 JSON，供 launch 端核对
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
        "num_timeout_skips": n_timeouts,
        "num_errors": n_errors,
        "max_chars": args.max_chars,
        "doc_timeout": args.doc_timeout,
        "dtype": args.dtype,
        "input_dir": args.input_dir,
    }
    meta_path = f"{args.output_prefix}.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[done] {n_docs} 文档 / {n_tokens} tokens in {time.time() - t0:.1f}s；"
          f"产物：{args.output_prefix}.bin/.idx/.json")


if __name__ == "__main__":
    main()
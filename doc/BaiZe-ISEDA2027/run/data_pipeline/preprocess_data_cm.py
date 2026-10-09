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
import os
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
    text: str, tokenizer, eod_id: int, add_special_tokens: bool = False
) -> List[int]:
    """单条文档 -> token id 序列，末尾附 EOD token。"""
    ids = tokenizer(text, add_special_tokens=add_special_tokens, truncation=False)["input_ids"]
    return ids + [eod_id]


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
    for text in iterator:
        ids = _tokenize_document(text, tokenizer, eod_id)
        builder.add_item(torch.tensor(ids, dtype=torch.long))
        builder.end_document()
        n_docs += 1
        n_tokens += len(ids)
        if n_docs % 50000 == 0:
            print(f"[tokenize] 已处理 {n_docs} 文档 / {n_tokens} tokens "
                  f"({time.time() - t0:.1f}s)")
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
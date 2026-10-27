#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convert_sft_jsonl_to_parquet.py — 把 UltraData-SFT-2605 / SFT-Agent-2609 JSONL
转成「每文件一个 parquet」的 content 列，供 preprocess_data_cm.py --mode content 分词。

运维令 2026-10-27 13:3x：分词 SFT-2605 + Agent-2609 到 /nas_env、纳入映射镜像同等对待。

为什么「每文件一个 parquet」（而不是 convert_sft_to_parquet.py 的「每子集一个 parquet」）：
  - preprocess_data_cm.py 单进程单核分词；并行靠「多个 shard 同时跑」。
  - 每子集一个 parquet ⇒ 仅 12+4=16 个 parquet ⇒ 最多 16 并发，且 think/Code(166G)
    单 shard 串行 BPE 极慢。
  - 每文件一个 parquet ⇒ 1504+50=1554 个 parquet ⇒ 可分 ~25+13=38 shard，96 并发吃满。

序列化（把多轮对话压成一段纯文本，末尾由分词器附 EOD）：
  SFT-2605（messages=[{role,content}]，role∈{system,user,assistant}）：
       |role|>\n{content} 段，段间 \n\n。
  Agent-2609（messages 含 tool_calls / reasoning_content / tool 角色，顶层还有 tools 字段）：
    assistant 带 tool_calls: <|assistant|>\n{content}\n<reasoning>...\n<tool_calls>{json}
    tool 角色: <|tool|>\n{content}
    顶层 tools 字段（函数定义）作为前置 <|tools|>\n{json} 段拼到最前（留证据：不丢字段）。
    ⚠️ Agent 类含 tool_call/assistant 结构，转换逻辑须适配并留证据 —— 本脚本把
       tool_calls / reasoning_content / tools 全部序列化进 content 文本，不丢字段。
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterator, List, Optional

import pyarrow as pa
import pyarrow.parquet as pq

_BATCH_SIZE = 4096
_ROLE_TAGS = {"user": "user", "assistant": "assistant", "system": "system", "tool": "tool"}


def _safe_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return json.dumps(x, ensure_ascii=False)


def _messages_to_text_sft(messages: list) -> str:
    """SFT-2605：messages=[{role,content}]，role∈{system,user,assistant}。"""
    segs: List[str] = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        tag = _ROLE_TAGS.get(role, role)
        segs.append(f"<|{tag}|>\n{content}" if tag else content)
    return "\n\n".join(segs)


def _messages_to_text_agent(messages: list, tools: Optional[list] = None) -> str:
    """Agent-2609：messages 含 tool_calls / reasoning_content / tool 角色。
    把 tool_calls / reasoning_content / tools 全部序列化进文本，不丢字段。"""
    segs: List[str] = []
    if tools:
        segs.append(f"<|tools|>\n{json.dumps(tools, ensure_ascii=False)}")
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        tag = _ROLE_TAGS.get(role, role)
        if role == "assistant":
            parts: List[str] = []
            content = (msg.get("content") or "").strip()
            if content:
                parts.append(content)
            rc = msg.get("reasoning_content")
            if rc:
                parts.append(f"<reasoning>\n{_safe_str(rc).strip()}")
            tc = msg.get("tool_calls")
            if tc:
                parts.append(f"<tool_calls>\n{json.dumps(tc, ensure_ascii=False)}")
            if not parts:
                continue
            segs.append(f"<|{tag}|>\n" + "\n".join(parts)) if tag else segs.append("\n".join(parts))
        else:
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            segs.append(f"<|{tag}|>\n{content}" if tag else content)
    return "\n\n".join(segs)

def _iter_jsonl_files(input_dir: Path) -> List[Path]:
    return sorted(input_dir.glob("*.jsonl"))


def convert_one_jsonl(jsonl_path: Path, out_dir: Path, prefix: str, file_idx: int,
                      kind: str, max_docs: Optional[int]) -> dict:
    """一个 jsonl 文件 -> 一个 parquet 文件（{prefix}_p{NNNN}.parquet）。"""
    out_path = out_dir / f"{prefix}_p{file_idx:04d}.parquet"
    written = 0
    t0 = time.time()
    writer = None
    batch_texts: List[str] = []
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            messages = obj.get("messages")
            if not messages:
                continue
            if kind == "agent2609":
                text = _messages_to_text_agent(messages, obj.get("tools"))
            else:
                text = _messages_to_text_sft(messages)
            if not text:
                continue
            batch_texts.append(text)
            if len(batch_texts) >= _BATCH_SIZE:
                table = pa.table({"content": pa.array(batch_texts, type=pa.string())})
                if writer is None:
                    writer = pq.ParquetWriter(str(out_path), table.schema)
                writer.write_table(table)
                written += len(batch_texts)
                batch_texts = []
            if max_docs is not None and written + len(batch_texts) >= max_docs:
                break
    if batch_texts:
        table = pa.table({"content": pa.array(batch_texts, type=pa.string())})
        if writer is None:
            writer = pq.ParquetWriter(str(out_path), table.schema)
        writer.write_table(table)
        written += len(batch_texts)
    if writer is not None:
        writer.close()
    fsize = out_path.stat().st_size if out_path.exists() else 0
    print(f"[convert] {prefix}_p{file_idx:04d}: {written} docs -> {out_path.name} "
          f"({fsize/1e6:.1f} MB, {time.time()-t0:.0f}s)")
    return {"file": str(out_path), "docs": written, "bytes": fsize}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="SFT-2605 / Agent-2609 JSONL -> 每文件一个 parquet (content 列)")
    ap.add_argument("--input-dir", required=True, help="一个子集目录（含 *.jsonl）")
    ap.add_argument("--output-dir", required=True, help="parquet 输出目录（扁平）")
    ap.add_argument("--prefix", required=True, help="parquet 文件名前缀")
    ap.add_argument("--kind", required=True, choices=["sft2605", "agent2609"],
                    help="sft2605=简单 messages；agent2609=含 tool_calls/reasoning_content/tool 角色")
    ap.add_argument("--max-docs", type=int, default=None, help="每文件仅前 N 条对话（冒烟）")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = _iter_jsonl_files(in_dir)
    if not files:
        print(f"[convert] WARNING: no .jsonl under {in_dir}")
        return
    print(f"[convert] {args.prefix}: {len(files)} jsonl files, kind={args.kind}")
    total_docs = 0
    total_bytes = 0
    t0 = time.time()
    for i, f in enumerate(files):
        st = convert_one_jsonl(f, out_dir, args.prefix, i, args.kind, args.max_docs)
        total_docs += st["docs"]
        total_bytes += st["bytes"]
    print(f"[convert] {args.prefix} DONE: {len(files)} parquet, {total_docs} docs, "
          f"{total_bytes/1e9:.2f} GB, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()


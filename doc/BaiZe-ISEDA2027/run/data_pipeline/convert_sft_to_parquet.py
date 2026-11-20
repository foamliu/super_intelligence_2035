#!/usr/bin/env python3
"""Convert UltraData-SFT-2605 JSONL (chat messages) -> parquet with `content` column.

Output parquet can be fed directly to ``preprocess_data.py --mode content``
for tokenization into NVIDIA GPT ``.bin/.idx`` format.

Usage (smoke test, first 1000 docs):
    python convert_sft_to_parquet.py \\
        --input-dir /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data/no_think/Math \\
        --output-dir /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/mix_sft/math_no_think \\
        --max-docs 1000

Full run (all subsets, both think/no_think):
    python convert_sft_to_parquet.py \\
        --input-dir /nas_inference/app.e0031982/datasets/openbmb/UltraData-SFT-2605/data \\
        --output-dir /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/mix_sft \\
        --recursive
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

_ROLE_TAGS = {"user": "user", "assistant": "assistant", "system": "system"}


def _messages_to_text(messages: list) -> str:
    """Flatten a list of {role, content} dicts to a single text string."""
    segs: List[str] = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        tag = _ROLE_TAGS.get(role, role)
        if tag:
            segs.append(f"<|{tag}|>\n{content}")
        else:
            segs.append(content)
    return "\n\n".join(segs)


def _iter_jsonl_files(input_dir: Path, recursive: bool) -> List[Path]:
    """Collect all *.jsonl files under input_dir."""
    pattern = "**/*.jsonl" if recursive else "*.jsonl"
    return sorted(input_dir.glob(pattern))


def _iter_jsonl_records(
    files: List[Path], max_docs: Optional[int] = None
) -> Iterator[str]:
    """Yield text strings from JSONL files, one per conversation."""
    count = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
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
                text = _messages_to_text(messages)
                if not text:
                    continue
                yield text
                count += 1
                if max_docs is not None and count >= max_docs:
                    return
    print(f"[convert] {count} docs from {len(files)} files")


def convert_subset(
    input_dir: str,
    output_dir: str,
    subset_label: str,
    recursive: bool = False,
    max_docs: Optional[int] = None,
) -> dict:
    """Convert one subset of JSONL files to a single parquet file."""
    files = _iter_jsonl_files(Path(input_dir), recursive)
    if not files:
        print(f"[convert] WARNING: no .jsonl found under {input_dir}")
        return {"file_count": 0, "doc_count": 0, "output_path": "", "bytes": 0}

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"sft_{subset_label}.parquet"
    iterator = _iter_jsonl_records(files, max_docs=max_docs)

    written = 0
    t0 = time.time()
    writer = None
    batch_texts: List[str] = []

    for text in iterator:
        batch_texts.append(text)
        if len(batch_texts) >= _BATCH_SIZE:
            table = pa.table({"content": pa.array(batch_texts, type=pa.string())})
            if writer is None:
                writer = pq.ParquetWriter(str(out_path), table.schema)
            writer.write_table(table)
            written += len(batch_texts)
            batch_texts = []
            if written % (_BATCH_SIZE * 10) == 0:
                print(f"  [{subset_label}] {written} docs, {time.time()-t0:.0f}s")

    if batch_texts:
        table = pa.table({"content": pa.array(batch_texts, type=pa.string())})
        if writer is None:
            writer = pq.ParquetWriter(str(out_path), table.schema)
        writer.write_table(table)
        written += len(batch_texts)

    if writer is not None:
        writer.close()

    fsize = out_path.stat().st_size if out_path.exists() else 0
    print(f"[convert] {subset_label}: {written} docs -> {out_path} ({fsize/1e6:.1f} MB)")
    return {"file_count": len(files), "doc_count": written,
            "output_path": str(out_path), "bytes": fsize}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert UltraData-SFT-2605 JSONL -> parquet (content column)"
    )
    parser.add_argument("--input-dir", required=True,
                        help="Root dir of SFT-2605 JSONL")
    parser.add_argument("--output-dir", required=True,
                        help="Output directory for parquet files")
    parser.add_argument("--recursive", action="store_true",
                        help="Recurse: convert all subsets under data/{no_think,think}/*")
    parser.add_argument("--max-docs", type=int, default=None,
                        help="Limit docs per subset (smoke test)")
    args = parser.parse_args()

    input_root = Path(args.input_dir)

    if args.recursive:
        all_stats = []
        for think_dir in sorted(input_root.iterdir()):
            if not think_dir.is_dir():
                continue
            think_type = think_dir.name
            for cat_dir in sorted(think_dir.iterdir()):
                if not cat_dir.is_dir():
                    continue
                label = f"{think_type}_{cat_dir.name}"
                stats = convert_subset(
                    str(cat_dir), args.output_dir, label,
                    recursive=False, max_docs=args.max_docs)
                all_stats.append((label, stats))
        total_docs = sum(s["doc_count"] for _, s in all_stats)
        total_bytes = sum(s["bytes"] for _, s in all_stats)
        print(f"\n[convert] ALL DONE: {len(all_stats)} subsets, "
              f"{total_docs} docs, {total_bytes/1e9:.2f} GB")
        for label, s in all_stats:
            if s["doc_count"] > 0:
                print(f"  {label}: {s['doc_count']} docs, {s['bytes']/1e6:.1f} MB")
    else:
        label = input_root.name
        convert_subset(str(input_root), args.output_dir, label,
                       recursive=False, max_docs=args.max_docs)


if __name__ == "__main__":
    main()

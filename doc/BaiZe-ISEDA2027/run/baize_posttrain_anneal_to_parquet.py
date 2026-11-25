#!/usr/bin/env python3
"""baize_posttrain_anneal_to_parquet.py — Convert PyAether anneal corpus JSONL -> parquet.

Reads ``pyAether_api_anneal_corpus.jsonl`` (built by R153, 400 API-ref docs,
contamination gate PASS) and writes a single-column parquet (``content``) that
``preprocess_data.py --mode content`` can tokenize into NVIDIA GPT ``.bin/.idx``
format for the domain-annealing blend in ``baize_posttrain_anneal.sh``.

This is the conversion half of the data-line tokenization request (R160).
The tokenization half (parquet -> .bin/.idx) requires ``preprocess_data.py`` +
``tokenizer_eod`` which only exist on .29/.12, not .17.

Usage:
    python3 baize_posttrain_anneal_to_parquet.py
    python3 baize_posttrain_anneal_to_parquet.py --input pyAether_api_anneal_corpus.jsonl --output /tmp/pyAether_api_anneal.parquet
    python3 baize_posttrain_anneal_to_parquet.py --help

Red line (total outline 5.1): corpus = API reference docs (signatures / params /
returns / usage examples) ONLY; the 158 eval-task prompts / entry_points /
assertions / canonical solutions NEVER enter.  Verified by
baize_posttrain_contamination_gate.sh in R153 (400 scanned / 0 hits / PASS).
"""
import argparse
import json
import sys
import time
from pathlib import Path

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("ERROR: pyarrow not installed. On .17 use: ~/code/verl_cu124_venv/bin/python",
          file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "pyAether_api_anneal_corpus.jsonl"
DEFAULT_OUTPUT = SCRIPT_DIR / "pyAether_api_anneal.parquet"
CHARS_PER_TOK = 3.7  # consistent with R153 estimate


def convert(input_path: Path, output_path: Path) -> dict:
    """Read JSONL (field ``text'') -> parquet (column ``content'')."""
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    texts = []
    t0 = time.time()
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = obj.get("text", "")
            if text:
                texts.append(text)

    if not texts:
        print("ERROR: no valid text records found", file=sys.stderr)
        sys.exit(1)

    table = pa.table({"content": pa.array(texts, type=pa.string())})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, str(output_path))

    total_chars = sum(len(t) for t in texts)
    est_tokens = int(total_chars / CHARS_PER_TOK)
    fsize = output_path.stat().st_size
    elapsed = time.time() - t0

    stats = {
        "docs": len(texts),
        "total_chars": total_chars,
        "est_tokens": est_tokens,
        "parquet_bytes": fsize,
        "parquet_mb": round(fsize / 1e6, 2),
        "elapsed_s": round(elapsed, 2),
        "output": str(output_path),
    }
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Convert PyAether anneal corpus JSONL -> parquet (content column) "
                    "for preprocess_data.py --mode content"
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT),
                        help=f"Input JSONL (default: {DEFAULT_INPUT.name})")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help=f"Output parquet (default: {DEFAULT_OUTPUT.name})")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    print(f"[anneal-to-parquet] {inp} -> {out}")
    stats = convert(inp, out)
    print(f"  docs         : {stats['docs']}")
    print(f"  total_chars  : {stats['total_chars']:,}")
    print(f"  est_tokens   : {stats['est_tokens']:,} (chars/{CHARS_PER_TOK})")
    print(f"  parquet_size : {stats['parquet_mb']} MB")
    print(f"  elapsed      : {stats['elapsed_s']}s")
    print(f"  output       : {stats['output']}")
    print("[anneal-to-parquet] DONE")


if __name__ == "__main__":
    main()

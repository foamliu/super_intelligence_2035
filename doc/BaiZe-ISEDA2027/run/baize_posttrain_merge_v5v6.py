#!/usr/bin/env python3
"""baize_posttrain_merge_v5v6.py — R150: Merge v5 + v6 PyAether SFT corpora into a unified corpus.

R149 conclusion (EXPERIMENTS_POSTTRAIN.md §R149 §6):
  - v5 (sft_pyaether_corpus_v5_deep_enriched.jsonl, 1193 pairs): broad API coverage
    (all 488 eval APIs) but completions are shallow LLM stubs (def call_x(): return X()).
  - v6 (sft_pyaether_corpus_v6_method_examples.jsonl, 352 pairs): authoritative >>> doctest
    examples extracted from API docs; higher quality but only 186/488 API coverage.
  - Merge -> 1545 pairs unified SFT pyaether corpus for the pyaether20 blend.

This script:
  1. Reads both JSONL files.
  2. Normalizes fields (api_used: list|str -> list; ensure pair_id/type/prompt/completion).
  3. Deduplicates by md5(prompt + completion) to avoid exact overlaps.
  4. Emits unified JSONL + prints stats (type distribution, API coverage, token estimate).
  5. Optionally emits a verl-compatible SFT parquet (conversation + metadata schema).

Usage:
  python3 baize_posttrain_merge_v5v6.py                          # full run, default paths
  python3 baize_posttrain_merge_v5v6.py --dry-run                # stats only, no output file
  python3 baize_posttrain_merge_v5v6.py --v5 <j> --v6 <j> -o <j>  # custom paths
  python3 baize_posttrain_merge_v5v6.py --parquet                # also emit verl SFT parquet
"""
import argparse
import collections
import hashlib
import json
import os
import sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_V5 = os.path.join(RUN_DIR, "sft_pyaether_corpus_v5_deep_enriched.jsonl")
DEFAULT_V6 = os.path.join(RUN_DIR, "sft_pyaether_corpus_v6_method_examples.jsonl")
DEFAULT_V7 = os.path.join(RUN_DIR, "sft_pyaether_corpus_v7_generative.jsonl")
DEFAULT_OUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_unified_v5v6.jsonl")


def normalize_api_used(val):
    """api_used may be a list (v5) or a string (v6); normalize to list of str."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, list):
        return [str(x) for x in val]
    return [str(val)]


def load_jsonl(path):
    pairs = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as exc:
                print("WARN: {0}:{1} parse error: {2}".format(path, lineno, exc),
                      file=sys.stderr)
                continue
            d["api_used"] = normalize_api_used(d.get("api_used"))
            d.setdefault("type", "unknown")
            d.setdefault("source", os.path.basename(path))
            d.setdefault("contamination_check", "pending")
            pairs.append(d)
    return pairs


def content_hash(d):
    h = hashlib.md5()
    h.update((d.get("prompt", "") + "\n|||\n" + d.get("completion", "")).encode("utf-8"))
    return h.hexdigest()


def merge(v5_pairs, v6_pairs, v7_pairs=None):
    """Merge v5 then v6 then v7; deduplicate by content hash (keep first occurrence)."""
    seen = set()
    merged = []
    dup_v5 = 0
    dup_v6 = 0
    dup_v7 = 0
    for d in v5_pairs:
        ch = content_hash(d)
        if ch in seen:
            dup_v5 += 1
            continue
        seen.add(ch)
        merged.append(d)
    for d in v6_pairs:
        ch = content_hash(d)
        if ch in seen:
            dup_v6 += 1
            continue
        seen.add(ch)
        d["contamination_check"] = "passed_R149"
        merged.append(d)
    if v7_pairs:
        for d in v7_pairs:
            ch = content_hash(d)
            if ch in seen:
                dup_v7 += 1
                continue
            seen.add(ch)
            d["contamination_check"] = "pending_v7"
            merged.append(d)
    return merged, dup_v5, dup_v6, dup_v7


def estimate_tokens(text):
    """Rough token estimate: chars / 3.7 (consistent with R149 estimate)."""
    return int(len(text) / 3.7)


def to_verl_conversation(d):
    """Convert a prompt/completion pair to verl SFT conversation format."""
    prompt = d.get("prompt", "")
    completion = d.get("completion", "")
    comp_clean = completion
    if comp_clean.startswith("```"):
        lines = comp_clean.split("\n")
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        comp_clean = "\n".join(lines)
    return {
        "conversation": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": comp_clean},
        ],
        "metadata": {
            "pair_id": d.get("pair_id", ""),
            "type": d.get("type", ""),
            "api_used": d.get("api_used", []),
            "source": d.get("source", ""),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Merge v5+v6(+v7) PyAether SFT corpora (R150/R151)")
    ap.add_argument("--v5", default=DEFAULT_V5, help="v5 JSONL path")
    ap.add_argument("--v6", default=DEFAULT_V6, help="v6 JSONL path")
    ap.add_argument("--v7", default="", help="v7 JSONL path (optional; default = auto-detect)")
    ap.add_argument("-o", "--out", default="", help="output unified JSONL (auto if empty)")
    ap.add_argument("--dry-run", action="store_true", help="stats only, no output file")
    ap.add_argument("--parquet", action="store_true",
                    help="also emit verl SFT parquet (requires pandas/pyarrow)")
    args = ap.parse_args()

    for p in (args.v5, args.v6):
        if not os.path.isfile(p):
            print("ERROR: input not found: {0}".format(p), file=sys.stderr)
            return 1

    v7_path = args.v7
    if not v7_path:
        v7_path = DEFAULT_V7 if os.path.isfile(DEFAULT_V7) else ""
    use_v7 = bool(v7_path and os.path.isfile(v7_path))
    if args.v7 and not use_v7:
        print("ERROR: --v7 not found: {0}".format(args.v7), file=sys.stderr)
        return 1

    out_path = args.out
    if not out_path:
        out_path = os.path.join(RUN_DIR, "sft_pyaether_corpus_unified_v5v6v7.jsonl") if use_v7 else DEFAULT_OUT

    v5 = load_jsonl(args.v5)
    v6 = load_jsonl(args.v6)
    v7 = load_jsonl(v7_path) if use_v7 else []
    merged, dup_v5, dup_v6, dup_v7 = merge(v5, v6, v7 if use_v7 else None)

    type_dist = collections.Counter(d["type"] for d in merged)
    all_apis = set()
    for d in merged:
        all_apis.update(d.get("api_used", []))
    total_chars = sum(len(d.get("prompt", "")) + len(d.get("completion", "")) for d in merged)
    total_tokens = estimate_tokens(" " * total_chars)

    print("=" * 60)
    print("R150/R151 v5+v6(+v7) Unified SFT Corpus Merge")
    print("=" * 60)
    print("v5 input : {0} ({1} pairs)".format(args.v5, len(v5)))
    print("v6 input : {0} ({1} pairs)".format(args.v6, len(v6)))
    if use_v7:
        print("v7 input : {0} ({1} pairs)".format(v7_path, len(v7)))
    print("dedup    : v5 removed {0}, v6 removed {1}, v7 removed {2}".format(dup_v5, dup_v6, dup_v7))
    print("merged   : {0} pairs".format(len(merged)))
    print("-" * 60)
    print("type distribution:")
    for t, c in sorted(type_dist.items()):
        print("  {0:30s} {1:5d}".format(t, c))
    print("-" * 60)
    print("unique api_used: {0}".format(len(all_apis)))
    print("total chars    : {0}".format(total_chars))
    print("est. tokens    : ~{0} ({1:.1f}K)".format(total_tokens, total_tokens / 1000.0))
    print("output         : {0}".format("(dry-run, no file)" if args.dry_run else out_path))
    print("=" * 60)

    if args.dry_run:
        return 0

    with open(out_path, "w", encoding="utf-8") as fh:
        for d in merged:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    out_size = os.path.getsize(out_path)
    print("wrote {0} ({1:.1f} KB)".format(out_path, out_size / 1024.0))

    if args.parquet:
        try:
            import pandas as pd
        except ImportError:
            print("WARN: pandas not available, skipping parquet", file=sys.stderr)
            return 0
        rows = [to_verl_conversation(d) for d in merged]
        df = pd.DataFrame(rows)
        pq_path = out_path.replace(".jsonl", ".parquet")
        df.to_parquet(pq_path, index=False)
        print("wrote {0} ({1:.1f} KB, {2} rows)".format(
            pq_path, os.path.getsize(pq_path) / 1024.0, len(df)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

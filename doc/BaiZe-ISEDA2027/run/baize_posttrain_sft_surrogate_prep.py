#!/usr/bin/env python3
"""baize_posttrain_sft_surrogate_prep.py — Phase 2 surrogate SFT data preparation.

Splits the unified v5+v6+v7 PyAether SFT parquet (R152, 1725 rows) into
deterministic train / val parquet files for verl FSDP SFT.

The parquet has columns:
    conversation : list[dict]  — [{role: "user", content: "..."},
                                  {role: "assistant", content: "..."}]
    metadata     : dict        — {pair_id, type, api_used, source}

verl MultiTurnSFTDataset reads the conversation column (configurable via
data.multiturn.messages_key) and calls tokenizer.apply_chat_template.

Usage:
    python baize_posttrain_sft_surrogate_prep.py --help
    python baize_posttrain_sft_surrogate_prep.py            # default 90/10 split
    python baize_posttrain_sft_surrogate_prep.py --upsample 3  # 3x train upsampling
    python baize_posttrain_sft_surrogate_prep.py --dry-run     # print plan only

Output (in --out-dir, default = script dir):
    sft_surrogate_train.parquet
    sft_surrogate_val.parquet

Red line: this script only re-splits an already-passed contamination gate
corpus (R150/R151 gate, 1725 docs / 0 hits). No new synthesis. If the source
parquet is missing, it errors out rather than generating anything.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(
    SCRIPT_DIR, "sft_pyaether_corpus_unified_v5v6v7.parquet"
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--src",
        default=DEFAULT_SRC,
        help="source unified parquet (default: sft_pyaether_corpus_unified_v5v6v7.parquet)",
    )
    ap.add_argument(
        "--out-dir",
        default=SCRIPT_DIR,
        help="output directory for train/val parquet (default: script dir)",
    )
    ap.add_argument(
        "--val-ratio",
        type=float,
        default=0.1,
        help="fraction for validation (default 0.1 = 10%%)",
    )
    ap.add_argument(
        "--upsample",
        type=int,
        default=1,
        help="upsample training set N times (default 1 = no upsampling)",
    )
    ap.add_argument(
        "--seed", type=int, default=42, help="random seed for split (default 42)"
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="print plan only, do not write files"
    )
    args = ap.parse_args()

    # ---- load source ----
    if not os.path.isfile(args.src):
        print(f"ERROR: source parquet not found: {args.src}")
        sys.exit(1)
    df = pd.read_parquet(args.src)
    n = len(df)
    print(f"[prep] source: {args.src}")
    print(f"[prep] rows: {n}")
    print(f"[prep] columns: {df.columns.tolist()}")

    # validate schema
    if "conversation" not in df.columns:
        print("ERROR: 'conversation' column missing in source parquet")
        sys.exit(1)
    # spot-check message structure
    sample = df.iloc[0]["conversation"]
    sample_msgs = list(sample) if not isinstance(sample, list) else sample
    for m in sample_msgs:
        if "role" not in m or "content" not in m:
            print(f"ERROR: malformed message in row 0: {m}")
            sys.exit(1)
    roles_seen = set()
    for conv in df["conversation"]:
        for m in (list(conv) if not isinstance(conv, list) else conv):
            roles_seen.add(m["role"])
    print(f"[prep] roles present: {roles_seen}")

    # ---- deterministic split ----
    n_val = max(1, int(n * args.val_ratio))
    n_train = n - n_val
    rng = np.random.RandomState(args.seed)
    idx = rng.permutation(n)
    val_idx = idx[:n_val]
    train_idx = idx[n_val:]
    print(f"[prep] split: train={n_train} val={n_val} (val_ratio={args.val_ratio})")

    train_df = df.iloc[train_idx].reset_index(drop=True)
    val_df = df.iloc[val_idx].reset_index(drop=True)

    # ---- optional upsampling ----
    if args.upsample > 1:
        frames = [train_df] * args.upsample
        train_df = pd.concat(frames, ignore_index=True)
        print(
            f"[prep] upsampled train x{args.upsample} -> {len(train_df)} rows"
        )

    # ---- char/token stats ----
    char_lens = []
    for conv in train_df["conversation"]:
        msgs = list(conv) if not isinstance(conv, list) else conv
        char_lens.append(sum(len(m["content"]) for m in msgs))
    char_lens.sort()
    p95 = char_lens[int(len(char_lens) * 0.05)] if char_lens else 0
    mx = char_lens[-1] if char_lens else 0
    print(
        f"[prep] train char_len: median={char_lens[len(char_lens)//2]} "
        f"p95={p95} max={mx} (est_tok max~{mx//3})"
    )
    print(
        f"[prep] recommended data.max_length: {max(1024, ((mx // 3) + 256) // 256 * 256)}"
    )

    # ---- write ----
    train_path = os.path.join(args.out_dir, "sft_surrogate_train.parquet")
    val_path = os.path.join(args.out_dir, "sft_surrogate_val.parquet")
    print(f"[prep] train -> {train_path} ({len(train_df)} rows)")
    print(f"[prep] val   -> {val_path} ({len(val_df)} rows)")

    if args.dry_run:
        print("[prep] --dry-run: no files written.")
        return

    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)

    # verify round-trip
    chk = pd.read_parquet(train_path)
    assert len(chk) == len(train_df), "round-trip row count mismatch"
    print("[prep] DONE — train/val parquet written and verified.")


if __name__ == "__main__":
    main()

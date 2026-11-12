#!/usr/bin/env python3
"""
Pre-tokenize v39 agentic SFT data to avoid the slow MultiTurnSFTDataset.__getitem__
(which calls tokenizer.apply_chat_template 2N times per example in DataLoader workers).

This script tokenizes each conversation using the MiniCPM5 chat template,
computes loss_mask (1 for assistant turns, 0 for system/user/tool_result),
pads to max_length, and saves as parquet with input_ids/attention_mask/loss_mask/position_ids.
"""
import argparse, os, sys, time
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer


def series_to_item(ls):
    while isinstance(ls, (pd.Series, np.ndarray)) and len(ls) == 1:
        ls = ls[0]
    return ls


def pretokenize_one(conv, tokenizer, max_length, truncation="right"):
    """Tokenize one conversation and compute loss mask (same logic as MultiTurnSFTDataset)."""
    full_tokens = tokenizer.apply_chat_template(
        conv, tokenize=True, return_tensors="pt", add_generation_prompt=False)
    input_ids = full_tokens[0]
    attention_mask = torch.ones_like(input_ids)
    loss_mask = torch.zeros_like(input_ids, dtype=torch.long)

    for i, msg in enumerate(conv):
        prefix_tokens = tokenizer.apply_chat_template(
            conv[:i+1], tokenize=True, return_tensors="pt", add_generation_prompt=False)
        prev_tokens = (tokenizer.apply_chat_template(
            conv[:i], tokenize=True, return_tensors="pt", add_generation_prompt=False)
            if i > 0 else None)
        start_pos = prev_tokens[0].shape[0] if prev_tokens is not None else 0
        end_pos = prefix_tokens[0].shape[0]
        if msg["role"] == "assistant":
            loss_mask[start_pos:end_pos] = 1

    seq_len = input_ids.shape[0]
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0

    if seq_len < max_length:
        pad_len = max_length - seq_len
        input_ids = torch.cat((input_ids, torch.ones((pad_len,), dtype=input_ids.dtype) * pad_id))
        attention_mask = torch.cat((attention_mask, torch.zeros((pad_len,), dtype=attention_mask.dtype)))
        loss_mask = torch.cat((loss_mask, torch.zeros((pad_len,), dtype=loss_mask.dtype)))
    elif seq_len > max_length:
        if truncation == "right":
            input_ids, attention_mask, loss_mask = (
                input_ids[:max_length], attention_mask[:max_length], loss_mask[:max_length])
        elif truncation == "left":
            input_ids, attention_mask, loss_mask = (
                input_ids[-max_length:], attention_mask[-max_length:], loss_mask[-max_length:])
        else:
            raise ValueError(f"seq_len={seq_len} > max_length={max_length}")

    position_ids = torch.arange(len(input_ids), dtype=torch.long) * attention_mask
    return {
        "input_ids": input_ids.tolist(),
        "attention_mask": attention_mask.tolist(),
        "loss_mask": loss_mask.tolist(),
        "position_ids": position_ids.tolist(),
    }


def process_parquet(in_path, out_path, tokenizer, max_length, truncation="right"):
    """Process one parquet file: read conversations, pre-tokenize, save."""
    df = pd.read_parquet(in_path)
    print(f"  Loaded {len(df)} examples from {in_path}")
    results, skipped = [], 0
    t0 = time.time()
    for idx in range(len(df)):
        conv = series_to_item(df["conversation"].iloc[idx])
        try:
            results.append(pretokenize_one(conv, tokenizer, max_length, truncation))
        except Exception as e:
            print(f"  WARNING: skipping example {idx}: {e}")
            skipped += 1
            continue
        if (idx + 1) % 200 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            print(f"  [{idx+1}/{len(df)}] {rate:.1f} ex/s, ETA {(len(df)-idx-1)/rate:.0f}s")
    print(f"  Processed {len(results)}, skipped {skipped}, time {time.time()-t0:.1f}s")
    pd.DataFrame(results).to_parquet(out_path)
    print(f"  Saved {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)")
    loss_sums = [sum(r["loss_mask"]) for r in results]
    print(f"  Loss tokens: mean={np.mean(loss_sums):.0f} min={np.min(loss_sums)} max={np.max(loss_sums)}")
    return len(results)


def main():
    ap = argparse.ArgumentParser(description="Pre-tokenize v39 agentic SFT data")
    ap.add_argument("--data-dir", default="sft_surrogate_data/minicpm5_agentic_v39")
    ap.add_argument("--out-dir", default="sft_surrogate_data/minicpm5_agentic_v39_pretok")
    ap.add_argument("--model-path", default="/nas_data/app.e0031982/models/MiniCPM5-2B")
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--truncation", default="right", choices=["left", "right"])
    args = ap.parse_args()

    print(f"Loading tokenizer from {args.model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    print(f"  pad_token_id={tokenizer.pad_token_id}, eos_token={tokenizer.eos_token}")
    os.makedirs(args.out_dir, exist_ok=True)

    print(f"\nProcessing TRAIN...")
    n_train = process_parquet(
        os.path.join(args.data_dir, "sft_surrogate_train.parquet"),
        os.path.join(args.out_dir, "sft_surrogate_train.parquet"),
        tokenizer, args.max_length, args.truncation)
    print(f"\nProcessing VAL...")
    n_val = process_parquet(
        os.path.join(args.data_dir, "sft_surrogate_val.parquet"),
        os.path.join(args.out_dir, "sft_surrogate_val.parquet"),
        tokenizer, args.max_length, args.truncation)

    print(f"\n=== DONE: train={n_train} val={n_val} max_length={args.max_length} ===")
    print(f"Use with verl: data.custom_cls.path={os.path.abspath('baize_posttrain_pretokenized_dataset.py')}")
    print(f"              data.custom_cls.name=PreTokenizedSFTDataset")
    print(f"              data.multiturn.enable=false")


if __name__ == "__main__":
    main()
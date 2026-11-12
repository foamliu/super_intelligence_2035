#!/usr/bin/env python3
"""Quick test: pre-tokenize a few v39 examples to verify the approach works."""
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained(
    "/nas_data/app.e0031982/models/MiniCPM5-2B", trust_remote_code=True
)

df = pd.read_parquet(
    "sft_surrogate_data/minicpm5_agentic_v39/sft_surrogate_train.parquet"
)
print(f"Total examples: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Check first 3 examples
for idx in range(3):
    conv = df["conversation"].iloc[idx]
    while isinstance(conv, (pd.Series, np.ndarray)) and len(conv) == 1:
        conv = conv[0]

    n_turns = len(conv)
    print(f"\n--- Example {idx}: {n_turns} turns ---")
    for i, msg in enumerate(conv):
        role = msg["role"]
        content_len = len(msg["content"])
        print(f"  Turn {i}: role={role}, content_len={content_len}")

    # Full tokenization
    full_tokens = tok.apply_chat_template(
        conv, tokenize=True, return_tensors="pt", add_generation_prompt=False
    )
    input_ids = full_tokens[0]
    print(f"  Full token count: {input_ids.shape[0]}")

    # Loss mask (same logic as MultiTurnSFTDataset)
    loss_mask = torch.zeros_like(input_ids, dtype=torch.long)
    for i, msg in enumerate(conv):
        prefix_tokens = tok.apply_chat_template(
            conv[: i + 1], tokenize=True, return_tensors="pt",
            add_generation_prompt=False
        )
        prev_tokens = (
            tok.apply_chat_template(
                conv[:i], tokenize=True, return_tensors="pt",
                add_generation_prompt=False
            )
            if i > 0
            else None
        )
        start_pos = prev_tokens[0].shape[0] if prev_tokens is not None else 0
        end_pos = prefix_tokens[0].shape[0]
        if msg["role"] == "assistant":
            loss_mask[start_pos:end_pos] = 1

    print(f"  Loss mask: {loss_mask.sum().item()} / {len(loss_mask)} tokens with loss")

print("\nSUCCESS: Pre-tokenization approach works!")

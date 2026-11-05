#!/usr/bin/env python
"""CPU dry-run test for SFT data pipeline (no model loading, no GPU needed).

Tests:
1. Tokenizer loads
2. conversation_to_text produces valid text + assistant spans
3. Tokenization + loss masking produces correct label distribution
4. collate_fn pads correctly
5. Dataset class loads correctly
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sft_train_wave import (
    conversation_to_text, WaveSFTDataset, collate_fn,
)
from transformers import AutoTokenizer

LLM_PATH = "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/qwen3vl_2b_text_extracted"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "sft_pilot_balanced.jsonl")

def main():
    print("=== 1. Load tokenizer ===")
    tok = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    print(f"  vocab_size={tok.vocab_size}, pad_token_id={tok.pad_token_id}, "
          f"eos_token_id={tok.eos_token}")
    print(f"  model_max_length={tok.model_max_length}")

    print()
    print("=== 2. Load 5 trajectories and test conversation_to_text ===")
    with open(DATA_FILE) as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            traj = json.loads(line)
            conv = traj["conversation"]
            full_text, assistant_spans = conversation_to_text(conv)
            print(f"  traj[{i}] circuit={traj['circuit_type']} "
                  f"conv_turns={len(conv)} text_len={len(full_text)} "
                  f"assistant_spans={len(assistant_spans)}")
            for sp in assistant_spans:
                assert 0 <= sp[0] < sp[1] <= len(full_text), \
                    f"Bad span {sp} for text_len {len(full_text)}"
            preview = full_text[:200].replace("\n", " | ")
            print(f"    text_preview: {preview}...")

    print()
    print("=== 3. Test tokenization + loss masking ===")
    with open(DATA_FILE) as f:
        traj = json.loads(f.readline())
    conv = traj["conversation"]
    full_text, assistant_spans = conversation_to_text(conv)
    enc = tok(full_text, add_special_tokens=False, truncation=True,
              max_length=2048, return_offsets_mapping=True,
              return_tensors=None)
    input_ids = enc["input_ids"]
    offsets = enc["offset_mapping"]
    labels = [-100] * len(input_ids)
    for span_start, span_end in assistant_spans:
        for tok_idx, (tok_start, tok_end) in enumerate(offsets):
            if tok_start >= span_end:
                break
            if tok_end <= span_start:
                continue
            if tok_idx < len(labels):
                labels[tok_idx] = input_ids[tok_idx]
    n_labelled = sum(1 for l in labels if l != -100)
    pct = 100.0 * n_labelled / len(input_ids) if input_ids else 0
    print(f"  total_tokens={len(input_ids)} labelled_tokens={n_labelled} "
          f"({pct:.1f}%)")
    print(f"  assistant_spans: {assistant_spans}")
    assert n_labelled > 0, "No tokens labelled -- loss masking is broken!"

    print()
    print("=== 4. Test collate_fn ===")
    samples = []
    with open(DATA_FILE) as f:
        for i, line in enumerate(f):
            if i >= 4:
                break
            traj = json.loads(line)
            conv = traj["conversation"]
            full_text, assistant_spans = conversation_to_text(conv)
            enc = tok(full_text, add_special_tokens=False, truncation=True,
                      max_length=2048, return_offsets_mapping=True,
                      return_tensors=None)
            ids = enc["input_ids"]
            offs = enc["offset_mapping"]
            labs = [-100] * len(ids)
            for sp_start, sp_end in assistant_spans:
                for ti, (ts, te) in enumerate(offs):
                    if ts >= sp_end:
                        break
                    if te <= sp_start:
                        continue
                    if ti < len(labs):
                        labs[ti] = ids[ti]
            samples.append({"input_ids": ids[:2048], "labels": labs[:2048]})

    batch = collate_fn(samples, tok, 2048)
    print(f"  input_ids shape: {batch['input_ids'].shape}")
    print(f"  attention_mask shape: {batch['attention_mask'].shape}")
    print(f"  labels shape: {batch['labels'].shape}")
    print(f"  labels non-(-100) count: "
          f"{(batch['labels'] != -100).sum().item()}")
    print(f"  attention_mask sum per sample: "
          f"{batch['attention_mask'].sum(dim=1).tolist()}")

    print()
    print("=== 5. Test WaveSFTDataset class ===")
    ds = WaveSFTDataset(DATA_FILE, tok, seq_len=2048)
    print(f"  Dataset size: {len(ds)}")
    sample = ds[0]
    print(f"  sample[0] input_ids len: {len(sample['input_ids'])}")
    print(f"  sample[0] labels len: {len(sample['labels'])}")
    print(f"  sample[0] labelled count: "
          f"{sum(1 for l in sample['labels'] if l != -100)}")
    assert len(sample["input_ids"]) == len(sample["labels"]) == 2048 or \
           len(sample["input_ids"]) <= 2048, "Length mismatch!"

    print()
    print("=== 6. Verify error-recovery trajectories exist ===")
    from collections import Counter
    tt_counts = Counter()
    with open(DATA_FILE) as f:
        for line in f:
            d = json.loads(line)
            tt_counts[d.get("trajectory_type", "unknown")] += 1
    print(f"  trajectory types: {dict(sorted(tt_counts.items()))}")
    assert "error_recovery" in tt_counts, "No error-recovery trajectories!"
    print(f"  error_recovery count: {tt_counts['error_recovery']}")

    print()
    print("=== ALL CPU DRY-RUN TESTS PASSED ===")


if __name__ == "__main__":
    main()

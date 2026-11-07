#!/usr/bin/env python3
"""baize_posttrain_build_eval_ngrams.py — Build n-gram set from 158 eval tasks
for cheat rate detection (red-line §5.2).

R22 (2026-11-07): During RL training, we need to detect if the model's
generated code contains memorized snippets from the 158 evaluation tasks.
This script extracts character-level n-grams from the eval tasks' test code
and canonical solutions, and saves them as a JSON set for the reward function
to use for overlap detection.

Usage:
    python3 baize_posttrain_build_eval_ngrams.py
    python3 baize_posttrain_build_eval_ngrams.py --ngram-size 8 --output eval_ngrams.json

Output: JSON file containing a list of unique n-gram strings.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys


def extract_ngrams(text: str, n: int = 8) -> set:
    """Extract character-level n-grams from text (normalized)."""
    if not text:
        return set()
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    if len(normalized) < n:
        return {normalized}
    return {normalized[i:i + n] for i in range(len(normalized) - n + 1)}


def build_eval_ngrams(eval_jsonl_path: str, ngram_size: int = 8) -> set:
    """Build n-gram set from the 158 eval tasks.

    Extracts from each task:
    - test_code (the assertion code)
    - canonical_solution (the reference solution)
    - prompt (the task description, for full coverage)
    """
    all_ngrams = set()
    n_tasks = 0

    if not os.path.exists(eval_jsonl_path):
        print(f"⚠️ Eval dataset not found: {eval_jsonl_path}", file=sys.stderr)
        return all_ngrams

    with open(eval_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
            except json.JSONDecodeError:
                continue

            n_tasks += 1

            # Extract test code
            test_code = task.get("test", "") or task.get("test_code", "")
            if test_code:
                all_ngrams |= extract_ngrams(test_code, ngram_size)

            # Extract canonical solution
            canon = task.get("canonical_solution", "")
            if canon:
                all_ngrams |= extract_ngrams(canon, ngram_size)

            # Extract prompt (task description)
            prompt = task.get("prompt", "")
            if prompt:
                # Only extract from the code parts of the prompt, not natural language
                code_blocks = re.findall(r"```python\n(.*?)```", prompt, re.DOTALL)
                for block in code_blocks:
                    all_ngrams |= extract_ngrams(block, ngram_size)

    return all_ngrams, n_tasks


def main():
    parser = argparse.ArgumentParser(description="Build eval n-grams for cheat rate detection")
    parser.add_argument("--eval-jsonl", default=os.path.expanduser(
        "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"),
        help="Path to the 158-task eval JSONL")
    parser.add_argument("--ngram-size", type=int, default=8, help="N-gram size (default: 8)")
    parser.add_argument("--output", default="eval_ngrams.json", help="Output JSON file path")
    args = parser.parse_args()

    print(f"Building {args.ngram_size}-grams from: {args.eval_jsonl}")
    ngrams, n_tasks = build_eval_ngrams(args.eval_jsonl, args.ngram_size)
    print(f"  Tasks processed: {n_tasks}")
    print(f"  Unique n-grams: {len(ngrams)}")

    # Save as JSON list (sets are not JSON serializable)
    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted(ngrams), f)
    print(f"  Saved to: {output_path}")
    print(f"  File size: {os.path.getsize(output_path)} bytes")

    # Print usage hint
    print(f"\nTo use in RL training:")
    print(f"  export CHEAT_EVAL_NGRAMS_PATH={output_path}")
    print(f"  bash baize_posttrain_rl_grpo.sh --reward-arm R2 --gpu-ids 0,1,2,3")


if __name__ == "__main__":
    main()

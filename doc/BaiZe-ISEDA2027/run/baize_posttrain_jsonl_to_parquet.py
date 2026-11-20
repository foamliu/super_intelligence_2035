#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_jsonl_to_parquet.py — Convert JSONL datasets to verl-compatible Parquet.

R10 (2026-11-07): verl requires Parquet format for both RL and SFT training.
This script converts the existing JSONL datasets:
  - RL synth tasks (rl_pyaether_synth_v2.jsonl) -> verl RLHF parquet
  - SFT corpus (sft_pyaether_corpus.jsonl) -> verl multi-turn SFT parquet

verl Data Format Requirements (from official docs + DeepWiki SDPO/verl):
  RLHF Dataset (PPO/GRPO):
    Required: prompt (list[dict] when return_raw_chat=True)
    Optional: reward_model (any, passed to reward fn), agent_name (str)
    For multi-turn tool calling: return_raw_chat=True is REQUIRED
    agent_name selects which tool config to use per sample
  Multi-turn SFT Dataset:
    Required: conversation (list[dict] of message turns)
    Config: prompt_dict_keys, response_dict_keys, use_conversation_format

Usage:
  python3 baize_posttrain_jsonl_to_parquet.py rl  -i rl_pyaether_synth_v2.jsonl  -o rl_pyaether_synth_v2.parquet
  python3 baize_posttrain_jsonl_to_parquet.py sft -i sft_pyaether_corpus.jsonl   -o sft_pyaether_corpus.parquet
  python3 baize_posttrain_jsonl_to_parquet.py rl  --dry-run
"""
import argparse, json, os, sys
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_rl_jsonl_to_parquet(input_path, output_path, dry_run=False):
    """Convert RL synth tasks JSONL -> verl RLHF parquet."""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("ERROR: pyarrow not installed. Install with: pip install pyarrow")
        return 1
    if not os.path.exists(input_path):
        print("ERROR: Input file not found: %s" % input_path); return 1

    records = []
    n_total = 0
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_total += 1
            task = json.loads(line)
            raw_prompt = task.get("prompt", "")
            chat_prompt = [{"role": "user", "content": (
                "You are an EDA automation assistant. Write a Python function "
                "that calls the specified PyAether API(s) and returns the result.\n\n"
                "You have access to the `run_eda_code` tool to execute code in the "
                "EDA sandbox. Use it to test your solution.\n\n" + raw_prompt)}]
            reward_model = {
                "test_code": task.get("test", ""),
                "canonical_solution": task.get("canonical_solution", ""),
                "entry_point": task.get("entry_point", ""),
                "metadata": json.dumps(task.get("metadata", {}), ensure_ascii=False),
            }
            records.append({"prompt": chat_prompt, "reward_model": reward_model,
                            "agent_name": "eda_sandbox"})

    print("  Read %d tasks, converted %d" % (n_total, len(records)))
    if dry_run:
        print("\n[DRY-RUN] Schema: prompt (list[dict]), reward_model (dict), agent_name (str)")
        print("  Total records: %d" % len(records))
        if records:
            s = records[0]
            print("  Sample prompt[0] role: %s" % s["prompt"][0]["role"])
            print("  Sample prompt[0] content[:120]: %s..." % s["prompt"][0]["content"][:120])
            print("  Sample reward_model keys: %s" % list(s["reward_model"].keys()))
            print("  Sample agent_name: %s" % s["agent_name"])
        return 0

    schema = pa.schema([
        pa.field("prompt", pa.list_(pa.struct([
            pa.field("role", pa.string()), pa.field("content", pa.string())]))),
        pa.field("reward_model", pa.struct([
            pa.field("test_code", pa.string()),
            pa.field("canonical_solution", pa.string()),
            pa.field("entry_point", pa.string()),
            pa.field("metadata", pa.string())])),
        pa.field("agent_name", pa.string())])
    table = pa.Table.from_pylist(records, schema=schema)
    pq.write_table(table, output_path, compression="snappy")
    sz = os.path.getsize(output_path)
    print("\n  Written: %s" % output_path)
    print("  Records: %d, File size: %d bytes (%.1f KB)" % (len(records), sz, sz / 1024))
    vt = pq.read_table(output_path)
    print("  Verification: read back %d rows, columns=%s" % (vt.num_rows, vt.column_names))
    return 0


def convert_sft_jsonl_to_parquet(input_path, output_path, dry_run=False):
    """Convert SFT corpus JSONL -> verl multi-turn SFT parquet."""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("ERROR: pyarrow not installed."); return 1
    if not os.path.exists(input_path):
        print("ERROR: Input file not found: %s" % input_path); return 1

    records = []
    n_total = 0
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_total += 1
            pair = json.loads(line)
            conversation = [
                {"role": "system", "content": (
                    "You are an EDA automation assistant specialized in PyAether API "
                    "usage. Write clean, correct Python code that calls the specified APIs.")},
                {"role": "user", "content": pair.get("prompt", "")},
                {"role": "assistant", "content": pair.get("completion", "")}]
            records.append({"conversation": conversation,
                            "pair_id": pair.get("pair_id", ""),
                            "type": pair.get("type", ""),
                            "api_used": json.dumps(pair.get("api_used", []), ensure_ascii=False),
                            "contamination_check": pair.get("contamination_check", "")})

    print("  Read %d SFT pairs, converted %d" % (n_total, len(records)))
    if dry_run:
        print("\n[DRY-RUN] Schema: conversation (list[dict]), pair_id, type, api_used, contamination_check")
        print("  Total records: %d" % len(records))
        if records:
            s = records[0]
            print("  Sample conversation turns: %d" % len(s["conversation"]))
            for i, msg in enumerate(s["conversation"]):
                preview = msg["content"][:80].replace("\n", " ")
                print("    [%d] %s: %s..." % (i, msg["role"], preview))
        return 0

    schema = pa.schema([
        pa.field("conversation", pa.list_(pa.struct([
            pa.field("role", pa.string()), pa.field("content", pa.string())]))),
        pa.field("pair_id", pa.string()),
        pa.field("type", pa.string()),
        pa.field("api_used", pa.string()),
        pa.field("contamination_check", pa.string())])
    table = pa.Table.from_pylist(records, schema=schema)
    pq.write_table(table, output_path, compression="snappy")
    sz = os.path.getsize(output_path)
    print("\n  Written: %s" % output_path)
    print("  Records: %d, File size: %d bytes (%.1f KB)" % (len(records), sz, sz / 1024))
    vt = pq.read_table(output_path)
    print("  Verification: read back %d rows, columns=%s" % (vt.num_rows, vt.column_names))
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="BaiZe Stage(ii) JSONL -> verl Parquet converter (R10)")
    sub = parser.add_subparsers(dest="mode", required=True)
    rl_p = sub.add_parser("rl", help="Convert RL synth tasks to verl RLHF parquet")
    rl_p.add_argument("--input", "-i", required=True)
    rl_p.add_argument("--output", "-o", required=True)
    rl_p.add_argument("--dry-run", action="store_true")
    sft_p = sub.add_parser("sft", help="Convert SFT corpus to verl multi-turn SFT parquet")
    sft_p.add_argument("--input", "-i", required=True)
    sft_p.add_argument("--output", "-o", required=True)
    sft_p.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print("=" * 60)
    print("BaiZe Stage(ii) JSONL -> verl Parquet Converter (R10)")
    print("=" * 60)
    if args.mode == "rl":
        print("\n[RL] Converting: %s -> %s" % (args.input, args.output))
        return convert_rl_jsonl_to_parquet(args.input, args.output, args.dry_run)
    elif args.mode == "sft":
        print("\n[SFT] Converting: %s -> %s" % (args.input, args.output))
        return convert_sft_jsonl_to_parquet(args.input, args.output, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""baize_posttrain_gen_sft_corpus.py — PyAether SFT 语料合成器

从 API_INFO_MERGED_V3.json (8463 API) 生成 SFT 训练对：
  S1: doc-to-code (API 文档 → 调用代码)
  S2: api-lookup (任务描述 → 选择并调用正确 API)
  S3: multi-api-chain (多步任务 → API 链式调用)
  S4: error-recovery (错误代码 → 修正，基于 R4 五分类法)

污染隔离：所有生成对走 contamination gate（158 题黑名单）。
零 GPU；Python 3.8 兼容。

用法:
  python3 baize_posttrain_gen_sft_corpus.py --dry-run --max-pairs 100
  python3 baize_posttrain_gen_sft_corpus.py --output sft_pyaether_corpus.jsonl
"""
import argparse
import json
import os
import re
import sys
import hashlib
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_DB_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
EVAL_DATASET = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
)
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "sft_pyaether_corpus.jsonl")


def load_api_db(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_eval_apis(path):
    """Load 158 eval task API names for contamination isolation."""
    apis = set()
    if not os.path.exists(path):
        return apis
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                for api in task.get("metadata", {}).get("apis_used", []):
                    apis.add(api)
            except (json.JSONDecodeError, KeyError):
                continue
    return apis


def extract_signature(desc):
    """Extract function signature from markdown description."""
    m = re.search(r"`(\w+)\(([^)]*)\)`", desc)
    if m:
        return m.group(0), m.group(1), m.group(2)
    return None, None, None


def gen_s1_doc_to_code(api_name, api_info, eval_apis):
    """S1: API doc -> calling code (doc-to-code pair)."""
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    desc = api_info.get("api_descriptions", "")
    if len(desc) < 30:
        return None
    _, func_name, _ = extract_signature(desc)
    if not func_name:
        func_name = api_name
    prompt = (
        "You are an EDA automation assistant. Read the following PyAether API "
        "documentation and write a Python function that calls this API.\n\n"
        "## API Documentation\n\n"
        f"{desc[:800]}\n\n"
        "## Task\n\n"
        f"Write a Python function that calls `{full_name}` and returns its result. "
        f"Use `import pyAether as pyScript` and call via `pyScript.{func_name}`."
    )
    completion = (
        f"```python\nimport pyAether as pyScript\n\n"
        f"def call_{func_name.lower()}():\n"
        f'    """Call {full_name} and return the result."""\n'
        f"    result = pyScript.{func_name}()\n"
        f"    return result\n```"
    )
    return {
        "pair_id": f"S1-{hashlib.sha256(full_name.encode()).hexdigest()[:12]}",
        "type": "S1_doc_to_code", "prompt": prompt, "completion": completion,
        "api_used": [full_name], "source": full_name,
        "contamination_check": "passed",
    }


def gen_s2_api_lookup(api_name, api_info, eval_apis, category_apis):
    """S2: task description -> select and call correct API."""
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    desc = api_info.get("api_descriptions", "")
    category = api_info.get("category", "unknown")
    _, func_name, _ = extract_signature(desc)
    if not func_name:
        func_name = api_name
    distractors = [
        a for a in category_apis.get(category, [])
        if a != full_name and a not in eval_apis
    ][:3]
    if not distractors:
        return None
    first_line = desc[:200].split("\n")[0]
    prompt = (
        "You are an EDA automation assistant. Select the correct PyAether API "
        "and write code to accomplish the task.\n\n## Task\n\n"
        f"Use the PyAether API to accomplish: {first_line}\n\n"
        "## Available APIs (choose one)\n\n"
        f"1. {full_name}\n"
        + "\n".join(f"{i+2}. {d}" for i, d in enumerate(distractors))
        + "\n\n## Write your solution"
    )
    completion = (
        f"The correct API is `{full_name}`.\n\n"
        f"```python\nimport pyAether as pyScript\n\n"
        f"def solve():\n    result = pyScript.{func_name}()\n    return result\n```"
    )
    return {
        "pair_id": f"S2-{hashlib.sha256(full_name.encode()).hexdigest()[:12]}",
        "type": "S2_api_lookup", "prompt": prompt, "completion": completion,
        "api_used": [full_name], "source": full_name,
        "contamination_check": "passed",
    }


def gen_s3_multi_api_chain(api_list, eval_apis):
    """S3: multi-step task -> API chain."""
    clean = [a for a in api_list if a not in eval_apis]
    if len(clean) < 2:
        return None
    apis_info = []
    for full_name in clean[:3]:
        parts = full_name.split(".")
        func_name = parts[-1] if len(parts) > 1 else full_name
        apis_info.append((full_name, func_name))
    prompt = (
        "You are an EDA automation assistant. Write a Python function that chains "
        "the following PyAether API calls.\n\n## APIs to chain\n\n"
        + "\n".join(f"{i+1}. `{a[0]}`" for i, a in enumerate(apis_info))
        + "\n\n## Write a function that calls all of these in sequence"
    )
    calls = "\n".join(f"    r{i} = pyScript.{a[1]}()" for i, a in enumerate(apis_info))
    ret = f"    return [{', '.join(f'r{i}' for i in range(len(apis_info)))}]"
    completion = (
        f"```python\nimport pyAether as pyScript\n\n"
        f"def chain_calls():\n"
        f'    """Chain {len(apis_info)} API calls."""\n'
        f"{calls}\n{ret}\n```"
    )
    return {
        "pair_id": f"S3-{hashlib.sha256(('+'.join(clean[:3])).encode()).hexdigest()[:12]}",
        "type": "S3_multi_api_chain", "prompt": prompt, "completion": completion,
        "api_used": [a[0] for a in apis_info], "source": "+".join(clean[:3]),
        "contamination_check": "passed",
    }


def gen_s4_error_recovery(api_name, api_info, eval_apis):
    """S4: buggy code -> fix (R4 SYN error type)."""
    full_name = api_info.get("api_name", api_name)
    if full_name in eval_apis:
        return None
    _, func_name, _ = extract_signature(api_info.get("api_descriptions", ""))
    if not func_name:
        func_name = api_name
    prompt = (
        "You are an EDA automation assistant. The following code has a bug. "
        "Identify and fix it.\n\n## Buggy code\n\n```python\n"
        f"def call_api():\n    result = pyScript.{func_name}()\n    return result\n```\n\n"
        "## Error\n\nNameError: name 'pyScript' is not defined\n\n## Fix the code"
    )
    completion = (
        "The error is a missing import. `pyScript` is not imported.\n\n"
        f"```python\nimport pyAether as pyScript\n\n"
        f"def call_api():\n    result = pyScript.{func_name}()\n    return result\n```"
    )
    return {
        "pair_id": f"S4-{hashlib.sha256(full_name.encode()).hexdigest()[:12]}",
        "type": "S4_error_recovery", "prompt": prompt, "completion": completion,
        "api_used": [full_name], "source": full_name,
        "contamination_check": "passed", "error_type": "SYN_missing_import",
    }


def main():
    parser = argparse.ArgumentParser(description="Generate PyAether SFT corpus")
    parser.add_argument("--api-db", default=API_DB_PATH)
    parser.add_argument("--eval-dataset", default=EVAL_DATASET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--max-pairs", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--types", default="S1,S2,S3,S4")
    args = parser.parse_args()

    print(f"Loading API DB from {args.api_db}...")
    api_db = load_api_db(args.api_db)
    print(f"  Loaded {len(api_db)} APIs")

    print(f"Loading eval APIs for contamination isolation...")
    eval_apis = load_eval_apis(args.eval_dataset)
    print(f"  Found {len(eval_apis)} eval API names (blacklist)")

    category_apis = defaultdict(list)
    for k, v in api_db.items():
        cat = v.get("category", "unknown")
        full_name = v.get("api_name", k)
        category_apis[cat].append(full_name)

    requested_types = set(args.types.split(","))
    pairs = []
    counts = defaultdict(int)

    if "S1" in requested_types:
        for k, v in api_db.items():
            pair = gen_s1_doc_to_code(k, v, eval_apis)
            if pair:
                pairs.append(pair)
                counts["S1"] += 1
                if args.max_pairs and len(pairs) >= args.max_pairs:
                    break

    if "S2" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for k, v in api_db.items():
            pair = gen_s2_api_lookup(k, v, eval_apis, category_apis)
            if pair:
                pairs.append(pair)
                counts["S2"] += 1
                if args.max_pairs and len(pairs) >= args.max_pairs:
                    break

    if "S3" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for cat, apis in category_apis.items():
            if len(apis) >= 3:
                pair = gen_s3_multi_api_chain(apis, eval_apis)
                if pair:
                    pairs.append(pair)
                    counts["S3"] += 1
                    if args.max_pairs and len(pairs) >= args.max_pairs:
                        break

    if "S4" in requested_types and (not args.max_pairs or len(pairs) < args.max_pairs):
        for k, v in api_db.items():
            if v.get("api_type") == "function":
                pair = gen_s4_error_recovery(k, v, eval_apis)
                if pair:
                    pairs.append(pair)
                    counts["S4"] += 1
                    if args.max_pairs and len(pairs) >= args.max_pairs:
                        break

    contaminated = [p for p in pairs if p.get("contamination_check") != "passed"]
    if contaminated:
        print(f"  WARNING: {len(contaminated)} contaminated pairs! Removing.")
        pairs = [p for p in pairs if p.get("contamination_check") == "passed"]

    print(f"\n=== SFT Corpus Generation Results ===")
    print(f"  Total pairs: {len(pairs)}")
    for t, c in sorted(counts.items()):
        print(f"    {t}: {c}")
    print(f"  Contaminated removed: {len(contaminated)}")
    unique_apis = set(a for p in pairs for a in p.get("api_used", []))
    print(f"  Unique APIs covered: {len(unique_apis)}")

    if args.dry_run:
        print("\n[dry-run] Not writing output file.")
        return

    with open(args.output, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"\n  Written to: {args.output}")
    print(f"  File size: {os.path.getsize(args.output)} bytes")


if __name__ == "__main__":
    main()

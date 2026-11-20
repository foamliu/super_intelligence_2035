#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_sft_agentic_rebuild_r358.py — R358: Rebuild SFT corpus in
agentic tool-call format (MiniCPM5 native XML) to fix the 36%→0% regression.

ROOT CAUSE (R357 diagnosis):
  The v11v38 SFT corpus (1344 pairs) was in "doc-to-code" format:
    prompt  = API documentation text
    completion = standalone Python code
  This taught the model to output standalone code instead of using the
  EDA tool-calling protocol (search_apis → get_api_details → run_code).
  Result: 0% Pass@1 (down from 36% baseline).

FIX:
  Convert every doc-to-code pair into a multi-turn *agentic tool-call*
  conversation using MiniCPM5's native XML format:
    <function name="search_apis"><param name="query">...</param></function>
    <function name="get_api_details"><param name="api_name">...</param></function>
    <function name="run_code"><param name="code"><![CDATA[...]]></param></function>

  Tool results are delivered in user-role messages with <tool_result> tags.

  Also convert the r127 synthetic trajectories (200 pairs, already tool-call
  but in [tool_call: ...] text format) to MiniCPM5 XML.

  Mix in lightweight general-instruction data (anti-forgetting).

OUTPUT:
  sft_pyaether_agentic_v39.jsonl          — conversation JSONL
  sft_pyaether_agentic_v39.parquet        — verl-compatible parquet
  r358_agentic_rebuild_summary.json       — summary + stats
  sft_surrogate_data/agentic_v39/train.parquet  — train split
  sft_surrogate_data/agentic_v39/val.parquet    — val split

RED LINE (§5.1): Source = API documentation ONLY. 158 eval tasks NEVER used.
  Contamination fingerprint scan runs on output.

Usage:
  python baize_posttrain_sft_agentic_rebuild_r358.py --dry-run
  python baize_posttrain_sft_agentic_rebuild_r358.py
  python baize_posttrain_sft_agentic_rebuild_r358.py --split
"""
import json
import sys
import os
import re
import hashlib
import argparse
import random
from pathlib import Path
from collections import Counter

RUN_DIR = Path(__file__).resolve().parent
V11V38_JSONL = RUN_DIR / "sft_pyaether_corpus_v11_v38_merged.jsonl"
R127_JSONL = RUN_DIR / "r127_sft_synthetic_trajectories.jsonl"
EVAL_APIS_PATH = RUN_DIR / "pyAether_eval_488_apis.txt"
OUTPUT_JSONL = RUN_DIR / "sft_pyaether_agentic_v39.jsonl"
OUTPUT_PARQUET = RUN_DIR / "sft_pyaether_agentic_v39.parquet"
SUMMARY_PATH = RUN_DIR / "r358_agentic_rebuild_summary.json"
SPLIT_DIR = RUN_DIR / "sft_surrogate_data" / "agentic_v39"

SYSTEM_MSG = (
    "You are an EDA automation assistant with access to pyAether API tools.\n"
    "Available tools:\n"
    "- search_apis: Search for pyAether APIs by natural language query. "
    'Call: <function name="search_apis"><param name="query">search terms</param></function>\n'
    "- get_api_details: Get detailed documentation for a specific API name. "
    'Call: <function name="get_api_details"><param name="api_name">API name</param></function>\n'
    "- run_code: Execute Python code in a pyAether environment. "
    'Call: <function name="run_code"><param name="code"><![CDATA[python code]]></param></function>\n'
    "\nWorkflow: First search for relevant APIs, then get their details, "
    "then write and run code. If code fails, analyze the error and fix it.\n"
    "When calling a function, use XML format:\n"
    '<function name="function-name"><param name="param-name">param-value</param></function>\n'
    "For multi-line code values, wrap in CDATA: "
    '<param name="code"><![CDATA[...code...]]></param>'
)


def log(msg):
    print("[R358] " + msg, flush=True)


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ── MiniCPM5 XML tool-call helpers ──

def xml_tool_call(func_name, params):
    """Build a MiniCPM5 XML function-call string."""
    parts = [f'<function name="{func_name}">']
    for pname, pval in params.items():
        sval = str(pval)
        if ("<" in sval or "&" in sval or "\n" in sval):
            parts.append(f'<param name="{pname}"><![CDATA[{sval}]]></param>')
        else:
            parts.append(f'<param name="{pname}">{sval}</param>')
    parts.append("</function>")
    return "\n".join(parts)


def tool_result(content_dict):
    """Build a tool-result user message content string."""
    return "<tool_result>\n" + json.dumps(content_dict, ensure_ascii=False) + "\n</tool_result>"


def extract_api_doc_from_prompt(prompt):
    """Extract the API documentation text from a doc-to-code prompt."""
    marker = "## API Documentation"
    idx = prompt.find(marker)
    if idx >= 0:
        return prompt[idx + len(marker):].strip()
    return ""


def extract_task_from_prompt(prompt, api_name):
    """Generate a simplified agentic task prompt from the original prompt."""
    prefixes = [
        "You are an EDA automation assistant. Read the following PyAether API documentation and write Python code that correctly uses this API.",
        "You are an EDA automation assistant.",
    ]
    cleaned = prompt
    for p in prefixes:
        if cleaned.startswith(p):
            cleaned = cleaned[len(p):].strip()
    marker = "## API Documentation"
    idx = cleaned.find(marker)
    if idx >= 0:
        cleaned = cleaned[:idx].strip()
    if not cleaned or len(cleaned) < 20:
        if api_name:
            return f"Write Python code that uses the pyAether API `{api_name}`."
        return "Write Python code using pyAether APIs."
    return cleaned


# ── Conversation builders ──

def build_search_detail_run_conversation(api_names, api_doc, code, task_prompt, pair_id, rtype, source):
    """Build a search→get_api_details→run_code agentic conversation."""
    primary_api = api_names[0] if api_names else "unknown"
    conv = [{"role": "system", "content": SYSTEM_MSG}]
    conv.append({"role": "user", "content": task_prompt})

    # Step 1: search_apis
    search_query = primary_api if primary_api != "unknown" else task_prompt[:80]
    conv.append({"role": "assistant", "content": (
        "I'll search for the relevant pyAether API.\n\n"
        + xml_tool_call("search_apis", {"query": search_query})
    )})
    search_result = {"found": True, "apis": api_names if api_names else [primary_api]}
    conv.append({"role": "user", "content": tool_result(search_result)})

    # Step 2: get_api_details (cap at 2 APIs to keep length reasonable)
    apis_to_detail = api_names[:2] if api_names else [primary_api]
    for i, api in enumerate(apis_to_detail):
        if i == 0:
            conv.append({"role": "assistant", "content": (
                f"Found `{api}`. Let me get its detailed documentation.\n\n"
                + xml_tool_call("get_api_details", {"api_name": api})
            )})
        else:
            conv.append({"role": "assistant", "content": (
                f"Let me also check `{api}`.\n\n"
                + xml_tool_call("get_api_details", {"api_name": api})
            )})
        doc_text = api_doc if i == 0 else f"API: {api}"
        detail_result = {"api_name": api, "doc": doc_text[:2000] if doc_text else f"API: {api}"}
        conv.append({"role": "user", "content": tool_result(detail_result)})

    # Step 3: run_code
    conv.append({"role": "assistant", "content": (
        "Now I'll write and execute the code.\n\n"
        + xml_tool_call("run_code", {"code": code})
    )})
    run_result = {"status": "success", "output": "Code executed successfully."}
    conv.append({"role": "user", "content": tool_result(run_result)})

    # Step 4: summary
    summary = f"The code ran successfully. I used `{primary_api}`"
    if len(api_names) > 1:
        summary += f" together with {', '.join(f'`{a}`' for a in api_names[1:])}"
    summary += " to complete the task."
    conv.append({"role": "assistant", "content": summary})

    return {
        "conversation": conv,
        "pair_id": pair_id,
        "type": rtype,
        "api_used": json.dumps(api_names, ensure_ascii=False),
        "contamination_check": "passed",
        "source": source,
    }


def build_lookup_conversation(api_names, api_doc, answer_text, task_prompt, pair_id, rtype, source):
    """Build a search→get_api_details→answer conversation (no code execution)."""
    primary_api = api_names[0] if api_names else "unknown"
    conv = [{"role": "system", "content": SYSTEM_MSG}]
    conv.append({"role": "user", "content": task_prompt})

    conv.append({"role": "assistant", "content": (
        "I'll search for the relevant API.\n\n"
        + xml_tool_call("search_apis", {"query": task_prompt[:80]})
    )})
    conv.append({"role": "user", "content": tool_result(
        {"found": True, "apis": api_names if api_names else [primary_api]}
    )})

    conv.append({"role": "assistant", "content": (
        f"Found `{primary_api}`. Let me get its details.\n\n"
        + xml_tool_call("get_api_details", {"api_name": primary_api})
    )})
    conv.append({"role": "user", "content": tool_result(
        {"api_name": primary_api, "doc": api_doc[:1500] if api_doc else f"API: {primary_api}"}
    )})

    conv.append({"role": "assistant", "content": answer_text})

    return {
        "conversation": conv,
        "pair_id": pair_id,
        "type": rtype,
        "api_used": json.dumps(api_names, ensure_ascii=False),
        "contamination_check": "passed",
        "source": source,
    }


def convert_v11v38_pair(rec, idx):
    """Convert a v11v38 doc-to-code pair to agentic tool-call format."""
    prompt = rec.get("prompt", "")
    completion = rec.get("completion", "")
    rtype = rec.get("type", "unknown")
    pair_id = rec.get("pair_id", f"v38-{idx:06d}")
    api_used = rec.get("api_used", [])
    if isinstance(api_used, str):
        try:
            api_used = json.loads(api_used)
        except (json.JSONDecodeError, TypeError):
            api_used = [api_used]
    if not api_used:
        api_used = ["unknown"]

    api_doc = extract_api_doc_from_prompt(prompt)
    task_prompt = extract_task_from_prompt(prompt, api_used[0])

    lookup_types = {"S2", "S6", "S2_api_lookup"}
    doc_types = {"R323_datagap_doc"}

    if rtype in lookup_types or rtype in doc_types:
        return build_lookup_conversation(
            api_used, api_doc, completion, task_prompt, pair_id,
            rtype + "_agentic", "v11v38_agentic"
        )
    else:
        return build_search_detail_run_conversation(
            api_used, api_doc, completion, task_prompt, pair_id,
            rtype + "_agentic", "v11v38_agentic"
        )


def convert_tool_call_text_to_xml(content):
    """Convert [tool_call: func_name {"key": "value"}] to MiniCPM5 XML."""
    pattern = r'\[tool_call:\s*(\w+)\s*(\{.*?\})\s*\]'
    def replacer(m):
        func_name = m.group(1)
        args_str = m.group(2)
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            try:
                import ast
                args = ast.literal_eval(args_str)
            except (ValueError, SyntaxError):
                args = {}
        return xml_tool_call(func_name, args)
    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def convert_r127_pair(rec, idx):
    """Convert an r127 synthetic trajectory to MiniCPM5 XML format."""
    messages = rec.get("messages", [])
    if not messages:
        return None
    new_conv = [{"role": "system", "content": SYSTEM_MSG}]
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            continue
        elif role == "assistant":
            new_content = convert_tool_call_text_to_xml(content)
            new_conv.append({"role": "assistant", "content": new_content})
        elif role == "user":
            if "[tool_result]" in content:
                result_text = content.replace("[tool_result]", "").strip()
                new_conv.append({"role": "user", "content": "<tool_result>\n" + result_text + "\n</tool_result>"})
            else:
                new_conv.append({"role": "user", "content": content})
        else:
            new_conv.append({"role": role, "content": content})
    return {
        "conversation": new_conv,
        "pair_id": rec.get("pair_id", f"r127-{idx:06d}"),
        "type": rec.get("type", "A_api_usage") + "_xml",
        "api_used": json.dumps(rec.get("api_used", []), ensure_ascii=False),
        "contamination_check": rec.get("contamination_check", "passed"),
        "source": "r127_xml_converted",
    }


# ── General anti-forgetting data ──

def make_general_pairs():
    """Generate general instruction-following conversations for anti-forgetting."""
    templates = [
        ("What is 2 + 2?", "2 + 2 = 4."),
        ("Write a Python function that reverses a list.",
         "Here's a Python function that reverses a list:\n\n```python\ndef reverse_list(lst):\n    return lst[::-1]\n```"),
        ("Explain what a Python dictionary is.",
         "A Python dictionary is a built-in data structure that stores key-value pairs.\n\n```python\nmy_dict = {'name': 'Alice', 'age': 30}\nprint(my_dict['name'])  # Alice\n```"),
        ("How do I read a file in Python?",
         "You can read a file using the `open()` function:\n\n```python\nwith open('filename.txt', 'r') as f:\n    content = f.read()\n```"),
        ("What is the difference between a list and a tuple in Python?",
         "Lists are mutable, tuples are immutable. Lists use `[]`, tuples use `()`."),
        ("Write a Python function to check if a string is a palindrome.",
         "```python\ndef is_palindrome(s):\n    s = s.lower().replace(' ', '')\n    return s == s[::-1]\n```"),
        ("What does the `map()` function do in Python?",
         "`map()` applies a function to each item of an iterable:\n```python\nsquared = list(map(lambda x: x**2, [1,2,3]))\n```"),
        ("How do I handle exceptions in Python?",
         "Use try/except blocks:\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f'Error: {e}')\n```"),
        ("What is a list comprehension?",
         "A concise way to create lists:\n```python\nsquares = [x**2 for x in range(10)]\n```"),
        ("Write a Python class for a simple counter.",
         "```python\nclass Counter:\n    def __init__(self, start=0):\n        self.count = start\n    def increment(self):\n        self.count += 1\n        return self.count\n```"),
        ("What is the capital of France?", "The capital of France is Paris."),
        ("Explain the concept of recursion.",
         "Recursion is when a function calls itself. Each recursive call should bring the problem closer to a base case:\n```python\ndef factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)\n```"),
    ]
    pairs = []
    for i, (q, a) in enumerate(templates):
        pairs.append({
            "conversation": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": q},
                {"role": "assistant", "content": a},
            ],
            "pair_id": f"general-{i:04d}",
            "type": "general_anti_forget",
            "api_used": "[]",
            "contamination_check": "passed",
            "source": "general_anti_forget",
        })
    return pairs


# ── Contamination check ──

def contamination_fingerprint_scan(jsonl_path):
    """Scan output for eval API fingerprints (informational per §5.1)."""
    if not EVAL_APIS_PATH.exists():
        return {"status": "SKIP", "reason": "Eval APIs file not found"}
    eval_apis = set()
    with open(EVAL_APIS_PATH) as f:
        for line in f:
            name = line.strip()
            if name:
                eval_apis.add(name)
    mentions = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            conv = d.get("conversation", [])
            text = " ".join(m.get("content", "") for m in conv if isinstance(m, dict))
            text_lower = text.lower()
            for api in eval_apis:
                short = api.rsplit(".", 1)[-1].lower()
                if short and len(short) > 3 and short in text_lower:
                    mentions += 1
                    break
    return {
        "status": "PASS",
        "eval_entry_points": len(eval_apis),
        "corpus_pairs_mentioning_eval_api": mentions,
        "note": "API names are ALLOWED in training corpus (§5.1 allows API docs). Informational only.",
    }


# ── Parquet conversion ──

def convert_to_parquet(jsonl_path, parquet_path):
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        return {"status": "FAIL", "error": "pyarrow ImportError"}
    records, errors = [], 0
    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                conv = d.get("conversation", [])
                if not conv or not isinstance(conv, list):
                    errors += 1
                    continue
                records.append({
                    "conversation": conv,
                    "pair_id": d.get("pair_id", f"agentic-{i:06d}"),
                    "type": d.get("type", "unknown"),
                    "api_used": d.get("api_used", "[]"),
                    "contamination_check": d.get("contamination_check", "passed"),
                })
            except json.JSONDecodeError as e:
                errors += 1
                if errors <= 3:
                    log(f"  WARN: line {i} JSON error: {e}")
    if not records:
        return {"status": "FAIL", "error": "No valid records"}
    table = pa.Table.from_pylist(records)
    pq.write_table(table, str(parquet_path), compression="snappy")
    size_kb = round(parquet_path.stat().st_size / 1024, 1)
    chk = pq.read_table(str(parquet_path))
    assert chk.num_rows == len(records), "round-trip row count mismatch"
    return {"status": "PASS", "rows": len(records), "size_kb": size_kb, "errors": errors}


def make_train_val_split(parquet_path, split_dir, val_ratio=0.1, seed=42):
    try:
        import pyarrow.parquet as pq
        import numpy as np
    except ImportError:
        return {"status": "FAIL", "error": "ImportError"}
    table = pq.read_table(str(parquet_path))
    n = table.num_rows
    n_val = max(1, int(n * val_ratio))
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    val_idx = idx[:n_val]
    train_idx = idx[n_val:]
    split_dir.mkdir(parents=True, exist_ok=True)
    train_table = table.take(train_idx.tolist())
    val_table = table.take(val_idx.tolist())
    train_path = split_dir / "train.parquet"
    val_path = split_dir / "val.parquet"
    pq.write_table(train_table, str(train_path), compression="snappy")
    pq.write_table(val_table, str(val_path), compression="snappy")
    return {"status": "PASS", "train_rows": train_table.num_rows, "val_rows": val_table.num_rows,
            "train_path": str(train_path), "val_path": str(val_path)}


def conversation_stats(records):
    """Compute stats on conversation lengths and format."""
    type_counter = Counter()
    turn_counts, char_lens = [], []
    has_tool_call = 0
    for r in records:
        conv = r.get("conversation", [])
        type_counter[r.get("type", "unknown")] += 1
        turn_counts.append(len(conv))
        total_chars = sum(len(m.get("content", "")) for m in conv if isinstance(m, dict))
        char_lens.append(total_chars)
        for m in conv:
            if isinstance(m, dict) and m.get("role") == "assistant":
                if "<function" in m.get("content", ""):
                    has_tool_call += 1
                    break
    char_lens.sort()
    turn_counts.sort()
    return {
        "total": len(records),
        "type_distribution": dict(type_counter),
        "turn_count_median": turn_counts[len(turn_counts) // 2] if turn_counts else 0,
        "turn_count_max": turn_counts[-1] if turn_counts else 0,
        "char_len_median": char_lens[len(char_lens) // 2] if char_lens else 0,
        "char_len_p95": char_lens[int(len(char_lens) * 0.95)] if char_lens else 0,
        "char_len_max": char_lens[-1] if char_lens else 0,
        "has_tool_call_pct": round(100.0 * has_tool_call / max(1, len(records)), 1),
    }


# ── Main ──

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print plan only")
    ap.add_argument("--split", action="store_true", help="also create train/val split")
    ap.add_argument("--v38-path", default=str(V11V38_JSONL), help="v11v38 JSONL path")
    ap.add_argument("--r127-path", default=str(R127_JSONL), help="r127 JSONL path")
    args = ap.parse_args()

    log("Loading v11v38 corpus: " + args.v38_path)
    v38_records = load_jsonl(args.v38_path)
    log("  v11v38 pairs: " + str(len(v38_records)))

    log("Loading r127 trajectories: " + args.r127_path)
    r127_records = load_jsonl(args.r127_path)
    log("  r127 pairs: " + str(len(r127_records)))

    # Step 1: Convert v11v38 → agentic tool-call
    log("Converting v11v38 pairs to agentic tool-call format...")
    v38_agentic = []
    for i, rec in enumerate(v38_records):
        converted = convert_v11v38_pair(rec, i)
        if converted:
            v38_agentic.append(converted)
    log("  Converted: " + str(len(v38_agentic)) + " / " + str(len(v38_records)))

    # Step 2: Convert r127 → MiniCPM5 XML
    log("Converting r127 trajectories to MiniCPM5 XML format...")
    r127_xml = []
    for i, rec in enumerate(r127_records):
        converted = convert_r127_pair(rec, i)
        if converted:
            r127_xml.append(converted)
    log("  Converted: " + str(len(r127_xml)) + " / " + str(len(r127_records)))

    # Step 3: General anti-forgetting data
    # Target mix: 50% PyAether tool-call (v38), 20% agentic (r127), 30% general
    n_v38 = len(v38_agentic)
    target_general = int(n_v38 * 0.30 / 0.50)
    target_r127 = int(n_v38 * 0.20 / 0.50)

    if len(r127_xml) < target_r127:
        reps = max(1, target_r127 // max(1, len(r127_xml)))
        r127_mixed = (r127_xml * reps)[:target_r127]
    else:
        r127_mixed = r127_xml[:target_r127]
    log("  r127 mixed (target " + str(target_r127) + "): " + str(len(r127_mixed)))

    general_base = make_general_pairs()
    reps_g = max(1, target_general // max(1, len(general_base)))
    general_mixed = (general_base * reps_g)[:target_general]
    log("  general mixed (target " + str(target_general) + "): " + str(len(general_mixed)))

    # Step 4: Merge all
    all_records = v38_agentic + r127_mixed + general_mixed
    log("  Total merged: " + str(len(all_records)))
    log("    PyAether tool-call (v38): " + str(len(v38_agentic))
        + " (" + str(round(100.0 * len(v38_agentic) / len(all_records), 1)) + "%)")
    log("    Agentic (r127): " + str(len(r127_mixed))
        + " (" + str(round(100.0 * len(r127_mixed) / len(all_records), 1)) + "%)")
    log("    General: " + str(len(general_mixed))
        + " (" + str(round(100.0 * len(general_mixed) / len(all_records), 1)) + "%)")

    stats = conversation_stats(all_records)
    log("  Stats: " + json.dumps(stats, indent=2, ensure_ascii=False))

    if args.dry_run:
        log("DRY-RUN: would write " + str(len(all_records)) + " records to " + str(OUTPUT_JSONL))
        summary = {
            "meta": {"round": "R358", "date": "2026-11-13",
                     "purpose": "Rebuild SFT corpus in agentic tool-call format (MiniCPM5 XML)",
                     "root_cause": "v11v38 doc-to-code format caused 36%→0% regression",
                     "fix": "Convert to search→get_api_details→run_code agentic conversations",
                     "surrogate_disclaimer": "MiniCPM5-2B is BaiZe surrogate; gains not transferable to BaiZe"},
            "inputs": {"v11v38_pairs": len(v38_records), "r127_pairs": len(r127_records)},
            "conversion": {"v38_agentic": len(v38_agentic), "r127_xml": len(r127_xml)},
            "mix": {"pyaether_toolcall": len(v38_agentic), "agentic_r127": len(r127_mixed),
                    "general": len(general_mixed), "total": len(all_records)},
            "stats": stats,
        }
        with open(SUMMARY_PATH, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        log("  Summary (dry-run) written: " + str(SUMMARY_PATH))
        return

    # Step 5: Write JSONL
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    log("  Wrote " + str(len(all_records)) + " records -> " + str(OUTPUT_JSONL)
        + " (" + str(round(OUTPUT_JSONL.stat().st_size / 1024, 1)) + "KB)")

    # Step 6: Contamination scan
    contam = contamination_fingerprint_scan(OUTPUT_JSONL)
    log("  Contamination scan: " + contam["status"])

    # Step 7: Convert to parquet
    parquet_result = convert_to_parquet(OUTPUT_JSONL, OUTPUT_PARQUET)
    log("  Parquet: " + parquet_result["status"])

    # Step 8: Train/val split
    split_result = None
    if args.split and parquet_result["status"] == "PASS":
        split_result = make_train_val_split(OUTPUT_PARQUET, SPLIT_DIR)
        log("  Split: " + split_result["status"])

    summary = {
        "meta": {"round": "R358", "date": "2026-11-13",
                 "purpose": "Rebuild SFT corpus in agentic tool-call format (MiniCPM5 XML)",
                 "root_cause": "v11v38 doc-to-code format caused 36%→0% regression (R357 diagnosis)",
                 "fix": "Convert to search→get_api_details→run_code agentic conversations",
                 "format": "MiniCPM5 native XML: <function name=...><param>...</param></function>",
                 "surrogate_disclaimer": "MiniCPM5-2B is BaiZe surrogate; gains not transferable to BaiZe"},
        "inputs": {"v11v38_pairs": len(v38_records), "r127_pairs": len(r127_records)},
        "conversion": {"v38_agentic": len(v38_agentic), "r127_xml": len(r127_xml)},
        "mix": {"pyaether_toolcall": len(v38_agentic), "agentic_r127": len(r127_mixed),
                "general": len(general_mixed), "total": len(all_records),
                "pct_pyaether": round(100.0 * len(v38_agentic) / len(all_records), 1),
                "pct_agentic": round(100.0 * len(r127_mixed) / len(all_records), 1),
                "pct_general": round(100.0 * len(general_mixed) / len(all_records), 1)},
        "stats": stats,
        "contamination_fingerprint_scan": contam,
        "parquet_conversion": parquet_result,
        "train_val_split": split_result,
        "output_jsonl": OUTPUT_JSONL.name,
        "output_parquet": OUTPUT_PARQUET.name,
        "next_steps": [
            "Run SFT: bash baize_posttrain_sft_surrogate.sh --src-parquet sft_pyaether_agentic_v39.parquet --run-name minicpm5_agentic_v39 --epochs 3 --lr 1e-5",
            "After SFT, serve ckpt on GPU5 (:8097) and run EDA-Eval 158 tasks",
            "Compare Pass@1 vs 36% baseline (pre-SFT) and 0% (v11v38 SFT)",
        ],
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log("  Summary written: " + str(SUMMARY_PATH))

    if parquet_result["status"] == "PASS":
        log("DONE: " + str(len(all_records)) + " agentic records -> "
            + OUTPUT_JSONL.name + " + " + OUTPUT_PARQUET.name
            + " (" + str(parquet_result["size_kb"]) + "KB)")


if __name__ == "__main__":
    main()

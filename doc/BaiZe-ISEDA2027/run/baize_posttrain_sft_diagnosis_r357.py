#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_sft_diagnosis_r357.py

SFT Recipe Diagnosis (R357, 2026-11-13)
=========================================
Root cause analysis of the 36%->0% regression after SFT (v11v38, step_90).

Background:
  - Base model (MiniCPM5-2B): 36% Pass@1 on EDA-Eval-PyAether 158 tasks
  - SFT model (v11v38 step_90): 0% Pass@1 on same 158 tasks
  - SFT data: 1344 "doc_to_code" pairs (read API doc -> write standalone Python function)
  - Eval harness: cline agentic tool calling (search_apis -> get_api_details -> run_code)

Hypothesis: The SFT data format (standalone code generation) is incompatible
with the eval harness format (agentic tool calling). SFT caused format collapse
and catastrophic forgetting of the tool-use protocol.

Usage:
  python3 baize_posttrain_sft_diagnosis_r357.py [--gen-log <path>] [--jsonl <path>]
  python3 baize_posttrain_sft_diagnosis_r357.py --help
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_GEN_LOG = os.path.join(
    SCRIPT_DIR, "baseline_eval_results",
    "postSFT_minicpm5_2b_sft_run1_20261112_190335_gen.log"
)
DEFAULT_SFT_JSONL = os.path.join(
    SCRIPT_DIR, "sft_pyaether_corpus_v11_v38_merged.jsonl"
)

EDA_TOOLS = ["search_apis", "get_api_details", "run_code"]
GENERIC_TOOLS = ["run_commands", "read_files", "search_codebase", "editor",
                 "ask_question", "fetch_web_content"]


def analyze_gen_log(log_path):
    """Analyze the eval generation log for tool usage patterns."""
    if not os.path.exists(log_path):
        return {"error": f"Log not found: {log_path}"}

    with open(log_path, "r", errors="replace") as f:
        content = f.read()
    lines = content.split("\n")

    tool_counts = Counter()
    for tool in EDA_TOOLS + GENERIC_TOOLS:
        pattern = f"[{tool}]"
        tool_counts[tool] = content.count(pattern)

    eda_total = sum(tool_counts[t] for t in EDA_TOOLS)
    generic_total = sum(tool_counts[t] for t in GENERIC_TOOLS)

    echo_done_count = content.count("echo done") + content.count('echo "done"')

    task_starts = len(re.findall(r'\[worker-\d+\] 开始任务', content))
    task_completions = len(re.findall(r'成功完成', content))

    garbled_samples = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(x) for x in ["[INFO]", "[SUCCESS]", "[ERROR]",
                                                  "DeprecationWarning", "Warning",
                                                  "at ", "      "]):
            continue
        if len(stripped) > 50 and not stripped.startswith("[") and not stripped.startswith("⎿"):
            if re.search(r'[^\x00-\x7f].*[^\x00-\x7f]', stripped) and \
               re.search(r'[a-zA-Z]{3,}.*[a-zA-Z]{3,}', stripped):
                garbled_samples.append(stripped[:200])
        if len(garbled_samples) >= 5:
            break

    return {
        "log_lines": len(lines),
        "eda_tool_calls": {t: tool_counts[t] for t in EDA_TOOLS},
        "eda_tool_total": eda_total,
        "generic_tool_calls": {t: tool_counts[t] for t in GENERIC_TOOLS if tool_counts[t] > 0},
        "generic_tool_total": generic_total,
        "eda_vs_generic_ratio": round(generic_total / max(eda_total, 1), 1),
        "echo_done_count": echo_done_count,
        "task_starts": task_starts,
        "task_completions": task_completions,
        "garbled_samples": garbled_samples,
    }


def analyze_sft_data(jsonl_path):
    """Analyze the SFT training data format."""
    if not os.path.exists(jsonl_path):
        return {"error": f"SFT data not found: {jsonl_path}"}

    types = Counter()
    has_standalone_code = 0
    has_tool_call_format = 0
    total = 0

    with open(jsonl_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                total += 1
                types[d.get("type", "unknown")] += 1
                completion = d.get("completion", "")
                prompt = d.get("prompt", "")
                if "import pyAether" in completion or "def " in completion:
                    has_standalone_code += 1
                if any(tool in prompt or tool in completion for tool in EDA_TOOLS):
                    has_tool_call_format += 1
            except json.JSONDecodeError:
                continue

    return {
        "total_pairs": total,
        "type_distribution": dict(types.most_common(10)),
        "standalone_code_format": has_standalone_code,
        "tool_call_format": has_tool_call_format,
        "format_mismatch_pct": round(has_standalone_code / max(total, 1) * 100, 1),
    }


def generate_report(gen_analysis, sft_analysis, output_path=None):
    """Generate a markdown diagnosis report."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# SFT Recipe Diagnosis -- R357 ({ts})",
        "",
        "## Summary",
        "",
        "| Metric | Base (pre-SFT) | SFT (step_90) | Change |",
        "|:--|:--|:--|:--|",
        "| Pass@1 (158 tasks) | 36% | 0% | **-36pp (catastrophic)** |",
        f"| EDA tool calls | -- | {gen_analysis.get('eda_tool_total', 'N/A')} | -- |",
        f"| Generic tool calls | -- | {gen_analysis.get('generic_tool_total', 'N/A')} | -- |",
        f"| EDA/Generic ratio | -- | 1:{gen_analysis.get('eda_vs_generic_ratio', 'N/A')} | -- |",
        "",
        "## Root Cause Analysis",
        "",
        "### 1. Format Mismatch (SFT data vs eval harness)",
        f"- SFT data: {sft_analysis.get('total_pairs', 'N/A')} pairs",
        f"- Standalone code format: {sft_analysis.get('standalone_code_format', 'N/A')} "
        f"({sft_analysis.get('format_mismatch_pct', 'N/A')}%)",
        f"- Tool-call format: {sft_analysis.get('tool_call_format', 'N/A')}",
        "",
        "SFT data teaches standalone Python code generation.",
        "Eval harness requires agentic tool calling (search_apis/get_api_details/run_code).",
        "These formats are fundamentally incompatible.",
        "",
        "### 2. Tool Protocol Forgetting",
        f"- EDA-specific tool calls: {gen_analysis.get('eda_tool_total', 'N/A')}",
        f"- Generic cline tool calls: {gen_analysis.get('generic_tool_total', 'N/A')}",
        f"- Ratio: 1:{gen_analysis.get('eda_vs_generic_ratio', 'N/A')} (generic >> EDA)",
        "",
        "Base model (36%) knows how to use search_apis/get_api_details/run_code.",
        "SFT model (0%) lost this ability, falls back to run_commands/ls/find.",
        "",
        "### 3. Reasoning Degradation in Agentic Setting",
        f"- 'echo done' purposeless commands: {gen_analysis.get('echo_done_count', 'N/A')}",
        f"- Tasks started: {gen_analysis.get('task_starts', 'N/A')}",
        f"- Tasks completed: {gen_analysis.get('task_completions', 'N/A')}",
        "",
        "## Proposed Fix",
        "A. SFT data format: doc_to_code -> agentic_tool_call (CRITICAL)",
        "B. Data mix: 30% general + 20% agentic + 50% PyAether-tool-call",
        "C. Training: lower LR (1e-5), fewer steps (40-60), consider LoRA",
        "D. Test earlier checkpoints (step_20/40/60/80) for less degradation",
        "",
        "## Surrogate Disclaimer",
        "MiniCPM5-2B is BaiZe surrogate; gains/losses not transferable to BaiZe.",
    ]
    report = "\n".join(lines)
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    return report


def main():
    parser = argparse.ArgumentParser(
        description="SFT Recipe Diagnosis R357 -- root cause of 36%->0% regression"
    )
    parser.add_argument("--gen-log", default=DEFAULT_GEN_LOG, help="Path to eval generation log")
    parser.add_argument("--jsonl", default=DEFAULT_SFT_JSONL, help="Path to SFT training data JSONL")
    parser.add_argument("--output", default=None, help="Output report path")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    print(f"[R357] SFT Recipe Diagnosis -- 2026-11-13")
    gen_analysis = analyze_gen_log(args.gen_log)
    sft_analysis = analyze_sft_data(args.jsonl)

    if args.json:
        result = {"round": "R357", "date": "2026-11-13",
                  "gen_log_analysis": gen_analysis, "sft_data_analysis": sft_analysis}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        report = generate_report(gen_analysis, sft_analysis, args.output)
        if not args.output:
            print(report)

    print("\n" + "=" * 60)
    print("KEY METRICS SUMMARY")
    print("=" * 60)
    print(f"EDA tool calls:     {gen_analysis.get('eda_tool_total', 'N/A')}")
    print(f"Generic tool calls: {gen_analysis.get('generic_tool_total', 'N/A')}")
    print(f"Ratio (1:N):        1:{gen_analysis.get('eda_vs_generic_ratio', 'N/A')}")
    print(f"SFT standalone code: {sft_analysis.get('format_mismatch_pct', 'N/A')}%")
    print(f"echo done count:    {gen_analysis.get('echo_done_count', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    main()

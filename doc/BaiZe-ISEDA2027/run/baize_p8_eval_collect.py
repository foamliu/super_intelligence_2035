#!/usr/bin/env python3
"""Collect P-8 14-benchmark eval results into a single JSON summary."""
import argparse
import glob
import json
import os
import sys

def find_result_json(out_dir, subdir):
    """Find the latest results_*.json in a subdirectory."""
    pattern = os.path.join(out_dir, subdir, "**", "results_*.json")
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        # Try direct subdirectory
        pattern2 = os.path.join(out_dir, subdir, "results_*.json")
        files = sorted(glob.glob(pattern2))
    return files[-1] if files else None

def extract_score(task_name, results):
    """Extract the primary score from a results dict for a given task."""
    # Priority: exact key match first, then prefix match
    for match_fn in [
        lambda k: k == task_name,
        lambda k: k.startswith(task_name),
    ]:
        for key, val in results.items():
            if match_fn(key) and isinstance(val, dict):
                # Priority: acc_norm > acc > exact_match > pass@1
                for metric in ["acc_norm,none", "acc,none", "exact_match,none",
                               "exact_match,flexible-extract",
                               "pass@1,none", "rougeL,none", "acc_norm,custom"]:
                    if metric in val:
                        return val[metric]
                # Fallback: first metric that's not stderr/name/alias
                for k, v in val.items():
                    if isinstance(v, (int, float)) and "stderr" not in k and k not in ("name", "alias", "sample_len", "sample_count"):
                        return v
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output directory with eval results")
    args = ap.parse_args()

    out_dir = args.out
    
    # Common sense 8 tasks
    cs_tasks = {
        "hellaswag": "hellaswag",
        "arc_easy": "arc_easy", 
        "boolq": "boolq",
        "arc_challenge": "arc_challenge",
        "sciq": "sciq",
        "piqa": "piqa",
        "winogrande": "winogrande",
        "openbookqa": "openbookqa",
    }
    
    # Complex 6 tasks
    cx_tasks = {
        "gsm8k": "gsm8k",
        "hendrycks_math500": "hendrycks_math500",
        "mmlu": "mmlu",
        "bbh_zeroshot": "bbh_zeroshot",
        "humaneval": "humaneval",
        "mbpp": "mbpp",
    }
    
    summary = {"common_sense": {}, "complex": {}, "errors": []}
    
    # Collect common sense
    print("\n--- Common Sense 8 ---")
    cs_scores = []
    for task_key, subdir in cs_tasks.items():
        json_file = find_result_json(out_dir, f"cs_{subdir}")
        if json_file is None:
            print(f"  {task_key}: NO RESULT FILE")
            summary["errors"].append(f"cs_{subdir}: no result file")
            summary["common_sense"][task_key] = None
            continue
        with open(json_file) as f:
            data = json.load(f)
        results = data.get("results", {})
        score = extract_score(task_key, results)
        if score is not None:
            print(f"  {task_key}: {score:.4f}")
            summary["common_sense"][task_key] = score
            cs_scores.append(score)
        else:
            print(f"  {task_key}: SCORE NOT FOUND in {json_file}")
            summary["errors"].append(f"{task_key}: score not found")
            summary["common_sense"][task_key] = None
    
    if cs_scores:
        cs_avg = sum(cs_scores) / len(cs_scores)
        summary["common_sense_avg"] = cs_avg
        print(f"  Common Sense Avg: {cs_avg:.4f} ({len(cs_scores)}/8)")
    
    # Collect complex
    print("\n--- Complex 6 ---")
    cx_scores = []
    for task_key, subdir in cx_tasks.items():
        json_file = find_result_json(out_dir, f"cx_{subdir}")
        if json_file is None:
            print(f"  {task_key}: NO RESULT FILE")
            summary["errors"].append(f"cx_{subdir}: no result file")
            summary["complex"][task_key] = None
            continue
        with open(json_file) as f:
            data = json.load(f)
        results = data.get("results", {})
        score = extract_score(task_key, results)
        if score is not None:
            print(f"  {task_key}: {score:.4f}")
            summary["complex"][task_key] = score
            cx_scores.append(score)
        else:
            print(f"  {task_key}: SCORE NOT FOUND in {json_file}")
            summary["errors"].append(f"{task_key}: score not found")
            summary["complex"][task_key] = None
    
    if cx_scores:
        cx_avg = sum(cx_scores) / len(cx_scores)
        summary["complex_avg"] = cx_avg
        print(f"  Complex Avg: {cx_avg:.4f} ({len(cx_scores)}/6)")
    
    # Save summary
    summary_path = os.path.join(out_dir, "p8_eval_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to: {summary_path}")
    
    # Print summary table
    print("\n" + "="*60)
    print(f"{'Task':<25} {'Score':>10}")
    print("-"*60)
    for task, score in summary["common_sense"].items():
        print(f"  {task:<23} {score:>10.4f}" if score is not None else f"  {task:<23} {'N/A':>10}")
    if "common_sense_avg" in summary:
        print(f"  {'CS Avg':<23} {summary['common_sense_avg']:>10.4f}")
    print("-"*60)
    for task, score in summary["complex"].items():
        print(f"  {task:<23} {score:>10.4f}" if score is not None else f"  {task:<23} {'N/A':>10}")
    if "complex_avg" in summary:
        print(f"  {'CX Avg':<23} {summary['complex_avg']:>10.4f}")
    print("="*60)

if __name__ == "__main__":
    main()

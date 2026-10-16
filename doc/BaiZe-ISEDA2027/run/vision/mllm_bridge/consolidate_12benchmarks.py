#!/usr/bin/env python
"""Consolidate eval results from multiple per-GPU JSON files into one summary.

The 12-benchmark eval set (per user directive 2026-10-16):
  ai2d, blink, chartqa, docvqa_val, infovqa_val, mme, mmmu_val, mmstar,
  ocrbench, realworldqa, countbench, mmmu_pro_standard

Results are spread across multiple JSON files (one per GPU).
This script merges them into a single consolidated JSON + prints a readable table.
"""
import json, os, sys

RESULTS_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results"

# Map of source JSON files to the benchmarks they contain
SOURCE_FILES = {
    "eval_mmmu_val.json": ["mmmu_val"],
    "eval_realworldqa.json": ["realworldqa"],
    "eval_mmmu_pro.json": ["mmmu_pro_standard"],
    "eval_ai2d_mmstar.json": ["ai2d", "mmstar"],
    "eval_infovqa.json": ["infovqa_val"],
    "eval_chart_ocr_count.json": ["chartqa", "countbench", "ocrbench"],
    "eval_docvqa.json": ["docvqa_val"],
    "eval_mme_blink.json": ["mme", "blink"],
}

# The 12 benchmarks in canonical order (per user directive)
BENCHMARKS_12 = [
    "ai2d", "blink", "chartqa", "docvqa_val", "infovqa_val",
    "mme", "mmmu_val", "mmstar", "ocrbench", "realworldqa",
    "countbench", "mmmu_pro_standard",
]


def extract_primary_metric(task_name, metrics):
    """Extract the primary metric for display."""
    metric_map = {
        "ai2d": ("exact_match,flexible-extract", "exact_match"),
        "blink": ("blink_acc,none", "blink_acc"),
        "chartqa": ("relaxed_overall,none", "relaxed_overall"),
        "docvqa_val": ("anls,none", "anls"),
        "infovqa_val": ("anls,none", "anls"),
        "mme": ("mme_perception_score,none", "perception+cognition"),
        "mmmu_val": ("mmmu_acc,none", "mmmu_acc"),
        "mmstar": ("average,none", "average"),
        "ocrbench": ("ocrbench_accuracy,none", "ocrbench_acc"),
        "realworldqa": ("exact_match,flexible-extract", "exact_match"),
        "countbench": ("acc,none", "acc"),
        "mmmu_pro_standard": ("mmmu_acc,none", "mmmu_acc"),
    }
    key, label = metric_map.get(task_name, (None, task_name))
    if key and key in metrics:
        val = metrics[key]
        if isinstance(val, (int, float)):
            return label, val
    # fallback: first numeric metric
    for k, v in metrics.items():
        if isinstance(v, (int, float)) and "stderr" not in k:
            return k, v
    return label, None


def main():
    consolidated = {}
    all_results = {}
    missing = []

    for fname, benchmarks in SOURCE_FILES.items():
        fpath = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"WARNING: {fpath} not found")
            for b in benchmarks:
                missing.append(b)
            continue
        with open(fpath) as f:
            data = json.load(f)
        results = data.get("results", {})
        for b in benchmarks:
            # Try exact match, then alias match
            if b in results:
                all_results[b] = results[b]
            else:
                # Try alias-based matching
                found = False
                for k, v in results.items():
                    alias = v.get("alias", k).strip()
                    if alias == b or k == b:
                        all_results[b] = v
                        found = True
                        break
                if not found:
                    missing.append(b)

    # Build consolidated summary in canonical order
    print("\n" + "=" * 70)
    print("  BaiZe-LLaVA 12-Benchmark Eval Results (Stage-2 step3500)")
    print("  12-benchmark set per user directive 2026-10-16")
    print("=" * 70)
    print(f"  {'Benchmark':<25s} {'Metric':<20s} {'Score':>10s}")
    print("-" * 70)

    for b in BENCHMARKS_12:
        if b in all_results:
            label, val = extract_primary_metric(b, all_results[b])
            if b == "mme":
                perc = all_results[b].get("mme_perception_score,none", 0)
                cog = all_results[b].get("mme_cognition_score,none", 0)
                print(f"  {b:<25s} {'perception+cog':<20s} {perc:.1f}+{cog:.1f}")
                consolidated[b] = {
                    "perception_score": perc,
                    "cognition_score": cog,
                    "total": perc + cog,
                }
            elif val is not None:
                print(f"  {b:<25s} {label:<20s} {val:>10.4f}")
                consolidated[b] = val
            else:
                print(f"  {b:<25s} {'(no metric)':<20s} {'N/A':>10s}")
                consolidated[b] = None
        else:
            print(f"  {b:<25s} {'MISSING':<20s} {'---':>10s}")
            missing.append(b)

    print("-" * 70)
    if missing:
        unique_missing = list(set(missing))
        print(f"  ⚠️  Missing benchmarks: {', '.join(unique_missing)}")
    else:
        print(f"  ✅ All 12 benchmarks have results!")
    print("=" * 70)

    # Save consolidated JSON
    out_path = os.path.join(RESULTS_DIR, "consolidated_12benchmarks.json")
    output = {
        "description": "BaiZe-LLaVA 12-benchmark eval results (Stage-2 step3500, per-GPU batch_size=32)",
        "benchmarks": BENCHMARKS_12,
        "results": consolidated,
        "source_files": list(SOURCE_FILES.keys()),
        "raw_results": all_results,
    }
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nConsolidated results saved to: {out_path}")


if __name__ == "__main__":
    main()

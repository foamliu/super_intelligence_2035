#!/usr/bin/env python3
"""analyze_v7_sweep.py - Aggregate v7 sweep results and apply pre-registered judgment.

Reads all 18 experiment_results.json files, computes:
  - v7 process reward: per-lambda mean+/-sd across 3 seeds, support@k
  - v7b LoRA probe: per-rank mean+/-sd across 3 seeds, support@k
  - Pre-registered PASS/FAIL judgment
"""
import json, os, sys, glob
import numpy as np
from collections import defaultdict

OUT_BASE = "/nas_train/app.e0031982/datasets/baize-vision/out"
V6_BASELINE_C = 0.40  # v6 C (outcome-only GRPO) = 40%
V6_BASELINE_B = 0.35  # v6 B (SFT) = 35%

def load_results(pattern):
    results = []
    for path in sorted(glob.glob(os.path.join(OUT_BASE, pattern, "experiment_results.json"))):
        with open(path) as f:
            d = json.load(f)
        d["_path"] = path
        d["_dirname"] = os.path.basename(os.path.dirname(path))
        results.append(d)
    return results

def extract_acc(d):
    return d["stats"]["accuracy"]["C_grpo"]

def extract_b_acc(d):
    return d["stats"]["accuracy"].get("B_sft", V6_BASELINE_B)

def extract_nonzero_std(d):
    return d["stats"]["grpo_stats"]["C_nonzero_std_frac"]

def extract_per_sample_correct(d):
    """Get per-question correct array from C results."""
    res_c = d.get("results", {}).get("C", [])
    if not res_c: return None
    return [r["correct"] for r in res_c]

def compute_support_at_k(all_corrects, k=2):
    """support@k: fraction of questions correct in >=k out of n runs."""
    if not all_corrects or len(all_corrects) < k: return None
    n_q = len(all_corrects[0])
    per_q = []
    for qi in range(n_q):
        corrects = sum(c[qi] for c in all_corrects if qi < len(c))
        per_q.append(corrects / len(all_corrects))
    support_k = np.mean([1 for p in per_q if p >= k/len(all_corrects)]) / len(per_q) if per_q else 0.0
    return {
        f"support@{k}": float(support_k),
        "mean_per_q": float(np.mean(per_q)),
        "std_per_q": float(np.std(per_q)),
        "n_runs": len(all_corrects),
        "n_questions": n_q
    }

def analyze_group(results, group_name, group_key_func, baseline_c=V6_BASELINE_C):
    """Analyze a group of results, grouped by group_key_func."""
    groups = defaultdict(list)
    for d in results:
        key = group_key_func(d)
        groups[key].append(d)

    print(f"\n{'='*60}")
    print(f"  {group_name}")
    print(f"  Baseline: v6 C (outcome-only GRPO) = {baseline_c:.1%}")
    print(f"{'='*60}")

    all_group_summaries = {}
    for key in sorted(groups.keys()):
        runs = groups[key]
        accs = [extract_acc(d) for d in runs]
        b_accs = [extract_b_acc(d) for d in runs]
        nz_stds = [extract_nonzero_std(d) for d in runs]

        mean_acc = np.mean(accs)
        std_acc = np.std(accs)
        mean_b = np.mean(b_accs)
        delta_vs_baseline = mean_acc - baseline_c
        delta_vs_b = mean_acc - mean_b

        # Check if all seeds improved over baseline
        all_above_baseline = all(a > baseline_c for a in accs)
        all_above_b = all(a > b for a, b in zip(accs, b_accs))

        # Pre-registered judgment: mean improvement > 1 sd AND 3 seeds same direction
        n_seeds = len(accs)
        if n_seeds >= 3:
            mean_improvement = delta_vs_baseline
            improvement_significant = mean_improvement > std_acc
            same_direction = all(a > baseline_c for a in accs) or all(a < baseline_c for a in accs)
            verdict = "PASS" if (improvement_significant and same_direction and all_above_baseline) else "FAIL"
        else:
            verdict = "INSUFFICIENT_DATA"

        # Support@k
        all_corrects = [extract_per_sample_correct(d) for d in runs]
        all_corrects = [c for c in all_corrects if c is not None]
        support_2 = compute_support_at_k(all_corrects, k=2) if len(all_corrects) >= 2 else None
        support_3 = compute_support_at_k(all_corrects, k=3) if len(all_corrects) >= 3 else None

        print(f"\n  Group: {key} ({n_seeds} seeds)")
        print(f"    Accuracies: {['%.1f%%' % (a*100) for a in accs]}")
        print(f"    Mean +/- sd: {mean_acc:.1%} +/- {std_acc:.1%}")
        print(f"    B (SFT) mean: {mean_b:.1%}")
        print(f"    Delta vs v6-C baseline: {delta_vs_baseline:+.1%}")
        print(f"    Delta vs B (SFT): {delta_vs_b:+.1%}")
        print(f"    Nonzero-std: {np.mean(nz_stds):.1%}")
        print(f"    All seeds > baseline: {all_above_baseline}")
        print(f"    All seeds > B: {all_above_b}")
        if support_2: print(f"    Support@2: {support_2['support@2']:.1%} (mean_per_q={support_2['mean_per_q']:.1%})")
        if support_3: print(f"    Support@3: {support_3['support@3']:.1%} (mean_per_q={support_3['mean_per_q']:.1%})")
        print(f"    PRE-REGISTERED VERDICT: {verdict}")

        all_group_summaries[str(key)] = {
            "n_seeds": n_seeds,
            "accuracies": accs,
            "mean": float(mean_acc),
            "std": float(std_acc),
            "mean_b": float(mean_b),
            "delta_vs_v6_baseline": float(delta_vs_baseline),
            "delta_vs_b": float(delta_vs_b),
            "nonzero_std_mean": float(np.mean(nz_stds)),
            "all_above_baseline": all_above_baseline,
            "all_above_b": all_above_b,
            "verdict": verdict,
            "support@2": support_2,
            "support@3": support_3,
        }
    return all_group_summaries

def main():
    print("="*60)
    print("  v7 SWEEP ANALYSIS")
    print("  Pre-registered judgment (2026-11-11):")
    print("    Baseline = v6 C (outcome-only GRPO) = 40%")
    print("    PASS: mean improvement > 1 sd AND 3 seeds same direction")
    print("="*60)

    # v7: Process Reward
    proc_results = load_results("cpu_rl_v7_proc_lam*_s*")
    print(f"\n  Found {len(proc_results)} process_reward result files")
    if proc_results:
        proc_summary = analyze_group(
            proc_results, "v7 PROCESS REWARD (lambda sweep)",
            lambda d: d["config"].get("lambda_process", 0))
    else:
        proc_summary = {}

    # v7b: LoRA Probe
    lora_results = load_results("cpu_rl_v7b_lora_r*_s*")
    print(f"\n  Found {len(lora_results)} lora_probe result files")
    if lora_results:
        lora_summary = analyze_group(
            lora_results, "v7b LoRA CAPACITY PROBE (rank sweep)",
            lambda d: d["config"].get("lora_r", 16))
    else:
        lora_summary = {}

    # Overall summary
    print(f"\n{'='*60}")
    print("  OVERALL SUMMARY")
    print(f"{'='*60}")
    all_pass = True
    for name, summary in [("v7_process", proc_summary), ("v7b_lora", lora_summary)]:
        for key, s in summary.items():
            status = "✅ PASS" if s["verdict"]=="PASS" else "❌ FAIL"
            print(f"  {name} [{key}]: mean={s['mean']:.1%} +/- {s['std']:.1%} delta={s['delta_vs_v6_baseline']:+.1%} -> {status}")
            if s["verdict"] != "PASS": all_pass = False
    print(f"\n  OVERALL: {'ALL PASS' if all_pass else 'NOT ALL PASS (negative results are also valuable)'}")

    # Save aggregated results
    out_path = os.path.join(OUT_BASE, "v7_sweep_analysis.json")
    with open(out_path, 'w') as f:
        json.dump({
            "v6_baseline": {"B_sft": V6_BASELINE_B, "C_grpo": V6_BASELINE_C},
            "v7_process_reward": proc_summary,
            "v7b_lora_probe": lora_summary,
            "n_proc_files": len(proc_results),
            "n_lora_files": len(lora_results),
        }, f, indent=2, default=str)
    print(f"\n  Aggregated results -> {out_path}")

if __name__ == "__main__": main()

#!/usr/bin/env python3
"""analyze_v8_freqcmp.py - Analyze v8 frequency comparison experiment results."""
import json, sys, os
import numpy as np
from scipy.stats import binomtest

OUT_BASE = "/nas_train/app.e0031982/datasets/baize-vision/out"


def load_results(name):
    path = os.path.join(OUT_BASE, name, "experiment_results.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def mcnemar(b_correct, c_correct):
    n01 = sum(1 for b, c in zip(b_correct, c_correct) if b and not c)
    n10 = sum(1 for b, c in zip(b_correct, c_correct) if not b and c)
    n_disc = n01 + n10
    if n_disc == 0:
        return 0.0, 1.0, 0
    p = binomtest(min(n01, n10), n_disc, 0.5).pvalue
    return abs(n01 - n10) / max(n_disc, 1), p, n_disc


def main():
    # Load all results
    seeds = []
    for i in range(3):
        r = load_results(f"cpu_rl_v8_std_s{i}")
        if r:
            seeds.append(r)
    
    ctrl = load_results("cpu_rl_v8_ctrl_s0")
    smoke = load_results("cpu_rl_v8_smoke")
    
    print("=" * 60)
    print("  v8 Frequency Comparison - Results Analysis")
    print("=" * 60)
    
    if not seeds:
        print("  No standard run results found yet.")
        return
    
    # Seed 0 has A+B+C
    s0 = seeds[0]
    acc_a = s0["stats"]["accuracy"]["A_base"]
    acc_b = s0["stats"]["accuracy"]["B_sft"]
    
    print(f"\n  Seed 0 (full A/B/C):")
    if acc_a is not None:
        print(f"    A (zero-shot): {acc_a:.1%}")
    print(f"    B (SFT):       {acc_b:.1%}")
    
    # Collect C results across seeds
    c_accs = []
    c_results_all = []
    b_results_all = []
    for s in seeds:
        c_acc = s["stats"]["accuracy"]["C_grpo"]
        c_accs.append(c_acc)
        c_results = s["results"]["C"]
        b_results = s["results"]["B"]
        if c_results:
            c_results_all.append([r["correct"] for r in c_results])
        if b_results:
            b_results_all.append([r["correct"] for r in b_results])
        print(f"    C (seed={s['config']['seed']}): {c_acc:.1%}")
    
    # Aggregate C
    if c_accs:
        c_mean = np.mean(c_accs)
        c_std = np.std(c_accs)
        print(f"\n  C (GRPO) mean: {c_mean:.1%} ± {c_std:.1%} (n={len(c_accs)} seeds)")
    
    # McNemar per seed
    print(f"\n  Per-seed McNemar C vs B:")
    all_p_values = []
    for i, s in enumerate(seeds):
        if s["results"]["B"] and s["results"]["C"]:
            bc = [r["correct"] for r in s["results"]["B"]]
            cc = [r["correct"] for r in s["results"]["C"]]
            stat, p, n_disc = mcnemar(bc, cc)
            all_p_values.append(p)
            print(f"    Seed {i}: p={p:.4f} (n_disc={n_disc})")
    
    # Control
    if ctrl:
        ctrl_acc = ctrl["stats"]["accuracy"]["C_grpo"]
        print(f"\n  Control (random reward): {ctrl_acc:.1%}")
        if b_results_all and ctrl["results"]["C"]:
            bc = b_results_all[0]
            cc = [r["correct"] for r in ctrl["results"]["C"]]
            stat, p, n_disc = mcnemar(bc, cc)
            print(f"    Control vs B: p={p:.4f} (n_disc={n_disc})")
    
    # Breakdown by difficulty
    print(f"\n  Breakdown by difficulty (seed 0, C):")
    if s0["stats"]["breakdown"]["C"]:
        for diff, vals in s0["stats"]["breakdown"]["C"].get("difficulty", {}).items():
            print(f"    {diff}: {vals['accuracy']:.1%} ({vals['correct']}/{vals['n']})")
    
    # Verdict
    print(f"\n  VERDICT:")
    if acc_b is not None and c_accs:
        c_mean = np.mean(c_accs)
        if c_mean > acc_b:
            n_sig = sum(1 for p in all_p_values if p < 0.05)
            n_consistent = sum(1 for a in c_accs if a > acc_b)
            print(f"    C > B: mean {c_mean:.1%} vs {acc_b:.1%}")
            print(f"    Significant (p<0.05): {n_sig}/{len(all_p_values)} seeds")
            print(f"    Consistent (C>B): {n_consistent}/{len(c_accs)} seeds")
            if n_sig >= 2 and n_consistent == len(c_accs):
                print(f"    => TREATMENT SIGNIFICANT")
            elif n_consistent == len(c_accs):
                print(f"    => IMPROVEMENT (consistent but not all significant)")
            else:
                print(f"    => MIXED RESULTS")
        else:
            print(f"    C <= B: mean {c_mean:.1%} vs {acc_b:.1%} => NO IMPROVEMENT")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

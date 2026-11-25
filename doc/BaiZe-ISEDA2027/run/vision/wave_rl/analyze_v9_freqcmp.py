#!/usr/bin/env python3
"""analyze_v9_freqcmp.py - Analyze v9 frequency comparison experiment results."""
import json, os, sys
import numpy as np

OUT_BASE = "/nas_train/app.e0031982/datasets/baize-vision/out"
SEEDS = [0, 1, 2]

def load_run(name):
    path = os.path.join(OUT_BASE, name, "experiment_results.json")
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)

def main():
    print("=" * 70)
    print("  v9 Frequency Comparison — Results Analysis")
    print("=" * 70)
    runs = {}
    for s in SEEDS:
        d = load_run(f"cpu_rl_v9_std_s{s}")
        if d: runs[f"seed{s}"] = d; print(f"  Loaded seed{s}: {d['stats']['accuracy']}")
    ctrl = load_run("cpu_rl_v9_ctrl_s0")
    if ctrl: runs["control"] = ctrl; print(f"  Loaded control: {ctrl['stats']['accuracy']}")
    if not runs: print("  No results found!"); return

    print("\n" + "=" * 70)
    print("  Summary Table")
    print("=" * 70)
    print(f"{'Metric':<25} {'Seed 0':<15} {'Seed 1':<15} {'Seed 2':<15} {'Control':<15}")
    print("-" * 70)
    accs_a, accs_b, accs_c = [], [], []
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            acc = runs[key]["stats"]["accuracy"]
            accs_a.append(acc.get("A_base")); accs_b.append(acc.get("B_sft")); accs_c.append(acc.get("C_grpo"))
    row_a = [f"{a:.1%}" if a is not None else "—" for a in accs_a]
    row_b = [f"{b:.1%}" if b is not None else "—" for b in accs_b]
    row_c = [f"{c:.1%}" if c is not None else "—" for c in accs_c]
    ctrl_a = f"{ctrl['stats']['accuracy']['A_base']:.1%}" if ctrl and ctrl['stats']['accuracy']['A_base'] is not None else "—"
    ctrl_b = f"{ctrl['stats']['accuracy']['B_sft']:.1%}" if ctrl and ctrl['stats']['accuracy']['B_sft'] is not None else "—"
    ctrl_c = f"{ctrl['stats']['accuracy']['C_grpo']:.1%}" if ctrl and ctrl['stats']['accuracy']['C_grpo'] is not None else "—"
    print(f"{'A (zero-shot)':<25} {row_a[0]:<15} {row_a[1]:<15} {row_a[2]:<15} {ctrl_a:<15}")
    print(f"{'B (SFT)':<25} {row_b[0]:<15} {row_b[1]:<15} {row_b[2]:<15} {ctrl_b:<15}")
    print(f"{'C (GRPO)':<25} {row_c[0]:<15} {row_c[1]:<15} {row_c[2]:<15} {ctrl_c:<15}")
    valid_c = [c for c in accs_c if c is not None]; valid_b = [b for b in accs_b if b is not None]
    if len(valid_c) >= 2: print(f"\n  C mean: {np.mean(valid_c):.1%} ± {np.std(valid_c):.1%} (n={len(valid_c)} seeds)")

    print("\n" + "=" * 70)
    print("  McNemar Tests")
    print("=" * 70)
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            mc = runs[key]["stats"].get("mcnemar_C_vs_B", {})
            if mc: print(f"  Seed {s} C-vs-B: p={mc['p']:.4f} (n_discordant={mc['n_discordant']})")
    if "control" in runs:
        mc_ctrl = runs["control"]["stats"].get("mcnemar_C_vs_B", {})
        if mc_ctrl: print(f"  Control C-vs-B: p={mc_ctrl['p']:.4f} (n_discordant={mc_ctrl['n_discordant']})")

    print("\n" + "=" * 70)
    print("  Pre-Registered Criteria Check")
    print("=" * 70)
    criteria = [
        ("B > 55%", f"B mean={np.mean(valid_b):.1%}" if valid_b else "N/A",
         np.mean(valid_b) > 0.55 if valid_b else False),
        ("C > B (mean)", f"C={np.mean(valid_c):.1%} vs B={np.mean(valid_b):.1%}" if valid_c and valid_b else "N/A",
         np.mean(valid_c) > np.mean(valid_b) if valid_c and valid_b else False),
        ("McNemar p<0.05 (s0)", f"p={runs['seed0']['stats']['mcnemar_C_vs_B']['p']:.4f}" if "seed0" in runs and "mcnemar_C_vs_B" in runs["seed0"]["stats"] else "N/A",
         "seed0" in runs and "mcnemar_C_vs_B" in runs["seed0"]["stats"] and runs["seed0"]["stats"]["mcnemar_C_vs_B"]["p"] < 0.05),
        ("3 seeds C>=B", f"C={[f'{c:.0%}' for c in valid_c]} B={[f'{b:.0%}' for b in valid_b]}" if valid_c and valid_b else "N/A",
         len(valid_c) >= 3 and len(valid_b) >= 3 and all(c >= b for c, b in zip(valid_c, valid_b))),
        ("Control C<=B+10%", f"ctrl_C={ctrl['stats']['accuracy']['C_grpo']:.1%}" if ctrl else "N/A",
         ctrl and ctrl['stats']['accuracy']['C_grpo'] is not None and valid_b and ctrl['stats']['accuracy']['C_grpo'] <= np.mean(valid_b) + 0.1),
    ]
    for name, detail, passed in criteria:
        print(f"  {name:<25} {detail:<40} {'✅' if passed else '❌'}")

    print("\n" + "=" * 70)
    print("  Difficulty Breakdown (Seed 0, C)")
    print("=" * 70)
    if "seed0" in runs:
        bd = runs["seed0"]["stats"]["breakdown"].get("C", {})
        if bd and "difficulty" in bd:
            for diff in ["easy", "medium", "hard"]:
                d = bd["difficulty"].get(diff, {})
                print(f"  {diff:<10} n={d.get('n',0):<5} correct={d.get('correct',0):<5} acc={d.get('accuracy',0):.1%}")

    print("\n  GRPO Stats:")
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            gs = runs[key]["stats"].get("grpo_stats", {})
            print(f"  Seed {s}: nonzero_std={gs.get('C_nonzero_std_frac',0):.0%} avg_reward_last5={gs.get('C_avg_reward_last5',0):.3f}")

    n_pass = sum(1 for _, _, p in criteria if p)
    print(f"\n  Verdict: {n_pass}/{len(criteria)} criteria passed → {'SIGNIFICANT' if n_pass >= 4 else 'MIXED' if n_pass >= 3 else 'NOT SIGNIFICANT'}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""analyze_v10_freqcmp.py - Analyze v10 frequency comparison experiment results.

v10 ran on .17 post-migration (2026-11-13) with results stored LOCALLY under
vision/wave_rl/v10_results/ (NOT /nas_train which is inaccessible on .17).

v10 changes vs v9 (fixing v9's NO CHANGE / n_disc=0):
  1. grpo_lr: 1e-6 -> 1e-5 (10x, key fix for n_disc=0)
  2. n_grpo_steps: 30 -> 50
  3. Base model: qwen3vl_2b_text_extracted -> Qwen3.5-2B (user-specified, available on .17)
  4. Output: local directory on .17
Everything else identical to v9 (SFT 500ex x 5ep, eval 91q, 3 seeds + control).
"""
import json, os
import numpy as np

OUT_BASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "v10_results",
)
SEEDS = [0, 1, 2]


def load_run(name):
    path = os.path.join(OUT_BASE, name, "experiment_results.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def fmt_pct(x):
    return f"{x:.1%}" if x is not None else "—"
def main():
    print("=" * 72)
    print("  v10 Frequency Comparison — Results Analysis (local .17 results)")
    print("=" * 72)
    print(f"  OUT_BASE = {OUT_BASE}")
    runs = {}
    for s in SEEDS:
        d = load_run(f"cpu_rl_v10_std_s{s}")
        if d:
            runs[f"seed{s}"] = d
            print(f"  Loaded seed{s}: {d['stats']['accuracy']}")
        else:
            print(f"  seed{s}: NOT FOUND")
    ctrl = load_run("cpu_rl_v10_ctrl_s0")
    if ctrl:
        runs["control"] = ctrl
        print(f"  Loaded control: {ctrl['stats']['accuracy']}")
    else:
        print("  control: NOT FOUND")
    if not runs:
        print("  No results found!")
        return

    print("\n" + "=" * 72)
    print("  Summary Table")
    print("=" * 72)
    print(f"{'Metric':<25} {'Seed 0':<15} {'Seed 1':<15} {'Seed 2':<15} {'Control':<15}")
    print("-" * 72)
    accs_a, accs_b, accs_c = [], [], []
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            acc = runs[key]["stats"]["accuracy"]
            accs_a.append(acc.get("A_base"))
            accs_b.append(acc.get("B_sft"))
            accs_c.append(acc.get("C_grpo"))
        else:
            accs_a.append(None); accs_b.append(None); accs_c.append(None)
    row_a = [fmt_pct(a) for a in accs_a]
    row_b = [fmt_pct(b) for b in accs_b]
    row_c = [fmt_pct(c) for c in accs_c]
    ctrl_a = fmt_pct(ctrl["stats"]["accuracy"]["A_base"]) if ctrl else "—"
    ctrl_b = fmt_pct(ctrl["stats"]["accuracy"]["B_sft"]) if ctrl else "—"
    ctrl_c = fmt_pct(ctrl["stats"]["accuracy"]["C_grpo"]) if ctrl else "—"
    print(f"{'A (zero-shot)':<25} {row_a[0]:<15} {row_a[1]:<15} {row_a[2]:<15} {ctrl_a:<15}")
    print(f"{'B (SFT)':<25} {row_b[0]:<15} {row_b[1]:<15} {row_b[2]:<15} {ctrl_b:<15}")
    print(f"{'C (GRPO)':<25} {row_c[0]:<15} {row_c[1]:<15} {row_c[2]:<15} {ctrl_c:<15}")
    valid_c = [c for c in accs_c if c is not None]
    valid_b = [b for b in accs_b if b is not None]
    valid_a = [a for a in accs_a if a is not None]
    if len(valid_c) >= 2:
        print(f"\n  C mean: {np.mean(valid_c):.1%} +/- {np.std(valid_c):.1%} (n={len(valid_c)} seeds)")
    if len(valid_b) >= 2:
        print(f"  B mean: {np.mean(valid_b):.1%} +/- {np.std(valid_b):.1%} (n={len(valid_b)} seeds)")

    print("\n" + "=" * 72)
    print("  McNemar Tests (C vs B)")
    print("=" * 72)
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            mc = runs[key]["stats"].get("mcnemar_C_vs_B", {})
            if mc:
                print(f"  Seed {s} C-vs-B: p={mc['p']:.4f} (n_discordant={mc['n_discordant']})")
            else:
                print(f"  Seed {s}: mcnemar_C_vs_B missing (skip_baseline_eval)")
    if "control" in runs:
        mc_ctrl = runs["control"]["stats"].get("mcnemar_C_vs_B", {})
        if mc_ctrl:
            print(f"  Control C-vs-B: p={mc_ctrl['p']:.4f} (n_discordant={mc_ctrl['n_discordant']})")
        else:
            print("  Control: mcnemar_C_vs_B missing")

    print("\n" + "=" * 72)
    print("  Discordant-pair diagnostic (v10 KEY fix vs v9 n_disc=0)")
    print("=" * 72)
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            mc = runs[key]["stats"].get("mcnemar_C_vs_B", {})
            nd = mc.get("n_discordant", "—")
            print(f"  Seed {s}: n_discordant = {nd}")
    print(f"  v9 reference: n_discordant = 0 (the bug v10 was designed to fix)")

    print("\n" + "=" * 72)
    print("  Pre-Registered Criteria Check (per run_v10_freqcmp.sh)")
    print("=" * 72)
    criteria = []
    criteria.append((
        "B > 55%",
        f"B mean={np.mean(valid_b):.1%}" if valid_b else "N/A",
        np.mean(valid_b) > 0.55 if valid_b else False,
    ))
    criteria.append((
        "C > B (mean)",
        f"C={np.mean(valid_c):.1%} vs B={np.mean(valid_b):.1%}" if valid_c and valid_b else "N/A",
        np.mean(valid_c) > np.mean(valid_b) if valid_c and valid_b else False,
    ))
    mc0 = runs.get("seed0", {}).get("stats", {}).get("mcnemar_C_vs_B", {})
    criteria.append((
        "McNemar p<0.05 (s0)",
        f"p={mc0.get('p'):.4f}" if mc0 else "N/A",
        bool(mc0) and mc0["p"] < 0.05,
    ))
    criteria.append((
        "3 seeds C>=B",
        f"C={[fmt_pct(c) for c in valid_c]} B={[fmt_pct(b) for b in valid_b]}" if valid_c and valid_b else "N/A",
        len(valid_c) >= 3 and len(valid_b) >= 3 and all(c >= b for c, b in zip(valid_c, valid_b)),
    ))
    nd0 = mc0.get("n_discordant", 0) if mc0 else 0
    criteria.append((
        "n_disc>0 (s0)",
        f"n_disc={nd0}",
        nd0 > 0,
    ))
    criteria.append((
        "Control C<=B+10%",
        f"ctrl_C={ctrl['stats']['accuracy']['C_grpo']:.1%}" if ctrl and ctrl["stats"]["accuracy"]["C_grpo"] is not None else "N/A",
        bool(ctrl) and ctrl["stats"]["accuracy"]["C_grpo"] is not None and bool(valid_b)
        and ctrl["stats"]["accuracy"]["C_grpo"] <= np.mean(valid_b) + 0.1,
    ))
    for name, detail, passed in criteria:
        print(f"  {name:<25} {detail:<40} {'PASS' if passed else 'FAIL'}")
    n_pass = sum(1 for _, _, p in criteria if p)
    verdict = "SIGNIFICANT" if n_pass >= 5 else "MIXED" if n_pass >= 3 else "NOT SIGNIFICANT"
    print(f"\n  Verdict: {n_pass}/{len(criteria)} criteria passed -> {verdict}")

    print("\n" + "=" * 72)
    print("  Difficulty Breakdown (Seed 0)")
    print("=" * 72)
    if "seed0" in runs:
        bd = runs["seed0"]["stats"]["breakdown"]
        for stage in ["A", "B", "C"]:
            print(f"  --- Stage {stage} ---")
            sbd = bd.get(stage, {})
            if sbd and "difficulty" in sbd:
                for diff in ["easy", "medium", "hard"]:
                    dd = sbd["difficulty"].get(diff, {})
                    print(f"    {diff:<10} n={dd.get('n', 0):<5} correct={dd.get('correct', 0):<5} acc={dd.get('accuracy', 0):.1%}")

    print("\n  GRPO Stats:")
    for s in SEEDS:
        key = f"seed{s}"
        if key in runs:
            gs = runs[key]["stats"].get("grpo_stats", {})
            print(f"  Seed {s}: nonzero_std={gs.get('C_nonzero_std_frac', 0):.0%} avg_reward_last5={gs.get('C_avg_reward_last5', 0):.3f}")
    if "control" in runs:
        gs = runs["control"]["stats"].get("grpo_stats", {})
        print(f"  Control: nonzero_std={gs.get('C_nonzero_std_frac', 0):.0%} avg_reward_last5={gs.get('C_avg_reward_last5', 0):.3f}")

    print("\n  Cheat rate (seed0):", runs.get("seed0", {}).get("stats", {}).get("cheat_rate", "—"))

    summary = {
        "version": "v10",
        "n_seeds_loaded": len([s for s in SEEDS if f"seed{s}" in runs]),
        "control_loaded": "control" in runs,
        "accuracy": {
            "A": valid_a, "B": valid_b, "C": valid_c,
            "control_C": ctrl["stats"]["accuracy"]["C_grpo"] if ctrl else None,
        },
        "mean": {
            "A": float(np.mean(valid_a)) if valid_a else None,
            "B": float(np.mean(valid_b)) if valid_b else None,
            "C": float(np.mean(valid_c)) if valid_c else None,
            "C_std": float(np.std(valid_c)) if valid_c else None,
        },
        "mcnemar_s0": mc0 if mc0 else None,
        "n_discordant_s0": nd0,
        "criteria_passed": n_pass,
        "criteria_total": len(criteria),
        "verdict": verdict,
    }
    out_json = os.path.join(OUT_BASE, "v10_summary.json")
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  Summary JSON written -> {out_json}")


if __name__ == "__main__":
    main()


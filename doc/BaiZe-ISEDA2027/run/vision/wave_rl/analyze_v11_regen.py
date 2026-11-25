#!/usr/bin/env python3
"""analyze_v11_regen.py - Analyze v11 regression-vs-generation three-arm results across seeds."""
import json, os
import numpy as np

OUT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v11_results")
SEEDS = [20261114, 20261115, 20261116]
ARMS = ["direct", "augment", "synthesis"]


def load_run(name):
    path = os.path.join(OUT_BASE, name, "experiment_results.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    print("=" * 74)
    print("  v11 Regression vs Generation — Three-Arm Analysis (3 seeds)")
    print("=" * 74)
    acc = {a: [] for a in ARMS}
    mre = {a: [] for a in ARMS}
    loaded = 0
    for s in SEEDS:
        d = load_run(f"cpu_rl_v11_std_s{s}")
        if not d:
            print(f"  seed {s}: NOT FOUND")
            continue
        loaded += 1
        st = d["stats"]
        row = []
        for a in ARMS:
            v = st["accuracy"].get(a)
            acc[a].append(v)
            mv = st["mean_rel_err"].get(a)
            mre[a].append(mv)
            row.append(f"{a}={v:.1%}" if v is not None else f"{a}=NA")
        mc_aug = st.get("mcnemar_augment_vs_direct", {})
        mc_syn = st.get("mcnemar_synthesis_vs_direct", {})
        print(f"  seed {s}: {' '.join(row)} | "
              f"aug p={mc_aug.get('p', 'NA')} nd={mc_aug.get('n_discordant', 'NA')} | "
              f"syn p={mc_syn.get('p', 'NA')} nd={mc_syn.get('n_discordant', 'NA')} | "
              f"verdict={st.get('verdict', 'NA')[:40]}")
    if loaded == 0:
        print("  No standard-seed results found.")
        return

    print("\n" + "=" * 74)
    print("  Mean across seeds")
    print("=" * 74)
    for a in ARMS:
        vals = [x for x in acc[a] if x is not None]
        mvals = [x for x in mre[a] if x is not None]
        if vals:
            print(f"  Arm {a:<10}: acc={np.mean(vals):.1%} +/- {np.std(vals):.1%} (n={len(vals)})  "
                  f"mean_rel_err={np.mean(mvals):.3f}" if mvals else f"  Arm {a:<10}: acc={np.mean(vals):.1%}")
        else:
            print(f"  Arm {a:<10}: no data")

    print("\n" + "=" * 74)
    print("  Pre-Registered Criteria Check")
    print("=" * 74)
    d_vals = [x for x in acc["direct"] if x is not None]
    aug_vals = [x for x in acc["augment"] if x is not None]
    syn_vals = [x for x in acc["synthesis"] if x is not None]
    crit = []
    if d_vals:
        crit.append(("Arm1 direct in [30,40%]", f"{np.mean(d_vals):.1%}",
                     0.30 <= np.mean(d_vals) <= 0.45))
    if aug_vals and d_vals:
        crit.append(("augment > direct (mean)", f"{np.mean(aug_vals):.1%} vs {np.mean(d_vals):.1%}",
                     np.mean(aug_vals) > np.mean(d_vals)))
    if syn_vals and d_vals:
        crit.append(("synthesis > direct (mean)", f"{np.mean(syn_vals):.1%} vs {np.mean(d_vals):.1%}",
                     np.mean(syn_vals) > np.mean(d_vals)))
    # per-seed significance
    sig_aug = 0; sig_syn = 0
    for s in SEEDS:
        d = load_run(f"cpu_rl_v11_std_s{s}")
        if not d:
            continue
        st = d["stats"]
        if st.get("mcnemar_augment_vs_direct", {}).get("p", 1) < 0.05:
            sig_aug += 1
        if st.get("mcnemar_synthesis_vs_direct", {}).get("p", 1) < 0.05:
            sig_syn += 1
    crit.append(("augment McNemar p<0.05 seeds", f"{sig_aug}/{loaded}", sig_aug >= 1))
    crit.append(("synthesis McNemar p<0.05 seeds", f"{sig_syn}/{loaded}", sig_syn >= 1))
    # >=5pp gain
    gain_aug = (np.mean(aug_vals) - np.mean(d_vals)) if aug_vals and d_vals else 0
    gain_syn = (np.mean(syn_vals) - np.mean(d_vals)) if syn_vals and d_vals else 0
    crit.append((">=1 gen arm +>=5pp & sig", f"aug+{gain_aug:.1%} syn+{gain_syn:.1%}",
                 (gain_aug >= 0.05 and sig_aug >= 1) or (gain_syn >= 0.05 and sig_syn >= 1)))
    for name, detail, passed in crit:
        print(f"  {name:<32} {detail:<28} {'PASS' if passed else 'FAIL'}")
    n_pass = sum(1 for _, _, p in crit if p)
    final = "GENERATIVE ADVANTAGE (pursue generative route)" if (gain_aug >= 0.05 and sig_aug >= 1) or (gain_syn >= 0.05 and sig_syn >= 1) else \
            "NO GENERATIVE ADVANTAGE (negative result: do not pursue generative route this period)"
    print(f"\n  FINAL VERDICT: {final}")

    summary = {"version": "v11", "n_seeds_loaded": loaded,
               "mean_acc": {a: float(np.mean([x for x in acc[a] if x is not None])) if any(x is not None for x in acc[a]) else None for a in ARMS},
               "mean_rel_err": {a: float(np.mean([x for x in mre[a] if x is not None])) if any(x is not None for x in mre[a]) else None for a in ARMS},
               "gain_augment_vs_direct": float(gain_aug), "gain_synthesis_vs_direct": float(gain_syn),
               "sig_aug_seeds": sig_aug, "sig_syn_seeds": sig_syn, "final_verdict": final}
    out_json = os.path.join(OUT_BASE, "v11_summary.json")
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n  Summary JSON -> {out_json}")


if __name__ == "__main__":
    main()

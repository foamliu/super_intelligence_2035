#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Paired statistical comparison of two eval arms (baseline-nailed 令 §D Stage3).

Quantifies the SFT delta (A1_sft - A0_base) on the SAME 158-task set with the
SAME frozen protocol (158 / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n).

Reads two `baseline_<label>_5run_summary.json` files (produced by
baize_posttrain_a0_finalize_5run.py). Each summary carries:
  - per_run_pass_rate            : {run_id: pass_rate}
  - five_run_mean / five_run_std : scalar
  - per_task_pass_count_by_run   : {task_id: [0/1, ...]}  (Pass@1, one entry per run)

Paired analyses (arms share the identical 158 tasks => paired by task):
  1. per-run mean+/-std per arm + delta on the run-level mean pass rate;
  2. per-task pass rate (pass_count / n_runs) -> Wilcoxon signed-rank + paired t;
  3. McNemar on per-task consensus under TWO thresholds:
       - majority  (pass_count >= ceil(n_runs/2))
       - any_pass  (pass_count >= 1)
     exact binomial two-sided p on discordant pairs + chi2 approx;
  4. paired bootstrap (resample 158 tasks w/ replacement, B=10000):
       delta of mean pass rate -> 95% percentile CI + two-sided p.

Does NOT touch protocol / benchmark / check.py / timeouts / -p. Pure stats.
No GPU / sandbox / network. Safe to re-run.
"""
import argparse, json, math, os, random, statistics, sys

try:
    import numpy as np  # noqa: F401
    from scipy import stats as sp_stats
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def load_summary(path):
    d = json.load(open(path))
    pt = d.get("per_task_pass_count_by_run", {})
    per_task = {tid: [int(x) for x in v] for tid, v in pt.items()}
    return {
        "label": d.get("arm", os.path.basename(path)),
        "per_run_pass_rate": d.get("per_run_pass_rate", {}),
        "five_run_mean": d.get("five_run_mean"),
        "five_run_std": d.get("five_run_std"),
        "n_runs_completed": d.get("n_runs_completed"),
        "per_task": per_task,
    }
def mcnemar(a0_consensus, a1_consensus):
    """a0_consensus/a1_consensus: dict task_id -> 0/1. Returns contingency + tests."""
    both = a0o = a1o = neither = 0
    tasks = sorted(set(a0_consensus) | set(a1_consensus))
    for t in tasks:
        x = a0_consensus.get(t, 0)
        y = a1_consensus.get(t, 0)
        if x and y:
            both += 1
        elif x and not y:
            a0o += 1
        elif (not x) and y:
            a1o += 1
        else:
            neither += 1
    discord = a0o + a1o
    if discord > 0:
        k = min(a0o, a1o)
        exact_p = 2.0 * float(sp_stats.binom.cdf(k, discord, 0.5)) if HAVE_SCIPY else None
        chi2 = (abs(a0o - a1o) - 1.0) ** 2 / discord
        chi2_p = float(sp_stats.chi2.sf(chi2, 1)) if HAVE_SCIPY else None
    else:
        exact_p = 1.0
        chi2 = 0.0
        chi2_p = 1.0
    return {
        "both_pass": both, "A0_only": a0o, "A1_only": a1o, "both_fail": neither,
        "discordant": discord,
        "exact_binom_p_two_sided": (round(exact_p, 6) if exact_p is not None else None),
        "chi2_continuity": round(chi2, 4),
        "chi2_p_two_sided": (round(chi2_p, 6) if chi2_p is not None else None),
    }


def consensus(per_task, threshold):
    return {tid: 1 if sum(v) >= threshold else 0 for tid, v in per_task.items()}


def paired_bootstrap(a0_rates, a1_rates, B=10000, seed=20261121):
    """a0_rates/a1_rates: per-task pass rates in [0,1], aligned by index."""
    rng = random.Random(seed)
    n = len(a0_rates)
    if n == 0:
        return None
    deltas = []
    n_arr = list(range(n))
    for _ in range(B):
        idx = [rng.choice(n_arr) for _ in range(n)]
        m0 = sum(a0_rates[i] for i in idx) / n
        m1 = sum(a1_rates[i] for i in idx) / n
        deltas.append(m1 - m0)
    deltas.sort()
    mean = sum(deltas) / len(deltas)
    lo = deltas[int(0.025 * B)]
    hi = deltas[int(0.975 * B) - 1]
    le = sum(1 for d in deltas if d <= 0.0)
    ge = sum(1 for d in deltas if d >= 0.0)
    p = min(2.0 * min(le, ge) / B, 1.0)
    return {
        "n_iter": B,
        "delta_mean": round(mean, 6),
        "ci95_low": round(lo, 6),
        "ci95_high": round(hi, 6),
        "p_two_sided": round(p, 6),
        "n_tasks": n,
    }
def compare(a0_path, a1_path):
    a0 = load_summary(a0_path)
    a1 = load_summary(a1_path)
    common = sorted(set(a0["per_task"]) & set(a1["per_task"]))
    n0 = a0["n_runs_completed"] or (len(next(iter(a0["per_task"].values()))) if a0["per_task"] else 0) or 0
    n1 = a1["n_runs_completed"] or (len(next(iter(a1["per_task"].values()))) if a1["per_task"] else 0) or 0

    a0_per_run = [float(v) for v in a0["per_run_pass_rate"].values()] or \
                 [sum(v) / len(v) for v in a0["per_task"].values() if v]
    a1_per_run = [float(v) for v in a1["per_run_pass_rate"].values()] or \
                 [sum(v) / len(v) for v in a1["per_task"].values() if v]
    mean0 = a0["five_run_mean"] if a0["five_run_mean"] is not None else (sum(a0_per_run) / len(a0_per_run) if a0_per_run else None)
    mean1 = a1["five_run_mean"] if a1["five_run_mean"] is not None else (sum(a1_per_run) / len(a1_per_run) if a1_per_run else None)
    std0 = a0["five_run_std"] if a0["five_run_std"] is not None else (statistics.stdev(a0_per_run) if len(a0_per_run) >= 2 else 0.0)
    std1 = a1["five_run_std"] if a1["five_run_std"] is not None else (statistics.stdev(a1_per_run) if len(a1_per_run) >= 2 else 0.0)

    a0_rates = [sum(a0["per_task"][t]) / len(a0["per_task"][t]) for t in common]
    a1_rates = [sum(a1["per_task"][t]) / len(a1["per_task"][t]) for t in common]

    per_task_tests = {"n_tasks_paired": len(common)}
    if HAVE_SCIPY and common:
        try:
            w = sp_stats.wilcoxon(a1_rates, a0_rates, zero_method="wilcox", alternative="two-sided")
            per_task_tests["wilcoxon_signed_rank"] = {"statistic": float(w.statistic),
                                                      "p_two_sided": round(float(w.pvalue), 6),
                                                      "direction": "A1 - A0 (positive => SFT helps)"}
        except Exception as e:
            per_task_tests["wilcoxon_signed_rank"] = {"error": str(e)}
        try:
            t = sp_stats.ttest_rel(a1_rates, a0_rates)
            per_task_tests["paired_t_test"] = {"t": round(float(t.statistic), 4),
                                               "p_two_sided": round(float(t.pvalue), 6),
                                               "df": len(common) - 1}
        except Exception as e:
            per_task_tests["paired_t_test"] = {"error": str(e)}
    per_task_tests["mean_per_task_pass_rate_A0"] = round(sum(a0_rates) / len(a0_rates), 6) if a0_rates else None
    per_task_tests["mean_per_task_pass_rate_A1"] = round(sum(a1_rates) / len(a1_rates), 6) if a1_rates else None

    mcnemar_block = {}
    if common:
        maj0 = math.ceil(n0 / 2.0) if n0 > 0 else 1
        maj1 = math.ceil(n1 / 2.0) if n1 > 0 else 1
        c0_maj = consensus({t: a0["per_task"][t] for t in common}, maj0)
        c1_maj = consensus({t: a1["per_task"][t] for t in common}, maj1)
        mcnemar_block["majority"] = dict(mcnemar(c0_maj, c1_maj),
                                         threshold_A0="pass_count >= ceil(%d/2)=%d" % (n0, maj0),
                                         threshold_A1="pass_count >= ceil(%d/2)=%d" % (n1, maj1))
        c0_any = consensus({t: a0["per_task"][t] for t in common}, 1)
        c1_any = consensus({t: a1["per_task"][t] for t in common}, 1)
        mcnemar_block["any_pass"] = dict(mcnemar(c0_any, c1_any),
                                         threshold="pass_count >= 1 (passed in at least one run)")

    boot = paired_bootstrap(a0_rates, a1_rates) if a0_rates else None
    delta_mean = (mean1 - mean0) if (mean0 is not None and mean1 is not None) else None

    per_task_table = {}
    for i, t in enumerate(common):
        per_task_table[t] = {
            "A0_pass_count": sum(a0["per_task"][t]), "A0_n_runs": len(a0["per_task"][t]),
            "A1_pass_count": sum(a1["per_task"][t]), "A1_n_runs": len(a1["per_task"][t]),
            "A0_rate": round(a0_rates[i], 4), "A1_rate": round(a1_rates[i], 4),
        }

    return {
        "comparison": "%s vs %s" % (a0["label"], a1["label"]),
        "direction": "delta = A1 - A0 (positive => SFT improves Pass@1)",
        "protocol": "158 / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n (frozen, same scale both arms)",
        "arms": {
            a0["label"]: {"n_runs": n0, "mean_pass_rate": round(mean0, 6) if mean0 is not None else None,
                          "std_pass_rate": round(std0, 6) if std0 is not None else None,
                          "per_run_pass_rate": {str(k): v for k, v in a0["per_run_pass_rate"].items()}},
            a1["label"]: {"n_runs": n1, "mean_pass_rate": round(mean1, 6) if mean1 is not None else None,
                          "std_pass_rate": round(std1, 6) if std1 is not None else None,
                          "per_run_pass_rate": {str(k): v for k, v in a1["per_run_pass_rate"].items()}},
        },
        "delta_mean_pass_rate": round(delta_mean, 6) if delta_mean is not None else None,
        "per_task_paired_tests": per_task_tests,
        "mcnemar": mcnemar_block,
        "paired_bootstrap": boot,
        "n_tasks_paired": len(common),
        "scipy_available": HAVE_SCIPY,
        "per_task_table": per_task_table,
        "note": "McNemar 'majority' = task passes if pass_count >= ceil(n_runs/2); "
                "'any_pass' = passes if pass_count >= 1. Bootstrap resamples tasks w/ replacement "
                "(B=10000); p_two_sided = 2*min(P(delta<=0),P(delta>=0)).",
    }
def selftest():
    """Build a synthetic A1 from A0's interim summary (perturb ~15% of tasks toward
    pass) to validate the full stats pipeline end-to-end."""
    a0_path = "baseline_A0_base_2run_interim_summary.json"
    if not os.path.exists(a0_path):
        print("[selftest] need %s; skip" % a0_path); return 1
    a0 = load_summary(a0_path)
    rng = random.Random(7)
    synth = json.load(open(a0_path))
    pt = {}
    for tid, v in a0["per_task"].items():
        v = list(v)
        if rng.random() < 0.15:
            v = [1] * len(v)
        pt[tid] = v
    synth["arm"] = "A1_sft_SYNTHETIC"
    synth["per_task_pass_count_by_run"] = pt
    rates = [sum(v) / len(v) for v in pt.values()]
    synth["five_run_mean"] = round(sum(rates) / len(rates), 6)
    synth["five_run_std"] = 0.0
    nrun = len(next(iter(pt.values())))
    synth["per_run_pass_rate"] = {str(i + 1): round(sum(v[i] for v in pt.values()) / len(pt), 6)
                                  for i in range(nrun)}
    a1_path = "/tmp/_selftest_A1_synth_summary.json"
    json.dump(synth, open(a1_path, "w"), ensure_ascii=False, indent=1)
    res = compare(a0_path, a1_path)
    res["selftest"] = True
    out = "/tmp/_selftest_A0_vs_A1_paired_compare.json"
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    print("[selftest] WROTE", out)
    print("[selftest] arms:", json.dumps(res["arms"], ensure_ascii=False))
    print("[selftest] delta_mean:", res["delta_mean_pass_rate"])
    print("[selftest] mcnemar_majority:", json.dumps(res["mcnemar"].get("majority", {}), ensure_ascii=False))
    print("[selftest] bootstrap:", json.dumps(res["paired_bootstrap"], ensure_ascii=False))
    print("[selftest] wilcoxon:", json.dumps(res["per_task_paired_tests"].get("wilcoxon_signed_rank", {}), ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a0", default="baseline_A0_base_5run_summary.json", help="A0 (base) 5run summary json")
    ap.add_argument("--a1", default="baseline_A1_sft_5run_summary.json", help="A1 (SFT) 5run summary json")
    ap.add_argument("--out", default="baseline_A0_vs_A1_paired_compare.json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not os.path.exists(args.a0):
        print("FATAL: a0 summary not found: %s" % args.a0); return 1
    if not os.path.exists(args.a1):
        print("FATAL: a1 summary not found: %s" % args.a1); return 1
    res = compare(args.a0, args.a1)
    with open(args.out, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("[compare] WROTE", args.out)
    print("[compare] %s | delta_mean=%.4f | n_paired=%d" % (res["comparison"], res["delta_mean_pass_rate"] or 0, res["n_tasks_paired"]))
    print("[compare] bootstrap:", json.dumps(res["paired_bootstrap"], ensure_ascii=False))
    print("[compare] mcnemar_majority:", json.dumps(res["mcnemar"].get("majority", {}), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())




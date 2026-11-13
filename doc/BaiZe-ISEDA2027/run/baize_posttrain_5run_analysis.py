#!/usr/bin/env python3
"""baize_posttrain_5run_analysis.py -- 5-run Pass@1 analysis: mean+/-std + McNemar + paired bootstrap.

Reads final_report.json (or result_summary.json fallback) from:
  /tmp/posttrain_5run_eval/<label>/run<N>/final_report.json
  /tmp/posttrain_5run_eval/<label>/run<N>/result_summary.json
"""
import argparse
import json
import os
import statistics
import sys
import math
import random

RESULTS_DIR = "/tmp/posttrain_5run_eval"


def load_run_result(label, run_n):
    run_dir = os.path.join(RESULTS_DIR, label, "run" + str(run_n))
    for fname in ("final_report.json", "result_summary.json"):
        fpath = os.path.join(run_dir, fname)
        if os.path.exists(fpath):
            try:
                data = json.load(open(fpath))
                # Try top-level fields first (result_summary.json), then nested (final_report.json)
                rate = data.get("pass_at_1_rate") or data.get("pass_rate") or data.get("pass@1")
                if rate is None and isinstance(data.get("metrics"), dict):
                    rate = data["metrics"].get("pass_rate") or data["metrics"].get("pass@1")
                if rate is None and isinstance(data.get("summary"), dict):
                    # final_report.json: total_correct_completions / total_problems_evaluated
                    tc = data["summary"].get("total_correct_completions")
                    tp = data["summary"].get("total_problems_evaluated")
                    if tc is not None and tp is not None and tp > 0:
                        rate = tc / tp
                passed = data.get("passed_tasks", [])
                # If no passed_tasks list, extract from details_per_task
                if not passed and isinstance(data.get("details_per_task"), dict):
                    # final_report.json: details_per_task is {task_id: {num_correct, pass_rate, ...}}
                    passed = [tid for tid, tv in data["details_per_task"].items()
                              if tv.get("num_correct", 0) > 0 or tv.get("pass_rate", 0) > 0]
                elif not passed and isinstance(data.get("details_per_task"), list):
                    passed = [t.get("task_id", t.get("id", "")) for t in data["details_per_task"]
                              if t.get("pass", t.get("passed", t.get("correct", False))) is True]
                return {
                    "run": run_n, "label": label,
                    "pass_at_1_rate": float(rate) if rate is not None else None,
                    "passed_tasks": set(passed) if isinstance(passed, list) else set(),
                    "source_file": fname,
                }
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                return {"run": run_n, "label": label, "error": str(e)}
    return {"run": run_n, "label": label, "error": "no result file found"}


def analyze_label(label):
    runs = []
    for run_n in range(1, 6):
        result = load_run_result(label, run_n)
        if "error" not in result:
            runs.append(result)
        else:
            print("  [" + label + "] run" + str(run_n) + ": SKIP (" + result["error"] + ")")
    if not runs:
        print("  [" + label + "] No valid runs found.")
        return None
    rates = [r["pass_at_1_rate"] for r in runs if r["pass_at_1_rate"] is not None]
    summary = {"label": label, "num_runs": len(rates), "rates": rates}
    if len(rates) >= 1:
        summary["mean"] = statistics.mean(rates)
    if len(rates) >= 2:
        summary["std"] = statistics.stdev(rates)
        summary["mean_pm_std"] = "%.4f+/-%.4f" % (summary["mean"], summary["std"])
    else:
        summary["mean_pm_std"] = "%.4f (n=1)" % rates[0]
    print("  [" + label + "] " + str(summary["num_runs"]) + "/5 runs: rates=" + str([round(r, 4) for r in rates]))
    print("  [" + label + "] mean+/-std = " + summary["mean_pm_std"])
    for r in runs:
        n_passed = len(r.get("passed_tasks", set()))
        rate_str = "%.4f" % r["pass_at_1_rate"] if r["pass_at_1_rate"] is not None else "N/A"
        print("    run" + str(r["run"]) + ": Pass@1=" + rate_str + " (" + str(n_passed) + "/158 tasks passed)")
    return summary


def mcnemar_test(set_a, set_b):
    b = len(set_a - set_b)
    c = len(set_b - set_a)
    n_discordant = b + c
    if n_discordant == 0:
        return {"b": b, "c": c, "chi2": 0.0, "p_value": 1.0, "note": "no discordant pairs"}
    chi2 = (abs(b - c) - 1) ** 2 / n_discordant
    p_value = math.erfc(math.sqrt(chi2 / 2))
    return {"b": b, "c": c, "chi2": round(chi2, 4), "p_value": round(p_value, 6)}


def paired_bootstrap(set_a, set_b, n_bootstrap=10000, seed=42):
    random.seed(seed)
    all_tasks = sorted(set_a | set_b)
    n_tasks = len(all_tasks)
    if n_tasks == 0:
        return {"mean_diff": 0.0, "ci_low": 0.0, "ci_high": 0.0, "note": "no tasks"}
    vec_a = [1 if t in set_a else 0 for t in all_tasks]
    vec_b = [1 if t in set_b else 0 for t in all_tasks]
    obs_diff = sum(a - b for a, b in zip(vec_a, vec_b)) / n_tasks
    diffs = []
    for _ in range(n_bootstrap):
        indices = [random.randint(0, n_tasks - 1) for _ in range(n_tasks)]
        boot_a = sum(vec_a[i] for i in indices) / n_tasks
        boot_b = sum(vec_b[i] for i in indices) / n_tasks
        diffs.append(boot_a - boot_b)
    diffs.sort()
    return {
        "observed_diff": round(obs_diff, 4),
        "ci_low": round(diffs[int(0.025 * n_bootstrap)], 4),
        "ci_high": round(diffs[int(0.975 * n_bootstrap)], 4),
        "n_bootstrap": n_bootstrap, "n_tasks": n_tasks,
    }


def compare_labels(label_a, label_b):
    print("\n=== Comparison: " + label_a + " vs " + label_b + " ===")
    result_a = result_b = None
    for run_n in range(1, 6):
        r = load_run_result(label_a, run_n)
        if "error" not in r and r.get("passed_tasks"):
            result_a = r; break
    for run_n in range(1, 6):
        r = load_run_result(label_b, run_n)
        if "error" not in r and r.get("passed_tasks"):
            result_b = r; break
    if not result_a or not result_b:
        print("  Missing data for comparison")
        return None
    set_a, set_b = result_a["passed_tasks"], result_b["passed_tasks"]
    print("  " + label_a + " (run" + str(result_a["run"]) + "): " + str(len(set_a)) + " tasks passed")
    print("  " + label_b + " (run" + str(result_b["run"]) + "): " + str(len(set_b)) + " tasks passed")
    mc = mcnemar_test(set_a, set_b)
    sig = "***" if mc["p_value"] < 0.001 else "**" if mc["p_value"] < 0.01 else "*" if mc["p_value"] < 0.05 else "ns"
    print("  McNemar: b=" + str(mc["b"]) + " (A pass,B fail), c=" + str(mc["c"]) + " (B pass,A fail)")
    print("    chi2=" + str(mc["chi2"]) + ", p=" + str(mc["p_value"]) + " " + sig)
    pb = paired_bootstrap(set_a, set_b)
    print("  Paired bootstrap (10k resamples):")
    print("    observed diff = %.4f (%s - %s)" % (pb["observed_diff"], label_a, label_b))
    print("    95%% CI = [%.4f, %.4f]" % (pb["ci_low"], pb["ci_high"]))
    return {"mcnemar": mc, "bootstrap": pb}


def main():
    parser = argparse.ArgumentParser(description="5-run Pass@1 analysis")
    parser.add_argument("--label", help="Analyze a single label")
    parser.add_argument("--compare", nargs=2, metavar=("LABEL_A", "LABEL_B"), help="Compare two labels")
    parser.add_argument("--output", help="Save summary JSON to this path")
    args = parser.parse_args()
    all_summaries = {}
    if args.compare:
        for label in args.compare:
            print("\n=== " + label + " ===")
            s = analyze_label(label)
            if s: all_summaries[label] = s
        cmp = compare_labels(args.compare[0], args.compare[1])
        if cmp: all_summaries["comparison"] = {"label_a": args.compare[0], "label_b": args.compare[1], **cmp}
    elif args.label:
        print("\n=== " + args.label + " ===")
        s = analyze_label(args.label)
        if s: all_summaries[args.label] = s
    else:
        if not os.path.isdir(RESULTS_DIR):
            print("Results dir not found: " + RESULTS_DIR); sys.exit(1)
        labels = sorted(d for d in os.listdir(RESULTS_DIR) if os.path.isdir(os.path.join(RESULTS_DIR, d)))
        for label in labels:
            print("\n=== " + label + " ===")
            s = analyze_label(label)
            if s: all_summaries[label] = s
    out_path = args.output or os.path.join(RESULTS_DIR, "5run_analysis.json")
    json.dump(all_summaries, open(out_path, "w"), indent=2)
    print("\nSummary saved to " + out_path)


if __name__ == "__main__":
    main()

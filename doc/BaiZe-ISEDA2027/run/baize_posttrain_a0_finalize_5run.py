#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A0 5-run finalize (baseline-nailed 令 §D Stage3 / §E 交付物 2+3).

Idempotent, safe to re-run as runs complete. For each run 1..5 with a
final_report.json:
  1. discover its eval-dir (batch dir under ~/eda_code_eval/) by matching
     run_dir/completed_code_generation.jsonl against on-disk
     completed_code_generation_<batch>.jsonl (size+sha1);
  2. if baseline_<label>_run<N>_pertask.json missing, generate it via
     baize_posttrain_baseline_pertask_profile.py (B5, this arm's own data);
  3. collect per-task pass_count across completed runs.
Then aggregate: 5-run mean±std of pass_rate; per-task pass distribution
0..N; pass_all / fail_all / partial; dominant fail_mode; four-metric means.
Writes baseline_<label>_5run_summary.json.

Protocol frozen (总纲 §2): 158 / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n.
Does NOT touch protocol / benchmark / check.py.
"""
import argparse, collections, hashlib, json, os, statistics, subprocess, sys

RUN_DIR_ROOT = "/tmp/posttrain_5run_eval"
EVAL_ROOT = os.path.expanduser("~/eda_code_eval")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PERTASK_PY = os.path.join(SCRIPT_DIR, "baize_posttrain_baseline_pertask_profile.py")


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 16)
            if not b:
                break
            h.update(b)
    return h.hexdigest(), os.path.getsize(path)


def discover_eval_dir(run_dir):
    """Match run_dir/completed_code_generation.jsonl to a batch dir under EVAL_ROOT."""
    src = os.path.join(run_dir, "completed_code_generation.jsonl")
    if not os.path.exists(src):
        return None
    src_sig = sha1_file(src)
    for name in os.listdir(EVAL_ROOT):
        full = os.path.join(EVAL_ROOT, name)
        if not os.path.isdir(full):
            continue
        cand = os.path.join(EVAL_ROOT, "completed_code_generation_%s.jsonl" % name)
        if os.path.exists(cand) and sha1_file(cand) == src_sig:
            return full
    return None


def run_pertask_profile(eval_dir, report, arm, run_n, out_path):
    cmd = [sys.executable, PERTASK_PY, "--eval-dir", eval_dir,
           "--report", report, "--arm", arm, "--run", str(run_n), "--out", out_path]
    print("[finalize] generating pertask:", out_path)
    r = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        print("[finalize] WARN pertask rc=%d: %s" % (r.returncode, r.stderr[-500:]), file=sys.stderr)
        return False
    return os.path.exists(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="A0_base")
    ap.add_argument("--runs", default="1,2,3,4,5")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--require-all", action="store_true",
                    help="only write summary json when all requested runs are done")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    out_path = args.out or "baseline_%s_5run_summary.json" % args.label
    run_nums = [int(x) for x in args.runs.split(",") if x.strip()]

    completed = []
    for n in run_nums:
        run_dir = os.path.join(RUN_DIR_ROOT, args.label, "run%d" % n)
        fr = os.path.join(run_dir, "final_report.json")
        if not os.path.exists(fr):
            print("[finalize] run%d: no final_report.json (running/failed) — skip" % n)
            continue
        try:
            rep = json.load(open(fr))
        except (OSError, ValueError) as e:
            print("[finalize] run%d: bad final_report: %s — skip" % (n, e))
            continue
        metrics = rep.get("metrics", {})
        pr = metrics.get("pass_rate", rep.get("pass_rate", rep.get("pass@1")))
        details = rep.get("details_per_task", {})
        eval_dir = discover_eval_dir(run_dir)
        pertask_path = os.path.join(SCRIPT_DIR, "baseline_%s_run%d_pertask.json" % (args.label, n))
        if not os.path.exists(pertask_path) and eval_dir and not args.dry_run:
            run_pertask_profile(eval_dir, fr, args.label, n, pertask_path)
        completed.append({"run": n, "run_dir": run_dir, "eval_dir": eval_dir,
                          "pass_rate": pr, "details": details,
                          "pertask_path": pertask_path if os.path.exists(pertask_path) else None,
                          "report_model_name": rep.get("model_name")})
        print("[finalize] run%d: pass_rate=%s n_details=%d eval_dir=%s pertask=%s"
              % (n, pr, len(details), eval_dir, os.path.exists(pertask_path)))

    print("[finalize] %d/%d runs completed" % (len(completed), len(run_nums)))
    if args.require_all and len(completed) < len(run_nums):
        print("[finalize] --require-all set and not all runs done; not writing summary.")
        return 0

    all_tasks = sorted(set(t for c in completed for t in c["details"].keys()))
    per_task_pass = {}
    per_task_failmode = collections.defaultdict(collections.Counter)
    pertask_loaded = {}
    for c in completed:
        pt = None
        if c["pertask_path"]:
            try:
                pt = json.load(open(c["pertask_path"])).get("per_task", {})
            except (OSError, ValueError):
                pt = None
        pertask_loaded[c["run"]] = bool(pt)
        for tid in all_tasks:
            d = c["details"].get(tid, {})
            per_task_pass.setdefault(tid, []).append(int(d.get("num_correct", 0)))
            if int(d.get("num_correct", 0)) == 0 and pt and tid in pt:
                fm = pt[tid].get("fail_mode")
                if fm:
                    per_task_failmode[tid][fm] += 1

    pass_dist = collections.Counter()
    for tid in all_tasks:
        pass_dist[sum(per_task_pass[tid])] += 1
    pass_dist_dict = {str(k): v for k, v in sorted(pass_dist.items())}
    return _emit(args, completed, run_nums, all_tasks, per_task_pass, per_task_failmode,
                 pass_dist_dict, pertask_loaded, out_path)

def _emit(args, completed, run_nums, all_tasks, per_task_pass, per_task_failmode,
          pass_dist_dict, pertask_loaded, out_path):
    n_completed = len(completed)
    pass_all = sum(1 for tid in all_tasks if sum(per_task_pass[tid]) == n_completed and n_completed)
    fail_all = sum(1 for tid in all_tasks if sum(per_task_pass[tid]) == 0 and n_completed)
    partial = len(all_tasks) - pass_all - fail_all

    failmode_summary = collections.Counter()
    for tid, cnt in per_task_failmode.items():
        failmode_summary[cnt.most_common(1)[0][0]] += 1

    rates = [c["pass_rate"] for c in completed if c["pass_rate"] is not None]
    mean_rate = statistics.mean(rates) if rates else None
    std_rate = statistics.stdev(rates) if len(rates) >= 2 else 0.0

    four_keys = ("agent_loop_entry_rate", "tool_call_count_mean", "error_rate_mean", "rag_queried_rate")
    four_runs = []
    for c in completed:
        if not c["pertask_path"]:
            continue
        try:
            d = json.load(open(c["pertask_path"]))
            four_runs.append(d.get("four_metric_means_over_tasks", {}))
        except (OSError, ValueError):
            pass
    four_mean = {}
    for k in four_keys:
        vals = [float(fr.get(k)) for fr in four_runs if fr.get(k) is not None]
        four_mean[k] = round(statistics.mean(vals), 4) if vals else None

    summary = {
        "arm": args.label,
        "source": "baseline-nailed §D Stage3 5-run finalize (MiniCPM5-2B base, .17 口径, 修复量尺)",
        "protocol": "158 / Pass@1 / 2500s / single-trace / 5-run / -p 8 -n (frozen)",
        "n_runs_completed": n_completed,
        "n_runs_requested": len(run_nums),
        "per_run_pass_rate": {str(c["run"]): c["pass_rate"] for c in completed},
        "five_run_mean": round(mean_rate, 6) if mean_rate is not None else None,
        "five_run_std": round(std_rate, 6) if len(rates) >= 2 else 0.0,
        "five_run_ci_note": "sd reported (n=%d); for paper use McNemar/paired-bootstrap on per-task outcomes" % n_completed,
        "per_task_pass_distribution_0_to_N": pass_dist_dict,
        "per_task_categories": {"pass_all_runs": pass_all, "fail_all_runs": fail_all,
                                "partial": partial, "n_tasks": len(all_tasks)},
        "dominant_fail_mode_over_failing_tasks": dict(failmode_summary.most_common()),
        "four_metric_means_over_runs": four_mean,
        "pertask_profile_present": {str(c["run"]): pertask_loaded.get(c["run"], False) for c in completed},
        "report_model_name_per_run": {str(c["run"]): c["report_model_name"] for c in completed},
        "note_model_identity": "final_report.model_name=zhulong_deepseek_v32 is a stale config.yaml tag; "
                               "authoritative identity = curl /v1/models id=minicpm5-2b + 158/158 sessions (B1 PASS)",
        "per_task_pass_count_by_run": {tid: per_task_pass[tid] for tid in all_tasks},
    }
    if args.dry_run:
        print("[dry-run] would write %s with %d runs" % (out_path, n_completed))
        print(json.dumps({k: v for k, v in summary.items() if k != "per_task_pass_count_by_run"},
                         ensure_ascii=False, indent=1))
        return 0
    with open(out_path, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("[finalize] WROTE", out_path)
    print("[finalize] %d/%d runs | mean=%.4f+/-%.4f | pass_all=%d fail_all=%d partial=%d"
          % (n_completed, len(run_nums), mean_rate or 0, std_rate, pass_all, fail_all, partial))
    return 0


if __name__ == "__main__":
    sys.exit(main())

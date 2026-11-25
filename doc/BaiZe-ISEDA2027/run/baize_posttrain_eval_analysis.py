#!/usr/bin/env python3
"""
baize_posttrain_eval_analysis.py — R39: Post-Training Evaluation Results Analysis Pipeline.

Takes real 5-run EDA-Eval-PyAether evaluation outputs (final_report.json) from
multiple checkpoints (baseline / anneal / SFT / RL) and produces:
  1. Per-task pass/fail matrices (158 tasks x 5 runs per ckpt)
  2. Pass@1 with 95% Wilson CI (mean across 5 runs)
  3. McNemar test for pairwise comparisons (paired by task, threshold=0.5)
  4. Paired bootstrap 95% CI for the difference in pass rates
  5. Per-scenario breakdown (Layout 64 / Schematic 47 / Design Mgmt 24 / Others 23)
  6. Pre-registered milestone tracking (M1=50% / M2=65% / M3=75% / M4=85%)
  7. Error type distribution (generation failure / execution failure / assertion failure)
  8. Self-contained HTML report (0 script, 0 external links)

Pure Python (no numpy/scipy) — uses only math, random, statistics, json, sys, os.
Compatible with Python 3.8+ (system python on .17).

Usage:
  # Analyze a single checkpoint (5 runs in a directory)
  python baize_posttrain_eval_analysis.py --ckpt baseline --dir /path/to/baseline_runs/

  # Compare two checkpoints
  python baize_posttrain_eval_analysis.py \\
      --ckpt baseline --dir /path/to/baseline_runs/ \\
      --ckpt sft --dir /path/to/sft_runs/ \\
      --compare

  # Dry-run with synthetic data (for testing without real evals)
  python baize_posttrain_eval_analysis.py --dry-run

  # Generate HTML report
  python baize_posttrain_eval_analysis.py --dry-run --html report_r39_eval_analysis_zh.html

R39 (2026-11-08): Built for Day-1+ evaluation analysis when GPU results arrive.
References: R19 (power analysis), task section 5.5 (evaluation protocol), section 4 step 4 (M1-M4).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics
import sys
from typing import Any, Dict, List, Optional, Tuple

# ─── Statistical helpers (pure Python, no scipy) ────────────────────────

def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))


def normal_ppf(p):
    """Inverse normal CDF (Acklam's algorithm)."""
    if p <= 0.0 or p >= 1.0:
        return float('-inf') if p <= 0 else float('inf')
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    elif p <= phigh:
        q = p - 0.5; r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)


def wilson_ci(pass_rate, n, confidence=0.95):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0
    z = normal_ppf((1 + confidence) / 2)
    denom = 1 + z**2 / n
    center = (pass_rate + z**2 / (2 * n)) / denom
    spread = z * math.sqrt(pass_rate * (1 - pass_rate) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, center - spread), min(1.0, center + spread)


def mcnemar_test(pass_a, pass_b):
    """McNemar's test with continuity correction."""
    n01 = sum(1 for a, b in zip(pass_a, pass_b) if not a and b)
    n10 = sum(1 for a, b in zip(pass_a, pass_b) if a and not b)
    n_disc = n01 + n10
    if n_disc == 0:
        return {"chi2": 0.0, "p_value": 1.0, "n01": 0, "n10": 0,
                "n_discordant": 0, "significant": False, "direction": "tie"}
    chi2 = (abs(n01 - n10) - 1) ** 2 / n_disc
    p = 2 * (1 - normal_cdf(math.sqrt(chi2))) if chi2 > 0 else 1.0
    direction = "B_better" if n01 > n10 else ("A_better" if n10 > n01 else "tie")
    return {"chi2": round(chi2, 4), "p_value": round(p, 6),
            "n01": n01, "n10": n10, "n_discordant": n_disc,
            "significant": p < 0.05, "direction": direction}


def paired_bootstrap_diff(pass_a, pass_b, n_bootstrap=10000, confidence=0.95, seed=42):
    """Paired bootstrap CI for the difference in pass rates (B - A)."""
    n = len(pass_a)
    if n == 0:
        return {"mean_diff": 0.0, "ci_lo": 0.0, "ci_hi": 0.0, "n_bootstrap": 0,
                "ci_significant": False}
    rng = random.Random(seed)
    rate_a = sum(pass_a) / n
    rate_b = sum(pass_b) / n
    obs_diff = rate_b - rate_a
    diffs = []
    for _ in range(n_bootstrap):
        idxs = [rng.randint(0, n - 1) for _ in range(n)]
        sa = sum(pass_a[i] for i in idxs) / n
        sb = sum(pass_b[i] for i in idxs) / n
        diffs.append(sb - sa)
    diffs.sort()
    alpha = (1 - confidence) / 2
    lo_idx = int(alpha * n_bootstrap)
    hi_idx = int((1 - alpha) * n_bootstrap)
    return {"mean_diff": round(obs_diff, 6),
            "ci_lo": round(diffs[lo_idx], 6),
            "ci_hi": round(diffs[hi_idx], 6),
            "ci_significant": diffs[lo_idx] > 0 or diffs[hi_idx] < 0,
            "n_bootstrap": n_bootstrap}


def paired_t_test(pass_a, pass_b):
    """Paired t-test on per-task pass rates."""
    n = len(pass_a)
    if n < 2:
        return {"t": 0.0, "p_value": 1.0, "mean_diff": 0.0, "se": 0.0}
    diffs = [float(b) - float(a) for a, b in zip(pass_a, pass_b)]
    md = statistics.mean(diffs)
    sd = statistics.stdev(diffs)
    se = sd / math.sqrt(n)
    if se == 0:
        return {"t": 0.0, "p_value": 1.0, "mean_diff": round(md, 6), "se": 0.0}
    t = md / se
    p = 2 * (1 - normal_cdf(abs(t)))
    return {"t": round(t, 4), "p_value": round(p, 6),
            "mean_diff": round(md, 6), "se": round(se, 6)}


# ─── Constants ───────────────────────────────────────────────────────────

DATASET_PATH = os.environ.get(
    "BAIZE_EVAL_DATASET",
    os.path.expanduser(
        "~/code/eda_fastmcp/pyAether-eval/original_dataset/"
        "EDA-Eval-PyAether-v20260311.jsonl"
    ),
)

MILESTONES = [
    {"name": "M0", "threshold": 0.36, "desc": "MiniCPM5-2B 零适配基线", "prior": "已实测"},
    {"name": "M1", "threshold": 0.50, "desc": "工具协议修好 (D1/D2/D6 改善)", "prior": "几近必然"},
    {"name": "M2", "threshold": 0.65, "desc": "+ 领域继续预训练 + SFT", "prior": "大概率"},
    {"name": "M3", "threshold": 0.75, "desc": "+ RL", "prior": "有望"},
    {"name": "M4", "threshold": 0.85, "desc": "逼近 DeepSeek-V4-Pro", "prior": "惊喜级别"},
]


# ─── Data loading ────────────────────────────────────────────────────────

def load_dataset_metadata(dataset_path=DATASET_PATH):
    """Load task_id to metadata mapping (scenario, category, etc.)."""
    meta = {}
    if not os.path.exists(dataset_path):
        return meta
    with open(dataset_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            tid = entry.get("task_id", "")
            m = entry.get("metadata", {})
            meta[tid] = {
                "scenario": m.get("scenario", "Unknown"),
                "category": m.get("category", "Unknown"),
                "apis_used": m.get("apis_used", []),
                "num_unique_apis": m.get("num_unique_apis", 0),
                "techlib_dependency": m.get("techlib_dependency", False),
                "lines_of_code": m.get("lines_of_code", 0),
            }
    return meta


def load_final_report(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def find_final_reports(directory):
    """Find all final_report.json files in a directory (sorted by mtime)."""
    results = []
    if not os.path.isdir(directory):
        return results
    for root, dirs, files in os.walk(directory):
        for fname in files:
            if fname == "final_report.json":
                results.append(os.path.join(root, fname))
    results.sort(key=lambda p: os.path.getmtime(p))
    return results


def extract_task_results(report):
    """Extract per-task results from a final_report.json."""
    details = report.get("details_per_task", {})
    results = {}
    for tid, d in details.items():
        exec_statuses = d.get("execution_statuses", [])
        gen_statuses = d.get("generation_statuses", [])
        passed = any(s == "passed" for s in exec_statuses)
        results[tid] = {
            "passed": passed, "pass_rate": d.get("pass_rate", 0.0),
            "num_correct": d.get("num_correct", 0),
            "num_samples": d.get("num_samples", 0),
            "error_types": d.get("error_types", []),
            "gen_status": gen_statuses[0] if gen_statuses else "unknown",
            "exec_status": exec_statuses[0] if exec_statuses else "unknown",
        }
    return results


def aggregate_runs(run_results):
    """Aggregate multiple runs into per-task pass/fail and overall metrics."""
    if not run_results:
        return {"task_ids": [], "pass_matrix": {}, "pass_rates": {},
                "overall_pass1": 0.0, "per_run_pass1": [], "mean_pass1": 0.0,
                "std_pass1": 0.0, "n_tasks": 0, "n_runs": 0}
    all_tids = set()
    for rr in run_results:
        all_tids.update(rr.keys())
    task_ids = sorted(all_tids)
    pass_matrix = {}
    pass_rates = {}
    for tid in task_ids:
        passes = []
        for rr in run_results:
            passes.append(rr[tid]["passed"] if tid in rr else False)
        pass_matrix[tid] = passes
        pass_rates[tid] = sum(passes) / len(passes) if passes else 0.0
    n_runs = len(run_results)
    per_run_pass1 = []
    for i in range(n_runs):
        n_pass = sum(1 for tid in task_ids if pass_matrix[tid][i])
        per_run_pass1.append(n_pass / len(task_ids) if task_ids else 0.0)
    mean_p1 = statistics.mean(per_run_pass1) if per_run_pass1 else 0.0
    std_p1 = statistics.stdev(per_run_pass1) if len(per_run_pass1) > 1 else 0.0
    return {
        "task_ids": task_ids, "pass_matrix": pass_matrix, "pass_rates": pass_rates,
        "overall_pass1": mean_p1, "per_run_pass1": per_run_pass1,
        "mean_pass1": mean_p1, "std_pass1": std_p1,
        "n_tasks": len(task_ids), "n_runs": n_runs,
    }


def per_scenario_breakdown(agg, metadata):
    """Break down pass rates by scenario."""
    scenarios = {}
    for tid in agg["task_ids"]:
        sc = metadata.get(tid, {}).get("scenario", "Unknown")
        if sc not in scenarios:
            scenarios[sc] = {"passes": 0.0, "total": 0}
        scenarios[sc]["passes"] += agg["pass_rates"].get(tid, 0.0)
        scenarios[sc]["total"] += 1
    results = []
    for sc, data in sorted(scenarios.items()):
        n = data["total"]
        pr = data["passes"] / n if n > 0 else 0.0
        ci_lo, ci_hi = wilson_ci(pr, n)
        results.append({"scenario": sc, "n_tasks": n, "pass_rate": pr,
                        "ci_lo": ci_lo, "ci_hi": ci_hi})
    return results


def error_type_analysis(agg, run_results):
    """Analyze error types across runs."""
    error_counts = {}
    gen_fail = exec_fail = assert_fail = total = 0
    for rr in run_results:
        for tid, d in rr.items():
            total += 1
            if not d["passed"]:
                gs = d.get("gen_status", "unknown")
                es = d.get("exec_status", "unknown")
                if gs in ("failure", "timeout"):
                    gen_fail += 1
                elif es in ("assertion_error", "wrong_answer"):
                    assert_fail += 1
                else:
                    exec_fail += 1
            for et in d.get("error_types", []):
                error_counts[et] = error_counts.get(et, 0) + 1
    return {
        "total_evals": total, "n_runs": len(run_results),
        "generation_failures": gen_fail, "execution_failures": exec_fail,
        "assertion_failures": assert_fail,
        "gen_fail_rate": gen_fail / total if total > 0 else 0.0,
        "exec_fail_rate": exec_fail / total if total > 0 else 0.0,
        "assert_fail_rate": assert_fail / total if total > 0 else 0.0,
        "error_type_counts": dict(sorted(error_counts.items(), key=lambda x: -x[1])),
    }


def milestone_check(pass1):
    """Check which milestones have been reached."""
    results = []
    for m in MILESTONES:
        reached = pass1 >= m["threshold"]
        results.append({
            "name": m["name"], "threshold": m["threshold"],
            "desc": m["desc"], "prior": m["prior"], "reached": reached,
            "gap": round(m["threshold"] - pass1, 4) if not reached else 0.0,
            "current": round(pass1, 4),
        })
    return results


def compare_ckpts(agg_a, agg_b, name_a, name_b):
    """Compare two checkpoints using paired statistical tests."""
    task_ids = sorted(set(agg_a["task_ids"]) & set(agg_b["task_ids"]))
    if not task_ids:
        return {"error": "No common tasks between checkpoints"}
    pass_a = [agg_a["pass_rates"][tid] >= 0.5 for tid in task_ids]
    pass_b = [agg_b["pass_rates"][tid] >= 0.5 for tid in task_ids]
    mc = mcnemar_test(pass_a, pass_b)
    bs = paired_bootstrap_diff(pass_a, pass_b)
    tt = paired_t_test(pass_a, pass_b)
    return {
        "name_a": name_a, "name_b": name_b, "n_common_tasks": len(task_ids),
        "pass1_a": round(agg_a["mean_pass1"], 6),
        "pass1_b": round(agg_b["mean_pass1"], 6),
        "std_a": round(agg_a["std_pass1"], 6),
        "std_b": round(agg_b["std_pass1"], 6),
        "diff": round(agg_b["mean_pass1"] - agg_a["mean_pass1"], 6),
        "mcnemar": mc, "bootstrap": bs, "ttest": tt,
    }


def generate_synthetic_eval(name, target_rate, n_tasks=158, n_runs=5, seed=42):
    """Generate a synthetic checkpoint evaluation for dry-run testing."""
    rng = random.Random(seed)
    run_results = []
    for _ in range(n_runs):
        rr = {}
        for i in range(1, n_tasks + 1):
            tid = "EDA-Eval-PyAether-%03d" % i
            if i <= 64:
                p = target_rate * 0.85
            elif i <= 111:
                p = target_rate * 0.75
            elif i <= 135:
                p = target_rate * 1.15
            else:
                p = target_rate * 1.10
            p = max(0.01, min(0.99, p))
            passed = rng.random() < p
            rr[tid] = {
                "passed": passed, "pass_rate": 1.0 if passed else 0.0,
                "num_correct": 1 if passed else 0, "num_samples": 1,
                "error_types": [] if passed else (
                    ["ImportError"] if rng.random() < 0.4 else ["AssertionError"]),
                "gen_status": "success",
                "exec_status": "passed" if passed else (
                    "assertion_error" if rng.random() < 0.5 else "failed"),
            }
        run_results.append(rr)
    return {"name": name, "run_results": run_results}


# ─── HTML report generation ──────────────────────────────────────────────

def _html_head():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R39 评测结果分析管线 — BaiZe Stage(ii) Post-Training</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333;line-height:1.6}
h1{color:#1a1a2e;border-bottom:3px solid #e94560;padding-bottom:10px}
h2{color:#16213e;margin-top:2em;border-left:4px solid #e94560;padding-left:10px}
h3{color:#0f3460;margin-top:1.5em}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14px}
th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}
th{background:#16213e;color:#fff;font-weight:600}
tr:nth-child(even){background:#f2f2f2}
.kpi{display:inline-block;background:#e94560;color:#fff;padding:6px 16px;border-radius:6px;margin:4px;font-size:18px;font-weight:bold}
.kpi-green{background:#27ae60}.kpi-orange{background:#e67e22}.kpi-blue{background:#3498db}
.ms-reached{background:#d4edda;color:#155724;padding:4px 8px;border-radius:4px;font-weight:bold}
.ms-not{background:#f8d7da;color:#721c24;padding:4px 8px;border-radius:4px}
.note{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:1em 0}
.danger{background:#f8d7da;border-left:4px solid #dc3545;padding:10px 15px;margin:1em 0}
.info{background:#d1ecf1;border-left:4px solid #17a2b8;padding:10px 15px;margin:1em 0}
.sc-bar{display:inline-block;height:20px;border-radius:3px;margin-right:5px;vertical-align:middle}
code{background:#f4f4f4;padding:2px 6px;border-radius:3px}
.card{background:#fff;border:1px solid #ddd;border-radius:8px;padding:15px;margin:10px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
</style>
</head>
<body>
<h1>R39 评测结果分析管线 — BaiZe Stage(ii) Post-Training</h1>
<p><small>生成时间: 2026-11-08 · R39 · 纯 Python 零依赖 · 用于 Day-1+ 真实评测结果分析</small></p>
"""


def _html_overview(ckpts, comparisons):
    n_c = len(ckpts)
    n_cmp = len(comparisons)
    return """
<h2>1. 管线概览</h2>
<div class="card">
<p><b>分析检查点数</b>: %d · <b>比较对数</b>: %d</p>
<p><b>评测协议</b>: EDA-Eval-PyAether 158 任务 · Pass@1 · 5-run mean ± std · 2500s/任务 · 单 trace · <code>-p 8 -n</code></p>
<p><b>统计方法</b>: Wilson CI (单臂) · McNemar 检验 (配对) · Paired Bootstrap 95%% CI (差值) · Paired t-test</p>
<p><b>预注册里程碑</b>: M0 36%% → M1 50%% → M2 65%% → M3 75%% → M4 85%%+ (先定后测)</p>
</div>
""" % (n_c, n_cmp)


def _html_ckpt_summary(ckpts):
    rows = ""
    for ckpt in ckpts:
        agg = ckpt["aggregated"]
        p1 = agg["mean_pass1"]
        std = agg["std_pass1"]
        ci_lo, ci_hi = wilson_ci(p1, agg["n_tasks"])
        ms = milestone_check(p1)
        reached = ", ".join(m["name"] for m in ms if m["reached"]) or "未达 M1"
        kpi_cls = "kpi-green" if p1 >= 0.5 else "kpi-orange"
        rows += (
            '<tr><td><b>%s</b></td>'
            '<td><span class="kpi %s">%.1f%%</span></td>'
            '<td>±%.1f%%</td><td>[%.1f%%, %.1f%%]</td>'
            '<td>%d</td><td>%d</td><td>%s</td></tr>'
        ) % (ckpt["name"], kpi_cls, p1*100, std*100,
             ci_lo*100, ci_hi*100, agg["n_tasks"], agg["n_runs"], reached)
    return '<h2>2. 各检查点 Pass@1 汇总</h2><table>' \
           '<tr><th>检查点</th><th>Pass@1 (mean)</th><th>Std</th><th>95%% Wilson CI</th><th>任务数</th><th>运行数</th><th>里程碑</th></tr>' \
           + rows + '</table>'


def _html_milestones(ckpts):
    best_p1 = max((c["aggregated"]["mean_pass1"] for c in ckpts), default=0.0)
    best_name = max(ckpts, key=lambda c: c["aggregated"]["mean_pass1"])["name"] if ckpts else "—"
    rows = ""
    for m in milestone_check(best_p1):
        status = '<span class="ms-reached">✅ 已达成</span>' if m["reached"] \
                 else '<span class="ms-not">⬜ 未达成</span>'
        gap = "+%.1fpp" % ((best_p1 - m["threshold"])*100) if m["reached"] \
              else "-%.1fpp" % (m["gap"]*100)
        rows += (
            '<tr><td><b>%s</b></td><td>%.0f%%</td><td>%s</td><td>%s</td>'
            '<td>%s (%.1f%%)</td><td>%s</td><td>%s</td></tr>'
        ) % (m["name"], m["threshold"]*100, m["desc"], m["prior"],
             best_name, best_p1*100, status, gap)
    return '<h2>3. 预注册里程碑追踪 (M0-M4)</h2><table>' \
           '<tr><th>里程碑</th><th>阈值</th><th>描述</th><th>先验判断</th><th>最佳检查点</th><th>状态</th><th>差距</th></tr>' \
           + rows + '</table>'


def _html_scenarios(ckpts, metadata):
    parts = '<h2>4. 分场景通过率</h2>'
    for ckpt in ckpts:
        agg = ckpt["aggregated"]
        breakdown = per_scenario_breakdown(agg, metadata)
        if not breakdown:
            continue
        parts += '<h3>%s</h3><table>' % ckpt["name"]
        parts += '<tr><th>场景</th><th>任务数</th><th>Pass@1</th><th>95%% CI</th><th>可视化</th></tr>'
        for sc in breakdown:
            bw = int(sc["pass_rate"] * 200)
            bc = "#27ae60" if sc["pass_rate"] >= 0.65 else ("#e67e22" if sc["pass_rate"] >= 0.4 else "#e74c3c")
            parts += (
                '<tr><td>%s</td><td>%d</td><td>%.1f%%</td>'
                '<td>[%.1f%%, %.1f%%]</td>'
                '<td><span class="sc-bar" style="width:%dpx;background:%s"></span> %.0f%%</td></tr>'
            ) % (sc["scenario"], sc["n_tasks"], sc["pass_rate"]*100,
                 sc["ci_lo"]*100, sc["ci_hi"]*100, bw, bc, sc["pass_rate"]*100)
        parts += '</table>'
    return parts


def _html_comparisons(comparisons):
    if not comparisons:
        return '<h2>5. 配对统计比较</h2><p>（仅一个检查点，无配对比较）</p>'
    parts = '<h2>5. 配对统计比较</h2><table>'
    parts += '<tr><th>比较</th><th>Pass@1 A</th><th>Pass@1 B</th><th>差值(B-A)</th>' \
             '<th>McNemar χ²</th><th>McNemar p</th><th>方向</th>' \
             '<th>Bootstrap 95%% CI</th><th>显著?</th></tr>'
    for cmp in comparisons:
        mc = cmp["mcnemar"]
        bs = cmp["bootstrap"]
        sig = "✅ 显著" if (mc["significant"] or bs.get("ci_significant", False)) else "❌ 不显著"
        direction = {"B_better": "B 优于 A", "A_better": "A 优于 B", "tie": "无差异"}.get(mc["direction"], "—")
        parts += (
            '<tr><td><b>%s</b> vs <b>%s</b></td><td>%.1f%%</td><td>%.1f%%</td>'
            '<td>%+.1fpp</td><td>%s</td><td>%s</td><td>%s</td>'
            '<td>[%+.1fpp, %+.1fpp]</td><td>%s</td></tr>'
        ) % (cmp["name_a"], cmp["name_b"], cmp["pass1_a"]*100, cmp["pass1_b"]*100,
             cmp["diff"]*100, mc["chi2"], mc["p_value"], direction,
             bs["ci_lo"]*100, bs["ci_hi"]*100, sig)
    parts += '</table>'
    parts += '<h3>McNemar 不一致对详情</h3><table>'
    parts += '<tr><th>比较</th><th>A失败B通过(n01)</th><th>A通过B失败(n10)</th><th>不一致总数</th><th>解读</th></tr>'
    for cmp in comparisons:
        mc = cmp["mcnemar"]
        interp = "B 在 %d 个任务上优于 A, A 在 %d 个任务上优于 B" % (mc["n01"], mc["n10"])
        parts += (
            '<tr><td>%s vs %s</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>'
        ) % (cmp["name_a"], cmp["name_b"], mc["n01"], mc["n10"], mc["n_discordant"], interp)
    parts += '</table>'
    return parts


def _html_errors(ckpts):
    parts = '<h2>6. 错误类型分析</h2>'
    for ckpt in ckpts:
        ea = ckpt.get("error_analysis", {})
        if not ea or ea.get("total_evals", 0) == 0:
            continue
        parts += '<h3>%s</h3><div class="card">' % ckpt["name"]
        parts += '<p><b>总评估数</b>: %d · <b>生成失败</b>: %d (%.1f%%) · ' \
                 '<b>执行失败</b>: %d (%.1f%%) · <b>断言失败</b>: %d (%.1f%%)</p>' % (
            ea["total_evals"], ea["generation_failures"], ea["gen_fail_rate"]*100,
            ea["execution_failures"], ea["exec_fail_rate"]*100,
            ea["assertion_failures"], ea["assert_fail_rate"]*100)
        if ea.get("error_type_counts"):
            parts += '<table><tr><th>错误类型</th><th>出现次数</th></tr>'
            for et, count in list(ea["error_type_counts"].items())[:15]:
                parts += '<tr><td><code>%s</code></td><td>%d</td></tr>' % (et, count)
            parts += '</table>'
        parts += '</div>'
    return parts


def _html_d1d6():
    return """
<h2>7. D1-D6 诊断指标映射</h2>
<div class="info">
<p>以下指标可在评测轨迹可用后从真实数据提取。Day-1 基线复测后自动填充。</p>
</div>
<table>
<tr><th>诊断项</th><th>计算方式</th><th>MiniCPM5-2B (36%)</th><th>DeepSeek (94%)</th><th>判读</th></tr>
<tr><td>D1 工具调用合法率</td><td>合法 tool_call / 总轮次</td><td>⏳ 待实测</td><td>0.6317</td><td>&lt;90% → SFT 可回收</td></tr>
<tr><td>D2 工具调用频次</td><td>每任务平均调用次数</td><td>⏳ 待实测</td><td>14.32</td><td>&lt;5 → 模型不用工具</td></tr>
<tr><td>D3 超时/截断比例</td><td>超时任务 / 总任务</td><td>⏳ 待实测</td><td>0.0%</td><td>高 → 长上下文适配</td></tr>
<tr><td>D4 失败类型分解</td><td>执行报错 vs 断言失败</td><td>⏳ 待实测</td><td>74% 执行 / 26% 断言</td><td>报错多 → SFT 语料</td></tr>
<tr><td>D5 per-scenario</td><td>各场景 Pass@1</td><td>⏳ 见上方分场景表</td><td>Schematic 66% &lt; Layout 64%</td><td>决定 SFT 配比</td></tr>
<tr><td>D6 平均迭代轮数</td><td>每任务平均对话轮数</td><td>⏳ 待实测</td><td>均值 5.01 / 中位 5</td><td>低 → RL 主战场</td></tr>
</table>
"""


def _html_usage():
    return """
<h2>8. 使用指南</h2>
<div class="note">
<p><b>典型用法（Day-1 基线复测后）</b>:</p>
<pre><code>
# 分析基线 (5-run)
python baize_posttrain_eval_analysis.py \\
    --ckpt baseline --dir ~/eda_code_eval/baseline_run/ \\
    --html report_eval_baseline_zh.html

# 比较基线 vs SFT
python baize_posttrain_eval_analysis.py \\
    --ckpt baseline --dir ~/eda_code_eval/baseline_run/ \\
    --ckpt sft --dir ~/eda_code_eval/sft_run/ \\
    --compare --html report_eval_baseline_vs_sft_zh.html

# 全链路比较 (baseline → SFT → RL)
python baize_posttrain_eval_analysis.py \\
    --ckpt baseline --dir ~/eda_code_eval/baseline/ \\
    --ckpt sft --dir ~/eda_code_eval/sft/ \\
    --ckpt rl --dir ~/eda_code_eval/rl/ \\
    --compare --html report_eval_full_comparison_zh.html
</code></pre>
<p><b>输入</b>: 每目录下含 5 个 final_report.json（每 run 一个）。脚本自动发现并聚合。</p>
</div>
"""


def _html_methodology():
    return """
<h2>9. 方法学说明</h2>
<div class="info">
<p><b>Pass@1</b>: 5 次独立运行（reshuffled, fresh context）的平均通过率。</p>
<p><b>Wilson CI</b>: Wilson score interval（优于正态近似，尤其在小样本/极端比例时）。</p>
<p><b>McNemar 检验</b>: 配对检验，n01 = A 失败 B 通过，n10 = A 通过 B 失败。连续性校正。p &lt; 0.05 → 显著。</p>
<p><b>Paired Bootstrap</b>: 10000 次有放回重采样，2.5%/97.5% 分位数作为 95% CI。CI 不含 0 → 显著。</p>
<p><b>预注册</b>: M0-M4 先定后测，避免事后合理化。</p>
</div>
"""


def _html_limitations():
    return """
<h2>10. 已知限制与后续扩展</h2>
<div class="danger">
<ul>
<li><b>D1/D2/D6 需 agent 模式轨迹</b>: final_report.json 仅含代码生成模式；agent 模式需从 api_conversation_history.json 提取。</li>
<li><b>单 run = 1 sample</b>: 代码生成模式每任务仅 1 sample。McNemar 阈值 0.5 = 3/5 通过。</li>
<li><b>Python 3.8 兼容</b>: 不使用 3.9+ 语法。</li>
</ul>
<p><b>后续扩展</b>: agent 轨迹分析(D1/D2/D6) · Pass@k · RL监控联动 · LaTeX表格片段</p>
</div>
<hr><p><small>R39 · BaiZe Stage(ii) · 2026-11-08 · 0 script · 0 外链</small></p>
</body></html>
"""


def generate_html_report(ckpts, comparisons, metadata, output_path):
    """Generate a self-contained HTML report."""
    html = _html_head() + _html_overview(ckpts, comparisons) + _html_ckpt_summary(ckpts) \
           + _html_milestones(ckpts) + _html_scenarios(ckpts, metadata) \
           + _html_comparisons(comparisons) + _html_errors(ckpts) + _html_d1d6() \
           + _html_usage() + _html_methodology() + _html_limitations()
    with open(output_path, "w") as f:
        f.write(html)
    return html


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="R39: Post-Training Evaluation Results Analysis Pipeline"
    )
    parser.add_argument("--ckpt", action="append", default=[],
                        help="Checkpoint name (repeatable)")
    parser.add_argument("--dir", action="append", default=[],
                        help="Directory containing final_report.json for a ckpt")
    parser.add_argument("--compare", action="store_true",
                        help="Compare all pairs of checkpoints")
    parser.add_argument("--dry-run", action="store_true",
                        help="Use synthetic data for testing")
    parser.add_argument("--html", default=None, help="Output HTML report path")
    parser.add_argument("--json", default=None, help="Output JSON raw data path")
    parser.add_argument("--dataset", default=DATASET_PATH,
                        help="Path to EDA-Eval-PyAether dataset")
    args = parser.parse_args()

    metadata = load_dataset_metadata(args.dataset)
    if metadata:
        print("[INFO] Loaded %d task metadata entries" % len(metadata))
    else:
        print("[WARN] Dataset not found at %s" % args.dataset)

    ckpts = []

    if args.dry_run:
        print("[DRY-RUN] Using synthetic data")
        for name, rate, seed in [("baseline", 0.36, 42), ("sft", 0.52, 43), ("rl", 0.68, 44)]:
            synth = generate_synthetic_eval(name, rate, seed=seed)
            run_results = synth["run_results"]
            agg = aggregate_runs(run_results)
            ea = error_type_analysis(agg, run_results)
            ckpts.append({"name": name, "run_results": run_results,
                          "aggregated": agg, "error_analysis": ea})
            print("  [SYNTH] %s: Pass@1=%.1f%% +-%.1f%% (%d tasks x %d runs)" % (
                name, agg["mean_pass1"]*100, agg["std_pass1"]*100,
                agg["n_tasks"], agg["n_runs"]))
    else:
        if len(args.ckpt) != len(args.dir):
            print("[ERROR] Number of --ckpt and --dir must match")
            sys.exit(1)
        for name, directory in zip(args.ckpt, args.dir):
            report_paths = find_final_reports(directory)
            if not report_paths:
                print("[WARN] No final_report.json in %s for '%s'" % (directory, name))
                continue
            print("[INFO] Ckpt '%s': %d run(s) in %s" % (name, len(report_paths), directory))
            run_results = []
            for rp in report_paths:
                report = load_final_report(rp)
                if report is None:
                    continue
                tr = extract_task_results(report)
                run_results.append(tr)
                mn = report.get("model_name", "unknown")
                pr = report.get("metrics", {}).get("pass_rate", 0.0)
                print("  Run %d: model=%s, pass_rate=%.1f%%, tasks=%d" % (
                    len(run_results), mn, pr*100, len(tr)))
            agg = aggregate_runs(run_results)
            ea = error_type_analysis(agg, run_results)
            ckpts.append({"name": name, "run_results": run_results,
                          "aggregated": agg, "error_analysis": ea})
            print("  -> Pass@1=%.1f%% +-%.1f%% (%d tasks x %d runs)" % (
                agg["mean_pass1"]*100, agg["std_pass1"]*100,
                agg["n_tasks"], agg["n_runs"]))

    if not ckpts:
        print("[ERROR] No checkpoint data available")
        sys.exit(1)

    comparisons = []
    if args.compare and len(ckpts) >= 2:
        for i in range(len(ckpts)):
            for j in range(i + 1, len(ckpts)):
                cmp = compare_ckpts(ckpts[i]["aggregated"], ckpts[j]["aggregated"],
                                     ckpts[i]["name"], ckpts[j]["name"])
                comparisons.append(cmp)
                mc = cmp["mcnemar"]
                bs = cmp["bootstrap"]
                print("\n[COMPARE] %s vs %s:" % (cmp["name_a"], cmp["name_b"]))
                print("  Pass@1: %.1f%% vs %.1f%% (diff=%+.1fpp)" % (
                    cmp["pass1_a"]*100, cmp["pass1_b"]*100, cmp["diff"]*100))
                print("  McNemar: chi2=%s, p=%s, n01=%d, n10=%d, dir=%s" % (
                    mc["chi2"], mc["p_value"], mc["n01"], mc["n10"], mc["direction"]))
                print("  Bootstrap: diff=%+.1fpp, 95%% CI=[%+.1fpp, %+.1fpp]" % (
                    bs["mean_diff"]*100, bs["ci_lo"]*100, bs["ci_hi"]*100))

    print("\n" + "=" * 60)
    print("R39 Evaluation Analysis Summary")
    print("=" * 60)
    for ckpt in ckpts:
        agg = ckpt["aggregated"]
        p1 = agg["mean_pass1"]
        std = agg["std_pass1"]
        ci_lo, ci_hi = wilson_ci(p1, agg["n_tasks"])
        ms = milestone_check(p1)
        reached = ", ".join(m["name"] for m in ms if m["reached"]) or "none"
        print("\n  %s:" % ckpt["name"])
        print("    Pass@1 = %.1f%% ± %.1f%%  (95%% CI: [%.1f%%, %.1f%%])" % (
            p1*100, std*100, ci_lo*100, ci_hi*100))
        print("    Milestones: %s" % reached)
        if metadata:
            for sc in per_scenario_breakdown(agg, metadata):
                print("    %-15s: %5.1f%%  (%d tasks)" % (
                    sc["scenario"], sc["pass_rate"]*100, sc["n_tasks"]))

    if args.html:
        html_path = args.html
        if not os.path.isabs(html_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)  # BaiZe-ISEDA2027/
            html_path = os.path.join(project_root, "reports", html_path)
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        generate_html_report(ckpts, comparisons, metadata, html_path)
        print("\n[HTML] Report: %s (%d bytes)" % (html_path, os.path.getsize(html_path)))

    if args.json:
        json_path = args.json
        if not os.path.isabs(json_path):
            json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), json_path)
        output = {
            "ckpts": [{"name": c["name"],
                        "aggregated": {k: v for k, v in c["aggregated"].items()
                                        if k != "pass_matrix"},
                        "error_analysis": c.get("error_analysis", {})} for c in ckpts],
            "comparisons": comparisons,
            "milestones": milestone_check(
                max((c["aggregated"]["mean_pass1"] for c in ckpts), default=0.0)),
        }
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        print("[JSON] Data: %s" % json_path)

    print("\n[DONE] R39 analysis complete.")


if __name__ == "__main__":
    main()

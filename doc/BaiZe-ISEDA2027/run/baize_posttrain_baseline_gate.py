#!/usr/bin/env python3
"""
baize_posttrain_baseline_gate.py — R44: Day-1 Baseline Reproduction Acceptance Gate
& Real Failure Trajectory Classifier.

Pre-registers the acceptance criteria for the 36% baseline reproduction BEFORE
seeing real data (avoids hindsight bias). When GPU arrives on 11/9 and the 5-run
baseline evaluation completes, this script:

  1. Ingests 5-run final_report.json results
  2. Computes Pass@1 mean ± std with Wilson CI
  3. Applies pre-registered acceptance band (36% ± 7pp = [29%, 43%])
  4. Classifies every failed task using the R4 five-category taxonomy
     (SYN / API / LOG / TMO / DEP)
  5. Compares failure distribution against DeepSeek reference (from R4)
  6. Produces GO / NO-GO / CONDITIONAL decision for proceeding to smoke test
  7. Generates self-contained HTML report (0 script, 0 external links)

Pure Python (no numpy/scipy) — uses only math, json, os, sys, statistics, random.
Compatible with Python 3.8+ (system python on .17).

Usage:
  # Real analysis (after 5-run baseline eval on 11/9)
  python baize_posttrain_baseline_gate.py --dir /path/to/baseline_5runs/

  # Dry-run with synthetic data (for testing without real evals)
  python baize_posttrain_baseline_gate.py --dry-run

  # Generate HTML report
  python baize_posttrain_baseline_gate.py --dry-run --html report_r44_baseline_gate_zh.html

R44 (2026-11-08): Pre-launch preparation for Day-1 baseline reproduction.
References: R4 (failure taxonomy), R19 (power analysis), R39 (eval analysis),
            task section 4 step 1-2 (baseline + failure trajectory collection).
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


def binomial_test(k, n, p0=0.36):
    """Two-sided exact binomial test (normal approximation for large n)."""
    if n == 0:
        return 1.0
    phat = k / n
    se = math.sqrt(p0 * (1 - p0) / n)
    if se == 0:
        return 1.0
    z = (phat - p0) / se
    return 2 * (1 - normal_cdf(abs(z)))


# ─── Pre-registered acceptance band ─────────────────────────────────────
# Rationale (pre-registered BEFORE seeing 11/9 data):
#   - Historical anchor: MiniCPM5-2B measured 36% Pass@1 (full harness, same protocol)
#   - n=158 tasks, binomial SE = sqrt(0.36*0.64/158) = 0.038 (3.8pp)
#   - 95% Wilson CI half-width ~ 7.5pp -> round to 7pp for practical band
#   - Acceptance band: [29%, 43%] = 36% +/- 7pp
#   - If measured mean falls in [29%, 43%] -> GO (baseline reproduced)
#   - If outside [29%, 43%] but inside [24%, 48%] -> CONDITIONAL (investigate)
#   - If outside [24%, 48%] -> NO-GO (something fundamentally wrong)
# These thresholds are FROZEN per pre-registration principle (task section 5 red line 5).

BASELINE_ANCHOR = 0.36
ACCEPTANCE_GO_LO = 0.29   # 36% - 7pp
ACCEPTANCE_GO_HI = 0.43   # 36% + 7pp
ACCEPTANCE_COND_LO = 0.24  # 36% - 12pp
ACCEPTANCE_COND_HI = 0.48  # 36% + 12pp
DEEPSEEK_REFERENCE = 0.94  # DeepSeek-V4-Pro full harness Pass@1

# ─── R4 Failure taxonomy (five categories) ──────────────────────────────
# Mapping from error_type strings to five-category taxonomy.
# Source: EXPERIMENTS_POSTTRAIN.md section R4, validated against 12 eval runs.

ERROR_CATEGORY_MAP = {
    "SyntaxError": "SYN",
    "IndentationError": "SYN",
    "Parse failed": "SYN",
    "ParseFailed": "SYN",
    "TypeError": "API",
    "ValueError": "API",
    "AttributeError": "API",
    "NameError": "API",
    "ImportError": "API",
    "KeyError": "API",
    "IndexError": "API",
    "AssertionError": "LOG",
    "Unknown Failure": "LOG",
    "UnknownFailure": "LOG",
    "Generation timeout": "TMO",
    "GenerationTimeout": "TMO",
    "Timeout": "TMO",
    "timeout": "TMO",
    "ModuleNotFoundError": "DEP",
    "FileNotFoundError": "DEP",
    "Generation failure": "SYN_API",  # split: if no code generated -> SYN, else API
    "GenerationFailure": "SYN_API",
    "RuntimeError": "RUNTIME",  # split: check if missing dependency
}

# R4 reference distributions (from EXPERIMENTS_POSTTRAIN.md section R4)
DEEPSEEK_ERROR_DIST = {
    "LOG": 0.667, "API": 0.207, "TMO": 0.143,
    "SYN": 0.015, "DEP": 0.002, "OTHER": 0.011,
}
WEAK_MODEL_ERROR_DIST = {
    "API": 0.655, "LOG": 0.256, "SYN": 0.047, "DEP": 0.047, "TMO": 0.0, "OTHER": 0.0,
}
PREDICTED_36PCT_DIST = {
    "API": 0.45, "LOG": 0.25, "TMO": 0.15, "SYN": 0.05, "DEP": 0.07, "OTHER": 0.03,
}

CATEGORY_NAMES = {
    "SYN": "语法错 (Syntax)",
    "API": "API 误用 (API Misuse)",
    "LOG": "逻辑错 (Logic Error)",
    "TMO": "超时 (Timeout)",
    "DEP": "缺依赖 (Missing Dependency)",
    "OTHER": "其他 (Other)",
}
CATEGORY_REMEDIATION = {
    "SYN": "SFT 注入 canonical_solution 结构模板",
    "API": "SFT 注入 PyAether API 参考语料 + 领域退火",
    "LOG": "RL(GRPO) 打磨查-写-改闭环 (核心 RL 价值)",
    "TMO": "上下文长度适配 + 推理加速",
    "DEP": "领域退火注入 techlib 语料 + SFT 环境配置",
    "OTHER": "个案分析",
}


def classify_error(error_type, gen_status="", exec_status=""):
    """Classify an error_type string into the R4 five-category taxonomy."""
    if not error_type or error_type == "unknown":
        if gen_status in ("timeout", "Generation timeout"):
            return "TMO"
        if gen_status in ("failure", "Generation failure"):
            return "SYN"
        if exec_status in ("timeout", "Timeout"):
            return "TMO"
        return "OTHER"
    cat = ERROR_CATEGORY_MAP.get(error_type, "")
    if cat == "SYN_API":
        if gen_status in ("failure", "Generation failure"):
            return "SYN"
        return "API"
    if cat == "RUNTIME":
        if "module" in error_type.lower() or "import" in error_type.lower():
            return "DEP"
        return "API"
    if cat:
        return cat
    return "OTHER"


def classify_task_failure(task_detail):
    """Classify all failure modes for a single task across runs."""
    categories = []
    error_types = task_detail.get("error_types", [])
    gen_statuses = task_detail.get("generation_statuses", [])
    exec_statuses = task_detail.get("execution_statuses", [])
    if error_types:
        for i, et in enumerate(error_types):
            gs = gen_statuses[i] if i < len(gen_statuses) else ""
            es = exec_statuses[i] if i < len(exec_statuses) else ""
            categories.append(classify_error(et, gs, es))
    else:
        n = max(len(gen_statuses), len(exec_statuses), 1)
        for i in range(n):
            gs = gen_statuses[i] if i < len(gen_statuses) else ""
            es = exec_statuses[i] if i < len(exec_statuses) else ""
            if es == "passed":
                continue
            categories.append(classify_error("", gs, es))
    return categories if categories else ["OTHER"]


# ─── Data loading (compatible with R39 eval_analysis.py) ────────────────

DATASET_PATH = os.environ.get(
    "BAIZE_EVAL_DATASET",
    os.path.expanduser(
        "~/code/eda_fastmcp/pyAether-eval/original_dataset/"
        "EDA-Eval-PyAether-v20260311.jsonl"
    ),
)


def load_dataset_metadata(dataset_path=DATASET_PATH):
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
                "num_unique_apis": m.get("num_unique_apis", 0),
                "techlib_dependency": m.get("techlib_dependency", False),
            }
    return meta


def load_final_report(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def find_final_reports(directory):
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
    details = report.get("details_per_task", {})
    results = {}
    for tid, d in details.items():
        exec_statuses = d.get("execution_statuses", [])
        gen_statuses = d.get("generation_statuses", [])
        passed = any(s == "passed" for s in exec_statuses)
        results[tid] = {
            "passed": passed,
            "pass_rate": d.get("pass_rate", 0.0),
            "num_correct": d.get("num_correct", 0),
            "num_samples": d.get("num_samples", 0),
            "error_types": d.get("error_types", []),
            "gen_status": gen_statuses[0] if gen_statuses else "unknown",
            "exec_status": exec_statuses[0] if exec_statuses else "unknown",
            "gen_statuses": gen_statuses,
            "exec_statuses": exec_statuses,
            "_raw": d,
        }
    return results


def aggregate_runs(run_results):
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
        passes = [rr[tid]["passed"] if tid in rr else False for rr in run_results]
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


# ─── Failure classification & analysis ──────────────────────────────────

def classify_all_failures(agg, run_results):
    """Classify every failed task-run using the R4 taxonomy."""
    category_counts = {"SYN": 0, "API": 0, "LOG": 0, "TMO": 0, "DEP": 0, "OTHER": 0}
    per_task_category = {}
    total_failures = 0
    for rr in run_results:
        for tid, d in rr.items():
            if d["passed"]:
                continue
            total_failures += 1
            cats = classify_task_failure(d["_raw"])
            if cats:
                primary = max(set(cats), key=cats.count)
                per_task_category.setdefault(tid, []).append(primary)
                category_counts[primary] = category_counts.get(primary, 0) + 1
    return category_counts, per_task_category, total_failures


def compare_distributions(observed, reference, total):
    """Compare observed failure distribution against a reference (chi-square)."""
    cats = sorted(set(list(observed.keys()) + list(reference.keys())))
    chi2 = 0.0
    contributions = {}
    for cat in cats:
        obs = observed.get(cat, 0)
        exp = reference.get(cat, 0) * total
        if exp > 0:
            contrib = (obs - exp) ** 2 / exp
            chi2 += contrib
            contributions[cat] = {"observed": obs, "expected": round(exp, 1),
                                  "contribution": round(contrib, 4)}
        elif obs > 0:
            chi2 += obs
            contributions[cat] = {"observed": obs, "expected": 0,
                                  "contribution": round(float(obs), 4)}
    df = len(cats) - 1
    p_value = 1 - normal_cdf(math.sqrt(2 * chi2) - math.sqrt(2 * df - 1)) if df > 0 else 1.0
    return {"chi2": round(chi2, 4), "df": df, "p_value": round(p_value, 6),
            "significant": p_value < 0.05, "contributions": contributions}


def per_scenario_failure(agg, per_task_category, metadata):
    """Break down failures by scenario."""
    scenarios = {}
    for tid in agg["task_ids"]:
        sc = metadata.get(tid, {}).get("scenario", "Unknown")
        if sc not in scenarios:
            scenarios[sc] = {"total": 0, "failed": 0, "categories": {}}
        scenarios[sc]["total"] += 1
        if tid in per_task_category:
            scenarios[sc]["failed"] += 1
            for cat in per_task_category[tid]:
                scenarios[sc]["categories"][cat] = scenarios[sc]["categories"].get(cat, 0) + 1
    results = []
    for sc, data in sorted(scenarios.items()):
        n = data["total"]
        fail = data["failed"]
        pr = (n - fail) / n if n > 0 else 0.0
        ci_lo, ci_hi = wilson_ci(pr, n)
        results.append({"scenario": sc, "n_tasks": n, "failed": fail,
                        "pass_rate": round(pr, 4), "ci_lo": round(ci_lo, 4),
                        "ci_hi": round(ci_hi, 4), "categories": data["categories"]})
    return results


# ─── Decision logic ─────────────────────────────────────────────────────

def make_decision(mean_pass1, std_pass1, n_runs, n_tasks, total_failures):
    """Produce GO / CONDITIONAL / NO-GO decision based on pre-registered criteria."""
    reasons = []
    decision = "GO"

    if ACCEPTANCE_GO_LO <= mean_pass1 <= ACCEPTANCE_GO_HI:
        reasons.append(f"OK Pass@1={mean_pass1:.1%} in GO band [{ACCEPTANCE_GO_LO:.0%}, {ACCEPTANCE_GO_HI:.0%}]")
    elif ACCEPTANCE_COND_LO <= mean_pass1 <= ACCEPTANCE_COND_HI:
        decision = "CONDITIONAL"
        reasons.append(f"WARN Pass@1={mean_pass1:.1%} in CONDITIONAL band, investigate")
    else:
        decision = "NO-GO"
        reasons.append(f"FAIL Pass@1={mean_pass1:.1%} outside band, baseline anomaly")

    if n_runs >= 5:
        reasons.append(f"OK runs={n_runs} (>=5, protocol compliant)")
    elif n_runs >= 3:
        if decision == "GO":
            decision = "CONDITIONAL"
        reasons.append(f"WARN runs={n_runs} (<5, incomplete protocol)")
    else:
        decision = "NO-GO"
        reasons.append(f"FAIL runs={n_runs} (<3, insufficient)")

    if n_tasks >= 150:
        reasons.append(f"OK tasks={n_tasks}/158 (>=150)")
    elif n_tasks >= 100:
        if decision == "GO":
            decision = "CONDITIONAL"
        reasons.append(f"WARN tasks={n_tasks}/158 (<150, partial)")
    else:
        decision = "NO-GO"
        reasons.append(f"FAIL tasks={n_tasks}/158 (<100, severe missing)")

    if std_pass1 <= 0.10:
        reasons.append(f"OK std={std_pass1:.4f} (<=0.10, stable)")
    else:
        if decision == "GO":
            decision = "CONDITIONAL"
        reasons.append(f"WARN std={std_pass1:.4f} (>0.10, unstable)")

    if total_failures == 0 and n_tasks > 0:
        decision = "NO-GO"
        reasons.append("FAIL zero failures (all passed? data anomaly)")
    elif total_failures > 0:
        reasons.append(f"OK failures={total_failures} (>0, expected)")

    n_pass = round(mean_pass1 * n_tasks)
    p_val = binomial_test(n_pass, n_tasks, BASELINE_ANCHOR)
    if p_val < 0.05:
        if decision == "GO":
            decision = "CONDITIONAL"
        reasons.append(f"WARN binomial p={p_val:.4f} (<0.05, significant deviation)")
    else:
        reasons.append(f"OK binomial p={p_val:.4f} (>=0.05, no significant deviation)")

    return {"decision": decision, "reasons": reasons,
            "mean_pass1": mean_pass1, "std_pass1": std_pass1,
            "n_runs": n_runs, "n_tasks": n_tasks, "binomial_p": p_val,
            "acceptance_band": f"[{ACCEPTANCE_GO_LO:.0%}, {ACCEPTANCE_GO_HI:.0%}]",
            "conditional_band": f"[{ACCEPTANCE_COND_LO:.0%}, {ACCEPTANCE_COND_HI:.0%}]"}


# ─── Synthetic data for dry-run ─────────────────────────────────────────

def generate_synthetic_5runs(n_tasks=158, base_pass_rate=0.36, seed=42):
    """Generate synthetic 5-run results mimicking final_report.json structure."""
    rng = random.Random(seed)
    error_pool = [
        ("AssertionError", "failure", "assertion_failed"),
        ("AssertionError", "failure", "assertion_failed"),
        ("Unknown Failure", "success", "unknown_failure"),
        ("TypeError", "success", "error"),
        ("ValueError", "success", "error"),
        ("AttributeError", "success", "error"),
        ("Generation timeout", "timeout", "timeout"),
        ("NameError", "success", "error"),
        ("SyntaxError", "failure", "parse_error"),
        ("RuntimeError", "success", "error"),
        ("ModuleNotFoundError", "success", "error"),
        ("Generation failure", "failure", "no_output"),
    ]
    runs = []
    for run_idx in range(5):
        report = {"details_per_task": {}}
        for tid in range(1, n_tasks + 1):
            task_id = f"task_{tid:03d}"
            passed = rng.random() < base_pass_rate
            err = rng.choice(error_pool)
            report["details_per_task"][task_id] = {
                "execution_statuses": ["passed"] if passed else [err[2]],
                "generation_statuses": ["success"] if passed else [err[1]],
                "pass_rate": 1.0 if passed else 0.0,
                "num_correct": 1 if passed else 0,
                "num_samples": 1,
                "error_types": [] if passed else [err[0]],
            }
        runs.append(report)
    return runs


# ─── HTML report ────────────────────────────────────────────────────────

def generate_html_report(agg, decision, category_counts, total_failures,
                         per_task_category, scenario_data, dist_comparison,
                         metadata, ref_agg=None):
    """Generate self-contained HTML report (0 script, 0 external links)."""
    mean_p = agg["mean_pass1"]
    std_p = agg["std_pass1"]
    n_runs = agg["n_runs"]
    n_tasks = agg["n_tasks"]
    total_cat = sum(category_counts.values()) or 1

    dist_rows = ""
    for cat in ["SYN", "API", "LOG", "TMO", "DEP", "OTHER"]:
        obs = category_counts.get(cat, 0)
        obs_pct = obs / total_cat * 100 if total_cat > 0 else 0
        ref_ds = DEEPSEEK_ERROR_DIST.get(cat, 0) * 100
        ref_wk = WEAK_MODEL_ERROR_DIST.get(cat, 0) * 100
        pred = PREDICTED_36PCT_DIST.get(cat, 0) * 100
        name = CATEGORY_NAMES.get(cat, cat)
        rem = CATEGORY_REMEDIATION.get(cat, "-")
        dist_rows += f'<tr><td><b>{cat}</b></td><td>{name}</td><td>{obs} ({obs_pct:.1f}%)</td><td>{pred:.1f}%</td><td>{ref_ds:.1f}%</td><td>{ref_wk:.1f}%</td><td>{rem}</td></tr>\n'

    sc_rows = ""
    for sc in scenario_data:
        cat_str = ", ".join(f"{k}:{v}" for k, v in sorted(sc["categories"].items())) or "-"
        sc_rows += f'<tr><td>{sc["scenario"]}</td><td>{sc["n_tasks"]}</td><td>{sc["failed"]}</td><td>{sc["pass_rate"]:.1%}</td><td>[{sc["ci_lo"]:.1%}, {sc["ci_hi"]:.1%}]</td><td>{cat_str}</td></tr>\n'

    run_rows = ""
    for i, rp in enumerate(agg["per_run_pass1"]):
        run_rows += f'<tr><td>Run {i+1}</td><td>{rp:.1%}</td><td>{round(rp*n_tasks)}/{n_tasks}</td></tr>\n'

    dec_color = {"GO": "#28a745", "CONDITIONAL": "#ffc107", "NO-GO": "#dc3545"}.get(decision["decision"], "#6c757d")
    dec_bg = {"GO": "#d4edda", "CONDITIONAL": "#fff3cd", "NO-GO": "#f8d7da"}.get(decision["decision"], "#e2e3e5")
    reasons_html = "<br>".join(decision["reasons"])

    comp_html = ""
    if dist_comparison:
        comp_rows = ""
        for cat, data in sorted(dist_comparison["contributions"].items()):
            comp_rows += f'<tr><td>{cat}</td><td>{data["observed"]}</td><td>{data["expected"]}</td><td>{data["contribution"]}</td></tr>\n'
        comp_html = f'<h2>7. DeepSeek 卡方检验</h2><p>chi2={dist_comparison["chi2"]}, df={dist_comparison["df"]}, p={dist_comparison["p_value"]}</p><table><tr><th>类别</th><th>实测</th><th>期望</th><th>贡献</th></tr>{comp_rows}</table>'

    ref_html = ""
    if ref_agg:
        ref_html = f'<h2>8. 参考模型对比</h2><table><tr><th>模型</th><th>Pass@1</th><th>std</th><th>runs</th><th>tasks</th></tr><tr><td>MiniCPM5-2B</td><td>{mean_p:.1%}</td><td>{std_p:.4f}</td><td>{n_runs}</td><td>{n_tasks}</td></tr><tr><td>参考</td><td>{ref_agg["mean_pass1"]:.1%}</td><td>{ref_agg["std_pass1"]:.4f}</td><td>{ref_agg["n_runs"]}</td><td>{ref_agg["n_tasks"]}</td></tr><tr><td>差距</td><td>{(ref_agg["mean_pass1"]-mean_p):.1%}</td><td>-</td><td>-</td><td>-</td></tr></table>'

    return _build_html(mean_p, std_p, n_runs, n_tasks, total_failures,
                       decision, dec_color, dec_bg, reasons_html, run_rows,
                       dist_rows, sc_rows, comp_html, ref_html)


def _build_html(mean_p, std_p, n_runs, n_tasks, total_failures,
                decision, dec_color, dec_bg, reasons_html, run_rows,
                dist_rows, sc_rows, comp_html, ref_html):
    """Build the final HTML string."""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R44 基线复现验收门</title><style>
body{{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:20px;color:#333}}
h1{{color:#1a1a2e;border-bottom:3px solid #0f3460;padding-bottom:10px}}
h2{{color:#16213e;margin-top:30px;border-left:4px solid #0f3460;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:15px 0}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}
th{{background:#0f3460;color:white}}
tr:nth-child(even){{background:#f8f9fa}}
.decision-box{{display:inline-block;padding:15px 30px;border-radius:8px;font-size:24px;font-weight:bold;color:{dec_color};background:{dec_bg};border:2px solid {dec_color};margin:10px 0}}
.metric{{display:inline-block;margin:5px 15px;padding:8px 16px;background:#e8eaf6;border-radius:4px}}
.info{{background:#e3f2fd;padding:10px;border-radius:4px;border-left:4px solid #2196f3}}
</style></head><body>
<h1>R44 基线复现验收门 &amp; 失败轨迹分类器</h1>
<p><small>R44 (2026-11-08) · Day-1 准备 · 零 GPU · 纯 Python 3.8+ · 预注册验收标准</small></p>
<div class="info"><b>预注册说明</b>：验收带 [29%, 43%] = 36% ± 7pp 在见到 11/9 真实数据前冻结。
依据：n=158 二项分布 SE ≈ 3.8pp，95% Wilson CI 半宽 ≈ 7.5pp → 取整 7pp。遵循预注册原则。</div>
<h2>1. 决策结果</h2>
<div class="decision-box">{decision["decision"]}</div>
<div style="margin:15px 0">
<span class="metric">Pass@1: <b>{mean_p:.1%}</b></span>
<span class="metric">std: {std_p:.4f}</span>
<span class="metric">runs: {n_runs}</span>
<span class="metric">tasks: {n_tasks}/158</span>
<span class="metric">binomial p: {decision["binomial_p"]:.4f}</span>
</div>
<div style="background:{dec_bg};padding:15px;border-radius:8px;border-left:4px solid {dec_color}"><b>决策理由：</b><br>{reasons_html}</div>
<h2>2. 验收带定义（预注册）</h2>
<table><tr><th>判定</th><th>Pass@1 范围</th><th>含义</th></tr>
<tr><td style="color:#28a745;font-weight:bold">GO</td><td>[29%, 43%]</td><td>基线复现成功，可进入 smoke test</td></tr>
<tr><td style="color:#856404;font-weight:bold">CONDITIONAL</td><td>[24%, 29%) ∪ (43%, 48%]</td><td>需调查偏差原因再决定</td></tr>
<tr><td style="color:#dc3545;font-weight:bold">NO-GO</td><td>&lt;24% 或 &gt;48%</td><td>基线异常，先 debug</td></tr></table>
<h2>3. 逐运行 Pass@1</h2>
<table><tr><th>运行</th><th>Pass@1</th><th>通过/总</th></tr>{run_rows}
<tr style="font-weight:bold;background:#e8eaf6"><td>Mean ± std</td><td>{mean_p:.1%} ± {std_p:.4f}</td><td>-</td></tr></table>
<h2>4. 失败模式分类（R4 五分类法）</h2>
<p>总失败 task-run 数：<b>{total_failures}</b></p>
<table><tr><th>代码</th><th>类别</th><th>实测</th><th>R4预测</th><th>DeepSeek</th><th>弱模型</th><th>治理</th></tr>{dist_rows}</table>
<h2>5. Per-Scenario 失败分解</h2>
<table><tr><th>场景</th><th>任务数</th><th>失败数</th><th>通过率</th><th>95%CI</th><th>失败类别</th></tr>{sc_rows}</table>
<h2>6. 与 R4 预测分布对比</h2>
<div class="info">R4 基于 DeepSeek + aether_coder 外推构建 36% 侧预测。关键预测：API 误用 40-60%。若显著偏离 → 调整 SFT 数据配比。</div>
{comp_html}{ref_html}
<h2>9. Day-1 后续行动</h2>
<div class="info"><ol>
<li><b>GO</b>：执行 smoke test (GRPO R0, 10 iters)</li>
<li><b>CONDITIONAL</b>：检查 vLLM 参数、超时、158 题全覆盖</li>
<li><b>NO-GO</b>：检查模型加载、endpoint、harness driver</li>
<li>用实测分布替换 R4 外推假设，调整 SFT 配比</li>
</ol></div>
<hr><p><small>R44 · baize_posttrain_baseline_gate.py · 2026-11-08 · 0 script · 0 外链</small></p>
</body></html>"""


# ─── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="R44: Day-1 Baseline Reproduction Acceptance Gate & Failure Classifier"
    )
    parser.add_argument("--dir", help="Directory containing 5-run final_report.json files")
    parser.add_argument("--ref-dir", help="Optional reference checkpoint directory")
    parser.add_argument("--dry-run", action="store_true", help="Use synthetic data for testing")
    parser.add_argument("--html", help="Output HTML report path")
    parser.add_argument("--json-out", help="Output JSON results path")
    args = parser.parse_args()

    if args.dry_run:
        print("=== R44 Dry-Run Mode (synthetic data) ===")
        synthetic_reports = generate_synthetic_5runs(n_tasks=158, base_pass_rate=0.36, seed=42)
        run_results = [extract_task_results(r) for r in synthetic_reports]
        ref_run_results = None
    else:
        if not args.dir:
            print("Error: --dir is required (or use --dry-run)")
            sys.exit(1)
        report_paths = find_final_reports(args.dir)
        if not report_paths:
            print(f"Error: No final_report.json found in {args.dir}")
            sys.exit(1)
        print(f"Found {len(report_paths)} final_report.json files")
        run_results = []
        for p in report_paths:
            report = load_final_report(p)
            if report:
                run_results.append(extract_task_results(report))
        ref_run_results = None
        if args.ref_dir:
            ref_paths = find_final_reports(args.ref_dir)
            ref_run_results = []
            for p in ref_paths:
                report = load_final_report(p)
                if report:
                    ref_run_results.append(extract_task_results(report))

    agg = aggregate_runs(run_results)
    ref_agg = aggregate_runs(ref_run_results) if ref_run_results else None
    metadata = load_dataset_metadata()
    category_counts, per_task_category, total_failures = classify_all_failures(agg, run_results)
    scenario_data = per_scenario_failure(agg, per_task_category, metadata)
    dist_comparison = compare_distributions(category_counts, DEEPSEEK_ERROR_DIST, total_failures) if total_failures > 0 else None
    decision = make_decision(agg["mean_pass1"], agg["std_pass1"], agg["n_runs"],
                             agg["n_tasks"], total_failures)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  R44 Baseline Reproduction Acceptance Gate")
    print(f"{'='*60}")
    print(f"\n  Pass@1: {agg['mean_pass1']:.1%} +/- {agg['std_pass1']:.4f}")
    print(f"  Runs: {agg['n_runs']}  Tasks: {agg['n_tasks']}/158")
    print(f"  Total failures: {total_failures}")
    print(f"\n  Decision: {decision['decision']}")
    print(f"  Acceptance band: {decision['acceptance_band']}")
    print(f"  Binomial test p: {decision['binomial_p']:.4f}")
    print(f"\n  Reasons:")
    for r in decision["reasons"]:
        print(f"    {r}")
    print(f"\n  Failure classification (R4 taxonomy):")
    total_cat = sum(category_counts.values()) or 1
    for cat in ["SYN", "API", "LOG", "TMO", "DEP", "OTHER"]:
        n = category_counts.get(cat, 0)
        print(f"    {cat}: {n} ({n/total_cat*100:.1f}%)  [predicted: {PREDICTED_36PCT_DIST.get(cat,0)*100:.1f}%]")
    print(f"\n  Per-scenario:")
    for sc in scenario_data:
        print(f"    {sc['scenario']}: {sc['pass_rate']:.1%} ({sc['n_tasks']-sc['failed']}/{sc['n_tasks']})")
    if dist_comparison:
        print(f"\n  Chi-square vs DeepSeek: chi2={dist_comparison['chi2']}, p={dist_comparison['p_value']}")

    if args.json_out:
        output = {"r44_baseline_gate": {
            "mean_pass1": agg["mean_pass1"], "std_pass1": agg["std_pass1"],
            "n_runs": agg["n_runs"], "n_tasks": agg["n_tasks"],
            "total_failures": total_failures, "decision": decision,
            "category_counts": category_counts, "per_scenario": scenario_data,
            "dist_comparison": dist_comparison, "per_run_pass1": agg["per_run_pass1"],
        }}
        with open(args.json_out, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n  JSON output: {args.json_out}")

    if args.html:
        html = generate_html_report(agg, decision, category_counts, total_failures,
                                    per_task_category, scenario_data, dist_comparison,
                                    metadata, ref_agg)
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  HTML report: {args.html}")

    print(f"\n{'='*60}")
    return 0 if decision["decision"] != "NO-GO" else 1


if __name__ == "__main__":
    sys.exit(main())

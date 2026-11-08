#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
baize_posttrain_stat_power_analysis.py — R72: Statistical Power Analysis for
Pre-Registered Success Ladder (M1-M4)

Computes minimum detectable effect size, McNemar test power, paired bootstrap
power, required runs, and pre-registered decision rules for 158 tasks x N runs.
Pure Python 3.8+ stdlib (no numpy/scipy).

Usage:
  python3 baize_posttrain_stat_power_analysis.py                  # Full analysis
  python3 baize_posttrain_stat_power_analysis.py --verbose        # Detailed output
  python3 baize_posttrain_stat_power_analysis.py --html           # Generate HTML report
  python3 baize_posttrain_stat_power_analysis.py --json           # Generate JSON output
  python3 baize_posttrain_stat_power_analysis.py --n-runs 5       # Custom run count
  python3 baize_posttrain_stat_power_analysis.py --n-tasks 158    # Custom task count
  python3 baize_posttrain_stat_power_analysis.py --alpha 0.05     # Significance level
  python3 baize_posttrain_stat_power_analysis.py --n-sims 10000   # Simulation iterations

WARNING: Surrogate results are NOT transferable to BaiZe.
"""

import argparse
import json
import math
import os
import random
import statistics
import sys
from datetime import datetime

# ── Constants ──
DEFAULT_N_TASKS = 158
DEFAULT_N_RUNS = 5
DEFAULT_ALPHA = 0.05
DEFAULT_N_SIMS = 10000
RANDOM_SEED = 42

# Pre-registered success ladder (from task book section 4 step 4)
SUCCESS_LADDER = [
    ("Baseline", 0.36, "MiniCPM5-2B, zero adaptation"),
    ("M1", 0.50, "Tool protocol fixed (D1/D2/D6)"),
    ("M2", 0.65, "+ domain CPT + SFT"),
    ("M3", 0.75, "+ RL"),
    ("M4", 0.85, "Approaching DeepSeek-V4-Pro"),
]

# ── Statistical utilities (pure stdlib) ──

def binomial_pmf(n, k, p):
    """P(X=k) for X ~ Binomial(n, p)."""
    if k < 0 or k > n:
        return 0.0
    log_coeff = 0.0
    for i in range(1, k + 1):
        log_coeff += math.log(n - k + i) - math.log(i)
    log_prob = log_coeff + k * math.log(p + 1e-300) + (n - k) * math.log(1 - p + 1e-300)
    return math.exp(log_prob)


def binomial_cdf(n, k, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    return sum(binomial_pmf(n, i, p) for i in range(k + 1))


def normal_cdf(x, mu=0, sigma=1):
    """Standard normal CDF using error function."""
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def normal_ppf(p, mu=0, sigma=1):
    """Inverse normal CDF using Acklam's algorithm."""
    if p <= 0:
        return float('-inf')
    if p >= 1:
        return float('inf')
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700998e-01,
         2.445134137142996e+00, 3.754408661907416e+00]
    p_low = 0.02425
    p_high = 1 - p_low
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
            (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    return mu + sigma * x


def mc_nemar_test(b_discordant, c_discordant):
    """McNemar's test for paired binary outcomes.
    b = #tasks where A passes B fails; c = #tasks where A fails B passes.
    Returns (statistic, p_value_approx)."""
    n = b_discordant + c_discordant
    if n == 0:
        return 0.0, 1.0
    stat = (abs(b_discordant - c_discordant) - 1) ** 2 / n
    if n < 25:
        k = min(b_discordant, c_discordant)
        p_val = min(2 * binomial_cdf(n, k, 0.5), 1.0)
        return stat, p_val
    else:
        p_val = 2 * (1 - normal_cdf(math.sqrt(stat)))
        return stat, p_val


def paired_bootstrap_ci(deltas, n_bootstrap, rng, alpha=0.05):
    """Paired bootstrap CI for mean difference.
    Returns (lower, upper, point_estimate)."""
    n = len(deltas)
    if n == 0:
        return (0, 0, 0)
    point_est = statistics.mean(deltas)
    boot_means = []
    for _ in range(n_bootstrap):
        sample = [deltas[rng.randint(0, n - 1)] for _ in range(n)]
        boot_means.append(statistics.mean(sample))
    boot_means.sort()
    lower_idx = int(n_bootstrap * alpha / 2)
    upper_idx = int(n_bootstrap * (1 - alpha / 2))
    return (boot_means[lower_idx], boot_means[upper_idx], point_est)


# ── Analysis functions ──

def analyze_mdes(n_tasks, n_runs, alpha=DEFAULT_ALPHA):
    """Minimum Detectable Effect Size for paired comparison."""
    results = []
    for p_a in [0.36, 0.50, 0.65, 0.75, 0.85]:
        for delta_pp in [5, 10, 15, 20, 25, 30]:
            p_b = p_a + delta_pp / 100
            if p_b > 1:
                continue
            disc_rate = p_a * (1 - p_b) + (1 - p_a) * p_b
            eff_disc = disc_rate * (1 - 2 * p_a * (1 - p_a) / n_runs - 2 * p_b * (1 - p_b) / n_runs)
            eff_disc = max(eff_disc, disc_rate * 0.5)
            n_discordant = int(n_tasks * eff_disc)
            min_k = 0
            for k in range(n_discordant // 2 + 1):
                p_val = 2 * binomial_cdf(n_discordant, k, 0.5)
                if p_val < alpha:
                    min_k = k
                    break
            if min_k > 0:
                mdes_pp = (n_discordant / 2 - min_k) * 2 / n_tasks * 100
            else:
                mdes_pp = n_discordant / n_tasks * 100
            power_approx = 1 - binomial_cdf(n_discordant, min_k, 0.5 + delta_pp / 200)
            results.append({
                "p_a": p_a, "delta_pp": delta_pp, "p_b": p_b,
                "disc_rate": round(disc_rate, 4), "eff_disc": round(eff_disc, 4),
                "n_discordant": n_discordant, "min_k_for_sig": min_k,
                "mdes_pp": round(mdes_pp, 2), "power_approx": round(power_approx, 4),
            })
    return results


def simulate_mc_nemar_power(n_tasks, p_a, p_b, n_runs, n_sims, alpha, rng):
    """Monte Carlo simulation of McNemar's test power."""
    rejections = 0
    total_b = total_c = total_disc = 0
    for _ in range(n_sims):
        b_disc = c_disc = 0
        for _ in range(n_tasks):
            pass_a = sum(1 for _ in range(n_runs) if rng.random() < p_a)
            pass_b = sum(1 for _ in range(n_runs) if rng.random() < p_b)
            rate_a = pass_a / n_runs
            rate_b = pass_b / n_runs
            if rate_a > 0.5 and rate_b <= 0.5:
                b_disc += 1
            elif rate_a <= 0.5 and rate_b > 0.5:
                c_disc += 1
        total_b += b_disc
        total_c += c_disc
        total_disc += b_disc + c_disc
        _, p_val = mc_nemar_test(b_disc, c_disc)
        if p_val < alpha:
            rejections += 1
    return rejections / n_sims, total_b / n_sims, total_c / n_sims, total_disc / n_sims


def simulate_bootstrap_power(n_tasks, p_a, p_b, n_runs, n_sims, n_boot, alpha, rng):
    """Monte Carlo simulation of paired bootstrap test power."""
    rejections = 0
    for _ in range(n_sims):
        deltas = []
        for _ in range(n_tasks):
            pass_a = sum(1 for _ in range(n_runs) if rng.random() < p_a)
            pass_b = sum(1 for _ in range(n_runs) if rng.random() < p_b)
            deltas.append(pass_b / n_runs - pass_a / n_runs)
        lower, upper, _ = paired_bootstrap_ci(deltas, n_boot, rng, alpha)
        if lower > 0 or upper < 0:
            rejections += 1
    return rejections / n_sims


def find_min_runs_for_power(n_tasks, p_a, p_b, target_power, n_sims, alpha, rng, max_runs=20):
    """Binary search for minimum number of runs to achieve target_power."""
    lo, hi = 1, max_runs
    best = max_runs
    while lo <= hi:
        mid = (lo + hi) // 2
        power, _, _, _ = simulate_mc_nemar_power(n_tasks, p_a, p_b, mid, max(n_sims // 4, 200), alpha, rng)
        if power >= target_power:
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return best


def run_full_analysis(n_tasks, n_runs, alpha, n_sims, verbose=False):
    """Run complete statistical power analysis."""
    rng = random.Random(RANDOM_SEED)
    results = {}

    # ── Section 1: MDES Table ──
    if verbose:
        print("\n=== Section 1: Minimum Detectable Effect Size (MDES) ===")
        print(f"  N_tasks={n_tasks}, N_runs={n_runs}, alpha={alpha}")
    mdes_table = analyze_mdes(n_tasks, n_runs, alpha)
    results["mdes_table"] = mdes_table
    if verbose:
        print(f"  {'p_a':>6} {'dpp':>5} {'p_b':>6} {'disc%':>6} {'n_disc':>7} {'MDES':>7} {'power':>7}")
        for r in mdes_table:
            print(f"  {r['p_a']:>6.2f} {r['delta_pp']:>5} {r['p_b']:>6.2f} "
                  f"{r['eff_disc']*100:>6.2f} {r['n_discordant']:>7} "
                  f"{r['mdes_pp']:>7.2f} {r['power_approx']:>7.4f}")

    # ── Section 2: McNemar Power for Success Ladder ──
    if verbose:
        print("\n=== Section 2: McNemar Test Power for Success Ladder ===")
    mc_power = []
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        delta_pp = (p_b - p_a) * 100
        power, mean_b, mean_c, mean_disc = simulate_mc_nemar_power(
            n_tasks, p_a, p_b, n_runs, n_sims, alpha, rng)
        entry = {
            "comparison": f"{name_a}({p_a*100:.0f}%) -> {name_b}({p_b*100:.0f}%)",
            "delta_pp": delta_pp, "power": round(power, 4),
            "mean_b_disc": round(mean_b, 2), "mean_c_disc": round(mean_c, 2),
            "mean_discordant": round(mean_disc, 2),
            "verdict": "ADEQUATE" if power >= 0.80 else "INSUFFICIENT",
        }
        mc_power.append(entry)
        if verbose:
            print(f"  {entry['comparison']:>30}  d={delta_pp:>5.1f}pp  "
                  f"power={power:.4f}  disc={mean_disc:.1f}  -> {entry['verdict']}")
    results["mc_nemar_power"] = mc_power

    # ── Section 3: Bootstrap Power ──
    if verbose:
        print("\n=== Section 3: Paired Bootstrap Test Power ===")
    boot_power = []
    n_boot = min(2000, n_sims)
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        delta_pp = (p_b - p_a) * 100
        bp = simulate_bootstrap_power(
            n_tasks, p_a, p_b, n_runs, min(n_sims // 5, 2000), n_boot, alpha, rng)
        entry = {
            "comparison": f"{name_a}({p_a*100:.0f}%) -> {name_b}({p_b*100:.0f}%)",
            "delta_pp": delta_pp, "power": round(bp, 4),
            "verdict": "ADEQUATE" if bp >= 0.80 else "INSUFFICIENT",
        }
        boot_power.append(entry)
        if verbose:
            print(f"  {entry['comparison']:>30}  d={delta_pp:>5.1f}pp  "
                  f"power={bp:.4f}  -> {entry['verdict']}")
    results["bootstrap_power"] = boot_power

    # ── Section 4: Required Runs for 80% Power ──
    if verbose:
        print("\n=== Section 4: Minimum Runs for 80% Power (McNemar) ===")
    min_runs = []
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        delta_pp = (p_b - p_a) * 100
        mr = find_min_runs_for_power(n_tasks, p_a, p_b, 0.80, n_sims, alpha, rng)
        mr90 = find_min_runs_for_power(n_tasks, p_a, p_b, 0.90, n_sims, alpha, rng)
        entry = {
            "comparison": f"{name_a}({p_a*100:.0f}%) -> {name_b}({p_b*100:.0f}%)",
            "delta_pp": delta_pp, "min_runs_80pct": mr, "min_runs_90pct": mr90,
            "current_runs": n_runs, "adequate_80pct": n_runs >= mr,
            "adequate_90pct": n_runs >= mr90,
        }
        min_runs.append(entry)
        if verbose:
            print(f"  {entry['comparison']:>30}  d={delta_pp:>5.1f}pp  "
                  f"min80={mr}  min90={mr90}  cur={n_runs}  "
                  f"-> {'OK' if n_runs >= mr else 'NO'}")
    results["min_runs"] = min_runs

    # ── Section 5: Pre-Registered Decision Rules ──
    if verbose:
        print("\n=== Section 5: Pre-Registered Decision Rules ===")
    decision_rules = []
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        delta_pp = (p_b - p_a) * 100
        p_avg = (p_a + p_b) / 2
        expected_disc = int(2 * p_avg * (1 - p_avg) * n_tasks * 0.7)
        crit_k = 0
        for k in range(expected_disc // 2 + 1):
            if 2 * binomial_cdf(expected_disc, k, 0.5) < alpha:
                crit_k = k
                break
        min_diff = (expected_disc // 2 - crit_k) * 2 if crit_k > 0 else expected_disc
        min_pp = min_diff / n_tasks * 100
        entry = {
            "comparison": f"{name_a} -> {name_b}", "delta_pp": delta_pp,
            "expected_discordant": expected_disc, "critical_k": crit_k,
            "min_discordant_diff": min_diff,
            "min_pp_for_significance": round(min_pp, 2),
            "alpha": alpha, "test": "McNemar exact (two-sided)",
            "rule": f"Declare {name_b} > {name_a} if |b-c| >= {min_diff} "
                    f"(~{min_pp:.1f}pp), p < {alpha} (exact McNemar)",
        }
        decision_rules.append(entry)
        if verbose:
            print(f"  {entry['comparison']:>20}  d={delta_pp:>5.1f}pp  "
                  f"min_diff={min_diff}  min_pp={min_pp:.2f}")
    results["decision_rules"] = decision_rules

    # ── Section 6: Multiple Comparison Correction ──
    n_comparisons = len(SUCCESS_LADDER) - 1
    bonferroni_alpha = alpha / n_comparisons
    bonf_rules = []
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        p_avg = (p_a + p_b) / 2
        expected_disc = int(2 * p_avg * (1 - p_avg) * n_tasks * 0.7)
        crit_k = 0
        for k in range(expected_disc // 2 + 1):
            if 2 * binomial_cdf(expected_disc, k, 0.5) < bonferroni_alpha:
                crit_k = k
                break
        min_diff = (expected_disc // 2 - crit_k) * 2 if crit_k > 0 else expected_disc
        bonf_rules.append({
            "comparison": f"{name_a} -> {name_b}",
            "bonferroni_alpha": round(bonferroni_alpha, 4),
            "min_discordant_diff": min_diff,
        })
    results["multiple_comparison"] = {
        "n_comparisons": n_comparisons,
        "bonferroni_alpha": round(bonferroni_alpha, 4),
        "fdr_alpha": alpha, "bonferroni_rules": bonf_rules,
        "recommendation": "Use Benjamini-Hochberg FDR for the success ladder. "
                          "For primary claim (any M_k achieved), use alpha=0.05.",
    }
    if verbose:
        print(f"\n=== Section 6: Multiple Comparison ===")
        print(f"  {n_comparisons} comparisons, Bonferroni alpha={bonferroni_alpha:.4f}")

    # ── Section 7: Summary ──
    adequate_steps = []
    for i in range(len(SUCCESS_LADDER) - 1):
        name_a, p_a, _ = SUCCESS_LADDER[i]
        name_b, p_b, _ = SUCCESS_LADDER[i + 1]
        adequate = mc_power[i]["power"] >= 0.80 or boot_power[i]["power"] >= 0.80
        adequate_steps.append({
            "step": f"{name_a} -> {name_b}",
            "delta_pp": (p_b - p_a) * 100,
            "mcnemar_power": mc_power[i]["power"],
            "bootstrap_power": boot_power[i]["power"],
            "min_runs_for_80pct": min_runs[i]["min_runs_80pct"],
            "current_runs": n_runs, "adequate": adequate,
            "recommendation": (
                f"5 runs {'ARE' if adequate else 'ARE NOT'} adequate for {p_b*100:.0f}% detection. "
                f"{'Consider ' + str(min_runs[i]['min_runs_80pct']) + ' runs' if not adequate else 'No change needed.'}"
            ),
        })
    all_adequate = all(s["adequate"] for s in adequate_steps)
    max_min_runs = max(s["min_runs_for_80pct"] for s in adequate_steps)
    if all_adequate:
        overall = f"OK: {n_runs} runs provide >=80% power for ALL success ladder steps."
    else:
        inadequate = [s["step"] for s in adequate_steps if not s["adequate"]]
        overall = (f"WARNING: {n_runs} runs INSUFFICIENT for: {', '.join(inadequate)}\n"
                   f"   Max required runs for 80% power: {max_min_runs}")
        if max_min_runs <= 10:
            overall += f"\n   RECOMMENDATION: Increase to {max_min_runs} runs"

    pre_reg_lines = [
        "PRE-REGISTERED EVALUATION PROTOCOL (frozen before testing):",
        f"  Significance level: alpha = {alpha} (two-sided)",
        "  Primary test: McNemar's exact test (paired, 158 tasks)",
        "  Secondary test: Paired bootstrap CI (2000 resamples)",
        "  Multiple comparison: Benjamini-Hochberg FDR for success ladder",
        "  Effect size: Cohen's h ( arcsin(sqrt(p2)) - arcsin(sqrt(p1)) )",
        "  Decision: Declare M_k achieved if (a) point estimate >= M_k threshold,",
        "    (b) McNemar p < alpha, (c) bootstrap 95% CI excludes 0, (d) effect size h > 0.3",
    ]
    for r in decision_rules:
        pre_reg_lines.append(f"    {r['comparison']}: min {r['min_pp_for_significance']:.1f}pp "
                             f"(critical |b-c| >= {r['min_discordant_diff']})")
    results["summary"] = {
        "n_tasks": n_tasks, "n_runs": n_runs, "alpha": alpha, "n_sims": n_sims,
        "success_ladder": [{"name": n, "pass_rate": p, "desc": d} for n, p, d in SUCCESS_LADDER],
        "adequate_steps": adequate_steps,
        "overall_recommendation": overall,
        "pre_registered_threshold": "\n".join(pre_reg_lines),
    }
    return results


def generate_html(results, output_path):
    """Generate self-contained HTML report."""
    n_runs = results["summary"]["n_runs"]
    n_tasks = results["summary"]["n_tasks"]
    alpha = results["summary"]["alpha"]
    n_sims = results["summary"]["n_sims"]
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R72 统计功效分析 — BaiZe Post-Train 预注册成功阶梯</title>
<style>
body {{ font-family: -apple-system, "Noto Sans CJK SC", sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #222; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #16213e; border-left: 5px solid #e94560; padding-left: 10px; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 14px; }}
th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: center; }}
th {{ background: #16213e; color: white; }}
tr:nth-child(even) {{ background: #f0f0f5; }}
.pass {{ color: #006600; font-weight: bold; }}
.fail {{ color: #cc0000; font-weight: bold; }}
.warn {{ color: #cc8800; font-weight: bold; }}
.box {{ background: #e8eaf6; border: 1px solid #c5cae9; border-radius: 8px; padding: 15px; margin: 15px 0; }}
.pre-reg {{ background: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 15px; margin: 15px 0; font-family: monospace; white-space: pre-wrap; font-size: 13px; }}
.summary-box {{ background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; padding: 15px; margin: 15px 0; }}
</style>
</head>
<body>
<h1>R72 统计功效分析 — 预注册成功阶梯 (M1-M4)</h1>
<p><strong>BaiZe Stage(ii) Post-Training</strong> · 2026-11-09 · 零 GPU · 纯统计</p>
<div class="box">
<p><strong>目的</strong>：任务书要求"预注册判定阈值：点估计 + 配对检验（McNemar / paired bootstrap）
显著性 —— 必须先定后测"。本分析计算 {n_tasks} 任务 x {n_runs} 次运行
是否提供足够统计功效来可靠检测 M1->M2->M3->M4 各步差异。</p>
<p><strong>参数</strong>：N_tasks={n_tasks} · N_runs={n_runs} · alpha={alpha} · N_sims={n_sims}</p>
</div>
<h2>1. 成功阶梯概览</h2>
<table>
<tr><th>里程碑</th><th>Pass@1</th><th>含义</th><th>与基线差距</th></tr>""")
    for name, rate, desc in SUCCESS_LADDER:
        delta = (rate - 0.36) * 100
        html_parts.append(f"<tr><td><strong>{name}</strong></td><td>{rate*100:.0f}%</td><td>{desc}</td><td>+{delta:.0f}pp</td></tr>")
    html_parts.append("</table>")

    # Section 2: MDES
    html_parts.append("""
<h2>2. 最小可检测效应量 (MDES)</h2>
<table>
<tr><th>p_a</th><th>dpp</th><th>p_b</th><th>不一致率</th><th>不一致对</th><th>MDES(pp)</th><th>功效</th></tr>""")
    for r in results["mdes_table"]:
        pc = "pass" if r["power_approx"] >= 0.80 else ("warn" if r["power_approx"] >= 0.50 else "fail")
        html_parts.append(f"<tr><td>{r['p_a']:.2f}</td><td>{r['delta_pp']}</td><td>{r['p_b']:.2f}</td>"
                          f"<td>{r['eff_disc']*100:.2f}%</td><td>{r['n_discordant']}</td>"
                          f"<td>{r['mdes_pp']:.2f}</td><td class='{pc}'>{r['power_approx']:.4f}</td></tr>")
    html_parts.append("</table>")

    # Section 3: McNemar Power
    html_parts.append(f"""
<h2>3. McNemar 检验功效（蒙特卡洛模拟 {n_sims} 次）</h2>
<table>
<tr><th>比较</th><th>dpp</th><th>功效</th><th>平均b</th><th>平均c</th><th>不一致</th><th>判定</th></tr>""")
    for r in results["mc_nemar_power"]:
        vc = "pass" if r["verdict"] == "ADEQUATE" else "fail"
        html_parts.append(f"<tr><td>{r['comparison']}</td><td>{r['delta_pp']:.1f}</td>"
                          f"<td class='{vc}'>{r['power']:.4f}</td>"
                          f"<td>{r['mean_b_disc']:.1f}</td><td>{r['mean_c_disc']:.1f}</td>"
                          f"<td>{r['mean_discordant']:.1f}</td><td class='{vc}'>{r['verdict']}</td></tr>")
    html_parts.append("</table>")

    # Section 4: Bootstrap Power
    html_parts.append("""
<h2>4. 配对 Bootstrap 检验功效</h2>
<table>
<tr><th>比较</th><th>dpp</th><th>功效</th><th>判定</th></tr>""")
    for r in results["bootstrap_power"]:
        vc = "pass" if r["verdict"] == "ADEQUATE" else "fail"
        html_parts.append(f"<tr><td>{r['comparison']}</td><td>{r['delta_pp']:.1f}</td>"
                          f"<td class='{vc}'>{r['power']:.4f}</td><td class='{vc}'>{r['verdict']}</td></tr>")
    html_parts.append("</table>")

    # Section 5: Required Runs
    html_parts.append("""
<h2>5. 达到 80% 功效所需的最少运行次数</h2>
<table>
<tr><th>比较</th><th>dpp</th><th>最少(80%)</th><th>最少(90%)</th><th>当前</th><th>80%</th><th>90%</th></tr>""")
    for r in results["min_runs"]:
        ok80 = "yes" if r["adequate_80pct"] else "NO"
        ok90 = "yes" if r["adequate_90pct"] else "NO"
        html_parts.append(f"<tr><td>{r['comparison']}</td><td>{r['delta_pp']:.1f}</td>"
                          f"<td>{r['min_runs_80pct']}</td><td>{r['min_runs_90pct']}</td>"
                          f"<td>{r['current_runs']}</td><td>{ok80}</td><td>{ok90}</td></tr>")
    html_parts.append("</table>")

    # Section 6: Decision Rules
    html_parts.append("""
<h2>6. 预注册判定规则（测试前冻结）</h2>
<table>
<tr><th>比较</th><th>dpp</th><th>期望不一致</th><th>临界|b-c|</th><th>最小显著pp</th></tr>""")
    for r in results["decision_rules"]:
        html_parts.append(f"<tr><td>{r['comparison']}</td><td>{r['delta_pp']:.1f}</td>"
                          f"<td>{r['expected_discordant']}</td><td>{r['min_discordant_diff']}</td>"
                          f"<td>{r['min_pp_for_significance']:.2f}</td></tr>")
    html_parts.append("</table>")

    # Section 7: Multiple Comparison
    mc = results["multiple_comparison"]
    html_parts.append(f"""
<h2>7. 多重比较校正</h2>
<div class="box">
<p>比较数：{mc['n_comparisons']} · Bonferroni alpha={mc['bonferroni_alpha']} · B-H FDR alpha={mc['fdr_alpha']}</p>
<p>{mc['recommendation']}</p>
</div>""")

    # Section 8: Summary
    html_parts.append("""
<h2>8. 总结与建议</h2>
<table>
<tr><th>步骤</th><th>dpp</th><th>McNemar</th><th>Bootstrap</th><th>最少(80%)</th><th>当前</th><th>达标</th></tr>""")
    for s in results["summary"]["adequate_steps"]:
        ok = "yes" if s["adequate"] else "NO"
        html_parts.append(f"<tr><td>{s['step']}</td><td>{s['delta_pp']:.1f}</td>"
                          f"<td>{s['mcnemar_power']:.4f}</td><td>{s['bootstrap_power']:.4f}</td>"
                          f"<td>{s['min_runs_for_80pct']}</td><td>{s['current_runs']}</td><td>{ok}</td></tr>")
    html_parts.append("</table>")

    html_parts.append(f"""
<div class="summary-box"><h3>总体建议</h3><pre>{results['summary']['overall_recommendation']}</pre></div>
<div class="pre-reg"><h3>预注册评测协议（测试前冻结）</h3>{results['summary']['pre_registered_threshold']}</div>
<h2>9. 方法论说明</h2>
<div class="box">
<p><strong>McNemar 精确检验</strong>：158 配对任务，b=A通过B失败数，c=A失败B通过数。p=2*BinomCDF(b+c,min(b,c),0.5)。</p>
<p><strong>配对 Bootstrap</strong>：每任务通过率差 Di，重采样2000次，2.5%/97.5%分位数为95%CI。0不在CI内则拒绝H0。</p>
<p><strong>功效模拟</strong>：蒙特卡洛 N_sims 次完整实验(158任务xN运行)，拒绝H0比例为功效。</p>
<p><strong>局限</strong>：假设任务独立、伯努利模型、测量噪声简化。实际功效可能偏离估计。</p>
</div>
<hr><p style="color:#888;font-size:12px">R72 BaiZe Post-Train 2026-11-09 零GPU 纯统计 Python3.8+ stdlib 替身结果不可迁移到白泽</p>
</body></html>""")

    html_content = "\n".join(html_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return os.path.getsize(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="R72: Statistical Power Analysis for Pre-Registered Success Ladder")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--n-runs", type=int, default=DEFAULT_N_RUNS)
    parser.add_argument("--n-tasks", type=int, default=DEFAULT_N_TASKS)
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--n-sims", type=int, default=DEFAULT_N_SIMS)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()

    print(f"R72: Statistical Power Analysis | N_tasks={args.n_tasks} N_runs={args.n_runs} "
          f"alpha={args.alpha} N_sims={args.n_sims}")
    results = run_full_analysis(args.n_tasks, args.n_runs, args.alpha, args.n_sims, args.verbose)

    if args.json:
        json_path = os.path.join(args.output_dir, "r72_stat_power_analysis.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"JSON saved: {json_path} ({os.path.getsize(json_path)} bytes)")

    if args.html:
        html_path = os.path.join(args.output_dir, "report_posttrain_r72_stat_power_zh.html")
        html_size = generate_html(results, html_path)
        print(f"HTML saved: {html_path} ({html_size} bytes)")

    print(f"\n=== Summary ===")
    for s in results["summary"]["adequate_steps"]:
        ok = "OK" if s["adequate"] else "NO"
        print(f"  [{ok}] {s['step']:>25}  d={s['delta_pp']:>5.1f}pp  "
              f"McNemar={s['mcnemar_power']:.4f}  Boot={s['bootstrap_power']:.4f}  "
              f"min_runs(80%)={s['min_runs_for_80pct']}")
    print(f"\n{results['summary']['overall_recommendation']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

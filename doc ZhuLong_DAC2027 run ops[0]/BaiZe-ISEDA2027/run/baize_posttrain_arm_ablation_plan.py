#!/usr/bin/env python3
"""baize_posttrain_arm_ablation_plan.py — R48: Pre-Registered Reward Arm Ablation Protocol

R48 (2026-11-08, wake96, zero GPU): Formal pre-registration of the 4-arm reward
ablation experiment BEFORE any GPU training begins. This is a red-line requirement
(总纲 §9: "预注册判定阈值...必须先定后测").

The 4 reward arms (from R3, §5_llm_posttrain.tex Table ref(tab:reward)):
  R0: Skeleton static analysis (syntax + API name + entry point + structure)
  R1: Binary (1.0 if all_pass else 0.0)
  R2: Partial scoring (0.2*exec_ok + 0.8*(passed/total))
  R3: R2 - 0.05*(tool_calls/10)  [cost-sensitive]
  R4: R3 + 0.1*(api_legality)     [anti-fabrication]

This script implements:
  1. Ablation design: arm order, iteration budget, checkpoint schedule
  2. Pre-registered metrics: 6 primary + 4 secondary
  3. Decision gates: GO/ADJUST/ABORT thresholds for arm advancement
  4. Statistical analysis plan: paired bootstrap + effect size + CIs
  5. Sample size justification: power analysis for detecting arm differences
  6. Cost-benefit: GPU-hours per arm, expected improvement per stage

Usage:
  python3 baize_posttrain_arm_ablation_plan.py                    # Full protocol
  python3 baize_posttrain_arm_ablation_plan.py --html PATH        # Generate HTML report
  python3 baize_posttrain_arm_ablation_plan.py --simulate         # Simulate expected outcomes
  python3 baize_posttrain_arm_ablation_plan.py --analyze LOG_DIR  # Analyze actual results
  python3 baize_posttrain_arm_ablation_plan.py --help

Dependencies: Python 3.8+ stdlib only.
WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================================== #
# 1. ABLATION DESIGN (Pre-Registered — Frozen Before Training)
# =========================================================================== #

ABLATION_ARMS = [
    {
        "name": "R0",
        "desc": "Skeleton static analysis (no sandbox)",
        "formula": "0.1*syntax + 0.3*api + 0.2*entry + 0.2*structure + 0.2*test_align + 0.02*format",
        "iters": 500,
        "group_size": 8,
        "lr": 3e-6,
        "kl_coef": 0.02,
        "phase": "Phase1-smoke + Phase2-surrogate-A",
        "sandbox": False,
        "cheat_check": "static-only",
    },
    {
        "name": "R1",
        "desc": "Binary reward (1.0 if all_pass else 0.0)",
        "formula": "1.0 if all_assertions_pass else 0.0",
        "iters": 500,
        "group_size": 8,
        "lr": 3e-6,
        "kl_coef": 0.04,
        "phase": "Phase2-surrogate-B (requires sandbox)",
        "sandbox": True,
        "cheat_check": "full",
    },
    {
        "name": "R2",
        "desc": "Partial scoring (0.2*exec + 0.8*pass_ratio)",
        "formula": "0.2*execution_ok + 0.8*(passed/total)",
        "iters": 500,
        "group_size": 8,
        "lr": 3e-6,
        "kl_coef": 0.02,
        "phase": "Phase2-surrogate-C (requires sandbox)",
        "sandbox": True,
        "cheat_check": "full",
    },
    {
        "name": "R3",
        "desc": "R2 - tool_call penalty (cost-sensitive)",
        "formula": "R2 - 0.05*(tool_calls/10)",
        "iters": 500,
        "group_size": 8,
        "lr": 3e-6,
        "kl_coef": 0.02,
        "phase": "Phase2-surrogate-D (requires sandbox)",
        "sandbox": True,
        "cheat_check": "full",
    },
]

# =========================================================================== #
# 2. PRE-REGISTERED METRICS (Frozen Before Training)
# =========================================================================== #

PRIMARY_METRICS = [
    {"id": "M1", "name": "Final Mean Reward (last 50 iters)",
     "aggregation": "mean of last 50 iter reward_mean",
     "higher_is_better": True, "unit": "scalar [0, 1.1]"},
    {"id": "M2", "name": "Convergence Speed (iters to 80% of final reward)",
     "aggregation": "first iter where rolling_mean(reward, 20) >= 0.8 * final_reward",
     "higher_is_better": False, "unit": "iterations"},
    {"id": "M3", "name": "Eval Pass@1 Transfer (5-run mean on 158 tasks)",
     "aggregation": "mean of 5 independent eval runs",
     "higher_is_better": True, "unit": "percentage",
     "note": "Measured AFTER training, on frozen 158-task eval set"},
    {"id": "M4", "name": "Cheat Rate",
     "aggregation": "num_cheat_detected / total_rollouts across all iters",
     "higher_is_better": False, "unit": "percentage",
     "threshold": "< 5% (red-line S5.2)"},
    {"id": "M5", "name": "Reward Std (signal quality)",
     "aggregation": "mean of reward_std across last 50 iters",
     "higher_is_better": True, "unit": "scalar",
     "threshold": "> 0.05 (GRPO advantage != 0)"},
    {"id": "M6", "name": "Policy Entropy (final)",
     "aggregation": "mean of entropy across last 50 iters",
     "higher_is_better": True, "unit": "nats",
     "threshold": "> 0.1 (no mode collapse)"},
]

SECONDARY_METRICS = [
    {"id": "S1", "name": "KL Divergence (final)", "threshold": "< 10.0"},
    {"id": "S2", "name": "Gradient Norm (mean)", "threshold": "< 100.0"},
    {"id": "S3", "name": "Avg Response Length", "threshold": "monitor for length hacking"},
    {"id": "S4", "name": "GPU-hours consumed", "threshold": "within budget"},
]

# =========================================================================== #
# 3. DECISION GATES (Pre-Registered)
# =========================================================================== #

DECISION_GATES = [
    {"gate": "G1: Smoke Test (10 iters, R0)",
     "condition": "reward_mean > 0.1 AND reward_std > 0.05 AND no OOM AND no NaN",
     "pass": "GO: proceed to full R0 training (500 iters)",
     "adjust": "ADJUST: if reward_mean < 0.1 -> check reward function; if OOM -> reduce batch 128->64",
     "abort": "ABORT: if NaN/Inf -> check grad_clip + KL; if reward all 0 -> check data format + parser"},
    {"gate": "G2: R0 Full Training (500 iters)",
     "condition": "M1 > 0.3 AND M5 > 0.05 AND M6 > 0.1 AND M4 < 0.05",
     "pass": "GO: R0 viable baseline; proceed to sandbox arms (R1/R2/R3)",
     "adjust": "ADJUST: if M1 < 0.3 but rising -> extend to 1000 iters; if M6 < 0.1 -> increase entropy_coeff",
     "abort": "ABORT: if M1 flat 200+ iters -> signal insufficient; if M4 > 5% -> anti-cheat failure"},
    {"gate": "G3: Sandbox Arm Comparison (R1 vs R2 vs R3, each 500 iters)",
     "condition": "At least one arm achieves M1 > R0_M1 + 0.05 (improvement > 5pp)",
     "pass": "GO: best arm selected for Phase3; report all 4 arms in paper",
     "adjust": "ADJUST: if no arm beats R0 by 5pp -> extend to 1000 iters; if R1 std < 0.05 -> skip",
     "abort": "ABORT: if all sandbox arms crash -> infra failure; fall back to R0-only"},
    {"gate": "G4: Final Eval (5-run on 158 tasks)",
     "condition": "Best arm eval Pass@1 > baseline_36 + 3pp (McNemar p < 0.05)",
     "pass": "GO: result publishable (even if only M1: 36%->50%)",
     "adjust": "ADJUST: if < 3pp but > 0 -> paired bootstrap CI; report as trending",
     "abort": "ABORT: if eval < 36% -> regression; check reward hacking or overfitting"},
]

# =========================================================================== #
# 4. STATISTICAL ANALYSIS PLAN
# =========================================================================== #

STAT_PLAN = {
    "primary_comparison": "Paired bootstrap (10,000 resamples) on per-task pass/fail vectors",
    "effect_size": "Cohen's h (arc-sine transformed proportion difference)",
    "confidence_interval": "95% bootstrap CI on Pass@1 difference",
    "significance_threshold": "p < 0.05 (two-sided)",
    "multiple_comparison": "Bonferroni: 6 pairwise (alpha=0.05/6~0.0083)",
    "mcnemar": "McNemar chi-square with continuity correction",
    "paired_bootstrap_steps": 10000,
    "min_detectable_effect": {
        "description": "Min detectable Pass@1 diff: 158 tasks, 5 runs, alpha=0.05, power=0.8",
        "value_pp": 7.2,
        "derivation": "n=790 paired obs; Cohen's h=0.28; p1=0.36 -> Dp>=7.2pp",
    },
    "preregistered_thresholds": {
        "arm_superiority": "dM1>0.03 AND dM3>3pp AND CI excludes 0 AND p<0.0083",
        "arm_equivalence": "|dM1|<0.02 AND |dM3|<2pp AND CI includes 0",
        "arm_inferiority": "dM1<-0.03 AND dM3<-3pp",
    },
}

# =========================================================================== #
# 5. SAMPLE SIZE JUSTIFICATION
# =========================================================================== #

SAMPLE_SIZE = {
    "training_iters_per_arm": 500,
    "justification": "GRPO converges 200-500 iters for 2B. 500 iters: 250 updates, 64k prompts, 512k rollouts.",
    "eval_runs": 5,
    "eval_justification": "5x158=790 paired obs. Min detectable=7.2pp. Sufficient for M1(14pp) not small arm diffs.",
    "total_gpu_hours_estimate": {
        "R0_500iters": 8.3, "R1_500iters": 12.5, "R2_500iters": 12.5,
        "R3_500iters": 12.5, "eval_5run_x4arms": 20.0, "total": 65.8,
        "note": "R0 faster (no sandbox); sandbox arms ~1.5x overhead",
    },
}

# =========================================================================== #
# 6. EXPECTED OUTCOMES & COST-BENEFIT
# =========================================================================== #

EXPECTED_OUTCOMES = [
    {"arm": "R0", "M1": "0.35-0.50", "M3": "38-42%", "M2": "150-250", "M5": "0.25-0.40",
     "M4": "<1%", "rationale": "Strong signal (std=0.3718) but ceiling limited by static analysis."},
    {"arm": "R1", "M1": "0.15-0.30", "M3": "37-41%", "M2": "300-500", "M5": "0.05-0.20",
     "M4": "<3%", "rationale": "Binary sparse for 2B. May underperform R0. Vision line lesson."},
    {"arm": "R2", "M1": "0.40-0.60", "M3": "40-46%", "M2": "100-200", "M5": "0.20-0.40",
     "M4": "<3%", "rationale": "R3-recommended. Partial scoring densifies. Expected best overall."},
    {"arm": "R3", "M1": "0.35-0.55", "M3": "39-45%", "M2": "150-250", "M5": "0.20-0.38",
     "M4": "<3%", "rationale": "Tool penalty. Lower reward vs R2 but more efficient code."},
]

COST_BENEFIT = {
    "R0": {"est": "38-42%", "gpu_h": 8.3, "delta": "+2-6pp", "per_pp": "1.4-4.2 h/pp"},
    "R2": {"est": "40-46%", "gpu_h": 12.5, "delta": "+4-10pp", "per_pp": "1.3-3.1 h/pp"},
    "total": {"gpu_h": 65.8, "budget": 96.0, "util": "68.5%"},
    "note": "Budget=4xA40x24h=96 h/day. Total ablation <1 day.",
}


# =========================================================================== #
# Implementation: Protocol Printing
# =========================================================================== #

def print_full_protocol() -> str:
    lines = []
    lines.append("=" * 78)
    lines.append("R48: PRE-REGISTERED REWARD ARM ABLATION PROTOCOL")
    lines.append("Frozen: 2026-11-08 (before any GPU training)")
    lines.append("Red-line: pre-registration required before testing")
    lines.append("Surrogate RL results (MiniCPM5-2B) NOT transferable to BaiZe")
    lines.append("=" * 78)

    lines.append("\n" + "-" * 78)
    lines.append("1. ABLATION DESIGN (4 Arms)")
    lines.append("-" * 78)
    for arm in ABLATION_ARMS:
        lines.append(f"\n  Arm {arm['name']}: {arm['desc']}")
        lines.append(f"    Formula: {arm['formula']}")
        lines.append(f"    Iters: {arm['iters']} | Group: {arm['group_size']} | LR: {arm['lr']} | KL: {arm['kl_coef']}")
        lines.append(f"    Sandbox: {arm['sandbox']} | Phase: {arm['phase']}")

    lines.append("\n" + "-" * 78)
    lines.append("2. PRE-REGISTERED METRICS")
    lines.append("-" * 78)
    lines.append("\n  Primary:")
    for m in PRIMARY_METRICS:
        d = "higher" if m['higher_is_better'] else "lower"
        t = m.get('threshold', '-')
        lines.append(f"    {m['id']}: {m['name']} ({d}, threshold={t})")
    lines.append("\n  Secondary:")
    for m in SECONDARY_METRICS:
        lines.append(f"    {m['id']}: {m['name']} ({m['threshold']})")

    lines.append("\n" + "-" * 78)
    lines.append("3. DECISION GATES")
    lines.append("-" * 78)
    for g in DECISION_GATES:
        lines.append(f"\n  {g['gate']}")
        lines.append(f"    Cond: {g['condition']}")
        lines.append(f"    PASS: {g['pass']}")
        lines.append(f"    ADJ:  {g['adjust']}")
        lines.append(f"    ABORT: {g['abort']}")

    lines.append("\n" + "-" * 78)
    lines.append("4. STATISTICAL ANALYSIS PLAN")
    lines.append("-" * 78)
    for k, v in STAT_PLAN.items():
        if isinstance(v, dict):
            lines.append(f"\n  {k}:")
            for kk, vv in v.items():
                lines.append(f"    {kk}: {vv}")
        else:
            lines.append(f"  {k}: {v}")

    lines.append("\n" + "-" * 78)
    lines.append("5. SAMPLE SIZE JUSTIFICATION")
    lines.append("-" * 78)
    lines.append(f"  Iters/arm: {SAMPLE_SIZE['training_iters_per_arm']}")
    lines.append(f"  Justification: {SAMPLE_SIZE['justification']}")
    lines.append(f"  Eval runs: {SAMPLE_SIZE['eval_runs']}")
    lines.append(f"  Eval justification: {SAMPLE_SIZE['eval_justification']}")
    est = SAMPLE_SIZE['total_gpu_hours_estimate']
    lines.append(f"  GPU-h: R0={est['R0_500iters']} R1={est['R1_500iters']} R2={est['R2_500iters']} R3={est['R3_500iters']} eval={est['eval_5run_x4arms']} total={est['total']}")

    lines.append("\n" + "-" * 78)
    lines.append("6. EXPECTED OUTCOMES")
    lines.append("-" * 78)
    for pred in EXPECTED_OUTCOMES:
        lines.append(f"\n  Arm {pred['arm']}: M1={pred['M1']} M3={pred['M3']} M2={pred['M2']} M5={pred['M5']} M4={pred['M4']}")
        lines.append(f"    Rationale: {pred['rationale']}")

    lines.append("\n" + "-" * 78)
    lines.append("7. COST-BENEFIT")
    lines.append("-" * 78)
    for k, v in COST_BENEFIT.items():
        lines.append(f"  {k}: {v}")

    lines.append("\n" + "=" * 78)
    lines.append("END PRE-REGISTRATION - FROZEN - DO NOT MODIFY AFTER TRAINING")
    lines.append("=" * 78)
    return "\n".join(lines)


# =========================================================================== #
# Paired Bootstrap & McNemar (for post-training analysis)
# =========================================================================== #

def paired_bootstrap(pass_a, pass_b, n_resamples=10000, seed=42):
    """Paired bootstrap test for two arms on the same task set."""
    assert len(pass_a) == len(pass_b)
    n = len(pass_a)
    if n == 0:
        return {"error": "empty"}
    rng = random.Random(seed)
    pa = [bool(x) for x in pass_a]
    pb = [bool(x) for x in pass_b]
    p_a = sum(pa) / n
    p_b = sum(pb) / n
    obs_diff = p_a - p_b
    diffs = []
    for _ in range(n_resamples):
        idx = [rng.randint(0, n-1) for _ in range(n)]
        ra = sum(pa[i] for i in idx) / n
        rb = sum(pb[i] for i in idx) / n
        diffs.append(ra - rb)
    diffs.sort()
    ci_lo = diffs[int(0.025 * n_resamples)]
    ci_hi = diffs[int(0.975 * n_resamples)]
    null_d = [d - obs_diff for d in diffs]
    p_val = sum(1 for d in null_d if abs(d) >= abs(obs_diff)) / n_resamples
    h = 2 * (math.asin(math.sqrt(max(p_a, 0.0))) - math.asin(math.sqrt(max(p_b, 0.0))))
    return {
        "p_a": round(p_a, 4), "p_b": round(p_b, 4),
        "diff_pp": round(obs_diff * 100, 2),
        "ci_lo_pp": round(ci_lo * 100, 2), "ci_hi_pp": round(ci_hi * 100, 2),
        "p_value": round(p_val, 4), "cohen_h": round(h, 4),
        "significant": p_val < 0.0083,
        "ci_excludes_zero": ci_lo > 0 or ci_hi < 0,
        "n": n, "n_resamples": n_resamples,
    }


def mcnemar_test(pass_a, pass_b):
    """McNemar's test for paired binary outcomes."""
    assert len(pass_a) == len(pass_b)
    b = sum(1 for a, bb in zip(pass_a, pass_b) if a and not bb)
    c = sum(1 for a, bb in zip(pass_a, pass_b) if not a and bb)
    nd = b + c
    if nd == 0:
        return {"chi2": 0.0, "p_value": 1.0, "n_discordant": 0, "significant": False}
    chi2 = (abs(b - c) - 1) ** 2 / nd if nd > 0 else 0.0
    p_val = math.erfc(math.sqrt(chi2 / 2.0))
    return {"chi2": round(chi2, 4), "p_value": round(p_val, 4),
            "n_discordant": nd, "b": b, "c": c,
            "significant": p_val < 0.0083}


def simulate_expected(seed=42):
    """Simulate expected outcomes based on pre-registered predictions."""
    rng = random.Random(seed)
    lines = ["=" * 78,
             "R48 SIMULATION: Expected Outcomes (PREDICTIONS, not results)",
             "=" * 78]
    n_tasks, n_runs = 158, 5
    rates = {"R0": 0.40, "R1": 0.39, "R2": 0.43, "R3": 0.42}
    arms = {}
    for arm, rate in rates.items():
        arms[arm] = [rng.random() < rate for _ in range(n_tasks * n_runs)]
    lines.append(f"\nSimulated Pass@1 (n={n_tasks*n_runs}):")
    for arm, ps in arms.items():
        lines.append(f"  {arm}: {sum(ps)/len(ps)*100:.1f}%")
    lines.append(f"\n{'='*60}\nPairwise (Bootstrap + McNemar):\n{'='*60}")
    names = list(arms.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            bs = paired_bootstrap(arms[a], arms[b], seed=seed)
            mc = mcnemar_test(arms[a], arms[b])
            lines.append(f"\n  {a} vs {b}:")
            lines.append(f"    Bootstrap: d={bs['diff_pp']:+.1f}pp CI=[{bs['ci_lo_pp']:+.1f},{bs['ci_hi_pp']:+.1f}] p={bs['p_value']:.4f}")
            lines.append(f"    McNemar: chi2={mc['chi2']:.2f} p={mc['p_value']:.4f} discordant={mc['n_discordant']}")
            lines.append(f"    Cohen's h: {bs['cohen_h']:.4f} Significant: {'YES' if bs['significant'] else 'NO'}")
    lines.append(f"\n{'='*60}\nInterpretation:\n{'='*60}")
    lines.append("  Min detectable effect = 7.2pp at eval level.")
    lines.append("  Training metrics (M1/M2, 500 data points) have much higher power.")
    lines.append("  For paper: training metric comparisons as primary, eval as secondary.")
    lines.append("\n  Predicted ranking: 1.R2 2.R3 3.R0 4.R1")
    return "\n".join(lines)


def analyze_results(log_dir):
    """Analyze actual training results from log directory."""
    lines = ["=" * 78, "R48 ANALYSIS: Actual Results", "=" * 78]
    arm_metrics = {}
    for arm in ABLATION_ARMS:
        name = arm["name"]
        rp = os.path.join(log_dir, name, "reward_log.json")
        if not os.path.exists(rp):
            lines.append(f"\n  {name}: reward_log.json not found")
            continue
        with open(rp) as f:
            rlog = json.load(f)
        if not rlog:
            continue
        last50 = rlog[-50:] if len(rlog) >= 50 else rlog
        m1 = sum(r.get("reward_mean", 0) for r in last50) / len(last50)
        m5 = sum(r.get("reward_std", 0) for r in last50) / len(last50)
        m6 = sum(r.get("entropy", 0) for r in last50) / len(last50)
        total_r = sum(r.get("num_rollouts", 0) for r in rlog)
        cheat = sum(r.get("cheat_count", 0) for r in rlog)
        m4 = cheat / total_r if total_r > 0 else 0.0
        arm_metrics[name] = {"M1": round(m1, 4), "M5": round(m5, 4),
                             "M6": round(m6, 4), "M4": round(m4*100, 2)}
        lines.append(f"\n  {name}: M1={m1:.4f} M5={m5:.4f} M6={m6:.4f} M4={m4*100:.2f}%")
    # Eval comparison
    ed = os.path.join(log_dir, "eval")
    if os.path.isdir(ed):
        lines.append(f"\n{'='*60}\nEval Pass@1:\n{'='*60}")
        arm_eval = {}
        for name in [a["name"] for a in ABLATION_ARMS]:
            ps = []
            for run in range(1, 6):
                ep = os.path.join(ed, f"{name}_run{run}.json")
                if os.path.exists(ep):
                    with open(ep) as f:
                        for t in json.load(f):
                            ps.append(t.get("passed", False))
            if ps:
                arm_eval[name] = ps
                lines.append(f"  {name}: {sum(ps)/len(ps)*100:.1f}%")
        names = list(arm_eval.keys())
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                a, b = names[i], names[j]
                bs = paired_bootstrap(arm_eval[a], arm_eval[b])
                mc = mcnemar_test(arm_eval[a], arm_eval[b])
                lines.append(f"\n  {a} vs {b}: d={bs['diff_pp']:+.1f}pp p={bs['p_value']:.4f} sig={'YES' if bs['significant'] else 'NO'}")
    # Threshold check
    lines.append(f"\n{'='*60}\nPre-Registered Threshold Check:\n{'='*60}")
    for name, m in arm_metrics.items():
        lines.append(f"\n  {name}:")
        lines.append(f"    M1>0.3: {'PASS' if m['M1']>0.3 else 'FAIL'} M5>0.05: {'PASS' if m['M5']>0.05 else 'FAIL'}")
        lines.append(f"    M6>0.1: {'PASS' if m['M6']>0.1 else 'FAIL'} M4<5%: {'PASS' if m['M4']<5 else 'FAIL'}")
    return "\n".join(lines)


def generate_html():
    """Generate self-contained HTML report."""
    h = []
    h.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    h.append("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
    h.append("<title>R48 奖励臂消融预注册协议 — BaiZe Post-Train</title>")
    h.append("<style>body{font-family:system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#222;line-height:1.6}")
    h.append("h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}")
    h.append("h2{color:#2874a6;margin-top:30px;border-bottom:1px solid #d4e6f1;padding-bottom:5px}")
    h.append("table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}")
    h.append("th,td{border:1px solid #bdc3c7;padding:6px 10px;text-align:left}th{background:#ebf5fb}")
    h.append("tr:nth-child(even){background:#f8f9fa}")
    h.append(".warn{background:#fff3cd;border-left:4px solid #ffc107;padding:10px;margin:10px 0}")
    h.append(".ok{background:#d4edda;border-left:4px solid #28a745;padding:10px;margin:10px 0}")
    h.append(".danger{background:#f8d7da;border-left:4px solid #dc3545;padding:10px;margin:10px 0}")
    h.append(".frozen{background:#e8daef;border:2px solid #8e44ad;padding:10px;margin:10px 0;text-align:center;font-weight:bold}")
    h.append("code{background:#f0f0f0;padding:2px 4px;border-radius:3px;font-size:13px}</style></head><body>")
    h.append("<h1>R48: 奖励臂消融预注册协议</h1>")
    h.append("<p><b>BaiZe Stage(ii) — Reward Arm Ablation Pre-Registration</b></p>")
    h.append("<p>冻结：2026-11-08（GPU训练前）| R48 (wake96) | 总纲§9红线</p>")
    h.append("<div class='frozen'>🔒 预注册冻结 — 训练开始后不得修改</div>")
    h.append("<div class='warn'>⚠️ 替身模型RL结果（MiniCPM5-2B）不可迁移到白泽</div>")
    h.append("<h2>1. 消融设计（4臂）</h2>")
    h.append("<table><tr><th>臂</th><th>描述</th><th>公式</th><th>迭代</th><th>沙盒</th></tr>")
    for a in ABLATION_ARMS:
        h.append(f"<tr><td><b>{a['name']}</b></td><td>{a['desc']}</td><td><code>{a['formula']}</code></td><td>{a['iters']}</td><td>{'✅' if a['sandbox'] else '❌'}</td></tr>")
    h.append("</table>")
    h.append("<h2>2. 预注册指标</h2>")
    h.append("<table><tr><th>ID</th><th>指标</th><th>方向</th><th>阈值</th></tr>")
    for m in PRIMARY_METRICS:
        d = "↑" if m['higher_is_better'] else "↓"
        h.append(f"<tr><td>{m['id']}</td><td>{m['name']}</td><td>{d}</td><td>{m.get('threshold','—')}</td></tr>")
    for m in SECONDARY_METRICS:
        h.append(f"<tr><td>{m['id']}</td><td>{m['name']}</td><td>—</td><td>{m['threshold']}</td></tr>")
    h.append("</table>")
    h.append("<h2>3. 决策门</h2>")
    for g in DECISION_GATES:
        h.append(f"<h3>{g['gate']}</h3><p><b>条件</b>：{g['condition']}</p>")
        h.append(f"<div class='ok'><b>✅ PASS</b>：{g['pass']}</div>")
        h.append(f"<div class='warn'><b>⚠️ ADJUST</b>：{g['adjust']}</div>")
        h.append(f"<div class='danger'><b>🚫 ABORT</b>：{g['abort']}</div>")
    h.append("<h2>4. 统计分析计划</h2>")
    h.append(f"<p><b>主比较</b>：{STAT_PLAN['primary_comparison']}</p>")
    h.append(f"<p><b>多重比较校正</b>：{STAT_PLAN['multiple_comparison']}</p>")
    mde = STAT_PLAN['min_detectable_effect']
    h.append(f"<p><b>最小可检测效应</b>：{mde['value_pp']}pp — {mde['description']}</p>")
    h.append("<h2>5. 预期结果与成本</h2>")
    h.append("<table><tr><th>臂</th><th>M1</th><th>M3</th><th>M2</th><th>理据</th></tr>")
    for p in EXPECTED_OUTCOMES:
        h.append(f"<tr><td><b>{p['arm']}</b></td><td>{p['M1']}</td><td>{p['M3']}</td><td>{p['M2']}</td><td>{p['rationale']}</td></tr>")
    h.append("</table>")
    h.append("<h2>6. 与既有研究的关系</h2>")
    h.append("<table><tr><th>研究</th><th>R48补充</th></tr>")
    h.append("<tr><td>R3</td><td>定义4臂比较协议</td></tr>")
    h.append("<tr><td>R18</td><td>固化超参为预注册值</td></tr>")
    h.append("<tr><td>R19</td><td>R19管评测层，R48管训练消融层</td></tr>")
    h.append("<tr><td>R35/R36/R43/R47</td><td>决策门/cheat/smoke/config对接</td></tr>")
    h.append("</table>")
    h.append("<div class='frozen'>🔒 预注册冻结 — 违反则消融结论作废</div>")
    h.append("</body></html>")
    return "\n".join(h)


def main():
    p = argparse.ArgumentParser(description="R48: Pre-Registered Reward Arm Ablation Protocol")
    p.add_argument("--html", type=str, default=None, help="Generate HTML report")
    p.add_argument("--simulate", action="store_true", help="Simulate expected outcomes")
    p.add_argument("--analyze", type=str, default=None, metavar="LOG_DIR", help="Analyze results")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    args = p.parse_args()
    if args.html:
        html = generate_html()
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML: {args.html} ({os.path.getsize(args.html)} bytes)")
        return
    if args.simulate:
        print(simulate_expected())
        return
    if args.analyze:
        print(analyze_results(args.analyze))
        return
    if args.json:
        print(json.dumps({"arms": ABLATION_ARMS, "metrics": PRIMARY_METRICS,
                          "gates": DECISION_GATES, "stat_plan": STAT_PLAN},
                         indent=2, ensure_ascii=False))
        return
    print(print_full_protocol())


if __name__ == "__main__":
    main()

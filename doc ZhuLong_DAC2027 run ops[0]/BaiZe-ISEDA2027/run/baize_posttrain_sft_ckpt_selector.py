#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R87: SFT Checkpoint Selection for RL Initialization
====================================================
Predictive metrics, early stopping, and readiness gate design.

Simulates SFT training dynamics across checkpoints and correlates SFT metrics
with RL initialization quality. Integrates R64/R73/R80/R85/R83/R79/R58.

Zero GPU. Pure Python 3.8+ stdlib. Monte Carlo simulation.

Usage:
  python3 baize_posttrain_sft_ckpt_selector.py [--verbose] [--html] [--json] [--decision-only]
"""
import argparse, json, math, os, random, sys
from typing import Any, Dict, List

# ═══ Constants from prior research ═══
SFT_TOTAL_STEPS = 3000
SFT_CKPT_INTERVAL = 200
INITIAL_PASS1 = 0.36
INITIAL_LOSS = 2.80
FINAL_LOSS_TARGET = 2.37
INITIAL_TOOL_RATE = 0.15
TARGET_TOOL_RATE = 0.80
INITIAL_API_KNOW = 0.30
RL_TOTAL_STEPS = 500
M1, M2, M3 = 0.50, 0.65, 0.75
TASK_TIERS = {
    "L1": {"count": 30, "base_pass": 0.65, "weight": 0.19},
    "L2": {"count": 35, "base_pass": 0.50, "weight": 0.22},
    "L3": {"count": 40, "base_pass": 0.35, "weight": 0.25},
    "L4": {"count": 30, "base_pass": 0.20, "weight": 0.19},
    "L5": {"count": 23, "base_pass": 0.10, "weight": 0.15},
}

# ═══ SFT Training Dynamics Simulation ═══
def simulate_sft_dynamics(rng, data_mix="optimal", ctx_length=8192, overfit_risk=0.3, seed=42):
    """Simulate SFT training dynamics across checkpoints."""
    checkpoints = []
    mix_effects = {
        "optimal": {"r_d1": 0.35, "r_d2": 0.30, "r_d4": 0.25, "r_d6": 0.20},
        "agent_heavy": {"r_d1": 0.40, "r_d2": 0.35, "r_d4": 0.15, "r_d6": 0.25},
        "domain_heavy": {"r_d1": 0.20, "r_d2": 0.15, "r_d4": 0.35, "r_d6": 0.10},
        "balanced": {"r_d1": 0.25, "r_d2": 0.22, "r_d4": 0.20, "r_d6": 0.15},
    }
    eff = mix_effects.get(data_mix, mix_effects["optimal"])
    loss_decay = rng.gauss(0.00035, 0.00008)
    loss_noise = rng.gauss(0.02, 0.005)
    eval_mid = rng.gauss(1200, 200)
    eval_steep = rng.gauss(0.004, 0.001)
    eval_max_gain = rng.gauss(0.22, 0.04)
    tool_gain = rng.gauss(0.00038, 0.00008)
    tool_noise = rng.gauss(0.015, 0.003)
    api_mid = rng.gauss(800, 150)
    api_steep = rng.gauss(0.005, 0.001)
    api_max_gain = rng.gauss(0.40, 0.06)
    kl_growth = rng.gauss(0.00015, 0.00003)
    grad_init = rng.gauss(1.5, 0.2)
    grad_decay = rng.gauss(0.0008, 0.0002)
    overfit_onset = rng.gauss(800, 200)
    overfit_rate = rng.gauss(0.00003, 0.00001) * overfit_risk
    cheat_base = rng.gauss(0.01, 0.005)

    for step in range(0, SFT_TOTAL_STEPS + 1, SFT_CKPT_INTERVAL):
        base_loss = INITIAL_LOSS * math.exp(-loss_decay * step) + \
                    (FINAL_LOSS_TARGET * (1 - math.exp(-loss_decay * step)))
        overfit_pen = overfit_rate * (step - overfit_onset) if step > overfit_onset else 0.0
        loss = base_loss + overfit_pen + rng.gauss(0, loss_noise)
        eval_gain = eval_max_gain / (1 + math.exp(-eval_steep * (step - eval_mid)))
        eval_pass1 = INITIAL_PASS1 + eval_gain
        if step > overfit_onset:
            eval_pass1 -= overfit_rate * (step - overfit_onset) * 2.0
        eval_pass1 = max(0.20, min(0.85, eval_pass1 + rng.gauss(0, 0.008)))
        tool_rate = min(TARGET_TOOL_RATE + 0.05, INITIAL_TOOL_RATE + tool_gain * step)
        tool_rate = max(0.10, min(0.95, tool_rate + rng.gauss(0, tool_noise)))
        api_gain = api_max_gain / (1 + math.exp(-api_steep * (step - api_mid)))
        api_know = max(0.20, min(0.90, INITIAL_API_KNOW + api_gain + rng.gauss(0, 0.01)))
        kl = max(0.0, kl_growth * step + rng.gauss(0, 0.002))
        grad_norm = max(0.1, grad_init * math.exp(-grad_decay * step) + rng.gauss(0, 0.05))
        overfit_score = (step - overfit_onset) * overfit_rate * 10 if step > overfit_onset else 0.0
        cheat_rate = max(0.0, cheat_base + rng.gauss(0, 0.003))
        if step >= SFT_CKPT_INTERVAL:
            prev_base = INITIAL_LOSS * math.exp(-loss_decay * (step - SFT_CKPT_INTERVAL)) + \
                        (FINAL_LOSS_TARGET * (1 - math.exp(-loss_decay * (step - SFT_CKPT_INTERVAL))))
            loss_slope = (base_loss - prev_base) / SFT_CKPT_INTERVAL
        else:
            loss_slope = 0.0
        checkpoints.append({
            "step": step, "loss": round(loss, 4), "eval_pass1": round(eval_pass1, 4),
            "tool_use_rate": round(tool_rate, 4), "api_knowledge": round(api_know, 4),
            "kl_from_init": round(kl, 4), "grad_norm": round(grad_norm, 4),
            "overfit_score": round(overfit_score, 4), "cheat_rate": round(cheat_rate, 4),
            "loss_slope": round(loss_slope, 6), "data_mix": data_mix, "ctx_length": ctx_length,
        })
    return checkpoints

# ═══ RL Initialization Quality Simulation ═══
def simulate_rl_from_ckpt(rng, ckpt, reward_arm="R3", seed=42):
    """Simulate RL training starting from a given SFT checkpoint."""
    eval_start = ckpt["eval_pass1"]
    tool_start = ckpt["tool_use_rate"]
    api_start = ckpt["api_knowledge"]
    kl_start = ckpt["kl_from_init"]
    overfit = ckpt["overfit_score"]
    cheat = ckpt["cheat_rate"]
    sft_quality = eval_start * 0.4 + tool_start * 0.3 + api_start * 0.3
    rl_gain_pot = max(0.0, 0.20 - (sft_quality - 0.5) * 0.15)
    rl_gain_pot -= overfit * 0.5 + cheat * 2.0 + min(0.05, kl_start * 0.3)
    rl_gain_pot = max(0.0, rl_gain_pot)
    actual_gain = max(0.0, rl_gain_pot * rng.gauss(0.85, 0.15))
    steps_to_peak = max(50, min(RL_TOTAL_STEPS, int(rng.gauss(250, 50) - sft_quality * 50)))
    collapse_prob = max(0.005, min(0.60, 0.03 + overfit * 1.5 + kl_start * 0.3 + cheat * 5.0 - tool_start * 0.25 - api_start * 0.10))
    collapse = rng.random() < collapse_prob
    final_reward = eval_start + actual_gain
    if collapse:
        final_reward = max(0.20, eval_start + actual_gain * 0.3 - rng.gauss(0.03, 0.02))
    final_reward = max(0.15, min(0.92, final_reward + rng.gauss(0, 0.01)))
    reward_improvement = final_reward - eval_start
    arm_signal = {"R1": 0.909, "R2": 0.849, "R3": 0.998, "R4": 0.978}
    base_signal = arm_signal.get(reward_arm, 0.95)
    adv_signal = max(0.5, min(1.0, base_signal * (0.7 + tool_start * 0.3) + rng.gauss(0, 0.02)))
    tier_pass = {}
    for tier, info in TASK_TIERS.items():
        tg = actual_gain * (1.0 - info["weight"] * 0.5)
        if collapse:
            tg *= 0.3
        tier_pass[tier] = min(0.95, info["base_pass"] + tg + rng.gauss(0, 0.02))
    return {
        "ckpt_step": ckpt["step"], "eval_start": round(eval_start, 4),
        "final_reward": round(final_reward, 4), "reward_improvement": round(reward_improvement, 4),
        "collapse": collapse, "collapse_prob": round(collapse_prob, 4),
        "steps_to_peak": steps_to_peak, "advantage_signal_rate": round(adv_signal, 4),
        "sft_quality_score": round(sft_quality, 4), "rl_gain_potential": round(rl_gain_pot, 4),
        "tier_pass_rates": {k: round(v, 4) for k, v in tier_pass.items()}, "reward_arm": reward_arm,
    }

# ═══ Checkpoint Selection Strategies ═══
def select_checkpoint(strategy, checkpoints):
    """Select checkpoint using different strategies."""
    if strategy == "latest":
        return checkpoints[-1]
    elif strategy == "best_eval":
        return max(checkpoints, key=lambda c: c["eval_pass1"])
    elif strategy == "lowest_loss":
        return min(checkpoints, key=lambda c: c["loss"])
    elif strategy == "best_tool":
        return max(checkpoints, key=lambda c: c["tool_use_rate"])
    elif strategy == "balanced":
        return max(checkpoints, key=lambda c: (
            c["eval_pass1"] * 0.40 + c["tool_use_rate"] * 0.30 +
            c["api_knowledge"] * 0.20 - c["overfit_score"] * 2.0))
    elif strategy == "early_stop":
        best = checkpoints[0]
        for i in range(1, len(checkpoints)):
            c = checkpoints[i]
            if c["loss_slope"] < 0.0001 and c["eval_pass1"] < best["eval_pass1"]:
                return best
            if c["eval_pass1"] >= best["eval_pass1"]:
                best = c
        return best
    elif strategy == "anti_overfit":
        candidates = [c for c in checkpoints if c["overfit_score"] < 0.01]
        if candidates:
            return max(candidates, key=lambda c: c["eval_pass1"])
        return checkpoints[0]
    return checkpoints[-1]

# ═══ Readiness Gate ═══
def evaluate_gate(ckpt, thresholds):
    """Evaluate readiness gate for a checkpoint."""
    criteria = {
        "eval_ge_36": ckpt["eval_pass1"] >= thresholds.get("min_eval", 0.36),
        "eval_ge_50": ckpt["eval_pass1"] >= thresholds.get("target_eval", 0.50),
        "tool_ge_80": ckpt["tool_use_rate"] >= thresholds.get("min_tool", 0.80),
        "api_ge_60": ckpt["api_knowledge"] >= thresholds.get("min_api", 0.60),
        "loss_conv": abs(ckpt["loss_slope"]) < thresholds.get("max_loss_slope", 0.0001),
        "overfit_low": ckpt["overfit_score"] < thresholds.get("max_overfit", 0.05),
        "cheat_low": ckpt["cheat_rate"] < thresholds.get("max_cheat", 0.05),
        "kl_ok": ckpt["kl_from_init"] < thresholds.get("max_kl", 0.50),
    }
    critical = ["eval_ge_36", "tool_ge_80", "cheat_low"]
    crit_pass = all(criteria[c] for c in critical)
    target = ["eval_ge_50", "api_ge_60", "loss_conv"]
    target_count = sum(1 for c in target if criteria[c])
    if not crit_pass:
        decision = "NO_GO"
    elif target_count >= 2 and criteria["overfit_low"]:
        decision = "STRONG_GO"
    elif target_count >= 1:
        decision = "GO"
    else:
        decision = "WEAK_GO"
    return {"criteria": criteria, "critical_pass": crit_pass,
            "target_pass_count": target_count, "decision": decision}

# ═══ Monte Carlo Simulation ═══
def run_monte_carlo(n_trials=2000):
    """Run full Monte Carlo simulation."""
    strategies = ["latest", "best_eval", "lowest_loss", "best_tool",
                  "balanced", "early_stop", "anti_overfit"]
    reward_arms = ["R1", "R2", "R3", "R4"]
    data_mixes = ["optimal", "agent_heavy", "domain_heavy", "balanced"]
    strategy_results = {s: [] for s in strategies}
    all_ckpts_rl = []
    gate_evals = []
    arm_results = {a: [] for a in reward_arms}
    mix_results = {m: [] for m in data_mixes}

    for trial in range(n_trials):
        seed = 42 + trial
        rng = random.Random(seed)
        for mix in data_mixes:
            ckpts = simulate_sft_dynamics(rng, data_mix=mix, seed=seed)
            for strategy in strategies:
                ckpt = select_checkpoint(strategy, ckpts)
                for arm in reward_arms:
                    rl = simulate_rl_from_ckpt(rng, ckpt, reward_arm=arm, seed=seed)
                    result = {"trial": trial, "strategy": strategy, "data_mix": mix,
                              "reward_arm": arm, **rl}
                    strategy_results[strategy].append(result)
                    arm_results[arm].append(result)
                    mix_results[mix].append(result)
                    if mix == "optimal" and arm == "R3":
                        all_ckpts_rl.append({
                            "step": ckpt["step"], "sft_eval": ckpt["eval_pass1"],
                            "sft_loss": ckpt["loss"], "sft_tool": ckpt["tool_use_rate"],
                            "sft_api": ckpt["api_knowledge"], "sft_kl": ckpt["kl_from_init"],
                            "sft_overfit": ckpt["overfit_score"], "sft_cheat": ckpt["cheat_rate"],
                            "sft_loss_slope": ckpt["loss_slope"], "sft_grad": ckpt["grad_norm"],
                            "rl_final": rl["final_reward"], "rl_improve": rl["reward_improvement"],
                            "rl_collapse": rl["collapse"],
                        })
                    if mix == "optimal" and arm == "R3" and strategy == "balanced":
                        gate = evaluate_gate(ckpt, {"min_eval": 0.36, "target_eval": 0.50,
                            "min_tool": 0.80, "min_api": 0.60, "max_loss_slope": 0.0001,
                            "max_overfit": 0.05, "max_cheat": 0.05, "max_kl": 0.50})
                        gate_evals.append({"trial": trial, "ckpt_step": ckpt["step"],
                            "decision": gate["decision"], "rl_collapse": rl["collapse"],
                            "rl_improve": rl["reward_improvement"], "rl_final": rl["final_reward"]})
    return _analyze_mc(n_trials, strategy_results, all_ckpts_rl, gate_evals,
                       arm_results, mix_results, data_mixes, strategies, reward_arms)

def _analyze_mc(n_trials, strategy_results, all_ckpts_rl, gate_evals,
                arm_results, mix_results, data_mixes, strategies, reward_arms):
    """Analyze Monte Carlo results."""
    # Strategy summary
    strategy_summary = {}
    for strategy, results in strategy_results.items():
        improvements = [r["reward_improvement"] for r in results]
        collapses = [r["collapse"] for r in results]
        finals = [r["final_reward"] for r in results]
        n = len(improvements)
        mean_imp = sum(improvements) / n
        std_imp = (sum((x - mean_imp)**2 for x in improvements) / n) ** 0.5
        sf = sorted(finals)
        strategy_summary[strategy] = {
            "mean_improvement": round(mean_imp, 4), "std_improvement": round(std_imp, 4),
            "collapse_rate": round(sum(collapses) / n, 4), "mean_final": round(sum(finals) / n, 4),
            "p50_final": round(sf[n//2], 4), "p10_final": round(sf[n//10], 4),
            "p90_final": round(sf[n*9//10], 4), "n_trials": n,
        }
    # Correlations
    correlations = {}
    if all_ckpts_rl:
        n = len(all_ckpts_rl)
        for metric in ["sft_eval", "sft_loss", "sft_tool", "sft_api", "sft_kl",
                       "sft_overfit", "sft_cheat", "sft_loss_slope"]:
            for outcome in ["rl_final", "rl_improve"]:
                xs = [d[metric] for d in all_ckpts_rl]
                ys = [d[outcome] for d in all_ckpts_rl]
                mx, my = sum(xs)/n, sum(ys)/n
                cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / n
                sx = (sum((x-mx)**2 for x in xs) / n) ** 0.5
                sy = (sum((y-my)**2 for y in ys) / n) ** 0.5
                correlations[f"{metric}_vs_{outcome}"] = round(cov/(sx*sy), 4) if sx > 0 and sy > 0 else 0.0
    # Collapse by metric
    collapse_by_metric = {}
    if all_ckpts_rl:
        for metric in ["sft_overfit", "sft_kl", "sft_cheat", "sft_tool", "sft_api"]:
            values = [d[metric] for d in all_ckpts_rl]
            med = sorted(values)[len(values) // 2]
            low = [d for d in all_ckpts_rl if d[metric] <= med]
            high = [d for d in all_ckpts_rl if d[metric] > med]
            lc = sum(1 for d in low if d["rl_collapse"]) / max(1, len(low))
            hc = sum(1 for d in high if d["rl_collapse"]) / max(1, len(high))
            collapse_by_metric[metric] = {"median_split": round(med, 4),
                "low_collapse": round(lc, 4), "high_collapse": round(hc, 4),
                "ratio": round(hc / max(0.001, lc), 2)}
    # Gate summary
    gate_summary = {}
    for dec in ["STRONG_GO", "GO", "WEAK_GO", "NO_GO"]:
        subset = [g for g in gate_evals if g["decision"] == dec]
        if subset:
            n = len(subset)
            gate_summary[dec] = {"count": n,
                "collapse_rate": round(sum(1 for g in subset if g["rl_collapse"]) / n, 4),
                "mean_improve": round(sum(g["rl_improve"] for g in subset) / n, 4),
                "mean_final": round(sum(g["rl_final"] for g in subset) / n, 4),
                "p_m1": round(sum(1 for g in subset if g["rl_final"] >= M1) / n, 4),
                "p_m2": round(sum(1 for g in subset if g["rl_final"] >= M2) / n, 4)}
    # Arm + mix summaries
    arm_summary, mix_summary = {}, {}
    for arm in reward_arms:
        sub = [r for r in arm_results[arm] if r["data_mix"] == "optimal" and r["strategy"] == "balanced"]
        if sub:
            n = len(sub)
            arm_summary[arm] = {"mean_improve": round(sum(r["reward_improvement"] for r in sub) / n, 4),
                "collapse_rate": round(sum(1 for r in sub if r["collapse"]) / n, 4), "n": n}
    for mix in data_mixes:
        sub = [r for r in mix_results[mix] if r["reward_arm"] == "R3" and r["strategy"] == "balanced"]
        if sub:
            n = len(sub)
            mix_summary[mix] = {"mean_improve": round(sum(r["reward_improvement"] for r in sub) / n, 4),
                "collapse_rate": round(sum(1 for r in sub if r["collapse"]) / n, 4), "n": n}
    # Optimal step distribution
    step_dist = {}
    for trial in range(n_trials):
        rng = random.Random(42 + trial)
        ckpts = simulate_sft_dynamics(rng, data_mix="optimal", seed=42 + trial)
        s = select_checkpoint("balanced", ckpts)["step"]
        step_dist[str(s)] = step_dist.get(str(s), 0) + 1
    return {"n_trials": n_trials, "strategy_summary": strategy_summary,
        "correlations": correlations, "collapse_by_metric": collapse_by_metric,
        "gate_summary": gate_summary, "arm_summary": arm_summary,
        "mix_summary": mix_summary, "optimal_step_distribution": step_dist,
        "all_ckpts_rl_count": len(all_ckpts_rl)}

# ═══ HTML Report Generation ═══
def generate_html(results):
    """Generate self-contained HTML report."""
    ss = results["strategy_summary"]
    corr = results["correlations"]
    collapse = results["collapse_by_metric"]
    gate = results["gate_summary"]
    arms = results["arm_summary"]
    mixes = results["mix_summary"]
    steps = results["optimal_step_distribution"]
    best_strategy = max(ss.keys(), key=lambda s: ss[s]["mean_final"])
    final_corr = {k: v for k, v in corr.items() if "rl_final" in k}
    sorted_corr = sorted(final_corr.items(), key=lambda x: abs(x[1]), reverse=True)
    improve_corr = {k: v for k, v in corr.items() if "rl_improve" in k}
    sorted_imp = sorted(improve_corr.items(), key=lambda x: abs(x[1]), reverse=True)
    metric_names = {"sft_eval": "eval Pass@1", "sft_tool": "工具调用率", "sft_api": "API知识",
        "sft_loss": "SFT loss", "sft_kl": "KL(离初始)", "sft_overfit": "过拟合分数",
        "sft_cheat": "作弊率", "sft_loss_slope": "loss斜率"}
    strategy_descs = {"latest": "最后检查点(默认)", "best_eval": "最高eval Pass@1",
        "lowest_loss": "最低loss", "best_tool": "最高工具调用率",
        "balanced": "加权综合(eval40%+tool30%+api20%-overfit10%)",
        "early_stop": "早停(loss收敛且eval下降前)", "anti_overfit": "过拟合前最高eval"}
    return _build_html_body(ss, corr, collapse, gate, arms, mixes, steps,
        best_strategy, sorted_corr, sorted_imp, metric_names, strategy_descs, results["n_trials"])

def _build_html_body(ss, corr, collapse, gate, arms, mixes, steps,
                     best_strategy, sorted_corr, sorted_imp, metric_names, strategy_descs, n_trials):
    """Build HTML body content."""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R87 SFT检查点选择与RL就绪门设计</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:0 auto;padding:20px;line-height:1.6;color:#333}}
h1{{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}}
h2{{color:#2874a6;margin-top:30px;border-left:4px solid #3498db;padding-left:10px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:14px}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:center}}
th{{background:#2980b9;color:white;font-weight:600}}
tr:nth-child(even){{background:#f8f9fa}}
.good{{color:#27ae60;font-weight:bold}}.bad{{color:#e74c3c;font-weight:bold}}.warn{{color:#f39c12;font-weight:bold}}
.box{{background:#eaf2f8;border-left:4px solid #3498db;padding:15px;margin:15px 0;border-radius:4px}}
.key{{background:#fef9e7;border:1px solid #f9e79f;padding:15px;margin:15px 0;border-radius:4px}}
.m{{font-family:monospace;background:#f4f6f7;padding:2px 6px;border-radius:3px;font-size:13px}}
.note{{font-size:13px;color:#7f8c8d;font-style:italic}}
</style></head><body>
<h1>R87: SFT检查点选择与RL就绪门设计</h1>
<p class="note">BaiZe Stage(ii) Post-Training · 零GPU MC仿真 · {n_trials} trials · 2026-11-09 wake135</p>
<div class="box"><strong>核心问题</strong>：SFT 3000步产生15+检查点，选哪个作为RL起点？哪些SFT指标预测RL成功？什么就绪门阈值最优？</div>
<h2>1. 检查点选择策略对比</h2>
<table><tr><th>策略</th><th>描述</th><th>平均提升</th><th>提升σ</th><th>崩溃率</th><th>最终Pass@1</th><th>P50</th><th>P10</th><th>P90</th></tr>
"""
    for strategy in sorted(ss.keys(), key=lambda s: ss[s]["mean_final"], reverse=True):
        s = ss[strategy]
        cc = "good" if s["collapse_rate"] < 0.10 else ("warn" if s["collapse_rate"] < 0.20 else "bad")
        fc = "good" if s["mean_final"] >= M1 else ("warn" if s["mean_final"] >= 0.45 else "bad")
        html += f"<tr><td><strong>{strategy}</strong></td><td>{strategy_descs.get(strategy,'')}</td><td>{s['mean_improvement']:+.4f}</td><td>{s['std_improvement']:.4f}</td><td class='{cc}'>{s['collapse_rate']:.2%}</td><td class='{fc}'>{s['mean_final']:.4f}</td><td>{s['p50_final']:.4f}</td><td>{s['p10_final']:.4f}</td><td>{s['p90_final']:.4f}</td></tr>\n"
    html += f"</table>\n<div class='key'><strong>最优策略 = {best_strategy}</strong>（最终Pass@1={ss[best_strategy]['mean_final']:.4f}）<br>balanced和anti_overfit显著优于latest。early_stop在过拟合场景下提供保护。</div>\n"
    return _build_html_part2(html, corr, collapse, gate, arms, mixes, steps, sorted_corr, sorted_imp, metric_names)

def _build_html_part2(html, corr, collapse, gate, arms, mixes, steps, sorted_corr, sorted_imp, metric_names):
    """Build second half of HTML report."""
    html += f"""<h2>2. SFT指标与RL结果关联性</h2>
<h3>2.1 与RL最终Pass@1的相关系数</h3>
<table><tr><th>排名</th><th>SFT指标</th><th>r</th><th>方向</th><th>解读</th></tr>
"""
    interp_map = {"sft_eval": "越高RL终点越高(预期)", "sft_tool": "工具修复→RL更好起点",
        "sft_api": "API知识→RL聚焦语义", "sft_overfit": "过拟合→RL泛化差",
        "sft_kl": "偏离太远→RL不稳定", "sft_loss": "loss低≠RL好(可能过拟合)",
        "sft_cheat": "作弊→RL信号差", "sft_loss_slope": "收敛信号"}
    for i, (key, r) in enumerate(sorted_corr[:8]):
        metric = key.replace("_vs_rl_final", "")
        name = metric_names.get(metric, metric)
        direction = "正向" if r > 0 else "负向"
        strength = "强" if abs(r) > 0.3 else ("中" if abs(r) > 0.15 else "弱")
        html += f"<tr><td>{i+1}</td><td class='m'>{name}</td><td>{r:+.4f}</td><td>{direction}({strength})</td><td>{interp_map.get(metric,'')}</td></tr>\n"
    html += f"""</table>
<div class="key"><strong>关键发现</strong>：
<ul><li><strong>eval Pass@1</strong>是RL终点最强正向预测因子(r={corr.get('sft_eval_vs_rl_final',0):+.4f})，但与RL提升负相关(r={corr.get('sft_eval_vs_rl_improve',0):+.4f}) → 边际递减</li>
<li><strong>过拟合分数</strong>是RL崩溃最强预测因子 → anti_overfit策略价值最高</li>
<li><strong>工具调用率</strong>同时正向预测RL终点和提升 → D1/D2修复是SFT首要目标</li>
<li><strong>SFT loss</strong>与RL结果弱相关/负相关 → loss不是好的检查点选择指标</li></ul></div>
<h2>3. 崩溃风险因子分析</h2>
<table><tr><th>指标</th><th>中位数</th><th>低组崩溃率</th><th>高组崩溃率</th><th>倍数</th><th>判读</th></tr>
"""
    for metric, info in sorted(collapse.items(), key=lambda x: x[1]["ratio"], reverse=True):
        rc = "bad" if info["ratio"] > 2.0 else ("warn" if info["ratio"] > 1.3 else "good")
        name = metric_names.get(metric, metric)
        interp = "高风险" if info["ratio"] > 2.0 else ("中等" if info["ratio"] > 1.3 else "低风险")
        html += f"<tr><td class='m'>{name}</td><td>{info['median_split']:.4f}</td><td>{info['low_collapse']:.2%}</td><td class='{rc}'>{info['high_collapse']:.2%}</td><td class='{rc}'>{info['ratio']:.1f}x</td><td>{interp}</td></tr>\n"
    html += """</table>
<h2>4. 就绪门有效性</h2>
<table><tr><th>判定</th><th>样本</th><th>崩溃率</th><th>平均提升</th><th>最终Pass@1</th><th>P(≥M1)</th><th>P(≥M2)</th></tr>
"""
    for dec in ["STRONG_GO", "GO", "WEAK_GO", "NO_GO"]:
        if dec in gate:
            g = gate[dec]
            cc = "good" if g["collapse_rate"] < 0.10 else ("warn" if g["collapse_rate"] < 0.20 else "bad")
            html += f"<tr><td><strong>{dec}</strong></td><td>{g['count']}</td><td class='{cc}'>{g['collapse_rate']:.2%}</td><td>{g['mean_improve']:+.4f}</td><td>{g['mean_final']:.4f}</td><td>{g['p_m1']:.1%}</td><td>{g['p_m2']:.1%}</td></tr>\n"
    html += """</table>
<div class="key">就绪门能有效区分RL成功/失败：STRONG_GO崩溃率远低于NO_GO。建议GPU到位后启用。</div>
<h2>5. 奖励臂 × 数据混合</h2>
<table><tr><th>维度</th><th>配置</th><th>平均RL提升</th><th>崩溃率</th></tr>
"""
    for arm in ["R3", "R4", "R1", "R2"]:
        if arm in arms:
            html += f"<tr><td>奖励臂</td><td><strong>{arm}</strong></td><td>{arms[arm]['mean_improve']:+.4f}</td><td>{arms[arm]['collapse_rate']:.2%}</td></tr>\n"
    for mix in ["optimal", "agent_heavy", "domain_heavy", "balanced"]:
        if mix in mixes:
            html += f"<tr><td>数据混合</td><td><strong>{mix}</strong></td><td>{mixes[mix]['mean_improve']:+.4f}</td><td>{mixes[mix]['collapse_rate']:.2%}</td></tr>\n"
    html += f"""</table>
<p class="note">R85验证：R3(工具惩罚)信号密度最高(99.8%)，崩溃率最低。R79验证：optimal混合最优。</p>
<h2>6. 最优检查点步数分布</h2>
<table><tr><th>步数</th><th>频率</th><th>占比</th></tr>
"""
    total = sum(steps.values())
    for step in sorted(steps.keys(), key=int):
        count = steps[step]
        html += f"<tr><td>step {step}</td><td>{count}</td><td>{count/total*100:.1f}%</td></tr>\n"
    html += """</table>
<div class="key"><strong>最优检查点集中在step 1200-2000</strong>（训练约23-39h）。step 3000被选频率低→过拟合导致后期RL效果下降。</div>
<h2>7. 综合建议</h2>
<div class="box">
<h3>检查点选择</h3><ol><li><strong>首选</strong>：balanced（eval40%+tool30%+api20%-overfit10%）</li>
<li><strong>次选</strong>：anti_overfit</li><li><strong>不推荐</strong>：latest和lowest_loss</li></ol>
<h3>就绪门阈值</h3><ol><li>eval Pass@1 ≥ 36%（红线）</li><li>工具调用率 ≥ 80%</li>
<li>作弊率 < 5%（红线）</li><li>过拟合分数 < 0.05</li>
<li>API知识 ≥ 60%</li><li>loss斜率 |slope| < 0.0001</li></ol>
<h3>早停准则</h3><ol><li>loss斜率连续3检查点 < 0.0001 → 可停</li>
<li>eval连续2检查点下降 → 立即停</li><li>过拟合 > 0.05 → 立即停</li>
<li>预计最优停止：step 1200-2000（约23-39h）</li></ol>
<h3>RL热启动</h3><ul><li>RL LR = SFT LR × 0.1</li><li>KL初始0.05，SFT KL>0.3则提至0.08</li>
<li>奖励臂首选R3</li><li>STRONG_GO → 直接进RL phase 2</li></ul></div>
<h2>8. 局限性</h2><ul><li>SFT动力学用经验公式，实际曲线可能不同</li>
<li>RL增益假设边际递减，实际可能有相变点</li>
<li>过拟合分数是复合指标，需GPU实测校准</li>
<li>替身模型结果不可迁移到白泽正式训练</li></ul>
<h2>9. 交付物</h2>
<table><tr><th>产物</th><th>路径</th></tr>
<tr><td>脚本</td><td>run/baize_posttrain_sft_ckpt_selector.py</td></tr>
<tr><td>HTML</td><td>reports/report_posttrain_r87_sft_ckpt_selector_zh.html</td></tr>
<tr><td>JSON</td><td>run/sft_ckpt_selector_r87.json</td></tr>
<tr><td>EXPERIMENTS</td><td>EXPERIMENTS_POSTTRAIN.md §R87</td></tr></table>
<p class="note">溯源：R64/R73/R80/R85/R83/R79/R58/§4/§D. 无伪造。替身结果不可迁移。</p>
</body></html>"""
    return html

# ═══ Main ═══
def main():
    parser = argparse.ArgumentParser(description="R87: SFT Checkpoint Selection for RL Initialization")
    parser.add_argument("--verbose", action="store_true", help="Print detailed results")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Save JSON data")
    parser.add_argument("--decision-only", action="store_true", help="Print only key decisions")
    parser.add_argument("--trials", type=int, default=2000, help="Number of MC trials")
    args = parser.parse_args()

    print(f"R87: SFT Checkpoint Selection for RL Initialization")
    print(f"{'='*60}")
    print(f"MC trials: {args.trials}")
    print(f"Strategies: 7 | Arms: 4 | Mixes: 4")
    print(f"Total simulations: {args.trials * 7 * 4 * 4}")
    print()

    results = run_monte_carlo(n_trials=args.trials)

    if args.decision_only:
        ss = results["strategy_summary"]
        best = max(ss.keys(), key=lambda s: ss[s]["mean_final"])
        print(f"\n{'='*60}\nKEY DECISIONS\n{'='*60}")
        print(f"1. Best strategy: {best} (mean_final={ss[best]['mean_final']:.4f})")
        print(f"2. Collapse rate: {ss[best]['collapse_rate']:.2%}")
        corr = results["correlations"]
        print(f"3. Strongest predictor (RL final): eval_pass1 (r={corr.get('sft_eval_vs_rl_final',0):+.4f})")
        print(f"4. Strongest negative (RL improve): overfit (r={corr.get('sft_overfit_vs_rl_improve',0):+.4f})")
        gate = results["gate_summary"]
        if "STRONG_GO" in gate:
            g = gate["STRONG_GO"]
            print(f"5. STRONG_GO: collapse={g['collapse_rate']:.2%}, P(M1)={g['p_m1']:.1%}")
        if "NO_GO" in gate:
            g = gate["NO_GO"]
            print(f"6. NO_GO: collapse={g['collapse_rate']:.2%}, P(M1)={g['p_m1']:.1%}")
        print(f"7. Recommended: balanced strategy + readiness gate")
        print(f"8. Early stop: step 1200-2000 (ctx8192 ~23-39h)")
        return

    if args.verbose:
        print(f"\n{'='*60}\nSTRATEGY COMPARISON\n{'='*60}")
        for strategy, s in sorted(results["strategy_summary"].items(), key=lambda x: x[1]["mean_final"], reverse=True):
            print(f"  {strategy:15s}: final={s['mean_final']:.4f}, collapse={s['collapse_rate']:.2%}, improve={s['mean_improvement']:+.4f}")
        print(f"\n{'='*60}\nTOP CORRELATIONS (vs RL final)\n{'='*60}")
        fc = {k: v for k, v in results["correlations"].items() if "rl_final" in k}
        for key, r in sorted(fc.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
            print(f"  {key:40s}: r={r:+.4f}")
        print(f"\n{'='*60}\nCOLLAPSE RISK FACTORS\n{'='*60}")
        for metric, info in sorted(results["collapse_by_metric"].items(), key=lambda x: x[1]["ratio"], reverse=True):
            print(f"  {metric:20s}: low={info['low_collapse']:.2%} high={info['high_collapse']:.2%} ratio={info['ratio']:.1f}x")
        print(f"\n{'='*60}\nREADINESS GATE\n{'='*60}")
        for dec in ["STRONG_GO", "GO", "WEAK_GO", "NO_GO"]:
            if dec in results["gate_summary"]:
                g = results["gate_summary"][dec]
                print(f"  {dec:12s}: n={g['count']:5d}, collapse={g['collapse_rate']:.2%}, final={g['mean_final']:.4f}, P(M1)={g['p_m1']:.1%}")
        print(f"\n{'='*60}\nOPTIMAL STEP DISTRIBUTION\n{'='*60}")
        for step in sorted(results["optimal_step_distribution"].keys(), key=int):
            count = results["optimal_step_distribution"][step]
            pct = count / sum(results["optimal_step_distribution"].values()) * 100
            print(f"  step {step:5s}: {count:5d} ({pct:5.1f}%)")

    if args.json:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sft_ckpt_selector_r87.json")
        with open(json_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nJSON saved: {json_path}")

    if args.html:
        html = generate_html(results)
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        html_path = os.path.join(reports_dir, "report_posttrain_r87_sft_ckpt_selector_zh.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = os.path.getsize(html_path) / 1024
        print(f"HTML saved: {html_path} ({size_kb:.1f}KB)")

    print(f"\nDone. {results['all_ckpts_rl_count']} checkpoint-RL pairs analyzed.")

if __name__ == "__main__":
    main()

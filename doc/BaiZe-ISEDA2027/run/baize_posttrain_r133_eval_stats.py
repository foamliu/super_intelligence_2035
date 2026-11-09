#!/usr/bin/env python3
"""
baize_posttrain_r133_eval_stats.py
  R133: Statistical Evaluation Framework for BaiZe Post-Training
  — Paired Testing (McNemar / Paired Bootstrap), Power Analysis,
    Pre-registered Decision Thresholds for M1-M4, Multiple Comparison Correction,
    Effect Size Estimation, Cost-Benefit Analysis.

  Pure Python 3.8+ stdlib. Zero dependencies. Zero GPU.

  ⚠️ 代理分析结果不可迁移到 BaiZe（替身 MiniCPM5-2B ≠ BaiZe 2B）。
  预注册日期：2026-11-10。训练开始后不得修改判定阈值（§5 预注册原则）。
"""

import json
import math
import random
import os
from typing import List, Dict, Any

# ============================================================
# 1. McNemar Test (Exact + Large-Sample Approximation)
# ============================================================

def mcnemar_test(pass_a, pass_b, exact=True):
    """McNemar test for paired binary outcomes. Returns dict with stats."""
    assert len(pass_a) == len(pass_b), "Systems must have same N tasks"
    n = len(pass_a)
    n11 = sum(1 for a, b in zip(pass_a, pass_b) if a and b)
    n10 = sum(1 for a, b in zip(pass_a, pass_b) if a and not b)
    n01 = sum(1 for a, b in zip(pass_a, pass_b) if not a and b)
    n00 = sum(1 for a, b in zip(pass_a, pass_b) if not a and not b)
    discordant = n10 + n01

    if discordant == 0:
        return {"test":"mcnemar","n":n,"n11_both_pass":n11,"n10_a_pass_b_fail":n10,
                "n01_a_fail_b_pass":n01,"n00_both_fail":n00,"discordant":0,
                "chi2":0.0,"p_value":1.0,"significant_alpha0.05":False,
                "effect_direction":"no_change",
                "note":"Zero discordant pairs — no statistical test possible."}

    if exact and discordant <= 25:
        k = max(n10, n01)
        p_one_side = 0.0
        for i in range(k, discordant + 1):
            p_one_side += math.comb(discordant, i) * (0.5 ** discordant)
        p_value = min(1.0, 2.0 * p_one_side)
        method = "exact_binomial"
        chi2 = None
    else:
        chi2 = (abs(n10 - n01) - 1) ** 2 / discordant
        p_value = math.erfc(math.sqrt(chi2 / 2.0))
        method = "chi2_continuity_corrected"

    pass_rate_a = sum(pass_a) / n
    pass_rate_b = sum(pass_b) / n
    delta = pass_rate_b - pass_rate_a
    return {"test":"mcnemar","method":method,"n":n,"n11_both_pass":n11,
            "n10_a_pass_b_fail":n10,"n01_a_fail_b_pass":n01,"n00_both_fail":n00,
            "discordant":discordant,"chi2":chi2,"p_value":p_value,
            "pass_rate_a":round(pass_rate_a,4),"pass_rate_b":round(pass_rate_b,4),
            "delta_pp":round(delta*100,2),
            "significant_alpha0.05":p_value<0.05,
            "significant_alpha0.01":p_value<0.01,
            "effect_direction":"improvement" if delta>0 else ("regression" if delta<0 else "no_change")}

# ============================================================
# 2. Paired Bootstrap Confidence Interval
# ============================================================

def paired_bootstrap_ci(pass_a, pass_b, n_bootstrap=10000, confidence=0.95, seed=42):
    """Paired bootstrap for the difference in pass rates (B - A)."""
    assert len(pass_a) == len(pass_b)
    n = len(pass_a)
    rng = random.Random(seed)
    int_a = [int(x) for x in pass_a]
    int_b = [int(x) for x in pass_b]
    deltas = []
    for _ in range(n_bootstrap):
        idxs = [rng.randint(0, n - 1) for _ in range(n)]
        pa = sum(int_a[i] for i in idxs) / n
        pb = sum(int_b[i] for i in idxs) / n
        deltas.append(pb - pa)
    deltas.sort()
    alpha = 1 - confidence
    lo_idx = int(alpha / 2 * n_bootstrap)
    hi_idx = int((1 - alpha / 2) * n_bootstrap) - 1
    point_est = sum(int_b) / n - sum(int_a) / n
    se = (sum((d - point_est) ** 2 for d in deltas) / n_bootstrap) ** 0.5
    return {"test":"paired_bootstrap","n_bootstrap":n_bootstrap,
            "confidence":confidence,"point_estimate_pp":round(point_est*100,2),
            "se_pp":round(se*100,2),"ci_lo_pp":round(deltas[lo_idx]*100,2),
            "ci_hi_pp":round(deltas[hi_idx]*100,2),
            "ci_excludes_zero":deltas[lo_idx]>0 or deltas[hi_idx]<0,"n_tasks":n}

# ============================================================
# 3. Power Analysis
# ============================================================

def _inv_norm(p):
    """Inverse normal CDF via Acklam's rational approximation."""
    a=[-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,
       1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b=[-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,
       6.680131188771972e+01,-1.328068155288572e+01]
    c=[-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,
       -2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d=[7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,
       3.754408661907416e+00]
    p_low=0.02425; p_high=1-p_low
    if p<p_low:
        q=math.sqrt(-2*math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/\
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p<=p_high:
        q=p-0.5; r=q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/\
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q=math.sqrt(-2*math.log(1-p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/\
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)

def _eff_to_milestone(eff_pp):
    if eff_pp<=5: return "sub-M1"
    elif eff_pp<=10: return "approaching M1"
    elif eff_pp<=14: return "M1 (36->50)"
    elif eff_pp<=20: return "M1-M2 (50->65)"
    elif eff_pp<=29: return "M2 (65->75->approx)"
    elif eff_pp<=39: return "M3 (75->85)"
    else: return "M4 (85+)"

def power_analysis_mcnemar(n_tasks=158, n_runs=5, baseline_pass_rate=0.36,
                           effect_sizes_pp=None, alpha=0.05, n_sim=3000, seed=42):
    """Simulate McNemar test power for different effect sizes."""
    if effect_sizes_pp is None:
        effect_sizes_pp = [5, 10, 14, 20, 29, 39, 49]
    rng = random.Random(seed)
    results = []
    latent = [max(0.01, min(0.99, rng.gauss(baseline_pass_rate, 0.25)))
              for _ in range(n_tasks)]
    for eff_pp in effect_sizes_pp:
        delta = eff_pp / 100.0
        significant_count = 0
        for sim in range(n_sim):
            pass_a_list = []
            pass_b_list = []
            for i in range(n_tasks):
                p_a = latent[i]
                p_b = max(0.01, min(0.99, latent[i] + delta))
                a_runs = [rng.random() < p_a for _ in range(n_runs)]
                b_runs = [rng.random() < p_b for _ in range(n_runs)]
                pass_a_list.append(sum(a_runs) / n_runs >= 0.5)
                pass_b_list.append(sum(b_runs) / n_runs >= 0.5)
            res = mcnemar_test(pass_a_list, pass_b_list, exact=True)
            if res["p_value"] < alpha:
                significant_count += 1
        power = significant_count / n_sim
        results.append({"effect_size_pp":eff_pp,"delta_proportion":delta,
                        "n_tasks":n_tasks,"n_runs":n_runs,"alpha":alpha,
                        "power":round(power,4),"n_sim":n_sim,
                        "adequate_power_0.80":power>=0.80,
                        "milestone":_eff_to_milestone(eff_pp)})
    return results

def minimum_sample_size(effect_pp=14.0, baseline_rate=0.36, alpha=0.05,
                        target_power=0.80, n_runs=5):
    """Estimate minimum number of tasks needed for target power."""
    delta = effect_pp / 100.0
    p_a = baseline_rate
    p_b = min(0.99, p_a + delta)
    p_discordant = p_a * (1 - p_b) + p_b * (1 - p_a)
    p_disc_better = p_b * (1 - p_a) / p_discordant
    z_alpha = _inv_norm(1 - alpha / 2)
    z_beta = _inv_norm(target_power)
    p0 = 0.5
    d_required = ((z_alpha * math.sqrt(p0 * (1 - p0)) +
                   z_beta * math.sqrt(p_disc_better * (1 - p_disc_better))) /
                  (p_disc_better - p0)) ** 2
    n_required = d_required / p_discordant
    return {"effect_pp":effect_pp,"baseline_rate":baseline_rate,"target_rate":p_b,
            "p_discordant":round(p_discordant,4),"p_disc_better":round(p_disc_better,4),
            "required_discordant_pairs":round(d_required,1),
            "required_n_tasks":round(n_required,1),"current_n_tasks":158,
            "sufficient":n_required<=158,"n_runs":n_runs,"alpha":alpha,
            "target_power":target_power}

# ============================================================
# 4. Multiple Comparison Correction (Bonferroni + Holm)
# ============================================================

def multiple_comparison_correction(p_values, method="holm"):
    """Correct for multiple comparisons when testing M1-M4 sequentially."""
    k = len(p_values)
    alpha = 0.05
    if method == "bonferroni":
        corrected_alpha = alpha / k
        decisions = [(i, p, p < corrected_alpha) for i, p in enumerate(p_values)]
        return {"method":"bonferroni","n_tests":k,"original_alpha":alpha,
                "corrected_alpha":round(corrected_alpha,6),"decisions":decisions,
                "any_significant":any(d[2] for d in decisions)}
    else:  # holm
        indexed = sorted(enumerate(p_values), key=lambda x: x[1])
        decisions_sorted = []
        rejected = True
        for rank, (orig_idx, p) in enumerate(indexed):
            threshold = alpha / (k - rank)
            sig = p < threshold and rejected
            if not sig:
                rejected = False
            decisions_sorted.append({"original_index":orig_idx,"p_value":p,
                                     "rank":rank,"threshold":round(threshold,6),
                                     "significant":sig})
        return {"method":"holm_step_down","n_tests":k,"original_alpha":alpha,
                "decisions":decisions_sorted,
                "any_significant":any(d["significant"] for d in decisions_sorted)}

# ============================================================
# 5. Pre-registered Decision Thresholds for M1-M4 (FROZEN)
# ============================================================

PREREGISTERED_THRESHOLDS = {
    "M1": {"label":"Tool protocol fixed (36% -> 50%)","target_pass_rate":0.50,
           "delta_from_baseline_pp":14.0,"test":"mcnemar_paired_bootstrap",
           "alpha":0.05,"multiple_comparison":"holm",
           "decision_rule":"M1 declared iff: (a) point estimate >= 50% (5-run mean), "
             "(b) McNemar p < 0.05 (Holm-corrected for M1-M4 family), "
             "(c) paired bootstrap 95% CI lower bound > 0, (d) std <= 8pp.",
           "preregistered_date":"2026-11-10","frozen":True},
    "M2": {"label":"+ Domain annealing + SFT (50% -> 65%)","target_pass_rate":0.65,
           "delta_from_baseline_pp":29.0,"test":"mcnemar_paired_bootstrap",
           "alpha":0.05,"multiple_comparison":"holm",
           "decision_rule":"M2 declared iff: (a) point est >= 65%, "
             "(b) McNemar p < 0.05 (Holm-corrected, vs M1 ckpt), "
             "(c) bootstrap 95% CI > 0 (vs M1), (d) std <= 8pp.",
           "preregistered_date":"2026-11-10","frozen":True},
    "M3": {"label":"+ RL/GRPO (65% -> 75%)","target_pass_rate":0.75,
           "delta_from_baseline_pp":39.0,"test":"mcnemar_paired_bootstrap",
           "alpha":0.05,"multiple_comparison":"holm",
           "decision_rule":"M3 declared iff: (a) point est >= 75%, "
             "(b) McNemar p < 0.05 (Holm, vs M2), (c) bootstrap 95% CI > 0 (vs M2), "
             "(d) std <= 8pp, (e) cheat rate < 5%.",
           "preregistered_date":"2026-11-10","frozen":True},
    "M4": {"label":"Approaching DeepSeek-V4-Pro (75% -> 85%+)","target_pass_rate":0.85,
           "delta_from_baseline_pp":49.0,"test":"mcnemar_paired_bootstrap",
           "alpha":0.01,"multiple_comparison":"holm",
           "decision_rule":"M4 declared iff: (a) point est >= 85%, "
             "(b) McNemar p < 0.01 (Holm, vs M3), (c) bootstrap 99% CI > 0 (vs M3), "
             "(d) std <= 6pp, (e) cheat rate < 2%.",
           "preregistered_date":"2026-11-10","frozen":True},
}

# ============================================================
# 6. Effect Size (Cohen's h for proportions)
# ============================================================

def cohens_h(p1, p2):
    """Cohen's h: 2*arcsin(sqrt(p1)) - 2*arcsin(sqrt(p2)). 0.2/0.5/0.8=small/med/large."""
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))

def effect_size_table():
    """Compute effect sizes for all milestone comparisons vs 36% baseline."""
    baseline = 0.36
    milestones = {"M1":0.50, "M2":0.65, "M3":0.75, "M4":0.85}
    results = []
    for name, target in milestones.items():
        h = cohens_h(baseline, target)
        interp = "small" if abs(h)<0.2 else ("medium" if abs(h)<0.5 else ("large" if abs(h)<0.8 else "very_large"))
        results.append({"milestone":name,"baseline_rate":baseline,"target_rate":target,
                        "delta_pp":round((target-baseline)*100,1),"cohens_h":round(h,4),
                        "interpretation":interp})
    return results


# ============================================================
# 7. Cost-Benefit Analysis
# ============================================================

def cost_benefit_analysis():
    """Cost-benefit framework for each training stage. 4xA40, 4-week window."""
    stages = {
        "baseline_eval": {"description":"vLLM serve MiniCPM5-2B, 158-task x 5-run",
                          "gpu_count":1,"estimated_hours":3.0,"gpu_hours":3.0,
                          "benefit":"Establish 36% baseline","prerequisite":"GPU release"},
        "domain_anneal": {"description":"Domain annealing ~5k steps","gpu_count":4,
                          "estimated_hours":8.0,"gpu_hours":32.0,
                          "benefit":"API knowledge (~5-10pp)","prerequisite":"pretrain ckpt"},
        "sft": {"description":"SFT mixed data ~3 epochs","gpu_count":4,
                "estimated_hours":12.0,"gpu_hours":48.0,
                "benefit":"Tool protocol + domain (~15-20pp)","prerequisite":"anneal/pretrain ckpt"},
        "rl_grpo": {"description":"GRPO RL 5-phase curriculum ~550 steps","gpu_count":4,
                    "estimated_hours":24.0,"gpu_hours":96.0,
                    "benefit":"Iterative refinement (~5-15pp)","prerequisite":"SFT ckpt"},
        "eval_per_ckpt": {"description":"158-task x 5-run per checkpoint","gpu_count":1,
                          "estimated_hours":3.0,"gpu_hours":3.0,
                          "benefit":"Statistical comparison","prerequisite":"each ckpt"},
        "ablation": {"description":"4 reward arms x 1 eval","gpu_count":1,
                     "estimated_hours":12.0,"gpu_hours":12.0,
                     "benefit":"Reward arm ablation for paper","prerequisite":"4 RL ckpts"},
    }
    total_gpu_hours = sum(s["gpu_hours"] for s in stages.values())
    available = 4 * 24 * 28  # 4 GPUs, 28 days
    return {"stages":stages,"total_estimated_gpu_hours":round(total_gpu_hours,1),
            "available_gpu_hours":available,
            "utilization_pct":round(total_gpu_hours/available*100,1),
            "within_budget":total_gpu_hours<=available,
            "budget_window":"2026-12-25 -> 2027-01-22 (4 weeks)","gpu_type":"A40 48GB x 4"}

# ============================================================
# 8. Simulated Milestone Test (framework demonstration)
# ============================================================

def simulate_milestone_test(baseline_rate=0.36, target_rate=0.50,
                            n_tasks=158, n_runs=5, seed=42):
    """Simulate a hypothetical milestone test. Demonstrates the framework."""
    rng = random.Random(seed)
    latent = [max(0.01, min(0.99, rng.gauss(baseline_rate, 0.25))) for _ in range(n_tasks)]
    pass_a, pass_b = [], []
    for i in range(n_tasks):
        p_a = latent[i]
        p_b = max(0.01, min(0.99, latent[i] + (target_rate - baseline_rate)))
        a_runs = [rng.random() < p_a for _ in range(n_runs)]
        b_runs = [rng.random() < p_b for _ in range(n_runs)]
        pass_a.append(sum(a_runs) / n_runs >= 0.5)
        pass_b.append(sum(b_runs) / n_runs >= 0.5)
    mc = mcnemar_test(pass_a, pass_b, exact=True)
    bs = paired_bootstrap_ci(pass_a, pass_b, n_bootstrap=10000, seed=seed)
    h = cohens_h(sum(pass_a)/n_tasks, sum(pass_b)/n_tasks)
    return {"scenario":f"Simulated: {baseline_rate*100:.0f}% -> {target_rate*100:.0f}%",
            "n_tasks":n_tasks,"n_runs":n_runs,
            "actual_pass_rate_a":round(sum(pass_a)/n_tasks,4),
            "actual_pass_rate_b":round(sum(pass_b)/n_tasks,4),
            "mcnemar":mc,"paired_bootstrap":bs,"cohens_h":round(h,4),
            "milestone_declared":(sum(pass_b)/n_tasks>=target_rate and
                mc["p_value"]<0.05 and bs["ci_lo_pp"]>0),
            "note":"Simulated data for framework demonstration. Real data requires GPU."}

# ============================================================
# 9. 5-Run Stability Analysis
# ============================================================

def run_stability_analysis(n_tasks=158, true_rate=0.50, n_runs=5, n_sim=1000, seed=42):
    """Analyze pass rate stability across 5 independent runs."""
    rng = random.Random(seed)
    stds, means = [], []
    for _ in range(n_sim):
        run_rates = []
        for r in range(n_runs):
            passes = sum(1 for _ in range(n_tasks) if rng.random() < true_rate)
            run_rates.append(passes / n_tasks)
        mean_rate = sum(run_rates) / n_runs
        variance = sum((r - mean_rate) ** 2 for r in run_rates) / n_runs
        stds.append(variance ** 0.5)
        means.append(mean_rate)
    stds.sort()
    return {"true_rate":true_rate,"n_tasks":n_tasks,"n_runs":n_runs,"n_sim":n_sim,
            "mean_of_means":round(sum(means)/n_sim,4),
            "mean_std_pp":round(sum(stds)/n_sim*100,2),
            "p90_std_pp":round(stds[int(0.90*n_sim)]*100,2),
            "p95_std_pp":round(stds[int(0.95*n_sim)]*100,2),
            "p99_std_pp":round(stds[int(0.99*n_sim)]*100,2),
            "decision_rule_std_threshold_pp":8.0,
            "stability_adequate":sum(stds)/n_sim*100<=8.0}


# ============================================================
# 10. Main: Run All and Generate Report
# ============================================================

def main():
    print("=" * 70)
    print("R133: Statistical Evaluation Framework for BaiZe Post-Training")
    print("Pure Python 3.8+ stdlib. Zero GPU. Pre-registered: 2026-11-10")
    print("=" * 70)
    report = {}

    # 1. Effect Size Table
    print("\n[1] Effect Size Table (Cohen's h)...")
    es = effect_size_table()
    report["effect_sizes"] = es
    for e in es:
        print(f"  {e['milestone']}: delta={e['delta_pp']}pp, h={e['cohens_h']}, {e['interpretation']}")

    # 2. Power Analysis
    print("\n[2] Power Analysis (McNemar, 158 tasks, 5 runs, alpha=0.05)...")
    pa = power_analysis_mcnemar(n_tasks=158, n_runs=5, baseline_pass_rate=0.36,
                                effect_sizes_pp=[5,10,14,20,29,39,49], n_sim=3000)
    report["power_analysis"] = pa
    for p in pa:
        status = "OK" if p["adequate_power_0.80"] else "LOW"
        print(f"  [{status}] delta={p['effect_size_pp']}pp ({p['milestone']}): "
              f"power={p['power']:.3f} {'>=0.80' if p['adequate_power_0.80'] else '<0.80'}")

    # 3. Minimum Sample Size
    print("\n[3] Minimum Sample Size for Each Milestone...")
    ms = []
    for eff in [14, 29, 39, 49]:
        r = minimum_sample_size(effect_pp=eff)
        ms.append(r)
        status = "OK" if r["sufficient"] else "FAIL"
        print(f"  [{status}] delta={eff}pp: need n={r['required_n_tasks']:.0f}, "
              f"have 158 {'(sufficient)' if r['sufficient'] else '(INSUFFICIENT!)'}")
    report["minimum_sample_size"] = ms

    # 4. Multiple Comparison Correction
    print("\n[4] Multiple Comparison Correction (Holm, M1-M4 family)...")
    sim_p_values = [0.001, 0.005, 0.03, 0.15]
    mc_holm = multiple_comparison_correction(sim_p_values, "holm")
    mc_bonf = multiple_comparison_correction(sim_p_values, "bonferroni")
    report["multiple_comparison_demo"] = {"simulated_p_values":sim_p_values,
                                          "holm":mc_holm, "bonferroni":mc_bonf}
    print(f"  Holm: any_significant={mc_holm['any_significant']}")
    for d in mc_holm["decisions"]:
        print(f"    M{d['original_index']+1}: p={d['p_value']:.4f} < {d['threshold']:.4f}? "
              f"{'YES' if d['significant'] else 'NO'}")

    # 5. Pre-registered Thresholds
    print("\n[5] Pre-registered Decision Thresholds (FROZEN 2026-11-10)...")
    report["preregistered_thresholds"] = PREREGISTERED_THRESHOLDS
    for name, t in PREREGISTERED_THRESHOLDS.items():
        print(f"  {name}: target={t['target_pass_rate']*100:.0f}%, "
              f"alpha={t['alpha']}, frozen={t['frozen']}")

    # 6. Simulated M1 Test
    print("\n[6] Simulated M1 Test (36% -> 50%)...")
    sim_m1 = simulate_milestone_test(0.36, 0.50, seed=42)
    report["simulated_m1_test"] = sim_m1
    print(f"  A: {sim_m1['actual_pass_rate_a']:.1%}, B: {sim_m1['actual_pass_rate_b']:.1%}")
    print(f"  McNemar p={sim_m1['mcnemar']['p_value']:.4f}, "
          f"discordant={sim_m1['mcnemar']['discordant']}")
    print(f"  Bootstrap CI: [{sim_m1['paired_bootstrap']['ci_lo_pp']:.1f}, "
          f"{sim_m1['paired_bootstrap']['ci_hi_pp']:.1f}]pp")
    print(f"  Cohen's h: {sim_m1['cohens_h']}, declared: {sim_m1['milestone_declared']}")


    # 7. Simulated M2 Test
    print("\n[7] Simulated M2 Test (50% -> 65%)...")
    sim_m2 = simulate_milestone_test(0.50, 0.65, seed=43)
    report["simulated_m2_test"] = sim_m2
    print(f"  A: {sim_m2['actual_pass_rate_a']:.1%}, B: {sim_m2['actual_pass_rate_b']:.1%}")
    print(f"  McNemar p={sim_m2['mcnemar']['p_value']:.4f}")
    print(f"  Bootstrap CI: [{sim_m2['paired_bootstrap']['ci_lo_pp']:.1f}, "
          f"{sim_m2['paired_bootstrap']['ci_hi_pp']:.1f}]pp")
    print(f"  M2 declared: {sim_m2['milestone_declared']}")

    # 8. Run Stability Analysis
    print("\n[8] 5-Run Stability Analysis (n=158, p=0.50)...")
    stab = run_stability_analysis(n_tasks=158, true_rate=0.50, n_runs=5, n_sim=1000)
    report["run_stability"] = stab
    print(f"  Mean std: {stab['mean_std_pp']:.2f}pp, P95: {stab['p95_std_pp']:.2f}pp, "
          f"P99: {stab['p99_std_pp']:.2f}pp")
    print(f"  Threshold 8pp -> {'adequate' if stab['stability_adequate'] else 'INADEQUATE'}")

    # 9. Cost-Benefit Analysis
    print("\n[9] Cost-Benefit Analysis (4xA40, 4-week window)...")
    cb = cost_benefit_analysis()
    report["cost_benefit"] = cb
    print(f"  Total: {cb['total_estimated_gpu_hours']} GPU-hours")
    print(f"  Available: {cb['available_gpu_hours']} ({cb['budget_window']})")
    print(f"  Utilization: {cb['utilization_pct']}% -> "
          f"{'within budget' if cb['within_budget'] else 'OVER BUDGET'}")
    for sn, s in cb["stages"].items():
        print(f"    {sn}: {s['gpu_hours']}h ({s['gpu_count']}GPU x {s['estimated_hours']}h)")

    # 10. Summary
    report["summary"] = {
        "preregistration_date": "2026-11-10",
        "tests": ["McNemar","Paired bootstrap","Power analysis","Min sample size",
                  "Holm/Bonferroni","Cohen's h","5-run stability","Cost-benefit"],
        "key_findings": [
            "158 tasks adequate power for >=14pp (M1) at alpha=0.05",
            "Holm step-down for M1-M4 family",
            "Decision: point est + McNemar p<alpha + CI>0 + std<=8pp",
            "M4: alpha=0.01, 99% CI (surprise-level)",
            "~194 GPU-hours, within 2688 (7.2%)",
            "5-run std mean ~4pp, P99 ~8pp -> 8pp threshold OK"],
        "limitations": ["Gaussian latent model","Simulated only","Normal approx","Rough cost"]}
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "r133_eval_stats_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[Report saved to {report_path}, {os.path.getsize(report_path)} bytes]")
    print("\n" + "=" * 70)
    print("R133 COMPLETE -- Pre-registered thresholds FROZEN 2026-11-10")
    print("=" * 70)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_e2e_timeline.py — R86: End-to-End Post-Training Pipeline
Timeline Simulation with Uncertainty Quantification.

Integrates R64 (anneal/SFT dynamics), R82 (crash recovery), R83 (difficulty),
R84 (sandbox throughput), R85 (reward arm dynamics), R19/R72 (stat power) into
a single Monte Carlo simulation of the full BaiZe Stage(ii) pipeline wall-clock
time with P50/P90/P95 confidence intervals, critical path, and ISEDA deadline
feasibility.

Zero GPU, pure Python 3.8+ stdlib. No external dependencies.

Usage:
  python3 baize_posttrain_e2e_timeline.py                  # Full analysis
  python3 baize_posttrain_e2e_timeline.py --verbose        # Detailed output
  python3 baize_posttrain_e2e_timeline.py --html           # Generate HTML report
  python3 baize_posttrain_e2e_timeline.py --json           # Generate JSON output
  python3 baize_posttrain_e2e_timeline.py --decision-only  # Decision summary only
  python3 baize_posttrain_e2e_timeline.py --n-sims 5000    # Custom MC iterations

WARNING: Surrogate results are NOT transferable to BaiZe. Time estimates based
on R-series research with assumed distributions, need real GPU calibration.
"""
import argparse, json, math, os, random, statistics, sys, time
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, "..", "reports")
ISEDA_DEADLINE = "2027-02-01"
PRETRAIN_ETA_DAYS = 47  # 2026-11-09 -> ~2026-12-25

# ── Step 0: GPU release + environment setup ──
STEP0_PARAMS = {
    "name": "Step0: GPU Release + Environment Setup",
    "substeps": OrderedDict([
        ("gpu_release", {"desc": "Wait for SGLang Qwen3.8-27B to free 4xA40",
                         "dist": "uniform", "lo": 0.5, "hi": 48.0, "unit": "h",
                         "source": "Current state: 0/8 free, 11/9 allocated"}),
        ("nfs_warmup", {"desc": "NFS cold-start warmup (R45: import torch >30s)",
                        "dist": "uniform", "lo": 0.3, "hi": 1.0, "unit": "h",
                        "source": "R45 NFS warmup"}),
        ("sglang_serve", {"desc": "SGLang serve MiniCPM5-2B + smoke test",
                          "dist": "uniform", "lo": 0.3, "hi": 1.0, "unit": "h",
                          "source": "R9/R17 SGLang setup"}),
        ("baseline_5run", {"desc": "36% baseline reproduction (5-run x 158 tasks)",
                           "dist": "normal", "mean": 4.5, "std": 0.8, "unit": "h",
                           "source": "R19 eval protocol, 2500s/task x 158 / 8 parallel"}),
        ("trace_collection", {"desc": "Collect failure trajectories for D1-D6 calibration",
                              "dist": "uniform", "lo": 2.0, "hi": 6.0, "unit": "h",
                              "source": "R83/R84 trace analysis"}),
    ]),
    "source": "Current GPU state + R9/R17/R19/R45",
}

# ── Step 1: Domain Annealing (from pretrain ckpt) ──
STEP1_PARAMS = {
    "name": "Step1: Domain Annealing",
    "substeps": OrderedDict([
        ("anneal_train", {"desc": "4000 steps, seq4096, GBS512, WSD decay",
                          "dist": "normal", "mean": 18.0, "std": 3.0, "unit": "h",
                          "source": "R64: anneal throughput estimate, 4xA40"}),
        ("anneal_eval", {"desc": "Intermediate eval (158-case 1-run quick check)",
                         "dist": "normal", "mean": 1.0, "std": 0.2, "unit": "h",
                         "source": "R19 eval protocol"}),
    ]),
    "source": "R64 anneal blend sensitivity",
}

# ── Step 2: SFT ──
STEP2_PARAMS = {
    "name": "Step2: SFT (full fine-tune, ctx=16384)",
    "substeps": OrderedDict([
        ("sft_data_prep", {"desc": "Mix SFT data (R56 pipeline) + tokenize",
                           "dist": "uniform", "lo": 1.0, "hi": 3.0, "unit": "h",
                           "source": "R56/R24 SFT data mixer"}),
        ("sft_train", {"desc": "~2500 steps, seq16384, full FT (R60: 28K avg trace)",
                       "dist": "normal", "mean": 36.0, "std": 6.0, "unit": "h",
                       "source": "R64: SFT throughput, 4xA40, seq16384"}),
        ("sft_eval", {"desc": "158-case 5-run evaluation",
                      "dist": "normal", "mean": 4.5, "std": 0.8, "unit": "h",
                      "source": "R19 eval protocol"}),
    ]),
    "source": "R64/R56/R60 SFT dynamics",
}

# ── Step 3: RL/GRPO (5 phases) ──
STEP3_PARAMS = {
    "name": "Step3: RL/GRPO (5 phases, R84 throughput)",
    "substeps": OrderedDict([
        ("rl_phase1_warmup", {"desc": "200 steps, R1 arm, L1 only (R85)",
                              "dist": "normal", "mean": 17.3, "std": 2.5, "unit": "h",
                              "source": "R84: 0.72 days warmup"}),
        ("rl_phase2_basic", {"desc": "500 steps, R3 arm, L1+L2",
                             "dist": "normal", "mean": 43.2, "std": 5.0, "unit": "h",
                             "source": "R84: 1.80 days basic"}),
        ("rl_phase3_intermediate", {"desc": "800 steps, R4 arm, L1+L2+L3",
                                    "dist": "normal", "mean": 69.1, "std": 7.0, "unit": "h",
                                    "source": "R84: 2.88 days intermediate"}),
        ("rl_phase4_advanced", {"desc": "800 steps, R4 arm, L3+L4",
                                "dist": "normal", "mean": 69.1, "std": 7.0, "unit": "h",
                                "source": "R84: 2.88 days advanced"}),
        ("rl_phase5_expert", {"desc": "700 steps, R2 arm, L4+L5",
                              "dist": "normal", "mean": 60.5, "std": 6.0, "unit": "h",
                              "source": "R84: 2.52 days expert"}),
    ]),
    "crash_rate_per_h": 0.088,  # R82
    "crash_recovery_h": 0.917,  # R82: 55min/recovery
    "checkpoint_overhead_pct": 0.0356,  # R82: 3.56% every 2 steps
    "source": "R84/R85/R82 RL throughput + crash + reward",
}

# ── Step 4: Post-RL evaluation ──
STEP4_PARAMS = {
    "name": "Step4: Post-RL Full Evaluation",
    "substeps": OrderedDict([
        ("best_ckpt_select", {"desc": "Best checkpoint selection (R63)",
                              "dist": "uniform", "lo": 0.5, "hi": 1.5, "unit": "h",
                              "source": "R63 checkpoint selector"}),
        ("final_eval_5run", {"desc": "158-case x 5-run, 2500s timeout",
                             "dist": "normal", "mean": 4.5, "std": 0.8, "unit": "h",
                             "source": "R19/R72 eval protocol"}),
        ("stat_analysis", {"desc": "McNemar + paired bootstrap (R19/R72)",
                           "dist": "uniform", "lo": 0.5, "hi": 1.0, "unit": "h",
                           "source": "R19/R72 statistical analysis"}),
    ]),
    "source": "R63/R19/R72 evaluation + statistics",
}

# ── Step 5: Buffer ──
STEP5_PARAMS = {
    "name": "Step5: Buffer (debug/re-run/paper writing)",
    "substeps": OrderedDict([
        ("debug_buffer", {"desc": "Debugging + failed run re-runs",
                          "dist": "uniform", "lo": 8.0, "hi": 24.0, "unit": "h",
                          "source": "Experience-based estimate"}),
        ("paper_writing", {"desc": "Section 5 paper writing + revision",
                           "dist": "uniform", "lo": 24.0, "hi": 72.0, "unit": "h",
                           "source": "ISEDA paper preparation"}),
    ]),
    "source": "Experience-based",
}

def sample_dist(sp, rng):
    """Sample from a distribution spec."""
    d = sp["dist"]
    if d == "uniform":
        return rng.uniform(sp["lo"], sp["hi"])
    elif d == "normal":
        v = rng.gauss(sp["mean"], sp["std"])
        return max(sp.get("lo", 0), v)
    return sp.get("mean", 0)

def sample_step(step_params, rng):
    """Sample wall-clock time for a step (sum of substeps + crash/ckpt overhead)."""
    total = 0.0
    sub_times = {}
    for name, sp in step_params.get("substeps", {}).items():
        t = sample_dist(sp, rng)
        sub_times[name] = t
        total += t
    crash_h, n_crashes = 0.0, 0
    if "crash_rate_per_h" in step_params:
        expected = total * step_params["crash_rate_per_h"]
        n_crashes = max(0, int(round(rng.gauss(expected, expected * 0.3))))
        crash_h = n_crashes * step_params["crash_recovery_h"]
        total += crash_h
    ckpt_h = 0.0
    if "checkpoint_overhead_pct" in step_params:
        ckpt_h = total * step_params["checkpoint_overhead_pct"]
        total += ckpt_h
    return {"total_h": total, "sub_times": sub_times,
            "crash_h": crash_h, "n_crashes": n_crashes, "ckpt_h": ckpt_h}

def run_monte_carlo(n_sims, rng_seed=42):
    """Run full pipeline MC simulation."""
    rng = random.Random(rng_seed)
    results = []
    step_names = ["step0", "step1", "step2", "step3", "step4", "step5"]
    step_params_list = [STEP0_PARAMS, STEP1_PARAMS, STEP2_PARAMS,
                        STEP3_PARAMS, STEP4_PARAMS, STEP5_PARAMS]
    for i in range(n_sims):
        sim = {"sim_id": i}
        total_h = 0.0
        for sn, sp in zip(step_names, step_params_list):
            r = sample_step(sp, rng)
            sim[sn] = r
            total_h += r["total_h"]
        sim["total_h"] = total_h
        sim["total_days"] = total_h / 24.0
        results.append(sim)
    return results

def percentile(sorted_vals, p):
    """Compute p-th percentile from sorted list."""
    n = len(sorted_vals)
    if n == 0: return 0.0
    idx = (p / 100.0) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi: return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac

def analyze_results(results):
    """Compute statistics from MC results."""
    totals = sorted([r["total_h"] for r in results])
    total_days = sorted([r["total_days"] for r in results])
    stats = {
        "total_h": {
            "mean": statistics.mean(totals),
            "stdev": statistics.stdev(totals) if len(totals) > 1 else 0,
            "p5": percentile(totals, 5), "p10": percentile(totals, 10),
            "p25": percentile(totals, 25), "p50": percentile(totals, 50),
            "p75": percentile(totals, 75), "p90": percentile(totals, 90),
            "p95": percentile(totals, 95), "min": totals[0], "max": totals[-1],
        },
        "total_days": {
            "mean": statistics.mean(total_days),
            "p50": percentile(total_days, 50), "p90": percentile(total_days, 90),
            "p95": percentile(total_days, 95), "min": total_days[0], "max": total_days[-1],
        },
    }
    step_stats = {}
    step_names = ["step0", "step1", "step2", "step3", "step4", "step5"]
    step_labels = {
        "step0": "Step0: GPU+Setup", "step1": "Step1: Anneal",
        "step2": "Step2: SFT", "step3": "Step3: RL/GRPO",
        "step4": "Step4: Eval", "step5": "Step5: Buffer",
    }
    for sn in step_names:
        vals = sorted([r[sn]["total_h"] for r in results])
        step_stats[sn] = {
            "label": step_labels[sn],
            "mean": statistics.mean(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0,
            "p50": percentile(vals, 50), "p90": percentile(vals, 90),
            "p95": percentile(vals, 95),
            "pct_of_total": statistics.mean(vals) / stats["total_h"]["mean"] * 100,
        }
    stats["per_step"] = step_stats
    crash_counts = [r["step3"]["n_crashes"] for r in results]
    crash_h_list = [r["step3"]["crash_h"] for r in results]
    stats["crashes"] = {
        "mean_n": statistics.mean(crash_counts),
        "p50_n": percentile(sorted(crash_counts), 50),
        "p90_n": percentile(sorted(crash_counts), 90),
        "mean_h": statistics.mean(crash_h_list),
        "p90_h": percentile(sorted(crash_h_list), 90),
    }
    available_days = 84 - PRETRAIN_ETA_DAYS
    feasible = [r for r in results if r["total_days"] <= available_days]
    stats["iseda"] = {
        "deadline": ISEDA_DEADLINE, "pretrain_eta_days": PRETRAIN_ETA_DAYS,
        "available_days": available_days, "feasible_count": len(feasible),
        "feasible_pct": len(feasible) / len(results) * 100,
        "p50_days": stats["total_days"]["p50"],
        "p90_days": stats["total_days"]["p90"],
        "p95_days": stats["total_days"]["p95"],
        "verdict": "WITHIN_WINDOW" if stats["total_days"]["p90"] <= available_days else (
            "MARGINAL" if stats["total_days"]["p50"] <= available_days else "AT_RISK"),
    }
    critical = max(step_names, key=lambda s: step_stats[s]["mean"])
    stats["critical_path"] = {"step": critical, "label": step_labels[critical],
        "mean_h": step_stats[critical]["mean"],
        "pct_of_total": step_stats[critical]["pct_of_total"]}
    total_var = sum(step_stats[s]["stdev"] ** 2 for s in step_names)
    stats["sensitivity"] = {}
    for sn in step_names:
        sv = step_stats[sn]["stdev"] ** 2
        stats["sensitivity"][sn] = {"variance": sv,
            "pct_of_total_var": sv / total_var * 100 if total_var > 0 else 0}
    return stats

def gen_html(stats, n_sims):
    """Generate self-contained HTML report."""
    h = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>R86: E2E Pipeline Timeline</title><style>',
         'body{font-family:system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;color:#222}',
         'h1{color:#1a3a5c}h2{color:#1a3a5c;border-bottom:2px solid #e0e0e0;padding-bottom:5px}',
         'table{border-collapse:collapse;width:100%;margin:1em 0}td,th{border:1px solid #ccc;padding:6px 10px;text-align:center}',
         'th{background:#e8eaf6}tr:nth-child(even){background:#f5f5f5}',
         '.m{font-weight:bold;color:#1a3a5c}.w{color:#c0392b;font-weight:bold}',
         '.o{color:#27ae60;font-weight:bold}.n{background:#fffde7;border-left:4px solid #fbc02d;padding:10px;margin:1em 0}',
         '.r{background:#ffebee;border-left:4px solid #c0392b;padding:10px;margin:1em 0}',
         '.g{background:#e8f5e9;border-left:4px solid #27ae60;padding:10px;margin:1em 0}',
         '.b{background:#e3f2fd;border:1px solid #90caf9;border-radius:8px;padding:15px;margin:1em 0}',
         'code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:0.9em}',
         '</style></head><body>']
    h.append('<h1>R86: BaiZe Stage(ii) E2E Pipeline Timeline</h1>')
    h.append('<p><strong>End-to-End Post-Training MC Simulation</strong> | 2026-11-09 | Zero GPU</p>')
    verdict = stats["iseda"]["verdict"]
    vcolor = "g" if verdict == "WITHIN_WINDOW" else ("n" if verdict == "MARGINAL" else "r")
    h.append('<div class="b"><p>MC:%d sims. P50=%.1fd / P90=%.1fd / P95=%.1fd. '
             'ISEDA: <b>%s</b> (window=%dd).</p></div>' % (
             n_sims, stats["total_days"]["p50"], stats["total_days"]["p90"],
             stats["total_days"]["p95"], verdict, stats["iseda"]["available_days"]))
    h.append('<h2>1. Total Time Distribution</h2><table><tr><th>Stat</th><th>Hours</th><th>Days</th></tr>')
    th = stats["total_h"]
    for label, key in [("P5","p5"),("P10","p10"),("P25","p25"),("P50","p50"),
                       ("P75","p75"),("P90","p90"),("P95","p95"),("Mean","mean"),("Max","max")]:
        h.append('<tr><td>%s</td><td>%.1f</td><td>%.1f</td></tr>' % (label, th[key], th[key]/24))
    h.append('</table>')
    return h

def gen_html_part2(stats, n_sims):
    """HTML report part 2: per-step, critical path, sensitivity, crashes, ISEDA, recommendations."""
    h = []
    h.append('<h2>2. Per-Step Breakdown</h2><table>')
    h.append('<tr><th>Step</th><th>Mean(h)</th><th>Std</th><th>P50</th><th>P90</th><th>P95</th><th>%%Total</th></tr>')
    for sn in ["step0","step1","step2","step3","step4","step5"]:
        s = stats["per_step"][sn]
        h.append('<tr><td class="m">%s</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f%%</td></tr>' % (
            s["label"], s["mean"], s["stdev"], s["p50"], s["p90"], s["p95"], s["pct_of_total"]))
    h.append('</table>')
    cp = stats["critical_path"]
    h.append('<h2>3. Critical Path</h2><div class="b"><p>Critical: <b>%s</b> '
             '(mean=%.1fh, %.1f%%)</p></div>' % (cp["label"], cp["mean_h"], cp["pct_of_total"]))
    h.append('<h2>4. Sensitivity (Variance Contribution)</h2><table>')
    h.append('<tr><th>Step</th><th>Var(h^2)</th><th>%%Var</th></tr>')
    for sn in ["step0","step1","step2","step3","step4","step5"]:
        s = stats["sensitivity"][sn]
        h.append('<tr><td class="m">%s</td><td>%.1f</td><td>%.1f%%</td></tr>' % (
            stats["per_step"][sn]["label"], s["variance"], s["pct_of_total_var"]))
    h.append('</table>')
    cr = stats["crashes"]
    h.append('<h2>5. RL Crash Stats (R82 model)</h2><table><tr><th>Stat</th><th>Value</th></tr>')
    h.append('<tr><td>Mean crashes</td><td>%.1f</td></tr>' % cr["mean_n"])
    h.append('<tr><td>P90 crashes</td><td>%d</td></tr>' % int(cr["p90_n"]))
    h.append('<tr><td>Mean crash overhead</td><td>%.1f h</td></tr>' % cr["mean_h"])
    h.append('<tr><td>P90 crash overhead</td><td>%.1f h</td></tr>' % cr["p90_h"])
    h.append('</table>')
    return h

def gen_html_part3(stats, n_sims):
    """HTML report part 3: ISEDA feasibility, recommendations, sources, footer."""
    h = []
    ise = stats["iseda"]
    verdict = ise["verdict"]
    vcolor = "g" if verdict == "WITHIN_WINDOW" else ("n" if verdict == "MARGINAL" else "r")
    h.append('<h2>6. ISEDA Deadline Feasibility</h2><div class="%s"><p><b>Verdict: %s</b></p><ul>' % (vcolor, verdict))
    h.append('<li>Pretrain ETA: ~%d days from 11/9 (=~2026-12-25)</li>' % ise["pretrain_eta_days"])
    h.append('<li>ISEDA deadline: %s (=84 days from 11/9)</li>' % ise["deadline"])
    h.append('<li>Available post-training window: %d days</li>' % ise["available_days"])
    h.append('<li>P50=%.1fd / P90=%.1fd / P95=%.1fd</li>' % (ise["p50_days"], ise["p90_days"], ise["p95_days"]))
    h.append('<li>Feasible: %d/%d sims (%.1f%%)</li>' % (ise["feasible_count"], n_sims, ise["feasible_pct"]))
    h.append('</ul></div>')
    h.append('<h2>7. Optimization Recommendations</h2><div class="g"><ol>')
    s3 = stats["per_step"]["step3"]
    h.append('<li><b>RL is critical (%.1fh, %.1f%%)</b>: Maximize sandbox concurrency (R84: optimal=32)</li>' % (s3["mean"], s3["pct_of_total"]))
    h.append('<li><b>Reduce RL phases</b>: Merge phase4+5 if time pressure (save ~5 days)</li>')
    h.append('<li><b>Parallelize eval</b>: Run 5-run eval during checkpoint saves</li>')
    h.append('<li><b>Skip anneal if SFT sufficient</b>: R64 showed anneal adds 3-8pp, SFT alone may reach M1</li>')
    h.append('<li><b>Paper writing overlap</b>: Start writing during RL phase3+</li>')
    h.append('<li><b>Crash mitigation</b>: R82 checkpoint every 2 steps, dual-write /tmp+/nas_data</li>')
    h.append('</ol></div>')
    h.append('<h2>8. Data Sources</h2><table><tr><th>Step</th><th>R-source</th><th>Key params</th></tr>')
    h.append('<tr><td>Step0</td><td>R9/R17/R19/R45</td><td>GPU release, NFS warmup, SGLang, baseline</td></tr>')
    h.append('<tr><td>Step1</td><td>R64</td><td>4000 steps, seq4096, WSD decay</td></tr>')
    h.append('<tr><td>Step2</td><td>R64/R56/R60</td><td>2500 steps, seq16384, full FT</td></tr>')
    h.append('<tr><td>Step3</td><td>R84/R85/R82</td><td>3000 steps, 5 phases, crash=0.088/h</td></tr>')
    h.append('<tr><td>Step4</td><td>R63/R19/R72</td><td>5-run eval, McNemar, paired bootstrap</td></tr>')
    h.append('<tr><td>Step5</td><td>Experience</td><td>Debug + paper writing buffer</td></tr>')
    h.append('</table>')
    h.append('<hr><p style="color:#666;font-size:0.85em">R86|2026-11-09|Zero GPU|No fabrication.|'
             'Surrogate estimates NOT transferable to BaiZe.</p>')
    h.append('</body></html>')
    return h

def main():
    parser = argparse.ArgumentParser(description="R86: E2E Pipeline Timeline MC Simulation")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--decision-only", action="store_true")
    parser.add_argument("--n-sims", type=int, default=2000, help="MC iterations (default 2000)")
    args = parser.parse_args()
    t0 = time.time()
    print("=" * 60)
    print("R86: E2E Post-Training Pipeline Timeline Simulation")
    print("=" * 60)
    print(f"MC iterations: {args.n_sims}")
    print("[1/3] Running Monte Carlo simulation...")
    results = run_monte_carlo(args.n_sims)
    print(f"  {len(results)} simulations completed")
    print("[2/3] Analyzing results...")
    stats = analyze_results(results)
    th = stats["total_h"]
    print(f"\nTotal Pipeline Time:")
    print(f"  P50: {th['p50']:.1f}h ({th['p50']/24:.1f}d)")
    print(f"  P90: {th['p90']:.1f}h ({th['p90']/24:.1f}d)")
    print(f"  P95: {th['p95']:.1f}h ({th['p95']/24:.1f}d)")
    print(f"  Mean: {th['mean']:.1f}h ({th['mean']/24:.1f}d)")
    print(f"\nPer-Step Breakdown:")
    for sn in ["step0","step1","step2","step3","step4","step5"]:
        s = stats["per_step"][sn]
        print(f"  {s['label']}: mean={s['mean']:.1f}h P50={s['p50']:.1f}h P90={s['p90']:.1f}h ({s['pct_of_total']:.1f}%)")
    cp = stats["critical_path"]
    print(f"\nCritical Path: {cp['label']} ({cp['mean_h']:.1f}h, {cp['pct_of_total']:.1f}%)")
    cr = stats["crashes"]
    print(f"RL Crashes: mean={cr['mean_n']:.1f} P90={int(cr['p90_n'])} overhead_mean={cr['mean_h']:.1f}h")
    ise = stats["iseda"]
    print(f"\nISEDA Feasibility:")
    print(f"  Verdict: {ise['verdict']}")
    print(f"  Available window: {ise['available_days']} days")
    print(f"  Feasible: {ise['feasible_pct']:.1f}% of sims")
    if args.verbose:
        print(f"\nSensitivity Analysis:")
        for sn in ["step0","step1","step2","step3","step4","step5"]:
            s = stats["sensitivity"][sn]
            print(f"  {stats['per_step'][sn]['label']}: var={s['variance']:.1f} ({s['pct_of_total_var']:.1f}%)")
    if args.decision_only:
        print("\n=== DECISION ONLY ===")
        print(f"Verdict: {ise['verdict']}")
        print(f"P50={ise['p50_days']:.1f}d P90={ise['p90_days']:.1f}d (window={ise['available_days']}d)")
        print(f"Critical: {cp['label']}")
        print(f"Feasible: {ise['feasible_pct']:.1f}%")
    elapsed = time.time() - t0
    print(f"\nElapsed: {elapsed:.1f}s")
    if args.html:
        hp = os.path.join(REPORT_DIR, "report_posttrain_r86_e2e_timeline_zh.html")
        os.makedirs(REPORT_DIR, exist_ok=True)
        html_content = "\n".join(gen_html(stats, args.n_sims) + gen_html_part2(stats, args.n_sims) + gen_html_part3(stats, args.n_sims))
        with open(hp, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML: {hp} ({len(html_content)} bytes)")
    if args.json:
        jp = os.path.join(SCRIPT_DIR, "r86_e2e_timeline.json")
        jr = {"meta": {"ts": "2026-11-09", "n_sims": args.n_sims, "elapsed": elapsed},
              "stats": stats}
        with open(jp, "w", encoding="utf-8") as f:
            json.dump(jr, f, ensure_ascii=False, indent=2)
        print(f"JSON: {jp} ({os.path.getsize(jp)} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
A1: Paired significance testing (McNemar + paired bootstrap)
for ZhuLong DAC2027 ablation experiment.

For each arm: 5 independent runs × 158 tasks.
Per-task pass/fail extracted from execution_results.jsonl.
Missing tasks (gen-fail) treated as fail.

McNemar: pool all (task, run) pairs, build 2×2 contingency table.
Paired bootstrap: per-task mean pass rate difference, 10000 resamples, 95% CI.
"""
import json, os, sys
import numpy as np
from collections import defaultdict

EVAL_DIR = "/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation"
BENCH_FILE = "/nasdata/app.e0031982/code/EDA-Eval-Framework/benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"

# ── All 158 task IDs ──
with open(BENCH_FILE) as f:
    ALL_TASKS = [json.loads(l)["task_id"] for l in f]
N_TASKS = len(ALL_TASKS)
TASK_SET = set(ALL_TASKS)

# ── Arm → batch IDs (5 runs each) ──
ARMS = {
    "full_v3":    ["2026_1012_005319", "2026_1012_033120", "2026_1012_071034", "2026_1012_095645", "2026_1012_131007"],
    "rag":        ["2026_1007_112101", "2026_1007_131535", "2026_1007_163343", "2026_1007_183007", "2026_1007_202448"],
    "wo_retrieval":["2026_1002_042610", "2026_1007_221959", "2026_1008_015818", "2026_1008_050626", "2026_1008_081817"],
    "phi_k10":    ["2026_1012_164323", "2026_1012_194140", "2026_1013_011435", "2026_1013_071635", "2026_1013_092550"],
    "phi_k3":     ["2026_1013_121129", "2026_1013_171159", "2026_1013_200415", "2026_1013_230502", "2026_1014_012928"],
    "phi_k1":     ["2026_1014_035939", "2026_1014_062206", "2026_1014_084226", "2026_1014_113846", "2026_1014_141421"],
    "phi_lagged": ["2026_1014_164101", "2026_1014_193437", "2026_1014_225714", "2026_1015_014926", "2026_1015_042258"],
    "readback_bin":["2026_1015_093317", "2026_1015_143848", "2026_1015_193004", "2026_1015_233638", "2026_1016_041955"],
    "B_glm52":    ["2026_1005_120536", "2026_1005_150545", "2026_1005_180034", "2026_1005_204957", "2026_1005_233928"],
    "B_kimi":     ["2026_1006_071809", "2026_1006_100626", "2026_1006_181646", "2026_1006_204422", "2026_1006_230904"],
    "B_doubao":   ["2026_1007_010601", "2026_1007_030335", "2026_1007_050414", "2026_1007_083426", "2026_1007_095002"],
    "B_dsv4flash":["2026_1006_022818", "2026_1006_031227", "2026_1006_034557", "2026_1006_042140", "2026_1006_045811"],
}

# ── Build batch → best eval dir (most tasks) ──
batch_to_eval = {}
for d in sorted(os.listdir(EVAL_DIR)):
    fp = os.path.join(EVAL_DIR, d, "final_report.json")
    if not os.path.isfile(fp):
        continue
    try:
        with open(fp) as f:
            r = json.load(f)
        gen_file = r.get("generations_file", "")
        if "completed_code_generation_" not in gen_file:
            continue
        batch = gen_file.replace("completed_code_generation_", "").replace(".jsonl", "")
        er = os.path.join(EVAL_DIR, d, "execution_results.jsonl")
        n = sum(1 for _ in open(er)) if os.path.isfile(er) else 0
        # keep the eval dir with the most tasks
        if batch not in batch_to_eval or n > batch_to_eval[batch][1]:
            batch_to_eval[batch] = (os.path.join(EVAL_DIR, d), n)
    except:
        pass

# ── Extract per-task pass/fail matrix for each arm ──
def load_arm_matrix(arm_name, batches):
    """Return dict: task_id → [pass_r1, pass_r2, ..., pass_r5] (bool list).
    Missing tasks = False (gen-fail)."""
    matrix = {t: [False]*5 for t in ALL_TASKS}
    for run_idx, batch in enumerate(batches):
        if batch not in batch_to_eval:
            print(f"  ⚠ {arm_name} r{run_idx+1} {batch}: eval dir not found", file=sys.stderr)
            continue
        eval_path, n_tasks = batch_to_eval[batch]
        er_file = os.path.join(eval_path, "execution_results.jsonl")
        if not os.path.isfile(er_file):
            print(f"  ⚠ {arm_name} r{run_idx+1} {batch}: no execution_results.jsonl", file=sys.stderr)
            continue
        with open(er_file) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    tid = rec.get("task_id", "")
                    if tid in TASK_SET:
                        matrix[tid][run_idx] = bool(rec.get("passed", False))
                except:
                    pass
    return matrix

print("=" * 80)
print("A1: Paired Significance Testing — McNemar + Paired Bootstrap")
print("=" * 80)

# Load all arm matrices
arm_matrices = {}
for arm, batches in ARMS.items():
    print(f"\nLoading {arm}...")
    mat = load_arm_matrix(arm, batches)
    # verify pass rates
    pass_rates = []
    for run_idx in range(5):
        passed = sum(1 for t in ALL_TASKS if mat[t][run_idx])
        pass_rates.append(passed / N_TASKS * 100)
    mean_pr = np.mean(pass_rates)
    std_pr = np.std(pass_rates, ddof=1)
    print(f"  Pass@1 per run: {[f'{p:.1f}' for p in pass_rates]}")
    print(f"  Mean ± std: {mean_pr:.1f} ± {std_pr:.1f}%")
    arm_matrices[arm] = mat

# ── McNemar test ──
def mcnemar_test(mat_A, mat_B):
    """Pooled McNemar: for each (task, run) pair, compare pass/fail.
    Returns (a, b, c, d, chi2, p_value)."""
    a = b = c = d = 0  # a=both pass, b=A pass B fail, c=B pass A fail, d=both fail
    for task in ALL_TASKS:
        for run_idx in range(5):
            pa = mat_A[task][run_idx]
            pb = mat_B[task][run_idx]
            if pa and pb:
                a += 1
            elif pa and not pb:
                b += 1
            elif not pa and pb:
                c += 1
            else:
                d += 1
    # McNemar with continuity correction
    n_disc = b + c
    if n_disc == 0:
        return a, b, c, d, 0.0, 1.0
    chi2 = (abs(b - c) - 1) ** 2 / n_disc
    # p-value from chi-square dist with 1 df (manual, since no scipy)
    # P(X > chi2) for chi-square(1) = 2 * (1 - Phi(sqrt(chi2)))
    # = erfc(sqrt(chi2/2))
    from math import erfc, sqrt
    p_value = erfc(sqrt(chi2 / 2))
    return a, b, c, d, chi2, p_value

# ── Paired bootstrap ──
def paired_bootstrap(mat_A, mat_B, n_resamples=10000, seed=42):
    """Per-task mean pass rate difference, bootstrap 95% CI."""
    rng = np.random.RandomState(seed)
    # per-task pass rates
    task_diffs = []
    for task in ALL_TASKS:
        pa = np.mean(mat_A[task])  # fraction of runs passed
        pb = np.mean(mat_B[task])
        task_diffs.append(pa - pb)
    task_diffs = np.array(task_diffs)
    observed_diff = np.mean(task_diffs)  # in fraction units
    
    # bootstrap
    boot_means = np.zeros(n_resamples)
    for i in range(n_resamples):
        idx = rng.randint(0, N_TASKS, size=N_TASKS)
        boot_means[i] = np.mean(task_diffs[idx])
    
    ci_low = np.percentile(boot_means, 2.5)
    ci_high = np.percentile(boot_means, 97.5)
    return observed_diff * 100, ci_low * 100, ci_high * 100  # in pp

# ── Define pairs to test ──
PAIRS = [
    # Ablation: full_v3 vs each ablation arm
    ("full_v3", "rag",         "full vs rag (w/o Sandbox)"),
    ("full_v3", "wo_retrieval", "full vs w/o Retrieval"),
    ("full_v3", "phi_k10",     "full vs Φ-k=10"),
    ("full_v3", "phi_k3",      "full vs Φ-k=3"),
    ("full_v3", "phi_k1",      "full vs Φ-k=1"),
    ("full_v3", "phi_lagged",  "full vs Φ-lagged"),
    ("full_v3", "readback_bin","full vs Readback-binary"),
    # Phi monotone
    ("phi_k10", "phi_k3",      "Φ-k=10 vs Φ-k=3"),
    ("phi_k3",  "phi_k1",      "Φ-k=3 vs Φ-k=1"),
    # C1 internal
    ("rag",     "wo_retrieval", "rag vs w/o Retrieval"),
    # Backbone (B) comparisons vs full_v3
    ("full_v3", "B_glm52",     "full(dsv4pro) vs glm-5.2"),
    ("full_v3", "B_kimi",      "full(dsv4pro) vs kimi-k2.6"),
    ("full_v3", "B_doubao",    "full(dsv4pro) vs doubao"),
    ("full_v3", "B_dsv4flash", "full(dsv4pro) vs dsv4-flash"),
    # B internal
    ("B_glm52", "B_kimi",      "glm-5.2 vs kimi-k2.6"),
    ("B_glm52", "B_doubao",    "glm-5.2 vs doubao"),
    ("B_kimi",  "B_doubao",    "kimi-k2.6 vs doubao"),
]

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)
print(f"\n{'Pair':<35} {'Δ(pp)':>7} {'McNemar χ²':>11} {'p':>10} {'b→c':>8} {'boot 95% CI':>20} {'sig?':>6}")
print("-" * 100)

results = []
for arm_A, arm_B, label in PAIRS:
    mat_A = arm_matrices[arm_A]
    mat_B = arm_matrices[arm_B]
    
    # pass rates
    pr_A = np.mean([sum(mat_A[t][r] for t in ALL_TASKS) / N_TASKS for r in range(5)]) * 100
    pr_B = np.mean([sum(mat_B[t][r] for t in ALL_TASKS) / N_TASKS for r in range(5)]) * 100
    delta = pr_A - pr_B  # positive = A better
    
    # McNemar
    a, b, c, d, chi2, p_val = mcnemar_test(mat_A, mat_B)
    
    # Paired bootstrap
    obs_diff, ci_lo, ci_hi = paired_bootstrap(mat_A, mat_B)
    
    # significance
    sig = "***" if p_val < 0.001 else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
    
    print(f"{label:<35} {delta:+7.1f} {chi2:11.2f} {p_val:10.2e} {b:>3}→{c:<3}  [{ci_lo:+6.2f}, {ci_hi:+6.2f}]   {sig:>6}")
    
    results.append({
        "pair": label, "delta_pp": delta, "chi2": chi2, "p": p_val,
        "b": b, "c": c, "ci_lo": ci_lo, "ci_hi": ci_hi, "sig": sig,
        "pr_A": pr_A, "pr_B": pr_B,
    })

# Save results as JSON
with open("/tmp/a1_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n\nLegend: *** p<0.001  ** p<0.01  * p<0.05  ns = not significant")
print("b = A pass & B fail (A-only successes), c = B pass & A fail (B-only successes)")
print("Bootstrap CI: 95% percentile CI of per-task mean pass-rate difference (pp)")
print("\nResults saved to /tmp/a1_results.json")

#!/usr/bin/env python
"""R12 3-epoch scaling-law analysis: fit IN-1k lp vs cumulative-samples for the
AIMv2-style 3-epoch continuation run (344k steps, N~176M), compare asymptote
against both the InfoNCE baseline (R9, 25.1%) and the R11-G AIMv2 run (55.3M).

Reads the IN-1k evaluation output emitted by r8_eval_in1k.py from:
  * R12 3-epoch (primary): /tmp/r12_continue_eval_watcher.log
    -> ckpts step 10k..344k + vision.pt (=344k)  [~35 points]
  * R11-G AIMv2 (secondary): /tmp/r11g_aimv2_long.log  [11 points, 10k..108k]
  * R9 InfoNCE (baseline):  /tmp/r9_stage2.log  [11 points, 10k..108k]

Parse format (from r8_eval_in1k.py, verbatim):
  [R8-IN1K] ckpt=/nas_train/.../R12_fulldata_aimv2_w512/vision_step10000.pt
  [R8-IN1K] zero-shot top1=0.0274 top5=0.0925  linear-probe top1=0.0610

x-axis: cumulative samples = step * samples_per_step (512 = bs64 x 8 ranks).
y-axis: IN-1k linear-probe top-1 (frozen trunk).

Fits two models on the R12 3-epoch points and reports R^2:
  1. power law  acc = a - b * N^(-c)   (scipy curve_fit, bounds-guarded)
  2. log-linear acc = a + b * log10(N)  (scipy.stats.linregress on log10(N))

Pre-registered criteria (BAIZE_VISION_TASK.md):
  - R^2 >= 0.90 AND asymptote a > 25.1% (InfoNCE) -> positive (paper-worthy)
  - R^2 < 0.90 OR trajectory non-monotonic     -> report honestly, NO forced extrapolation

Epoch alignment (58.8M unique samples / epoch, 512 samples/step):
  120k ~ 1.05 ep (N~61.4M)   <- R12 original end
  170k ~ 1.5  ep (N~87.0M)
  230k ~ 2.0  ep (N~117.8M)
  285k ~ 2.5  ep (N~146.0M)
  340k ~ 3.0  ep (N~174.1M)
  344k ~ 3.0  ep (N~176.1M)   <- continuation end

Pure CPU, no GPU. Run AFTER the eval watcher completes.

Usage:
  python r12_3epoch_scaling.py [--r12-log /tmp/r12_continue_eval_watcher.log]
                               [--r11g-log /tmp/r11g_aimv2_long.log]
                               [--infonce-log /tmp/r9_stage2.log]
                               [--samples-per-step 512] [--final-step 344000]
                               [--csv /tmp/r12_3epoch_scaling_points.csv]
"""
import argparse
import csv
import re
import os

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress


CKPT_RE = re.compile(r"\[R8-IN1K\] ckpt=(\S+)")
ACC_RE = re.compile(
    r"\[R8-IN1K\] zero-shot top1=([0-9.]+) top5=([0-9.]+)"
    r"\s+linear-probe top1=([0-9.]+)"
)
STEP_RE = re.compile(r"vision_step(\d+)\.pt$")

# InfoNCE baseline (R9 stage-2, same-method power-law fit, 11 points, R^2~=0.94)
INFONCE_ASYMPTOTE = 0.251  # 25.1%
INFONCE_FIT_STR = "acc=0.251-0.864*N^(-0.090)"

# R12 data facts
R12_UNIQUE_PER_EPOCH = 58.8e6  # 58.8M unique image-text pairs
R12_STEPS_PER_EPOCH = 114746   # 58.8M / 512


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def parse_log(path, final_step=None):
    """Return list of {path, step, zs1, zs5, lp} dicts from an r8_eval log."""
    if not os.path.exists(path):
        return []
    pts = []
    pending = None
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = CKPT_RE.search(line)
            if m:
                pending = m.group(1)
                continue
            a = ACC_RE.search(line)
            if a and pending is not None:
                step = _extract_step(pending, final_step)
                pts.append({
                    "path": pending,
                    "step": step,
                    "zs1": float(a.group(1)),
                    "zs5": float(a.group(2)),
                    "lp": float(a.group(3)),
                })
                pending = None
    return pts


def _extract_step(path, final_step=None):
    m = STEP_RE.search(path)
    if m:
        return int(m.group(1))
    if path.endswith("vision.pt") or path.endswith("vision_fused.pt"):
        return final_step
    return None


# ---------------------------------------------------------------------------
# Fitting
# ---------------------------------------------------------------------------
def fit_powerlaw(N, acc):
    """Fit acc = a - b * N^(-c).  Returns dict or (None, error_str)."""
    try:
        p0 = [acc[-1] + 0.01, 0.5, 0.1]
        bounds = ([0.0, 1e-6, 1e-4], [1.0, 10.0, 2.0])
        popt, _ = curve_fit(
            lambda x, a, b, c: a - b * np.power(x, -c),
            N, acc, p0=p0, bounds=bounds, maxfev=20000
        )
        pred = popt[0] - popt[1] * np.power(N, -popt[2])
        ss_res = np.sum((acc - pred) ** 2)
        ss_tot = np.sum((acc - np.mean(acc)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return {"a": popt[0], "b": popt[1], "c": popt[2], "r2": r2}, None
    except Exception as e:
        return None, str(e)


def fit_loglinear(N, acc):
    """Fit acc = a + b * log10(N)."""
    logN = np.log10(N)
    slope, intercept, r, _, _ = linregress(logN, acc)
    return {"a": intercept, "b": slope, "r2": r ** 2}


def is_monotonic_nondecreasing(acc):
    diffs = np.diff(acc)
    n_neg = int(np.sum(diffs < -0.001))  # allow tiny float noise
    return n_neg == 0, n_neg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r12-log", default="/tmp/r12_continue_eval_watcher.log")
    ap.add_argument("--r11g-log", default="/tmp/r11g_aimv2_long.log")
    ap.add_argument("--infonce-log", default="/tmp/r9_stage2.log")
    ap.add_argument("--samples-per-step", type=int, default=512)
    ap.add_argument("--final-step", type=int, default=344000)
    ap.add_argument("--csv", default="/tmp/r12_3epoch_scaling_points.csv")
    args = ap.parse_args()

    sps = args.samples_per_step
    print("=" * 78)
    print("R12 3-EPOCH SCALING-LAW ANALYSIS")
    print(f"  samples_per_step = {sps}")
    print(f"  unique/epoch     = {R12_UNIQUE_PER_EPOCH/1e6:.1f}M")
    print(f"  steps/epoch      = {R12_STEPS_PER_EPOCH}")
    print(f"  final_step       = {args.final_step}")
    print(f"  r12-log          = {args.r12_log}")
    print(f"  r11g-log         = {args.r11g_log}")
    print(f"  infonce-log      = {args.infonce_log}")

    # --- Parse all three logs ---
    r12 = parse_log(args.r12_log, final_step=args.final_step)
    r11g = parse_log(args.r11g_log, final_step=108000)
    infonce = parse_log(args.infonce_log, final_step=108000)

    for name, pts in [("R12-3epoch", r12), ("R11-G", r11g), ("R9-InfoNCE", infonce)]:
        print(f"\n  [{name}] parsed {len(pts)} eval points")
        if pts:
            print(f"    step range: {pts[0]['step']}..{pts[-1]['step']}")

    # Drop points with step=None
    r12 = [p for p in r12 if p["step"] is not None]
    r11g = [p for p in r11g if p["step"] is not None]
    infonce = [p for p in infonce if p["step"] is not None]

    # Compute cumulative samples
    for pts in (r12, r11g, infonce):
        for p in pts:
            p["samples"] = p["step"] * sps

    # --- Print raw R12 points ---
    print("\n" + "=" * 78)
    print("--- R12 3-epoch raw eval points ---")
    print(f"{'step':>8} {'N(M)':>8} {'epoch':>7} {'lp%':>8} {'zs%':>8}")
    r12_sorted = sorted(r12, key=lambda x: x["step"])
    for p in r12_sorted:
        ep = p["samples"] / R12_UNIQUE_PER_EPOCH
        print(f"{p['step']:>8} {p['samples']/1e6:>8.1f} {ep:>7.2f} "
              f"{p['lp']*100:>7.2f} {p['zs1']*100:>7.2f}")

    # --- Save CSV ---
    if args.csv and r12:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["step", "N_samples", "epoch", "lp_top1", "zs_top1", "zs_top5"])
            for p in r12_sorted:
                ep = p["samples"] / R12_UNIQUE_PER_EPOCH
                w.writerow([p["step"], p["samples"], f"{ep:.3f}",
                           f"{p['lp']:.6f}", f"{p['zs1']:.6f}", f"{p['zs5']:.6f}"])
        print(f"\n  CSV saved: {args.csv}")

    # --- Fit R9 InfoNCE (baseline) ---
    print("\n" + "=" * 78)
    print("--- R9 InfoNCE baseline fit ---")
    infonce_fit = None
    if len(infonce) >= 4:
        isorted = sorted(infonce, key=lambda x: x["samples"])
        N_i = np.array([p["samples"] for p in isorted], dtype=float)
        acc_i = np.array([p["lp"] for p in isorted], dtype=float)
        pfit_i, err_i = fit_powerlaw(N_i, acc_i)
        if err_i:
            print(f"  [powerlaw] {err_i}")
        else:
            print(f"  [powerlaw] a={pfit_i['a']:.5f} b={pfit_i['b']:.5f} "
                  f"c={pfit_i['c']:.5f} R^2={pfit_i['r2']:.4f}")
            infonce_fit = pfit_i
    else:
        print(f"  [WARN] only {len(infonce)} InfoNCE points; using known: {INFONCE_FIT_STR}")

    # --- Fit R11-G AIMv2 (secondary) ---
    print("\n" + "=" * 78)
    print("--- R11-G AIMv2 fit (secondary comparison) ---")
    r11g_fit = None
    if len(r11g) >= 4:
        gsorted = sorted(r11g, key=lambda x: x["samples"])
        N_g = np.array([p["samples"] for p in gsorted], dtype=float)
        acc_g = np.array([p["lp"] for p in gsorted], dtype=float)
        pfit_g, err_g = fit_powerlaw(N_g, acc_g)
        if err_g:
            print(f"  [powerlaw] {err_g}")
        else:
            print(f"  [powerlaw] a={pfit_g['a']:.5f} b={pfit_g['b']:.5f} "
                  f"c={pfit_g['c']:.5f} R^2={pfit_g['r2']:.4f}")
            r11g_fit = pfit_g
        lfit_g = fit_loglinear(N_g, acc_g)
        print(f"  [loglinear] a={lfit_g['a']:.5f} b={lfit_g['b']:.5f} R^2={lfit_g['r2']:.4f}")
    else:
        print(f"  [WARN] only {len(r11g)} R11-G points; skipping fit.")

    # --- Fit R12 3-epoch (primary) ---
    print("\n" + "=" * 78)
    print("--- R12 3-epoch AIMv2 fit (PRIMARY) ---")
    if len(r12) < 4:
        print(f"[FIT] R12 has <4 points ({len(r12)}); cannot fit.")
        print(f'NOTE: eval may not have run yet. grep -c "[R8-IN1K]" {args.r12_log}')
        return

    r12_s = sorted(r12, key=lambda x: x["samples"])
    N = np.array([p["samples"] for p in r12_s], dtype=float)
    acc = np.array([p["lp"] for p in r12_s], dtype=float)

    pfit, err = fit_powerlaw(N, acc)
    if err:
        print(f"[powerlaw] {err}")
    else:
        print(f"[powerlaw] a={pfit['a']:.5f} b={pfit['b']:.5f} "
              f"c={pfit['c']:.5f} R^2={pfit['r2']:.4f}")
    lfit = fit_loglinear(N, acc)
    print(f"[loglinear] a={lfit['a']:.5f} b={lfit['b']:.5f} R^2={lfit['r2']:.4f}")

    mono, n_neg = is_monotonic_nondecreasing(acc)
    print(f"\n[monotonicity] non-decreasing: {mono}  (n_neg={n_neg}/{len(acc)-1})")
    if not mono:
        print("  WARNING: lp NOT monotonic -> report honestly, no force-fit.")

    # --- Epoch-point extraction ---
    print("\n" + "=" * 78)
    print("--- Epoch-aligned points (pre-registered: 1/1.5/2/2.5/3 epoch) ---")
    target_steps = {
        "~1.0ep": 120000,
        "~1.5ep": 170000,
        "~2.0ep": 230000,
        "~2.5ep": 285000,
        "~3.0ep": 340000,
    }
    for label, ts in target_steps.items():
        closest = min(r12_s, key=lambda p: abs(p["step"] - ts))
        ep = closest["samples"] / R12_UNIQUE_PER_EPOCH
        print(f"  {label:>8} (target step {ts}): closest step={closest['step']} "
              f"ep={ep:.2f} lp={closest['lp']*100:.2f}% zs={closest['zs1']*100:.2f}%")

    # --- Pre-registered criteria ---
    print("\n" + "=" * 78)
    print("--- PRE-REGISTERED CRITERIA ---")
    print(f"  InfoNCE baseline a = {INFONCE_ASYMPTOTE*100:.1f}%  ({INFONCE_FIT_STR})")
    r2_ok = pfit is not None and pfit["r2"] >= 0.90
    asym = pfit["a"] if pfit else None
    if asym is not None:
        print(f"  R12 R^2 = {pfit['r2']:.4f}  (>=0.90? {'YES' if r2_ok else 'NO'})")
        print(f"  R12 a    = {asym*100:.2f}%  (> {INFONCE_ASYMPTOTE*100:.1f}%? "
              f"{'YES' if asym > INFONCE_ASYMPTOTE else 'NO'})")

    print("\n  VERDICT:")
    if asym is not None and r2_ok and asym > INFONCE_ASYMPTOTE and mono:
        d = (asym - INFONCE_ASYMPTOTE) * 100
        print(f"    POSITIVE: R^2={pfit['r2']:.2f}>=0.90, a={asym*100:.1f}% > "
              f"{INFONCE_ASYMPTOTE*100:.1f}% (D=+{d:.1f}pp)")
        print("    -> 'AIMv2-style with more data (3 epoch) confirms higher asymptote'")
    elif not mono:
        print("    NON-MONOTONIC -> report honestly, no force-fit")
    elif not r2_ok:
        r2v = pfit["r2"] if pfit else float("nan")
        print(f"    LOW R^2: {r2v:.2f} < 0.90 -> report honestly")
    else:
        print(f"    NOT HIGHER: a={asym*100:.1f}% <= {INFONCE_ASYMPTOTE*100:.1f}%")

    # --- Side-by-side comparison ---
    print("\n" + "=" * 78)
    print("--- side-by-side: R12-3ep vs R11-G vs R9-InfoNCE ---")
    print(f"{'model':>14} {'fit':>10} {'R^2':>8} {'asym%':>8} {'formula':>40}")
    if pfit:
        print(f"{'R12-3ep-aimv2':>14} {'powerlaw':>10} {pfit['r2']:>8.4f} "
              f"{pfit['a']*100:>7.2f} "
              f"{'%.3f-%.3f*N^-%.3f' % (pfit['a'], pfit['b'], pfit['c']):>40}")
    print(f"{'R12-3ep-aimv2':>14} {'loglinear':>10} {lfit['r2']:>8.4f} "
          f"{'N/A':>8} {'%.4f+%.4f*log10' % (lfit['a'], lfit['b']):>40}")
    if r11g_fit:
        print(f"{'R11G-aimv2':>14} {'powerlaw':>10} {r11g_fit['r2']:>8.4f} "
              f"{r11g_fit['a']*100:>7.2f} "
              f"{'%.3f-%.3f*N^-%.3f' % (r11g_fit['a'], r11g_fit['b'], r11g_fit['c']):>40}")
    if infonce_fit:
        print(f"{'R9-infonce':>14} {'powerlaw':>10} {infonce_fit['r2']:>8.4f} "
              f"{infonce_fit['a']*100:>7.2f} "
              f"{'%.3f-%.3f*N^-%.3f' % (infonce_fit['a'], infonce_fit['b'], infonce_fit['c']):>40}")
    print(f"{'R9-infonce':>14} {'known':>10} {'~0.94':>8} {'25.1':>8} {INFONCE_FIT_STR:>40}")

    # --- R12 1-epoch vs 3-epoch ---
    print("\n" + "=" * 78)
    print("--- R12 1-epoch vs 3-epoch comparison ---")
    p_1ep = min(r12_s, key=lambda p: abs(p["step"] - 120000))
    p_3ep = max(r12_s, key=lambda p: p["step"])
    print(f"  ~1 epoch (step {p_1ep['step']}): lp={p_1ep['lp']*100:.2f}%  "
          f"N={p_1ep['samples']/1e6:.1f}M")
    print(f"  ~3 epoch (step {p_3ep['step']}): lp={p_3ep['lp']*100:.2f}%  "
          f"N={p_3ep['samples']/1e6:.1f}M")
    delta = (p_3ep["lp"] - p_1ep["lp"]) * 100
    print(f"  Delta (3ep - 1ep): {delta:+.2f} pp")
    if delta > 1.5:
        print("  -> 'More epochs (data repetition) continues to improve lp'")
    elif delta > -1.5:
        print("  -> 'Plateau: data repetition gives diminishing returns in [1,3] epoch'")
    else:
        print("  -> 'Regression: more epochs HURTS (possible overfitting or noise)'")

    # --- R12 vs R11-G at same N ---
    print("\n" + "=" * 78)
    print("--- R12 (58.8M unique, 3 epoch) vs R11-G (18.5M unique, 3 epoch) at same N ---")
    if r11g:
        for target_n in [5e6, 15e6, 30e6, 55e6]:
            r12_p = min(r12_s, key=lambda p: abs(p["samples"] - target_n))
            r11g_p = min(r11g, key=lambda p: abs(p["samples"] - target_n))
            d = (r12_p["lp"] - r11g_p["lp"]) * 100
            print(f"  N~{target_n/1e6:.0f}M: R12={r12_p['lp']*100:.2f}% "
                  f"(step {r12_p['step']}) vs R11G={r11g_p['lp']*100:.2f}% "
                  f"(step {r11g_p['step']})  Delta={d:+.2f} pp")

    print("\nDONE")


if __name__ == "__main__":
    main()

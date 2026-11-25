#!/usr/bin/env python
"""R12b scaling-law analysis: fit IN-1k lp vs cumulative-samples for the
AIMv2-style full-data fresh run (272k steps, N~139M at 2 epochs), compare
against R11-G AIMv2 (55.3M) and R9 InfoNCE (25.1% asymptote).

Reads IN-1k eval output from r8_eval_in1k.py. Pure CPU. Run AFTER eval.

Usage:
  python r12b_scaling.py [--r12b-log /tmp/r12b_eval_watcher.results]
"""
import argparse, re, sys
from pathlib import Path
import numpy as np
try:
    from scipy.optimize import curve_fit
    from scipy.stats import linregress
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

SAMPLES_PER_STEP = 512  # bs64 x 8 ranks


def parse_eval_log(path):
    """Parse r8_eval_in1k.py output: extract (step, lp_top1) pairs."""
    if not Path(path).exists():
        print(f"[WARN] log not found: {path}")
        return []
    text = Path(path).read_text()
    results = []
    ckpt_re = re.compile(r'\[R8-IN1K\] ckpt=.*vision_step(\d+)\.pt')
    lp_re = re.compile(r'\[R8-IN1K\].*linear-probe top1=([\d.]+)')
    lines = text.split('\n')
    current_step = None
    for line in lines:
        m = ckpt_re.search(line)
        if m:
            current_step = int(m.group(1))
            continue
        m3 = lp_re.search(line)
        if m3 and current_step is not None:
            results.append((current_step, float(m3.group(1))))
            current_step = None
    seen = {}
    for step, lp in results:
        seen[step] = lp
    return sorted(seen.items())


def power_law(N, a, b, c):
    return a - b * np.power(N, -c)


def fit_and_report(name, points, baseline_asymptote=0.251):
    """Fit power law + log-linear, print results."""
    if len(points) < 3:
        print(f"\n[{name}] Too few points ({len(points)}), skipping fit.")
        return None
    steps = np.array([p[0] for p in points], dtype=float)
    lps = np.array([p[1] for p in points], dtype=float)
    N = steps * SAMPLES_PER_STEP
    print(f"\n{'='*70}")
    print(f"[{name}] {len(points)} points")
    print(f"  step range: {int(steps.min())} – {int(steps.max())}")
    print(f"  N range:    {N.min():.2e} – {N.max():.2e}")
    print(f"  lp range:   {lps.min()*100:.2f}% – {lps.max()*100:.2f}%")
    for s, lp in points:
        print(f"    step={int(s):>7d}  N={s*SAMPLES_PER_STEP:.3e}  lp={lp*100:.2f}%")
    log_N = np.log10(N)
    slope, intercept, r_value, _, _ = linregress(log_N, lps)
    r2_log = r_value ** 2
    print(f"\n  Log-linear: acc = {intercept:.4f} + {slope:.4f} * log10(N)  R²={r2_log:.4f}")
    a_power = None
    r2_power = None
    if HAS_SCIPY:
        try:
            p0 = [max(lps[-5:].mean(), 0.01), 0.5, 0.1]
            popt, _ = curve_fit(power_law, N, lps, p0=p0,
                                bounds=([0, 0, 0.001], [1.0, 10, 1]), maxfev=20000)
            a_fit, b_fit, c_fit = popt
            pred = power_law(N, *popt)
            ss_res = np.sum((lps - pred) ** 2)
            ss_tot = np.sum((lps - lps.mean()) ** 2)
            r2_power = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            print(f"  Power law:  acc = {a_fit:.4f} - {b_fit:.4f} * N^(-{c_fit:.4f})  R²={r2_power:.4f}")
            a_power = a_fit
        except Exception as e:
            print(f"  Power law fit failed: {e}")
    monotonic = all(lps[i] <= lps[i+1] + 0.005 for i in range(len(lps)-1))
    print(f"\n  Monotonic (±0.5pp): {monotonic}")
    best_r2 = max(r2_log, r2_power or 0)
    if a_power is not None:
        print(f"  Asymptote (power law a): {a_power*100:.1f}%  vs InfoNCE 25.1%  → {'ABOVE' if a_power > 0.251 else 'BELOW'}")
    print(f"  Best R²: {best_r2:.4f}")
    if best_r2 >= 0.90 and a_power is not None and a_power > baseline_asymptote:
        print(f"  VERDICT: ✅ POSITIVE — asymptote {a_power*100:.1f}% > {baseline_asymptote*100:.1f}%, R²={best_r2:.2f}")
    elif best_r2 >= 0.90:
        print(f"  VERDICT: ⚠️ R² OK but asymptote not above InfoNCE baseline")
    else:
        print(f"  VERDICT: ⚠️ R² < 0.90 — report honestly, no forced extrapolation")
    return {'r2': best_r2, 'asymptote': a_power, 'n_points': len(points),
            'lp_max': lps.max(), 'lp_final': lps[-1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--r12b-log', default=None)
    ap.add_argument('--r11g-log', default='/tmp/r11g_aimv2_long.log')
    ap.add_argument('--infonce-log', default='/tmp/r9_stage2.log')
    ap.add_argument('--r12-3ep-log', default='/tmp/r12_continue_eval_watcher.log')
    args = ap.parse_args()
    r12b_log = args.r12b_log
    if r12b_log is None:
        for c in ['/tmp/r12b_eval_watcher.results', '/tmp/r12b_fulldata_aimv2.log']:
            if Path(c).exists():
                r12b_log = c
                break
    if r12b_log is None:
        print("ERROR: No R12b eval log found. Specify --r12b-log."); sys.exit(1)
    print(f"R12b log: {r12b_log}")
    r12b_pts = parse_eval_log(r12b_log)
    r11g_pts = parse_eval_log(args.r11g_log)
    infonce_pts = parse_eval_log(args.infonce_log)
    r12_3ep_pts = parse_eval_log(args.r12_3ep_log)
    r12b_result = fit_and_report("R12b full-data AIMv2 (fresh, 2 epoch)", r12b_pts)
    if r12_3ep_pts:
        fit_and_report("R12 3-epoch AIMv2 (3 epoch repeat)", r12_3ep_pts)
    if r11g_pts:
        fit_and_report("R11-G AIMv2 (55.3M, 1 epoch)", r11g_pts)
    if infonce_pts:
        fit_and_report("R9 InfoNCE baseline (55.3M)", infonce_pts)
    print(f"\n{'='*70}")
    print("SUMMARY: InfoNCE baseline asymptote = 25.1%")
    if r12b_result:
        a_str = f"{r12b_result['asymptote']*100:.1f}%" if r12b_result['asymptote'] else "N/A"
        print(f"R12b: {r12b_result['n_points']} pts, lp_max={r12b_result['lp_max']*100:.2f}%, "
              f"R²={r12b_result['r2']:.4f}, asymptote={a_str}")
    print("Key: Does full-data 69.7M×2ep(139M) beat 3-epoch 58.8M×3ep(176M)? Compare lp at similar N.")


if __name__ == '__main__':
    main()


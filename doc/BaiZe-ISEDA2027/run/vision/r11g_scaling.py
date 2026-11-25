#!/usr/bin/env python
"""R11-G scaling-law analysis: fit IN-1k lp vs cumulative-samples for the
AIMv2-style long run (108k steps), compare asymptote against InfoNCE baseline.

Reads the IN-1k evaluation output emitted by r8_eval_in1k.py from:
  * R11-G (AIMv2 108k): /tmp/r11g_aimv2_long.log  -> 11 ckpts (step 10k..108k)
  * R9 stage-2 (InfoNCE 108k, baseline): /tmp/r9_stage2.log  -> 11 ckpts

Parse format (from r8_eval_in1k.py, verbatim):
  [R8-IN1K] ckpt=/nas_train/.../R11G_aimv2_long_w512/vision_step10000.pt
  [R8-IN1K] zero-shot top1=0.0274 top5=0.0925  linear-probe top1=0.0610

x-axis: cumulative samples = step * samples_per_step (512 = bs64 x 8 ranks).
y-axis: IN-1k linear-probe top-1 (frozen trunk).

Fits two models on the R11-G points and reports R^2:
  1. power law  acc = a - b * N^(-c)   (scipy curve_fit, bounds-guarded)
  2. log-linear acc = a + b * log10(N)  (scipy.stats.linregress on log10(N))

Pre-registered criteria (BAIZE_VISION_TASK.md §运维指令 2026-10-04(七)):
  - R^2 >= 0.90 AND asymptote a > 25.1% (InfoNCE) -> positive (paper-worthy)
  - R^2 < 0.90 OR trajectory non-monotonic     -> report honestly, NO forced extrapolation

Baseline reference (same-method fit on InfoNCE R9 stage-2):
  acc = 0.251 - 0.864 * N^(-0.090), R^2 ~= 0.94, asymptote a = 25.1%

Pure CPU, no GPU. Run AFTER the chain's auto-eval completes.

Usage:
  python r11g_scaling.py [--r11g-log /tmp/r11g_aimv2_long.log]
                         [--infonce-log /tmp/r9_stage2.log]
                         [--samples-per-step 512] [--csv /tmp/r11g_scaling_points.csv]
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
STEPS_RE = re.compile(r"steps=(\d+)")

# InfoNCE baseline (R9 stage-2, same-method power-law fit, 11 points, R^2~=0.94)
INFONCE_ASYMPTOTE = 0.251  # 25.1%
INFONCE_FIT_STR = "acc=0.251-0.864*N^(-0.090)"


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


def _final_step_from_log(path, default):
    if not os.path.exists(path):
        return default
    with open(path, errors="replace") as fh:
        for line in fh:
            m = STEPS_RE.search(line)
            if m:
                return int(m.group(1))
    return default


# ---------------------------------------------------------------------------
# Fits (identical methodology to r9_scaling.py for fair comparison)
# ---------------------------------------------------------------------------
def _powerlaw(N, a, b, c):
    return a - b * np.power(N.astype(float), -c)


def fit_powerlaw(N, acc):
    N = N.astype(float)
    a0 = max(acc) * 1.05 + 1e-3
    p0 = [a0, max((a0 - min(acc)), 0.1) * 0.5, 0.3]
    bounds = ([max(acc) * 0.99, 0.0, 1e-3], [1.0, 1e3, 5.0])
    try:
        popt, _ = curve_fit(_powerlaw, N, acc, p0=p0, bounds=bounds, maxfev=20000)
    except Exception as e:  # noqa: BLE001
        return None, f"fit failed: {e}"
    pred = _powerlaw(N, *popt)
    ss_res = float(np.sum((acc - pred) ** 2))
    ss_tot = float(np.sum((acc - np.mean(acc)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"a": popt[0], "b": popt[1], "c": popt[2], "r2": r2}, None


def fit_loglinear(N, acc):
    lg = np.log10(N.astype(float))
    res = linregress(lg, acc)
    pred = res.intercept + res.slope * lg
    ss_res = float(np.sum((acc - pred) ** 2))
    ss_tot = float(np.sum((acc - np.mean(acc)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"a": res.intercept, "b": res.slope, "r2": r2}


def is_monotonic_nondecreasing(acc):
    diffs = np.diff(acc)
    n_neg = int(np.sum(diffs < 0))
    return n_neg <= 1, n_neg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--r11g-log', default='/tmp/r11g_aimv2_long.log')
    ap.add_argument('--infonce-log', default='/tmp/r9_stage2.log')
    ap.add_argument('--samples-per-step', type=int, default=512)
    ap.add_argument('--csv', default='/tmp/r11g_scaling_points.csv')
    args = ap.parse_args()

    spp = args.samples_per_step
    r11g_final = _final_step_from_log(args.r11g_log, 108000)
    infonce_final = _final_step_from_log(args.infonce_log, 108000)

    r11g_raw = parse_log(args.r11g_log, r11g_final)
    infonce_raw = parse_log(args.infonce_log, infonce_final)

    def with_samples(pts, tag):
        out = []
        for p in pts:
            if p['step'] is None:
                print(f"[SKIP][{tag}] cannot parse step: {p['path']}")
                continue
            p = dict(p)
            p['samples'] = p['step'] * spp
            p['tag'] = tag
            out.append(p)
        return out

    r11g = with_samples(r11g_raw, 'R11G-aimv2')
    infonce = with_samples(infonce_raw, 'R9-infonce')

    print('=' * 78)
    print('R11-G scaling-law analysis (AIMv2-style vs InfoNCE baseline)')
    print(f'  samples/step = {spp} (bs64 x 8 ranks)')
    print(f'  R11-G points: {len(r11g)}  InfoNCE points: {len(infonce)}')
    print('=' * 78)

    print('\n--- parsed points ---')
    print(f"{'tag':>12} {'step':>8} {'N(M)':>8} {'zs1%':>7} {'zs5%':>7} {'lp%':>7}  ckpt")
    all_pts = sorted(r11g + infonce, key=lambda x: (x['tag'], x['step']))
    for p in all_pts:
        print(f"{p['tag']:>12} {p['step']:>8} {p['samples']/1e6:>8.2f} "
              f"{p['zs1']*100:>7.2f} {p['zs5']*100:>7.2f} {p['lp']*100:>7.2f}  "
              f"{os.path.basename(p['path'])}")

    with open(args.csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['tag', 'step', 'samples',
                                           'zs1', 'zs5', 'lp', 'path'])
        w.writeheader()
        for p in all_pts:
            w.writerow({k: p[k] for k in w.fieldnames})
    print(f'\n[saved] points -> {args.csv}')

    # --- Fit InfoNCE baseline ---
    print('\n' + '=' * 78)
    print('--- InfoNCE baseline (R9 stage-2, re-fit from raw points) ---')
    infonce_fit = None
    if len(infonce) >= 2:
        isorted = sorted(infonce, key=lambda x: x['samples'])
        N_i = np.array([p['samples'] for p in isorted], dtype=float)
        acc_i = np.array([p['lp'] for p in isorted], dtype=float)
        pfit_i, err_i = fit_powerlaw(N_i, acc_i)
        if err_i:
            print(f'[powerlaw] {err_i}')
        else:
            print(f"[powerlaw] a={pfit_i['a']:.5f} b={pfit_i['b']:.5f} "
                  f"c={pfit_i['c']:.5f} R^2={pfit_i['r2']:.4f}")
            infonce_fit = pfit_i
        lfit_i = fit_loglinear(N_i, acc_i)
        print(f"[loglinear] a={lfit_i['a']:.5f} b={lfit_i['b']:.5f} R^2={lfit_i['r2']:.4f}")
    else:
        print(f'  [WARN] only {len(infonce)} InfoNCE points; using known: {INFONCE_FIT_STR}')

    # --- Fit R11-G ---
    print('\n' + '=' * 78)
    print('--- R11-G AIMv2-style fit (primary) ---')
    if len(r11g) < 2:
        print(f'[FIT] R11-G has <2 points ({len(r11g)}); cannot fit.')
        print(f'NOTE: eval may not have run yet. grep -c "[R8-IN1K]" {args.r11g_log}')
        return

    gsorted = sorted(r11g, key=lambda x: x['samples'])
    N = np.array([p['samples'] for p in gsorted], dtype=float)
    acc = np.array([p['lp'] for p in gsorted], dtype=float)

    pfit, err = fit_powerlaw(N, acc)
    if err:
        print(f'[powerlaw] {err}')
    else:
        print(f"[powerlaw] a={pfit['a']:.5f} b={pfit['b']:.5f} "
              f"c={pfit['c']:.5f} R^2={pfit['r2']:.4f}")
    lfit = fit_loglinear(N, acc)
    print(f"[loglinear] a={lfit['a']:.5f} b={lfit['b']:.5f} R^2={lfit['r2']:.4f}")

    mono, n_neg = is_monotonic_nondecreasing(acc)
    print(f'\n[monotonicity] non-decreasing: {mono}  (n_neg={n_neg}/{len(acc)-1})')
    if not mono:
        print('  WARNING: lp NOT monotonic -> "非简单幂律，需更多点/更长跑"，no force-fit.')

    # --- Pre-registered criteria ---
    print('\n' + '=' * 78)
    print('--- PRE-REGISTERED CRITERIA ---')
    print(f'  InfoNCE baseline a = {INFONCE_ASYMPTOTE*100:.1f}%  ({INFONCE_FIT_STR})')
    r2_ok = pfit is not None and pfit['r2'] >= 0.90
    asym = pfit['a'] if pfit else None
    if asym is not None:
        print(f'  R11-G R^2 = {pfit["r2"]:.4f}  (>=0.90? {"YES" if r2_ok else "NO"})')
        print(f'  R11-G a    = {asym*100:.2f}%  (> {INFONCE_ASYMPTOTE*100:.1f}%? '
              f'{"YES" if asym > INFONCE_ASYMPTOTE else "NO"})')

    print('\n  VERDICT:')
    if asym is not None and r2_ok and asym > INFONCE_ASYMPTOTE and mono:
        d = (asym - INFONCE_ASYMPTOTE) * 100
        print(f'    POSITIVE: R^2={pfit["r2"]:.2f}>=0.90, a={asym*100:.1f}% > '
              f'{INFONCE_ASYMPTOTE*100:.1f}% (D=+{d:.1f}pp)')
        print('    -> "换目标函数(AIMv2-style)可抬高渐近上限" (paper-worthy)')
    elif not mono:
        print('    NON-MONOTONIC -> "非简单幂律，需更多点/更长跑" (report honestly)')
    elif not r2_ok:
        r2v = pfit['r2'] if pfit else float('nan')
        print(f'    LOW R^2: {r2v:.2f} < 0.90 -> "非简单幂律，需更多点/更长跑"')
    else:
        print(f'    NOT HIGHER: a={asym*100:.1f}% <= {INFONCE_ASYMPTOTE*100:.1f}% '
              '-> "换目标函数未抬高渐近上限" (negative, also valuable)')

    print('\n' + '=' * 78)
    print('--- side-by-side: AIMv2 vs InfoNCE ---')
    print(f"{'model':>12} {'fit':>10} {'R^2':>8} {'asym%':>8} {'formula':>40}")
    if pfit:
        print(f"{'R11G-aimv2':>12} {'powerlaw':>10} {pfit['r2']:>8.4f} "
              f"{pfit['a']*100:>7.2f} "
              f"{'%.3f-%.3f*N^-%.3f' % (pfit['a'], pfit['b'], pfit['c']):>40}")
    print(f"{'R11G-aimv2':>12} {'loglinear':>10} {lfit['r2']:>8.4f} "
          f"{'N/A':>8} {'%.4f+%.4f*log10' % (lfit['a'], lfit['b']):>40}")
    if infonce_fit:
        print(f"{'R9-infonce':>12} {'powerlaw':>10} {infonce_fit['r2']:>8.4f} "
              f"{infonce_fit['a']*100:>7.2f} "
              f"{'%.3f-%.3f*N^-%.3f' % (infonce_fit['a'], infonce_fit['b'], infonce_fit['c']):>40}")
    print(f"{'R9-infonce':>12} {'known':>10} {'~0.94':>8} {'25.1':>8} {INFONCE_FIT_STR:>40}")
    print('\nDONE')


if __name__ == '__main__':
    main()

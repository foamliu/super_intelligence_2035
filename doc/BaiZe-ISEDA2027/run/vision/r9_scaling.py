#!/usr/bin/env python
"""R9 scaling-law analysis: fit IN-1k vs cumulative-samples, extrapolate.

Reads the IN-1k evaluation output emitted by r8_eval_in1k.py from the two R9 runs:
  * stage-2 : /tmp/r9_stage2.log   -> 11 ckpts (w512, steps 10k..108k)  [PRIMARY]
  * stage-1 : /tmp/r9.log          ->  3 ckpts (w512/w768/w1024 @ 30k)  [width sweep]

Parse format (from r8_eval_in1k.py, verbatim):
  [R8-IN1K] ckpt=/nas_train/.../R9_stage2_w512/vision_step10000.pt
  [R8-IN1K] zero-shot top1=0.0274 top5=0.0925  linear-probe top1=0.0610

x-axis (primary): cumulative samples = step * samples_per_step (default 512
  = batch_size 64 * world_size 8, confirmed r9_train.py:192).
y-axis (primary): IN-1k linear-probe top-1 (frozen trunk); zs top-1/5 secondary.

Fits two models on the STAGE-2 points and reports R^2:
  1. power law  acc = a - b * N^(-c)   (scipy curve_fit, bounds-guarded)
  2. log-linear acc = a + b * log10(N)  (scipy.stats.linregress on log10(N))

Then extrapolates each model to target accuracies (default 20/40/60 %) and
compares required samples vs the local unique-pair ceiling (measured
2026-10-03 E1: ~118M = GPIC-full ~100M + CC12M ~11M + Amshaker ~6M; on-disk
now ~33M; R9 used ~18.5M). Also flags the fitted asymptote `a` (power law
saturates at `a`).

Does NOT run training/eval; pure CPU, no GPU. Run AFTER:
  grep -c "R9 stage2 ALL DONE" /tmp/r9_stage2.log  == 1

Usage:
  python r9_scaling.py [--stage2-log /tmp/r9_stage2.log] [--stage1-log /tmp/r9.log]
                       [--samples-per-step 512] [--targets 0.20,0.40,0.60]
                       [--local-cap-m 118] [--csv /tmp/r9_scaling_points.csv]
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
WIDTH_RE = re.compile(r"R9_stage\d+_w(\d+)")
STEPS_RE = re.compile(r"steps=(\d+)")


def parse_log(path, step_name_normalizer, final_step=None):
    """Return list of {path, step, width, zs1, zs5, lp} dicts."""
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
                step, width = step_name_normalizer(pending, final_step)
                pts.append({
                    "path": pending,
                    "step": step,
                    "width": width,
                    "zs1": float(a.group(1)),
                    "zs5": float(a.group(2)),
                    "lp": float(a.group(3)),
                })
                pending = None
    return pts


def stage2_step_width(path, final_step=None):
    m = STEP_RE.search(path)
    if m:
        step = int(m.group(1))
    elif path.endswith("vision.pt") or path.endswith("vision_fused.pt"):
        step = final_step
    else:
        step = None
    w = WIDTH_RE.search(path)
    width = int(w.group(1)) if w else None
    return step, width


def stage1_step_width(path, final_step=None):
    # stage-1 only evaluated the final vision.pt per arm (30k steps).
    if not path.endswith("vision.pt"):
        return None, None
    w = WIDTH_RE.search(path)
    width = int(w.group(1)) if w else None
    return 30000, width


# ---------------------------------------------------------------------------
# Fits
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


def extrapolate_powerlaw(pfit, target):
    """Solve target = a - b*N^-c  =>  N = (b / (a - target)) ^ (1/c)."""
    a, b, c = pfit["a"], pfit["b"], pfit["c"]
    if target >= a:
        return float("inf"), a
    return float((b / (a - target)) ** (1.0 / c)), a


def extrapolate_loglinear(lfit, target):
    """Solve target = a + b*log10(N)  =>  N = 10^((target-a)/b)."""
    a, b = lfit["a"], lfit["b"]
    if abs(b) < 1e-12:
        return float("inf"), a
    return float(10 ** ((target - a) / b)), a

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage2-log', default='/tmp/r9_stage2.log')
    ap.add_argument('--stage1-log', default='/tmp/r9.log')
    ap.add_argument('--samples-per-step', type=int, default=512)
    ap.add_argument('--targets', default='0.20,0.40,0.60')
    # C1 修正 (2026-10-03 E1 实测): 本地全量上限 ≈118M (GPIC-full ~100M + CC12M ~11M
    # + Amshaker ~6M)，非原假设的 53M。盘上现有 ≈33M；R9 用过 18.5M。
    ap.add_argument('--local-cap-m', type=float, default=118.0)
    ap.add_argument('--csv', default='/tmp/r9_scaling_points.csv')
    args = ap.parse_args()

    targets = [float(t) for t in args.targets.split(',')]
    spp = args.samples_per_step

    # Final training step for stage-2's closing vision.pt (not vision_step*.pt).
    def _final_step(path, default):
        if not os.path.exists(path):
            return default
        with open(path, errors="replace") as fh:
            for line in fh:
                m = STEPS_RE.search(line)
                if m:
                    return int(m.group(1))
        return default
    s2_final = _final_step(args.stage2_log, 108000)
    s1_final = _final_step(args.stage1_log, 30000)

    s2 = parse_log(args.stage2_log, stage2_step_width, s2_final)
    s1 = parse_log(args.stage1_log, stage1_step_width, s1_final)

    def with_samples(pts, tag):
        out = []
        for p in pts:
            if p['step'] is None or p['width'] is None:
                print(f"[SKIP][{tag}] cannot parse step/width: {p['path']}")
                continue
            p = dict(p)
            p['samples'] = p['step'] * spp
            p['tag'] = tag
            out.append(p)
        return out

    s2 = with_samples(s2, 'stage2')
    s1 = with_samples(s1, 'stage1')

    print('=' * 78)
    print('R9 scaling-law analysis (IN-1k linear-probe top-1 vs samples)')
    print(f'  samples/step = {spp} (bs64 x 8 ranks)')
    print(f'  stage-2 points: {len(s2)}  stage-1 points: {len(s1)}')
    print('=' * 78)

    print('\n--- parsed points ---')
    print(f"{'tag':>8} {'width':>6} {'step':>8} {'samples(M)':>11} "
          f"{'zs1%':>7} {'zs5%':>7} {'lp%':>7}  path")
    for p in sorted(s2 + s1, key=lambda x: (x['tag'], x['step'], x['width'])):
        print(f"{p['tag']:>8} {p['width']:>6} {p['step']:>8} "
              f"{p['samples']/1e6:>11.2f} {p['zs1']*100:>7.2f} "
              f"{p['zs5']*100:>7.2f} {p['lp']*100:>7.2f}  "
              f"{os.path.basename(p['path'])}")

    with open(args.csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['tag', 'width', 'step', 'samples',
                                           'zs1', 'zs5', 'lp', 'path'])
        w.writeheader()
        for p in sorted(s2 + s1, key=lambda x: (x['tag'], x['step'], x['width'])):
            w.writerow({k: p[k] for k in w.fieldnames})
    print(f'\n[saved] points -> {args.csv}')

    if len(s2) < 2:
        print('\n[FIT] stage-2 has <2 points; cannot fit. Exiting.')
        return

    s2 = sorted(s2, key=lambda x: x['samples'])
    N = np.array([p['samples'] for p in s2], dtype=float)
    acc = np.array([p['lp'] for p in s2], dtype=float)

    print('\n--- stage-2 fit (w512 long curve) ---')
    pfit, err = fit_powerlaw(N, acc)
    if err is not None:
        print(f'[powerlaw] {err}')
    else:
        print(f"[powerlaw] acc = a - b*N^-c : a={pfit['a']:.5f} "
              f"b={pfit['b']:.5f} c={pfit['c']:.5f}  R^2={pfit['r2']:.4f}")
    lfit = fit_loglinear(N, acc)
    print(f"[loglinear] acc = a + b*log10(N): a={lfit['a']:.5f} "
          f"b={lfit['b']:.5f}  R^2={lfit['r2']:.4f}")

    models = []
    if pfit is not None:
        models.append(('powerlaw', pfit, 'power'))
    models.append(('loglinear', lfit, 'log'))

    cap_samples = args.local_cap_m * 1e6
    print('\n--- extrapolation (samples to reach target IN-1k lp) ---')
    print(f"{'model':>10} {'target%':>8} {'samples(M)':>12} "
          f"{'reach@cap?':>11} {'samples/param':>14}")
    for name, fit, kind in models:
        for t in targets:
            if kind == 'power':
                n, asym = extrapolate_powerlaw(fit, t)
                if n == float('inf'):
                    note = f'NO(asym {asym*100:.1f}%)'
                else:
                    note = 'YES' if n <= cap_samples else 'NO'
            else:
                n, _ = extrapolate_loglinear(fit, t)
                note = 'YES' if n <= cap_samples else 'NO'
            spp_ = n / 126_800_000.0
            n_str = f'{n/1e6:.2f}' if n != float('inf') else 'inf'
            print(f'{name:>10} {t*100:>8.0f} {n_str:>12} {note:>11} {spp_:>14.2f}')

    print('\n--- context (C1-corrected 2026-10-03, E1 measured) ---')
    print(f'local unique-pair ceiling ~= {args.local_cap_m}M '
          f'(GPIC-full ~100M + CC12M ~11M + Amshaker ~6M; +LLaVA/CC3M ~1.15M)')
    print('  three denominators: R9-used ~18.5M | on-disk-now ~33M | local-full ~118M (dynamic, still downloading)')
    print('AIMv2: ~12B pairs = 649x R9-18.5M, 359x on-disk-33M, 102x local-full-118M.')
    print('NOTE: 11 points span ~1 order of magnitude; extrapolating to '
          '20/40/60% is 1-2 orders beyond the data -> large uncertainty.')
    print('DONE')


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""R10-2 — fit a 2D scaling law  acc = f(N, M)  (IN-1k linear-probe top-1).

Data (parsed verbatim from r8_eval_in1k.py output):
  stage-1 periodic ckpts: /tmp/r10_stage1_in1k.log (R10-1, r10_eval_stage1.sh)
      3 towers (w512=126.8M / w768=284.5M / w1024=505.0M) x step{10k,20k,30k}
  stage-2 long curve    : /tmp/r9_stage2.log (R9, 11 ckpts, M=w512)
Axes: N = step*512 samples (bs64 x 8 rank); M = tower params; acc = IN-1k lp top-1.
"""
import argparse, os, re
import numpy as np

CKPT_RE = re.compile(r"\[R8-IN1K\] ckpt=(\S+)")
ACC_RE = re.compile(r"\[R8-IN1K\] zero-shot top1=([0-9.]+) top5=([0-9.]+)"
                    r"\s+linear-probe top1=([0-9.]+)")
STEP_RE = re.compile(r"vision_step(\d+)\.pt$")
WIDTH_RE = re.compile(r"R9_stage\d+_w(\d+)")
WIDTH_PARAMS = {512: 126.8e6, 768: 284.5e6, 1024: 505.2e6}
SPP = 512


def parse_log(path, final_step_default=None):
    if not os.path.exists(path):
        return []
    pts, pending = [], None
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = CKPT_RE.search(line)
            if m:
                pending = m.group(1); continue
            a = ACC_RE.search(line)
            if a and pending is not None:
                step = None
                sm = STEP_RE.search(pending)
                if sm:
                    step = int(sm.group(1))
                elif pending.endswith("vision.pt") and final_step_default is not None:
                    step = final_step_default
                wm = WIDTH_RE.search(pending)
                width = int(wm.group(1)) if wm else None
                pts.append({"path": pending, "step": step, "width": width,
                            "zs1": float(a.group(1)), "zs5": float(a.group(2)),
                            "lp": float(a.group(3))})
                pending = None
    return pts


def ols(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return coef, r2, pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage1-log', default='/tmp/r10_stage1_in1k.log')
    ap.add_argument('--stage2-log', default='/tmp/r9_stage2.log')
    ap.add_argument('--csv', default='/tmp/r10_scaling2d_points.csv')
    args = ap.parse_args()

    s1 = parse_log(args.stage1_log, final_step_default=30000)
    s2 = parse_log(args.stage2_log, final_step_default=108000)

    print('=' * 82)
    print('R10 2D scaling-law analysis  acc = f(N, M)  (IN-1k linear-probe top-1)')
    print(f'  samples/step = {SPP} (bs64 x 8 rank)')
    print(f'  stage-1 points: {len(s1)}   stage-2 points: {len(s2)}')
    print('=' * 82)

    rows = []
    for p in s1:
        if p['step'] is None:
            continue
        M = WIDTH_PARAMS.get(p['width'])
        if M is None:
            continue
        rows.append({'tag': 'stage1', 'width': p['width'], 'step': p['step'],
                     'N': p['step'] * SPP, 'M': M, 'M_m': M / 1e6,
                     'lp': p['lp'], 'zs1': p['zs1'], 'zs5': p['zs5'], 'path': p['path']})
    for p in s2:
        if p['step'] is None:
            continue
        M = WIDTH_PARAMS.get(p['width'])
        if M is None:
            continue
        rows.append({'tag': 'stage2', 'width': p['width'], 'step': p['step'],
                     'N': p['step'] * SPP, 'M': M, 'M_m': M / 1e6,
                     'lp': p['lp'], 'zs1': p['zs1'], 'zs5': p['zs5'], 'path': p['path']})

    print('\n--- all raw points (N, M, acc) ---')
    print(f"{'tag':>7} {'w':>4} {'step':>8} {'samples(M)':>11} {'M(M)':>8} "
          f"{'zs1%':>7} {'zs5%':>7} {'lp%':>7}")
    for r in sorted(rows, key=lambda x: (x['width'], x['N'])):
        print(f"{r['tag']:>7} {r['width']:>4} {r['step']:>8} {r['N']/1e6:>11.3f} "
              f"{r['M_m']:>8.1f} {r['zs1']*100:>7.2f} {r['zs5']*100:>7.2f} {r['lp']*100:>7.2f}")

    # Write merged points CSV (reproducibility / report citation).
    try:
        with open(args.csv, 'w') as fh:
            fh.write("tag,width,step,N_samples,M_params,lp_top1,zs_top1,zs_top5,path\n")
            for r in sorted(rows, key=lambda x: (x['width'], x['N'])):
                fh.write(f"{r['tag']},{r['width']},{r['step']},{r['N']:.0f},{r['M']:.0f},"
                         f"{r['lp']:.6f},{r['zs1']:.6f},{r['zs5']:.6f},{r['path']}\n")
        print(f'\n[csv] wrote {len(rows)} points -> {args.csv}')
    except OSError as e:
        print(f'\n[csv] WARN could not write {args.csv}: {e}')

    # Primary fit: stage2 w512 (N-axis) + stage1 w768/w1024 (M-axis).
    # Stage1 w512 dup-region kept OUT (covered by stage2); reported as consistency check.
    fit_rows = [r for r in rows if r['tag'] == 'stage2']
    fit_rows += [r for r in rows if r['tag'] == 'stage1' and r['width'] in (768, 1024)]
    fit_rows = sorted(fit_rows, key=lambda x: (x['width'], x['N']))

    print('\n--- fit set (stage2 w512 long curve + stage1 w768/w1024 M-axis) ---')
    print(f'n = {len(fit_rows)} points')
    for r in fit_rows:
        print(f"  {r['tag']:>7} w={r['width']:>4} N={r['N']/1e6:9.3f}M "
              f"M={r['M_m']:>6.1f}M lp={r['lp']*100:.2f}%")

    if len(fit_rows) < 4:
        print('\n[FIT] <4 points; cannot fit 2D model. Exiting.')
        return

    N = np.array([r['N'] for r in fit_rows], dtype=float)
    M = np.array([r['M'] for r in fit_rows], dtype=float)
    acc = np.array([r['lp'] for r in fit_rows], dtype=float)
    lnN, lnM = np.log10(N), np.log10(M)

    XA = np.column_stack([np.ones_like(lnN), lnN, lnM, lnN * lnM])
    coefA, r2A, _ = ols(XA, acc)
    a, b, c, d = coefA
    print('\n--- fit A (full: a + b*log10(N) + c*log10(M) + d*log10(N)*log10(M)) ---')
    print(f'  a={a:+.5f}  b={b:+.5f} (log10 N)  c={c:+.5f} (log10 M)  d={d:+.5f} (inter)')
    print(f'  R^2 = {r2A:.4f}')

    XA0 = np.column_stack([np.ones_like(lnN), lnN, lnM])
    coefA0, r2A0, _ = ols(XA0, acc)
    a0, b0, c0 = coefA0
    print('\n--- fit A0 (no interaction: a + b*log10(N) + c*log10(M)) ---')
    print(f'  a={a0:+.5f}  b={b0:+.5f} (log10 N)  c={c0:+.5f} (log10 M)  R^2 = {r2A0:.4f}')

    print('\n--- marginal effect of M at fixed N (observed range) ---')
    n_lo, n_hi = lnN.min(), lnN.max()
    lnN_mid = np.log10(15.36e6)
    for name, coef in [('A ', (a, b, c, d)), ('A0', (a0, b0, c0, None))]:
        aa, bb, cc, dd = coef
        deff = lambda n_: cc + (dd * n_ if dd is not None else 0.0)
        per2x = deff(lnN_mid) * np.log10(2.0)
        print(f'  [{name}] dacc/dlog10(M) @N=5.12M={deff(n_lo):+.4f}  @N=55.3M={deff(n_hi):+.4f}  '
              f'(per 2x M @N=15.4M: {per2x:+.4f} acc)')

    print('\n--- optimal N/M allocation under compute budget C ~ 6*N*M ---')
    print('  x=log10(M), K=log10(C/6): acc = a+bK + (c-b+dK)x - d x^2')
    sweep_M = np.logspace(np.log10(20e6), np.log10(2e9), 200)
    C_ref = 6.0 * 55.3e6 * 126.8e6
    K_ref = np.log10(C_ref / 6.0)
    N_sweep = C_ref / (6.0 * sweep_M)
    lnN_s = np.log10(N_sweep); x_s = np.log10(sweep_M)
    acc_s = a + b * lnN_s + c * x_s + d * lnN_s * x_s
    i_best = int(np.argmax(acc_s))
    print(f'  reference budget C_ref = 6*55.3M*126.8M = {C_ref:.2e} FLOPs')
    print(f'  [A] sweep M in [20M..2G] @ fixed C_ref -> max acc={acc_s[i_best]*100:.2f}% at '
          f'M={sweep_M[i_best]/1e6:.0f}M, N={N_sweep[i_best]/1e6:.1f}M '
          f'(observed M range [126.8M..505.2M]; else EXTRAPOLATION)')
    if sweep_M[i_best] < 126.8e6:
        print('  => optimum M BELOW observed floor -> extend M axis downward (R10-3: w384 ~71M / w640 ~197M)')
    else:
        print(f'  => optimum M={sweep_M[i_best]/1e6:.0f}M within/near observed range.')
    x_anchor = np.log10(126.8e6); K_anchor = np.log10(15.36e6) + x_anchor
    ddx = (c - b + d * K_anchor) - 2 * d * x_anchor
    print(f'  [A] dacc/dlog10(M) @anchor(N=15.4M,M=126.8M own budget)={ddx:+.4f} -> '
          f'{"larger M WORSE here (data-limited regime)" if ddx < 0 else "larger M better here"}')

    print('\n--- span & uncertainty (honest) ---')
    print(f'  N span: {N.min()/1e6:.2f}M .. {N.max()/1e6:.2f}M samples ({N.max()/N.min():.1f}x, ~1 order)')
    Ms = np.array([WIDTH_PARAMS[w] for w in (512, 768, 1024)])
    print(f'  M span: {Ms.min()/1e6:.1f}M .. {Ms.max()/1e6:.1f}M params ({Ms.max()/Ms.min():.1f}x, '
          f'~0.6 orders, {len(Ms)} points; no point < 126.8M)')
    print('  -> M axis VERY sparse (3 pts, 4x). Extrapolation to smaller/larger M is highly uncertain.')
    print('  -> run variance: stage-1 w512 @30k vs stage-2 w512 @30k = 2 independent runs same (N,M).')

    print('\n--- consistency check: stage-1 w512 (dup region) vs stage-2 w512 curve ---')
    s1w512 = [r for r in rows if r['tag'] == 'stage1' and r['width'] == 512]
    s2byN = {r['N']: r for r in rows if r['tag'] == 'stage2' and r['width'] == 512}
    for r in sorted(s1w512, key=lambda x: x['N']):
        s2r = s2byN.get(r['N'])
        if s2r is not None:
            print(f"  N={r['N']/1e6:9.3f}M  stage1 lp={r['lp']*100:5.2f}%  "
                  f"stage2 lp={s2r['lp']*100:5.2f}%  delta={(r['lp']-s2r['lp'])*100:+5.2f} pp")

    print('\nDONE')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WSD（Warmup-Stable-Decay）LR 曲线 · D 段指数衰减 的理论值 / 对账工具。

公式（本计划 2026-10-26 定案）::

    0 <= it <= warmup            : lr = peak * it / warmup
    warmup < it <= total-decay   : lr = peak
    total-decay < it <= total    : p  = (it - (total-decay)) / decay
                                   lr = peak * (min_lr/peak) ** p

即 D 段是**纯指数**：p=0 → peak，p=1 → min_lr（本例 1e-3 → 1e-4，每 25% 段约 ×0.562）。

用法::

    # 打印理论曲线（默认 S1+S2+Decay 全程 1,070,000 步）
    python lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 \
        --decay-iters 20000 --total-iters 1070000

    # 与 TensorBoard 导出的 csv 对账（表头需含 step / learning-rate）
    python lr_schedule.py ... --tb-csv /tmp/lr.csv --tol 1e-3

退出码：0=一致 / 1=超差或文件问题。
"""
from __future__ import annotations

import argparse
import csv
import math
import sys


def lr_at(it: int, peak: float, min_lr: float, warmup: int, total: int, decay: int) -> float:
    if warmup > 0 and it <= warmup:
        return peak * it / warmup
    stable_end = total - decay
    if decay <= 0 or it <= stable_end:
        return peak
    p = (it - stable_end) / decay
    p = min(max(p, 0.0), 1.0)
    return peak * (min_lr / peak) ** p


def main() -> None:
    ap = argparse.ArgumentParser(description="WSD-指数 LR 曲线 / 对账")
    ap.add_argument("--peak", type=float, default=1e-3)
    ap.add_argument("--min", dest="min_lr", type=float, default=1e-4)
    ap.add_argument("--warmup", type=int, default=2000)
    ap.add_argument("--decay-iters", type=int, default=20000)
    ap.add_argument("--total-iters", type=int, default=1070000)
    ap.add_argument("--points", type=int, default=11, help="D 段采样点数")
    ap.add_argument("--tb-csv", default="", help="TensorBoard 导出的 csv（step,learning-rate）")
    ap.add_argument("--tol", type=float, default=1e-3, help="相对误差容限（默认 0.1%）")
    args = ap.parse_args()

    total, decay = args.total_iters, args.decay_iters
    stable_end = total - decay
    print(f"# peak={args.peak:g} min={args.min_lr:g} warmup={args.warmup} "
          f"total={total:,} decay={decay:,} (D 段起 {stable_end:,})")
    hl = decay * math.log(2) / math.log(args.peak / args.min_lr)
    print(f"# 指数底 = (min/peak)^(1/decay) = "
          f"{(args.min_lr / args.peak) ** (1.0 / decay):.10f} /步；半衰期 ≈ {hl:.1f} 步")

    print(f"\n{'step':>11}  {'phase':<8} {'p':>6} {'lr':>14}")
    rows = [0, args.warmup // 2, args.warmup, stable_end]
    rows += [stable_end + round(decay * i / (args.points - 1)) for i in range(args.points)]
    shown = set()
    for it in sorted(set(rows)):
        if it < 0:
            continue
        shown.add(it)
        p = max(0.0, (it - stable_end) / decay) if decay else 0.0
        phase = "warmup" if it <= args.warmup else ("stable" if it <= stable_end else "decay")
        print(f"{it:>11,}  {phase:<8} {p:>6.3f} "
              f"{lr_at(it, args.peak, args.min_lr, args.warmup, total, decay):>14.6e}")
    if total not in shown:
        print(f"{total:>11,}  {'end':<8} {1.0:>6.3f} "
              f"{lr_at(total, args.peak, args.min_lr, args.warmup, total, decay):>14.6e}")

    if not args.tb_csv:
        return

    try:
        with open(args.tb_csv, encoding="utf-8") as f:
            rd = csv.DictReader(f)
            fields = {k.lower(): k for k in (rd.fieldnames or [])}
            k_step = fields.get("step") or fields.get("iteration")
            k_lr = fields.get("learning-rate") or fields.get("learning_rate") or fields.get("lr")
            if not k_step or not k_lr:
                print(f"FAIL: csv 缺 step/learning-rate 列（表头={rd.fieldnames}）", file=sys.stderr)
                sys.exit(1)
            worst, worst_it, n = 0.0, -1, 0
            for r in rd:
                it = int(float(r[k_step]))
                got = float(r[k_lr])
                exp = lr_at(it, args.peak, args.min_lr, args.warmup, total, decay)
                rel = abs(got - exp) / exp if exp else 0.0
                n += 1
                if rel > worst:
                    worst, worst_it = rel, it
    except OSError as e:
        print(f"FAIL: 读不到 {args.tb_csv}: {e}", file=sys.stderr)
        sys.exit(1)

    ok = worst <= args.tol
    print(f"\n对账：{n} 点，最大相对误差 {worst:.3e} @ step {worst_it:,}"
          f"（容限 {args.tol:g}）-> {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

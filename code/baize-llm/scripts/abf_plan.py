#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ABF（Adjusted Base Frequency）长上下文准备表。

输出三件事：
  1. 每个目标上下文长度对应的 **ABF 建议 theta**（理论式）+ 本项目 **实测锚点**；
  2. 为保持 tok/microbatch/GPU = 16,384（显存顶格线）所需的 **CP / DP / gbs**；
  3. 每级能否用现有 16 卡跑（DP 必须为 ≥1 的整数）。

公式（Xiong et al. 2023 / CodeLlama ABF）::

    theta_ABF = theta_train * (L_target / L_train) ** (d / (d - 2))

其中 d = head_dim（本项目 128 ⇒ 指数 ≈ 1.0159）。⚠️ 该式是**理论参考**；
本项目 2026-10-06 的 B1 实测表明 **theta=1e6 已可从 4K 训练外推到 1M 且 PPL 无退化**
（128K 53.34 / 256K 52.99 / 512K 55.81 / 1M 55.42），所以**默认不抬 theta，只在实测退化时按本表升级**。

用法::

    python abf_plan.py
    python abf_plan.py --targets 32768,65536,131072,262144,524288,1048576 --json
"""
from __future__ import annotations

import argparse
import json
import math
import sys

# 本项目实测锚点（B1，2026-10-06，p5b/hf_iter_4771，theta=1e6, mp=1M）
MEASURED = {
    4096: ("83.24", "基线(theta=1e4) 75.36 → ABF 税 +10.5%"),
    8192: ("64.91", "—"),
    16384: ("60.08", "本次训练长度"),
    32768: ("58.55", "—"),
    65536: ("51.53", "—"),
    131072: ("53.34", "prefill 10.7s / 10.9GB"),
    262144: ("52.99", "prefill 13.8s / 14.25GB"),
    524288: ("55.81", "prefill 53.0s / 19.65GB"),
    1048576: ("55.42", "prefill 172.4s / 34.68GB"),
}


def fmt_tok(n: float) -> str:
    for u, v in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if n >= v:
            return f"{n / v:.2f}{u}"
    return f"{n:.0f}"


def main() -> None:
    ap = argparse.ArgumentParser(description="ABF 长上下文准备表")
    ap.add_argument("--base-theta", type=float, default=1e6, help="当前训练 theta（默认 1e6）")
    ap.add_argument("--train-ctx", type=int, default=16384)
    ap.add_argument("--head-dim", type=int, default=128)
    ap.add_argument("--gpus", type=int, default=16)
    ap.add_argument("--tok-per-mb", type=int, default=16384,
                    help="tok/microbatch/GPU 上限（显存顶格线，#792 实测 16,384）")
    ap.add_argument("--accum", type=int, default=16)
    ap.add_argument("--mbs", type=int, default=1)
    ap.add_argument("--targets", default="32768,65536,131072,262144,524288,1048576")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets = [int(x) for x in args.targets.replace(" ", "").split(",") if x]
    expo = args.head_dim / (args.head_dim - 2)
    rows = []
    for t in targets:
        s = t / args.train_ctx
        theta_abf = args.base_theta * (s ** expo)
        cp = max(1, math.ceil(t / args.tok_per_mb))
        cp = 1 << (cp - 1).bit_length()          # 向上取 2 的幂
        dp = args.gpus // cp
        gbs = args.accum * args.mbs * dp if dp >= 1 else 0
        feasible = dp >= 1
        tps = gbs * t if feasible else 0
        tmb = t // cp
        ppl = MEASURED.get(t, (None, ""))
        rows.append({
            "target": t, "scale": round(s, 3), "theta_abf": float(f"{theta_abf:.4g}"),
            "cp": cp, "dp": dp, "gbs": gbs, "tok_per_mb_gpu": tmb,
            "tok_per_step": tps, "feasible_16gpu": feasible,
            "measured_ppl_theta1e6": ppl[0], "note": ppl[1],
        })

    if args.json:
        print(json.dumps({"base_theta": args.base_theta, "train_ctx": args.train_ctx,
                          "exponent": round(expo, 6), "rows": rows},
                         ensure_ascii=False, indent=2))
        return

    print(f"# base_theta={args.base_theta:g}  train_ctx={args.train_ctx}  head_dim={args.head_dim}"
          f"  ABF 指数 d/(d-2)={expo:.4f}")
    print(f"# 约束：tok/microbatch/GPU = {args.tok_per_mb}（seq/CP），accum={args.accum}，GPU={args.gpus}")
    print()
    hdr = (f"{'target':>10} {'scale':>7} {'theta_ABF':>12} {'CP':>3} {'DP':>3} "
           f"{'gbs':>5} {'tok/mb/gpu':>10} {'tok/step':>10} {'可跑':>4} {'实测PPL@1e6':>11}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['target']:>10,} {r['scale']:>7.2f} {r['theta_abf']:>12.4g} {r['cp']:>3} "
              f"{r['dp']:>3} {r['gbs']:>5} {r['tok_per_mb_gpu']:>10,} "
              f"{r['tok_per_step']:>10,} {'✓' if r['feasible_16gpu'] else '✗':>4} "
              f"{r['measured_ppl_theta1e6'] or '-':>11}")
    print()
    print("# 说明：实测 PPL 来自 B1（theta=1e6，p5b ckpt）——数值随 ctx 增大而下降是正常因果 LM 行为；")
    print("#       theta_ABF 是**理论升级值**，只在实测出现退化（PPL 相对上一级抬升 >5% 或 passkey 掉点）时才启用。")
    print("#       16 卡不可行的目标（DP<1）需 CP>8 或多机扩卡，当前不做。")
    bad = [r for r in rows if not r["feasible_16gpu"]]
    if bad:
        print(f"# ⚠️ 不可行目标：{[r['target'] for r in bad]}（需 CP>{max(r['cp'] for r in bad)} 或更多 GPU）",
              file=sys.stderr)


if __name__ == "__main__":
    main()

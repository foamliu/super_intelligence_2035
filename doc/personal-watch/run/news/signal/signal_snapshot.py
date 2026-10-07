#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/signal_snapshot.py — 第11批(P0) · **信号面最近快照**（供日报 §3 引用）
============================================================================
口径**完全沿用** `lag_corr.py`（同源语料 / 同关键词 / 同滚动 z-score），
唯一区别：**不解价格、不做回归** —— 只打印**最近 N 个交易日**的
「信号 X 的原始条数 + 滚动 z 分（窗 252 / min60，只用 ≤t 信息）」。

用途：`news/signal/daily/<date>.md` 早报的「盘前信号简报」（规格 §3）——
      「近 24h 新信号（类别 / 条数 / 偏离 z 分）」。

⚠️ 语料 `chinanews-*.jsonl.gz` 截至 2026-10-03（回溯已冻结）⇒ 本快照 **as-of = 语料末日所在交易日**，
   **不是**「今日实时」；日报**必须如实标注 as-of**（🚫 不许把历史快照写成当日信号）。
⚠️ 非因果 · 非投资建议；🚫 无点位/仓位/择时。

用法：
  python3 news/signal/signal_snapshot.py            # 写 LATEST_SIGNALS.md（最近 5 交易日）
  python3 news/signal/signal_snapshot.py --tail 10  # 最近 10 交易日
"""
from __future__ import annotations

import argparse
import os
import sys
from bisect import bisect_left

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lag_corr as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, "LATEST_SIGNALS.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tail", type=int, default=5, help="打印最近 N 个交易日")
    args = ap.parse_args()

    assets = L.load_prices()
    cal = L.build_calendar(assets)
    M = len(cal)
    daily_counts = L.load_signal_counts()
    names = [n for n, _ in L.SIGNALS]
    cnt = {}
    for name in names:
        arr = np.zeros(M)
        for d, dic in daily_counts.items():
            c = dic.get(name, 0)
            if c:
                idx = bisect_left(cal, d)
                if idx < M:
                    arr[idx] += c
        cnt[name] = arr
    z = {n: L.rolling_z(np.log1p(cnt[n]), L.ROLL_WIN, L.ROLL_MIN) for n in names}

    tail = min(args.tail, M)
    idxs = list(range(M - tail, M))
    out = []
    out.append("# LATEST_SIGNALS — 信号面最近快照（第11批 · 供日报引用）")
    out.append("")
    out.append(f"> 生成：`news/signal/signal_snapshot.py` ｜ 口径 = `lag_corr.py`（同源/同关键词/同滚动 z）")
    out.append(f"> ⚠️ **as-of = {cal[-1]}**（语料 `chinanews` 末日所在交易日）——"
               "**不是今日实时信号**；语料回溯已冻结（截至 2026-10-03）。")
    out.append("> ⚠️ **非因果 · 非投资建议**；🚫 无点位/仓位/择时。z = 滚动 z-score（窗 252 / min60，只用 ≤t 信息）。")
    out.append("")
    out.append("| 交易日 | 信号 | 原始条数 | z 分 |")
    out.append("|:--|:--|--:|--:|")
    for i in idxs:
        for n in names:
            zz = z[n][i]
            zs = "" if not np.isfinite(zz) else f"{zz:+.2f}"
            mark = " ⚠️" if (np.isfinite(zz) and abs(zz) >= 1.5) else ""
            out.append(f"| {cal[i]} | {n} | {int(cnt[n][i])} | {zs}{mark} |")
    # 汇总：末日 |z|>=1.5 的信号
    last = M - 1
    hi = [(n, float(z[n][last]), int(cnt[n][last])) for n in names
          if np.isfinite(z[n][last]) and abs(z[n][last]) >= 1.5]
    out.append("")
    out.append(f"## 汇总（as-of {cal[-1]}）")
    if hi:
        out.append(f"- |z| ≥ 1.5 的信号（{len(hi)} 个）：" +
                   "；".join(f"`{n}` z={zv:+.2f}（条数 {c}）" for n, zv, c in hi))
    else:
        out.append("- **末日无 |z| ≥ 1.5 的信号**（如实记录：既不异常偏高、也不异常偏低）。")
    out.append("- ⚠️ 单条 |z| ≥ 1.5 属**未校正的探索性读数**，**不构成任何结论**；"
               "任何「线索」必须过 `LAG_CORR.md` 的 **FDR + 样本外 + 分年度一致**三道（PREREG §6）。")
    out.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"[snapshot] as-of {cal[-1]} · {len(hi)} 个 |z|>=1.5 → {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

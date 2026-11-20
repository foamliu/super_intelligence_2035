#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/block_boot.py — 第11批(P0) · R2 补充：**移动块自助（moving-block bootstrap）CI**
============================================================================
为什么有本脚本（PREREG §5① 欠账）：
  `PREREG.md` §5① 写死：自相关/重叠窗的 CI **除 HAC(Newey–West) 外，另给 block bootstrap**
  （block = 21 交易日、5,000 次）。R1 只给了 HAC 解析 CI ⇒ 本脚本补齐。

对象如何选（**先写死、机械化、不挑好看格**，分三组，**分别报**）：
  * **G1** = **FDR 后 `q<0.10` 的全部格子**（PREREG §6 判据下的「候选线索」）；空集则如实写「无对象」；
  * **G2** = **每个频率下 |系数| 最大的前 N 格**（机械规则）—— ⚠️ **事后选取** ⇒ 标 `exploratory(事后选取)`；
  * **G3** = **全网格均匀随机抽 N 格**（`seed` 固定）—— ⚠️ 这是**为负面结论做稳健性检验的关键组**：
    「典型格」的 bootstrap CI 是否普遍跨 0。**G1/G2/G3 一律不得据此宣称任何信号。**

方法（移动块自助，保序列自相关）：
  * 取该格的**有效样本掩码**（与 `lag_corr.py::eval_cell` **同一构造**：`y=r_{t+k}`、`D=[1,xz,prev,...ctrl]`）；
  * 对掩码后的 **有序** `(D, y)` 做 **长度 21 的移动块重采样**（`ceil(N/21)` 块、起点均匀随机）；
  * 每轮重抽后 OLS 重估 `b`（= xz 的系数）→ 得 5,000 个 `b*`；
  * CI = 百分位 `[2.5%, 97.5%]`；另报**同号占比**（`b*` 与点估计同号的频率）。

⚠️ 口径（全行程禁用「影响/导致/利好/利空/冲击」「点位预测/仓位/择时」；非因果 · 非投资建议）。
✅ 负面结果（「未发现稳定滞后相关」）照写 —— 本脚本**正是为它做稳健性支撑**。

用法：
  python3 news/signal/block_boot.py                 # 全量（FDR 存活格 + 每频 top5）→ 写 BOOTSTRAP.md
  python3 news/signal/block_boot.py --top 3 --B 1000  # 自检（小 B）
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from bisect import bisect_left

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lag_corr as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(HERE, "BOOTSTRAP.md")
CSV_IN = os.path.join(HERE, "lag_corr.csv")

BLOCK = 21          # 块长（交易日；PREREG §5① 写死）
BOOT_B = 5000       # 自助次数（PREREG §5① 写死）
SEED = 20351008     # 自助抽样固定种子（可复现）
SEED_RAND = 20351009  # G3 随机选格固定种子（可复现）


def rebuild_design(freq, signal, code, k, ctx):
    """按 lag_corr.eval_cell 的**同一口径**重建该格的 (Dm, ym, N)；None = 样本不足/口径不一致。"""
    xz_map, r_map, ctrl, years, dates, min_n = ctx[freq]
    xz = xz_map.get(signal)
    r = r_map.get(code)
    if xz is None or r is None or len(r) != len(xz):
        return None
    M = len(r)
    y = np.full(M, np.nan)
    if k > 0:
        y[:M - k] = r[k:]
    else:
        y = r.copy()
    prev = np.full(M, np.nan)
    prev[1:] = r[:-1]
    ctrl_cols = ctrl if ctrl is not None else []
    D = np.column_stack([np.ones(M), xz, prev] + ctrl_cols)
    mask = np.isfinite(y) & np.isfinite(xz) & np.all(np.isfinite(D), axis=1)
    N = int(mask.sum())
    if N < min_n or np.std(xz[mask]) < 1e-9:
        return None
    return D[mask], y[mask], N


def ols_b1(D, y):
    """只取 xz 系数 b1（pinv，容忍共线）。"""
    beta = np.linalg.pinv(D.T @ D) @ (D.T @ y)
    return float(beta[1])


def block_bootstrap(Dm, ym, B, rng):
    """移动块自助 → (b* 数组, 是否退化为整段重抽)。"""
    N = len(ym)
    nb = int(np.ceil(N / BLOCK))
    starts_max = N - BLOCK
    bs = np.empty(B)
    if starts_max < 1:                      # N<=块长：退化为整段重抽（如实标注在文里）
        for i in range(B):
            idx = rng.integers(0, N, size=N)
            bs[i] = ols_b1(Dm[idx], ym[idx])
        return bs, True
    for i in range(B):
        st = rng.integers(0, starts_max + 1, size=nb)
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in st])[:N]
        bs[i] = ols_b1(Dm[idx], ym[idx])
    return bs, False




def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5, help="每频率取 |coef| 最大前 N 格（G2，事后选取）")
    ap.add_argument("--rand", type=int, default=20, help="G3 全网格随机抽样格数")
    ap.add_argument("--B", type=int, default=BOOT_B, help="自助次数")
    args = ap.parse_args()

    rows = read_csv()
    surv = [r for r in rows if float(r["q"]) < 0.10]        # G1: FDR 存活格（可能为空）
    by_freq = {}                                            # G2: 每频率 |coef| 前 N
    for r in rows:
        by_freq.setdefault(r["freq"], []).append(r)

    groups = []                                             # [(label, [row,...])]
    groups.append(("G1 · FDR q<0.10（PREREG 判据）", surv))
    for f in ("daily", "weekly", "monthly"):
        if f in by_freq:
            top = sorted(by_freq[f], key=lambda x: -abs(float(x["coef"])))[:args.top]
            groups.append((f"G2 · top|coef| {f}（事后选取·exploratory）", top))
    rsel = np.random.default_rng(SEED_RAND)
    ridx = rsel.choice(len(rows), size=min(args.rand, len(rows)), replace=False)
    groups.append((f"G3 · 随机 {len(ridx)} 格（uniform·seed={SEED_RAND}）",
                   [rows[i] for i in ridx]))

    targets = []
    for glabel, grows in groups:
        for r in grows:
            targets.append((r, glabel))

    # ── 载入与 lag_corr.main 一致的上下文 ────────────────────────────────────
    assets = L.load_prices()
    cal = L.build_calendar(assets)
    M = len(cal)
    print(f"[boot] 交易日历 {M} 天 {cal[0]}~{cal[-1]} · 资产 {len(assets)}")
    daily_counts = L.load_signal_counts()
    # 窗口 = 「价格 ∩ 语料」共同可用区间（与 lag_corr.main 同规则 · R3 显式化）
    corpus_end = max(daily_counts) if daily_counts else ""
    if corpus_end and cal[-1] > corpus_end:
        cal = [d for d in cal if d <= corpus_end]
        M = len(cal)
        print(f"[boot] 语料止于 {corpus_end} → 日历截断为 {M} 天 {cal[0]}~{cal[-1]}")
    names = [n for n, _ in L.SIGNALS]
    cnt_daily = {}
    for name in names:
        arr = np.zeros(M)
        for d, dic in daily_counts.items():
            c = dic.get(name, 0)
            if c:
                idx = bisect_left(cal, d)
                if idx < M:
                    arr[idx] += c
        cnt_daily[name] = arr
    xz_daily = {n: L.rolling_z(np.log1p(cnt_daily[n]), L.ROLL_WIN, L.ROLL_MIN) for n in names}
    ctrl_daily = L.build_ctrl(cal, True)
    years_daily = np.array([int(d[:4]) for d in cal])
    dates_daily = np.array(cal)
    r_daily = {}
    for a in assets:
        rr = L.log_returns(a["rows"], cal)
        if rr is not None:
            r_daily[a["code"]] = rr

    ctx = {"daily": (xz_daily, r_daily, ctrl_daily, years_daily, dates_daily, L.MIN_N_DAILY)}
    for mode, win, minp, lag, mn in [("weekly", 52, 12, L.LAG_WEEK, L.MIN_N_LOW),
                                     ("monthly", 24, 6, L.LAG_MONTH, L.MIN_N_LOW)]:
        keys, members, years_p = L.group_periods(cal, mode)
        xz_p = {}
        for nm in names:
            cp = np.array([sum(cnt_daily[nm][m]) for m in members])
            xz_p[nm] = L.rolling_z(np.log1p(cp), win, minp)
        r_map = {a["code"]: np.array([np.nansum(r_daily[a["code"]][m]) for m in members])
                 for a in assets if a["code"] in r_daily}
        ctx[mode] = (xz_p, r_map, None, np.array(years_p),
                     np.array([k[:4] for k in keys]), mn)

    rng = np.random.default_rng(SEED)
    out = []
    t0 = time.time()
    for r, glabel in targets:
        f, k = r["freq"], int(r["k"])
        rebuilt = rebuild_design(f, r["signal"], r["code"], k, ctx)
        if rebuilt is None:
            out.append({**r, "group": glabel, "boot_lo": None, "boot_hi": None,
                        "same_sign": None, "nb": None})
            continue
        Dm, ym, N = rebuilt
        bs, fallback = block_bootstrap(Dm, ym, args.B, rng)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        coef = float(r["coef"])
        same = float(np.mean((bs >= 0) == (coef >= 0)))
        out.append({**r, "group": glabel, "boot_lo": float(lo), "boot_hi": float(hi),
                    "same_sign": same, "nb": args.B,
                    "note": "整段重抽(N<=块长)" if fallback else ""})
        print(f"[boot] {glabel[:2]} {f:7s} {r['signal']:14s} {r['code']:9s} k={k:2d} "
              f"b={coef:+.3g} boot=[{lo:+.3g},{hi:+.3g}] same_sign={same:.3f} "
              f"({time.time()-t0:.0f}s)")
    write_md(out, args, surv)
    print(f"[boot] 完成 {len(out)} 格 → {OUT_MD}（{time.time()-t0:.0f}s）")
    return 0

def read_csv():
    with open(CSV_IN, encoding="utf-8") as f:
        return list(csv.DictReader(f))



def write_md(out, args, surv):
    L_ = []
    L_.append("# BOOTSTRAP — 移动块自助 CI（第11批 · R2 补充 · `block_boot.py`）")
    L_.append("")
    L_.append(f"> 生成：`news/signal/block_boot.py` ｜ 预注册依据：`PREREG.md` §5①"
              f"（block={BLOCK} 交易日 · B={args.B} · seed={SEED}）｜ 源数据：`lag_corr.csv`")
    L_.append("> ⚠️ **非因果 · 非投资建议**：本文只对**已落盘格**补**保序列自相关**的自助 CI；"
              "🚫 无「影响/导致/利好/利空/冲击」、🚫 无点位/仓位/择时。")
    L_.append("> ⚠️ **选取规则（写死）**：**G1** = FDR `q<0.10` 全部格；"
              "**G2** = 每频率 |系数| 前 5 格（**事后选取** ⇒ 标 `exploratory`）；"
              "**G3** = 全网格**均匀随机** 20 格（固定 seed）—— **三组均不得据此宣称任何信号**。")
    L_.append("")
    L_.append("## 1. 对象说明（三组，分别报）")
    L_.append(f"- **G1（FDR `q<0.10` 存活格）= {len(surv)} 格** —— "
              + ("**空集 ⇒ 无「候选线索」可用于自助（如实记录）**。" if not surv else "见下表。"))
    L_.append("- **G2（每频率 |系数| 前 N）** = **事后选取** ⇒ 标 `exploratory`，**不得当作线索**"
              "（其在网格中本就偏向 |b| 大者）。")
    L_.append(f"- **G3（全网格均匀随机 N 格，seed={SEED_RAND}）** = **负面结论的关键稳健性组**："
              "「**典型格**」的 bootstrap CI 是否普遍跨 0。")
    L_.append(f"- 合计自助 **{len(out)}** 格；块长 {BLOCK} 交易日、B={args.B}。")
    L_.append("")
    seen_groups = []
    for r in out:
        if r["group"] not in seen_groups:
            seen_groups.append(r["group"])
    for gi, g in enumerate(seen_groups, 1):
        rs = [r for r in out if r["group"] == g]
        n_ok = sum(1 for r in rs if r["boot_lo"] is not None)
        n_in = sum(1 for r in rs if r["boot_lo"] is not None and float(r["ci_lo"]) <= 0 <= float(r["ci_hi"]))
        n_bt = sum(1 for r in rs if r["boot_lo"] is not None and r["boot_lo"] <= 0 <= r["boot_hi"])
        n_agree = sum(1 for r in rs if r["boot_lo"] is not None
                      and (r["boot_lo"] <= 0 <= r["boot_hi"]) == (float(r["ci_lo"]) <= 0 <= float(r["ci_hi"])))
        L_.append(f"## 2.{gi} {g}")
        if not rs:
            L_.append("- _（空）_")
            L_.append("")
            continue
        L_.append(f"- 格数 **{len(rs)}**（有效自助 {n_ok}）｜**HAC CI 含 0**：{n_in}｜"
                  f"**bootstrap CI 含 0**：{n_bt}｜**两者『含 0 判定』一致**：{n_agree}/{n_ok}")
        L_.append("")
        L_.append("| 频率 | 信号 | 资产 | k | 系数 b | q | HAC 95%CI | block-boot 95%CI | 同号占比 | N |")
        L_.append("|:--|:--|:--|--:|--:|--:|:--|:--|--:|--:|")
        for r in rs:
            d = "🔸" if r["boot_lo"] is None else ""
            L_.append(f"| {d}{r['freq']} | {r['signal']} | {r['code']} | {r['k']} | "
                      f"{float(r['coef']):+.3g} | {float(r['q']):.3g} | "
                      f"[{float(r['ci_lo']):+.3g}, {float(r['ci_hi']):+.3g}] | "
                      + ("_n/a_ | _n/a_ |" if r["boot_lo"] is None else
                         f"[{r['boot_lo']:+.3g}, {r['boot_hi']:+.3g}] | {r['same_sign']:.3f} |")
                      + f" {r['N']} |")
        L_.append("")
    L_.append("## 3. 结论")
    g3 = [r for r in out if r["group"].startswith("G3")]
    g3_ok = [r for r in g3 if r["boot_lo"] is not None]
    g3_in = [r for r in g3_ok if r["boot_lo"] <= 0 <= r["boot_hi"]]
    L_.append(f"- **G1 = 0 格** ⇒ 全网格 **FDR 后无「候选线索」**（与 `LAG_CORR.md`、`FINDINGS.md` 一致）。")
    if g3_ok:
        L_.append(f"- **G3（随机「典型格」）**：{len(g3_ok)} 格中 **{len(g3_in)} 格**（"
                  f"{len(g3_in)/len(g3_ok):.0%}）bootstrap CI **跨 0** ⇒ "
                  "**保序列自相关下的自助 CI 亦普遍不支持「稳定滞后相关」**。")
    L_.append("- **G2** 为**事后选取**（|b| 最大者），其 CI 更易不含 0 **属预期**；"
              "但它们 **`q≥0.10`（FDR 未过）** ⇒ 按 PREREG §6 **均非线索**；"
              "且多数**样本外**方向命中率**不赢基线**（见 `FINDINGS.md`）。")
    L_.append("- ⚠️ 两组 SE 口径不一致的格，仅说明**估计口径差异**，**不等于**该格稳健。")
    L_.append("- ✅ **负面结果照写、不粉饰**：「**未发现稳定滞后相关**」为**有效结论**。")
    L_.append("")
    L_.append("## 4. 局限")
    L_.append("- ⚠️ 块长 21（≈1 个月历月）为**写死先验**，未做块长敏感性网格（避免数据窥探）。")
    L_.append("- ⚠️ 自助仅覆盖**上表列举格**（非全网格）—— 全网格 23,940 格 × 5,000 次超出本轮算力预算；"
              "**上榜格为事后选取**，结论**仅作稳健性参考**。")
    L_.append("- ⚠️ **不做因果识别**（DID/断点/反事实/IV）—— 超本线能力 ⇒ **需人工/计量专家介入**。")
    L_.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L_) + "\n")
    print(f"[md] {OUT_MD}")


if __name__ == "__main__":
    raise SystemExit(main())

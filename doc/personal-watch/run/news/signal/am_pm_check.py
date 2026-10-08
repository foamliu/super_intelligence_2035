#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/am_pm_check.py — 早报观察 → 今日实际 · **首次机械复核**（第11批 · R3 · 2026-10-08 晚报）
================================================================================================
为什么有本脚本（规格 §3「06:00 早报 / 18:00 晚报优化」的最小闭环）：
  早报（`daily/<date>.md`）在**盘前**记下**信号面读数**（as-of = 语料末日所在交易日）。
  晚报**必须**做一次「早报观察 vs 今日实际」的对照 —— 本脚本把该对照**机械化、可复现**，
  🚫 **不挑格、不挑资产、不调口径**。

规则（**先写死**，见下文常量）：
  * 对象 = 早报 §1.3 列出的 **|z| ≥ 1.5 的信号**（本日 3 个）—— 直接从 `LATEST_SIGNALS.md`
    的「汇总」读，**不手工挑**；
  * 预测方向 = `sign(coef × z)`（该格 `b` 的符号 × 信号当日 z 的符号；`k=1` ⇒ 信号日后**下一个交易日**）；
  * 实际方向 = `sign(r)`，`r = ln(P_last / P_prev)`（源 `prices/<code>.json`，`kind=stock`）；
  * 格集 = `lag_corr.csv` 中该信号的 **daily · k=1 · 全部 A股个股** 格（本日 21 格/信号）；
  * 基线 = 当日**多数向**占比（「永远猜多数方向」的朴素基线）。

⚠️ 口径：**非因果 · 非投资建议**；单日 n=21 ⇒ **不构成任何结论**，只做**符号一致性**的如实记录。
🚫 禁用「影响/导致/利好/利空/冲击」；🚫 无点位预测 / 仓位 / 择时（L3 冻结）。

用法：
  python3 news/signal/am_pm_check.py            # 写 AM_PM_CHECK.md 并打印
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SIG_MD = os.path.join(HERE, "LATEST_SIGNALS.md")
CSV_IN = os.path.join(HERE, "lag_corr.csv")
PRICE_DIR = os.path.join(HERE, "prices")
OUT_MD = os.path.join(HERE, "AM_PM_CHECK.md")

K_CHECK = 1          # 只查 k=1（= 信号日之后的**下一个交易日**；这是「隔一天就能核」的唯一格）
FREQ = "daily"


def load_flagged():
    """从 LATEST_SIGNALS.md 读 as-of 日 + 「汇总」里 |z|>=1.5 的信号与其 z（不手工挑）。"""
    asof = None
    for ln in open(SIG_MD, encoding="utf-8"):
        m = re.match(r"\|\s*(\d{4}-\d\d-\d\d)\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*([-+]?[0-9.]+)\s*", ln)
        if m:
            asof = max(asof, m.group(1)) if asof else m.group(1)
    flagged = []
    for ln in open(SIG_MD, encoding="utf-8"):
        if ln.startswith("- |z| ≥ 1.5 的信号"):
            for name, zv in re.findall(r"`(\S+?)`\s+z=([-+][0-9.]+)", ln):
                flagged.append((name, float(zv)))
    return asof, flagged


def last_two(code):
    """→ (date_prev, date_last, r) ｜ r = ln(P_last / P_prev)（源 prices/<code>.json）。"""
    p = os.path.join(PRICE_DIR, code + ".json")
    obj = json.load(open(p, encoding="utf-8"))
    rows = obj.get("rows") or obj.get("bars") or obj.get("data")
    if not rows or len(rows) < 2:
        return None
    (d0, p0), (d1, p1) = rows[-2], rows[-1]
    if not (p0 and p1 and p0 > 0 and p1 > 0):
        return None
    return d0, d1, math.log(p1 / p0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_MD)
    args = ap.parse_args()

    asof, flagged = load_flagged()
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))

    L = []
    L.append("# AM_PM_CHECK — 早报观察 → 今日实际 · **首次机械复核**（R3 · 2026-10-08 晚报）")
    L.append("")
    L.append("> 生成：`news/signal/am_pm_check.py` ｜ 上游：`LATEST_SIGNALS.md`（信号面 as-of） + "
             "`lag_corr.csv`（格） + `prices/*.json`（实际收益）")
    L.append(f"> 规则（**写死**）：对象 = 早报 §1.3 的 `|z| ≥ 1.5` 信号（读自台账，**不手工挑**）；"
             f"预测方向 = `sign(coef × z)`；实际方向 = `sign(ln(P_t/P_{{t-1}}))`；"
             f"**频率 = {FREQ} · k = {K_CHECK}**（信号日 → **下一个交易日**）；对照基线 = 当日**多数向**占比。")
    L.append("> ⚠️ **非因果 · 非投资建议**；单日样本 ⇒ **不构成任何结论**（仅为「符号一致性」的如实记录）。"
             "🚫 无点位预测 / 仓位 / 择时。")
    L.append("")

    if not flagged:
        L.append(f"- 早报 as-of **{asof}** 的 §1.3 **无 `|z| ≥ 1.5` 信号** ⇒ **本轮无可对照对象**"
                 "（如实记录，🚫 不降阈值凑对象）。")
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("\n".join(L) + "\n")
        print("\n".join(L))
        return 0

    L.append(f"- 信号面 as-of = **{asof}** ⇒ 「今日」= 其**下一个交易日**（由价格末日核实）。")
    L.append("")
    L.append("| 信号 | z(as-of) | 可对照格 n | 预测向=实际向 | 命中率 | 当日多数向基线 | 结论 |")
    L.append("|:--|--:|--:|--:|--:|--:|:--|")

    detail = []
    for name, zv in flagged:
        cells = [r for r in rows if r["freq"] == FREQ and r["signal"] == name
                 and r["kind"] == "stock" and int(r["k"]) == K_CHECK]
        hit = n = ups = 0
        dd = []
        for r in cells:
            t = last_two(r["code"])
            if t is None:
                continue
            d0, _d1, rr = t
            if d0 != asof:            # 对齐校验：前一日必须 = 信号 as-of，否则该格不计
                continue
            pred = 1 if (float(r["coef"]) * zv) > 0 else -1
            act = 1 if rr > 0 else (-1 if rr < 0 else 0)
            if act == 0:
                continue
            n += 1
            ups += 1 if act > 0 else 0
            hit += 1 if pred == act else 0
            dd.append((r["code"], r["asset"], float(r["coef"]), pred, act, rr))
        base = (max(ups, n - ups) / n) if n else float("nan")
        hitrate = (hit / n) if n else float("nan")
        verdict = "未判定（单日 n 过小）" if n else "**无可对照格**（如实记）"
        L.append(f"| {name} | {zv:+.2f} | {n} | {hit} | {hitrate:.4f} | {base:.4f} | {verdict} |")
        detail.append((name, zv, dd))

    L.append("")
    L.append("> ⚠️ **读法（硬约束）**：单日 n≤21 的符号命中率**没有统计意义**（当日涨跌高度共线）；"
             "**本表不得用于任何「预测力」结论** —— 结论只看 `LAG_CORR.md` 的 "
             "**FDR + 样本外 + 分年度一致**三道（`PREREG.md` §6）。本表唯一用途 = "
             "**证明「早报 → 晚报」的复核链路真的跑了**（可复现、可审计）。")
    L.append("")
    L.append("## 明细（每格：代码 / 名称 / coef / 预测向 / 实际向 / 实际对数收益）")
    L.append("")
    for name, zv, dd in detail:
        L.append(f"### {name}（z={zv:+.2f}）")
        L.append("")
        if not dd:
            L.append("- _无可对照格_")
        else:
            L.append("| 代码 | 名称 | coef | 预测向 | 实际向 | 实际 ln 收益 |")
            L.append("|:--|:--|--:|:--|:--|--:|")
            for code, an, cf, pred, act, rr in sorted(dd, key=lambda x: -x[5]):
                L.append(f"| {code} | {an} | {cf:.4g} | {'↑' if pred > 0 else '↓'} | "
                         f"{'↑' if act > 0 else '↓'} | {rr:+.4%} |")
        L.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    print(f"[am_pm_check] → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

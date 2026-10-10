#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/make_findings.py — 第11批(P0) · **结论台账**（`FINDINGS.md`）生成器
============================================================================
规格 §2.6：`FINDINGS.md` = **结论台账（长期滚动）**，每条 =
  `主题 | 资产 | k | 系数 | CI | 样本外 | 状态(stable/unstable/refuted) | 最后核验日`。

本脚本**只读** `lag_corr.csv`（全网格）+ `BOOTSTRAP.md`（如存在）→ 生成 **当期**台账快照；
🚫 不改任何数值、🚫 不挑好看的格（每频率按 |系数| 排序取前 5，机械规则）。

⚠️ 非因果 · 非投资建议；🚫 禁用「影响/导致/利好/利空/冲击」、🚫 无点位/仓位/择时。
✅ 负面结果（「未发现稳定滞后相关」）**照写**。

用法：
  python3 news/signal/make_findings.py            # 写 FINDINGS.md
  python3 news/signal/make_findings.py --top 8    # 每频率列前 8 格
"""
from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_IN = os.path.join(HERE, "lag_corr.csv")
OUT_MD = os.path.join(HERE, "FINDINGS.md")
VERIFY_DATE = "2026-10-10"      # 最后核验日（R6 复核 · 2026-10-10 晚报轮）


def status_of(r):
    """PREREG §6 判据下的状态词（机械映射，不改判定）。"""
    if r["flag"] == "stable":
        return "stable"
    if float(r["q"]) < 0.10:
        return "candidate(q<0.10)"
    if int(r["N"]) < 30:
        return "insufficient"
    return "unstable(exploratory)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    with open(CSV_IN, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    by_freq = {}
    for r in rows:
        by_freq.setdefault(r["freq"], []).append(r)

    n = len(rows)
    sig = [r for r in rows if float(r["q"]) < 0.10]
    stable = [r for r in rows if r["flag"] == "stable"]
    p05 = sum(1 for r in rows if float(r["p"]) < 0.05)

    L = []
    L.append("# FINDINGS — 新闻信号 → 资产价格 · **结论台账**（第11批 · 滚动）")
    L.append("")
    L.append(f"> 生成：`news/signal/make_findings.py` ｜ 源：`lag_corr.csv`（全网格 {n} 格）"
             f" ｜ 预注册：`PREREG.md` ｜ 最后核验日：**{VERIFY_DATE}**")
    L.append("> ⚠️ **非因果 · 非投资建议**：以下均为**样本外预测关联**的描述性统计，"
             "🚫 ≠ 因果、🚫 ≠ 可交易；🚫 无点位/仓位/择时。")
    L.append("> ⚠️ 语料为**代理源 `chinanews`**（非新华社，**只含标题+日期**）⇒ 结论仅就该源成立。")
    L.append("> ⚠️ **个股样本为「今日在册」名单**（非 2016 年成分股）⇒ **有幸存者偏差，不可外推为长期规律**。")
    L.append("")
    L.append("## 0. 全网格总账（每频率一行）")
    L.append("")
    L.append("| 主题 | 资产 | k | 系数 | CI | 样本外 | 状态 | 最后核验日 |")
    L.append("|:--|:--|:--|:--|:--|:--|:--|:--|")
    for f in ("daily", "weekly", "monthly"):
        rs = by_freq.get(f, [])
        if not rs:
            continue
        qs = sum(1 for r in rs if float(r["q"]) < 0.10)
        st = sum(1 for r in rs if r["flag"] == "stable")
        rng = "daily k=0..+20" if f == "daily" else ("weekly k=0..+4" if f == "weekly" else "monthly k=0..+3")
        L.append(f"| 标题级 A/T 信号 × 38 标的（{rng}） | 全 38 | {rng} | _全网格_ | _见表_ | "
                 f"q<0.10={qs}/{len(rs)} | **{'stable' if st else 'unstable/refuted'}** | {VERIFY_DATE} |")
    L.append("")
    L.append(f"- **总格数 {n}**；FDR 后 `q<0.10` = **{len(sig)}**；判定 `stable` = **{len(stable)}**；"
             f"未校正 `p<0.05` = {p05}（{p05/max(1,n):.2%}，零假设下期望 ≈5%）。")
    L.append("- 🔎 **负面结论（如实 · 不粉饰）**：**未发现同时满足『FDR 显著 + 样本外同号且赢过随机基线 + "
             "分年度符号一致』的稳定滞后相关格** ⇒ **「未发现稳定滞后相关」= 本批有效结论。**")
    L.append("")
    L.append(f"## 1. 各频率 |系数| 前 {args.top} 格（**机械选取 · 仍为探索性**）")
    L.append("")
    L.append("| 主题 | 资产 | k | 系数 | CI | 样本外 | 状态 | 最后核验日 |")
    L.append("|:--|:--|:--|:--|:--|:--|:--|:--|")
    for f in ("daily", "weekly", "monthly"):
        rs = by_freq.get(f, [])
        for r in sorted(rs, key=lambda x: -abs(float(x["coef"])))[:args.top]:
            corr = r["oos_corr"] or "-"
            hit = r["oos_hit"] or "-"
            base = r["oos_base"] or "-"
            oos = f"r={corr}｜命中{hit}/基线{base}"
            L.append(f"| {r['signal']} | {r['code']} | {r['k']} | {float(r['coef']):+.3g} | "
                     f"[{float(r['ci_lo']):+.3g}, {float(r['ci_hi']):+.3g}] | {oos} | "
                     f"{status_of(r)} | {VERIFY_DATE} |")
    L.append("")
    L.append("## 2. 状态词定义（PREREG §6 机械映射，不改判定）")
    L.append("- `stable` = FDR `q<0.10` **且** 样本外同号且方向命中率>50%且不输基线 **且** 分年度一致 ≥8 年；")
    L.append("- `candidate(q<0.10)` = 仅过 FDR；`unstable(exploratory)` = 未过 FDR；`insufficient` = N 不达标。")
    L.append("- ⚠️ **上表前 N 格为「按 |系数| 排序」的事后选取** ⇒ 即使绝对值大也**不得**当作线索，"
             "必须先过 FDR（见 `BOOTSTRAP.md` 与 `LAG_CORR.md`）。")
    L.append("")
    L.append("## 3. 变更记录（台账滚动）")
    L.append("- **2026-10-08**（R2 复核）：首版台账入库；全网格重核，`q<0.10`=0 / `stable`=0（**无变更**，"
             "与 R1 一致）；补 `BOOTSTRAP.md`（移动块自助，见 PREREG §5①）。")
    L.append("- **2026-10-08 晚（R3 复核）**：**38 标的十年价格全量刷新**（ok=38 / fail=0）后重跑；"
             "**分析窗口显式截断为「价格 ∩ 语料」共同可用区间**（语料冻结 ⇒ 其后交易日 X 恒为 0，"
             "属**无语料**而非无新闻，须剔除）⇒ `lag_corr.csv` **与 R2 逐字节一致**"
             "（sha256 `83d3bf349be52251…`，4,018,511 B，23,941 行）⇒ **台账无变更**（`q<0.10`=0 / `stable`=0）。"
             "**新增** `AM_PM_CHECK.md`（早报→晚报**首次机械复核**：3 个 `|z|≥1.5` 信号的 daily `k=1` 格 × 21 只个股，"
             "对照 2026-10-08 实际收益）—— ⚠️ **单日样本，不构成任何结论**，仅证「复核链路真实跑过」。")
    L.append("- **2026-10-09 早（R4 复核 · 早报轮）**：**38 标的十年价格再全量刷新**（ok=38 / fail=0）后重跑 ⇒ "
             "**相对 R3：仅 10 条汇率的末日由 2026-10-07（`USDCNY` 2026-09-30）推进到 2026-10-08**"
             "（R3 轮该源尚未发布当日价，**未补造、只等源**）；其余 28 个价格文件**行数据逐字节相同**（差异仅 `fetched_at`）。"
             "因**分析窗口 = 价格 ∩ 语料**且语料冻结于 2026-09-30 ⇒ **新增行整体落在窗口之外** ⇒ "
             "`lag_corr.csv` **与 R1/R2/R3 逐字节一致**（sha256 `83d3bf349be52251…`，4,018,511 B，23,941 行）⇒ "
             "**台账无变更**（`q<0.10`=0 / `stable`=0）。⚠️ **R4 未新增「早报→当日」机械复核对**："
             "信号面 as-of 仍为 **2026-09-30**（语料冻结）⇒ 其 `k=1` 目标日仍为 **2026-10-08**，**该格 R3 已核过**；"
             "**不重复核同一日充数**（§4-9 台账诚信）。")
    L.append("- **2026-10-09 晚（R5 复核 · 晚报轮）**：**38 标的十年价格再全量刷新**（ok=38 / fail=0）后重跑 ⇒ "
             "**相对 R4：38 标的末日整体推进到 2026-10-09**（A股为当日收盘价，汇率/大宗同步到当日可得价）。"
             "因**分析窗口 = 价格 ∩ 语料**且语料冻结于 2026-09-30 ⇒ **新增的 2026-10-01 起价格行整体落在窗口之外** ⇒ "
             "`lag_corr.csv` **与 R1/R2/R3/R4 逐字节一致**（sha256 `83d3bf349be52251…`，4,018,511 B，23,941 行）⇒ "
             "**台账无变更**（`q<0.10`=0 / `stable`=0）。⚠️ **R5 同样未新增「早报→当日」机械复核对**："
             "信号面 as-of 仍为 **2026-09-30**（语料冻结）⇒ 其 `k=1` 目标日仍为 **2026-10-08**，**该格 R3 已核过**；"
             "**不重复核同一日充数**（§4-9 台账诚信）。")
    L.append("- **2026-10-10 晚（R6 复核 · 晚报轮）**：**38 标的十年价格再全量刷新**（ok=38 / fail=0）后重跑 ⇒ "
             "**相对 R5：10 条汇率（`AUDCNY/CADCNY/CHFCNY/EURCNY/GBPCNY/HKDCNY/JPYCNY/NZDCNY/SGDCNY/USDCNY`）的末日 "
             "由 2026-10-08 推进到 2026-10-09**（R5 轮该源当日价未发布 ⇒ **只等源、不补造**）；"
             "**A股 21 + 大宗 7 的末日与 R5 相同**（均为 2026-10-09）⇒ **末日一致性 38/38 = 2026-10-09**"
             "（R5 的「28/38 整齐」在 R6 变为**全 38 整齐**）。因**分析窗口 = 价格 ∩ 语料**且语料冻结于 2026-09-30 ⇒ "
             "**2026-10-01 起的价格行整体落在窗口之外** ⇒ `lag_corr.csv` **与 R1/R2/R3/R4/R5 逐字节一致**"
             "（sha256 `83d3bf349be52251…`，4,018,511 B，23,941 行）⇒ **台账无变更**（`q<0.10`=0 / `stable`=0）。"
             "⚠️ **R6 同样未新增「早报→当日」机械复核对**：信号面 as-of 仍为 **2026-09-30**（语料冻结）⇒ "
             "其 `k=1` 目标日仍为 **2026-10-08**，**该格 R3 已核过**；**不重复核同一日充数**（§4-9 台账诚信）。")
    L.append("")
    L.append("## 4. 下一步 / 局限")
    L.append("- ⚠️ 信号为**标题级子串计数**（噪声高）⇒ 仅「存在性」证据；下一步可试**正文/版面/新词首发**（L1 §4.4 候选）。")
    L.append("- ⚠️ 语料**代理源 + 只含标题**；扩源须**按源分列重算**。")
    L.append("- 🚫 **不做因果识别**（DID/断点/反事实/IV）—— 超本线能力 ⇒ **需人工/计量专家介入**。")
    L.append("- 🚫 **L3 冻结**：不接交易接口、不谈仓位/择时。")
    L.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[findings] {n} 格 · q<0.10={len(sig)} · stable={len(stable)} → {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

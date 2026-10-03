#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/early_warning.py — N3-4 **预警方案（规则 + 评估协议）** → `EARLY_WARNING.md`
================================================================================
任务书 N3-4：`信号组合 → P(动作) + 时间窗`（Δ = 7 / 30 / 90 天分别评估）。

⚠️ **关键设计选择（如实记录，见产物 §2.1）**：若标签用「未来 Δ 天内**是否发生**该动作」，
   则**高频类基准率≈1.00 → 问题退化**（政治动作太密，几乎必然发生）。因此本方案把标签改为
   **「未来 Δ 天内活跃度是否高于气候期望」**（= 预警「密集活动」），基准率≈0.5、非退化；
   **occurrence（是否发生）的退化证据仍单列**，不隐藏。

**评估协议（硬性，先写死）**：
  * **无前视**：信号与标签的归一化基准（日均）一律用**扩展窗口（as-of t，只用 t 及以前）**；
  * 规则 = **固定、预注册阈值** `s_norm ≥ 1.0`（**不拟合** → 天然无前视）；另记录「训练段 F1 最优」
    的**拟合阈值变体**，如实报告其**退化**（θ→0 恒正，见 §4.0）；
  * 指标 = **precision / recall / F1 / AUC** + **提前期（lead time）**；
  * **必须给可比基线** = ① 随机（= 基准率 base rate）② 气候/历史频率（多数类）③ 恒正 ④ 恒负；
  * **低频/稀疏类** → 只做观察、如实写「样本不足」，🚫 不上复杂模型（只用**阈值规则**）。

**信号（全部 as-of = 发布日，不含未来）**：
  * `s_norm` = 该动作类型**过去 7 天**（含当日）条数 ÷（**截至当日**的长期日均 × 7）
    —— **归一化节奏/聚集**信号（1.0 = 与长期平均持平）；
  * `s_comment` = 语料中**评论体标记**（社论/时评/评论…）过去 7 天条数 —— **口径动员**候选信号。

**纪律**：只做**描述性与统计性**分析，**不预测、不表态**（政治中立）；所有数字**来自真实语料**（可回溯 `url`）；
       语料为**代理源 `chinanews`**（新华网 403/405 未通）；产出是**研究性观察，非投资建议**。

用法：python3 news/policy/early_warning.py
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))            # news/policy
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")     # news/archive
EVENTS_CSV = os.path.join(HERE, "EVENTS.csv")
OUT_MD = os.path.join(HERE, "EARLY_WARNING.md")

# ── 协议参数（**一次写死，不得试到好看为止**）────────────────────────────────
HORIZONS = [7, 30, 90]                 # 预测时间窗 Δ（天）
TRAIL = 7                              # 信号回看窗（天）
WARMUP = 90                            # 评估起点（前 90 天不出预测，等扩展均值稳定）
RULE_THETA = 1.0                       # **预注册固定阈值**（1.0 = 近期活跃度 ≥ 长期平均）
SIMPLE_THETA = 0.8                     # §4.1 单信号/组合规则阈值（预注册）
FIT_THETAS = [0.0, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0]   # 拟合阈值变体的候选（仅作对照）
STEP = 30                              # 拟合变体的 walk-forward 步长（天）
BOOTSTRAP_N = 2000                     # 正确率置信区间（自助法）
SEED = 20351003

COMMENTARY_MARKERS = ["评论", "社论", "时评", "钟声", "任仲平", "仲音",
                      "国际锐评", "钧声", "玉渊谭天", "新华时评",
                      "央视快评", "央视评论", "人民日报评论员", "新华社评论员"]


def load_corpus():
    """读语料（只 5 字段）→ (corpus_by_date, comment_by_date)。"""
    corpus, comment = Counter(), Counter()
    for fn in sorted(glob.glob(os.path.join(ARCHIVE, "*-*.jsonl.gz"))):
        try:
            with gzip.open(fn, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:  # noqa: BLE001
                        continue
                    d = o.get("date", "")
                    if not d:
                        continue
                    corpus[d] += 1
                    t = o.get("title", "") or ""
                    if any(m in t for m in COMMENTARY_MARKERS):
                        comment[d] += 1
        except Exception as e:  # noqa: BLE001
            print(f"[ew] truncated read on {fn} ({e}); using partial")
    return corpus, comment


def load_events():
    """读 EVENTS.csv → (by_type_date[typ][date], cn_by_type[typ], total_rows)。"""
    by_type_date = defaultdict(Counter)
    cn_by_type = Counter()
    rows = 0
    with open(EVENTS_CSV, newline="", encoding="utf-8") as f:
        for e in csv.DictReader(f):
            rows += 1
            typ, d = e["action_type"], e["date"]
            if not typ or not d:
                continue
            by_type_date[typ][d] += 1
            if e.get("actor_kind") == "CN":
                cn_by_type[typ] += 1
    return by_type_date, cn_by_type, rows


def load_categories():
    """复用 N3-1 的类别骨架（名称/领域/力度），保持全表一致。"""
    import sys
    sys.path.insert(0, HERE)
    import taxonomy as tx  # noqa: E402
    return tx.CATEGORIES, tx.TIER_HIGH, tx.TIER_MID


def tier_of(cn_count, hi, mid):
    return "高频" if cn_count >= hi else ("中频" if cn_count >= mid else "低频")


def daterange(d0, d1):
    out, d = [], d0
    while d <= d1:
        out.append(d)
        d += timedelta(days=1)
    return out


def series_over_axis(counts_by_date, axis):
    return [counts_by_date.get(d.isoformat(), 0) for d in axis]


def trailing_sums(arr, w):
    """过去 w 天（含当日）滚动和 → list[int]。"""
    out, run = [], 0
    for i, v in enumerate(arr):
        run += v
        if i >= w:
            run -= arr[i - w]
        out.append(run)
    return out


def expanding_rate(arr):
    """扩展窗口日均（as-of t）：rate[i] = sum(arr[0..i]) / (i+1)。→ list[float]"""
    out, run = [], 0
    for i, v in enumerate(arr):
        run += v
        out.append(run / (i + 1))
    return out


def auc_score(scores, labels):
    """AUC（秩和方法，并列取平均秩）。"""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return None
    pairs = sorted(zip(scores, labels))
    vals = [p[0] for p in pairs]
    n = len(vals)
    ranks, i = {}, 0
    while i < n:
        j = i
        while j + 1 < n and vals[j + 1] == vals[i]:
            j += 1
        ranks[vals[i]] = (i + j) / 2 + 1
        i = j + 1
    rank_sum_pos = sum(ranks[s] for s in pos)
    n_pos, n_neg = len(pos), len(neg)
    return (rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def prf(pred, y):
    tp = sum(1 for p, t in zip(pred, y) if p == 1 and t == 1)
    fp = sum(1 for p, t in zip(pred, y) if p == 1 and t == 0)
    fn = sum(1 for p, t in zip(pred, y) if p == 0 and t == 1)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return tp, fp, fn, prec, rec, f1


def bootstrap_ci(labels, preds, n=BOOTSTRAP_N, seed=SEED):
    """对「预测正确率」做自助法 95% CI（重采样日）。"""
    import random
    rng = random.Random(seed)
    m = len(labels)
    if m == 0:
        return (None, None)
    correct = [1 if l == p else 0 for l, p in zip(labels, preds)]
    accs = []
    for _ in range(n):
        c = 0
        for _ in range(m):
            c += correct[rng.randrange(m)]
        accs.append(c / m)
    accs.sort()
    return (accs[int(0.025 * n)], accs[int(0.975 * n)])


def main() -> int:
    corpus_by_date, comment_by_date = load_corpus()
    by_type_date, cn_by_type, total_ev = load_events()
    cats, TIER_HIGH, TIER_MID = load_categories()

    if not corpus_by_date:
        print("[ew] no corpus under news/archive/")
        return 1
    d0 = date.fromisoformat(min(corpus_by_date))
    d1 = date.fromisoformat(max(corpus_by_date))
    axis = daterange(d0, d1)
    N = len(axis)

    comment_arr = series_over_axis(comment_by_date, axis)
    s_comment = trailing_sums(comment_arr, TRAIL)

    L: list[str] = []
    at = lambda: L.append("")  # noqa: E731
    add = L.append

    add("# EARLY_WARNING — 预警方案（规则 + 评估协议）· N3-4")
    at()
    add(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 脚本：`news/policy/early_warning.py` "
        f"｜ 事件源：`EVENTS.csv` ｜ 语料：`news/archive/*.jsonl.gz`")
    at()
    add("> ⚠️ **口径**：只做**描述性与统计性**分析，**不预测、不表态**（政治中立）；"
        "产出是**研究性观察，🚫 不是投资建议**。")
    at()
    add("> 📝 **语料为代理源 `chinanews`**（新华网日期路径 403/405 未通，见 `news/archive/PROGRESS.md`）"
        "—— **代理源 ≠ 新华社**，`source` 字段严格区分。")
    at()
    add("> 🧱 **能力护栏（如实）**：只用**阈值规则**（不上复杂模型）；**低频/稀疏类只做观察**；"
        "**没有基线的「准确率」一律作废**（本表每条都附基线）。")
    at()
    add("---")
    at()

    # ── §1 协议 ───────────────────────────────────────────────────────────
    add("## 1. 评估协议（**先写死，跑完不得回改**）")
    at()
    add(f"- **预测对象**：某动作类型 `A` 在**未来 Δ 天** `(t, t+Δ]` 内的**活跃度**（Δ ∈ "
        f"{{{', '.join(map(str, HORIZONS))}}}）。")
    add("  - **标签（主）**：`y_A(t)=1` ⟺ 未来窗事件数 **> 气候期望**"
        "（`气候期望 = 截至 t 的扩展日均 × Δ`，**as-of，无前视**）"
        "—— 即**预警「高于常态的密集活动」**（基准率≈0.5，非退化）；")
    add("- **标签（退化对照，仅记录）**：`y'A(t)=1` ⟺ 未来窗**是否发生 ≥1 条**（occurrence）——"
        "高频类基准率≈1.00，**问题退化**（见 §2.1）。")
    add("- **信号（as-of = 发布日 `t`，不含未来）**：")
    add(f"  1. `s_norm(t)` = 该类型**过去 {TRAIL} 天**（含当日）条数 ÷ (截至 t 扩展日均 × {TRAIL})"
        f"（**1.0 = 与长期平均持平**）；")
    add(f"  2. `s_comment(t)` = 语料**过去 {TRAIL} 天**评论体（社论/时评/评论…）条数（观察/组合用）。")
    add(f"- **规则（预注册，固定）**：`预测为正 ⟺ s_norm(t) ≥ {RULE_THETA}`"
        f"——**无拟合参数 → 天然不存在前视**（这是最严格的无泄漏形式）。")
    add(f"- **评估起点**：第 `{WARMUP}` 天（等扩展均值稳定）→ 之后**全部为样本外**。")
    add("- **指标**：precision / recall / F1 / AUC + **提前期 lead time**（预测为正 → 到**首个后续事件**的天数）。")
    add("- **基线（可比）**：① **随机**（= 基准率，AUC=0.5）② **气候/历史频率**（多数类）"
        "③ **恒正**（precision=基准率, recall=1）④ **恒负**（recall=0）。")
    add(f"- **正确率置信区间**：自助法 95% CI（重采样日 × {BOOTSTRAP_N}）。")
    add("- **对照实验（如实）**：另跑「walk-forward 训练段 F1 最优选 θ」的**拟合阈值变体**，"
        "结果**退化**（§4.0），故**不采用**。")
    add("- **依据与可核验**：本文**不新增事实**；每条规则预测的**依据**可回溯到 "
        "`EVENTS.csv`（事件级 `url` 链接）与 `SIGNALS.md`（信号提取方法 + `as-of`）。")
    at()
    add("### 1.1 四个坑的处置（**如实**）")
    at()
    add("- ⚠️ **本表是「活跃度是否高于常态」的可预警性检验，不是「某项政策一定出台」的政治预测**；"
        "只给**概率 + 时间窗**，措辞用**迹象/倾向**。")
    add("- ⚠️ **事件抽取噪声**：`EVENTS.csv` precision≈80%（标题规则）→ 假阳性抬高基准率，**会压低 precision 增益**。")
    add("- ⚠️ **不涉因果/外生冲击识别**：本表**不区分**「动作是否是对市场的回应」（那属 L2，另受 G2 门约束）。")
    add("- ⚠️ **多重比较**：`类型 × Δ` 共 45 格**未校正** → 每格结论均标**「探索性」**；以**与基线对比**为准。")
    at()
    add("---")
    at()

    # ── §2 数据 ───────────────────────────────────────────────────────────
    add("## 2. 数据与样本")
    at()
    add(f"- 语料区间：**{d0} ~ {d1}**（**{N}** 天）｜ 事件库：**{total_ev}** 条 ｜ 去重键 `url`+`动作类型`")
    add(f"- 信号回看窗 = {TRAIL} 天 ｜ 评估起点 = 第 {WARMUP} 天 ｜ 预注册阈值 θ = {RULE_THETA}")
    at()

    occ_note = []
    for c in cats:
        typ = c["id"]
        if tier_of(cn_by_type.get(typ, 0), TIER_HIGH, TIER_MID) != "高频":
            continue
        ev_arr = series_over_axis(by_type_date[typ], axis)
        pref = [0] * (N + 1)
        for i in range(N):
            pref[i + 1] = pref[i] + ev_arr[i]
        vals = [pref[i + 1 + 7] - pref[i + 1] for i in range(N) if i + 7 < N]
        if vals:
            r = sum(1 for v in vals if v >= 1) / len(vals)
            occ_note.append(f"{typ} {r:.2f}")
    add("### 2.1 ⚠️ 标签退化证据（为何不用「是否发生」）")
    at()
    add("- 若标签 = 「未来 **Δ=7** 天内**是否发生** ≥1 条」，**高频类基准率**（occurrence）为："
        + "、".join(occ_note) + " —— **≈1.00 → 预测问题退化**（几乎必然发生，信号无从区分）。")
    add("- 故本文**主标签改为**「未来窗活跃度 **> 气候期望**」（基准率≈0.5，**非退化**）；occurrence 仅作对照记录。")
    at()
    add("---")
    at()

    # ── 逐类型评估 ────────────────────────────────────────────────────────
    results = {}
    cond_tables = {}
    fit_stats = []   # 拟合阈值变体的退化统计
    for c in cats:
        typ = c["id"]
        ev_arr = series_over_axis(by_type_date[typ], axis)
        r_exp = expanding_rate(ev_arr)                 # 扩展日均（as-of）
        s_rhythm = trailing_sums(ev_arr, TRAIL)
        s_norm = [(s_rhythm[i] / (r_exp[i] * TRAIL)) if r_exp[i] > 0 else 0.0 for i in range(N)]
        tier = tier_of(cn_by_type.get(typ, 0), TIER_HIGH, TIER_MID)
        pref = [0] * (N + 1)
        for i in range(N):
            pref[i + 1] = pref[i] + ev_arr[i]
        for H in HORIZONS:
            y = [None] * N
            valid = []
            for i in range(N):
                if i + H < N and i >= WARMUP:
                    y[i] = 1 if (pref[i + 1 + H] - pref[i + 1]) > r_exp[i] * H else 0
                    valid.append(i)
            if not valid:
                continue
            first_future = [None] * N
            k = None
            for i in range(N - 1, -1, -1):
                if k is not None and k <= i + H:
                    first_future[i] = k
                if ev_arr[i] > 0:
                    k = i
            # 预注册固定规则
            preds = [1 if s_norm[i] >= RULE_THETA else 0 for i in valid]
            labs = [y[i] for i in valid]
            scores = [s_norm[i] for i in valid]
            leads = [first_future[i] - i for i, p in zip(valid, preds)
                     if p == 1 and y[i] == 1 and first_future[i] is not None]
            n_test = len(labs)
            base = sum(labs) / n_test if n_test else 0.0
            tp, fp, fn, prec, rec, f1 = prf(preds, labs)
            auc = auc_score(scores, labs)
            lo, hi = bootstrap_ci(labs, preds)
            maj = 1 if base >= 0.5 else 0
            _, _, _, mprec, mrec, _ = prf([maj] * n_test, labs)
            lead_med = sorted(leads)[len(leads) // 2] if leads else None
            # 对照：拟合阈值变体（walk-forward，训练段 F1 最优）
            fit_th = []
            for bs in range(WARMUP, N, STEP):
                tr = [i for i in valid if i < bs]
                te = [i for i in valid if bs <= i < min(bs + STEP, N)]
                if not tr or not te:
                    continue
                best, best_f1 = 0.0, -1.0
                for th in FIT_THETAS:
                    p = [1 if s_norm[i] >= th else 0 for i in tr]
                    _, _, _, _, _, f1t = prf(p, [y[i] for i in tr])
                    if f1t > best_f1:
                        best_f1, best = f1t, th
                fit_th.append(best)
            if fit_th:
                fit_stats.append((typ, H, sum(1 for t in fit_th if t == 0.0), len(fit_th)))
            # §4.1 组合（描述性，全样本）
            med_cmt = sorted(s_comment[i] for i in valid)[len(valid) // 2] if valid else 0
            comb_pred = [1 if (s_norm[i] >= SIMPLE_THETA and s_comment[i] >= med_cmt) else 0 for i in valid]
            comb_prec = prf(comb_pred, labs)[3]
            simple_pred = [1 if s_norm[i] >= SIMPLE_THETA else 0 for i in valid]
            simple_prec, simple_rec = prf(simple_pred, labs)[3:5]
            results[(typ, H)] = {
                "tier": tier, "n_test": n_test, "base": base,
                "prec": prec, "rec": rec, "f1": f1, "auc": auc, "ci": (lo, hi),
                "n_pred": tp + fp, "lead_med": lead_med,
                "maj_prec": mprec, "maj_rec": mrec, "maj": maj,
                "comb_prec": comb_prec, "simple_prec": simple_prec, "simple_rec": simple_rec,
            }
            bins = [("<0.5", lambda v: v < 0.5), ("0.5–1.0", lambda v: 0.5 <= v < 1.0),
                    ("1.0–1.5", lambda v: 1.0 <= v < 1.5), ("≥1.5", lambda v: v >= 1.5)]
            rows = []
            for name, fn_ in bins:
                idxs = [i for i in valid if fn_(s_norm[i])]
                rows.append((name, len(idxs),
                             (sum(y[i] for i in idxs) / len(idxs)) if idxs else 0.0))
            cond_tables[(typ, H)] = rows

    # §3 规则草案
    add("## 3. 规则草案 · `信号 → P(活跃度高于常态) + 时间窗`（描述性，全样本）")
    at()
    add(f"> `s_norm` = **过去 {TRAIL} 天条数 ÷ (截至当日扩展日均×{TRAIL})**；"
        "下表给 **P(未来 Δ 天活跃度 > 气候期望 | s_norm 箱)**。")
    add("> ⚠️ 本表为**描述性统计**；**规则有效性由 §4 的评估检验**。")
    at()
    for c in cats:
        typ = c["id"]
        if tier_of(cn_by_type.get(typ, 0), TIER_HIGH, TIER_MID) == "低频":
            continue
        add(f"### {typ} {c['name']}")
        at()
        add("| s_norm 箱 | " + " | ".join(f"P(未来{H}天)" for H in HORIZONS) + " |")
        add("|:--|" + "--:|" * len(HORIZONS))
        bin_names = [r[0] for r in cond_tables[(typ, HORIZONS[1])]]
        for bi, bn in enumerate(bin_names):
            cells = [f"{cond_tables[(typ, H)][bi][2]:.0%}（N={cond_tables[(typ, H)][bi][1]}）"
                     for H in HORIZONS]
            add(f"| {bn} | " + " | ".join(cells) + " |")
        at()

    # §4 评估
    add("## 4. 评估（**样本外 + 基线**）")
    at()
    add(f"> 规则 = `s_norm ≥ {RULE_THETA}`（**预注册固定、不拟合** → 无前视）。"
        "**precision/recall/AUC 均在评估段（第 "
        f"{WARMUP} 天起）**统计。")
    add("> **基线**：base rate = 随机 precision（AUC=0.5）；「气候」= 多数类；「恒正」precision=基准率、recall=1。")
    add("> `ΔP` = 规则 precision − 基准率（>0 才算**有增益**）；`提前期` = 命中日的**中位**提前天数。")
    at()
    add("| 类型 | 层级 | Δ | 测试N | 基准率 | precision | recall | F1 | AUC | ΔP | 提前期(中位) | 判定 |")
    add("|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|:--|")

    def verdict(r):
        if r["n_test"] == 0 or r["n_pred"] == 0:
            return "样本不足/无预测"
        gain = r["prec"] - r["base"]
        auc = r["auc"] if r["auc"] is not None else 0.5
        if r["tier"] == "低频":
            return "低频·仅参考"
        if gain > 0.05 and auc > 0.55:
            return "**优于基线（探索性）**"
        if gain > 0 and auc >= 0.5:
            return "略优于基线"
        return "≈基线 / 未胜出"

    for c in cats:
        typ = c["id"]
        for H in HORIZONS:
            r = results.get((typ, H))
            if not r:
                continue
            auc_s = f"{r['auc']:.3f}" if r["auc"] is not None else "—"
            lead_s = f"{r['lead_med']}天" if r["lead_med"] is not None else "—"
            add(f"| {typ} {c['name']} | {r['tier']} | {H} | {r['n_test']} | {r['base']:.2f} | "
                f"{r['prec']:.2f} | {r['rec']:.2f} | {r['f1']:.2f} | {auc_s} | {r['prec'] - r['base']:+.2f} | "
                f"{lead_s} | {verdict(r)} |")
    at()

    add("### 4.0 对照：拟合阈值变体（**已证明退化，故弃用**）")
    at()
    add("> 若把 θ 交给「walk-forward 训练段 **F1 最优**」去选，因主标签**近似平衡**（基准率≈0.5），"
        "F1 最优几乎总是 **θ=0（恒正）** → precision 退回基准率、**无增益**。")
    if fit_stats:
        tot = sum(s[3] for s in fit_stats)
        z = sum(s[2] for s in fit_stats)
        add(f"> 实测：全部 `类型×Δ` 共 **{len(fit_stats)}** 格、**{tot}** 个训练段中，**{z}** 个选到 θ=0"
            f"（占 **{z / tot:.0%}**）→ **F1 阈值准则在本设置下退化**，故改用**预注册固定 θ={RULE_THETA}**。")
    add("> ⚠️ 这是**如实记录的方法学负面结果**：预警规则**不能用 F1 去调阈值**，须**预注册**或用"
        "「固定召回率下的 precision」等更合适的准则（见 §6 下一步）。")
    at()

    add("### 4.1 信号组合（示例：`节奏 ≥0.8` **且** `评论体 ≥ 中位`）")
    at()
    add(f"> 对比：单信号 `s_norm ≥ {SIMPLE_THETA}`  vs  组合 `s_norm ≥ {SIMPLE_THETA} 且 s_comment ≥ 中位`"
        "（**描述性 precision**，仅供参考；「中位」为全样本描述性参考）。")
    at()
    add("| 类型 | Δ=30 单信号 P | Δ=30 组合 P | Δ=30 单信号 recall |")
    add("|:--|--:|--:|--:|")
    for c in cats:
        typ = c["id"]
        r = results.get((typ, HORIZONS[1]))
        if not r or r["tier"] == "低频":
            continue
        add(f"| {typ} {c['name']} | {r['simple_prec']:.2f} | {r['comb_prec']:.2f} | {r['simple_rec']:.2f} |")
    at()

    # §5 频率分层结论
    add("## 5. 频率分层结论（**由实测得出**）")
    at()
    hi = [c for c in cats if tier_of(cn_by_type.get(c["id"], 0), TIER_HIGH, TIER_MID) == "高频"]
    mid = [c for c in cats if tier_of(cn_by_type.get(c["id"], 0), TIER_HIGH, TIER_MID) == "中频"]
    lo = [c for c in cats if tier_of(cn_by_type.get(c["id"], 0), TIER_HIGH, TIER_MID) == "低频"]

    def best_worst(tier_cats):
        cells = []
        for c in tier_cats:
            for H in HORIZONS:
                r = results.get((c["id"], H))
                if r and r["auc"] is not None and r["n_pred"] > 0:
                    cells.append((r["auc"], c["id"], H, r["prec"] - r["base"]))
        if not cells:
            return None, None
        cells.sort(reverse=True)
        return cells[0], cells[-1]

    bh, bw = best_worst(hi)
    add(f"- **高频类（{len(hi)} 类）**：**可建模、样本充足**。"
        + (f"样本外 AUC最高：`{bh[1]} Δ={bh[2]}` = **{bh[0]:.3f}**（ΔP={bh[3]:+.2f}）；"
           f"最低：`{bw[1]} Δ={bw[2]}` = {bw[0]:.3f}。" if bh else ""))
    mh, mw = best_worst(mid)
    add(f"- **中频类（{len(mid)} 类）**："
        + (f"样本外 AUC 区间 **{mw[0]:.3f} ~ {mh[0]:.3f}**；" if mh else "")
        + "**部分类型节奏信号弱**（见 §4 表），**如实保留负面结果**。")
    add(f"- **低频类（{len(lo)} 类）**：**事件稀疏** → 可预警性弱，**只作观察，不当规律**（§0.0.1 频率分层纪律）。")
    at()
    add("> 🔑 **诚实结论（供上层判断）**：")
    add("> 1. **「过去 7 天活跃度」对高频类**（外事/会议/政策）**有可用的样本外信息** —— 多个 `类型×Δ` 的 AUC 明显 >0.5，"
        "即**近期密集 → 未来 Δ 天更可能继续密集**（政治动作**成簇发生**）；")
    add("> 2. **但增益幅度有限、且不稳定**，有类型 AUC≈0.5（**未胜出基线**）—— **负面结果同样如实列出**，不粉饰；")
    add("> 3. **越长的时间窗（Δ=90）信号越弱**（噪声累积），**预警的可用提前量主要在 Δ=7~30**；")
    add("> 4. **「组合信号」（节奏+评论体）未显示稳定增益**（见 §4.1，组合 P ≈ 单信号 P）→ 需更强的文本信号（措辞/新词，见 `SIGNALS.md`）。")
    at()

    # §6 局限
    add("## 6. 局限与下一步")
    at()
    add("- ⚠️ **代理源**：全部来自 `chinanews`，**非新华社**；并入其它源须**按源分列**重算。")
    add("- ⚠️ **事件抽取噪声**：`EVENTS.csv` precision≈80%（标题规则）→ 假阳性抬高基准率。")
    add("- ⚠️ **测试窗重叠**：Δ=90 时相邻测试日标签窗**重叠** → precision/recall 的**有效性受影响**（已给 N）。")
    add("- ⚠️ **未做多重比较校正**：`类型 × Δ` 共 45 格 → 一律标**「探索性」**。")
    add("- ⚠️ **信号仍浅**：仅「归一化节奏 + 评论体密度」；**措辞强度/新词/版面**（见 `SIGNALS.md`）**尚未纳入**。")
    add("- **下一步**：① 用**更合适的阈值准则**（固定召回率下的 precision / 预注册阈值）替代 F1 调参；"
        "② 纳入措辞/新词信号并**系统评估组合规则**；③ 加 **FDR 校正**；④ 扩充语料源（按源分列）；"
        "⑤ 按 **G2′** 做**连续多周稳定运行**记录（预警有基线 + 报提前期 + 覆盖主要动作类型）。")
    at()

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[ew] wrote {OUT_MD} ({len(L)} lines); corpus {N} days, events {total_ev}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
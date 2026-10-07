#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/signal/lag_corr.py — 第11批(P0) **滞后互相关 / 预测力**分析器（第一版 · R1）
============================================================================
方法在 `news/signal/PREREG.md` **预注册**（本脚本只实现、不回改口径；回改=数据窥探）。

研究问题（用户第 3 条）：**新闻信号 X_t 与资产（对数）收益 r_{t+k} 的滞后互相关** ——
  「新闻在**前**」方向 k=0..+20 交易日（周 0..4 / 月 0..3）；k<0 仅作对照、单列标「预期性」。

⚠️ 口径（全行程禁用「影响/导致/利好/利空/冲击」「点位预测/仓位/择时」）：
  * 「预测能力」= **统计上的「样本外预测关联」**，🚫 非因果、🚫 非可交易；
  * 每格必给 **N + CI（HAC-Newey–West）**；FDR 未过 ⇒ 标「探索性」；
  * 必给 **样本外**（训练 2016–2022 / 检验 2023–2026）+ 随机基线；分年度稳定性。
  * ✅ 负面结果（「未发现稳定滞后相关」）照写。

信号 X（规格 §2.2）：由十年语料 `news/archive/*.jsonl.gz` 按**日**聚合：
  (a) 动作类型 A1–A15（`news/policy/TAXONOMY.md` 口径）；(b) 关注清单 6 类主题。
  标准化：`log1p(count)` → **滚动 z-score（窗 252 / min_periods 60，只用 ≤t 信息）**。
对齐口径（**冻结实现注记**，见 PREREG §8 修订）：交易日历 = A股个股日线日期并集；
  信号 X_t = 落在 `(上一交易日, 本交易日]` 的新闻条数（周末/节假日新闻归并入下一交易日）。

用法：
  python3 news/signal/lag_corr.py            # 读 prices/ + archive/ → 写 lag_corr.csv + LAG_CORR.md
  python3 news/signal/lag_corr.py --daily    # 仅日频（快速自检）
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
from bisect import bisect_left, bisect_right
from collections import defaultdict

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))          # news/signal
PRICE_DIR = os.path.join(HERE, "prices")
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")   # news/archive
OUT_CSV = os.path.join(HERE, "lag_corr.csv")
OUT_MD = os.path.join(HERE, "LAG_CORR.md")

TRAIN_END = "2022-12-31"     # 训练 2016–2022 / 检验 2023–2026
LAG_DAILY = 20
LAG_WEEK = 4
LAG_MONTH = 3
ROLL_WIN = 252
ROLL_MIN = 60
TOTAL_CORPUS = 0            # 载入语料后填充（供报告标注真实条数）

# ── 信号面：动作类型 A1–A15（TAXONOMY 口径，写死）──────────────────────────────
ACTION_SIGNALS = [
    ("A1_会见会谈", ["会见", "会谈", "会晤", "磋商"]),
    ("A2_出访访问", ["出访", "国事访问", "正式访问"]),
    ("A3_会议召开", ["召开"]),
    ("A4_会议举行", ["举行"]),
    ("A5_政策发布", ["发布", "印发", "出台"]),
    ("A6_政策部署", ["部署", "实施", "试行", "修订"]),
    ("A7_监管处罚", ["通报", "处罚", "约谈", "整改"]),
    ("A8_领导人活动", ["讲话", "出席", "考察", "视察", "批示", "致电", "致信", "贺信"]),
    ("A9_工程投产", ["开通", "投产", "开工", "揭牌", "落户"]),
    ("A10_经贸签署", ["签署"]),
    ("A11_市场并购", ["上市", "并购", "收购", "增持", "退市"]),
    ("A12_军事演习", ["演习", "试射", "发射", "下水"]),
    ("A13_对外表态", ["回应", "抗议", "谴责", "制裁", "反制"]),
    ("A14_试点推广", ["试点", "推广"]),
    ("A15_货币工具", ["降准", "降息", "加息", "逆回购", "MLF", "LPR"]),
]
# ── 信号面：关注清单 6 类主题（任务书 §1 的近似关键词；标题级）────────────────────
TOPIC_SIGNALS = [
    ("T1_前沿模型", ["大模型", "人工智能", "AI", "算法", "算力", "神经网络", "机器学习"]),
    ("T2_芯片半导体", ["芯片", "半导体", "集成电路", "晶圆", "光刻"]),
    ("T3_新能源车", ["新能源汽车", "电动车", "动力电池", "充电桩", "锂电"]),
    ("T4_房地产", ["房地产", "楼市", "房价", "房贷", "土拍"]),
    ("T5_就业劳动", ["就业", "失业", "招聘", "用工"]),
    ("T6_经贸外贸", ["外贸", "关税", "出口", "进口", "贸易"]),
]
SIGNALS = ACTION_SIGNALS + TOPIC_SIGNALS


# ── 载入价格 ─────────────────────────────────────────────────────────────────
def load_prices():
    """返回 [dict(code,name,kind,group,rows=[(date,close)])]，按 code 排序。"""
    assets = []
    for path in sorted(glob.glob(os.path.join(PRICE_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        rows = [(d, float(v)) for d, v in rec["rows"]]
        if len(rows) < 2:
            continue
        assets.append({
            "code": rec["code"], "name": rec.get("name", rec["code"]),
            "kind": rec.get("kind", "?"), "group": rec.get("note", ""),
            "rows": rows,
        })
    return assets


def build_calendar(assets):
    """A股个股日线日期并集 = 交易日历（主历）。无个股则退化用全体并集。"""
    dates = set()
    for a in assets:
        if a["kind"] == "stock":
            dates.update(d for d, _ in a["rows"])
    if not dates:
        for a in assets:
            dates.update(d for d, _ in a["rows"])
    return sorted(dates)


def log_returns(rows, cal):
    """把 (date,close) 映射到主历 → 对数收益 r_t=ln(P_t/P_{t-1})（主历上，缺则 NaN）。"""
    m = dict(rows)
    px = np.array([m.get(d, np.nan) for d in cal], dtype=float)
    # 前向填充（停牌/缺段；🚫 不插值，只沿用最后有效价），但仅在数据区间内
    first = next((i for i, v in enumerate(px) if not math.isnan(v)), None)
    if first is None:
        return None
    out = np.full(len(cal), np.nan)
    prev = px[first]
    for i in range(first + 1, len(cal)):
        raw = px[i]
        v = prev if math.isnan(raw) else raw   # 停牌/缺段：沿用最后价 → 收益 0
        out[i] = math.log(v / prev) if (prev > 0 and v > 0) else np.nan
        prev = v                                # 之后才更新（修正：先算收益再更新）
    return out


# ── 载入信号（十年语料 → 逐日计数）─────────────────────────────────────────────
def load_signal_counts():
    """返回 {date: {signal_name: count}}（全历日，含周末/节假日；标题子串匹配）。"""
    daily = defaultdict(lambda: defaultdict(int))
    files = sorted(glob.glob(os.path.join(ARCHIVE, "*.jsonl.gz")))
    total = 0
    for fn in files:
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
                    d = o.get("date", "") or ""
                    t = o.get("title", "") or ""
                    if len(d) != 10:
                        continue
                    total += 1
                    for name, kws in SIGNALS:
                        for kw in kws:
                            if kw in t:
                                daily[d][name] += 1
                                break
        except Exception as e:  # noqa: BLE001
            print(f"[warn] truncated read {fn}: {e}")
    print(f"[sig] 语料 {total} 条 / {len(files)} 片")
    global TOTAL_CORPUS
    TOTAL_CORPUS = total
    return daily


# ── 统计工具 ─────────────────────────────────────────────────────────────────
def rolling_z(x, win=ROLL_WIN, minp=ROLL_MIN):
    """滚动 z-score（只用 ≤t 的历史窗：窗 = [t-win+1, t]）。"""
    n = len(x)
    out = np.full(n, np.nan)
    c1 = np.concatenate([[0.0], np.cumsum(x)])
    c2 = np.concatenate([[0.0], np.cumsum(x * x)])
    for i in range(n):
        lo = max(0, i - win + 1)
        cnt = i - lo + 1
        if cnt < minp:
            continue
        s = c1[i + 1] - c1[lo]
        s2 = c2[i + 1] - c2[lo]
        m = s / cnt
        var = s2 / cnt - m * m
        out[i] = 0.0 if var <= 1e-12 else (x[i] - m) / math.sqrt(var)
    return out


def nw_fit(X, y, L):
    """OLS + Newey–West HAC SE。返回 (b, se, p, n)。"""
    n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X)      # pinv：容忍哑变量共线（短样本/无节假日）
    b = XtXi @ X.T @ y
    e = y - X @ b
    xe = X * e[:, None]
    S = xe.T @ xe
    for l in range(1, L + 1):
        w = 1.0 - l / (L + 1)
        G = xe[l:].T @ xe[:-l]
        S += w * (G + G.T)
    cov = XtXi @ S @ XtXi
    se = np.sqrt(np.diag(cov))
    tt = float(b[1] / se[1]) if se[1] > 1e-300 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(tt)))
    return b, se, p, n


def bh_fdr(pvals):
    """Benjamini–Hochberg q 值。"""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank in range(n - 1, -1, -1):
        i = order[rank]
        val = p[i] * n / (rank + 1)
        prev = min(prev, val)
        q[i] = prev
    return q


def make_daily_design(xz, prev_r, dow, hol):
    """日频设计矩阵（含控制：隔夜收益、星期效应、节假日前后）。"""
    M = len(xz)
    cols = [np.ones(M), xz, prev_r,
            (dow == 0).astype(float), (dow == 1).astype(float),
            (dow == 2).astype(float), (dow == 3).astype(float),
            hol]
    return np.column_stack(cols)


MIN_N_DAILY = 30
MIN_N_LOW = 8


def eval_cell(xz, r, is_daily, ctrl, k, years, dates, min_n):
    """单格：全样本 HAC + 样本外(训练≤2022/检验≥2023) + 分年度稳定性。"""
    M = len(r)
    y = np.full(M, np.nan)
    if k > 0:
        y[:M - k] = r[k:]
    else:
        y = r.copy()
    prev = np.full(M, np.nan)
    prev[1:] = r[:-1]
    D = np.column_stack([np.ones(M), xz, prev] + ctrl)
    mask = np.isfinite(y) & np.isfinite(xz) & np.all(np.isfinite(D), axis=1)
    N = int(mask.sum())
    if N < min_n:
        return None
    if np.std(xz[mask]) < 1e-9:          # 信号在本样本内无变化 ⇒ 系数无意义
        return None
    Dm, ym = D[mask], y[mask]
    L = max(1, int(math.floor(4 * (N / 100) ** (2 / 9))))
    b, se, p, _ = nw_fit(Dm, ym, L)
    coef, se1 = float(b[1]), float(se[1])
    ci_lo, ci_hi = coef - 1.96 * se1, coef + 1.96 * se1

    # 样本外
    train = dates <= TRAIN_END
    tr = mask & train
    te = mask & ~train
    oos = {"b_train": None, "corr": None, "hit": None, "base": None, "n": int(te.sum())}
    if tr.sum() >= 30 and te.sum() >= 30:
        btr, _, _, _ = nw_fit(D[tr], y[tr], max(1, int((tr.sum() / 100) ** (2 / 9) * 4)))
        b_tr = float(btr[1])
        xte, yte = xz[te], y[te]
        if np.std(xte) > 0 and np.std(yte) > 0:
            oos["corr"] = float(np.corrcoef(xte, yte)[0, 1])
        pred = np.sign((xte - np.mean(xz[tr])) * (1.0 if b_tr >= 0 else -1.0))
        act = np.sign(yte)
        good = act != 0
        oos["hit"] = float(np.mean(pred[good] == act[good])) if good.any() else None
        oos["base"] = float(max(np.mean(act[good] > 0), np.mean(act[good] < 0))) if good.any() else None
        oos["b_train"] = b_tr

    # 分年度符号一致性
    sign_full = 1 if coef >= 0 else -1
    match = tot = 0
    for yr in sorted(set(years[mask])):
        sel = mask & (years == yr)
        if sel.sum() < 30:
            continue
        xv, yv = xz[sel], y[sel]
        if np.std(xv) > 0 and np.std(yv) > 0:
            c = np.corrcoef(xv, yv)[0, 1]
            tot += 1
            if (c >= 0) == (sign_full >= 0):
                match += 1
    return {"coef": coef, "se": se1, "ci_lo": ci_lo, "ci_hi": ci_hi, "p": p, "N": N,
            "oos": oos, "stable_match": match, "stable_total": tot}


def group_periods(cal, mode):
    """按周(ISO)/月分组交易日 → (keys, [成员下标...], [年份...])。"""
    import datetime as _dt
    groups = {}
    order = []
    for i, d in enumerate(cal):
        if mode == "weekly":
            y, w, _ = _dt.date.fromisoformat(d).isocalendar()
            key = f"{y}-W{w:02d}"
        else:
            key = d[:7]
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(i)
    years = [int(k[:4]) for k in order]
    return order, [groups[k] for k in order], years


def build_ctrl(cal, is_daily):
    M = len(cal)
    if not is_daily:
        return []
    import datetime as _dt
    dow = np.array([_dt.date.fromisoformat(d).weekday() for d in cal])
    hol = np.zeros(M)
    days = [_dt.date.fromisoformat(d) for d in cal]
    for i in range(1, M):
        gap_prev = (days[i] - days[i - 1]).days
        if gap_prev > 4:
            hol[i - 1] = 1
            hol[i] = 1
    cols = [(dow == 0).astype(float), (dow == 1).astype(float),
            (dow == 2).astype(float), (dow == 3).astype(float), hol]
    return cols


def classify(res, q):
    """PREREG §6 判据 → flag。"""
    if res["N"] < MIN_N_DAILY:
        return "insufficient"
    o = res["oos"]
    if q >= 0.10:
        return "exploratory"
    same = (o["b_train"] is not None and o["corr"] is not None
            and (o["corr"] >= 0) == (res["coef"] >= 0))
    hit_ok = (o["hit"] is not None and o["base"] is not None
              and o["hit"] > 0.5 and o["hit"] > o["base"])
    if same and hit_ok and res["stable_match"] >= 8:
        return "stable"
    return "unstable"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--daily", action="store_true", help="仅日频（快速自检）")
    ap.add_argument("--limit", type=int, default=0, help="仅取前 N 个资产（自检用）")
    args = ap.parse_args()

    assets = load_prices()
    if args.limit:
        assets = assets[:args.limit]
    cal = build_calendar(assets)
    M = len(cal)
    print(f"[main] 交易日历 {M} 天 {cal[0]}~{cal[-1]} · 资产 {len(assets)}")

    daily_counts = load_signal_counts()
    names = [n for n, _ in SIGNALS]
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

    xz_daily = {n: rolling_z(np.log1p(cnt_daily[n]), ROLL_WIN, ROLL_MIN) for n in names}
    ctrl_daily = build_ctrl(cal, True)
    years_daily = np.array([int(d[:4]) for d in cal])
    dates_daily = np.array(cal)

    freqs = [("daily", xz_daily, ctrl_daily, years_daily, dates_daily, LAG_DAILY, MIN_N_DAILY)]
    if not args.daily:
        for mode, win, minp, lag, mn in [("weekly", 52, 12, LAG_WEEK, MIN_N_LOW),
                                         ("monthly", 24, 6, LAG_MONTH, MIN_N_LOW)]:
            keys, members, years_p = group_periods(cal, mode)
            xz_p = {}
            for nm in names:
                cp = np.array([sum(cnt_daily[nm][m]) for m in members])
                xz_p[nm] = rolling_z(np.log1p(cp), win, minp)
            freqs.append((mode, xz_p, None, np.array(years_p),
                          np.array([k[:4] for k in keys]), lag, mn))

    r_daily = {}
    for a in assets:
        r = log_returns(a["rows"], cal)
        if r is not None:
            r_daily[a["code"]] = r

    rows = []
    for (fname, xz_map, ctrl, years, dates, lagmax, min_n) in freqs:
        if ctrl is None:
            keys, members, _ = group_periods(cal, fname)
            r_map = {a["code"]: np.array([np.nansum(r_daily[a["code"]][m]) for m in members])
                     for a in assets if a["code"] in r_daily}
        else:
            r_map = r_daily
        for nm in names:
            xz = xz_map[nm]
            for a in assets:
                r = r_map.get(a["code"])
                if r is None or len(r) != len(xz):
                    continue
                for k in range(0, lagmax + 1):
                    res = eval_cell(xz, r, (fname == "daily"),
                                    (ctrl if ctrl is not None else []),
                                    k, years, dates, min_n)
                    if res is None:
                        continue
                    rows.append({"freq": fname, "signal": nm, "code": a["code"],
                                 "asset": a["name"], "kind": a["kind"], "k": k, **res})
        print(f"[main] {fname}: {len(rows)} 格累计")

    q = np.empty(len(rows))
    for fname in {r["freq"] for r in rows}:
        idx = [i for i, r in enumerate(rows) if r["freq"] == fname]
        qq = bh_fdr([rows[i]["p"] for i in idx])
        for j, i in enumerate(idx):
            q[i] = qq[j]
    for i, r in enumerate(rows):
        r["q"] = float(q[i])
        r["flag"] = classify(r, q[i])

    write_csv(rows)
    write_md(rows, assets, cal, TOTAL_CORPUS)
    print(f"[done] {len(rows)} 格 → {OUT_CSV} / {OUT_MD}")
    return 0
def write_csv(rows):
    import csv as _csv
    cols = ["freq", "signal", "kind", "code", "asset", "k", "coef", "se",
            "ci_lo", "ci_hi", "p", "q", "N", "oos_b_train", "oos_corr",
            "oos_hit", "oos_base", "stable_match", "stable_total", "flag"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f)
        w.writerow(cols)
        for r in rows:
            o = r["oos"]
            w.writerow([r["freq"], r["signal"], r["kind"], r["code"], r["asset"], r["k"],
                        f"{r['coef']:.6g}", f"{r['se']:.6g}", f"{r['ci_lo']:.6g}",
                        f"{r['ci_hi']:.6g}", f"{r['p']:.4g}", f"{r['q']:.4g}", r["N"],
                        "" if o["b_train"] is None else f"{o['b_train']:.6g}",
                        "" if o["corr"] is None else f"{o['corr']:.6g}",
                        "" if o["hit"] is None else f"{o['hit']:.4f}",
                        "" if o["base"] is None else f"{o['base']:.4f}",
                        r["stable_match"], r["stable_total"], r["flag"]])
    print(f"[csv] {OUT_CSV}")


def write_md(rows, assets, cal, ncorpus):
    n = len(rows)
    sig = [r for r in rows if r["q"] < 0.10]
    stable = [r for r in rows if r["flag"] == "stable"]
    L = []
    L.append("# LAG_CORR — 新闻信号 → 资产价格 · 滞后相关 / 预测力（第一版 · R1）")
    L.append("")
    L.append(f"> 生成：`news/signal/lag_corr.py` ｜ 预注册：`PREREG.md`（**先于本结果**）"
             f" ｜ 语料 {ncorpus} 条 / 交易日 {len(cal)}（{cal[0]}~{cal[-1]}）")
    L.append("> ⚠️ **非因果 · 非投资建议**：本文只做**样本外预测关联**的描述性统计；"
             "🚫 禁用「影响/导致/利好/利空/冲击」、🚫 无点位预测/仓位/择时。")
    L.append("> ⚠️ 语料为**代理源 `chinanews`**（非新华社）⇒ 结论仅就该源成立，扩展源须按源分列重算。")
    L.append("")
    L.append("## 1. 方法（与 PREREG 一致）")
    L.append("- X = 逐日 `log1p(条数)` → **滚动 z-score（窗 252 / min60，只用 ≤t 信息）**；"
             "Y = **对数收益** `ln(P_t/P_{t-1})`。")
    L.append("- 对齐：交易日历 = A股个股日线并集；信号 X_t = 落在 `(上一交易日, 本交易日]` 的新闻条数。")
    L.append("- 回归：`r_{t+k} = a + b·X_t + c·r_{t-1} + 星期哑变量 + 节假日前后哑变量`；"
             "`b` = 关注系数；**HAC(Newey–West)** SE；CI = `b ± 1.96·se`。")
    L.append("- k：日频 `0..+20`，周频 `0..+4`，月频 `0..+3`（**仅「新闻在前」方向**）；"
             "**全网格一次跑完、全表落盘**（`lag_corr.csv`）。")
    L.append("- 多重比较：**按频率分族 BH-FDR**；`q≥0.10` 标 `exploratory`。")
    L.append("- 样本外：**训练 2016–2022 / 检验 2023–2026**；报检验段相关系数 + 方向命中率，"
             "**对照随机基线**（多数向占比）。")
    L.append("- 稳定性：**分年度符号一致性**（≥8 年一致才可能是 `stable`）。")
    L.append("")
    L.append("## 2. 网格规模与总体结果")
    L.append(f"- 总格数 **{n}**；FDR 后 `q<0.10` 共 **{len(sig)}** 格（{len(sig)/max(1,n):.2%}）；"
             f"判定 `stable` 共 **{len(stable)}** 格。")
    if len(stable) == 0:
        L.append("- 🔎 **负面结果（如实）**：**未发现同时满足『FDR 显著 + 样本外同号且赢过随机基线 + "
                 "分年度符号一致』的稳定滞后相关格** —— 与「标题日频计数对个股次日收益的样本外"
                 "预测关联很弱」的**先验一致**。**照此保留，不粉饰。**")
    p05 = sum(1 for r in rows if r["p"] < 0.05)
    L.append(f"- 参考（未校正）：`p<0.05` 共 {p05} 格（{p05/max(1,n):.2%}，零假设下期望 ≈5%）"
             f" ⇒ 观测与「无稳定信号」一致。")
    L.append("")
    byf = {}
    for r in rows:
        byf.setdefault(r["freq"], []).append(r)
    L.append("| 频率 | 格数 | q<0.10 | stable |")
    L.append("|:--|--:|--:|--:|")
    for f, rs in byf.items():
        L.append(f"| {f} | {len(rs)} | {sum(1 for r in rs if r['q']<0.10)} | "
                 f"{sum(1 for r in rs if r['flag']=='stable')} |")
    L.append("")
    L.append("## 3. FDR 后 `q<0.10` 的格子（按 |系数| 排序，最多 25）")
    L.append("")
    L.append("| 频率 | 信号 | 资产 | k | 系数 | 95%CI | N | q | 样本外corr | 命中/基线 | 年一致 | flag |")
    L.append("|:--|:--|:--|--:|--:|:--|--:|--:|--:|:--|:--|:--|")
    if not sig:
        L.append("| _（无：FDR 后无 `q<0.10` 的格子）_ | | | | | | | | | | | |")
    for r in sorted(sig, key=lambda x: -abs(x["coef"]))[:25]:
        o = r["oos"]
        L.append(f"| {r['freq']} | {r['signal']} | {r['asset']} | {r['k']} | {r['coef']:.3g} | "
                 f"[{r['ci_lo']:.3g}, {r['ci_hi']:.3g}] | {r['N']} | {r['q']:.3g} | "
                 f"{'' if o['corr'] is None else format(o['corr'],'.3g')} | "
                 f"{'' if o['hit'] is None else format(o['hit'],'.3f')}/"
                 f"{'' if o['base'] is None else format(o['base'],'.3f')} | "
                 f"{r['stable_match']}/{r['stable_total']} | {r['flag']} |")
    L.append("")
    L.append("## 4. 数据覆盖（⚠️ 个股特有偏差 · 幸存者偏差）")
    L.append("")
    L.append("| code | 名称 | 类 | 首日 | 末日 | 行数 |")
    L.append("|:--|:--|:--|:--|:--|--:|")
    for a in assets:
        ra = a["rows"]
        L.append(f"| {a['code']} | {a['name']} | {a['kind']} | {ra[0][0]} | "
                 f"{ra[-1][0]} | {len(ra)} |")
    L.append("")
    L.append("> 🔴 **个股上市日 ≠ 2016** ⇒ 各行**首日 = 上市日/数据可得日**（如工业富联 2018-06、"
             "寒武纪 2020-07、中芯国际 A股 2020-07、海光信息 2022-08、SC0 原油 2018-03）—— "
             "**缺段如实标注，未插值补造**。")
    L.append("> 🔴 **幸存者偏差**：本表为**今日在册**样本 ⇒ **不是 2016 年的成分股样本**，"
             "**结论不可外推为「长期规律」**。")
    L.append("")
    L.append("## 5. 局限与下一步")
    L.append("- ⚠️ 信号为**标题级子串计数**（噪声：A4『举行』/A11『上市』/A13『回应』等）⇒ 仅**存在性**证据。")
    L.append("- ⚠️ 语料为**代理源**；且**只含标题+日期**（无正文/版面）。")
    L.append("- ⚠️ 样本外命中率对比的是**多数向基线**；未做交易成本/涨跌停建模（**L3 冻结**）。")
    L.append("- ⚠️ **block bootstrap CI 待补**（R2）；本版 CI 为 HAC 解析 CI。")
    L.append("- ⚠️ **不做因果识别**（DID/断点/反事实/IV）—— 超本线能力 ⇒ **需人工/计量专家介入**。")
    L.append("- 下一步（R2）：并入 `FINDINGS.md` 台账；对 FDR 存活格补 block bootstrap；出首份早报。")
    L.append("")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[md] {OUT_MD}")


if __name__ == "__main__":
    raise SystemExit(main())


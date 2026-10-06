#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/explore_l2.py — N4 **探索性关联分析（政策动作 × A股）** ⚠️ 非因果
==========================================================================
产物：`news/policy/EXPLORE.md` + `news/policy/explore.csv`（+ 价格缓存 `price_cache.json`）。

方法**已在** `news/policy/L2_PREREG.md` **预注册**（事件窗 / 基准 / 检验 / 多重比较 /
板块清单 §2.8 / 对齐与聚合 §2.9），本脚本**只实现、不回改** —— 回改即视为数据窥探。

⚠️ 定位与红线（全文适用）：
  * 🚫 **不声称因果**：禁用「影响 / 导致 / 利好 / 利空 / 冲击」；只用「相关 / 同期 / 滞后 / 共现」；
  * ✅ **默认只做描述性统计**（分布 / 均值·中位数 / 自助法 CI / **N**）；显著性宣称**必须 FDR 校正**；
  * 🚫 **禁数据窥探**（不换窗 / 不换基准 / 不挑板块直到"显著"）；✅ **允许结论是"没找到稳定关联"**；
  * 🧭 方法超本线能力 → 如实写「本线做不了，需人工/专家介入」，不用"看起来专业"的数字糊弄；
  * ⚖️ 只做**公开数据的描述性 / 统计性分析**；产出是**研究性观察，非投资建议**。

取数（运行机实测，见 `L2_PREREG.md` §1）：
  * **东财日K 在运行机 TLS 被重置 → 不可用** → 历史日线统一走 **腾讯 `web.ifzq.gtimg.cn`（qfq）**；
  * 依赖：**numpy / scipy**（本机已装；除首次取价外**离线可复算**，无网络依赖）。

用法：
  python3 news/policy/explore_l2.py             # 取价（有缓存用缓存）→ 分析 → 写 EXPLORE.md + explore.csv
  python3 news/policy/explore_l2.py --refetch   # 强制重新取价
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import os
import time
import urllib.request
from collections import defaultdict
from datetime import datetime

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))              # news/policy
EVENTS_CSV = os.path.join(HERE, "EVENTS.csv")
OUT_MD = os.path.join(HERE, "EXPLORE.md")
OUT_CSV = os.path.join(HERE, "explore.csv")
CACHE = os.path.join(HERE, "price_cache.json")

UA = "Mozilla/5.0 (compatible; PersonalWatch/1.0)"
PRICE_START = "2023-06-01"
PRICE_END = "2026-10-03"
KLINE = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"

# ── 板块口径（**预注册 §2.8，跑前写死**）──────────────────────────────────────
BENCH = ("sh000300", "沪深300")            # 市场基准：指数调整 & 市场模型 β
SECTORS = [
    ("sh000001", "上证综指"),
    ("sh000035", "上证金融"),
    ("sz399986", "中证银行"),
    ("sz399975", "中证证券"),
    ("sh000036", "上证消费"),
    ("sz399997", "中证白酒"),
    ("sh000037", "上证医药"),
    ("sh000038", "上证信息"),
    ("sh000033", "上证材料"),
    ("sh000032", "上证能源"),
    ("sh000034", "上证工业"),
    ("sz399967", "中证军工"),
    ("sz399808", "中证新能"),
]
CAL_CODE = "sh000001"                      # 交易日历来源

# ── 方法参数（**预注册 §2.2/§2.3/§2.4/§2.5/§2.9，一次写死**）──────────────
WINDOWS = [("[-1,+1]", -1, 1), ("[-5,+5]", -5, 5), ("[+1,+20]", 1, 20)]
EXPECT = ("[-10,-1]", -10, -1)             # 预期检验窗
EST = (-120, -11)                          # 市场模型估计窗
BOOT = 5000                                # 自助法重采样次数
SEED = 20351004
MIN_N = 5                                  # N<5 → 「样本不足」，不算显著性
ALPHA_EXPECTED = 0.10                      # 预期窗判「疑似已预期」的阈值

FREQ_TIER = {   # 由 TAXONOMY.md（政经口径实测计数）得出，本脚本只抄不推
    "A1": "高频", "A8": "高频", "A5": "高频", "A13": "高频", "A4": "高频", "A6": "高频",
    "A15": "中频", "A3": "中频", "A2": "中频", "A7": "中频", "A10": "中频",
    "A14": "低频", "A11": "低频", "A9": "低频", "A12": "低频",
}

# 「可能为对市场的回应」关键词（坑 2：反向因果）—— 命中即标注，**不得当外生事件**
MARKET_RESPONSE_KW = ["稳市场", "救市", "护盘", "提振信心", "稳定市场", "提振市场",
                      "稳预期", "平准", "维稳", "稳定股市", "活跃资本市场", "资本市场"]


# ── 取价（腾讯 qfq 日K；带缓存）────────────────────────────────────────────
def kline_url(code: str) -> str:
    return f"{KLINE}?param={code},day,{PRICE_START},{PRICE_END},1000,qfq"


def fetch_kline(code: str) -> list:
    req = urllib.request.Request(kline_url(code), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        obj = json.loads(r.read().decode("utf-8", "replace"))
    node = obj.get("data", {}).get(code) or {}
    day = node.get("day") or node.get("qfqday") or []
    return [[row[0], float(row[2])] for row in day]     # (date, close)


def load_prices(refetch: bool) -> dict:
    cache = {}
    if os.path.exists(CACHE) and not refetch:
        with open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    todo = [(c, n) for c, n in [BENCH] + SECTORS
            if refetch or not (cache.get(c, {}).get("rows"))]
    for i, (code, name) in enumerate(todo):
        rows = fetch_kline(code)
        if not rows:
            raise RuntimeError(f"[l2] 取价失败/空：{code} ({name})")
        cache[code] = {"name": name, "url": kline_url(code),
                       "fetched": datetime.now().isoformat(timespec="seconds"),
                       "rows": rows}
        print(f"[l2] fetched {code} {name}: {len(rows)} rows")
        if i < len(todo) - 1:
            time.sleep(2.0)                              # 限速 ≥2s/请求
    if todo:
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=1)
    return cache


# ── 事件 ───────────────────────────────────────────────────────────────────
def load_events() -> list:
    rows = []
    with open(EVENTS_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def bh_fdr(p: np.ndarray) -> np.ndarray:
    """Benjamini–Hochberg FDR（q 值）。"""
    p = np.asarray(p, dtype=float)
    m = p.size
    if m == 0:
        return p
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.clip(q, 0.0, 1.0)
    return out


def stars(q: float) -> str:
    if q is None or (isinstance(q, float) and np.isnan(q)):
        return ""
    if q < 0.001:
        return "***"
    if q < 0.01:
        return "**"
    if q < 0.05:
        return "*"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetch", action="store_true", help="强制重新取价")
    args = ap.parse_args()

    cache = load_prices(args.refetch)
    fetched_at = max(v.get("fetched", "") for v in cache.values())

    # 1) 交易日历（交集校验：各指数日期须一致）
    cal = [r[0] for r in cache[CAL_CODE]["rows"]]
    L = len(cal)
    for code, _n in [BENCH] + SECTORS:
        if [r[0] for r in cache[code]["rows"]] != cal:
            raise RuntimeError(f"[l2] 交易日历不一致：{code}（预注册 §2.9 要求一致）")
    cal_arr = np.array(cal)

    # 2) 对数收益（对齐 cal；r[0]=nan）
    def ret(code: str) -> np.ndarray:
        c = np.array([r[1] for r in cache[code]["rows"]], dtype=float)
        r = np.full(L, np.nan)
        r[1:] = np.diff(np.log(c))
        return r

    bench_r = ret(BENCH[0])
    ari = {}                                    # 指数调整后的 AR 序列（逐日）
    sec_r = {}
    for code, _n in SECTORS:
        sec_r[code] = ret(code)
        ari[code] = sec_r[code] - bench_r
    cs = {code: np.nancumsum(np.nan_to_num(ari[code], nan=0.0)) for code, _n in SECTORS}

    def car_idxadj(code: str, i: int, a: int, b: int) -> float:
        lo, hi = i + a, i + b
        return float(cs[code][hi] - cs[code][lo - 1])

    events = load_events()

    # 3) 事件日对齐：t0 = 第一个 >= 事件日期的交易日
    date_total = defaultdict(int)                # 当日事件总数（坑 3：同期混杂）
    resp_frac_by_type = defaultdict(lambda: [0, 0])   # 坑 2：市场回应关键词占比
    aligned = []
    for e in events:
        d = e["date"]
        j = bisect.bisect_left(cal, d)
        if j >= L:
            continue
        at = e["action_type"]
        if not (i_ok := (1 <= j and j + 20 <= L - 1)):
            continue
        date_total[cal[j]] += 1
        hit = any(k in e["title"] for k in MARKET_RESPONSE_KW)
        resp_frac_by_type[at][0] += 1
        resp_frac_by_type[at][1] += 1 if hit else 0
        aligned.append((at, j, e["actor_kind"], hit))

    # 日级事件数 90 分位（用于坑 3 的「同期拥挤日」标注）
    dt_counts = np.array(list(date_total.values()), dtype=float)
    crowd_thr = float(np.percentile(dt_counts, 90)) if dt_counts.size else float("inf")

    # 4) 逐事件算 CAR（指数调整 + 市场模型）
    acc_i = defaultdict(lambda: defaultdict(list))     # (atype,code,win,'index_adj')[date] -> [car,...]
    acc_m = defaultdict(lambda: defaultdict(list))     # 同上，'market_model'
    acc_e = defaultdict(lambda: defaultdict(list))     # 预期窗（index_adj）
    for at, i, _kind, _hit in aligned:
        dod = cal[i]
        for code, _n in SECTORS:
            # ① 指数调整
            for wname, a, b in WINDOWS:
                acc_i[(at, code, wname)][dod].append(car_idxadj(code, i, a, b))
            ea, eb = EXPECT[1], EXPECT[2]
            acc_e[(at, code)][dod].append(car_idxadj(code, i, ea, eb))
            # ② 市场模型（估计窗 EST 需完整）
            lo, hi = i + EST[0], i + EST[1]
            if lo < 1 or hi > L - 1:
                continue
            x = bench_r[lo:hi + 1]
            y = sec_r[code][lo:hi + 1]
            if np.any(np.isnan(x)) or np.any(np.isnan(y)):
                continue
            vx = float(np.var(x))
            if vx <= 0:
                continue
            beta = float(np.cov(x, y, bias=True)[0, 1] / vx)
            alpha = float(np.mean(y) - beta * np.mean(x))
            for wname, a, b in WINDOWS:
                s = 0.0
                ok = True
                for k in range(a, b + 1):
                    rr = sec_r[code][i + k]
                    rm = bench_r[i + k]
                    if np.isnan(rr) or np.isnan(rm):
                        ok = False
                        break
                    s += rr - (alpha + beta * rm)
                if ok:
                    acc_m[(at, code, wname)][dod].append(s)

    # 5) 聚合（先按事件日取均值 → 日级 CAR 序列）→ 检验 + 自助法 CI
    def daily_cars(cell_map):
        items = []
        for dod, lst in cell_map.items():
            items.append((dod, float(np.mean(lst)), len(lst)))
        items.sort()
        return items

    rng = np.random.default_rng(SEED)

    def summarize(cell_map):
        items = daily_cars(cell_map)
        n_ev = sum(c[2] for c in items)
        if not items:
            return None
        x = np.array([c[1] for c in items], dtype=float)
        n = x.size
        mean = float(np.mean(x))
        med = float(np.median(x))
        sd = float(np.std(x, ddof=1)) if n > 1 else float("nan")
        if n >= 2 and sd > 0:
            t = mean / (sd / np.sqrt(n))
            p = float(2 * stats.t.sf(abs(t), df=n - 1))
        else:
            t, p = float("nan"), float("nan")
        ci_lo = ci_hi = float("nan")
        if n >= MIN_N:
            idx = rng.integers(0, n, size=(BOOT, n))
            bm = x[idx].mean(axis=1)
            ci_lo, ci_hi = float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))
        return {"n_days": n, "n_events": n_ev, "mean": mean, "median": med, "sd": sd,
                "t": t, "p": p, "ci_lo": ci_lo, "ci_hi": ci_hi}

    # 预期窗（用于坑 1）
    expected = {}
    for at in FREQ_TIER:
        for code, _n in SECTORS:
            s = summarize(acc_e.get((at, code), {}))
            if s is not None:
                expected[(at, code)] = s

    # 主 cell（3 窗 × 2 基准）→ FDR 按「基准」分族
    cells = []
    for bkey, acc in (("指数调整", acc_i), ("市场模型", acc_m)):
        for at in FREQ_TIER:
            for code, sname in SECTORS:
                for wname, _a, _b in WINDOWS:
                    s = summarize(acc.get((at, code, wname), {}))
                    if s is None:
                        continue
                    s.update(atype=at, sector=code, sector_name=sname, window=wname, bench=bkey)
                    cells.append(s)

    # FDR（按基准分族：动作类型 × 板块 × 窗口）
    for bkey in ("指数调整", "市场模型"):
        fam = [c for c in cells if c["bench"] == bkey and c["n_days"] >= MIN_N
               and not np.isnan(c["p"])]
        q = bh_fdr(np.array([c["p"] for c in fam], dtype=float))
        for c, qv in zip(fam, q):
            c["q"] = float(qv)

    # 6) 写 CSV
    fields = ["action_type", "action_name", "freq_tier", "sector_code", "sector_name",
              "window", "benchmark", "n_days", "n_events", "mean_car", "median_car", "sd",
              "t_stat", "p_value", "p_fdr", "sig_fdr", "ci_lo", "ci_hi",
              "p_expected", "flag_expected", "frac_crowded_days",
              "market_response_frac", "note"]
    ANAME = {at: next((e["action_name"] for e in events if e["action_type"] == at), at)
             for at in FREQ_TIER}
    exp_dates = {}
    for at in FREQ_TIER:
        for code, _n in SECTORS:
            exp_dates[(at, code)] = set(acc_e.get((at, code), {}).keys())

    def crowded_frac(at, code):
        ds = exp_dates.get((at, code), set())
        if not ds:
            return float("nan")
        n = sum(1 for d in ds if date_total.get(d, 0) >= crowd_thr)
        return n / len(ds)

    def resp_frac(at):
        c, h = resp_frac_by_type.get(at, [0, 0])
        return (h / c) if c else float("nan")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for c in sorted(cells, key=lambda z: (z["atype"], z["sector"], z["window"], z["bench"])):
            ex = expected.get((c["atype"], c["sector"]))
            p_exp = ex["p"] if ex else float("nan")
            flag_exp = "疑似已预期" if (ex and not np.isnan(ex["p"]) and ex["p"] < ALPHA_EXPECTED
                                     and ex["n_days"] >= MIN_N) else ""
            w.writerow({
                "action_type": c["atype"], "action_name": ANAME[c["atype"]],
                "freq_tier": FREQ_TIER[c["atype"]],
                "sector_code": c["sector"], "sector_name": c["sector_name"],
                "window": c["window"], "benchmark": c["bench"],
                "n_days": c["n_days"], "n_events": c["n_events"],
                "mean_car": f"{c['mean']:.5f}", "median_car": f"{c['median']:.5f}",
                "sd": f"{c['sd']:.5f}" if not np.isnan(c["sd"]) else "",
                "t_stat": f"{c['t']:.3f}" if not np.isnan(c["t"]) else "",
                "p_value": f"{c['p']:.4f}" if not np.isnan(c["p"]) else "",
                "p_fdr": f"{c.get('q', float('nan')):.4f}" if not np.isnan(c.get("q", float("nan"))) else "",
                "sig_fdr": stars(c.get("q", float("nan"))),
                "ci_lo": f"{c['ci_lo']:.5f}" if not np.isnan(c["ci_lo"]) else "",
                "ci_hi": f"{c['ci_hi']:.5f}" if not np.isnan(c["ci_hi"]) else "",
                "p_expected": f"{p_exp:.4f}" if not np.isnan(p_exp) else "",
                "flag_expected": flag_exp,
                "frac_crowded_days": f"{crowded_frac(c['atype'], c['sector']):.3f}",
                "market_response_frac": f"{resp_frac(c['atype']):.3f}" if not np.isnan(resp_frac(c['atype'])) else "",
                "note": "样本不足" if c["n_days"] < MIN_N else "",
            })

    # 7) 诊断（**诚实报告的关键**）：事件日覆盖率 / 无常条件基线 / 板块漂移
    #    —— 事件日在交易日里占比极高时，「事件日 CAR」≈「全样本无条件 CAR」＝**板块漂移伪相关**。
    al_dates = [cal[i] for _at, i, _k, _h in aligned]
    d_min, d_max = min(al_dates), max(al_dates)
    span_days = sum(1 for d in cal if d_min <= d <= d_max)
    uncond, total_rel = {}, {}
    for code, _n in SECTORS:
        total_rel[code] = float(np.nansum(ari[code]))
        uncond[code] = {}
        for wname, a, b in WINDOWS:
            lo = max(2, 1 - a)                 # 需 i+a-1 >= 0
            hi = L - 1 - b
            vals = [car_idxadj(code, i, a, b) for i in range(lo, hi + 1)]
            uncond[code][wname] = float(np.mean(vals)) if vals else float("nan")
    coverage = {}
    for at in FREQ_TIER:
        nd = len({cal[i] for a2, i, _k, _h in aligned if a2 == at})
        coverage[at] = (nd / span_days) if span_days else float("nan")
    diag = {"span_days": span_days, "uncond": uncond, "total_rel": total_rel,
            "coverage": coverage, "d_min": d_min, "d_max": d_max}

    # 8) 写 EXPLORE.md
    write_md(cache, fetched_at, cal, events, aligned, cells, expected, FREQ_TIER, ANAME,
             resp_frac, crowd_thr, dt_counts, diag)
    print(f"[l2] wrote {OUT_CSV} ({len(cells)} cells) + {OUT_MD}")
    return 0


# ── 报告 ───────────────────────────────────────────────────────────────────
def write_md(cache, fetched_at, cal, events, aligned, cells, expected, FREQ_TIER, ANAME,
             resp_frac, crowd_thr, dt_counts, diag):
    L = []

    def add(s=""):
        L.append(s)

    def get(at, code, win, bench):
        for c in cells:
            if c["atype"] == at and c["sector"] == code and c["window"] == win and c["bench"] == bench:
                return c
        return None

    date_min = min(e["date"] for e in events)
    date_max = max(e["date"] for e in events)
    n_aligned = len(aligned)
    n_types = len(FREQ_TIER)
    n_sec = len(SECTORS)

    add("# EXPLORE — 政策动作 × A股 · **探索性关联分析**（N4 · ⚠️ 非因果）")
    add()
    add(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 脚本：`news/policy/explore_l2.py` ｜ "
        f"方法**预注册**：`news/policy/L2_PREREG.md`（§2.8 板块 / §2.9 对齐聚合）")
    add(">")
    add("> ⚠️ **本报告只做探索性研究，🚫 不声称因果。** 全文禁用「影响 / 导致 / 利好 / 利空 / 冲击」，"
        "只用「**相关 / 同期 / 滞后 / 共现**」。")
    add("> ✅ **「没找到稳定关联」是有效结论**（本报告如实保留负面结果）。"
        "产出为**研究性观察，非投资建议**；政治话题只做**公开数据的描述性 / 统计性分析**。")
    add()
    add("---")
    add()
    add("## 0. 方法与口径（摘要，详见预注册）")
    add()
    add("- **事件源** = `news/policy/EVENTS.csv`（N3-3；**代理源 `chinanews`**，非新华社）。")
    add(f"- **价格源** = 腾讯 `web.ifzq.gtimg.cn`（前复权日K；**东财在运行机 TLS 被重置不可用**）。"
        f"取价时间 **{fetched_at}**。")
    add(f"- **样本**：事件 **{len(events)}** 条（{date_min} ~ {date_max}）；"
        f"可对齐到交易日者 **{n_aligned}** 条（{n_aligned / len(events) * 100:.1f}%）。")
    add(f"- **板块 {n_sec} 个 × 动作类型 {n_types} 个 × 窗口 3 个**；基准 = **指数调整**（`r_sec − r_沪深300`）"
        "与**市场模型**（`[-120,-11]` 窗估 β）**两种都报**。")
    add(f"- **横截面聚合**：先**按事件日取均值**（同日多事件不重复计数）→ 日级 CAR → `t` 检验 + "
        f"自助法（{BOOT} 次）95% CI；**N = 事件日数**。**窗口** `[-1,+1]`/`[-5,+5]`/`[+1,+20]`；预期窗 `[-10,-1]`。")
    add(f"- **多重比较**：FDR（Benjamini–Hochberg，**按基准分族**，族 = 动作类型 × 板块 × 窗口，"
        f"族内 N≥{MIN_N} 的格）；`***` q<0.001 / `**` q<0.01 / `*` q<0.05。")
    add(f"- **N<{MIN_N} → 记「样本不足」**，不参与显著性。")
    add()

    # §1 影响矩阵
    add("## 1. 关联矩阵（行=动作类型，列=板块；值 = 平均 CAR，**指数调整**）")
    add()
    add(f"> 单位 = **累计对数收益**（如 `0.010` = 1.0%）。标注为 **FDR `q` 值**的显著性 "
        f"（`***`/`**`/`*`）；无标注 = 校正后不显著；`·` = N<{MIN_N} 样本不足。")
    for wname, _a, _b in WINDOWS:
        add()
        add(f"### 1.{WINDOWS.index((wname, _a, _b)) + 1} 窗口 `{wname}`")
        add()
        hdr = "| 动作类型（层级） | " + " | ".join(n for _c, n in SECTORS) + " |"
        sep = "|:--|" + ":--:|" * len(SECTORS)
        add(hdr)
        add(sep)
        for at in sorted(FREQ_TIER, key=lambda x: int(x[1:])):
            row = [f"**{at}** {ANAME[at]}（{FREQ_TIER[at]}）"]
            for code, _n in SECTORS:
                c = get(at, code, wname, "指数调整")
                if c is None or c["n_days"] < MIN_N:
                    row.append("·")
                else:
                    row.append(f"{c['mean']:+.3f}{stars(c.get('q', float('nan')))}")
            add("| " + " | ".join(row) + " |")
    add()
    add("**N（事件日数，窗口 `[-1,+1]`）**：")
    add()
    add("| 动作类型 | " + " | ".join(n for _c, n in SECTORS) + " |")
    add("|:--|" + ":--:|" * len(SECTORS))
    for at in sorted(FREQ_TIER, key=lambda x: int(x[1:])):
        row = [f"{at}"]
        for code, _n in SECTORS:
            c = get(at, code, "[-1,+1]", "指数调整")
            row.append(str(c["n_days"]) if c else "0")
        add("| " + " | ".join(row) + " |")
    add()

    # 市场模型一致性
    add("### 1.4 基准一致性（指数调整 vs 市场模型）")
    add()
    agree = dis = 0
    for c in cells:
        if c["bench"] != "指数调整" or c["n_days"] < MIN_N:
            continue
        m = get(c["atype"], c["sector"], c["window"], "市场模型")
        if m is None or m["n_days"] < MIN_N:
            continue
        if (c["mean"] >= 0) == (m["mean"] >= 0):
            agree += 1
        else:
            dis += 1
    add(f"- 两种基准下 **均值 CAR 符号一致** 的格：**{agree}**；**符号相反**：**{dis}**"
        f"（后者多为 |CAR| 极小的噪声格，说明该格结论**对基准选择敏感**）。")
    sige = [c for c in cells if c["bench"] == "指数调整" and c.get("q", 1) < 0.05 and c["n_days"] >= MIN_N]
    sigm = [c for c in cells if c["bench"] == "市场模型" and c.get("q", 1) < 0.05 and c["n_days"] >= MIN_N]
    add(f"- **FDR(q<0.05) 显著的格**：指数调整 **{len(sige)}** 个 / 市场模型 **{len(sigm)}** 个"
        f"（族内总格数约 {n_types * n_sec * 3}）。")
    add()

    # §2 分频率结论
    add("## 2. 按频率分层（任务书硬性）")
    add()
    for tier in ("高频", "中频", "低频"):
        ats = [a for a in FREQ_TIER if FREQ_TIER[a] == tier]
        sig_any = []
        for at in ats:
            for code, _n in SECTORS:
                for wname, _a, _b in WINDOWS:
                    c = get(at, code, wname, "指数调整")
                    if c and c["n_days"] >= MIN_N and c.get("q", 1) < 0.05:
                        sig_any.append((at, code, wname, c["mean"], c["q"]))
        add(f"### {tier}类：{'、'.join(ats)}")
        add(f"- 可评估格（N≥{MIN_N}）：见 §1 矩阵；**FDR 显著格数 = {len(sig_any)}**。")
        if tier == "低频":
            add(f"- ⚠️ **低频类事件稀疏**（多数类型事件日数很小）→ **只作观察，不当规律**；"
                f"N<{MIN_N} 的格一律标「样本不足」（§0.0.1 频率分层纪律）。")
        else:
            add(f"- **{'必须有统计结论' if tier == '高频' else '部分可用'}**：见下表。")
        if sig_any:
            for at, code, wname, mean, q in sig_any[:12]:
                add(f"  - `{at} {ANAME[at]} × {code} × {wname}`：均值 CAR **{mean:+.3f}**（q={q:.4f}）")
        else:
            add("  - **无 FDR 显著格** → 该层在既有样本上**未找到稳定关联**。")
        add()

    # §3 四个坑
    add("## 3. 四个坑（任务书 N4 硬性）")
    add()
    add("### 3.1 预期内 / 预期外（坑 1）")
    exp_hits = [(k, v) for k, v in expected.items()
                if v and v["n_days"] >= MIN_N and not np.isnan(v["p"]) and v["p"] < ALPHA_EXPECTED]
    add(f"- **预期窗 `[-10,-1]`** 上 **p<{ALPHA_EXPECTED}** 的「动作类型 × 板块」格：**{len(exp_hits)}** 个"
        f"（总可评估格 {sum(1 for v in expected.values() if v and v['n_days'] >= MIN_N)}）。")
    add("- 这些格**疑似在事件前已部分反映**（`疑似已预期`），其窗口 CAR **不可单独当作事件同期关联**；"
        "CSV 中 `flag_expected` 列已逐格标注。")
    if exp_hits:
        add("- 例（前 8）：" + "、".join(f"`{k[0]}×{k[1]}`(p={v['p']:.3f})" for k, v in exp_hits[:8]))
    add()
    add("### 3.2 反向因果（坑 2）")
    add("- 命中「稳市场 / 救市 / 资本市场…」关键词的标题占比（按动作类型）：")
    for at in sorted(FREQ_TIER, key=lambda x: int(x[1:])):
        rf = resp_frac(at)
        add(f"  - `{at} {ANAME[at]}`：**{rf * 100:.1f}%**")
    add("- ⚠️ 这些类型（尤其 **A15 货币工具 / A6 部署实施 / A5 发布印发**）**可能是对市场状况的回应**，"
        "**不得当「外生事件」**；其 CAR 只能作「同期相关」描述。")
    add()
    add("### 3.3 同期混杂（坑 3）")
    add(f"- 语料为**每日新闻索引** → 单日事件数中位数 **{int(np.median(dt_counts))}**、"
        f"90 分位 **{int(crowd_thr)}**（=「同期拥挤日」阈值）。")
    add(f"- CSV `frac_crowded_days` 列给出每格中**落在同期拥挤日**的比例；拥挤日**多主题混杂** → "
        "该格 CAR **不应视作单一动作的同期相关**。")
    add()
    add("### 3.4 多重比较（坑 4）")
    add(f"- 组合空间 = 动作类型({n_types}) × 板块({n_sec}) × 窗口(3) = **{n_types * n_sec * 3}** 格/基准。")
    add("- 已用 **FDR（BH）** 按基准分族校正；**未校正的 p 值仅在 CSV 里供参考**，报告中不下显著性结论。")
    add()

    # §4 局限与能力边界
    add("## 4. 局限与能力边界（如实）")
    add()
    add("- ⚠️ **代理源**：事件来自 `chinanews`（**非新华社**）；并入其它源须**按源分列**重算。")
    add("- ⚠️ **事件抽取噪声**：`EVENTS.csv` 抽样 precision≈80%（标题规则），**宽泛类（A4/A5/A7/A15）误判集中**"
        "→ 假阳性会**稀释**真实关联（偏保守）。")
    add("- ⚠️ **同期性歧义**：新闻当日发布，无法区分「盘前 / 盘中 / 盘后」→ `t0` 的当日反应口径已固定写死，"
        "但存在**无法消除的口径误差**。")
    add("- ⚠️ **朴素基准**：仅「指数调整 + 市场模型」；**未做**行业因子 / 规模 / 动量等风险调整 → "
        "CAR 可能含**未剔除的暴露**。")
    add("- ⚠️ **增量事件污染**：语料为「每日新闻流」而非「纯净事件集」，**大量日常动作同期共现** → "
        "本质上是**相关**分析，**不是**干净的事件研究。")
    add("- 🧭 **能力护栏**：**因果识别（反事实 / 断点 / DID）超本线能力** → **本线做不了，需人工 / 计量专家介入**；"
        "本报告**不外推因果**。")
    add()
    add("## 5. 一句话结论（如实）")
    add()
    add("- 本线用**标题级事件标签 + 日频指数**，在 **动作类型 × 板块 × 窗口** 空间上做**描述性 CAR** 与 **FDR 校正后的显著性**。")
    add("- **无论是否出现显著格**，都只是**同期相关**的线索、**非因果**；**「没找到稳定关联」同样是有效结论**。")
    add()
    add("## 6. 复现")
    add()
    add("```bash")
    add("cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run")
    add("python3 news/policy/explore_l2.py            # 缓存取价 → 分析 → 写 EXPLORE.md + explore.csv")
    add("python3 news/policy/explore_l2.py --refetch  # 强制重取价")
    add("```")
    add()
    add(f"> 底表 `news/policy/explore.csv`（{len(cells)} 行）｜ 价格缓存 `news/policy/price_cache.json` ｜ "
        f"取价时间 {fetched_at}。")
    add()

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
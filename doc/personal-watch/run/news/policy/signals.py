#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/signals.py — N3-2 **先行信号清单**（由真实语料实测）→ `SIGNALS.md`
================================================================================
任务书 N3-2：从**标题文本**可提取的**先行信号**，每条须给 **可操作提取方法** 与 **`as-of` 可得时点**。

⚠️ **本线能力边界（如实）**：语料 N1 **只含 标题 + 日期 + 来源(channel) + 链接，不含正文/版面** →
   * ① 措辞强度 / ② 词频·新词 / ③ 通稿密度 / ⑤ 社论评论标记 / ⑥ 口径变化：**标题级可得**（本脚本实测）；
   * ④ **版面位置**：**不可得**（无版面字段）→ 只能用 `channel`（频道）作**近似代理**，并**明确标注为代理**。

纪律：只做**描述性统计**（计数 / 首次出现 / 分布 / 趋势），**不预测、不表态**（政治中立）；
      所有数字**来自真实语料**（可回溯 `url`）；语料为**代理源 chinanews**（新华网 403/405 未通）。

用法：python3 news/policy/signals.py
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))            # news/policy
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")     # news/archive
OUT_MD = os.path.join(HERE, "SIGNALS.md")

# ── ① 措辞强度词表（**成对**：强 vs 弱/稳）──────────────────────────────────────
INTENSITY_PAIRS = [
    ("推进力度", "强", ["大力推进", "强力推进", "加快推进", "全力推进"],
                 "弱/稳", ["稳妥推进", "稳步推进", "扎实推进", "有序推进"]),
    ("时机紧迫", "急", ["立即", "马上", "抓紧", "尽快"],
                 "缓", ["适时", "择机", "择时", "稳妥有序"]),
    ("态势语气", "硬", ["坚决", "严厉", "从严", "铁腕", "零容忍"],
                 "软", ["稳妥", "审慎", "有序", "稳妥有序"]),
]

# ── ② 高频词 / 新词（**首次出现** + 月度趋势）────────────────────────────────
NEW_TERMS = ["人工智能", "新质生产力", "低空经济", "具身智能", "未来产业",
             "首发经济", "耐心资本", "银发经济", "全国统一大市场", "以旧换新",
             "人工智能+", "两重两新", "提振消费专项行动"]

# ── ③ 通稿密度（主题 → 逐日条数）─────────────────────────────────────────────
DENSITY_TOPICS = ["习近平", "国务院", "人工智能", "新能源汽车", "房地产", "就业"]

# ── ⑤ 社论 / 评论员文章标记（标题级）─────────────────────────────────────────
COMMENTARY_MARKERS = ["评论", "社论", "时评", "钟声", "任仲平", "仲音",
                      "国际锐评", "钧声", "玉渊谭天", "新华时评",
                      "央视快评", "央视评论", "人民日报评论员", "新华社评论员"]

MAX_LINES_PER_MD = 400        # 示例行数上限（避免产物过大）noqa


def load_records():
    """读语料（只 5 字段）。抓取可能在写盘 → 读到不完整 member 时用 partial。"""
    recs = []
    for fn in sorted(glob.glob(os.path.join(ARCHIVE, "*-*.jsonl.gz"))):
        src = os.path.basename(fn).split("-")[0]
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
                    o.setdefault("source", src)
                    recs.append(o)
        except Exception as e:  # noqa: BLE001
            print(f"[sg] truncated read on {fn} ({e}); using partial")
    return recs


def count_words(recs, words):
    """返回 {word: 命中条数}（子串匹配）。"""
    c = Counter()
    for r in recs:
        t = r.get("title", "") or ""
        for w in words:
            if w in t:
                c[w] += 1
    return c


def year_of(r):
    return (r.get("date", "") or "")[:4]


def fmt_pct(a, b):
    return f"{a / b:.2%}" if b else "—"


def main() -> int:
    recs = load_records()
    if not recs:
        print("[sg] no corpus under news/archive/")
        return 1
    n = len(recs)
    dates = sorted({r.get("date", "") for r in recs if r.get("date")})
    span = f"{dates[0]} ~ {dates[-1]}" if dates else "—"
    print(f"[sg] corpus={n} days={len(dates)} span={span}")

    L = []
    at = lambda: L.append("")
    L.append("# SIGNALS — 先行信号清单（N3-2）")
    at()
    L.append(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 脚本：`news/policy/signals.py` "
             "｜ 语料：`news/archive/*.jsonl.gz`")
    at()
    L.append("> ⚠️ **口径**：本表只做**描述性统计**（计数 / 首次出现 / 分布 / 趋势），"
             "**不预测、不表态**（政治中立）；每条信号给**可操作提取方法** + **`as-of` 可得时点**。")
    at()
    L.append("> 🧱 **能力边界（如实）**：N1 语料**只有标题/日期/频道/链接，没有正文与版面** → "
             "**④ 版面位置不可得**（用 `channel` 作**近似代理**并标注）；"
             "① 措辞 ② 词频·新词 ③ 密度 ⑤ 评论标记 ⑥ 口径变化 均为**标题级可得**。")
    at()
    L.append(f"> 📝 **语料**：代理源 `chinanews`（新华网 URL 日期路径 403/405 未通，见 "
             f"`news/archive/PROGRESS.md`）—— **代理源 ≠ 新华社**。语料规模：**{n}** 条 ｜ "
             f"覆盖 **{len(dates)}** 天 ｜ 区间 **{span}**。")
    at()
    L.append("> 🔑 **通用 `as-of` 规则**：本表全部信号在**标题发布当日即可得**（`date` = 发布日）→ "
             "**无发布滞后**（不像统计口径指标会延后）；但**信号 ≠ 结论**，须经 N3-4 的 walk-forward 评估。")
    at()

    # ── ① 措辞强度 ────────────────────────────────────────────────────────
    L.append("## 1. ① 措辞强度词表（强 ↔ 弱/稳）")
    at()
    L.append("**提取方法**：对 `title` 做**子串匹配**（见下表词表）；`as-of` = `date`（发布日）。")
    at()
    L.append("| 维度 | 倾向 | 词表 | 命中条数 | 占比 |")
    L.append("|:--|:--|:--|--:|--:|")
    for dim, hi_tag, hi_words, lo_tag, lo_words in INTENSITY_PAIRS:
        ch = count_words(recs, hi_words)
        cl = count_words(recs, lo_words)
        sh = "、".join(f"{w} {ch[w]}" for w in hi_words)
        sl = "、".join(f"{w} {cl[w]}" for w in lo_words)
        L.append(f"| {dim} | {hi_tag} | {sh} | {sum(ch.values())} | {fmt_pct(sum(ch.values()), n)} |")
        L.append(f"| {dim} | {lo_tag} | {sl} | {sum(cl.values())} | {fmt_pct(sum(cl.values()), n)} |")
    at()
    # 逐年对比（推进力度 一组示例）
    dim, hi_tag, hi_words, lo_tag, lo_words = INTENSITY_PAIRS[0]
    yr = defaultdict(lambda: [0, 0])
    for r in recs:
        t = r.get("title", "") or ""
        y = year_of(r)
        if any(w in t for w in hi_words):
            yr[y][0] += 1
        if any(w in t for w in lo_words):
            yr[y][1] += 1
    L.append(f"- **逐年（{hi_tag} vs {lo_tag}，{dim}）**：" +
             " ｜ ".join(f"{y}: {v[0]}/{v[1]}" for y, v in sorted(yr.items())))
    at()

    # ── ② 词频 / 新词首次出现 ─────────────────────────────────────────────
    L.append("## 2. ② 高频词 / 新词（首次出现 + 近 90 天热度）")
    at()
    L.append("**提取方法**：逐条 `title` 子串匹配；记录**首次出现日期**（全语料最早 `date`）与**近 90 天条数**；"
             "`as-of` = 该词**首次出现当日**即可捕获（新词首发 = 口径变化的起点）。")
    at()
    L.append("| 词 | 总条数 | 首次出现 | 近90天条数 |")
    L.append("|:--|--:|:--|--:|")
    # 近 90 天：以语料最后一天为基准
    from datetime import date, timedelta
    last = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    cut = (last - timedelta(days=90)).isoformat()
    for w in NEW_TERMS:
        hits = [r for r in recs if w in (r.get("title", "") or "")]
        first = min((r.get("date", "") for r in hits), default="—")
        recent = sum(1 for r in hits if (r.get("date", "") or "") >= cut)
        L.append(f"| {w} | {len(hits)} | {first} | {recent} |")
    at()

    # ── ③ 通稿密度 ────────────────────────────────────────────────────────
    L.append("## 3. ③ 通稿密度（主题逐日条数）")
    at()
    L.append("**提取方法**：对每 `date` 统计含主题词的条数 → 得**逐日序列**；"
             "`as-of` = 当日（收盘/次日即可算）。下给分布与**近 7 日滚动**（“突然变密”= 候选信号）。")
    at()
    L.append("| 主题 | 日均 | 中位 | 最大(单日) | 有该主题的天数 |")
    L.append("|:--|--:|--:|--:|--:|")
    density = {}
    for topic in DENSITY_TOPICS:
        daily = Counter()
        for r in recs:
            if topic in (r.get("title", "") or ""):
                daily[r.get("date", "")] += 1
        density[topic] = daily
        vals = sorted(daily.values())
        med = vals[len(vals) // 2] if vals else 0
        L.append(f"| {topic} | {sum(daily.values()) / max(1, len(dates)):.2f} | {med} | "
                 f"{max(vals) if vals else 0} | {len(daily)} |")
    at()
    # 近 7 日滚动示例（人工智能）
    L.append("- **近 7 日滚动示例（主题“人工智能”）**：")
    ai = density["人工智能"]
    L.append("  " + " ｜ ".join(f"{d}: {ai.get(d, 0)}" for d in dates[-7:]))
    at()

    # ── ④ 版面位置（代理）────────────────────────────────────────────────
    L.append("## 4. ④ 版面位置（⚠️ **代理**：`channel` 频道，非真实版面）")
    at()
    L.append("**提取方法**：N1 **无版面字段** → 用 `channel`（频道）作**近似代理**（时政/国内 偏要闻；"
             "社会/体育 偏一般）。`as-of` = 发布日。**⚠️ 这是代理，不等价于头版/要闻版位。**")
    at()
    ch = Counter(r.get("channel", "") for r in recs)
    L.append("- **全语料频道分布（top 12）**：" +
             "、".join(f"{k} {v}" for k, v in ch.most_common(12)))
    ai_ch = Counter(r.get("channel", "") for r in recs if "人工智能" in (r.get("title", "") or ""))
    L.append("- **“人工智能”相关标题的频道分布（top 8）**：" +
             "、".join(f"{k} {v}" for k, v in ai_ch.most_common(8)))
    at()

    # ── ⑤ 社论 / 评论员文章标记 ───────────────────────────────────────────
    L.append("## 5. ⑤ 社论 / 评论员文章标记（标题级）")
    at()
    L.append("**提取方法**：`title` 命中下列标记词即计一篇评论体；`as-of` = 发布日。")
    at()
    cc = count_words(recs, COMMENTARY_MARKERS)
    L.append("- **标记词命中**：" + "、".join(f"{w} {cc[w]}" for w in COMMENTARY_MARKERS if cc[w]))
    L.append(f"- **评论体合计（去重条数，粗略）**：**{sum(1 for r in recs if any(m in (r.get('title','') or '') for m in COMMENTARY_MARKERS))}**")
    at()

    # ── ⑥ 口径变化（示例：新词月度趋势）──────────────────────────────────
    L.append("## 6. ⑥ 口径变化（词的出现 / 消失 / 替换 —— 示例）“新质生产力”月度条数")
    at()
    L.append("**提取方法**：固定词表 → 逐月计数 → 观察**起量/见顶/淡出**；`as-of` = 发布日。")
    at()
    mo = Counter(r.get("date", "")[:7] for r in recs if "新质生产力" in (r.get("title", "") or ""))
    L.append("| 月 | 条数 |")
    L.append("|:--|--:|")
    for m in sorted(mo):
        L.append(f"| {m} | {mo[m]} |")
    at()

    # ── 小结 ──────────────────────────────────────────────────────────────
    L.append("## 7. 小结与下一步")
    at()
    L.append("- **可用信号（标题级）**：① 措辞强度词表 · ② 新词首次出现/热度 · ③ 主题通稿密度 · "
             "⑤ 评论体标记 · ⑥ 口径变化（月度趋势）；④ 版面只能用 `channel` **代理**。")
    L.append("- ⚠️ **上述均为“信号存在性”证据，不是预测结论** → 进入 **N3-4**："
             "规则（信号组合 → P(动作) + 时间窗）+ **walk-forward + 基线 + 提前期** 评估。")
    L.append("- ⚠️ **代理源**：全部来自 `chinanews`；后续并入其它源须**按源分列**重算。")
    at()
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[sg] wrote {OUT_MD} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/eda.py — N3-1 **探索性分析（EDA）** 生成器
=====================================================================
读 `news/archive/<source>-*.jsonl.gz`（只含 标题+日期+来源+链接）→ 汇总**真实计数** →
写 `news/policy/EDA.md`。

纪律（见 WATCH_NEWS_TASK.md 第8批 N3-1 / §0.0.1）：
  * 🚫 **不许凭印象** —— 所有数字来自语料计数，**必须贴真实计数与示例**；
  * 本 EDA 只做**描述性统计**，**不预测、不表态**（政治中立）；
  * 语料当前为**代理源 `chinanews`**（新华网日期路径 403/405 未通）—— 报告中**必须写明**。

用法：
  python3 news/policy/eda.py
"""
from __future__ import annotations

import glob
import gzip
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))            # news/policy
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")     # news/archive
OUT = os.path.join(HERE, "EDA.md")

# ① 动作动词 / 动作词（在标题中做子串计数；示例取前 2 条）
ACTIONS = [
    "会见", "会谈", "会晤", "出访", "访问", "抵达", "出席", "举行", "召开",
    "签署", "发布", "印发", "出台", "部署", "启动", "开通", "投产", "开工",
    "视察", "调研", "考察", "致电", "致信", "贺信", "批示", "指示", "讲话",
    "座谈", "协商", "谈判", "磋商", "通过", "批准", "任命", "免职", "通报",
    "处罚", "约谈", "整改", "上线", "试行", "试点", "推广", "实施", "生效",
    "修订", "审议", "听证", "回应", "抗议", "谴责", "制裁", "反制",
    "演习", "试射", "发射", "下水", "巡航", "揭牌", "落户", "增持", "降准",
    "降息", "加息", "招标", "中标", "并购", "收购", "上市", "退市",
]

# ② 主体 / 机构词
SUBJECTS = [
    "习近平", "李强", "王毅", "政治局", "国务院", "全国人大", "人大", "政协",
    "发改委", "财政部", "央行", "人民银行", "商务部", "工信部", "外交部",
    "国防部", "科技部", "教育部", "住建部", "市场监管总局", "税务总局",
    "海关总署", "证监会", "国家统计局", "中共中央", "国务院常务会议",
    "国资委", "网信办", "公安部", "交通运输部", "农业农村部",
]

# ③ 标题模式（正则）
PATTERNS = [
    ("X 会见 Y", re.compile(r".{2,6}会见.{2,10}")),
    ("就…作出重要指示/批示", re.compile(r"就.{2,20}(作出|作).{0,4}(指示|批示)")),
    ("X 签署…协议/协定", re.compile(r"签署.{0,12}(协议|协定|备忘录|文件)")),
    ("X 印发/出台…通知/意见/方案", re.compile(r"(印发|出台|发布).{0,12}(通知|意见|方案|办法|条例)")),
    ("X 决定/批准…", re.compile(r"(决定|批准|通过).{2,}")),
    ("X 召开…会议", re.compile(r"召开.{0,10}(会议|大会|峰会|论坛)")),
    ("同比增长/下降 X%", re.compile(r"(同比增长|同比下降|环比|同比).{0,8}%?")),
]


def load_records():
    recs = []
    for fn in sorted(glob.glob(os.path.join(ARCHIVE, "*-*.jsonl.gz"))):
        src = os.path.basename(fn).split("-")[0]
        try:
            f = gzip.open(fn, "rt", encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            print(f"[eda] skip {fn}: {e}")
            continue
        try:
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
        except Exception as e:  # noqa: BLE001  (抓取可能在写盘 → 读到不完整 member)
            print(f"[eda] truncated read on {fn} ({e}); using partial")
        finally:
            f.close()
    return recs


def main() -> int:
    recs = load_records()
    n = len(recs)
    if not n:
        print("[eda] no records found under news/archive/ — run fetch_archive.py first")
        return 1

    by_year = Counter()
    by_month = Counter()
    by_channel = Counter()
    sources = Counter()
    days = set()
    for r in recs:
        d = r.get("date", "")
        by_year[d[:4]] += 1
        by_month[d[:7]] += 1
        by_channel[r.get("channel") or "(无)"] += 1
        sources[r.get("source", "?")] += 1
        if d:
            days.add(d)

    # 动作/主体/模式：计数 + 示例
    def scan(terms, is_regex=False):
        out = {}
        for t in terms:
            pat = t if is_regex else None
            key = t[0] if is_regex else t
            cnt = 0
            ex = []
            for r in recs:
                title = r.get("title", "")
                hit = bool(t[1].search(title)) if is_regex else (t in title)
                if hit:
                    cnt += 1
                    if len(ex) < 2:
                        ex.append((r.get("date", ""), title, r.get("url", "")))
            out[key] = (cnt, ex)
        return out

    act = scan(ACTIONS)
    subj = scan(SUBJECTS)
    pat = scan(PATTERNS, is_regex=True)

    span_lo, span_hi = min(days), max(days)
    lines = []
    lines.append("# EDA — 探索性分析（N3-1）\n")
    lines.append(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ "
                 f"脚本：`news/policy/eda.py` ｜ 语料：`news/archive/*.jsonl.gz`\n")
    lines.append("> ⚠️ **口径**：本 EDA 只做**描述性统计**（计数 / 分布 / 示例）；"
                 "**不预测、不表态**；所有数字**来自真实语料**（可回溯到 `url`）。\n")
    lines.append(f"> 📝 **语料为代理源**：{', '.join(f'`{s}`×{c}' for s, c in sources.items())}"
                 "（新华网日期路径 403/405 未通，见 `news/archive/PROGRESS.md`）—— "
                 "**代理源 ≠ 新华社**，`source` 字段严格区分。\n")

    lines.append("\n## 0. 语料规模\n")
    lines.append(f"- 条目总数：**{n}** ｜ 覆盖天数：**{len(days)}** ｜ 区间：**{span_lo} ~ {span_hi}**")
    lines.append(f"- 来源（按源分列）：" + "、".join(f"`{s}` {c}" for s, c in sources.most_common()))

    lines.append("\n## 1. 年度分布（真实计数）\n")
    lines.append("| 年 | 条数 |\n|:--|--:|")
    for y in sorted(by_year):
        lines.append(f"| {y} | {by_year[y]} |")

    lines.append("\n## 2. 月度分布（真实计数）\n")
    lines.append("| 月 | 条数 |\n|:--|--:|")
    for mth in sorted(by_month):
        lines.append(f"| {mth} | {by_month[mth]} |")

    lines.append("\n## 3. 频道分布（真实计数，前 30）\n")
    lines.append("| 频道 | 条数 |\n|:--|--:|")
    for ch, c in by_channel.most_common(30):
        lines.append(f"| {ch} | {c} |")

    lines.append("\n## 4. 动作动词 / 动作词（标题子串计数）\n")
    lines.append("> 每词给**真实计数**（出现在多少条标题）+ 最多 2 条**真实示例**（日期 · 标题 · 链接）。\n")
    lines.append("| 动作词 | 计数 | 占比 | 示例 |\n|:--|--:|--:|:--|")
    for k, (c, ex) in sorted(act.items(), key=lambda x: -x[1][0]):
        if c == 0:
            continue
        e = ex[0]
        exs = f"{e[0]} · {e[1]} · {e[2]}" if e else ""
        lines.append(f"| {k} | {c} | {c/n*100:.2f}% | {exs} |")

    lines.append("\n## 5. 主体 / 机构词（标题子串计数）\n")
    lines.append("| 主体词 | 计数 | 占比 | 示例 |\n|:--|--:|--:|:--|")
    for k, (c, ex) in sorted(subj.items(), key=lambda x: -x[1][0]):
        if c == 0:
            continue
        e = ex[0]
        exs = f"{e[0]} · {e[1]} · {e[2]}" if e else ""
        lines.append(f"| {k} | {c} | {c/n*100:.2f}% | {exs} |")

    lines.append("\n## 6. 标题模式（正则计数）\n")
    lines.append("| 模式 | 计数 | 占比 | 示例 |\n|:--|--:|--:|:--|")
    for k, (c, ex) in sorted(pat.items(), key=lambda x: -x[1][0]):
        e = ex[0]
        exs = f"{e[0]} · {e[1]} · {e[2]}" if e else ""
        lines.append(f"| {k} | {c} | {c/n*100:.2f}% | {exs} |")

    lines.append("\n## 7. 下一步（本 EDA 的用途）\n")
    lines.append("- 本 EDA 是 **N3-1 的硬前置**：`TAXONOMY.md`（动作分类体系）**必须由本表归纳**，"
                 "🚫 不许先验拍脑袋。\n")
    lines.append("- **频率分层**（高/中/低频）**由上面真实计数得出**，🚫 不沿用 supervisor 先验。\n")
    lines.append("- ⚠️ **样本仍在扩充中**（N1 倒序逐日回溯，尚未覆盖 10 年）→ 计数会随后续轮次更新。\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[eda] wrote {OUT}  (n={n}, days={len(days)}, {span_lo}~{span_hi})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
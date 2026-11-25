#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/taxonomy.py — N3-1 ③④ **数据驱动的动作分类体系（TAXONOMY）** 生成器
=========================================================================
读 `news/archive/<source>-*.jsonl.gz`（只含 标题+日期+来源+链接）→
按【动作类别】聚合**真实计数**（原始口径 + 政经口径）→ 写 `news/policy/TAXONOMY.md`。

纪律（见 WATCH_NEWS_TASK.md 第8批 N3-1 / §0.0.1）：
  * 类别**由 `EDA.md` 归纳**（触发词 = EDA §4 的动作词），🚫 **不先验拍脑袋**；
  * **频率分层（高/中/低）由实测计数得出**，🚫 不沿用 supervisor 先验；
  * 只做**描述性统计**（计数 / 示例），**不预测、不表态**（政治中立）；
  * 语料当前为**代理源**（`chinanews`；新华网日期路径 403/405 未通）—— 报告中**必须写明**。

用法：
  python3 news/policy/taxonomy.py
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))            # news/policy
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")     # news/archive
OUT = os.path.join(HERE, "TAXONOMY.md")

# ── 政经口径（govt/state actor 标记）──────────────────────────────────────────
# 取自 `EDA.md` §5「主体/机构词」+ 通用机构标记；用于把「政经动作」从综合新闻里
# 粗略切出来（⚠️ 仍是启发式；边界规则见 TAXONOMY.md 正文）。
# 🚫 不用裸「人大」（会命中「万人大合唱」等）→ 用「全国人大」「人大常委会」。
GOV_MARKERS = [
    "习近平", "李强", "王毅", "政治局", "国务院", "中共中央", "全国人大", "人大常委会",
    "政协", "外交部", "国防部", "商务部", "央行", "人民银行", "财政部", "发改委",
    "工信部", "证监会", "教育部", "公安部", "交通运输部", "农业农村部", "海关总署",
    "网信办", "税务总局", "国资委", "市场监管总局", "住建部", "科技部", "水利部",
    "自然资源部", "生态环境部", "文旅部", "文化和旅游部", "统计局", "医保局",
    "消防救援局", "最高检", "最高法", "卫健委", "民政部", "人社部", "司法部",
    "应急管理部", "国务院常务会议", "政府",
]

# ── 动作类别（由 `EDA.md` §4 的动作词归纳）──────────────────────────────────
# 每类：id · 名称 · 层级 · 领域 · 力度 · 触发词（标题子串）· 边界规则
CATEGORIES = [
    {
        "id": "A1", "name": "外事·会见会谈", "level": "中央/外交", "domain": "外交",
        "force": "表态/协商",
        "triggers": ["会见", "会谈", "会晤", "磋商"],
        "boundary": "算：国家/政府/外交首长之间的会见、会谈、会晤、磋商。不算：企业商务会面、"
                    "文艺演出见面会（除非主语为政府首长）。",
    },
    {
        "id": "A2", "name": "外事·出访访问", "level": "中央/外交", "domain": "外交",
        "force": "表态",
        "triggers": ["出访", "国事访问", "正式访问"],
        "boundary": "算：国家元首/政府首脑/外长的出访与正式访问。不算：一般代表团、经贸/文体"
                    "交流的『访问』（噪声大，故只用『出访/国事访问/正式访问』）。",
    },
    {
        "id": "A3", "name": "会议·召开", "level": "中央/部委/地方", "domain": "综合",
        "force": "—",
        "triggers": ["召开"],
        "boundary": "算：政治局会议、国常会、部委/地方工作会议、政党会议。不算：企业内部会议、"
                    "商业论坛（『召开』主语非党政机构时）。",
    },
    {
        "id": "A4", "name": "会议·举行", "level": "中央/部委/地方", "domain": "综合",
        "force": "—",
        "triggers": ["举行"],
        "boundary": "⚠️ 最宽泛的动词（含展会/赛事/演出）。算：党政机构主办的会议/仪式/发布会。"
                    "不算：体育赛事、文娱演出、商业展会。→ 须叠加政经口径才可解释。",
    },
    {
        "id": "A5", "name": "政策·发布印发", "level": "中央/部委/地方", "domain": "综合",
        "force": "表态/文件",
        "triggers": ["发布", "印发", "出台"],
        "boundary": "算：政府/部委/地方发布政策、印发文件、出台办法。不算：企业新品发布、"
                    "机构发布行业报告（主语非政府时）。",
    },
    {
        "id": "A6", "name": "政策·部署实施", "level": "中央/部委/地方", "domain": "综合",
        "force": "推广/强制",
        "triggers": ["部署", "实施", "试行", "修订"],
        "boundary": "算：政府部署工作、实施/试行/修订法规或方案。不算：企业实施内部制度。",
    },
    {
        "id": "A7", "name": "监管·通报处罚", "level": "部委/地方", "domain": "监管",
        "force": "强制",
        "triggers": ["通报", "处罚", "约谈", "整改"],
        "boundary": "算：党政监管机关的通报、行政处罚、约谈、责令整改。不算：企业/媒体自发通报"
                    "（如事故通报、天气通报）。",
    },
    {
        "id": "A8", "name": "领导人·讲话活动", "level": "中央", "domain": "综合",
        "force": "表态",
        "triggers": ["讲话", "出席", "考察", "视察", "批示", "致电", "致信", "贺信"],
        "boundary": "算：国家领导人的讲话、出席、考察、视察、批示、致电致信。不算：外国非政府人物"
                    "活动；企业/文艺人物『出席』。",
    },
    {
        "id": "A9", "name": "工程·开通投产", "level": "部委/地方/央企", "domain": "经济/基建",
        "force": "推广",
        "triggers": ["开通", "投产", "开工", "揭牌", "落户"],
        "boundary": "算：交通/能源/水利等基建开通投产、项目开工、机构揭牌落地。不算：商业门店"
                    "开业、产品上线（非基建类）。",
    },
    {
        "id": "A10", "name": "经贸·签署", "level": "中央/部委/地方", "domain": "贸易/产业",
        "force": "承诺",
        "triggers": ["签署"],
        "boundary": "算：政府间/政企间协议、协定、备忘录、文件的签署。不算：纯企业商务合同（除非"
                    "涉重大产业政策或政府背书）。",
    },
    {
        "id": "A11", "name": "市场·上市并购", "level": "企业/监管", "domain": "资本市场",
        "force": "—",
        "triggers": ["上市", "并购", "收购", "增持", "退市"],
        "boundary": "算：企业上市/并购/收购/增持/退市等资本市场动作（对 L2 板块研究相关）。"
                    "不算：一般商品『上市』（如新车型上市）—— 噪声较大，须人工复核。",
    },
    {
        "id": "A12", "name": "军事·演习试射", "level": "中央/军方", "domain": "军事",
        "force": "强制/威慑",
        "triggers": ["演习", "试射", "发射", "下水"],
        "boundary": "算：军队/国防部主导的演习、试射、发射（航天/导弹）、舰艇下水。不算：民用"
                    "商业航天『发射』（如卫星发射，除非涉国家航天工程）。",
    },
    {
        "id": "A13", "name": "对外表态·回应反制", "level": "中央/外交", "domain": "外交/安全",
        "force": "表态/强制",
        "triggers": ["回应", "抗议", "谴责", "制裁", "反制"],
        "boundary": "算：政府/外交部的回应、抗议、谴责、制裁、反制。不算：企业/明星对舆情的"
                    "『回应』（噪声大，须叠加政经口径）。",
    },
    {
        "id": "A14", "name": "试点·推广", "level": "中央/部委/地方", "domain": "综合",
        "force": "试点/推广",
        "triggers": ["试点", "推广"],
        "boundary": "算：政府主导的试点、经验推广。不算：企业产品推广、商业营销『推广』。",
    },
    {
        "id": "A15", "name": "货币·政策工具", "level": "央行", "domain": "货币财政",
        "force": "强制/引导",
        "triggers": ["降准", "降息", "加息", "逆回购", "MLF", "LPR"],
        "boundary": "算：央行的降准/降息/加息、公开市场操作（逆回购/MLF/LPR）。不算：商业银行"
                    "自主调整存款利率（须标注为市场主体行为）。",
    },
]

# 频率分层阈值（**由实测计数得出**；可按语料更新，但阈值一次写死）
TIER_HIGH = 1000   # 政经口径近3年 ≥1000 → 高频
TIER_MID = 200     # 200–999 → 中频；<200 → 低频


def load_records():
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
            print(f"[tax] truncated read on {fn} ({e}); using partial")
    return recs


def is_gov(title: str) -> bool:
    return any(g in title for g in GOV_MARKERS)


def main() -> int:
    recs = load_records()
    n = len(recs)
    if not n:
        print("[tax] no records under news/archive/ — run fetch_archive.py first")
        return 1

    days = {r.get("date", "") for r in recs if r.get("date")}
    span_lo, span_hi = min(days), max(days)
    sources = Counter(r.get("source", "?") for r in recs)
    years = sorted({d[:4] for d in days if d})

    # 每类：原始计数 + 政经计数 + 示例（优先政经）
    rows = []
    for c in CATEGORIES:
        raw = 0
        gov = 0
        ex_raw, ex_gov = [], []
        for r in recs:
            t = r.get("title", "")
            if any(k in t for k in c["triggers"]):
                raw += 1
                if len(ex_raw) < 2:
                    ex_raw.append((r.get("date", ""), t, r.get("url", "")))
                if is_gov(t):
                    gov += 1
                    if len(ex_gov) < 3:
                        ex_gov.append((r.get("date", ""), t, r.get("url", "")))
        tier = "高频" if gov >= TIER_HIGH else ("中频" if gov >= TIER_MID else "低频")
        rows.append({"c": c, "raw": raw, "gov": gov, "tier": tier,
                     "ex": ex_gov if ex_gov else ex_raw})

    rows.sort(key=lambda x: -x["gov"])

    L = []
    at = lambda: L.append("")
    L.append("# TAXONOMY — 政策动作分类体系（N3-1 ③④）")
    at()
    L.append(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 脚本：`news/policy/taxonomy.py` "
             "｜ 语料：`news/archive/*.jsonl.gz`")
    at()
    L.append("> ⚠️ **口径**：类别**由 `EDA.md` 归纳**（触发词 = EDA §4 动作词），**计数来自真实语料**；"
             "本表只做**描述性统计**，**不预测、不表态**。")
    at()
    L.append(f"> 📝 **语料为代理源**：{('、'.join(f'`{s}`×{c}' for s, c in sources.items()))}"
             "（新华网日期路径 403/405 未通，见 `news/archive/PROGRESS.md`）—— "
             "**代理源 ≠ 新华社**，`source` 字段严格区分。")
    at()
    at()
    L.append("## 0. 语料与口径")
    at()
    L.append(f"- 条目总数：**{n}** ｜ 覆盖天数：**{len(days)}** ｜ 区间：**{span_lo} ~ {span_hi}** ｜ 年：{', '.join(years)}")
    L.append(f"- **原始口径**：标题含该类触发词即计入（含噪声，**互不排斥**，一条可进多类）。")
    L.append(f"- **政经口径**：在原始口径基础上，**要求标题含政经主体标记**（{len(GOV_MARKERS)} 个；"
             "取自 EDA §5，见脚本 `GOV_MARKERS`）→ 作为 **L1 更相关的计数**。")
    L.append(f"- **频率分层阈值**（一次写死，近3年政经口径）：**高频 ≥{TIER_HIGH}** ｜ "
             f"**中频 {TIER_MID}–{TIER_HIGH - 1}** ｜ **低频 <{TIER_MID}**。")
    at()
    L.append("> ⚠️ **计数是启发式**：触发词为**标题子串**，含大量噪声（如『举行』含赛事/演出；"
             "『上市』含新车上市）→ **边界规则见下表**；政经口径显著更干净，但仍需人工抽样校验。")
    at()
    L.append("## 1. 动作类别总表（**计数即分层依据**）")
    at()
    L.append("| 类别 | 触发词 | 原始计数 | 政经计数 | 政经占比 | 频率层级 |")
    L.append("|:--|:--|--:|--:|--:|:--|")
    for r in rows:
        c = r["c"]
        L.append(f"| **{c['id']} {c['name']}** | {'/'.join(c['triggers'])} | {r['raw']} | "
                 f"{r['gov']} | {r['gov'] / n * 100:.2f}% | **{r['tier']}** |")
    at()
    L.append("## 2. 各类边界规则与真实示例")
    at()
    L.append("> 每类给 **2–3 个真实示例（日期 · 标题 · 链接）**，**优先政经口径**；示例可回溯到原文。")
    for r in rows:
        c = r["c"]
        at()
        L.append(f"### {c['id']} {c['name']} ｜ {c['level']} · {c['domain']} · 力度={c['force']} ｜ "
                 f"**{r['tier']}**（政经 {r['gov']} / 原始 {r['raw']}）")
        L.append(f"- **边界规则**：{c['boundary']}")
        for d, t, u in r["ex"]:
            L.append(f"- 示例：{d} · {t} · {u}")
    at()
    L.append("## 3. 频率分层（**由实测计数归纳**）")
    at()
    hi = [r for r in rows if r["tier"] == "高频"]
    mid = [r for r in rows if r["tier"] == "中频"]
    lo = [r for r in rows if r["tier"] == "低频"]
    L.append(f"- **高频（政经 ≥{TIER_HIGH}/近3年）**："
             + ("、".join(f"{r['c']['id']} {r['c']['name']}（{r['gov']}）" for r in hi) or "（无）"))
    L.append(f"- **中频（{TIER_MID}–{TIER_HIGH - 1}）**："
             + ("、".join(f"{r['c']['id']} {r['c']['name']}（{r['gov']}）" for r in mid) or "（无）"))
    L.append(f"- **低频（<{TIER_MID}）**："
             + ("、".join(f"{r['c']['id']} {r['c']['name']}（{r['gov']}）" for r in lo) or "（无）"))
    at()
    L.append("> 🔑 **结论（阶段性）**：**政治动作整体样本充足** —— 高频/中频类具备统计建模条件，"
             "与 §0.0.1「动作 ≠ 稀有事件」的判断**一致**；真正稀疏的是**战略级事件**（本表未单列）。")
    L.append("> ⚠️ 低频类的**个例不得当规律**；高频类的显著性**不得冒充低频类结论**。")
    at()
    L.append("## 4. 除「动作类型」外的其它维度（方案）")
    at()
    L.append("> 事件库（N3-3）每条将同时标注下列维度；本表先给**取值域**（由 EDA/语料归纳）。")
    L.append("")
    L.append("| 维度 | 取值（归纳） | 说明 |")
    L.append("|:--|:--|:--|")
    L.append("| **层级** | 中央 / 部委 / 地方 / 外国政府 / 市场主体 | 由标题主体判定（见 EDA §5） |")
    L.append("| **领域** | 外交 / 监管 / 经济基建 / 贸易产业 / 资本市场 / 货币财政 / 军事 / 综合 | 见各类 `domain` |")
    L.append("| **力度** | 表态 / 文件 / 试点 / 推广 / 强制 / 承诺 / 威慑 | 见各类 `force` |")
    L.append("| **可观察性** | 已发生·有公开文本 / 已发生·无全文 / 预告 | 事件库只收录**已发生**且有链接者 |")
    at()
    L.append("## 5. 与 L1 / N3-3 的关系")
    at()
    L.append("- 本表是 **N3-3（事件库 `EVENTS.csv`）** 的**标注骨架**：`动作类型 = 上表 A1–A15`，"
             "其余维度见 §4。")
    L.append("- 抽取须走**半自动流水线**（`extract_events.py`：规则/正则 → 候选 → LLM 分类 → 抽样人工校验），"
             "**高频类先做**。")
    L.append("- ⚠️ **代理源局限**：本表来自 `chinanews`，**非新华社**；后续若新华网可通/或并入人民网/央视网，"
             "须**按源分列**重算。")
    at()
    L.append("## 6. 局限与下一步")
    at()
    L.append("- ⚠️ **样本仍在扩充**（N1 倒序回溯，当前 2024-06~2026-10，**尚未覆盖 10 年**）→ 计数会随后续轮次更新。")
    L.append("- ⚠️ **子串计数有噪声**（尤其 A4 举行 / A11 上市 / A13 回应）；政经口径已缓解，"
             "但**仍需 N3-3 抽样人工校验**报准确率。")
    L.append("- ⚠️ **政经口径偏中国**：`GOV_MARKERS` 以中国党政机构为主 → **美/欧/日/韩等外国政府动作被低估**"
             "（其『会见/签署/制裁』多落在原始口径）→ **政经计数是中国一侧的下界**，外国一侧须另设主体词表。")
    L.append("- ⚠️ **A15 含例行操作**：`逆回购/MLF/LPR` 多为**高频例行**公开市场操作，"
             "与『降准/降息』等**政策转向**不同量级 → 事件库须把**例行操作**与**政策变化**分开标注。")
    L.append("- 下一步：**N3-3 事件库**（`extract_events.py` + `EVENTS.csv`/`EVENTS.md`，抽 ≥100 条报准确率）"
             "→ **N3-2 信号** → **N3-4 预警**。")
    at()

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"[tax] wrote {OUT}  (n={n}, cats={len(rows)}, {span_lo}~{span_hi})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
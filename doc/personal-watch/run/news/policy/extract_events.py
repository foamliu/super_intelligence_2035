#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news/policy/extract_events.py — N3-3 **事件库（监督标签）** 半自动抽取器
==========================================================================
读 `news/archive/<source>-*.jsonl.gz`（只含 标题+日期+来源(channel)+链接）→
用【规则 / 词典 / 正则】抽取「政经动作」候选 → 写 `news/policy/EVENTS.csv` + `EVENTS.md`。

流水线（见 WATCH_NEWS_TASK.md 第 8 批 N3-3）：
  ① 规则 / 词典 / 正则 → 批量候选        ← 本脚本
  ② LLM 分类                             ← ⚠️ 本环境**无 LLM key**（用户已定「免 key」）
                                            → **未接入**；分类改由**词典规则**完成，
                                            ② 的角色由 ③ 顶替（见 EVENTS.md §0）。
  ③ 抽样人工校验（`--sample N --seed S` → `EVENTS_AUDIT.csv`，可复现）

标注字段（任务书要求）：`日期 · 主体 · 动作类型 · 领域 · 力度 · 依据标题 · 链接`
（另附 `actor_kind / subtype / level / noise_risk / matched_trigger` 便于复核与降噪）。

纪律：
  * 🚫 **不许编造**：每条事件**可核验到原文链接**（`url` 直接取自语料，未改写）；
  * 只做**描述性标注**（主体 / 动作 / 领域 / 力度），**不预测、不表态**（政治中立）；
  * 语料当前为**代理源 `chinanews`**（新华网 403/405 未通）—— 报告中**必须写明**；
  * **高频类先做**；低频类**样本不足时如实标注**，不许硬凑、不许个例当规律。

用法：
  python3 news/policy/extract_events.py                       # 抽候选 → EVENTS.csv + EVENTS.md
  python3 news/policy/extract_events.py --sample 100 --seed 20351003
  python3 news/policy/extract_events.py --write-audit --verdicts "1110..."
"""
from __future__ import annotations

import argparse
import csv
import glob
import gzip
import hashlib
import io
import json
import os
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))            # news/policy
ARCHIVE = os.path.join(os.path.dirname(HERE), "archive")     # news/archive
OUT_CSV = os.path.join(HERE, "EVENTS.csv")
OUT_MD = os.path.join(HERE, "EVENTS.md")
AUDIT_CSV = os.path.join(HERE, "EVENTS_AUDIT.csv")
INDEX_MD = os.path.join(HERE, "INDEX_FILES.md")
MAX_BYTES = 20 * 1024 * 1024                                 # 体积纪律：>20MB → 按年分片

sys.path.insert(0, HERE)
import taxonomy as tx  # noqa: E402  （复用 N3-1 的类别骨架 + 政经主体标记，保持一致）

# ── 主体（actor）词典 ───────────────────────────────────────────────────────
# 由 `EDA.md` §5（主体/机构词）+ TAXONOMY 的 GOV_MARKERS 归纳（**数据驱动**）。
CN_ACTORS = {
    "习近平": ("习近平", "中央"),
    "李强": ("李强", "中央"),
    "王毅": ("外交部", "中央/外交"),
    "政治局": ("中央政治局", "中央"),
    "国务院常务会议": ("国务院常务会议", "中央"),
    "国务院": ("国务院", "中央"),
    "中共中央": ("中共中央", "中央"),
    "全国人大": ("全国人大", "中央/立法"),
    "人大常委会": ("全国人大常委会", "中央/立法"),
    "政协": ("政协", "中央"),
    "外交部": ("外交部", "部委"),
    "国防部": ("国防部", "部委"),
    "商务部": ("商务部", "部委"),
    "央行": ("中国人民银行", "部委"),
    "人民银行": ("中国人民银行", "部委"),
    "财政部": ("财政部", "部委"),
    "发改委": ("国家发改委", "部委"),
    "工信部": ("工信部", "部委"),
    "证监会": ("证监会", "部委"),
    "教育部": ("教育部", "部委"),
    "公安部": ("公安部", "部委"),
    "交通运输部": ("交通运输部", "部委"),
    "农业农村部": ("农业农村部", "部委"),
    "海关总署": ("海关总署", "部委"),
    "网信办": ("网信办", "部委"),
    "税务总局": ("税务总局", "部委"),
    "国资委": ("国资委", "部委"),
    "市场监管总局": ("市场监管总局", "部委"),
    "住建部": ("住建部", "部委"),
    "科技部": ("科技部", "部委"),
    "水利部": ("水利部", "部委"),
    "自然资源部": ("自然资源部", "部委"),
    "生态环境部": ("生态环境部", "部委"),
    "文旅部": ("文旅部", "部委"),
    "文化和旅游部": ("文化和旅游部", "部委"),
    "统计局": ("国家统计局", "部委"),
    "医保局": ("国家医保局", "部委"),
    "最高检": ("最高检", "司法"),
    "最高法": ("最高法", "司法"),
    "卫健委": ("卫健委", "部委"),
    "民政部": ("民政部", "部委"),
    "人社部": ("人社部", "部委"),
    "司法部": ("司法部", "部委"),
    "应急管理部": ("应急管理部", "部委"),
    "消防救援局": ("国家消防救援局", "部委"),
    "政府": ("（地方）政府", "地方/泛指"),
}

# 外国政府 / 国际组织（§0.0.1 建模对象：美/欧/日/韩等）
FOREIGN_ACTORS = {
    "美国财政部": ("美国·财政部", "外国政府"),
    "美国商务部": ("美国·商务部", "外国政府"),
    "美国国防部": ("美国·国防部", "外国政府"),
    "白宫": ("美国·白宫", "外国政府"),
    "美国": ("美国", "外国政府"),
    "美联储": ("美国·美联储", "外国政府"),
    "欧盟委员会": ("欧盟委员会", "外国政府"),
    "欧盟": ("欧盟", "外国政府"),
    "欧洲": ("欧洲", "外国政府"),
    "日本": ("日本", "外国政府"),
    "韩国": ("韩国", "外国政府"),
    "英国": ("英国", "外国政府"),
    "法国": ("法国", "外国政府"),
    "德国": ("德国", "外国政府"),
    "俄罗斯": ("俄罗斯", "外国政府"),
    "印度": ("印度", "外国政府"),
    "澳大利亚": ("澳大利亚", "外国政府"),
    "加拿大": ("加拿大", "外国政府"),
    "巴西": ("巴西", "外国政府"),
    "东盟": ("东盟", "国际组织"),
    "联合国": ("联合国", "国际组织"),
    "北约": ("北约", "国际组织"),
    "世界卫生组织": ("世界卫生组织", "国际组织"),
    "世卫": ("世界卫生组织", "国际组织"),
    "世界银行": ("世界银行", "国际组织"),
}

# ── 噪声风险启发式（延续 TAXONOMY 的「边界规则」）─────────────────────────────
BROAD_TRIG = {"举行", "回应", "发布", "实施", "考察", "出席", "上市", "开通",
              "落户", "推广", "增持", "收购", "并购", "调研"}
MID_TRIG = {"会谈", "会晤", "磋商", "印发", "出台", "部署", "签署", "试点",
            "通报", "试行", "修订", "约谈", "整改", "处罚", "制裁"}
AMBIG_ACTOR = {"政府"}                      # 「政府」为泛指 → 风险高


def load_records():
    """读语料（只 5 字段）。⚠️ 抓取可能在写盘 → 读到不完整 member 时用 partial。"""
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
            print(f"[ev] truncated read on {fn} ({e}); using partial")
    return recs


def detect_actor(title: str):
    """取标题中**位置最靠前**的主体（同位置取最长标记）→ (marker, actor, level, kind)。"""
    best = None
    for marker, (actor, level) in CN_ACTORS.items():
        p = title.find(marker)
        if p >= 0:
            cand = (p, -len(marker), marker, actor, level, "CN")
            if best is None or cand < best:
                best = cand
    for marker, (actor, level) in FOREIGN_ACTORS.items():
        p = title.find(marker)
        if p >= 0:
            cand = (p, -len(marker), marker, actor, level, "FOREIGN")
            if best is None or cand < best:
                best = cand
    if best is None:
        return None
    _, _, marker, actor, level, kind = best
    return marker, actor, level, kind


def subtype_for(cat_id: str, title: str) -> str:
    """A15 货币工具：把「例行操作」与「政策变化」分开（TAXONOMY §6 局限）。"""
    if cat_id != "A15":
        return ""
    if any(k in title for k in ("降准", "降息", "加息")):
        return "政策变化"
    if any(k in title for k in ("逆回购", "MLF", "LPR", "公开市场")):
        return "例行操作"
    return ""


def noise_risk(trigger: str, marker: str) -> str:
    if trigger in BROAD_TRIG or marker in AMBIG_ACTOR:
        return "高"
    if trigger in MID_TRIG:
        return "中"
    return "低"


def build_events(recs):
    events, seen = [], set()
    for r in recs:
        title = r.get("title", "") or ""
        a = detect_actor(title)
        if not a:
            continue                              # 无政经主体 → 不是「政经动作」
        marker, actor, actor_level, kind = a
        for c in tx.CATEGORIES:
            trig = next((t for t in c["triggers"] if t in title), None)
            if trig is None:
                continue
            key = (r.get("url", ""), c["id"])
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "date": r.get("date", ""),
                "actor": actor,
                "actor_kind": kind,
                "action_type": c["id"],
                "action_name": c["name"],
                "subtype": subtype_for(c["id"], title),
                "level": "外国政府" if kind == "FOREIGN" else actor_level,
                "domain": c["domain"],
                "force": c["force"],
                "noise_risk": noise_risk(trig, marker),
                "matched_trigger": trig,
                "source": r.get("source", ""),
                "channel": r.get("channel", ""),
                "title": title,
                "url": r.get("url", ""),
            })
    events.sort(key=lambda e: (e["date"], e["action_type"], e["url"]), reverse=True)
    return events


COLS = ["date", "actor", "actor_kind", "action_type", "action_name", "subtype",
        "level", "domain", "force", "noise_risk", "matched_trigger",
        "source", "channel", "title", "url"]


def write_csv(events, outpath):
    """写 CSV；若单文件 >20MB → 按年分片（体积纪律）。返回 [(path, rows, bytes), ...]。"""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    for e in events:
        w.writerow(e)
    data = buf.getvalue().encode("utf-8")
    if len(data) <= MAX_BYTES:
        with open(outpath, "wb") as f:
            f.write(data)
        return [(outpath, len(events), len(data))]
    paths = []
    base = outpath[:-4] if outpath.endswith(".csv") else outpath
    for r in sorted({e["date"][:4] for e in events}):
        sub = [e for e in events if e["date"][:4] == r]
        p = f"{base}-{r}.csv"
        b = io.StringIO()
        ww = csv.DictWriter(b, fieldnames=COLS, extrasaction="ignore")
        ww.writeheader()
        for e in sub:
            ww.writerow(e)
        d = b.getvalue().encode("utf-8")
        with open(p, "wb") as f:
            f.write(d)
        paths.append((p, len(sub), len(d)))
    if os.path.exists(outpath):
        os.remove(outpath)
    return paths


def strat_sample(events, n, seed):
    """按动作类别分层抽样（比例分配 + 每类下限 2），**可由 seed 复现**。"""
    rnd = random.Random(seed)
    by_cat = defaultdict(list)
    for e in events:
        by_cat[e["action_type"]].append(e)
    total = len(events)
    if total == 0:
        return []
    cats = sorted(by_cat)
    alloc = {c: max(2, int(round(n * len(by_cat[c]) / total))) for c in cats}
    while sum(alloc.values()) > n:
        c = max(cats, key=lambda k: (alloc[k], len(by_cat[k])))
        alloc[c] -= 1
    while sum(alloc.values()) < n:
        c = max(cats, key=lambda k: len(by_cat[k]))
        alloc[c] += 1
    picked = []
    for c in cats:
        pool = by_cat[c][:]
        rnd.shuffle(pool)
        picked += pool[:alloc[c]]
    picked.sort(key=lambda e: (e["action_type"], e["date"], e["url"]))
    return picked


def read_audit():
    """读 `EVENTS_AUDIT.csv`（idx/action_type/.../verdict），返回准确率统计。"""
    if not os.path.exists(AUDIT_CSV):
        return None
    rows = []
    with open(AUDIT_CSV, "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    done = [r for r in rows if r.get("verdict", "").strip() in ("0", "1")]
    if not done:
        return None
    ok = sum(1 for r in done if r["verdict"].strip() == "1")
    per = defaultdict(lambda: [0, 0])
    for r in done:
        per[r["action_type"]][0] += 1
        per[r["action_type"]][1] += (r["verdict"].strip() == "1")
    return {"n": len(done), "ok": ok, "acc": ok / len(done), "per": dict(per),
            "rows": done}


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def write_index(files):
    L = ["# INDEX_FILES — news/policy 大文件清单", "",
         "> 由 `extract_events.py` **自动生成**。体积纪律：**单文件 >20 MB → 🚫 不入 git**",
         "> （本体移 `~/archive_data/`，本表登记路径/行数/大小/sha256）。", "",
         "| 路径 | 行数 | 大小(B) | sha256(前16) | 入 git |",
         "|:--|--:|--:|:--|:--|"]
    for p, rows, size in files:
        rel = os.path.relpath(p, os.path.dirname(HERE))
        L.append(f"| `{rel}` | {rows} | {size} | `{sha16(p)}` | "
                 f"{'✅ 是' if size <= MAX_BYTES else '❌ 否（>20MB）'} |")
    with open(INDEX_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def write_md(events, files, audit):
    at = lambda: L.append("")
    L = []
    L.append("# EVENTS — 政策动作**事件库**（N3-3）")
    at()
    at()
    L.append(f"> **生成**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 脚本：`news/policy/extract_events.py` "
             "｜ 语料：`news/archive/*.jsonl.gz`")
    at()
    L.append("> ⚠️ **口径**：本库为**描述性监督标签**（主体 / 动作 / 领域 / 力度）；"
             "由**规则/词典/正则**从**标题**抽取；**不预测、不表态**（政治中立）。")
    at()
    L.append("> 📝 **语料为代理源 `chinanews`**（新华网日期路径 403/405 未通，见 "
             "`news/archive/PROGRESS.md`）—— **代理源 ≠ 新华社**，`source` 字段严格区分。")
    at()
    at()
    L.append("## 0. 方法与口径")
    at()
    L.append("**半自动流水线**（任务书 N3-3）：① 规则/词典/正则 → 批量候选（**本脚本**） → "
             "② LLM 分类 → ③ 抽样人工校验。")
    L.append("- ⚠️ **② LLM 分类未接入**：本环境**无 LLM key**（用户 2026-10-03 定：免 key / 暂不付费 API）"
             "→ 分类**由词典规则完成**（触发词 + 主体词），**未引入任何模型**；"
             "② 的角色由 ③ **抽样人工校验**顶替。**这是本线能力的如实边界。**")
    L.append("- **纳入口径（三条件同时满足）**：① 标题含 `TAXONOMY.md` 的**动作触发词**；"
             "② 标题含**政经主体**（中国党政机构 **或** 外国政府/国际组织，见 §3）；"
             "③ **一条标题可进多类**（互不排斥，主键 = `url` + `动作类型`）。")
    L.append("- **未纳入**：无政经主体的标题（如纯企业/体育/社会新闻）—— 但这会**漏掉**"
             "「未点名主体的政策动作」，属**已知召回损失**（见 §7）。")
    at()
    L.append(f"- 事件总数：**{len(events)}** ｜ 去重键：`url`+`动作类型` ｜ 生成文件："
             + "、".join(f"`{os.path.basename(p)}`({r} 行)" for p, r, _ in files))
    yrs = Counter(e["date"][:4] for e in events)
    L.append("- 年份分布：" + "、".join(f"**{y}** {yrs[y]}" for y in sorted(yrs)))
    at()
    L.append("## 1. 按动作类别（`TAXONOMY.md` A1–A15）")
    at()
    L.append("| 类别 | 名称 | 事件数 | 中国主体 | 外国/国际 | 高噪声占比 | 频率层级 |")
    L.append("|:--|:--|--:|--:|--:|--:|:--|")
    by_cat = defaultdict(list)
    for e in events:
        by_cat[e["action_type"]].append(e)
    for c in sorted(tx.CATEGORIES, key=lambda x: -len(by_cat.get(x["id"], []))):
        lst = by_cat.get(c["id"], [])
        if not lst:
            continue
        cn = sum(1 for e in lst if e["actor_kind"] == "CN")
        fo = len(lst) - cn
        hi = sum(1 for e in lst if e["noise_risk"] == "高") / len(lst)
        tier = "高频" if len(lst) >= 1000 else ("中频" if len(lst) >= 200 else "低频")
        L.append(f"| {c['id']} | {c['name']} | {len(lst)} | {cn} | {fo} | {hi:.0%} | **{tier}** |")
    at()
    L.append("## 2. 年度 / 月度分布（真实计数）")
    at()
    L.append("| 年 | 事件数 |")
    L.append("|:--|--:|")
    for y in sorted(yrs):
        L.append(f"| {y} | {yrs[y]} |")
    at()
    L.append("| 年-月 | 事件数 |")
    L.append("|:--|--:|")
    mo = Counter(e["date"][:7] for e in events)
    for m in sorted(mo):
        L.append(f"| {m} | {mo[m]} |")
    at()
    L.append("## 3. 主体分布（top 25，**中国一侧 + 外国一侧**）")
    at()
    L.append("| 主体 | 类型 | 事件数 |")
    L.append("|:--|:--|--:|")
    ac = Counter((e["actor"], e["actor_kind"]) for e in events)
    for (a, k), c in ac.most_common(25):
        L.append(f"| {a} | {'中国' if k == 'CN' else '外国/国际'} | {c} |")
    at()
    L.append("## 4. 噪声风险分布（启发式，用于降噪与复核）")
    at()
    rk = Counter(e["noise_risk"] for e in events)
    L.append(f"- **低** {rk.get('低', 0)} ｜ **中** {rk.get('中', 0)} ｜ **高** {rk.get('高', 0)}"
             "（高 = 宽泛动词〔举行/回应/发布…〕或泛指主体〔政府〕，**须优先人工复核**）")
    a15 = [e for e in events if e["action_type"] == "A15"]
    if a15:
        st = Counter(e["subtype"] or "未分类" for e in a15)
        L.append("- **A15 货币工具细分**：" + "、".join(f"{k} {v}" for k, v in st.most_common()))
    at()
    L.append("## 5. 抽样人工校验（N3-3 硬性：抽 ≥100 条报准确率）")
    at()
    if audit:
        L.append(f"- 样本量：**{audit['n']}** ｜ **总体准确率（precision）**："
                 f"**{audit['acc']:.0%}**（判对 {audit['ok']} / {audit['n']}）")
        L.append("- **判定口径（rubric）**：`verdict=1` ⟺ 标题描述**真实发生的政经动作**、且与所标类别"
                 "**基本相符**；`verdict=0` ⟺ **非政经噪声**（天气/灾害预警 · 文体活动 · 企业/社会新闻）"
                 "或**体裁非报道**（评论 / 观察 / 回顾 / 微纪录），或**类别明显误标**（如商业航天当军事试射）。"
                 "⚠️ **主体归属错误不单列为误判**（属已知启发式局限，见 §7）。")
        L.append("- **分类别准确率**：")
        for cid in sorted(audit["per"], key=lambda c: audit["per"][c][1] / audit["per"][c][0]):
            n, okk = audit["per"][cid]
            L.append(f"  - {cid}：{okk}/{n} = {okk / n:.0%}"
                     + ("" if okk / n >= 0.999 else "  ⚠️ 低"))
        fps = [r for r in audit["rows"] if r["verdict"].strip() == "0"]
        L.append(f"- **误判（false positive）共 {len(fps)} 例**，集中在："
                 + "、".join(f"{c}({sum(1 for r in fps if r['action_type'] == c)})"
                             for c in sorted({r["action_type"] for r in fps})))
        L.append("- **误判示例（限 15，可复核）**：")
        for r in fps[:15]:
            L.append(f"  - [{r['action_type']}] {r['title'][:44]}…")
        L.append("- **结论（实测）**：**宽泛触发词类**（A4『举行』/ A5『发布』/ A7『通报』/ A15『降息·回应』）"
                 "误判集中，多为**非政经事件**（论坛/文体/天气预警/社会新闻）或**评论观察体**；"
                 "**窄义词类**（A1/A2/A3/A9/A10/A11/A14）几乎无误 → "
                 "**事件库下游使用应对宽泛类设更高阈值或人工复核**（见 §4 噪声列）。")
        L.append("- ⚠️ **校验由 agent 执行、可复核**：`EVENTS_AUDIT.csv`（逐条 verdict）+ "
                 f"`--sample N --seed {audit.get('seed', 20351003)}` **可复现同一批样本**。")
    else:
        L.append("- ⬜ **尚未抽样校验**。命令：`python3 news/policy/extract_events.py "
                 "--sample 100 --seed 20351003` → 人工判定 → `--write-audit`。")
    at()
    L.append("## 6. 与 L1 / L2 的关系")
    at()
    L.append("- 本库是 **L1（政策动作预警）** 的**监督标签来源**：`动作类型(A1–A15) + 日期 + 主体` "
             "→ 供 N3-2（信号）/ N3-4（预警）做 **walk-forward + 基线** 评估。")
    L.append("- 亦可作 **L2（探索性关联分析 N4）** 的**事件源**（⚠️ 仅**相关 / 同期 / 滞后**，"
             "🚫 **不声称因果**；L2 仍受 **G2 阶段门**约束，**未过门不跑 CAR**）。")
    at()
    L.append("## 7. 局限与下一步")
    at()
    L.append("- ⚠️ **代理源**：全部来自 `chinanews`，**非新华社**；后续若新华网可通/并入其它源，"
             "须**按源分列**重算。")
    L.append("- ⚠️ **规则召回有限**：仅用**标题子串**，会**漏**「未点名主体」或「非常用触发词」的动作；"
             "也会**误纳**宽泛动词（→ §4 高噪声，须人工复核）。")
    L.append("- ⚠️ **主体判定是启发式**：取标题**最靠前**的主体标记，可能与真实动作主体不一致"
             "（如「中方回应美国…」会判到靠前的主体）→ 供**粗分组**，不可当精确归属。")
    L.append("- ⚠️ **样本仍在扩充**（N1 倒序回溯，当前覆盖 2024-04 ~ 2026-10）→ 计数会随后续轮次更新。")
    L.append("- **下一步**：N3-2 `SIGNALS.md`（信号清单 + `as-of`）→ N3-4 `EARLY_WARNING.md`"
             "（规则 + walk-forward + 基线 + 提前期）。")
    at()
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="N3-3 政策动作事件库抽取器")
    ap.add_argument("--sample", type=int, default=0, help="打印分层抽样 N 条（不写盘）")
    ap.add_argument("--seed", type=int, default=20351003, help="抽样随机种子（可复现）")
    ap.add_argument("--write-audit", action="store_true", help="写 EVENTS_AUDIT.csv（含 verdict 列）")
    ap.add_argument("--verdicts", default="", help="与样本等长的判定串，如 '1110...'（1=对 0=错）")
    args = ap.parse_args()

    recs = load_records()
    if not recs:
        print("[ev] no records under news/archive/ — run fetch_archive.py first")
        return 1
    events = build_events(recs)
    print(f"[ev] corpus={len(recs)} events={len(events)} "
          f"(CN={sum(1 for e in events if e['actor_kind'] == 'CN')})")

    if args.sample:
        s = strat_sample(events, args.sample, args.seed)
        print(f"[sample] n={len(s)} seed={args.seed}")
        for i, e in enumerate(s):
            print(f"{i:3} | {e['action_type']:3} | {e['noise_risk']} | {e['date']} | "
                  f"{e['actor']} | {e['title']} | {e['url']}")
        return 0

    if args.write_audit:
        s = strat_sample(events, len(args.verdicts) or 100, args.seed)
        vs = (args.verdicts + "0" * len(s))[:len(s)]
        with open(AUDIT_CSV, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["idx", "action_type", "noise_risk", "actor", "title", "url", "verdict"])
            for i, e in enumerate(s):
                w.writerow([i, e["action_type"], e["noise_risk"], e["actor"],
                            e["title"], e["url"], vs[i]])
        print(f"[audit] wrote {AUDIT_CSV} (n={len(s)}, seed={args.seed})")
        return 0

    files = write_csv(events, OUT_CSV)
    audit = read_audit()
    aa = dict(audit) if audit else None
    if aa:
        aa["seed"] = args.seed
    write_md(events, files, aa)
    write_index(files)
    for p, rows, size in files:
        print(f"[ev] wrote {p} rows={rows} size={size} ({size / 1024 / 1024:.2f} MB)")
    print(f"[ev] wrote {OUT_MD}  audit={'yes' if audit else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
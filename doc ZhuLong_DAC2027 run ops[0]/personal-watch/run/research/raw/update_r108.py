#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零八轮（本地 2026-10-23 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次已刷新**：`2026-10-21` -> **`2026-10-22`**（totalResults 636928 -> 637451（+523），
  最新样本 published=2026-10-22T17:59:53Z）；`--fetch --seen`（window_mode=daily 72h，
  generated=2026-10-23T10:01:53Z）15/15 ok（全部 attempts=1）、**kept 160 / dropped 429**。
- 晚报 2 篇「科普」直接取自本批：2610.31651 BrickWright（LEGO 实体可行搭建）/ 2610.30769
  LLM 多智能体羊群效应与失控级联 -> SEEN 追加 160 行（2 收录 + 158 候选），4452 -> 4612
  -> papers.jsonl 追加 2 行（239 -> 241）
- 元数据取自 id_list 权威复核 raw/2026-10-23-idlist-r108{a,b}.xml（官方 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-23-fetch-r108-seen.json"
XMLS = [BASE / "raw" / "2026-10-23-idlist-r108a.xml", BASE / "raw" / "2026-10-23-idlist-r108b.xml"]

FIRST_SEEN = "2026-10-23"
RECOMMENDED = ["2610.31651", "2610.30769"]

SUMMARY_ZH = {
    "2610.31651": (
        "前沿 coding agent 已能做 3D 建模，但让它们生成「要在物理世界拼装」的物体时仍常失败："
        "出现悬空件、穿模件或互不连通的零件。作者认为，只要给 agent 一套拼装工具 + 物理可行性校验器就够；"
        "以 LEGO 积木为场景提出 BrickWright：agent 通过 Python 工具包 BrickLayer 写拼装代码"
        "（面向积木的操作 API + 可行性校验器），由校验器回传「悬空 / 穿模 / 不连通 / 非真实零件」等反馈。"
        "可行性定义为：只用真实零件、无穿模、无悬空、尽可能连成一体。在 512 条提示上，"
        "基线 agent 的物理可行率仅 9%（GPT-6 Luna）到 69%（GPT-6 Astra），BrickWright 引导下达到 100%，"
        "同时提升轻量模型的提示遵循度、对强模型保持不降；在文本→积木任务上超过专用模型。"
        "⚠️ 只测 LEGO 积木这一域；「可行性」是几何/拓扑判据，不含真实结构强度与拼装顺序；"
        "数字作者自报、本线未复现；未做全文精读。"
    ),
    "2610.30769": (
        "LLM 越来越多地以多智能体系统协作：彼此回应对方的选择，形成内生反馈回路，"
        "因而可能像人类社会一样出现从众、羊群效应与失控级联。作者沿用经典 Music Lab 实验设计，"
        "让大规模 LLM 智能体在不熟悉歌曲上做推荐，分「可见累计推荐数」与「不可见」两组。"
        "结果显示：可见他人选择会引发失控级联，使集体推荐极端且不可预测、越来越偏离歌曲本身的质量；"
        "与人类相比，LLM 群体总体上对从众更敏感，且级联发生后更难以自我纠偏。"
        "作者指出该脆弱性对推荐系统、自动评测、复杂问题求解与「未授权的合谋」都有影响。"
        "⚠️ 实验基于经典 Music Lab 范式与特定模型族/提示；「比人类更容易从众」的比较依赖该范式；"
        "数字作者自报、本线未复现；未做全文精读。"
    ),
}

AREAS = {
    "2610.31651": ["agent", "3D 建模", "LEGO", "物理可行性校验", "generate-execute-refine", "ZhuLong"],
    "2610.30769": ["多智能体", "羊群效应", "级联", "社会影响", "评测", "科普"],
}


SUMMARY_LINE = (
    "> **第一百零八轮（本地 2026-10-23 18:00（CST）· P0 第 5 批第 6 轮「晚 2」轮 · 当日收口）**："
    "**公告批次已刷新** —— `2026-10-21` → **`2026-10-22`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults` `636928` → **`637451`**（+523），最新样本 `published=2026-10-21T17:59:14Z` → **`2026-10-22T17:59:53Z`**）；"
    "**15/15 查询 `ok`**（**全部 `attempts=1`**）、**`kept 160` / `dropped 429`**"
    "（`window_mode=daily` 72h，`generated=2026-10-23T10:01:53Z`；160 条 `published` 分布 2026-10-22 = 137 / 2026-10-21 = 23）。"
    "R1′ arXiv ✅（首次 `ConnectTimeout`、重试后 `200`）/ HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 超时 · cs.CV 192 · cs.LG 339（仅作发现）。"
    "**晚报 2 篇「科普」直接取自本批** + **单条权威复核**"
    "（`id_list` 两批 3+3 → **6/6 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；"
    "证据 `raw/2026-10-23-idlist-r108{a,b}.{xml,headers}`）："
    "`2610.31651` BrickWright: Agentic Creation of Physically Feasible Brick Builds（**本日 TOP-1**）/ "
    "`2610.30769` LLM Multi-Agent Systems Are Vulnerable to Herding and Runaway Cascades。"
    "台账 **4,452 → 4,612 行（+160）**（2 行「收录」+ 158 行「候选」）→ 累计（**收录 241 / 候选 3,864 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **239 → 241**；PDF 5/5 落地校验通过；落盘脚本 `raw/update_r108.py`。口径见 `ARXIV_API.md` §9.108。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom",
          "x": "http://arxiv.org/schemas/atom"}
    official = {}
    for p in XMLS:
        root = ET.parse(p).getroot()
        for e in root.findall("a:entry", ns):
            aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
            cat = e.find("x:primary_category", ns)
            com = e.find("x:comment", ns)
            official[aid] = {
                "arxiv_id": aid,
                "title": " ".join(e.find("a:title", ns).text.split()),
                "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
                "published": e.find("a:published", ns).text,
                "updated": e.find("a:updated", ns).text,
                "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
                "comment": com.text if com is not None else "",
                "summary": " ".join(e.find("a:summary", ns).text.split()),
            }
    assert len(official) == 6, "expected 6 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-22"), official[k]["published"]
    return official


def main():
    official = load_official()
    items = json.load(FETCH.open(encoding="utf-8"))["items"]
    assert len(items) == 160, len(items)

    # 1) SEEN: 追加 160 行（2 收录 + 158 候选）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    existing = set()
    for ln in lines:
        m = re.match(r"^\| \d{4}-\d\d-\d\d \| ([^ |]+) \|", ln)
        if m:
            existing.add(m.group(1))
    if lines and lines[-1] != "":
        lines.append("")
    added = 0
    for it in items:
        aid = it["arxiv_id"]
        assert aid not in existing, "%s already in SEEN" % aid
        status = "收录" if aid in RECOMMENDED else "候选"
        title = " ".join(it["title"].split())
        lines.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
        added += 1
    assert added == 160, added
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加 2 行
    have = set()
    with PAPERS.open(encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                have.add(json.loads(ln)["arxiv_id"])
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            assert k not in have, "%s already in papers.jsonl" % k
            e = official[k]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": e["authors"],
                "submitted": e["published"][:10],
                "updated": e["updated"][:10],
                "category": e["category"],
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": FIRST_SEEN,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 3) 统计
    st = {}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows appended:", added)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十二轮（本地 2026-10-30 18:00 PM「晚 2」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-30-pm-fetch-r122-seen.json`（`--fetch --seen`，`generated=2026-10-30T10:04:23Z`）
  - `raw/2026-10-30-pm-idlist-r122a.xml`（官方 Atom 元数据，2 条）

动作：
  1) 断言：15 查询全 `ok` / `HTTP 200`（2 条 `attempts=2` 后成功）、`kept 217` / `dropped 357`、
     `window_mode=daily`、`items==217`；
  2) `SEEN.md`：217 条新候选按「首次提交」倒序插入表格末尾（首次收录 = 2026-10-30）；
     其中 2 条推荐论文直接记「收录」；
  3) `papers.jsonl`：追加 2 条（元数据取自官方 id_list XML）；
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-30-pm-fetch-r122-seen.json"
XML = BASE / "raw" / "2026-10-30-pm-idlist-r122b.xml"

RECOMMENDED = ["2610.40599", "2610.40589"]
FIRST_SEEN = "2026-10-30"
EXPECT_PUB = {"2610.40599": "2026-10-29", "2610.40589": "2026-10-29"}

AREAS = {
    "2610.40599": ["多模态", "3D 生成", "游戏美术资产", "头发建模（hair cards）", "单图生成", "科普"],
    "2610.40589": ["LLM", "agent harness", "自主实验", "AI for Science", "量子自旋", "科普"],
}

SUMMARY_ZH = {
    "2610.40599": (
        "游戏/虚拟人角色的头发，业界一直用「发卡（hair cards）」——美术手摆的带状面片，"
        "由弹簧骨骼（spring bones）驱动动画。本文提出 **HairDeck**：把一套发卡当成**无序集合**，"
        "每张发卡 = 一个 token，用**集合扩散 Transformer** 一次性去噪生成全部发卡，"
        "**并且同时生成驱动它们的弹簧骨骼链**，因此单张图片即可得到可直接导出、能动的资产。"
        "在 CHARM 自己的测试集上：Chamfer 距离 **降低 44%**、发卡朝向误差 **减半以上**、"
        "运行速度 **快 33 倍**；单图输入下优于 CHARM、image-to-3D 流水线与基于发丝（strand）的方法。"
        "⚠️ 对比基线是「唯一一个同类生成器」CHARM 及通用 image-to-3D/strand 方法；"
        "作者自报、本线未复现。"
    ),
    "2610.40589": (
        "把「自主实验室」做成**能自我否决**的多智能体闭环：一组基于大模型的 agent 各自承担提问、理论推导、"
        "实验设计与复核，**可以否决或改向别人的工作**。任务：在金刚石色心（固态量子自旋）体系里，"
        "推出「预测给定一族微波脉冲序列的响应」所需的**最少标定设置数**，并设计实验区分竞争性预测。"
        "首次实验与理论一致，但重复的参考测量显示**信号在采集中漂移**⇒ agent 判定「不确定」，"
        "**在不放宽验收标准的前提下**修改测量协议；修订版实验通过标准并支持理论预测。"
        "⚠️ 17 页 / 5 图；判定链与实验协议由 LLM agent 生成，作者的「自主」为标准内的自主；"
        "作者自报、本线未复现。"
    ),
}


def load_official():
    root = ET.parse(XML).getroot()
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    out = {}
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [a.find("a:name", ns).text for a in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": e.find("x:primary_category", ns).attrib["term"],
        }
    assert len(out) == 2, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return out


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)
ROW_RE = re.compile(r"^\| [0-9-]{10} \| ([0-9.]+) \|")


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 217, meta["n_kept"]
    assert meta["n_dropped"] == 357, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert sum(1 for a in attempts if a == 2) == 2, attempts
    assert len(items) == 217, len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    print("dropped: already_in_SEEN=%d stale=%d" % (n_seen, n_stale))

    ids = [it["arxiv_id"] for it in items]
    assert len(set(ids)) == 217, "dup ids in items"
    for k in RECOMMENDED:
        assert k in ids, "%s not in kept items" % k

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    before = set()
    for ln in lines:
        m = ROW_RE.match(ln)
        if m:
            before.add(m.group(1))
    assert not (set(ids) & before), "kept id already in SEEN: %s" % (set(ids) & before)
    assert not (set(RECOMMENDED) & before), "recommended already present in SEEN"

    last_row = max(i for i, ln in enumerate(lines) if ANY_ROW_RE.match(ln))
    new_rows = []
    for it in sorted(items, key=lambda x: x["published"], reverse=True):
        aid = it["arxiv_id"]
        title = " ".join(it["title"].split()).replace("|", "\\|")
        status = "收录" if aid in RECOMMENDED else "候选"
        new_rows.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
    lines[last_row + 1:last_row + 1] = new_rows
    SEEN.write_text("\n".join(lines), encoding="utf-8")

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

    st = {}
    for ln in lines:
        m = ANY_ROW_RE.match(ln)
        if m:
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN lines:", len(lines), "(+%d)" % len(new_rows))
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零六轮（本地 2026-10-22 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次已刷新**：`2026-10-20` -> `2026-10-21`（主源 totalResults 636364 -> 636926，
  最新样本 published=2026-10-21T17:59:14Z）；`--fetch --seen`（window_mode=daily 72h，
  generated=2026-10-22T10:01:39Z）15/15 ok（sweep-cs-5cats attempts=2 一次重试成功）、
  **kept 158 / dropped 415** -> 158 条全部首次发现。
- 晚报 2 篇「科普」取自本 PM 轮新批：
  2610.29025 Single-Image Food Mass Estimators ...（TOP-1）/ 2610.30035 Plausible but Unimplantable ...
  -> SEEN 新增 158 行（2 行「收录」+ 156 行「候选」），4,294 -> 4,452
  -> papers.jsonl 追加 2 行（234 -> 236）
- 元数据取自 id_list 权威复核 raw/2026-10-22-idlist-r106.xml（官方 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-10-22-idlist-r106.xml"
FETCH = BASE / "raw" / "2026-10-22-fetch-r106-seen.json"

FIRST_SEEN = "2026-10-22"
RECOMMENDED = ["2610.29025", "2610.30035"]

SUMMARY_ZH = {
    "2610.29025": (
        "用 Nutrition5k 的 2,253 个已称重餐盘微调 DINOv2-base，从单张 RGB 照片预测食物质量；"
        "域内平均绝对误差 24.8 g（不到零样本 Qwen3-VL-32B 的一半），但在三个外部数据集"
        "（ASA24 studio portions / ECUSTFD whole foods / Food Portion Benchmark meal trays）上并不优于 Qwen。"
        "对没见过的食物它会按大小排序，但不比「数食物像素」更强。"
        "其克数尺度有两种错法：随照片覆盖场景的比例变化，且每种食物的偏移因子不同。"
        "用该数据集里其他食物 / 餐盘训练可把外部误差降低 38–65%；更大的 DINOv2-large 并未降低外部误差；"
        "同一食物加一张有标注照片可把 ASA24 误差降到 28.3 g（好于该照片单用）。"
        "在 Nutrition5k 上覆盖 90% 真值的预测区间，在外部照片上至多覆盖一半；"
        "Nutrition5k 常对同一餐盘多拍，随机切分会与训练集共享近似重复照片、夸大精度。"
        "结论：单图质量估计需要来自实际使用场景的标注照片。"
        "⚠️ 单一作者；只测质量、不含热量与成分；数字作者自报、本线未复现；未做全文精读。"
    ),
    "2610.30035": (
        "颅骨缺损植入物目前仍由专家在 CAD 中手工绘制，作者把该任务视为 shape completion，"
        "审计 3 个公开预训练补全模型（其中 2 个为 foundation model）零样本用于 239 个颅骨缺损"
        "（210 个从公开颅骨数据集人工挖出 + 29 个真实去骨瓣术后病例）。"
        "每个输出都与「直接返回患者剩余骨」比较，并检验预测材料能否在不与现存骨相交的前提下放置。"
        "210 个挖出缺损上 3 个模型没有一个超过「什么都不做」；29 个真实病例上只有一个超过随机水平。"
        "且没有任何一个输出是可植入的：没有一个同时做到避开现存骨、又比什么都不做放置更多材料；"
        "而一个为此任务训练、并在这些病例上选型的体素模型除 1 例外全部可植入。"
        "最像颅骨的那个输出并不比其它更可放置；在这些点密度下植入物厚度无法从输出点云读出，"
        "这是输出表示本身的属性而非某个模型的问题。结论：这些模型按发布状态不可信、不可用于临床，"
        "可信的 shape completion 基础模型仍需大量研究。"
        "⚠️ 结论仅针对作者可获得并审计的 3 个模型；数字作者自报、本线未复现；未做全文精读。"
    ),
}

AREAS = {
    "2610.29025": ["食物质量估计", "跨数据集迁移", "饮食评估", "视觉语言模型", "科普"],
    "2610.30035": ["形状补全", "基础模型审计", "颅骨植入物", "医疗可信度", "零样本", "科普"],
}

SUMMARY_LINE = (
    "> **第一百零六轮（本地 2026-10-22 18:00（CST）· P0 第 5 批第 3 轮「晚 2」轮 · 当日收口）**："
    "**公告批次已刷新** —— `2026-10-20` → **`2026-10-21`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults` `636364` → **`636926`**（+562），最新样本 `published=2026-10-20T17:59:56Z` → **`2026-10-21T17:59:14Z`**；"
    "周三 20:00 ET 公告已落地）；**15/15 查询 `ok`**（`sweep-cs-5cats` `attempts=2` 一次脚本级重试后成功，其余 `attempts=1`）、"
    "**`kept 158` / `dropped 415`**（`window_mode=daily` 72h，`generated=2026-10-22T10:01:39Z`）→ **158 条全部首次发现**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 221 · cs.CV 212 · cs.LG 379（仅作发现）。"
    "**晚报 2 篇「科普」取自本 PM 轮新批 158 条** + **单条权威复核**"
    "（`id_list=2610.29025,2610.30086,2610.30035,2610.30125,2610.30089` → **5/5 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-22-idlist-r106.{xml,headers}`）："
    "`2610.29025` Single-Image Food Mass Estimators Do Not Transfer Their Gram Scale Across Datasets（**本日 TOP-1**）/ "
    "`2610.30035` Plausible but Unimplantable: A Trustworthiness Audit of Shape Completion Foundation Models for Cranial Defect Reconstruction。"
    "台账 **4,294 → 4,452 行（+158）**（2 行「收录」+ 156 行「候选」）→ 累计（**收录 236 / 候选 3,709 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **234 → 236**；PDF 2/2 落地校验通过（并入当日 3 篇共 5 篇）；"
    "落盘脚本 `raw/update_r106.py`。口径见 `ARXIV_API.md` §9.106。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom",
          "x": "http://arxiv.org/schemas/atom"}
    root = ET.parse(XML).getroot()
    official = {}
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
    assert len(official) == 5, "expected 5 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-21"), official[k]["published"]
    return official


def main():
    official = load_official()
    fetched = json.loads(FETCH.read_text(encoding="utf-8"))["items"]
    assert len(fetched) == 158, len(fetched)

    # 1) SEEN: 追加 158 行（2 收录 + 156 候选）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    existing = set()
    for ln in lines:
        m = re.match(r"^\| \d{4}-\d\d-\d\d \| ([^ |]+) \|", ln)
        if m:
            existing.add(m.group(1))
    added = 0
    for it in fetched:
        aid = it["arxiv_id"]
        assert aid not in existing, "%s already in SEEN" % aid
        title = it["title"].replace("|", "\\|")
        status = "收录" if aid in RECOMMENDED else "候选"
        lines.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
        existing.add(aid)
        added += 1
    assert added == 158, added
    if lines and lines[-1] != "":
        lines.append("")
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
    print("SEEN rows appended: %d" % added)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十八轮（本地 2026-10-18 18:00 P0「晚 2」轮 · PM · 当日收口）结果落盘。

- 本轮 PM：**无新公告批次**（周日 arXiv 不公告；批次仍 2026-10-15；
  `--fetch` window_mode=weekend_batch 120h → kept 0 / dropped 600，15/15 ok）
  -> 晚报 2 篇「科普」取自**前轮（第九十四轮 PM）已入账的窗口内候选池**
  -> SEEN.md 对应 2026-10-16「候选」行改为「收录」
- 2 篇推荐（均「科普」）：2610.22340 Dexterity from Supervised Play（本日 TOP-1）/ 2610.21011 狗声纹识别
  -> papers.jsonl 追加 2 行（214 -> 216）
- 元数据取自 id_list 权威复核 raw/2026-10-18-idlist-shortlist-r98.xml（含官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

FIRST_SEEN = "2026-10-18"
RECOMMENDED = ["2610.22340", "2610.21011"]

SUMMARY_ZH = {
    "2610.22340": "作者提出 **DSP（Dexterity from supervised play）**：机器人先从**数分钟人类玩耍**中通过行为克隆学到一个「玩耍策略」，再**自主部署**该策略收集**数小时交互数据**训练世界模型；推理时同一个玩耍策略为**模型预测控制（MPC）**提出候选动作序列，由世界模型评估挑选；并可在世界模型内通过**自博弈蒸馏**得到闭环、目标条件策略以加速推理。作者在**欠驱动推动**与**多指手 any-to-any 手内姿态重定向**（仿真 + 真实）上评估：真实世界成功率比 hindsight behavior cloning 高 69.6%，并与强化学习效果相当而交互数据少 490 倍。⚠️ 数字为作者自报、本线未复现。",
    "2610.21011": "作者提出**多模态「狗狗指纹」框架**，把**视觉身份识别 + 多目标跟踪 + 犬吠声纹**结合：同步吠叫事件与跟踪到的狗，用外观与声音特征持续更新个体档案，从而在**遮挡、同时吠叫、画外叫声**等情形下把叫声归属到具体个体。作者发布 **46 段真实视频 / 213 个手工标注吠叫事件**的基准：可见事件中正确定位「正在叫的可见狗」占 61.83%（IoU ≥ 0.30），画面内 vs 画外吠叫判别 F1 达 91.33%。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.22340": ["机器人", "灵巧操作", "世界模型", "模仿学习", "MPC"],
    "2610.21011": ["多模态", "声纹", "多目标跟踪", "动物行为监测"],
}


def main():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-18-idlist-shortlist-r98.xml").getroot()
    by = {}
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        cat = e.find("{http://arxiv.org/schemas/atom}primary_category")
        by[aid] = {
            "arxiv_id": aid,
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
        }
    for k in RECOMMENDED:
        assert k in by, "missing %s" % k

    # 1) SEEN: 候选 -> 收录（行数不变）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    changed = 0
    for i, ln in enumerate(lines):
        for k in RECOMMENDED:
            if ln.startswith("| 2026-10-16 | %s |" % k) and ln.rstrip().endswith("| 候选 |"):
                lines[i] = ln[: -len("| 候选 |")] + "| 收录 |"
                changed += 1
    assert changed == len(RECOMMENDED), "expected %d changed, got %d" % (len(RECOMMENDED), changed)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by[k]
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
    st = {"收录": 0, "候选": 0, "候选（RSS补充）": 0}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

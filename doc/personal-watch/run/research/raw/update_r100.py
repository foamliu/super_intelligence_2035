#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百轮（本地 2026-10-19 18:00 P0「晚 2」轮 · PM · 当日收口）结果落盘。

- 本轮 PM：**公告批次已刷新 2026-10-15 → 2026-10-16**（周一 20:00 ET 公告落地）
  -> 15 查询全量 `--fetch` 遭 arXiv 429（如实记 FAIL），改用**单条发现查询**
     `cat:cs.CV OR cat:cs.RO OR cat:cs.MM`（HTTP 200，60 条，最新 published=2026-10-16T17:59:55Z）
  -> 晚报 2 篇「科普」取自该新批，并逐条 `id_list` 权威复核（2/2）
- 2 篇推荐：2610.23438 No Eyes, No Problem（**本日 TOP-1**）/ 2610.23813 MOSS
  -> SEEN.md **追加 2 行**（新 ID，状态=收录）
  -> papers.jsonl 追加 2 行（219 -> 221）
- 元数据取自 raw/2026-10-19-idlist-pm-r100.xml（官方 Atom，含 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

FIRST_SEEN = "2026-10-19"
RECOMMENDED = ["2610.23438", "2610.23813"]

SUMMARY_ZH = {
    "2610.23438": "研究「没有视觉时，机器人能否只靠触觉在手里持续操作物体」。作者让人形灵巧手（Shadow Dexterous Hand Lite）在仿真中用强化学习学**保定铁球（Baoding ball）旋转**，观测只有**本体感觉 + 二值触觉**；为跨过 sim-to-real，设计了传感器对齐的耦合建模、触觉标定，以及两种新的回合级域随机化（**slew-rate 动作限幅**与 **STuck-AT Taxels** 模拟卡死触觉点）。在真实手上实现**零样本迁移**：单次连续试验中完成 **225 次连续 180° 旋转（=112.5 整圈）**、约 **0.36 转/秒**，全程无视觉、无物体状态信息；并对比「只有本体感觉」与「本体+触觉」，定位触觉最关键的掌部区域。作者称这是**不论传感模态**下保定球操作在旋转次数与速度上的最强硬件结果（作者自报，本线未复现）。",
    "2610.23813": "面向湿地 / 沼泽的环境监测，提出 **MOSS（Multimodal Origami Swamp Robot System）**：一台紧凑两栖机器人，轮子用 **3D 打印折纸结构**，由曲柄机构在**收缩 / 展开**两种构型间切换，同时改变轮宽、轮体直径与鳍片朝向。收缩态适合硬地高效滚动，展开态在软地面提供更大接触与抓地。作者在土、沙、不同含水量的泥、水中评测，并测试行进中变形与陆水过渡：更省能的构型取决于地形 —— 收缩态在较硬土壤与泥地成本更低，展开态在更湿的泥、沙与水中**降低运输成本最多 29%**，并减少湿泥打滑、沙中下陷；构型切换耗时 **1.95 ± 0.11 s**，可连续跨越土—泥—水。户外试验验证了自然变形地面与水面运行（作者自报，本线未复现；comment 自述投稿 ICRA 2027，本线未核会务）。",
}

AREAS = {
    "2610.23438": ["触觉", "灵巧操作", "sim-to-real", "强化学习", "域随机化"],
    "2610.23813": ["两栖机器人", "折纸结构", "变形轮", "环境监测", "地形适应"],
}


def main():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-19-idlist-pm-r100.xml").getroot()
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

    # 1) SEEN: 追加 2 行（新 ID）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    existing = "\n".join(lines)
    new_rows = []
    for k in RECOMMENDED:
        assert ("| %s |" % k) not in existing, "already in SEEN: %s" % k
        e = by[k]
        new_rows.append("| %s | %s | %s | %s | 收录 |" % (FIRST_SEEN, k, e["title"], e["category"]))

    # 插到表格末尾（最后一条 | 2026- 行之后）
    last = max(i for i, ln in enumerate(lines) if ln.startswith("| 2026-"))
    lines[last + 1:last + 1] = new_rows
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

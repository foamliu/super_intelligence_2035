#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十六轮（本地 2026-10-17 18:00 P0「晚 2」轮 · PM · 当日收口）结果落盘。

- 本轮 PM：**无新公告批次**（批次仍 2026-10-15；`--fetch` window_mode=weekend_batch 120h
  → kept 3 / dropped 597；3 条均为 10-12 批的**旧条目补漏**，非新批）
  -> 晚报 2 篇「科普」取自**前轮（第九十四轮 PM）已入账的窗口内候选池**
  -> SEEN.md 对应 2026-10-16「候选」行改为「收录」
- 新发现 3 条（2610.16621 / 2610.16537 / 2610.16518）以「候选」追加进 SEEN（防重复评估）
- 2 篇推荐（均「科普」）：2610.22371 Gen4P（TOP-1） / 2610.22372 LIBERO-PeRM
  -> papers.jsonl 追加 2 行（209 -> 211）
- 元数据取自 id_list 权威复核 raw/2026-10-17-idlist-shortlist-r96.xml（含官方 published/作者/comment）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-17-fetch-r96-seen.json"

FIRST_SEEN = "2026-10-17"
RECOMMENDED = ["2610.22371", "2610.22372"]

SUMMARY_ZH = {
    "2610.22371": "作者提出 Gen4P：把**预训练视频生成器**改造成**前馈 4D 感知器**，**无需迭代去噪** —— 单次编码器前向处理干净的视频 latent，再用轻量 **cross-attention 解码器**按查询预测所需 4D 属性；**按需查询（on-demand query）**支持灵活的空间采样，**连续时间查询**带来时间上的灵活性；并给出一个即插即用方案：把预训练的视频深度 LoRA 作为**冻结的几何先验**，在不增加可训练参数的情况下提升整体表现。作者称在 **3D 点跟踪 / 视频深度 / 相机位姿估计**上达到 **SOTA 或具竞争力**，并在真实场景视频上展示了跟踪复杂运动同时保持细节结构的能力。⚠️ 数字与结论为作者自报、本线未复现。",
    "2610.22372": "作者提出 **LIBERO-PeRM**：一个面向**个性化机器人操作（PeRM）**的基准，用于在仿真中把「**完成任务**」与「**满足偏好**」分开评估。作者给出可控的偏好表述与分类（覆盖**动作、技能、用户画像**选择），限定为**可用语言表达、可自动评测、可跨任务复用**且**不改变任务目标**的偏好；基于 LIBERO 用程序化流水线生成**成对演示（含偏好 / 不含偏好）**，构建 **5 个任务套件、共 312 个任务**，配高质量演示、丰富元数据与**偏好满足度指标**。实验结论（作者自报）：当前 **VLA 策略零样本个性化表现弱**；**SFT 能让偏好变得可学**；**混合训练**在保留「无偏好」能力上优于顺序适配，并在上下文提示下优于「只训偏好」，但可能削弱动作偏好的学习；**偏好泛化、分解与冲突处理仍然困难**。代码/数据见项目主页（原文自述）。⚠️ 本线未复现。",
}

AREAS = {
    "2610.22371": ["多模态", "4D 感知", "视频生成", "3D 点跟踪", "相机位姿"],
    "2610.22372": ["机器人", "VLA", "个性化偏好", "评测基准"],
}

# 本轮 fetch 新发现（10-12 批补漏，非推荐）→ 以「候选」入 SEEN，防重复评估
NEW_CANDIDATES = [
    ("2610.16621", "AgentCue: Statistical Summaries for Guiding Decentralized Multi-Agent Self-Organization", "cs.MA"),
    ("2610.16537", "Learning Graded Sparse Mechanisms: A Representation Theorem and Certified Generalization", "cs.LG"),
    ("2610.16518", "Asymptotic Risk of Learning-Rate Schedules for Least-Squares Regression with Discretely Distributed Features", "cs.LG"),
]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by = {}
    for e in data["items"]:
        by[re.sub(r"v\d+$", "", e["arxiv_id"])] = e
    # 推荐的两篇不在本轮 kept（来自候选池）⇒ 用 id_list 证据补元数据
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-17-idlist-shortlist-r96.xml").getroot()
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        by[aid] = {
            "arxiv_id": aid,
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": e.find("a:category", ns).get("term"),
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

    # 2) SEEN: 新发现 3 条以「候选」追加到表格末尾（最后一行表格行之后）
    last = max(i for i, ln in enumerate(lines) if ln.startswith("| 2026-"))
    add = ["| %s | %s | %s | %s | 候选 |" % (FIRST_SEEN, a, t, c) for a, t, c in NEW_CANDIDATES]
    lines[last + 1:last + 1] = add
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 3) papers.jsonl 追加
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

    # 4) 统计
    st = {"收录": 0, "候选": 0, "候选（RSS补充）": 0}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

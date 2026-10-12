#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第八十九轮（本地 2026-10-12 18:00 P0「晚 2」轮）结果落盘。

- raw/2026-10-12-fetch-r89-seen.json 的 items（169 条 kept，窗口 <=120h）
  -> SEEN.md（收录 2 / 候选 167）
- 2 篇收录（科普）-> papers.jsonl
"""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-12-fetch-r89-seen.json"

RECOMMENDED = ["2610.13948", "2610.13860"]

SUMMARY_ZH = {
    "2610.13948": "把「维基百科游戏」（只能用条目内链接，从起点页走到目标页）当作一个可比的信息检索任务，用来检验语言模型在「太大、无法建索引」的文档集合里做导航的能力。作者用 OpenAlex + 本地抓取，构建了覆盖 5 种维基百科语言与 5 个学术文献数据集的超大地图（页面/引文图），并提供建图与导航代码，从而不依赖第三方 API。在人类与 TF-IDF 基准下对比句向量模型与 LLM：没有任何模型显著超过人类，但最好的几个（GPT-o3 mini、GPT-4o、QwQ:32B、DeepSeek-R1:70B）成功率与人类相当；性能与排名随语言与主题而变，对使用这些技术的实践者有启示。⚠️ 数字为作者自报、未复现。",
    "2610.13860": "3D Gaussian Splatting（3DGS）能实时生成高质量新视角画面，但默认场景是静止的，而现实环境里流动的水等高频动态很难在「随手拍摄」条件下（无密集多视角、无高速采集）重建。提出一种给静态 3DGS 场景「让水动起来」的方法：从参考图或模型渲染估计 2D 光流，并把它提升为一致的 3D 欧拉运动场；再用受 cinemagraph（局部动图）启发的算法，用该运动场变形高斯图元，产出时间上无缝循环的动画。结果保持实时渲染性能、显著提升感知真实感、并保留场景内自由视角漫游。在一个新采集的「野外瀑布」数据集上，相对既有动态高斯泼溅与 3D cinemagraph 方法在视觉质量与计算效率上均有清晰改进。⚠️ 数字为客观效果描述、未由本线复现。",
}

AREAS = {
    "2610.13948": ["LLM", "信息检索", "导航/评测"],
    "2610.13860": ["多模态", "3D 重建", "4D 动态"],
}


def clean_title(t):
    return t.replace("|", "/").strip()


def base(aid):
    return re.sub(r"v\d+$", "", aid)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["items"]
    by_base = {}
    for e in items:
        b = base(e["arxiv_id"])
        if b not in by_base:
            by_base[b] = e
    print("fetch kept items:", len(items), "dedup base:", len(by_base))
    for k in RECOMMENDED:
        assert k in by_base, "missing %s" % k

    rec_rows, cand_rows = [], []
    for k in RECOMMENDED:
        e = by_base[k]
        rec_rows.append("| 2026-10-12 | %s | %s | %s | 收录 |" % (k, clean_title(e["title"]), e["category"]))
    for k, e in sorted(by_base.items(), reverse=True):
        if k in RECOMMENDED:
            continue
        cand_rows.append("| 2026-10-12 | %s | %s | %s | 候选 |" % (k, clean_title(e["title"]), e["category"]))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last_idx = None
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("| 2026-"):
            last_idx = idx
            break
    assert last_idx is not None, "未找到最后数据行"
    new_lines = lines[:last_idx + 1] + rec_rows + cand_rows + lines[last_idx + 1:]
    SEEN.write_text("\n".join(new_lines), encoding="utf-8")

    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by_base[k]
            authors = e["authors"] if isinstance(e["authors"], list) else [e["authors"]]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": authors,
                "submitted": e["published"][:10],
                "updated": e["updated"][:10],
                "category": e["category"],
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-12",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows added:", len(rec_rows) + len(cand_rows), "(rec %d / cand %d)" % (len(rec_rows), len(cand_rows)))
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

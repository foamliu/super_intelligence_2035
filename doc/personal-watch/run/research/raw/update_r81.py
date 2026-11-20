#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第八十一轮（本地 2026-10-08 18:00 P0「晚 2」轮）结果落盘。
- fetch-r81.json 的 180 条新条目 -> SEEN.md（收录 2 / 候选 178）
- 2 篇收录 -> papers.jsonl
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-08-fetch-r81.json"

RECOMMENDED = ["2610.09769", "2610.10462"]

SUMMARY_ZH = {
    "2610.09769": "介绍 Bolzano —— 一个开源多智能体数学系统：多个「证明者」智能体并行做证明搜索，配一个「验证者」智能体，并维护一份人类可读的研究状态。先在专家挑选的问题上人工使用，得 8 个经领域专家核验的结果；随后不做问题级人工引导，对从四组论文中抽取的约 3800 个未解问题运行，解出约 200 个；其中一个实验使用 STOC 2026 录用论文，回答了论文提出的 4 个问题（经作者确认）。",
    "2610.10462": "面向长程「衣物折叠」的自我纠错掩码生成策略 FoldBack：现有长程策略在抓取错失/滑脱后往往继续执行，即使衣物未到目标构型。FoldBack 把恢复机制组织为三个推理期决策（何时细化与验证、如何回滚、在哪里与如何重试），把细化与抓取验证对齐到拾放事件，将机器人带回可重试的预抓取构型同时保留成功抓取，并有选择地重生成失败片段与部分未来动作、避开此前失败的抓取位置。原文称其为首个统一这些决策的可编辑全轨迹策略；在 6 类 33 件真实衣物上达 75.2% 最终折叠成功率与 0.837 最终掩码 IoU（最强先前基线 45.7% / 0.689）。",
}

def clean_title(t):
    return t.replace("|", "/").strip()

def main():
    data = json.loads(FETCH.read_text(encoding="utf-8"))
    items = data["items"]
    by_id = {i["arxiv_id"]: i for i in items}
    assert len(items) == 180, len(items)
    for k in RECOMMENDED:
        assert k in by_id, k

    # 1) SEEN.md 行
    rec_rows, cand_rows = [], []
    for k in RECOMMENDED:
        i = by_id[k]
        rec_rows.append("| 2026-10-08 | %s | %s | %s | 收录 |" % (k, clean_title(i["title"]), i["category"]))
    for i in items:
        k = i["arxiv_id"]
        if k in RECOMMENDED:
            continue
        cand_rows.append("| 2026-10-08 | %s | %s | %s | 候选 |" % (k, clean_title(i["title"]), i["category"]))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    # 找最后一行数据行（含 2610.05569 或最后一行以 '| 2026-10-08 |' 开头）
    last_idx = None
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("| 2026-10-08 |") or lines[idx].startswith("| 2026-10-07 |"):
            last_idx = idx
            break
    assert last_idx is not None, "未找到最后数据行"
    new_lines = lines[:last_idx + 1] + rec_rows + cand_rows + lines[last_idx + 1:]
    SEEN.write_text("\n".join(new_lines), encoding="utf-8")

    # 2) papers.jsonl
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            i = by_id[k]
            rec = {
                "arxiv_id": k,
                "title": i["title"],
                "authors": i["authors"],
                "submitted": i["published"][:10],
                "updated": i["updated"][:10],
                "category": i["category"],
                "areas": i.get("areas", []),
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": i["abs_url"],
                "pdf_url": i["pdf_url"],
                "first_seen": "2026-10-08",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows added:", len(rec_rows) + len(cand_rows), "(rec %d / cand %d)" % (len(rec_rows), len(cand_rows)))
    print("papers.jsonl +", len(RECOMMENDED))

if __name__ == "__main__":
    main()

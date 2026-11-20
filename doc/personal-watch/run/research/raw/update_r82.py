#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第八十二轮（本地 2026-10-09 06:00 P0「早 3」轮）结果落盘。
- raw/2026-10-09-rss-r82.json 的 in_window（<=72h）条目 -> SEEN.md（收录 3 / 候选 N）
- 3 篇收录 -> papers.jsonl
"""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-09-rss-r82.json"

RECOMMENDED = ["2610.10426", "2610.10118", "2610.10129"]

SUMMARY_ZH = {
    "2610.10426": "针对「终端智能体」的能力同时取决于模型权重与运行时 harness（负责格式化提示、绑定工具、处理错误恢复）这一事实，指出既有 harness-模型协同演化工作把 harness 搜索中产生的轨迹当成不加区分的回放缓冲、忽略「轨迹价值取决于其生成时的 harness」。提出交替式协同演化框架，把 harness 搜索与策略训练解耦为逐组件晋级决策，并给出 harness-aware 数据配方 CoTrace：显式管理轨迹路由、来源匹配与课程刷新——执行失败驱动 harness 合成，策略训练则严格条件于「与所采纳运行时匹配、经核验的 rollout」（SFT）或新鲜在线交互（RL）。原文在 Tmax 晋级划分上报告把 Qwen3.5-9B 从 78 提升到 88（SFT），在线 RL 变体达 90，并称紧凑的 harness-匹配语料比跨同类 harness 汇聚的大语料更省算力；Terminal-Bench 2.1 / SWE-bench Lite 上所述 OOD 迁移取决于 harness 兼容性。",
    "2610.10118": "面向长程推理「既要访问早期信息、又要把生成成本控制住」的矛盾（全历史注意力存储/算力随长度增长，循环压缩又会丢失精确细节），提出通用循环模型 YANchor-4B：把关键记忆保留为「锚点（anchors）」供后续推理检索，具备 O(N) 生成时间与 O(1) 记忆，并配多维记忆机制。原文报告在 AIME 2024–2026 上平均 pass@1 82.93%、HMMT 63.64%，称优于包括更大模型在内的线性时间 / 常数状态同类；在 H100 上称批量长生成吞吐较 Transformer 与混合基线有数倍提升。",
    "2610.10129": "来自 EDA 研究者的「agentic 算法探索」自述案例：八次刻意试验（1 位教师 + 7 名学生，含无发表经验学生），在有限算法干预下让智能体做数学构造、分析既有工具并实现改进（部分未达实用目标）；另用 AI 收集/分类/分析 2022–2026 年四大 EDA 会议与两刊共 8,420 篇论文，对其中 2,380 篇主核论文中 97.7% 按题摘归类为「计算封闭」（含新表述工作）。结论指向：EDA 大量环节对算法研究而言是「可执行环境」，工具开发者可借此探究此前没时间做的想法，并提出「当结果比审阅更容易产出时，EDA 该如何验证与激励研究」之问。",
}

AUTHORS = {
    "2610.10426": ["Jixuan Chen", "Jiaxin Zhang", "Qinyuan Ye", "Yada Pruksachatkun"],
    "2610.10118": ["Huishan Ji", "Hua Xu", "Weiming Zhang", "Qirui Ye"],
    "2610.10129": ["Keren Zhu", "Yu Deng", "Xiaoyu Hao", "Liwen Jiang"],
}
AREAS = {
    "2610.10426": ["agent harness"],
    "2610.10118": ["LLM"],
    "2610.10129": ["agent harness"],
}
UPDATED = {
    "2610.10426": "2026-10-07",
    "2610.10118": "2026-10-07",
    "2610.10129": "2026-10-07",
}

def clean_title(t):
    return t.replace("|", "/").strip()

def base(aid):
    return re.sub(r"v\d+$", "", aid)

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    inw = data["in_window"]
    # 去重（按 base id）
    by_base = {}
    for e in inw:
        b = base(e["id"])
        if b not in by_base:
            by_base[b] = e
    print("in_window raw:", len(inw), "dedup base:", len(by_base))

    rec_rows, cand_rows = [], []
    for k in RECOMMENDED:
        assert k in by_base, k
    for k in RECOMMENDED:
        e = by_base[k]
        rec_rows.append("| 2026-10-09 | %s | %s | %s | 收录 |" % (k, clean_title(e["title"]), e["primary"]))
    for k, e in sorted(by_base.items(), reverse=True):
        if k in RECOMMENDED:
            continue
        cand_rows.append("| 2026-10-09 | %s | %s | %s | 候选 |" % (k, clean_title(e["title"]), e["primary"]))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last_idx = None
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("| 2026-10-0"):
            last_idx = idx
            break
    assert last_idx is not None, "未找到最后数据行"
    new_lines = lines[:last_idx + 1] + rec_rows + cand_rows + lines[last_idx + 1:]
    SEEN.write_text("\n".join(new_lines), encoding="utf-8")

    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by_base[k]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": AUTHORS[k],
                "submitted": e["published"][:10],
                "updated": UPDATED[k],
                "category": e["primary"],
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-09",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows added:", len(rec_rows) + len(cand_rows), "(rec %d / cand %d)" % (len(rec_rows), len(cand_rows)))
    print("papers.jsonl +", len(RECOMMENDED))

if __name__ == "__main__":
    main()

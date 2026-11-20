#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十九轮（本地 2026-10-19 06:00 P0「早 3」轮 · AM）结果落盘。

- 本轮 AM：**无新公告批次**（周日 20:00 ET 的公告在本轮唤醒后 2 小时才到；
  批次仍 2026-10-15；`--fetch` window_mode=weekend_batch 120h → kept 0 / dropped 600）
  -> 早报 3 篇「借鉴」取自**前轮已入账的窗口内候选池**
  -> SEEN.md 对应「候选」行改为「收录」
- 3 篇推荐（均「借鉴」）：2610.17901 FlashMask-3 / 2610.22350 FDE-Gym / 2610.19928 MemDuet
  -> papers.jsonl 追加 3 行（216 -> 219）
- 元数据取自 id_list 权威复核 raw/2026-10-19-idlist-final-r99.xml（含官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

FIRST_SEEN = "2026-10-19"
RECOMMENDED = ["2610.17901", "2610.22350", "2610.19928"]

SUMMARY_ZH = {
    "2610.17901": "指出长上下文训练把**结构化注意力掩码**（document / prefix-LM / share-question / sliding-window / block-sparse）与**多机 context parallelism（CP）**耦合后，掩码成为主要瓶颈。**FlashMask-3** 在 FlashAttention-3 的 TMA/WGMMA 流水线上实现**掩码感知的 Hopper kernel**（三角色 warp specialization），并把任意多 chunk CP 分配下的每 rank 掩码定位化为**边界向量上的零通信 clip–shift–max**；另加**稀疏感知负载均衡（HCC-IPO）**与**掩码驱动的计算-通信重叠 / 通信剪枝**（前向 all-gather 用拓扑感知分层路由）。作者实测：单 H100、12 种掩码、4K–128K 上下文，TFLOPs 较 FlashMask / FlexAttention / MagiAttention 提升 45–141% / 34–71% / 2–44%；CP 度 4–32（每卡 8K 序列）达 31–75% 计算-通信重叠效率，吞吐较 Megatron-Core CP ring / all-gather / MagiAttention 提升 1.80–3.71× / 1.71–2.92× / 1.09–1.46×；128 卡 H100 上训练 118B-A14B MoE @128K，较 Dual Chunk all-gather 吞吐 +7.3–11.0%，attention 前反向快 24.5–44.9%。⚠️ 数字为作者自报、本线未复现；comment 自述发表于 NeurIPS 2026 主会（本线未核会务）。",
    "2610.22350": "指出现有 agent 基准多在**需求已写清**的任务（issue / spec / ticket）上评测，而真实客户交付要求**前向部署工程师**澄清模糊需求、在运行系统中工作、发现未明说约束。作者提出 **FDE-Gym**：**95 个端到端交付任务 / 20 个客户场景 / 18 个行业**，由行业专家从真实交付项目改编；在**带脚本化 stakeholder 与可修改客户系统**的模拟环境中，agent 与 stakeholder 交互并操作类生产系统交付可用方案。评分按**客户自身业务指标的提升**归一化（0 = 系统未变，1 = 参考解），并对消息、试跑与等待时间**罚分**。评测 7 家厂商 13 个模型配置：真实设置下最佳配置平均分 **0.56**，95 题中仅 **14 题**达到「≥0.8 且无事故」；**发现未明说约束**是主要瓶颈；即便在最佳配置已拿到全部关键事实的 23 题中，也只有 **10 题**业务提升 ≥0.8。⚠️ 数字为作者自报、本线未复现；comment 给出网站 / 代码 / 数据地址（本线未核）。",
    "2610.19928": "面向超长文档推理中「上下文越长、推理效果与效率越难兼顾」的问题，提出**双过程记忆 MemDuet**：**小模型（System 1）**从原始 context chunk 中**并行快速选证据**，**大模型（System 2）**按文档顺序**验证记忆更新并写入记忆**，借鉴 Kahneman 的快/慢思考分工。训练分三阶段：先 **SFT** 训练 System 1 的证据选择，再用 **GRPO** 训练 System 2 的验证与记忆重写，最后**联合优化**两者以协调选择与更新。在 RULER-HQA / LongBench v2 / 2WikiMultiHopQA 上，作者称随上下文增长取得更好的 accuracy–efficiency 权衡；三项评测平均相对 RL-MemAgent **端到端推理加速 9.74×、输出 token 减少 73.91%**。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.17901": ["长上下文", "attention mask", "context parallelism", "分布式训练", "Hopper"],
    "2610.22350": ["agent 评测", "交付", "stakeholder 交互", "约束发现", "基准"],
    "2610.19928": ["长上下文", "记忆", "SLM-LLM 协同", "GRPO", "推理效率"],
}


def main():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-19-idlist-final-r99.xml").getroot()
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
            if ("| %s |" % k) in ln and ln.startswith("| 2026-") and ln.rstrip().endswith("| 候选 |"):
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

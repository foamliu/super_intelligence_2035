#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十轮（本地 2026-10-13 06:00 P0「早 3」轮）结果落盘。

本轮 API 增量 kept=0（无新公告批次，批次仍 2026-10-09，已被 PM 第八十九轮消费）；
早报 3 篇「借鉴」取自第八十九轮（PM）已入账窗口内候选池 → SEEN 状态 候选 -> 收录
（行数不变），并追加 papers.jsonl（+3）。
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

RECOMMENDED = ["2610.12995", "2610.13835", "2610.13889"]

SUMMARY_ZH = {
    "2610.12995": "SFT 用固定示范把期望的推理策略与行为模式直接教给模型，但「强迫模型模仿外部给定轨迹」可能与预训练已支持的行为冲突，限制训练分布之外的泛化。近期动态 SFT 按预测概率 / 先验支持 / 分布兼容性等「模型侧信号」对 token 级监督重加权，但「模型兼容 ≠ 学习价值」：一个当前模型弱支持的 token，既可能是坏的不匹配，也可能恰是示范要教的任务特定决策。作者提出 CIG-SFT（信息论框架）：在 teacher forcing 下，用冻结参考模型比较「给定 / 不给任务输入」时示范 token 的似然（gold 前缀固定），得到「条件信息增益」——量化任务本身把示范决策的不确定性降低了多少；再把它转成对当前策略的 KL 正则投影，并推导出一个等价的标量加权 SFT 目标（其 logit 梯度与投影目标完全一致）。在数学推理与代码生成基准上，CIG-SFT 稳定优于标准 SFT 与近期自适应微调基线，尤其在难评测分布上的泛化提升明显，且不需要额外训练数据或在线 rollout。⚠️ 数字为作者自报、本线未复现。",
    "2610.13835": "理想的（语言）模型要能持续更新知识；既有工作多关注「训练之后如何让更新更高效」。本文反过来研究「预训练阶段对时变知识的组织方式」如何影响后续更新的效率。按时间顺序训练知识的模型专精于最近遇到的知识（称 specialists）；把同样知识随机打乱顺序训练的模型在所有时间段都表现好（称 generalists）。意外发现：specialists 获得新知识所需更新步数远少于 generalists。为解释，作者从第一性原理推导出一条把「更新成本」与「模型优化动力学」联系起来的规律，且与实测吻合。据此设计一种组织预训练数据的策略：既保留稳定的历史知识、又能高效更新当前知识；并证明该时间化知识组织的收益可迁移到真实预训练模型与既有知识更新工具，且推广到其他知识排序。⚠️ 数字为作者自报、本线未复现。",
    "2610.13889": "随着 AI agent 越来越依赖外部工具，准确的「工具检索」对可靠行为至关重要。既有方法优化语义相关性，却基本忽略执行期间的工具可用性。为此提出 RATED：把鲁棒语义匹配与动态可靠性自适应结合——用冻结双编码器 + 对比微调做语义匹配，再用一个轻量上下文 bandit 模块依据实时执行反馈对候选重排序，从而快速适应运行时工具故障、无需昂贵重训。作者同时提出 EcoAgent 基准（5,172 个真实工具、>21 万条 query-tool 对，用于离线检索与动态可靠性评测）。实验显示：相对 ToolLLM API retriever，真实查询下 MRR 相对提升 52.2%；在 30% 故障率的严重 API 中断场景，把「错误选择率」从 86.2% 降到 2.9%，而延迟开销相比「仅编码」推理增加不到 1 ms。代码与数据集已公开（github.com/Elliotes/EcoAgent）。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.12995": ["LLM", "后训练/SFT", "泛化"],
    "2610.13835": ["LLM", "预训练数据组织", "持续学习/知识更新"],
    "2610.13889": ["agent harness", "工具检索", "可靠性"],
}

META = {
    # arxiv_id: (title, authors, submitted, updated, category)
    "2610.12995": (
        "What Should SFT Learn? Conditional Information Gain for Generalizable Post-Training",
        ["Yuxuan Gu", "Kequan Niu", "Xiaocheng Feng", "Yun Li", "Yiqiao Yang", "Bing Qin"],
        "2026-10-09", "2026-10-09", "cs.CL"),
    "2610.13835": (
        "Specialists Learn Faster: Knowledge Organization in Pre-training Shapes Knowledge Update Efficiency",
        ["Sheng Zhao", "Yuhao Zhu"], "2026-10-09", "2026-10-09", "cs.LG"),
    "2610.13889": (
        "RATED: Reliability-Aware AI Agent Tool Retrieval via Execution Dynamics",
        ["Weiliang Chen", "Song Liao"], "2026-10-09", "2026-10-09", "cs.AI"),
}


def main():
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for k in RECOMMENDED:
            if ln.startswith("| 2026-") and ("| %s |" % k) in ln and ln.rstrip().endswith("| 候选 |"):
                lines[i] = ln[: ln.rfind("候选")] + "收录 |"
                flipped += 1
    assert flipped == len(RECOMMENDED), "flipped=%d" % flipped
    SEEN.write_text("\n".join(lines), encoding="utf-8")
    print("SEEN flipped 候选->收录:", flipped, "(行数不变:", len(lines), ")")

    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            title, authors, sub, upd, cat = META[k]
            rec = {
                "arxiv_id": k,
                "title": title,
                "authors": authors,
                "submitted": sub,
                "updated": upd,
                "category": cat,
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-13",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

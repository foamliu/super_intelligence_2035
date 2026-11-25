#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十五轮（本地 2026-10-17 06:00 P0「早 3」轮 · AM）结果落盘。

- 本轮 AM 轮 **无新公告批次**（批次仍 2026-10-15，`--fetch` kept 0 / dropped 600）
  -> 早报 3 篇「借鉴」取自**前轮（第九十四轮 PM）已入账的窗口内候选池**（raw/2026-10-16-fetch-r94-seen.json）
  -> SEEN.md 对应 2026-10-16「候选」行改为「收录」（行数不变 3688）
  -> 台账 收录 206 -> 209 / 候选 2975 -> 2972 / 候选（RSS补充）507
- 3 篇推荐（均「借鉴」）：2610.21126 / 2610.20673 / 2610.22344
  -> papers.jsonl 追加 3 行（206 -> 209）
- 元数据取自 id_list 权威复核 raw/2026-10-17-idlist-shortlist-r95.xml（含官方 published/作者/comment）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-16-fetch-r94-seen.json"

FIRST_SEEN = "2026-10-17"
RECOMMENDED = ["2610.21126", "2610.20673", "2610.22344"]

SUMMARY_ZH = {
    "2610.21126": "稀疏 KV 压缩通过保留部分历史状态降低长上下文推理成本，但这些状态仍沿用原始（全长历史）位置坐标；在 RoPE 下，被逐出 token 留下的位置空隙会继续影响 query–key 匹配，可能削弱对所保留证据的利用。作者在「固定选择器产出的缓存」上研究**选择之后的位置几何（post-selection positional geometry）**，提出 **RoPERelay**：为缓存键赋予**紧凑且保序的 RoPE 坐标**，通过**逆旋转 + 再旋转**迁移已缓存 key 的相位，并同步当前 query 与后续生成；它**复用既有 K/V**，无需重新选择、历史重预填或额外缓存预算。在跨 2 个模型、6 个稀疏选择器、3 类长期记忆任务的 **36 组对比**中，RoPERelay 在 **32 组**提升答案质量；Llama-3.1-8B-Instruct + BM25 在 LongMemEval-S 上准确率 **23.6% → 35.4%**，实测整请求时间开销约 **1%–3%**。⚠️ 数字为作者自报、本线未复现。",
    "2610.20673": "编程 agent 越来越多用于优化代码，但现有基准**固定单一加速器 / 编程模型 / harness**，无法**分离各组件贡献**，也说不清新增的 skill / tool 是否值回成本。作者提出 **HPCAgent-Bench**：**689 个 kernel** 分三条赛道（循环级优化题 / 从 HPC 代码抽取的 kernel / 机器学习模型）；每个 kernel 用 **NumPy 规约一次**、自动派生 **C 与 Fortran 参考实现**，通过**统一 C ABI 或 Python 接口**提交，可在 **CPU / GPU、单机或多机**上运行；**外部裁判在隐藏 fuzz 输入上校验正确性**并计时，堵住 agent 钻测试系统的路径。作者另给出两个报告指标：**intervention efficacy（干预效力）**——用配对运行在加速比 / 成功率 / 成本上衡量「加一个工具」这类干预；**weighted token cost（加权 token 成本）**——按显式权重报告输入 / 缓存输入 / 输出 token。实验中 agent 相对自动并行器最高达 **4.2× 加速**，且优化可迁移到另一台机器（**93%–99%** 不含设备相关代码的答案仍正确，per-kernel 加速比秩相关 **r_s ≥ 0.84**）；在 40 组配对设置中，干预**只有 2 次显著改变加速比**，但 token 成本可差达 **3.0×**。⚠️ 数字为作者自报、本线未复现。",
    "2610.22344": "LLM 正从辅助科研 / 工程走向**自主开发并改进 AI 系统**（AI4AI，作者列为通向递归自我改进 RSI 的路径之一）。工作流驱动的**机器学习工程（MLE）**系统通过复杂编排管理**长时程实验**；近期 MLE 系统采用模型主导交互，让模型自主组织实验、按执行反馈调整优化策略。但每次实验的反馈都反映此前若干决策，一次长程 MLE 运行包含许多昂贵实验，训练必须从**长交互轨迹**中选出有用监督、并**从中间结果学习**。作者提出一种面向**自主长时程 MLE 优化**的后训练方法，并据此训练 **MLExpert**——一个 **35B MoE 智能体模型**；他们设计了 **Kaggle-MLE Factory** 构造可执行任务与**模型主导实验的交互 harness**。**分层 agentic SFT** 把通用工具使用与编程能力经结果引导监督迁移到 MLE；**Windowed Interaction RL（WIRL）**把相邻实验结果之间的多轮决策视为一个「执行窗口」、赋以共享的结果奖励，并用**异步采集与策略校正**支持在轨迹结束前更新策略。在 **MLE-Bench Lite** 上，MLExpert 把基座模型的平均奖牌率 **37.9% → 72.7%**，作者称与 **Kimi-K3、GLM-5.3** 等更大前沿模型相当；在 NatureBench Lite、agent scaffold 优化、算法优化上亦有提升。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.21126": ["LLM", "长上下文", "KV cache", "稀疏注意力", "RoPE", "高效推理"],
    "2610.20673": ["agent harness", "code agent", "评测基准", "HPC/性能优化", "成本度量"],
    "2610.22344": ["agent harness", "MLE agent", "MoE", "长时程", "后训练/RL"],
}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by = {}
    for e in data["items"]:
        by[re.sub(r"v\d+$", "", e["arxiv_id"])] = e
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
                "first_seen": FIRST_SEEN,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows changed 候选->收录:", changed, "(rows unchanged)")
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

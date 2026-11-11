#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十七轮（本地 2026-11-11 12:00 午间轮）：把 2 篇（1 借鉴 + 1 科普）写入台账。

幂等：每个 arXiv ID 在 SEEN.md / papers.jsonl 中恰好 1 行；published 前缀均为 2026-11-10。
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/

PAPERS = [
    {
        "arxiv_id": "2611.14009",
        "title": "Coding Agent Memory Post-Training II: Unlocking the Memory Potential of Pre-trained File Operations for Long-Horizon Tasks via On-Policy Distillation",
        "authors": ["Lirui Luo", "Kelong Mao", "Xinwei Yang", "Rongqing Li", "Luyu Chen",
                    "Kieran Wong", "Yudong Guo", "Xinrui Wang", "Jiayin Zhu",
                    "Gu Simiu", "Sulong Xu", "Cong Fang"],
        "submitted": "2026-11-10",
        "updated": "2026-11-10",
        "category": "cs.LG",
        "areas": ["agent harness", "长程记忆", "文件式记忆", "on-policy 蒸馏", "上下文替换", "Terminal-Bench", "SWE-Bench Pro"],
        "summary_zh": (
            "长程 agent 的交互历史会超出活跃上下文，因此必须决定「写什么、何时读回」。"
            "作者先造 CAMG-II：Shop / Coding / AutoResearch / General / Visual 五个长程环境，"
            "每个环境除原生任务接口外都给普通 Bash 与「跨上下文替换仍存在」的工作区，"
            "让策略用文件（笔记 + 有界续接文件）做记忆；再提出 CAMP-II，"
            "用完全异步的 on-policy 蒸馏把「文件式记忆」直接训进单个策略（教师冻结）。"
            "关键观察：教师/学生对 Bash 文件接口的先验最强（每 token NLL：文件 0.19/0.42、专用记忆工具 0.70/0.91、压缩协议 0.98/1.40），"
            "文件接口承载的记忆动作占比 21.6%，约为专用工具（7.8%）的 3 倍。"
            "结果：CAMG-II 测试集平均成功率 CAMP-II-4B 64.6 / CAMP-II-9B 66.5，高于 CAMP-I 54.2、Hy-Memory 48.9、"
            "单模型 HELM 49.8；相对最强 OPD 基线增益 2.97 倍。外部迁移：Terminal-Bench 2.1 / SWE-Bench Pro V2 上，"
            "CAMP-II-4B 从 23.1/11.2 升到 30.0/18.1（各 +6.9 点），CAMP-II-9B 38.0/30.1（均值 34.1）"
            "超过更大的 Qwen3.5-35B-A3B（33.8/27.4，均值 30.6）。"
            "⚠️ 上限只到 9B、单一冻结教师；作者自报、本线未复现。"
        ),
        "abs_url": "https://arxiv.org/abs/2611.14009",
        "pdf_url": "https://arxiv.org/pdf/2611.14009",
        "first_seen": "2026-11-11",
    },
    {
        "arxiv_id": "2611.13541",
        "title": "Agent Benchmarks Stop Ranking Before They Run Out of Tasks",
        "authors": ["Zihan Dong", "Qishi Zhan", "Minxuan Hu"],
        "submitted": "2026-11-10",
        "updated": "2026-11-10",
        "category": "cs.AI",
        "areas": ["评测协议", "agent benchmark", "榜单饱和", "分级信用", "verifier 误差", "成本轴", "可复现锚点"],
        "summary_zh": (
            "重打分 8 个基准的已发布运行（含 SWE-bench Verified、Terminal-Bench 2.0、OSWorld-Verified、ALE-Bench、"
            "MLE-bench、METR、SWE-fficiency、AlgoTune），结论是「榜单饱和」很大一部分来自测量方式而非任务耗尽。"
            "失效 A（太粗）：SWE-bench Verified 前十名今日只差 3.6 分、统计上同属一档（2024-09 还是 19.2 分三档）；"
            "Terminal-Bench 2.0 前十差 8.5 分、一档；OSWorld-Verified 差 12.0 分、两档；"
            "三榜单前十里没有任何相邻对显著可分，且校正 verifier 误差带来的重排不比「随机删掉每个 agent 六分之一的通过」更多。"
            "失效 B（封顶在参考解）：ALE-Bench 官方分把前十分成三档（S=0.07），二值化为「是否超过人类中位数」后变一档（S=1.00），"
            "而按「目标函数」打分（参考处=1、超过按对数比、封顶 3）恢复三档（S=0.03）；ALE-Bench 47.8% 的运行其实超过参考。"
            "同分模型在 Terminal-Bench 复跑里，在被丢弃的「量」上可差 10 倍以上。"
            "57 份旗舰模型卡（7 家实验室）里只有约三分之一的结果与上一代旗舰可比。"
            "方案：带日期锚点的截断对数比分数 + 成本单列 + 冻结锚点保证版本可比。"
            "⚠️ 预印本、榜单数据截至 2026-09-01；作者自报、本线未复现。"
        ),
        "abs_url": "https://arxiv.org/abs/2611.13541",
        "pdf_url": "https://arxiv.org/pdf/2611.13541",
        "first_seen": "2026-11-11",
    },
]


def main():
    seen_path = BASE / "SEEN.md"
    seen_lines = seen_path.read_text(encoding="utf-8").splitlines()
    existing = set()
    for ln in seen_lines:
        if ln.startswith("|"):
            parts = [p.strip() for p in ln.strip("|").split("|")]
            if len(parts) >= 2:
                existing.add(parts[1])

    new_rows = []
    for p in PAPERS:
        assert p["submitted"] == "2026-11-10", p["arxiv_id"]
        if p["arxiv_id"] in existing:
            print("SKIP seen:", p["arxiv_id"])
            continue
        new_rows.append("| 2026-11-11 | %s | %s | %s | 收录 |" % (
            p["arxiv_id"], p["title"], p["category"]))

    if new_rows:
        seen_path.write_text("\n".join(seen_lines + new_rows) + "\n", encoding="utf-8")

    jl_path = BASE / "papers.jsonl"
    jl_lines = [ln for ln in jl_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    have = set()
    for ln in jl_lines:
        have.add(json.loads(ln)["arxiv_id"])
    added = 0
    for p in PAPERS:
        if p["arxiv_id"] in have:
            continue
        jl_lines.append(json.dumps(p, ensure_ascii=False))
        added += 1
    jl_path.write_text("\n".join(jl_lines) + "\n", encoding="utf-8")

    ids = [json.loads(ln)["arxiv_id"] for ln in jl_lines]
    for p in PAPERS:
        assert ids.count(p["arxiv_id"]) == 1, p["arxiv_id"]

    print("SEEN rows +%d -> %d lines" % (len(new_rows), len(seen_path.read_text(encoding="utf-8").splitlines())))
    print("papers.jsonl +%d -> %d lines" % (added, len(jl_lines)))


if __name__ == "__main__":
    main()

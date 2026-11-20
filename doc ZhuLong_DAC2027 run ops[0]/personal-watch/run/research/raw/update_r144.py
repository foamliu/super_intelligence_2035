#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百四十四轮（本地 2026-11-11 06:00 AM）：把 3 篇「借鉴」写入台账。

幂等：每个 arXiv ID 在 SEEN.md / papers.jsonl 中恰好 1 行；published 前缀均为 2026-11-09。
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/

PAPERS = [
    {
        "arxiv_id": "2611.12728",
        "title": "Safe Reinforcement Learning for Multi-Turn Clinical Agents: When Dense Rewards Beat Outcome Rewards",
        "authors": ["Brendan P. Murphy", "Agustina Saenz"],
        "submitted": "2026-11-09",
        "updated": "2026-11-09",
        "category": "cs.LG",
        "areas": ["GRPO", "过程奖励", "稠密信用分配", "多轮 agent", "高危子群", "奖励几何", "评测协议"],
        "summary_zh": (
            "在三个受控临床多轮环境（药物续方分诊、急性诊断检查、剂量滴定）里研究 RLVR 对「决策过程」的影响。"
            "只用最终结果奖励的 GRPO 常把聚合分刷高，却同时出现过早承诺、只问一个问题就收手、以及在罕见高危病例上崩坏；"
            "在诊断任务里给「能降低不确定性的提问」加稠密过程信用（λ=0.2），3 个训练种子上留出集价值 +0.285±0.027→+0.313±0.024、"
            "高危价值 +0.098±0.037→+0.157±0.057、高危支持率 0.33±0.29→0.50±0.00、中等病例支持率 0.38±0.18→0.67±0.10，"
            "提问数只从 1.82 增到 2.08。过程信用强度是任务相关的：滴定里 λ=0.03 仍欠收集（1.24 问、one-question 率 0.93），"
            "λ=0.2 过度收集（4.10 问、价值 −0.091），λ=0.1 最校准（2.67 问、one-question 0.62）。"
            "分离探索/利用可在最优 ckpt 把高危支持推到 1.00，但提问升到 4.4、良性支持 0.48→0.04，末次 ckpt 又回落 0.50。"
            "RL 也修不好有偏 SFT 留下的稀有行为缺口。⚠️ 临床域、高危子群仅 2 例（support 只能取 0/0.5/1）、"
            "主实验 3 seeds 其余单种子；作者自报、本线未复现。"
        ),
        "abs_url": "https://arxiv.org/abs/2611.12728",
        "pdf_url": "https://arxiv.org/pdf/2611.12728",
        "first_seen": "2026-11-11",
    },
    {
        "arxiv_id": "2611.12856",
        "title": "WorkflowArena: Benchmarking Executable Workflow Orchestration in LLM-Based Multi-Agent Systems",
        "authors": ["Zheng Jiang", "Fang Niu", "Bo Peng", "Houde Qian", "Wenyi Li", "Deyao Hong",
                    "Mingju Gao", "Yizhe Chi", "Youjie Zheng", "Kaisen Yang", "Calvin Xiao",
                    "Lifeng Sun", "Huan-ang Gao"],
        "submitted": "2026-11-09",
        "updated": "2026-11-09",
        "category": "cs.CL",
        "areas": ["agent harness", "多 agent 编排", "委派遥测", "隐藏 verifier", "resolved vs continuous", "成本前沿", "评测协议"],
        "summary_zh": (
            "把「多 agent 如何组织工作」形式化为可测能力：145 个长程任务、8 个专业域、17 种任务形态，"
            "每个任务给初始工作区与由隐藏 verifier 判分的整合交付物；agent 自主决定是否/如何委派，"
            "所有委派必须走统一 Workflow 工具（最多 16 并发 worker、原生 sub-agent 禁用），并共享同一时间预算，"
            "委派事件与主/子 agent 的 token、成本全部记账。25 个「模型 × effort」配置无一通吃：最强 Opus max 平均解出 36.95%，"
            "MATH 最高 95.83%、SWE 最高 29.41%、LAW ≤9.09%、FIN ≤18.75%；effort 对 Claude 系影响大（Opus 22.02–36.95、"
            "Sonnet 16.88–33.21），对 Astra/Sol 只 27.34–30.80 / 25.63–29.50。resolved 率与连续得分 Spearman 0.90，"
            "但域内差可达 66.16 分（Opus high SWE 得分 96.98 而 resolved 仅 17.65%；LAW 70.7 vs 2.9%），排名会翻转。"
            "成本：Sol low 27.59% @$3.61/任务、Opus high 34.11% @$6.66、Astra xhigh 30.80% @$29.26（低 3.31 分却贵 4.4×）。"
            "委派策略分家：Claude Code 系少委派大编组（Opus 0.86 次/任务、5.55 worker/次；Sonnet 0.76、6.14），"
            "Codex 系多委派小编组（Astra 2.09、1.72；Sol 1.94、1.69）；固定执行模型后 Opus 写的 workflow 提升所有弱执行者"
            "（Kimi 35.75→46.61、DeepSeek 18.37→25.24）。⚠️ 无 EDA 域、只测 9 个 API 模型；作者自报、本线未复现。"
        ),
        "abs_url": "https://arxiv.org/abs/2611.12856",
        "pdf_url": "https://arxiv.org/pdf/2611.12856",
        "first_seen": "2026-11-11",
    },
    {
        "arxiv_id": "2611.12712",
        "title": "Will AI mess my RTL? A snapshot-based approach to verifying AI-written RTL",
        "authors": ["Bernat Homs", "Oscar Palomar", "Miquel Moreto", "Marcelo Orenes-Vera"],
        "submitted": "2026-11-09",
        "updated": "2026-11-09",
        "category": "cs.SE",
        "areas": ["RTL 验证", "SystemVerilog 断言", "形式验证", "快照回归", "埋 bug 检出", "覆盖率计分", "非二值判分"],
        "summary_zh": (
            "提出 SVApshot：让 LLM 为已有 RTL 模块生成 SystemVerilog 断言（SVA），经语法修正、去重扩展、"
            "再用形式验证反例（CEX）反馈让 LLM 迭代修断言（每条最多 5 次），最终得到一组「对参考 RTL 证明通过」的断言快照，"
            "作为该模块功能的回归测试集；之后人/AI 改代码，跑快照即可发现功能被改坏。16 个 RTL 模块（24–419 行，"
            "含层次化子模块）上测 GPT-4.1-mini / Llama 3.3 70b / Llama 3.1 405b（JasperGold v2021.12）："
            "覆盖率连续可变，如 branch_unit 14.4%→42.0%、score_board_scalar 55.7%→86.0%、ptw 47.9%→52.8%、"
            "tlb 23.7%→39.3%、alu 初始即 100%；也有 mul_unit 上 Llama 3.3 仅 0.7%→1.76% 的失败。"
            "人工在 scoreboard 埋「64 位乘法误写 inst_d[2] 而非 inst_d[1]」的 bug，生成的断言成功检出。"
            "成本约 0.5 €/快照；时间主要在 Stage5 修断言（55 min、77.4%），FPV 工具占 69.4%。"
            "⚠️ 依赖 SystemVerilog + JasperGold、只测小模块、假设参考 RTL 正确；作者自报、本线未复现。"
        ),
        "abs_url": "https://arxiv.org/abs/2611.12712",
        "pdf_url": "https://arxiv.org/pdf/2611.12712",
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
        assert p["submitted"] == "2026-11-09", p["arxiv_id"]
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

    print("SEEN rows +%d -> %d lines" % (len(new_rows), len(seen_path.read_text(encoding='utf-8').splitlines())))
    print("papers.jsonl +%d -> %d lines" % (added, len(jl_lines)))


if __name__ == "__main__":
    main()

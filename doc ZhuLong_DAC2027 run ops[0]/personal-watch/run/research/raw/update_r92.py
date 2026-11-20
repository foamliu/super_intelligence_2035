#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十二轮（本地 2026-10-15 18:00 P0「补满 5 篇」轮）结果落盘。

- raw/2026-10-15-fetch-r92-seen.json 的 items（267 条 kept，窗口 <=72h）
  -> SEEN.md（收录 5 / 候选 262）
- 5 篇推荐（3 借鉴 + 2 科普）-> papers.jsonl
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-15-fetch-r92-seen.json"

FIRST_SEEN = "2026-10-15"
RECOMMENDED = ["2610.17637", "2610.17202", "2610.20193", "2610.19863", "2610.19587"]

SUMMARY_ZH = {
    "2610.17637": "既有规模律开始纳入量化（跟随 AI 加速器上的低精度数据类型），但多只考虑量化对「模型容量」的影响。本文从优化理论出发并实证校验，给出一个更准确的「前向 / 反向混精度训练」规模律：把量化对模型容量与对优化效率的影响分开建模，并显式刻画收敛分析中发现的「前向 / 反向量化带来的持续优化误差」。为选定拟合与评估区制，作者先把现有 4-bit 训练配方分解为前向 / 反向两部分、隔离出对 loss 影响最大的成分。在 Qwen3 的选定 4-bit 区制实验、加上已发表的 Llama 类实验上，该律随模型规模与 token 数增长的 loss 预测 MSE 比既有律最多低 11 倍；并进一步扩展到逐层混精度，在硬件感知算力预算下给出最优量化预训练配方（模型大小 / 训练 token / 逐层前向反向精度）。与以往精度规模律不同，该律预测「最优精度随算力预算提高而提高」。⚠️ 数字为作者自报、本线未复现。",
    "2610.17202": "Multi-Head Latent Attention（MLA）把 KV cache 压到潜在表示，降低推理显存与带宽；但既有 MHA2MLA / TransMLA 不支持 QKNorm、且在现代 LLM（尤其 MoE）上需要昂贵的恢复训练。作者提出 MLAfication：一个兼容 QKNorm、参数高效的 MHA2MLA 扩展，组合了校准式 KNorm、参数高效蒸馏、贡献感知的 Partial-RoPE 与激活感知的联合 KV 初始化。在 MHA 与 GQA 模型（含 QKNorm 与 MoE 变体）上，MLAfication 在显著 KV cache 压缩下仍保持性能，在常识与长上下文基准上超过当前 SOTA，并把 MLA 转换扩展到现代架构。在 Qwen3-30B-A3B 上，服务吞吐最高为 BF16 GQA 的 5.35×；配合 4-bit KV 量化可把 KV cache 占用降低 94.73%。代码开源（github.com/JT-Ushio/MLAfication）。⚠️ 数字为作者自报、本线未复现。",
    "2610.20193": "软件工程 agent 的训练受限于高质量「可执行任务」稀缺；开发历史含可构造此类任务的信号，但环境不全、单测缺失、产物不一致，往往需要大量重建。作者提出 SWE-Stream：通过「渐进式构造 + 弹性流式执行」来规模化可执行 SWE 训练数据 —— 渐进验证与精修任务候选，尽量复用已有产物、仅在必要时做定向补全；弹性调度器在共享资源约束下异步协调各构造阶段，按观测到的负载自适应执行预算。基于 6 种编程语言、10,728 个仓库的开发历史，构造 80,874 个经验证任务、采集 118,688 条成功轨迹。用这些轨迹微调 Qwen3-30B-A3B-Thinking-2507，在 SWE-bench Verified / Multilingual / Pro 上分别达到 69.0% / 49.3% / 45.42% 解决率；在训练预算大致匹配的受控对比中，SWE-bench Verified 上取得 45.6% 解决率、优于三种既有数据源。其流式构造策略效率更高：被接受任务吞吐为批式构造的 1.45×，比固定上限流式多接受 13.2% 任务。⚠️ 数字为作者自报、本线未复现。",
    "2610.19863": "LLM agent 越来越多地充当多智能体社会模拟中的「计算行动者」；既有工作强调代表性人格与平均行为，而社会科学表明「持续存在的尾部行动者」能不成比例地左右集体动态。作者在受控的 LLM 多智能体系统（LLM-MAS）中研究这一规律：这类行动者不能被简化为固定标量状态 —— prompt、自然语言历史与 backbone 生成共同中介其行为与影响。作者先分析社会学中极端者的三条性质，并以「LLM 原生」视角对 LLM 极端者建模，提出 EXAM（EXtremist Agent Modeling）框架：可为特定任务配置极端者 agent，并精确控制其人口比例、空间分布、交互协议与测量接口。在国会选举、金融危机、疫情舆论、重复囚徒困境四类场景中，观察到「小而持续的尾部群体」会产生可测量的、依赖 backbone 与场景的集体偏移；EXAM 展示了这一社会科学规律如何通过语言中介机制在 LLM 社会模拟中显现。⚠️ 结论为作者自报、本线未复现。",
    "2610.19587": "社会心理学早就描述了「人如何被说服把有害行为解读为道德」。近期研究表明 LLM 也复现了人类心理的若干侧面（认知偏差、社会从众等），由此引出一个有直接安全含义的问题：能否用「道德化」让 LLM 绕过安全护栏？作者提出一个基于「道德基础理论（MFT）」的多智能体框架：对一个最初被拒绝的有害请求，agent 先诊断该 prompt 违反了哪条道德基础，再找到一个能使同一请求显得「正当 / 美德」的道德基础，据此改写 prompt，并用生成的同类道德重构先例加以强化。作者在三个知名越狱数据集的有害 prompt 上、跨五个开源与专有模型评测：模型对「道德化」高度易感，单次尝试越狱率已很高，且在反复尝试下成功率进一步上升；同时发现安全基准在「所违反的道德基础」上分布不均衡，集中在模型本就存在偏差的那些基础上。⚠️ 结论为作者自报、本线未复现。",
}

AREAS = {
    "2610.17637": ["LLM", "预训练", "量化/混精度", "规模律"],
    "2610.17202": ["LLM", "推理效率", "KV cache/MLA", "MoE"],
    "2610.20193": ["agent harness", "SWE agent", "训练数据", "code agent"],
    "2610.19863": ["多智能体", "社会模拟", "科普"],
    "2610.19587": ["对齐安全", "越狱", "多智能体", "科普"],
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
        rec_rows.append("| %s | %s | %s | %s | 收录 |" % (FIRST_SEEN, k, clean_title(e["title"]), e["category"]))
    for k, e in sorted(by_base.items(), reverse=True):
        if k in RECOMMENDED:
            continue
        cand_rows.append("| %s | %s | %s | %s | 候选 |" % (FIRST_SEEN, k, clean_title(e["title"]), e["category"]))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last_idx = None
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("| 2026-"):
            last_idx = idx
            break
    assert last_idx is not None, "未找到最后数据行"
    new_lines = lines[: last_idx + 1] + rec_rows + cand_rows + lines[last_idx + 1:]
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
                "first_seen": FIRST_SEEN,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows added:", len(rec_rows) + len(cand_rows), "(rec %d / cand %d)" % (len(rec_rows), len(cand_rows)))
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

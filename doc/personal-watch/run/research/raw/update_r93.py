#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十三轮（本地 2026-10-16 06:00 P0「早 3」轮 · AM）结果落盘。

- 3 篇推荐（均「借鉴」）：2610.19605 / 2610.19210 / 2610.18616
  -> SEEN.md 对应 2026-10-15「候选」行 改为「收录」（行数不变 3487）
  -> papers.jsonl 追加 3 行（201 -> 204）
- 元数据取自前轮窗口内候选池 raw/2026-10-15-fetch-r92-seen.json（含官方 abstract/作者/日期）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-15-fetch-r92-seen.json"

FIRST_SEEN = "2026-10-16"
RECOMMENDED = ["2610.19605", "2610.19210", "2610.18616"]

SUMMARY_ZH = {
    "2610.19605": "LLM 长输出推理受 KV cache 显存与带宽瓶颈所困；KV cache 量化可缓解，但低比特（如 2-bit）严重掉精度，既有混合精度 key-cache 量化仅按 key 统计量估计通道显著性。作者在 RoPE 通道对（channel-pair）层面做注意力 logit 扰动分析，发现 query–key 对范数乘积大的通道对，其量化误差对 logit 变化贡献显著。据此提出 PN-Mix：在 prefill 阶段一次性识别这些显著通道对并分配更高精度、解码全程复用。在标准推理、代码生成与 AIME 基准上，PN-Mix 以 2.26-bit 平均精度达到或优于既往 2.32–2.39-bit 方法的平均精度；Pareto 扫描中可平滑退化到 1.5 bit，而对比基线在 2.25 bit 以下明显掉点。⚠️ 数字为作者自报、本线未复现。",
    "2610.19210": "Transformer 预训练可并行、但长上下文推理的 KV cache 越来越大；高效循环替代方案降低推理复杂度，却因顺序依赖限制 token 级并行、更难扩展，且「精确保留信息」与「长上下文推理高效」存在张力。作者提出 Titan-Llama：一种后训练方法，把基于注意力的预训练模型改造为分层记忆架构、并在测试时更新参数；用分块注意力掩码对最近 token 保留全保真注意力，把历史上下文压缩进循环、固定大小的神经记忆模块（NMM）。该形式化允许替换预训练注意力层而不必从头训练新模型。在 Llama-3.2-1B-Instruct 上，相对分段注意力窗口：QuALITY 准确率 23.87% → 40.51%、LongHealth 14.50% → 40.75%；推理基准显示 prefill 快 >20%、中等上下文长度 decode 快 37%、稳态 decode 显存降 24%。代码已开源（github.com/sarahpannn/titans-pytorch）。⚠️ 数字为作者自报、本线未复现。",
    "2610.18616": "在文本丰富的知识图谱上检索需要沿关系走同时查文本证据；预定义图接口限制了 agent 能拿到的证据（即便它会写代码组合工具调用、处理检索到的子图）。作者提出 DKGI（direct knowledge graph interaction）：一种 harness，让 LLM agent 直接在完整的节点/边文件上创建图访问工具 —— agent 写 Python 代码沿关系、组合节点集、选取文本证据，并把执行与 shell 搜索、文件检视交错；这让 agent 能批量处理大节点集，同时只把选中的文本交回模型评估。执行反馈引导工具创建与修订，演化的工具又决定 agent 下一步取哪些证据。在覆盖三个领域的基准上，免训练的 DKGI 在每个图上至少超过最强公开基线 6.7 Hit@1 点（即便用最小 harness）；对照消融显示多轮编程优于「仅 shell 访问」与「预定义图工具」。代码与数据开源（github.com/leopoldwhite/DKGI）。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.19605": ["LLM", "高效推理", "KV cache 量化", "显存/带宽"],
    "2610.19210": ["LLM", "长上下文", "记忆架构", "高效推理"],
    "2610.18616": ["agent harness", "工具创建/使用共演化", "图检索", "code agent"],
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
            if ln.startswith("| 2026-10-15 | %s |" % k) and ln.rstrip().endswith("| 候选 |"):
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

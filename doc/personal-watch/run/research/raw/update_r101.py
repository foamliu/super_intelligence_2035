#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零一轮（本地 2026-10-20 06:00 P0「早 3」轮 · AM）结果落盘。

- AM 轮**公告批次已刷新**：2026-10-15 -> 2026-10-16（最新样本 published=2026-10-16T17:59:55Z）
  - 首次 `--fetch`（window_mode=daily 72h）kept 0 / dropped 600：新批最老条目已约 76h，落在 72h 窗口外
  - 复跑 `--fetch --window-hours 120`（window_mode=override）kept 193 / dropped 383
  -> SEEN.md 追加 193 行（首次收录 = 2026-10-20），其中 3 行为「收录」、190 行为「候选」
  -> 台账 3,693 -> 3,886 行；累计 收录 221 -> 224 / 候选 2,965 -> 3,155 / 候选（RSS 补充）507
- 3 篇推荐（均「借鉴」）：2610.23796 FuTransformer / 2610.23449 GatewayBench / 2610.23787 DLite
  -> papers.jsonl 追加 3 行（221 -> 224）
- 元数据取自 id_list 权威复核 raw/2026-10-20-idlist-r101.xml（官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-20-fetch-r101-w120.json"

FIRST_SEEN = "2026-10-20"
RECOMMENDED = ["2610.23796", "2610.23449", "2610.23787"]

SUMMARY_ZH = {
    "2610.23796": (
        "针对 Llama 风格 Transformer 推理的两处不对称瓶颈——**prefill 复用权重**，主要受矩阵乘与激活搬运限制；"
        "**单 token decode 复用少**，主要受权重与 KV-cache 读取限制——作者给出一个面向 **NVIDIA Hopper** 的 CUDA 实现。"
        "沿 CODA 的「GEMM + epilogue」思路：KV-cache 直接落位、把固定 RMSNorm gain 折进权重、FP8 输出配合 delayed scaling 直接写出、"
        "prefill 免 padding；decode 使用 **INT4 投影权重**与 **INT4 KV-cache 副本**，权重与 key 按 Tensor Core fragment 布局"
        "**直接反量化进 MMA 操作数**（不生成完整中间 tile）；再用 **block-diagonal Hadamard 变换**压低 outlier 通道带来的 cache 量化误差。"
        "单张 H100 实测：prefill 较编译版 PyTorch FP8 快至多 **1.48×**、达 **1.29 PFLOP/s**；8B 形状 SwiGLU gate/up 投影的 BF16 路径较 CODA 快 **1.13×**，"
        "FP8 路径比所测 BF16 CODA 路径快 **2.02–2.18×**；8B/70B、batch 1–32 的 INT4 decode 比 PyTorch BF16/INT4 block 中较快者快 **1.3–2.4×**"
        "（比编译 + CUDA graph 的 BF16 快 2.1–3.3×，比 PyTorch INT4 投影 kernel 快 1.3–6.3×，比作者自己的 FP8 路径快 31–51%）；"
        "完整 Llama-3.1-8B decode 单步 **2.8 ms**（batch=1），编译版 transformers 为 8.1 ms。质量代价：WikiText-2 全 token 走 INT4 权重路径，"
        "perplexity **6.24 → 7.23**（round-to-nearest）或 **6.99**（同格式 GPTQ），旋转后的 INT4 cache 再加 **0.20**；kernel 与量化参考计算差在 0.001 ppl 内。"
        "⚠️ 数字为作者自报、本线未复现。"
    ),
    "2610.23449": (
        "agent 通过调用工具与外部环境交互，**MCP（Model Context Protocol）**正成为连接 agent 与异构工具/服务的标准接口；规模化部署后，"
        "**MCP gateway** 成为聚合、治理、塑造「暴露给 agent 的工具面」的关键中间层，但此前没有工作系统研究 gateway 设计如何影响 agent 的能力、效率与安全。"
        "作者提出 **GatewayBench**：首个面向 MCP gateway 的统一评测框架与基准；把 gateway 架构分为 **flattened（扁平）** 与 **hierarchical（分层）** 两大类；"
        "含 **6 个领域 524 个任务**、来自 **251 个真实 MCP server** 的 **11,118 个真实工具**；为模拟大规模部署，向每个 agent 环境**系统性注入与该任务无关的工具**（distractor），"
        "从而在受控条件下评测「可访问工具面」扩大时的影响。基于该基准评测 **7 个已广泛部署的 MCP gateway** 与多种 agent 配置，覆盖良性任务与对抗任务；"
        "结果显示不同 gateway 设计在**任务完成、工具使用效率、抗攻击韧性**上差异显著，且这些效应与底层模型和 **agent harness** 强烈交互。"
        "作者结论：MCP gateway 是 agentic AI 栈中「影响大但研究不足」的组件。⚠️ 摘要未给具体分数与 7 个 gateway 名单；数字/结论为作者自报，本线未复现。"
    ),
    "2610.23787": (
        "投机解码用轻量 draft 模型产生候选 token、再由目标模型验证，是 LLM 推理加速的主流手段；但 **agent 负载**带来长且持续演化的上下文与频繁多轮交互——"
        "作者观察到在这种负载下现有 draft 模型的**接受长度最多下降 80%**，而保留历史 KV-cache 又带来可观的系统开销。他们把「不断增长的历史上下文」"
        "识别为这两个问题的共同来源，提出 **DLite**：**无需维护历史**的投机解码框架，直接**复用目标模型已有的上下文 hidden states** 做局部投机预测，"
        "把「越来越复杂的建模问题」转化为「局部简单预测」；再加一个**轻量顺序 head** 以低开销恢复块内因果依赖；并给出面向这种异构无历史架构的**两阶段训练策略**。"
        "在通用、长上下文与 agent 负载上，DLite 取得 **2–6 的接受长度**，较当前最优方法 **DSpark 最多提升 70%**。"
        "⚠️ 数字为作者自报、本线未复现；摘要只给接受长度，未给端到端延迟 / 吞吐，也未给精度损失。"
    ),
}

AREAS = {
    "2610.23796": ["推理效率", "FP8", "INT4", "KV-cache 量化", "Hopper", "kernel"],
    "2610.23449": ["MCP gateway", "agent harness", "工具面", "评测基准", "安全"],
    "2610.23787": ["投机解码", "agent 推理", "长上下文", "draft 模型", "服务效率"],
}

SUMMARY_LINE = (
    "> **第一百零一轮（本地 2026-10-20 06:00（CST）· P0 第 4 批第 24 轮「早 3」轮 · 新一日 AM 轮）**："
    "**公告批次已刷新** —— `2026-10-15` → **`2026-10-16`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=633893 → 634451`，最新样本 `published=2026-10-16T17:59:55Z`）；"
    "**首次 `--fetch`**（`window_mode=daily` 72h）**15/15 `ok`**、**`kept 0` / `dropped 600`** —— 新批最老条目约 **76h**，"
    "整体落在 72h 窗口外（**方法论留痕**，非「无数据」）；**复跑 `--fetch --window-hours 120`**（`window_mode=override`，"
    "`generated=2026-10-19T22:04:28Z`）**15/15 `ok`**（14 条 `attempts=1`、`llm-large-language-model` **`attempts=2`** 一次脚本级重试后成功）、"
    "**`kept 193` / `dropped 383`** → **193 条全部为新发现**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL = **226**、cs.CV / cs.LG = **0 / 0**（`status=None`，如实记未取到）。"
    "**早报 3 篇「借鉴」取自当日新批 193 条** + **单条权威复核**（`id_list=2610.23796,2610.23449,2610.23787,2610.23342,2610.22428` → **5/5 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-20-idlist-r101.{xml,headers}`）："
    "`2610.23796` FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper / "
    "`2610.23449` GatewayBench: Unified Capability and Security Evaluation Platform for MCP Gateways / "
    "`2610.23787` DLite: History-free Speculative Decoding for Agentic AI。"
    "台账 **3,693 → 3,886 行（+193）**（3 行「收录」+ 190 行「候选」）→ 累计（**收录 224 / 候选 3,155 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **221 → 224**；证据 `raw/2026-10-20-{probe-r101.log,fetch-r101.log,fetch-r101-w120.json}` + 落盘脚本 `raw/update_r101.py`。"
    "口径见 `ARXIV_API.md` §9.102。"
)


def main():
    import xml.etree.ElementTree as ET

    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) == 193, "expected 193 items, got %d" % len(items)
    by = {}
    for e in items:
        by[re.sub(r"v\d+$", "", e["arxiv_id"])] = e
    for k in RECOMMENDED:
        assert k in by, "missing %s in fetch items" % k

    # 元数据以 id_list 权威复核为准
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-20-idlist-r101.xml").getroot()
    official = {}
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        cat = e.find("{http://arxiv.org/schemas/atom}primary_category")
        official[aid] = {
            "arxiv_id": aid,
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
        }
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k

    # 1) SEEN: 追加 193 行（按 arXiv ID 降序）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last = max(i for i, ln in enumerate(lines) if re.match(r"^\| 2026-\d\d-\d\d \|", ln))
    new_rows = []
    for k in sorted(by, reverse=True):
        e = by[k]
        status = "收录" if k in RECOMMENDED else "候选"
        new_rows.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, k, e["title"], e["category"], status))
    assert len(new_rows) == 193
    lines[last + 1: last + 1] = new_rows
    lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = official[k]
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
    st = {}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows +", len(new_rows), "(收录 %d / 候选 %d)" % (len(RECOMMENDED), len(new_rows) - len(RECOMMENDED)))
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

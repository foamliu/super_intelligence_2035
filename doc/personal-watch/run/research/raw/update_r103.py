#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零三轮（本地 2026-10-21 06:00 AM「早 3」轮）结果落盘。

- **公告批次未刷新**：仍 2026-10-19（totalResults=635673，最新 published=2026-10-19T17:59:59Z，
  与第一百零二轮 PM 完全一致）；`--fetch`（window_mode=daily 72h）14/15 ok（agent-tool-use FAIL）、
  **kept 0 / dropped 560**（10-19 整批已在前一轮 PM 入账 SEEN）⇒ 本轮**不新增 SEEN 行**
- 3 篇推荐（全部「借鉴」）取自上一轮已入账候选池：
  2610.26754 TokenGate / 2610.26834 KronLSTM / 2610.26836 Same Simulation, Different Evidence
  -> SEEN 中 3 行状态「候选」->「收录」（行数不变，仍 4,105）
  -> papers.jsonl 追加 3 行（226 -> 229）
- 元数据取自 id_list 权威复核 raw/2026-10-21-idlist-r103.xml（官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-10-21-idlist-r103.xml"

FIRST_SEEN = "2026-10-21"
RECOMMENDED = ["2610.26754", "2610.26834", "2610.26836"]

SUMMARY_ZH = {
    "2610.26754": (
        "长上下文 LLM 的主要成本在 **prefill**（每个 token 都要过每一层）。作者提出 **TokenGate**："
        "一个**可学习、即插即用的 token 剪枝**组件，为每个 token 学出重要性分数，**只把重要 token 送进后续层**。"
        "关键是绕过「top-K 不可导」：用受 MoE 启发的 **token-gated attention**（以重要性分数重加权 attention logits）实现**端到端训练**。"
        "在多种任务上，**prefill 首 token 时延（TTFT）快 1.4–11.3×、峰值显存降 1.5–3.4×**，精度不降；"
        "相对此前最好的 token 剪枝方法最多**快 6.4×、省 2× 显存**；适配成本「与标准 PEFT 相当」，"
        "并**原生支持标准 transformer（Qwen3）与混合注意力模型（Qwen3.5）**。作者声明代码开源。"
        "⚠️ 数字为作者自报、本线未复现；指标限于 **prefill**（未给 decode 吞吐）；未做全文精读。"
    ),
    "2610.26834": (
        "线性注意力的**关联矩阵记忆**需要持续写入新关联而不破坏旧关联。作者提出 **Kronecker Delta Rule**："
        "修正目标关联时**只沿矩阵空间的单一方向改动记忆**，比 delta-rule **更少干扰已存信息**。"
        "作者证明其记忆动力学是一条**收敛到稳态分布的马尔可夫链**，且记忆矩阵的**期望范数在整条输入序列上一致有界**，"
        "因此**不需要额外的归一化或稳定机制**。在长上下文基准上，与其竞争的 **(Gated) DeltaNet 家族**相比"
        "「有竞争力、且常常更优」；**代码与模型已开源**。"
        "⚠️ 摘要只给定性结论、**无具体数值**；属 xLSTM 家族新架构（非可插拔模块）；作者自报、本线未复现、未做全文精读。"
    ),
    "2610.26836": (
        "工具增强的 LLM agent 常把长工具输出**存成文件、按需检索**以省上下文。作者用真实科学工具"
        "（USGS 地球化学模拟器 **PHREEQC**，单份报告可达 **846.8k 字符**）构建 **158 道执行可验证选择题**，"
        "受测 GPT-5.1 / GPT-5.2 / Claude Opus 4.6 / Sonnet 4.6。结果：同一模拟、只改「报告内联 vs 通过 section index 检索」，"
        "**GPT-5.1 / GPT-5.2 准确率分别掉 11.3 / 7.9 分**，Claude 两模型**无可测损失**。"
        "复跑 **11,007 次**模拟调用后定位机理：失败**不是算错**，而是**证据替换（evidence substitution）**——"
        "agent 跳过权威报告、拿自己更高精度的输出文件作答并舍入到邻近选项。"
        "**点名权威输出**可回升 **6.3–7.9 分**；对 GPT-5.x **直接内联**同样有效；「要求正确舍入」**无效**。"
        "⚠️ 单工具单领域（非 EDA）、多选题形式；受测模型与我们不同，结论不可直接外推；未声明代码；作者自报、本线未复现。"
    ),
}

AREAS = {
    "2610.26754": ["长上下文", "prefill", "token 剪枝", "可学习门控", "TTFT", "显存"],
    "2610.26834": ["线性注意力", "长上下文", "关联记忆", "记忆稳定性", "xLSTM", "DeltaNet"],
    "2610.26836": ["agent harness", "工具输出管理", "检索 vs 上下文", "证据替换", "评测"],
}

SUMMARY_LINE = (
    "> **第一百零三轮（本地 2026-10-21 06:00（CST）· P0 第 5 批第 1 轮「早 3」轮）**："
    "**公告批次未刷新** —— 仍 **`2026-10-19`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=635673`，最新样本 `published=2026-10-19T17:59:59Z`，**与第一百零二轮 PM 完全一致**；"
    "周二 20:00 ET 批次尚未被索引）；**14/15 查询 `ok`**（13 条 `attempts=1`、`agent-csma-multiagent` `attempts=2`；"
    "**`agent-tool-use` `FAIL`**，`attempts=3` 耗尽，`Read timed out (read timeout=30)`，如实记失败）、"
    "**`kept 0` / `dropped 560`**（`window_mode=daily` 72h，`generated=2026-10-20T22:02:02Z`）"
    "—— **`kept 0` 的成因是「10-19 整批已在前一轮 PM 入账 SEEN」，不是「无数据」、也不是「窗口越界」**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL·CV·LG = **435 / 505 / 817**（`HTTP 200`，仅作发现）。"
    "**早报 3 篇「借鉴」取自上一轮已入账候选池** + **单条权威复核**（`id_list=2610.26834,2610.26754,2610.26836,2610.26342,2610.25516` "
    "→ **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-21-idlist-r103.{xml,headers}`）："
    "`2610.26754` TokenGate: Adapting LLMs for Fast and Memory-Efficient Prefill with Learned Token Pruning / "
    "`2610.26834` Kronecker Delta Rule for Long Context Linear Attention / "
    "`2610.26836` Same Simulation, Different Evidence: Where Retrieved Tool Output Costs LLM Agents Accuracy。"
    "3 篇首次提交均 **2026-10-19**（**非当日新提交**，页面已显式标注）。"
    "台账 **行数不变 4,105**（3 行「候选」→「收录」）→ 累计（**收录 229 / 候选 3,369 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **226 → 229**；PDF 3/3 落地校验通过；证据 `raw/2026-10-21-{probe-r103.log,fetch-r103.log,fetch-r103-seen.json}` "
    "+ 落盘脚本 `raw/update_r103.py`。口径见 `ARXIV_API.md` §9.103。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(XML).getroot()
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
    assert len(official) == 5, "expected 5 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-19"), official[k]["published"]
    return official


def main():
    official = load_official()

    # 1) SEEN: 3 行「候选」->「收录」（行数不变）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\| (\d{4}-\d\d-\d\d) \| ([^ |]+) \| (.+?) \| ([^ |]+) \| (候选|收录) \|$", ln)
        if not m or m.group(2) not in RECOMMENDED:
            continue
        assert m.group(5) == "候选", "%s already %s" % (m.group(2), m.group(5))
        lines[i] = "| %s | %s | %s | %s | 收录 |" % (
            m.group(1), m.group(2), m.group(3), m.group(4))
        flipped += 1
    assert flipped == 3, "expected 3 rows flipped, got %d" % flipped
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加 3 行（按 ID 升序，与页面顺序一致）
    existing = set()
    with PAPERS.open(encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                existing.add(json.loads(ln)["arxiv_id"])
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            assert k not in existing, "%s already in papers.jsonl" % k
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
    print("SEEN rows flipped: %d" % flipped)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


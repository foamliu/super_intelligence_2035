#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十三轮（本地 2026-10-31 06:00 AM「早 3」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-31-am-fetch-r123-seen.json`（`--fetch --seen`，`generated=2026-10-30T22:01:13Z`）
  - `raw/2026-10-31-am-idlist-r123a.xml`（官方 Atom 元数据：2610.38095 / 2610.40305）
  - `raw/2026-10-31-am-idlist-r123b.xml`（官方 Atom 元数据：2610.40574）

动作：
  1) 断言：15 查询全 200 / 全 `attempts=1`、`kept 0` / `dropped 600`（558 已入 SEEN + 42 stale）、
     `window_mode=daily`、`items==[]`；
  2) `SEEN.md`：3 个推荐 ID 原为「候选」，本轮只翻成「收录」（**不新增行**）；
  3) `papers.jsonl`：追加 3 条（元数据取自官方 id_list XML）；
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-31-am-fetch-r123-seen.json"
XML_A = BASE / "raw" / "2026-10-31-am-idlist-r123a.xml"
XML_B = BASE / "raw" / "2026-10-31-am-idlist-r123b.xml"

RECOMMENDED = ["2610.38095", "2610.40305", "2610.40574"]
FIRST_SEEN = "2026-10-30"  # 三条均来自 r122 候选池（当日入 SEEN，状态=候选）

AREAS = {
    "2610.38095": ["LLM", "MoE", "混合架构", "Mamba-Transformer", "蒸馏", "投机解码", "量化", "agent harness"],
    "2610.40305": ["LLM", "推理服务", "内存管理", "专家卸载", "MoE", "vLLM", "SLM"],
    "2610.40574": ["LLM", "后训练", "蒸馏", "on-policy", "数学推理", "SLM"],
}

SUMMARY_ZH = {
    "2610.38095": (
        "NVIDIA 放出两个**开源的 MoE 混合 Mamba–Transformer** 模型：**Nemotron 3.5 Super**（120B 总参 / 12B 激活，"
        "多模态 VL）与 **Nemotron 3.5 Lightning**（30B / 3B 激活，纯文本），面向推理、长上下文与长时间运行的 agent 负载。"
        "两者都走「**大规模蒸馏 + 长上下文训练 + 原生投机解码（MTP）**」三件套：Super 由 Super 3 Base 初始化、"
        "Lightning 由 Nano 3 Base 初始化，**各用 1 万亿 token 蒸馏**（Lightning 取 Super 3 Base 的 **top-128 logits** 作为教师，"
        "损失 = **0.9×前向 KL + 0.1×交叉熵**（另加 sink token 承接 top-128 之外的残差概率），LR 从 **1e-5 缓慢升到 1e-4**"
        " 用掉 200B tokens、再线性退回 1e-5）。投机解码用**递归共享的 MTP 头**，先**冻结主干、只用 100B tokens 训 MTP 头**；"
        "作者指出现成两段递归训练会造成**训练–推理的条件分布错配**（推理时 MTP 头看到的是主干隐状态与合成隐状态的混合）⇒ "
        "Super 改用**隐状态混合（hidden-state mixing）**让第 k 步在 1…k−1 的隐状态里采样，从而在更深草稿步上保住接受率。"
        "后训练 = SFT + RLVR/RLHF，Super 另加**专门教师训练 + 多教师 on-policy 蒸馏（MOPD）**，并有"
        "**agentic 软件工程 mid-training**（Codex harness 下 SWE-bench Verified **48.4% → 61.8%**）。"
        "结果（**厂商自报**）：后训练的 Super 在 **SWE-bench Pro 51.78%**，**超过 Nemotron 3 Ultra，而激活参数约少 4.6×**；"
        "MTP boosting 把投机解码接受长度从 **4.287 → 4.718**（最高 **+21.8%**）；**NVFP4** 量化相对 BF16 "
        "**中位精度恢复 99.62%**、交互式 agent 负载下吞吐 **2.43×**（BF16 基线）；GB200 上最高 "
        "**4,856 output tokens/s/GPU** 且每用户 ≥50 tokens/s；Indic 继续预训练（约 **2.83 万亿**合成 token、22 种印度语言）"
        "使相关基准最高 **+9.82 个百分点**。作者一并开源 base / BF16 后训练 / NVFP4 三种 checkpoint、独立并行 drafters"
        "（LiLiCorr、DFlash、DSpark）、数据与训练配方。⚠️ 79 页技术报告、**559 位署名（NVIDIA）**；"
        "全部数字为厂商自报，对比基线多为自建或闭源，**本线未复现**。"
    ),
    "2610.40305": (
        "把 LLM 服务里的「**权重**」和「**注意力状态（KV）**」从两块固定内存池改成一个**共享页池**：Rimuru 在 vLLM 之上实现"
        "（≈4,400 行，页表感知的 expert GEMM 用 Triton、专家加载用 C++ 扩展），核心是四种机制 —— "
        "① **共享页池 + memory views**：不同张量类型用各自的**页大小与页表**解释同一段内存；"
        "② **大页对齐 + 多级页分配器**（可切分/合并）实现跨类型容量复用；③ **页表感知的融合 MoE kernel** 直接读取"
        "**非连续**的专家权重，省掉拷贝；④ **负载感知调节器**在运行时按需求在张量类型间重新分配页（即「弹性专家卸载」）。"
        "动机是现有系统给权重与 KV 划**固定边界**：重负载下 KV 容量不足限制并发，轻负载下闲置内存又不能挪用。"
        "实验：8×RTX 5090（32GB）与 2×RTX 4090D（24GB）两台机器；模型 Qwen3-30B-A3B、Qwen3.5-35B-A3B、"
        "Qwen3.5-122B-A10B；负载 ShareGPT；基线 vLLM / SGLang / KTransformers / Fate / llama.cpp。"
        "结果（**作者自报**）：相对卸载类基线吞吐 **1.39×–19.03×**（19.03× 出现在 4090D 上对 KTransformers —— "
        "该机 CPU 无 AMX、只能走 AVX2，作者也注明这是对方退化场景）、**TTFT 平均降低 98.1%**（最高 99%）、"
        "对 Fate **11.34×**、对 llama.cpp **12.7×**；与 SGLang / vLLM 比 **1.1×–2.88×**。"
        "⚠️ 边界：只用消费级 GPU + Qwen MoE 系模型 + 合成请求流；vLLM 在其中一个配置因 Triton GDN kernel autotuning "
        "**OOM** 被移出该面板（作者如实写出）；数字自报、本线未复现。"
    ),
    "2610.40574": (
        "on-policy 自蒸馏（OPSD）里，教师要么整段固定（始终看完整参考答案），要么**按整条回答**调参考暴露比例；"
        "作者用**教师干预试验**说明：**同一条回答内，每个 token 偏好的教师都不一样** ⇒ 提出 **MTA-OPSD**：构造"
        "**多教师池**（7 种参考暴露配置：完整参考 / prefix-0.5 / prefix-0.75 / suffix-0.5 / suffix-0.75 / "
        "random-span-0.5 / random-span-0.75，每种都保留最终答案），再用**多数投票 + KL 选择**为**每个 token** 挑教师，"
        "学生只对被选中的教师做 on-policy 蒸馏。实验：Qwen3-1.7B / 4B / 8B 三个规模（thinking 模式），"
        "训练数据 DeepMath-103K（中等难度），评测 AMC23 / AIME24 / AIME25，各方法同为 **300 步**、"
        "每 50 步评测取最佳 **Avg@12**；基线 OPSD（前向 KL + token 级 KL 裁剪）、SDPO（JSD）、"
        "Paint（按学生–教师差距自适应调暴露比例）。结果（**作者自报**）：平均分相对 base 提升 "
        "**+5.9（1.7B）/ +1.5（4B）/ +2.8（8B）**，三个规模均为最高平均分；消融显示多数投票与 KL 选择都用上才最好，"
        "且**教师选择在池内分布较均匀、没有塌到单一教师**。⚠️ 边界：**只做数学推理**、只用 Qwen3 系学生、"
        "只有 3 个基准；对比是**按步数对齐**（300 步），而 7 个教师配置意味着更多教师前向 ⇒ "
        "**论文没有给出等算力/等墙钟的对照**；代码 `github.com/xingzhejun/MTA-OPSD`；数字自报、本线未复现。"
    ),
}

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
EXPECT_PUB = {
    "2610.38095": "2026-10-28",
    "2610.40305": "2026-10-29",
    "2610.40574": "2026-10-29",
}


def load_official():
    out = {}
    for xml in (XML_A, XML_B):
        for e in ET.parse(xml).getroot().findall("a:entry", NS):
            aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
            out[aid] = {
                "title": " ".join(e.find("a:title", NS).text.split()),
                "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                "published": e.find("a:published", NS).text,
                "updated": e.find("a:updated", NS).text,
                "category": e.find("x:primary_category", NS).attrib["term"],
            }
    assert set(RECOMMENDED).issubset(out), (RECOMMENDED, out.keys())
    # ⚠️ 如实记录：`r123a` 是按**初选组合**取的（含 `2610.37842`），但该篇 `published=2026-10-27T18:52:54Z`
    # 在本轮唤醒时已 ≈83h > 72h（超出 §0.1 时效）⇒ 改选 `2610.40574`（`published=2026-10-29`）并补取 `r123b`。
    # `37842` 的元数据保留在 `r123a` 原件里备查，但**不作为本轮推荐**。
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return {k: out[k] for k in RECOMMENDED}


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert all(a == 1 for a in attempts), attempts
    assert items == [], len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    assert (n_seen, n_stale) == (558, 42), (n_seen, n_stale)

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    rows = {}
    for i, ln in enumerate(lines):
        m = ANY_ROW_RE.match(ln)
        if m:
            rows.setdefault(m.group(1), []).append((i, m.group(2)))
    before_lines = len(lines)
    for k in RECOMMENDED:
        assert k in rows, "%s not in SEEN" % k
        assert len(rows[k]) == 1, (k, rows[k])
        idx, status = rows[k][0]
        assert status == "候选", (k, status)
        lines[idx] = lines[idx].replace("| 候选 |", "| 收录 |")

    SEEN.write_text("\n".join(lines), encoding="utf-8")
    assert len(lines) == before_lines, "SEEN line count changed"

    have = set()
    with PAPERS.open(encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                have.add(json.loads(ln)["arxiv_id"])
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            assert k not in have, "%s already in papers.jsonl" % k
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

    st = {}
    for ln in lines:
        m = ANY_ROW_RE.match(ln)
        if m:
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN lines:", len(lines), "(unchanged)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十五轮（本地 2026-11-01 06:00 AM「早 3」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-11-01-am-fetch-r125-seen.json`（`--fetch --seen`，`generated=2026-10-31T22:01:30Z`）
  - `raw/2026-11-01-am-idlist-r125a.xml`（官方 Atom 元数据，10 条短名单中取 3 条）

动作：
  1) 断言：15 查询全 `ok` / `HTTP 200` / `attempts=1`、`kept 0` / `dropped 600`、
     `window_mode=weekend_batch`（120h，周日 arXiv 未公告 ⇒ 脚本自动放宽）、`items==0`；
  2) `SEEN.md`：**不新增行**（本批 217 条已在 r122 入账）；只把 3 篇推荐论文的
     状态由「候选」翻为「收录」；
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
FETCH = BASE / "raw" / "2026-11-01-am-fetch-r125-seen.json"
XML = BASE / "raw" / "2026-11-01-am-idlist-r125a.xml"

RECOMMENDED = ["2610.40577", "2610.39562", "2610.38329"]
FIRST_SEEN = "2026-11-01"
EXPECT_PUB = {"2610.40577": "2026-10-29", "2610.39562": "2026-10-29", "2610.38329": "2026-10-28"}

AREAS = {
    "2610.40577": ["LLM", "MoE", "路由 / router", "预训练配方", "latent view", "借鉴"],
    "2610.39562": ["多模态", "MLLM 推理", "prefill / TTFT", "token 剪枝", "KV / 循环态", "借鉴"],
    "2610.38329": ["agent harness", "kernel 优化", "NPU / DSL", "AI for 芯片", "借鉴"],
}

SUMMARY_ZH = {
    "2610.40577": (
        "传统 MoE 只用一个路由头做 top-k 选专家；作者先做「稠密评估」实验，发现**单路由排序与实际专家效用排序在中层/深层明显不一致**。"
        "**Multi-View MoE** 用**多个独立初始化的 sigmoid 路由头**汇总分数做选择，并把每个被选专家在各路由上的相对分数用来**混合多个学到的 latent view** 作为该专家的输入"
        "（每个被选专家仍只做一次前向）。在 **24 层 10B-A1B**（top-8 路由 + 1 个常驻共享专家）、**708B tokens** 上，"
        "九任务均值 **33.07 → 34.25（+1.18 个百分点）**，单加 Multi-Router 为 **33.69（+0.6）**；相对 Multi-Router，GPQA **+2.74**、MMLU-Redux **+2.03**。"
        "参数开销 **≈0.19%**（路由 +0.06% + 视图投影 +0.13%），激活专家数 / 专家 FLOPs / all-to-all 通信量不变。⚠️ 作者自报、本线未复现。"
    ),
    "2610.39562": (
        "多轮多模态对话里，长图像/视频输入把 TTFT 拉高；按当前问题做**硬剪枝**能降 prefill，但被剪掉的 token **永久丢失**，后续问题可能需要它们。"
        "**Raincheck** 把「初始选哪些 token」与「后续还能不能用」解耦：先用现有剪枝方法选 30% 做初始 prefill，"
        "**未选中的 token 在解码阶段的闲置算力里按源顺序渐进补 prefill**，答完仍可继续补；"
        "靠 **attention 可见性控制 + 仿射状态映射**，让 full-attention 与 hybrid 循环模型在「已开始生成」后还能更新上下文；prefill-decode 融合减少重复权重读取。"
        "在 Qwen3-VL-8B / Qwen3.5-9B、30% 初始保留、4 种剪枝方法上，分别找回硬剪枝损失质量的 **77.7% / 60.4%**（MultiVerse / ConvBench）；"
        "**MultiVerse 首轮 TTFT 相对全量 prefill 降低 24.1% / 17.9%**，平均 TPOT 仅增 **0.13% / 0.47%**。⚠️ 作者自报、本线未复现。"
    ),
    "2610.38329": (
        "前沿 LLM 写 CUDA kernel 已经不错，但换到**没见过、文档稀疏的加速器**上正确率会塌。作者做了一份**单案例研究**："
        "在 **FuriosaAI RNGD NPU**（新 Rust DSL，文档少）上，用 LLM agent 循环在**共享且稀缺的设备**上、**12 天（283 h）**优化 **3 个 Gemma-4-12B 解码 kernel**。"
        "循环自己**建目标知识**（读并自检 DSL 文档摘要、用微基准测芯片、记录编译器派生的合法性规则，工具链变了就回查），"
        "用**基于角色的 Design Tree 搜索**做整 kernel 设计并累积小改动；设备时间稀缺 + 读数有噪声 ⇒ **先用廉价检查筛掉候选**，后期只在设备上反复对比后才接受改动。"
        "最终 kernel 相对官方基线 **几何平均 9.293×**，每个 kernel 的周期数**在「仅搬运权重所需周期」的 1.25× 以内**。⚠️ 单案例、作者自报、本线未复现。"
    ),
}



def load_official():
    root = ET.parse(XML).getroot()
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    out = {}
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [a.find("a:name", ns).text for a in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": e.find("x:primary_category", ns).attrib["term"],
        }
    assert len(out) == 10, len(out)
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return out


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)
ROW_RE = re.compile(r"^\| [0-9-]{10} \| ([0-9.]+) \|")


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert float(meta["window_hours"]) == 120.0, meta["window_hours"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert attempts == [1] * 15, attempts
    assert len(items) == 0, len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    assert (n_seen, n_stale) == (558, 42), (n_seen, n_stale)
    print("dropped: already_in_SEEN=%d stale=%d" % (n_seen, n_stale))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    hit = {}
    for i, ln in enumerate(lines):
        m = ROW_RE.match(ln)
        if m and m.group(1) in RECOMMENDED:
            hit[m.group(1)] = i
    assert set(hit) == set(RECOMMENDED), hit
    for aid, i in hit.items():
        assert lines[i].rstrip().endswith("| 候选 |"), lines[i]
        lines[i] = lines[i].rstrip()[: -len("候选 |")] + "收录 |"
        assert lines[i].endswith("| 收录 |"), lines[i]
    SEEN.write_text("\n".join(lines), encoding="utf-8")

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
    print("SEEN lines:", len(lines), "(+0)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

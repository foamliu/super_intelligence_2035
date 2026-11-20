#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十七轮（本地 2026-11-02 06:00 AM「早 3」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-11-02-am-fetch-r127-seen.json`（`--fetch --seen`，`generated=2026-11-01T22:02:04Z`）
  - `raw/2026-11-02-am-idlist-r127a.xml`（官方 Atom 元数据，6 条短名单中取 3 条）

动作：断言 fetch 结果 → SEEN 状态「候选」→「收录」（不新增行）→ `papers.jsonl` 追加 3 条。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-11-02-am-fetch-r127-seen.json"
XML = BASE / "raw" / "2026-11-02-am-idlist-r127a.xml"

RECOMMENDED = ["2610.39412", "2610.40039", "2610.40541"]
FIRST_SEEN = "2026-11-02"
EXPECT_PUB = {
    "2610.39412": "2026-10-29",
    "2610.40039": "2026-10-29",
    "2610.40541": "2026-10-29",
}

AREAS = {
    "2610.39412": ["训练效率", "分布式优化器", "Muon/矩阵感知", "FSDP/TP 通信", "借鉴"],
    "2610.40039": ["端侧推理", "VLM", "边缘 NPU", "跨层测量", "借鉴"],
    "2610.40541": ["推理调度", "解码长度预测", "prefill", "基准口径", "借鉴"],
}

SUMMARY_ZH = {
    "2610.39412": (
        "参数与优化器状态超过单节点内存时，只能把张量切分到多卡；而在 TP / FSDP 下，"
        "像 Muon 这类「矩阵感知」优化器要做跨分片的全局矩阵运算（如正交化），于是引入额外通信。"
        "本文提出 Dobb（Distributed Optimizer with Block-diagonal Eigenbases）："
        "用对角块近似输入激活的二阶矩，在每个块内维护一套完整特征基，把动量投影到该基、"
        "对系数做 sign normalization 再反变换得到更新 —— 只要每个块落在一个分片内，"
        "矩阵更新就能本地完成，除数据并行的二阶矩同步外不需要额外通信。"
        "对照同样为削减通信而设计的矩阵感知优化器 Dion：在 GPT-2 XL（1.56B 参数）上，"
        "Dobb 取 16 个块时验证损失 2.476，Dion（秩比例 1/16）为 2.511；"
        "在 32×H100 的 FSDP 上，Dobb 把摊薄后的优化器调用时间从 Dion 的 124.1 ms 降到 9.2 ms。"
        "⚠️ 作者自报、本线未复现。"
    ),
    "2610.40039": (
        "端侧 VLM 部署已经堆了很多「架构 / 运行时 / 硬件加速」层面的单点优化，但跨层如何协同仍少有人系统测过。"
        "本文做实证测量：6 个代表性 VLM × 3 个真实边缘平台 × 10 个多模态基准，"
        "从端到端时延与热特征一路下钻到 kernel 级执行行为，并挑战了几条社区常见假设："
        "① softmax 主导 attention 开销，即便用查表式 softmax 优化，也消不掉让 NPU 矩阵单元严重闲置的流水线气泡；"
        "② 线性注意力纸面上的加速在真实 NPU 上被张量重排开销吃掉；"
        "③ 没有哪个后端在自回归解码上全面占优 —— 是 attention 张量形状决定的并行度在左右 NPU 效率，"
        "并改变 CPU–NPU 的性能平衡。作者还发现各任务存在 Sweet Resolution（分辨率甜点）："
        "小幅时延代价换取可观的精度增益，并给出面向硬件架构师 / 运行时开发者 / 模型设计者的跨层建议。"
        "⚠️ 作者自报、本线未复现。"
    ),
    "2610.40541": (
        "只用 prefill 阶段隐状态预测 LLM 会解码多少 token，是推理调度（批组队、容量规划）的关键原语。"
        "作者先指出：现有基准把预测器质量与任务难度混在一起 —— 换个目标模型、数据集或采样配置，"
        "报出的准确率就塌，而预测器本身没变。根因是被忽视的误差源：自回归解码的固有随机性。"
        "本文把解码视为停时随机过程：单步停止概率不是常数，而是在数百步内逐步上升，"
        "解码长度因而从众多局部决策继承中心极限定理 —— 得到逐 prompt 的正态性与显式误差项，"
        "以及仿射方差律 σ = αμ + b（斜率 = 响应分段数的变异系数）。"
        "实测上正态律能把逐 prompt MAE 与解码长度分布的主体质量复现到几个百分点以内，"
        "偏离正态的部分（轻微右偏、略高峭度）恰是采样噪声修正所预测的方向。"
        "在固定模型 / 数据 / 采样条件时，一大片预测器设计（MLP、EGTP、FiLM、soft-label、MoE 变体）"
        "都收敛到接近该上界的性能 ⇒ 说明「系统误差主导模型误差」。"
        "作者据此主张：基准协议应固定模型/数据/采样参数，并同时报相对误差与绝对指标。"
        "⚠️ 作者自报、本线未复现。"
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
    assert len(out) == 6, len(out)
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十九轮（本地 2026-11-03 06:00 AM「早 3」轮）：台账落盘（幂等）。

只追加 3 条**最近公告批次**论文（`published=2026-10-30`）：
  - `2610.42147` Latent Sparse Attention（cs.AI · 借鉴）
  - `2610.41359` LEAP（cs.AI · 借鉴）
  - `2610.41177` TraceSpec（cs.CL · 借鉴）

断言（幂等，可重复执行）：
  ① `SEEN.md` 中三 ID 原先**不存在**（本轮 291 条候选与 SEEN 0 重叠）；
  ② 追加后三 ID 各出现 1 行，状态为「收录」；
  ③ `papers.jsonl` 追加后行数 == 旧行数 + 3（已存在则不重复追加）；
  ④ 元数据全部来自官方 `id_list` XML（`raw/2026-11-03-am-idlist-r129a.xml`）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-11-03-am-idlist-r129a.xml"

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}

RECOMMENDED = ["2610.42147", "2610.41359", "2610.41177"]
SUMMARY = {
    "2610.42147": (
        "超长上下文下全注意力代价不可承受，稀疏注意力的瓶颈在索引器本身。作者提出 Latent Sparse "
        "Attention（LSA）：把 key 在学到的低维隐空间里做层次聚类，query 只给「簇中心」打分再下钻，"
        "因此 prefill / decode / 训练都更快。两个变体：D-LSA（对预训练模型做蒸馏，短 KL 阶段）与 "
        "N-LSA（从零用 next-token loss 训练）。在 GLM-5.3-FLASH（QWEN-3.8-27B）10M token 上，"
        "D-LSA 让单层注意力 prefill 提速 22.7×（对全注意力 72.4×）、decode 提速 4.6×（42.5×），"
        "精度大体保持；10M 时索引内存 246 MiB/层，基线 331 MiB、QSA 642 MiB。N-LSA 用 0.5B 混合模型"
        "（每 4 层 1 个注意力层、其余 Gated DeltaNet；100B FineWeb-Edu@4k + 12B LongDocs@128k）在 "
        "128k 上验证损失 1.085 与全注意力持平（PISA 1.100 / NSA 1.117 / SWA 1.154），单层训练 1.6× 加速。"
        "作者另建 PaperTrail 超长上下文基准（1,246 篇、512k–10M、植入伪造论文的证据链 + 4 组对照）。"
        "⚠️ 作者自报、本线未复现；速度数字为作者在 H200/B300 + SGLang 特定并行配置下的实测。"
    ),
    "2610.41359": (
        "长度感知调度能降时延，但长度预测器在领域/任务漂移下排序能力退化、重训贵、推理开销还可能吃掉收益。"
        "作者提出 LEAP：直接复用服务模型 prefill 的隐状态（Qwen 默认取 block 30 的最后一个 prompt token），"
        "用线性读出预测输出长度；再用递归最小二乘（RLS）以已完成请求为监督在线更新，无需梯度、无需回放历史数据；"
        "预测与更新都异步跑在 CPU 上，与剩余 GPU prefill 重叠。评测：Qwen3-8B / Llama3.1-8B-Instruct / "
        "Mistral-7B-Instruct-v0.3，Alpaca / ShareGPT / LMSYS-Chat-1M，并做 Alpaca / MATH / Aya 跨域迁移。"
        "单卡 A800 80GB + vLLM 0.8.5.post1 eager 上，平均每 token 时延比 LTR −15.9%、TIE −19.0%、TRAIL −40.8%，"
        "吞吐比 LTR +1.9%，TTFT 接近 FCFS；大漂移下在线适配把 Spearman 相关提升 64.7%；预测器参数比最强基线少 30,569×。"
        "⚠️ 作者自报、本线未复现；作者自陈局限：原型仅单卡 eager 模式 vLLM（多卡 / prefix cache / chunked prefill 未覆盖）、"
        "读出不看 temperature/top-k、结果为共享机器上的单次运行。"
    ),
    "2610.41177": (
        "LLM agent 靠反复调用模型推进（推理—动作—工具反馈不断变长的历史），而聚合口径的投机解码指标会把不同决策"
        "混成一个数。作者提出 TraceSpec：把轨迹级评测与 draft 自适应训练接起来（动态执行 + 固定前缀回放），"
        "并发布 TraceSpec-Traj（10,000 训练状态 / 2,500 测试状态，覆盖浏览与软件工程）。分析 5 个投机基线发现："
        "聚合接受率会随上下文变长而上升，但同一阶段的晚期动作反而下降，故 supervision 应由轨迹条件决定。"
        "方法：在中间 assistant turn 上训练 draft，并按「状态条件化的前缀感知接受率缺口」在固定预测预算内分配。"
        "结果（Qwen3-4B/8B/14B，T∈{0,1}，共 108 个配置）：回放吞吐比 DSpark 高 12.5%–22.6%，验证产出率 +8.4–11.2 个百分点，"
        "动态执行吞吐 +1.4%–5.5%；Qwen3-4B 上回放接受长度比「固定全轮监督」高 3.3%–10.0%。"
        "⚠️ 作者自报、本线未复现；SWE 的编辑/测试反馈为模拟反馈（非真实 CI），episode 时延还受工具成本影响。"
    ),
}
AREAS = {
    "2610.42147": ["长上下文", "稀疏注意力", "学习式索引", "层次聚类", "训练与推理加速", "KV 索引内存"],
    "2610.41359": ["LLM 推理服务", "调度", "输出长度预测", "在线适配", "CPU 异步", "尾时延"],
    "2610.41177": ["投机解码", "LLM agent", "code agent", "轨迹级评测", "draft 训练", "吞吐"],
}


def official():
    out = {}
    for e in ET.parse(XML).getroot().findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", NS).text.split()),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "published": e.find("a:published", NS).text,
            "updated": e.find("a:updated", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
        }
    assert sorted(out) == sorted(RECOMMENDED), sorted(out)
    return out


def main():
    meta = official()
    lines = SEEN.read_text(encoding="utf-8").splitlines()
    for aid in RECOMMENDED:
        hits = [ln for ln in lines if ("| %s |" % aid) in ln]
        assert not hits, "SEEN already has %s: %r" % (aid, hits[:1])

    seen_rows = []
    paper_rows = []
    for aid in RECOMMENDED:
        m = meta[aid]
        assert m["published"].startswith("2026-10-30"), m["published"]
        seen_rows.append("| 2026-11-03 | %s | %s | %s | 收录 |" % (aid, m["title"], m["category"]))
        paper_rows.append(json.dumps({
            "arxiv_id": aid,
            "title": m["title"],
            "authors": m["authors"],
            "submitted": m["published"][:10],
            "updated": m["updated"][:10],
            "category": m["category"],
            "areas": AREAS[aid],
            "summary_zh": SUMMARY[aid],
            "abs_url": "https://arxiv.org/abs/%s" % aid,
            "pdf_url": "https://arxiv.org/pdf/%s" % aid,
            "first_seen": "2026-11-03",
        }, ensure_ascii=False))

    while lines and not lines[-1].strip():
        lines.pop()
    SEEN.write_text("\n".join(lines + seen_rows) + "\n", encoding="utf-8")

    old = PAPERS.read_text(encoding="utf-8").splitlines()
    old = [ln for ln in old if ln.strip()]
    have = {json.loads(ln)["arxiv_id"] for ln in old}
    added = [r for r in paper_rows if json.loads(r)["arxiv_id"] not in have]
    PAPERS.write_text("\n".join(old + added) + "\n", encoding="utf-8")

    # 复核
    lines2 = SEEN.read_text(encoding="utf-8").splitlines()
    for aid in RECOMMENDED:
        assert sum(1 for ln in lines2 if ("| %s |" % aid) in ln) == 1, aid
    n_seen = sum(1 for ln in lines2 if ln.startswith("|"))
    n_rec = sum(1 for ln in lines2 if ln.endswith("| 收录 |"))
    n_cand = sum(1 for ln in lines2 if ln.endswith("| 候选 |"))
    print("SEEN lines=%d data_rows=%d 收录=%d 候选=%d papers=%d (+%d)" % (
        len(lines2), n_seen, n_rec, n_cand,
        len([ln for ln in PAPERS.read_text(encoding="utf-8").splitlines() if ln.strip()]), len(added)))


if __name__ == "__main__":
    main()

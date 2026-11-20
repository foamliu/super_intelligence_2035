#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十三轮（本地 2026-10-26 06:00 AM「早 3」轮）结果落盘。

- **公告批次仍未刷新**：仍为 `2026-10-22`（`totalResults=637451` 与 r109~r112 逐条相同，
  最新样本 `published=2026-10-22T17:59:53Z`）⇒ `window_mode=weekend_batch`（120h），
  15/15 查询 200、`kept 0` / `dropped 600`（整批早已入 SEEN）。
- 早报 3 篇「借鉴」取自 **10-23 批候选池**（已入 SEEN、未进过任何日报），
  本轮 `id_list` 权威复核 3/3 返回（证据 raw/2026-10-26-am-idlist-r113a.{xml,headers}）。
- 台账：3 行「候选」→「收录」+ 追加 SUMMARY_LINE；`papers.jsonl` 251 → 254。
- 元数据（标题 / 作者 / 分类 / published / updated）一律取自官方 id_list XML，不手抄。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-26-am-fetch-r113-seen.json"
XML = BASE / "raw" / "2026-10-26-am-idlist-r113a.xml"

FIRST_SEEN = "2026-10-26"
RECOMMENDED = ["2610.31276", "2610.31646", "2610.31024"]

AREAS = {
    "2610.31276": ["agent harness", "code agent", "长程任务", "过程级信用分配", "自我恢复"],
    "2610.31646": ["SLM", "n-gram 记忆", "低比特量化", "推理显存", "预训练"],
    "2610.31024": ["EDA", "SPICE 仿真", "晶体管建模", "标准单元库", "存储/芯片视角"],
}

SUMMARY_ZH = {
    "2610.31276": (
        "长程编码智能体常见的失效模式是：它已经看到测试失败、也能说出一段看起来合理的反思，"
        "但接下来的动作仍沿着同一条错误轨迹继续 —— 作者把这种脱节称为 Critique-to-Action Handoff Gap。"
        "RIPPLE 是一个面向「恢复」的训练框架，目标是把过程级指导内化进单一策略：先用一个只看前缀"
        "（拿不到未来动作和最终结果）的教师，生成有证据支撑的恢复监督；轻量蒸馏后，用强化学习"
        "分别给「触发反思 / 诊断 / 纠正动作」三个阶段分配信用；再用局部有效性信号给轨迹优势做门控，"
        "避免中间恢复决策不加区分地继承终局成败。在四个仓库级软件工程基准上，RIPPLE 相对基础策略"
        "平均提升 4.8 分，部署时无需任何额外 critic。消融实验把局部信用与阶段对齐各自的贡献分开，"
        "匹配前缀的干预实验说明「反思说了什么」确实影响后续纠正；增益集中在「前缀里已有足够诊断证据、"
        "且剩余预算内仓库状态可回退」的情形。⚠️ 数字作者自报、本线未复现；未精读全文。"
    ),
    "2610.31646": (
        "近期不少开源权重模型用 n-gram embedding 表（存放二元 / 三元连续 token 的学习表示）"
        "来提升效果，但显存代价很高：例如 DeepSeek-V4.1-Flash 的 Engram n-gram 记忆就占 1960 亿参数。"
        "本文问：能否在不损失这份增益的前提下压缩表内存。做法是把 n-gram embedding 以低精度存储 —— "
        "为每张表学一个码本，每个分量存 b 比特索引 + 一个 16 比特 scale，并系统比较量化方法、"
        "码本构建、scale 拟合与两/三元表之间的比特分配。从零训练的 nanochat / Llama / GPT-2 系列上，"
        "4 比特表省下约 75% 表内存、同时保留超过 99% 的「加表带来的验证损失改善」；3 比特省 80%、"
        "保留约 97%；比特再低掉点更多，但短时间微调能补回相当一部分。把省下的内存用于扩大表规模，"
        "可以超过原全精度表的效果：4 倍 embedding、2 比特存储可达原改善的 122–126%，"
        "且表内存仍少 46–48%。在 DeepSeek-V4.1-Flash 与 Qwen3.8-Flash-Next 上省 47–55% 表内存，"
        "困惑度上升不到 1.2%，下游任务大体保持。⚠️ 数字作者自报、本线未复现；未精读全文。"
    ),
    "2610.31024": (
        "用神经网络替代紧凑晶体管模型（compact model）来加速电路仿真已有不少尝试，但很少在"
        "真实 EDA 工具流的复杂任务里被严格检验 —— 标准单元库表征恰恰要求极高精度才能收敛。"
        "作者为 3nm nanosheet 器件训练 NN 模型，预测漏极电流与各类电荷，并把它接进标准单元库表征："
        "该流程包含数千次 SPICE 仿真，是检验模型质量与一致性的好基准；此外还在多种模拟/数字电路上"
        "做电路级验证，并与工业标准 BSIM-CMG（Verilog-A）对比。结果显示 NN 模型是现有紧凑模型的"
        "可行替代：在大量电路上延迟误差低于 0.11%、总功耗误差 0.76%，标准单元库表征耗时最多缩短 8 倍"
        "（NN16 约比 BSIM-CMG 快 8×）；论文还给出 NN 规模与仿真精度关系的系统性指导。"
        "⚠️ 针对 3nm nanosheet / 特定工艺训练；数字作者自报、本线未复现；未精读全文。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十三轮（本地 2026-10-26 06:00（CST）· P0 第 4 批第 11 轮「早 3」轮 · 新一日 AM）**："
    "**公告批次仍未刷新** —— 仍为 `2026-10-22`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=637451`（与 r109~r112 逐条相同）、最新样本 `published=2026-10-22T17:59:53Z`；"
    "**周一 06:00 CST = 周日 22:00 UTC，arXiv 尚未公告**）；"
    "`window_mode=weekend_batch`（120h）⇒ **15/15 查询 `200`**、"
    "**`kept 0` / `dropped 600`**（`generated=2026-10-25T22:01:25Z`；600 = `already in SEEN` 558 + `stale > 120h` 42；"
    "`sweep-cs-5cats` 首次请求网络失败 → `attempts=2` 后成功，其余 14 条 `attempts=1`）。"
    "早报 3 篇「借鉴」取自 10-23 批候选池 + **`id_list` 权威复核 3/3 返回**"
    "（证据 `raw/2026-10-26-am-idlist-r113a.{xml,headers}`）：`2610.31276` RIPPLE、"
    "`2610.31646` Low-Bit N-Gram Embeddings、`2610.31024` NN-Based Transistor Modeling。"
    "台账 3 行「候选」→「收录」→ **收录 254 / 候选 3,852 / 候选（RSS 补充）507**；"
    "`papers.jsonl` **251 → 254**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r113.py`。口径见 `ARXIV_API.md` §9.113。"
)

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def load_official():
    root = ET.parse(str(XML)).getroot()
    out = {}
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", NS).text.split()),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "published": e.find("a:published", NS).text,
            "updated": e.find("a:updated", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
        }
    assert len(out) == 3, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith("2026-10-2"), out[k]["published"]
    return out


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert sum(q["attempts"] for q in meta["per_query"]) == 16, "unexpected retry count"
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert payload["items"] == [], payload["items"]

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for aid in RECOMMENDED:
            if re.match(r"^\| \d{4}-\d\d-\d\d \| %s \| .* \| 候选 \|$" % re.escape(aid), ln):
                lines[i] = ln[: -len("候选 |")] + "收录 |"
                flipped += 1
    assert flipped == 3, flipped

    add_at = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("| 2026-"):
            add_at = i + 1
            break
    assert add_at is not None, "no ledger rows found"
    assert not any(SUMMARY_LINE[:40] in ln for ln in lines), "summary already present"
    lines.insert(add_at, SUMMARY_LINE)
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
        m = re.match(r"^\| [0-9-]{10} \| [0-9.]+ \| .* \| (收录|候选|候选（RSS 补充）) \|$", ln)
        if m:
            st[m.group(1)] = st.get(m.group(1), 0) + 1
    print("SEEN flipped:", flipped)
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


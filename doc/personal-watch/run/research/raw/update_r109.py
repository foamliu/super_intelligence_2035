#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零九轮（本地 2026-10-24 06:00 AM「早 3」轮 · 新一日）结果落盘。

- **公告批次未刷新**：仍为 `2026-10-22`（totalResults 637451 == 上一轮 r108 PM；
  最新样本 published=2026-10-22T17:59:53Z）；`--fetch --seen`（window_mode=daily 72h，
  generated=2026-10-23T22:08:15Z）15/15 ok（全部 attempts=1）、**kept 0 / dropped 600**。
- 早报 3 篇「借鉴」取自上一轮 PM 已入账的 158 条候选池（上轮 id_list 复核过但未入账的 3 篇）：
  2610.30042 HGM-Dual / 2610.30132 LongZero / 2610.29013 Target Regeneration
  -> SEEN **行数不变**（3 行「候选」→「收录」）+ 追加 r109 摘要行；papers.jsonl 241 -> 244。
- 元数据取自 id_list 权威复核 raw/2026-10-24-idlist-r109{,b}.xml（官方 published/作者/摘要）。
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-24-fetch-r109-seen.json"
XMLS = [BASE / "raw" / "2026-10-24-idlist-r109.xml", BASE / "raw" / "2026-10-24-idlist-r109b.xml"]

FIRST_SEEN = "2026-10-24"
RECOMMENDED = ["2610.30042", "2610.30132", "2610.29013"]


SUMMARY_ZH = {
    "2610.30042": (
        "agent harness 优化（改 prompt / 工具 / 工作流）是在冻结或闭源 LLM 之上提升 agent 的常用手段；"
        "现有 Darwin–Gödel Machine / HGM 一类方法靠递归自改，主要面向代码任务 —— 改 harness 所需的能力"
        "与要被提升的能力恰好重合。规划任务要产出「联合满足相互约束」的一串工具调用，这种重合被打破，"
        "开放式自改会反复做无效修改、烧掉大量评测预算。作者提出 HGM-Dual：① 把 agent 演化写成"
        "「谱系感知上下文」，记录每个祖先改了什么、哪些行为变好或变差、哪些修改无效，让编辑器能做"
        "编辑—结果归因，而不是面对一堆无结构的历史 agent 归档；② 错误条件化的双路子代生成 —— 每个选中父代"
        "既生成保留开放探索的通用子代，也生成针对「父代排名最高的约束违反」所对应 harness 组件的专用子代。"
        "结果：相对最强基线 case accuracy 最多 **+14.45%**（相对提升），并以 **2×–4× 更少**的评测预算"
        "达到 HGM 变体的最终性能。"
        "⚠️ 摘要未给基准名与所用模型；「规划任务」的具体形态需看原文；数字作者自报、本线未复现；未精读。"
    ),
    "2610.30132": (
        "用强化学习强化 LLM 的长上下文推理，需要「长、多样、有挑战、可验证」的训练数据：人工标注贵，"
        "自然语料不足以支撑 RL，已有合成方法又依赖外部语料或更强的教师模型（模型越强越难找）。"
        "已有「零数据 RL」（模型自学自出的任务）只在短上下文任务上奏效。LongZero 把它推到长上下文："
        "不直接在已有文档上写问答，而是先让模型以紧凑结构化形式自写「问题 + 答案 + 支撑证据」，"
        "再把证据单独展开成长篇多文档上下文；把这种自写多跳推理任务与自写多轮检索任务结合，用 **GRPO** 训练。"
        "在两个 LLM、五个长上下文推理基准上，LongZero 能泛化到真实任务，且优于「外部语料合成数据做 RL」的基线。"
        "⚠️ 上限取决于模型自生成任务与自验证的质量；具体模型规模 / 训练算力摘要未给；"
        "数字作者自报、本线未复现；未精读。"
    ),
    "2610.29013": (
        "投机解码靠并行验证 draft token 来加速 LLM；新的 draft 训练目标通常以「相对外部撰写回答上的交叉熵」"
        "所增加的接受率为功劳，但很多流水线会让 target 模型重写这些回答。作者用视觉语言 target + block drafter，"
        "在同一语料的四个版本上训练三种目标：语料 token 上的交叉熵、来自 target 的 token 级蒸馏、"
        "以及只在「能通过验证的位置」上做门控的蒸馏；比较在**外部回答**与**target 贪心重生成之后**的增益。"
        "结果：蒸馏与门控在外部回答上增益很大，重生成后蒸馏只剩较小增益、门控几乎没有；这种收缩在数据顺序、"
        "位置权重、验证器、解码温度，以及蒸馏的初始化与学习率下都成立，在匹配监督长度、各目标最佳训练长度下也仍在；"
        "第二个视觉语料与纯文本复现同样观察到。作者的结论是评测口径问题：目标收益应在"
        "**target 重生成的基线**上、并跨训练长度测量。"
        "⚠️ 以 block drafter + 视觉语言 target 为主（纯文本为复现）；加速比等绝对值不在摘要内；"
        "数字作者自报、本线未复现；未精读。"
    ),
}

AREAS = {
    "2610.30042": ["agent harness", "harness 优化", "长程规划", "评测预算", "ZhuLong"],
    "2610.30132": ["长上下文", "强化学习", "零数据", "合成数据", "GRPO", "BaiZe"],
    "2610.29013": ["投机解码", "推理加速", "蒸馏", "评测口径", "BaiZe"],
}


SUMMARY_LINE = (
    "> **第一百零九轮（本地 2026-10-24 06:00（CST）· P0 第 5 批第 7 轮「早 3」轮 · 新一日 AM 轮）**："
    "**公告批次未刷新** —— 仍为 `2026-10-22`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=637451`（与 r108 PM 相同）、最新样本 `published=2026-10-22T17:59:53Z`（`2610.31671`，cs.CV）；"
    "周五 20:00 ET 批未索引 / 周末不公告）；**15/15 查询 `ok`**（**全部 `attempts=1`**）、"
    "**`kept 0` / `dropped 600`**（`window_mode=daily` 72h，`generated=2026-10-23T22:08:15Z`；"
    "600 = 15 × 40，剔除原因均为 `already in SEEN` 或 `stale > 72h`）。"
    "R1′ arXiv ✅（DNS 边缘 `146.75.115.42` 不可达 → 运行期覆盖到 `151.101.67.42`，见 `raw/run_arxiv_r109.py`）/ "
    "HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 183 · cs.CV 192 · cs.LG 超时（仅作发现）。"
    "**早报 3 篇「借鉴」取自上一轮 PM 已入账的 158 条候选池**（上轮复核通过但未入账）+ **单条权威复核**"
    "（两批 `id_list` 6 + 7 → **全部返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；"
    "证据 `raw/2026-10-24-idlist-r109{,b}.{xml,headers}`）："
    "`2610.30042` HGM-Dual: Lineage-Aware Guided Agent Harness Optimization for Long-Horizon Planning / "
    "`2610.30132` LongZero: Enhancing Long-Context Reasoning in LLMs from Zero Data / "
    "`2610.29013` Target Regeneration Shrinks the Gains of Draft-Training Objectives in Speculative Decoding。"
    "台账 **4,612 行不变**（3 行「候选」→「收录」）→ 累计（**收录 244 / 候选 3,861 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **241 → 244**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r109.py`。口径见 `ARXIV_API.md` §9.109。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    official = {}
    for p in XMLS:
        root = ET.parse(p).getroot()
        for e in root.findall("a:entry", ns):
            aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
            cat = e.find("x:primary_category", ns)
            com = e.find("x:comment", ns)
            official[aid] = {
                "arxiv_id": aid,
                "title": " ".join(e.find("a:title", ns).text.split()),
                "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
                "published": e.find("a:published", ns).text,
                "updated": e.find("a:updated", ns).text,
                "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
                "comment": com.text if com is not None else "",
                "summary": " ".join(e.find("a:summary", ns).text.split()),
            }
    # 两批 6 + 7 = 13 条请求，其中 2610.30042 / 2610.29426 在批间重复 => 11 条唯一
    assert len(official) == 11, "expected 11 distinct entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-21"), official[k]["published"]
    return official


def main():
    official = load_official()
    meta = json.load(FETCH.open(encoding="utf-8"))["meta"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert all(q["ok"] and q["attempts"] == 1 for q in meta["per_query"]), "query not clean"

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for aid in RECOMMENDED:
            if re.match(r"^\| \d{4}-\d\d-\d\d \| %s \| .* \| 候选 \|$" % re.escape(aid), ln):
                lines[i] = ln[: -len("| 候选 |")] + "| 收录 |"
                flipped += 1
    assert flipped == 3, flipped

    add_at = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("| 2026-"):
            add_at = i + 1
            break
    assert add_at is not None
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
        m = re.match(r"^\| [0-9-]{10} \| [0-9.]+ \| .* \| ([^ |]+) \| (收录|候选) \|$", ln)
        if m:
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN flipped:", flipped)
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


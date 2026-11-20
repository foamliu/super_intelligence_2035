#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十一轮（本地 2026-10-25 06:00 AM「早 3」轮）结果落盘。

- **公告批次未刷新**：仍为 `2026-10-22`（`totalResults=637451` 与 r109/r110 逐条相同；
  最新样本 published=2026-10-22T17:59:53Z）。本轮为**周日**，arXiv 周末不公告；
  `window_mode` 自动为 `weekend_batch`（120h）⇒ 15/15 查询 200、`kept 0` / `dropped 600`。
- 早报 3 篇「借鉴」取自 **r108 PM 的候选池**（10-23 已入 SEEN 但未入账），本轮
  `id_list` 权威复核 8/8 返回（证据 raw/2026-10-25-idlist-r111a.{xml,headers}）。
- 台账：3 行「候选」→「收录」+ 追加 SUMMARY_LINE；`papers.jsonl` 246 → 249。
- 元数据（标题 / 作者 / 分类 / published / comment）一律取自官方 id_list XML，不手抄。
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-25-fetch-r111-seen.json"
XMLS = [BASE / "raw" / "2026-10-25-idlist-r111a.xml"]

FIRST_SEEN = "2026-10-25"
RECOMMENDED = ["2610.31098", "2610.30231", "2610.28815"]

AREAS = {
    "2610.31098": ["投机解码", "KV cache 压缩", "长上下文", "推理加速", "draft 训练"],
    "2610.30231": ["视觉语言模型", "on-policy 蒸馏", "小模型", "多模态推理", "强化学习"],
    "2610.28815": ["agent harness", "自我演化", "证据选择", "评测预算", "agent"],
}

SUMMARY_ZH = {
    "2610.31098": (
        "投机解码是长输出生成的常用加速手段，但长输出意味着 KV cache 越来越大；"
        "面向 prefill 信息的 KV 压缩方法会随输出变长而失去相关性（作者称之为 decode staleness），"
        "从而拉低 draft 模型准确率。RIFT 提出一族「基于选择」的 KV cache 压缩策略，在 prefill 信息与"
        "最近生成 token 之间做平衡，并在生成过程中刷新 KV 选择；为压低刷新带来的解码延迟，"
        "再提出自适应刷新策略以减少打分次数、同时保住 draft 质量。作者还用基于稀疏注意力掩码的"
        "「可压缩性驱动」draft 训练阶段，提升 draft 在压缩缓存下的质量。与可压缩性训练结合后，"
        "Qwen3.5-4B 为 Qwen3.5-122B 做 draft，在 32K 输入 / 4K 输出、8K KV 预算下保留超过 98% 的"
        "满缓存接受长度。⚠️ 数字作者自报、本线未复现；未精读。"
    ),
    "2610.30231": (
        "视觉数学推理可能「推理还没开始就错了」：VLM 读错图，后续推理便建立在假前提上。"
        "这个感知瓶颈在小模型上尤其明显，而准确的文字描述能显著缩小与大模型的差距 —— 给 2B VLM 一份"
        "忠实图注，Geometry3K pass@1 从 0.32 升到 0.46，接近约 4 倍大的 8B 的 0.49；"
        "但推理时要拿到这些描述，需额外标注或模型调用。作者提出最小编辑式纠错 on-policy 蒸馏："
        "只把「参考图注 + 已验证参考解」当训练时信息，让 teacher 以最小编辑目标给学生的错误 rollout 打分，"
        "只有 teacher 不认可的 token 进入纠错损失；正确 rollout 则用任务奖励做 RL。这样保留 on-policy 监督、"
        "避免整段模仿。方法在测试时不需要图注，在各模型规模上达到或超过「推理时给基线模型参考图注」；"
        "也提升面向感知（尤其低层几何感知）的表现并可迁移到外部数学与感知基准；用冻结的同尺寸 teacher 仍有效，"
        "但多数指标上增益小于大 teacher。⚠️ 数字作者自报、本线未复现；未精读。"
    ),
    "2610.28815": (
        "agentic harness 演化用任务执行经验去优化 agent 的指令、工具与控制流；直觉上演化任务越多越好，"
        "但作者的前期研究发现一个悖论式失效：任务池扩大时现有方法的性能反而下降。进一步分析表明，"
        "退化来自优化过程中的证据选择不佳 —— 不同证据组合会导致差别很大的演化结果。作者提出 "
        "Successive Scale Racing（SSR）：每轮按任务质量与覆盖度构造多样化的证据组合，并在小算力预算下"
        "对候选 harness 做竞速筛选。在 3 个不同基准、6 种配置上均取得 SOTA；任务池从 40 增到 200 时，"
        "SSR 的通过率从 64.3% 稳定升到 68.3%，而基线全部下降；竞速机制在识别近最优候选的同时，"
        "把验证执行减少 60%。⚠️ 摘要未给基准名、harness 表示形式与所用 LLM；数字作者自报、本线未复现；未精读。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十一轮（本地 2026-10-25 06:00（CST）· P0 第 4 批「早 3」轮 · 新一日 AM）**："
    "**公告批次未刷新** —— 仍为 `2026-10-22`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=637451`（与 r109/r110 逐条相同）、最新样本 `published=2026-10-22T17:59:53Z`；**周日无公告**）；"
    "`window_mode=weekend_batch`（120h）⇒ **15/15 查询 `200`、全部 `attempts=1`**、"
    "**`kept 0` / `dropped 600`**（`generated=2026-10-24T22:00:45Z`；600 = `already in SEEN` 558 + `stale > 120h` 42）。"
    "早报 3 篇「借鉴」取自 r108 PM 候选池 + **`id_list` 权威复核 8/8 返回**"
    "（证据 `raw/2026-10-25-idlist-r111a.{xml,headers}`）：`2610.31098` RIFT、`2610.30231` Edit, Don't Imitate、"
    "`2610.28815` SSR。台账 3 行「候选」→「收录」→ **收录 249 / 候选 3,857 / 候选（RSS 补充）507**；"
    "`papers.jsonl` **246 → 249**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r111.py`。口径见 `ARXIV_API.md` §9.111。"
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
    assert len(official) == 8, "expected 8 distinct entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-2"), official[k]["published"]
    return official


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "attempts != 1"
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

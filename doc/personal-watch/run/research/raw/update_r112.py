#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十二轮（本地 2026-10-25 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次未刷新**：仍为 `2026-10-22`（`totalResults=637451` 与 r109/r110/r111 逐条相同；
  最新样本 `published=2026-10-22T17:59:xxZ`）。本轮为**周日**，arXiv 周末不公告；
  `window_mode` 自动为 `weekend_batch`（120h）⇒ 15/15 查询 200、`kept 0` / `dropped 600`。
- 晚报 2 篇「科普」取自 **r111 AM 附录 C「复核通过但未入账」候选**（10-23 已入 SEEN），
  本轮 `id_list` 权威复核 2/2 返回（证据 raw/2026-10-25-pm-idlist-r112a.{xml,headers}）。
- 台账：2 行「候选」→「收录」+ 追加 SUMMARY_LINE；`papers.jsonl` 249 → 251。
- 元数据（标题 / 作者 / 分类 / published / updated）一律取自官方 id_list XML，不手抄。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-25-pm-fetch-r112-seen.json"
XML = BASE / "raw" / "2026-10-25-pm-idlist-r112a.xml"

FIRST_SEEN = "2026-10-25"
RECOMMENDED = ["2610.30499", "2610.31633"]

AREAS = {
    "2610.30499": ["agent harness", "自我改进", "ARC-AGI-3", "评测协议", "agent"],
    "2610.31633": ["looped 架构", "KV cache 共享", "推理显存", "长上下文", "高效推理"],
}

SUMMARY_ZH = {
    "2610.30499": (
        "一个足够通用的智能体应当能高效获得新技能，而不需要人类为每个新任务重写它的软件脚手架；"
        "harness 就是这样一个「符号程序」，替模型处理感知、记忆、工具调用、失败恢复与推理预算分配。"
        "ARC-AGI-3 是交互式基准：智能体要在陌生环境里自行探索、边玩边搞清目标并持续学习。"
        "作者问：前沿模型能不能自己造出、并持续改进这样的 harness？做法是固定一套编码引导流程，"
        "让每个模型从受控的最小仓库出发，造出完整 harness，在 5 个开发游戏上行动，并把整个代码库改写两轮；"
        "每一版都在 20 个从不参与改写的留出游戏上评测。指标 RHAE（相对人类行动效率）结合关卡完成度与"
        "相对人类基线的行动效率，同时记录美元计价的推理成本。9 种「模型 × 推理强度」条件、27 条独立 lineage、"
        "81 个冻结快照、2,025 次游戏评测：harness 表现从 0 到接近满分；但两轮改写只把平均留出 RHAE 抬高 "
        "2.80 分（95% 区间 [-1.44, 7.35]），而开发集上平均涨了 8.42 分（适应差 5.62 分，区间 [1.78, 9.77]）。"
        "同一 harness 重复评测 10 次的样本标准差就有 3.99 分，所以几分的变化要谨慎解读。成本侧：27 条里 9 条"
        "「更好且更便宜」，6 条「更好但更贵」，9 条「更便宜但更差」，3 条双输；平均每局省 $2.72，中位数只省 $0.54。"
        "⚠️ 数字作者自报、本线未复现；未精读。"
    ),
    "2610.31633": (
        "looped（循环）架构把同一组层反复过几遍，在不增加参数的情况下提升质量；但推理时每一遍都会生成"
        "独立的 KV cache，显存随循环次数线性增长。已有工作发现：某些情况下最后一遍的 KV 可以共享给前面几遍"
        "而不掉质量（作者称之为 KV-shareability），但机制不清楚 —— 即使同配方训练的模型也不是都具备"
        "（如 Parcae 1.3B 共享后困惑度 0.601 → 2.281）。本文提出两阶段做法：① 预训练时用 stochastic depth，"
        "诱导收缩型残差动力学，让各遍表示收敛到同一不动点；② 后训练 BeNice! 把最后一遍的 KV 广播给第一遍，"
        "训练第一遍产生兼容的残差，同时保住原模型质量。结果：共享时相对标准微调把验证困惑度改善 9.75 分，"
        "不共享时质量持平；Core / Core-extended 的共享质量分别最多 +8.35 / +4.56 分；可与 MLA、Kimi delta "
        "attention 等省显存序列混合器以及 fp8 / mxfp4 / nvfp4 低精度 KV 量化叠加。在模拟低显存长上下文推理里，"
        "缓存命中率最多 +31.4%（+8.1 个百分点）、吞吐 +23.6%、p90 首字延迟最多 −83.6%。"
        "⚠️ 评测基于 Parcae / Huginn / Ouro 等公开 looped 模型与模拟服务负载；数字作者自报、本线未复现；未精读。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十二轮（本地 2026-10-25 18:00（CST）· P0 第 4 批「晚 2」轮 · 当日 5/5 收口）**："
    "**公告批次未刷新** —— 仍为 `2026-10-22`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=637451`（与 r109/r110/r111 逐条相同）、最新样本 `published=2026-10-22T17:59:48Z`；**周日无公告**）；"
    "`window_mode=weekend_batch`（120h）⇒ **15/15 查询 `200`、全部 `attempts=1`**、"
    "**`kept 0` / `dropped 600`**（`generated=2026-10-25T10:01:55Z`；600 = `already in SEEN` 558 + `stale > 120h` 42）。"
    "晚报 2 篇「科普」取自 r111 AM 附录 C「复核通过但未入账」候选 + **`id_list` 权威复核 2/2 返回**"
    "（证据 `raw/2026-10-25-pm-idlist-r112a.{xml,headers}`）：`2610.30499` Can LLMs Improve Their Own Harness?、"
    "`2610.31633` BeNice!。台账 2 行「候选」→「收录」→ **收录 251 / 候选 3,855 / 候选（RSS 补充）507**；"
    "`papers.jsonl` **249 → 251**；PDF 5/5 落地校验通过（全日）；落盘脚本 `raw/update_r112.py`。口径见 `ARXIV_API.md` §9.112。"
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
    assert len(out) == 2, out.keys()
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
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "attempts != 1"
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert payload["items"] == [], payload["items"]

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for aid in RECOMMENDED:
            if re.match(r"^\| \d{4}-\d\d-\d\d \| %s \| .* \| 候选 \|$" % re.escape(aid), ln):
                lines[i] = ln[: -len("候选 |")] + "收录 |"
                flipped += 1
    assert flipped == 2, flipped

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

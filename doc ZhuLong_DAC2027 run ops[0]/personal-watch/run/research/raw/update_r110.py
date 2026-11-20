#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十轮（本地 2026-10-24 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次未刷新**：仍为 `2026-10-22`（totalResults 637451 == r109 AM；最新样本
  published=2026-10-22T17:59:53Z）。因本轮为周六，`window_mode=auto` 自动切到
  **`weekend_batch`（120h）** ⇒ `kept 1`（2610.30181 cs.IR，published 2026-10-19T18:59:21Z，
  111h 前；其余 599 条 = 557 already in SEEN + 42 stale > 120h）。
- 晚报 2 篇「科普」**取自上一轮 PM 的 158 条候选池**（10-23 PM 已 id_list 复核但未入账）：
  2610.31579 Who Is Sycophantic to Whom?（本日 TOP-1）/ 2610.30740 Where Did the Light Come From?
  -> SEEN 追加 1 行「候选」（新 kept）+ 2 行「候选」→「收录」；papers.jsonl 244 -> 246。
- 元数据取自本轮 id_list 权威复核 raw/2026-10-24-pm-idlist-r110a.xml（官方 published/作者/摘要）。
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-24-pm-fetch-r110.json"
XMLS = [BASE / "raw" / "2026-10-24-pm-idlist-r110a.xml"]

FIRST_SEEN = "2026-10-24"
RECOMMENDED = ["2610.31579", "2610.30740"]
NEW_CANDIDATE = "2610.30181"

NEW_CANDIDATE_TITLE = "Deep Search in Real-World Web Environments"
NEW_CANDIDATE_CAT = "cs.IR"

AREAS = {
    "2610.31579": ["谄媚", "人机信任", "信心校准", "用户研究", "评测口径"],
    "2610.30740": ["视觉语言模型", "影子/光照理解", "物理一致性", "评测基准", "生成模型先验"],
}

SUMMARY_ZH = {
    "2610.31579": (
        "谄媚（sycophancy）研究问的是 LLM 会不会顺着用户想听的说；本文反过来问：当 LLM 自信、"
        "前后一致、却是错的时候，用户会不会顺着它弯？在一个被试内实验中，32 名参与者通过与 5 个助手"
        "（同一个 GPT-5-mini）聊天来学习最多 5 个科学主题；每个助手的讲解里分别有 0 / 25 / 50 / 75 / 100% "
        "的事实被替换成「看起来合理的假话」，且所有助手都以十足把握的语气说话。每个主题后有一次突袭测验，"
        "选项是正确事实、植入的假话和两个干扰项，每个答案还要打信心分。104 次测验、1,040 个答案："
        "得分从 7.4 掉到 2.9（满分 10）；在被篡改的条目上 60% 选了植入的假话（未被篡改条目只有 11%，"
        "odds ratio 12.5）。对话逐轮编码显示：助手每说出一次假话，约 65% 被吸收，且在 5 档篡改比例下都一样；"
        "被吸收的假话被以高信心持有（8.4/10），「答对更自信」的优势消失，用信心区分对错的 AUROC 从 0.70 "
        "掉到随机水平；而任务后的信任评分几乎没有变化。参与者越觉得助手差、越会回来继续聊，但回来带来的是"
        "更多吸收而不是更少；30% 的对话轮次是把测验题粘贴回被检验的助手。助手本身几乎从不谄媚、"
        "被反驳时从不退让。作者提出经基线校正的 Human Deference Index 来量化这种「人类侧的谄媚」，"
        "并主张可信度是人-AI 配对的属性、谄媚评测应双向测量、学习界面应逐条声明可靠性。"
        "⚠️ 样本仅 32 人、单一模型（GPT-5-mini）与单一主题域；数字作者自报、本线未复现；未精读。"
    ),
    "2610.30740": (
        "影子是「光照—物体几何—场景结构」交互的可观测结果；真正理解影子的模型不仅要能读出影子的方向，"
        "还要能在影子缺失时推断它该落在哪，并能判断影子与场景是否物理自洽。作者构建 ShadowBench"
        "（来自真实照片）：每个场景给出「正确影子 / 去掉影子 / 人工标注的错误方向」三种状态，对应上述三个问题。"
        "评测 19 个开源 VLM（2B–78B）与前沿闭源模型：VLM 读可见影子的方向明显高于随机并随规模改善，"
        "但推断「缺失时该朝哪」只有很弱的水平，判断物理自洽则落到随机水平 —— 即使换成去掉 yes 偏差的"
        "二选一测试也是如此。只有 Gemini-3.1-pro 在「有效性」判断上高于随机，幅度不大、且远低于人类。"
        "Chain-of-Thought 没有帮助。作者认为缺的不是推理能力，而是图像生成模型（IGM）已经具备的知识："
        "把 VLM 路由经过一个 IGM，能把它对缺失影子方向的推断明显抬到其直接作答之上，并帮助它标出"
        "原本会接受的错误方向影子。投影方向只是光照理解的一个侧面，但 VLM 与 IGM 之间这道明显差距提示："
        "图像生成 / 重建目标可能是通向「光照感知 VLM」的一条路径。"
        "⚠️ 摘要未给各模型逐项准确率与人工基线数值；IGM 路由的实现与推理成本未述；数字作者自报、本线未复现；未精读。"
    ),
}


SUMMARY_LINE = (
    "> **第一百一十轮（本地 2026-10-24 18:00（CST）· P0 第 5 批第 8 轮「晚 2」轮 · 当日收口）**："
    "**公告批次未刷新** —— 仍为 `2026-10-22`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=637451`（与 r109 AM 相同）、最新样本 `published=2026-10-22T17:59:53Z`；周六无公告）；"
    "`window_mode=auto` 因周六自动切到 **`weekend_batch`（120h）** ⇒ **15/15 查询 `200`**"
    "（14 条 `attempts=1`；`slm-small-language-model` `attempts=2`：首次 `ConnectTimeout`、backoff 20s 后成功，如实记录）、"
    "**`kept 1` / `dropped 599`**（`generated=2026-10-24T10:01:12Z`；599 = `already in SEEN` 557 + `stale > 120h` 42）。"
    "**晚报 2 篇「科普」取自上一轮 PM 的 158 条候选池** + **单条权威复核**（`id_list` 2/2 返回，均 `HTTP 200` + "
    "`application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-24-pm-idlist-r110a.{xml,headers}`）："
    "`2610.31579` Who Is Sycophantic to Whom? Confident LLMs, Human Deference, and the Collapse of Trust Calibration"
    "（**本日 TOP-1**）/ `2610.30740` Where Did the Light Come From? Diagnosing Cast-Shadow Reasoning in VLMs "
    "and Borrowing the Missing Shadow Prior from Image Generation Models。"
    "台账 **4,612 → 4,613 行（+1 新候选）**（另有 2 行「候选」→「收录」）→ 累计（**收录 246 / 候选 3,860 / "
    "候选（RSS 补充）507**）；`papers.jsonl` **244 → 246**；PDF 2/2 落地校验通过；落盘脚本 `raw/update_r110.py`。"
    "口径见 `ARXIV_API.md` §9.110。"
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
    assert len(official) == 2, "expected 2 distinct entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-22"), official[k]["published"]
    return official


def main():
    official = load_official()
    meta = json.load(FETCH.open(encoding="utf-8"))["meta"]
    assert meta["n_kept"] == 1, meta["n_kept"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert sum(1 for q in meta["per_query"] if q["attempts"] == 1) == 14, "attempts != 14x1"
    assert [i["arxiv_id"] for i in json.load(FETCH.open(encoding="utf-8"))["items"]] == [NEW_CANDIDATE]

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for aid in RECOMMENDED:
            if re.match(r"^\| \d{4}-\d\d-\d\d \| %s \| .* \| 候选 \|$" % re.escape(aid), ln):
                lines[i] = ln[: -len("候选 |")] + "收录 |"
                flipped += 1
    assert flipped == 2, flipped

    # 新候选（本轮 kept 1）插在最后一条台账行之后、摘要区之前
    add_at = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("| 2026-"):
            add_at = i + 1
            break
    assert add_at is not None, "no ledger rows found"
    assert not any(NEW_CANDIDATE in ln for ln in lines), "candidate already in SEEN"
    new_row = "| %s | %s | %s | %s | 候选 |" % (
        FIRST_SEEN, NEW_CANDIDATE, NEW_CANDIDATE_TITLE, NEW_CANDIDATE_CAT)
    lines.insert(add_at, new_row)
    lines.insert(add_at + 1, SUMMARY_LINE)
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
    print("SEEN flipped:", flipped, "| added:", new_row)
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


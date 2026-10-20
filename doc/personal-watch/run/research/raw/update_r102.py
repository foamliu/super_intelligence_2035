#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零二轮（本地 2026-10-20 18:00 P0「晚 2」轮 · PM）结果落盘。

- PM 轮**公告批次再次刷新**：2026-10-16 -> 2026-10-19（最新样本 published=2026-10-19T17:59:59Z）
  - `--fetch`（window_mode=daily 72h）15/15 ok（均 attempts=1）、kept 219 / dropped 347
  -> SEEN.md 追加 219 行（首次收录 = 2026-10-20），其中 2 行为「收录」、217 行为「候选」
  -> 台账 3,886 -> 4,105 行；累计 收录 224 -> 226 / 候选 3,155 -> 3,372 / 候选（RSS 补充）507
- 2 篇推荐（均「科普」）：2610.26781 Game of Phones / 2610.26851 Manga2Animate
  -> papers.jsonl 追加 2 行（224 -> 226）
- 元数据取自 id_list 权威复核 raw/2026-10-20-idlist-r102.xml（官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-20-fetch-r102-seen.json"

FIRST_SEEN = "2026-10-20"
RECOMMENDED = ["2610.26781", "2610.26851"]


SUMMARY_ZH = {
    "2610.26781": (
        "电话诈骗给个人与金融系统带来越来越大的损失，但**现有反制手段不给诈骗者造成任何资源成本**。"
        "**策略性「反诈陪聊」（scam-baiting）**——让自动 agent 与诈骗者周旋、消耗其运营能力——是一种主动替代方案，"
        "但需要**动态策略适应**，静态系统做不到。作者提出一个**博弈论框架**，让 LLM **无需微调、仅靠上下文经验**学会有效反制策略："
        "把诈骗者—陪聊者的交互建模为**两人博弈**，策略与效用函数**有实证依据**，并以**纳什均衡**作为评估学习行为的正式基准。"
        "在 **300 段模拟对话**、**3 种 LLM 架构**上，自适应策略选择比非自适应基线**更接近纳什均衡 28.9–79.7%**。"
        "作者同时开源代码与 **300 段带轮级策略标注与效用分数的对话数据集**。"
        "⚠️ 数字为作者自报、本线未复现；摘要未给真实电话系统部署或真人对话实验。"
    ),
    "2610.26851": (
        "把已有漫画改编成**连贯且忠实于原作**的动画既有价值又困难：现有方法要么主要通过**文本**理解漫画（丢失角色与画风），"
        "要么把漫画页**直接喂给视频生成模型**（模型误读漫画结构、生成错误剧情线）。"
        "作者提出 **Manga2Animate**，一个**多智能体框架**，把生成的每个阶段都**锚定在源漫画**上：把任务分解为两个中间表示——"
        "**动画剧本（animation script）**与**视觉分镜（visual storyboard）**；每个表示由一个 **creator agent** 生成、"
        "由一个配对的 **reviewer agent** 对照原漫画分镜审校；再用**表示特定的选择机制**与**双层反馈**逐步精修两者，最后合成动画。"
        "大量实验与**用户研究**表明，Manga2Animate 生成的动画比当前最优方法**更忠实于原作、镜头间更一致**。"
        "⚠️ 摘要只给定性结论、未给具体指标数值；作者自报，本线未复现；未做全文精读。"
    ),
}

AREAS = {
    "2610.26781": ["反诈", "scam-baiting", "博弈论", "纳什均衡", "LLM agent", "安全"],
    "2610.26851": ["漫画动画化", "多智能体", "剧本", "分镜", "视频生成", "创作工具"],
}

SUMMARY_LINE = (
    "> **第一百零二轮（本地 2026-10-20 18:00（CST）· P0 第 4 批第 25 轮「晚 2」轮 · 当日收口）**："
    "**公告批次再次刷新** —— `2026-10-16` → **`2026-10-19`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=634451 → 635673`，最新样本 `published=2026-10-19T17:59:59Z`；距 AM 轮 12h，周一 20:00 ET 公告已落地）；"
    "**15/15 查询 `ok`**（**均 `attempts=1`、`retries=[]`**），**`kept 219` / `dropped 347`**"
    "（`window_mode=daily` 72h，`generated=2026-10-20T10:02:54Z`）→ **219 条全部为新发现**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL·CV·LG = **0 / 0 / 0**（`status=None`，如实记未取到）。"
    "**晚报 2 篇「科普」取自本 PM 轮新批 219 条** + **单条权威复核**（`id_list=2610.26781,2610.26851,2610.26861,2610.25026,2610.26538` → **5/5 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-20-idlist-r102.{xml,headers}`）："
    "`2610.26781` Game of Phones: Harnessing Game Theory and LLMs in 'Bot Wars' to Counteract Phone Scams（**本日 TOP-1**）/ "
    "`2610.26851` Manga2Animate: An Agentic Framework for Faithful Manga Animation with Script and Storyboard Planning。"
    "台账 **3,886 → 4,105 行（+219）**（2 行「收录」+ 217 行「候选」）→ 累计（**收录 226 / 候选 3,372 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **224 → 226**；证据 `raw/2026-10-20-{probe-r102.log,fetch-r102.log,fetch-r102-seen.json}` + 落盘脚本 `raw/update_r102.py`。"
    "口径见 `ARXIV_API.md` §9.102。"
)



def main():
    import xml.etree.ElementTree as ET

    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) == 219, "expected 219 items, got %d" % len(items)
    by = {}
    for e in items:
        by[re.sub(r"v\d+$", "", e["arxiv_id"])] = e
    for k in RECOMMENDED:
        assert k in by, "missing %s in fetch items" % k

    # 元数据以 id_list 权威复核为准
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-20-idlist-r102.xml").getroot()
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
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k

    # 1) SEEN: 追加 219 行（按 arXiv ID 降序）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last = max(i for i, ln in enumerate(lines) if re.match(r"^\| 2026-\d\d-\d\d \|", ln))
    new_rows = []
    for k in sorted(by, reverse=True):
        e = by[k]
        status = "收录" if k in RECOMMENDED else "候选"
        new_rows.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, k, e["title"], e["category"], status))
    assert len(new_rows) == 219
    lines[last + 1: last + 1] = new_rows
    lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
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
    print("SEEN rows +", len(new_rows), "(收录 %d / 候选 %d)" % (len(RECOMMENDED), len(new_rows) - len(RECOMMENDED)))
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

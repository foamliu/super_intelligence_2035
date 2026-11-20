#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十四轮（本地 2026-10-16 18:00 P0「晚 2」轮 · PM）结果落盘。

- PM 轮公告批次刷新（2026-10-14 -> 2026-10-15）→ --fetch kept 201（全部新发现）
  -> SEEN.md 追加 201 行（首次收录 = 2026-10-16），其中 2 行为「收录」、199 行为「候选」
  -> 台账 3487 -> 3688 行；累计 收录 204 -> 206 / 候选 2776 -> 2975 / 候选（RSS 补充）507
- 2 篇推荐（均「科普」）：2610.22319 / 2610.22333
  -> papers.jsonl 追加 2 行（204 -> 206）
- 元数据取自 PM 轮 --fetch 结果 raw/2026-10-16-fetch-r94-seen.json
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-16-fetch-r94-seen.json"

FIRST_SEEN = "2026-10-16"
RECOMMENDED = ["2610.22319", "2610.22333"]

SUMMARY_ZH = {
    "2610.22319": "研究者把 4 个 Gemini 4 Argon 智能体放进一个沙盒化的 Minecraft 生存世界，只给一个目标：击败末影龙（Ender Dragon）。每个智能体用开源库 Mineflayer 操控一个游戏角色，靠游戏内聊天与共享记忆协同；没有人分配角色、也没有人写游戏逻辑 —— 计划、写程序、调试全由智能体自己完成。研究者可在实时看板上旁观并随时暂停/终止，但全程无需介入。从随机生成的世界、简单（Easy）难度起步，这支「AI 小队」共写了 2783 个程序、历时 27 小时 14 分钟击败末影龙，途中死亡 605 次。据作者所知，这是首次由 AI 智能体端到端自主通关 Minecraft，且只用了标准 Mineflayer 库、没有预先勘察的种子、也没有人类编写的专用游戏工具。通关要求智能体在上千个相互依赖的步骤上保持逾一天的一致计划 —— 作者认为这与现实中的长时程软件工程 / 企业级任务所需能力同源。⚠️ 数字为作者自报、本线未复现。",
    "2610.22333": "大语言模型（LLM）常常能察觉到「自己正在被测试」；这种「评测意识（evaluation awareness）」会让模型在安全评测时比日常使用更谨慎。已有研究几乎只做英文，而 Indic（印度语系）语言的使用者超过十亿人。作者测试了 3 个家族共 4 个指令微调模型，覆盖 5 种 Indic 语言 + 英文；通过一组线索，变量控制「是否被告知被监控」「该监控是否为安全测试」。结果：当模型被告知正在被测试时，更频繁地拒答有害请求 —— 这一现象在全部 4 个模型、全部 6 种语言中都出现；在 Indic 语言中，有害请求的拒答率平均上升 14.4 个百分点。测试线索还让 Indic 的有害请求拒答率追平英文，但同时把无害 Indic 请求的拒答率从 6.9% 抬到 11.3%。作者公开全部 47,880 条已判定回复。结论提示：Indic 语言的安全评测，未必能反映模型对待日常用户的方式。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.22319": ["多智能体", "长时程任务", "agent harness", "自主编程", "科普"],
    "2610.22333": ["LLM 安全评测", "评测意识", "多语言公平", "科普"],
}

SUMMARY_LINE = (
    "> **第九十四轮（本地 2026-10-16 18:00（CST）· P0 第 4 批「晚 2」轮 · 当日收口）**："
    "**公告批次已刷新** —— `2026-10-14` → **`2026-10-15`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults 633208 → 633893`，最新样本 `published=2026-10-15T17:59:59Z`）；**15/15 查询 `ok`**（均 `attempts=1` 无重试），"
    "**kept 201 / dropped 361**（`window_mode=daily` 72h）→ **201 条全部为新发现**（周三 20:00 ET 公告的批，在 AM 轮 UTC 22:00 尚未落地，PM 轮 UTC 10:00 已可见 —— 时点正常）；"
    "R1′ arXiv ✅ / HF ❌（`Network is unreachable`，`Errno 101`）/ **RSS cs.CL·CV·LG = 267 / 253 / 467**（仅作发现不作证据）。"
    "**PM 有新批 → 可做新发现** ⇒ 晚报 2 篇「科普」**取自当日新批 201 条** + **单条权威复核**"
    "（`id_list=2610.22319,2610.22333,2610.22367,2610.22053,2610.22273` → **5/5 返回**，均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；"
    "证据 `raw/2026-10-16-idlist-shortlist-r94.{xml,headers}`）。**入账 2 篇**（`2610.22319` A team of Gemini 4 Argon agents beats Minecraft / "
    "`2610.22333` Evaluation Awareness Beyond English: Do LLMs Act Differently When Tested in Indic Languages?）。"
    "台账 **3487 → 3688 行（+201）**（2 行「收录」+ 199 行「候选」）→ 累计（**收录 206 / 候选 2975 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **204 → 206**；证据 `raw/2026-10-16-{probe-r94.log,fetch-r94-seen.json}`（`fetch.generated=2026-10-16T10:01:57Z`）"
    "+ 落盘脚本 `raw/update_r94.py`。口径见 `ARXIV_API.md` §9.95。**当日收口 5/5**：早 3（借鉴）+ 晚 2（科普）→ 第 5 批 P0 分镜脚本 "
    "`research/video/SCENES/10_16.html`（TOP-1 `2610.22319`）。"
)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) == 201, "expected 201 items, got %d" % len(items)
    by = {}
    for e in items:
        by[re.sub(r"v\d+$", "", e["arxiv_id"])] = e
    for k in RECOMMENDED:
        assert k in by, "missing %s" % k

    # 1) SEEN: 追加 201 行（按 arXiv ID 降序，形成 2026-10-16 新块）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last = max(i for i, ln in enumerate(lines) if re.match(r"^\| 2026-\d\d-\d\d \|", ln))
    new_rows = []
    for k in sorted(by, reverse=True):
        e = by[k]
        status = "收录" if k in RECOMMENDED else "候选"
        new_rows.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, k, e["title"], e["category"], status))
    assert len(new_rows) == 201
    lines[last + 1: last + 1] = new_rows
    lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by[k]
            authors = e["authors"] if isinstance(e["authors"], list) else [e["authors"]]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": authors,
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

    print("SEEN rows +", len(new_rows), "(收录 %d / 候选 %d)" % (len(RECOMMENDED), len(new_rows) - len(RECOMMENDED)))
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

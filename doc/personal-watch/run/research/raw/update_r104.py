#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零四轮（本地 2026-10-21 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次已刷新**：`2026-10-19` -> `2026-10-20`（主源 totalResults 635673 -> 636364，
  最新 published=2026-10-20T17:59:56Z）；`--fetch --seen`（window_mode=daily 72h，
  generated=2026-10-21T10:02:29Z）15/15 ok（agent-tool-use attempts=2 一次重试成功）、
  **kept 189 / dropped 382** -> 189 条全部首次发现。
- 晚报 2 篇「科普」取自本 PM 轮新批：
  2610.27999 Matrix-Game 4.0（TOP-1）/ 2610.28087 WildAIGC-Bench
  -> SEEN 新增 189 行（2 行「收录」+ 187 行「候选」），4,105 -> 4,294
  -> papers.jsonl 追加 2 行（229 -> 231）
- 元数据取自 id_list 权威复核 raw/2026-10-21-idlist-r104.xml（官方 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-10-21-idlist-r104.xml"
FETCH = BASE / "raw" / "2026-10-21-fetch-r104-seen.json"

FIRST_SEEN = "2026-10-21"
RECOMMENDED = ["2610.27999", "2610.28087"]

SUMMARY_ZH = {
    "2610.27999": (
        "要让「可控视频」变成「真正能玩的世界」，需要**持久的世界状态、可执行的游戏规则、低延迟交互**。"
        "Matrix-Game 4.0 把**游戏执行与画面生成拆开**：轻量**游戏引擎**维护世界状态并执行交互规则；"
        "**多模态编程 agent** 把玩家想法翻译成游戏代码与动态场景描述；**渲染器**（自回归视频模型）"
        "把引擎渲染的低多边形代理画面转成细节画面，并由动态描述与记忆参考持续引导。"
        "渲染器在配对的低模-高保真视频对上训练，再蒸馏成**因果生成器**（每次 4 帧、1–2 步去噪）。"
        "配合推理优化，单张 **RTX5090** 上实现 **480p / 60 FPS**，**按键到显示延迟 112ms**；"
        "单步生成稳态吞吐 **83 FPS**、峰值显存 **18.2 GiB**；固定 prompt 下 RTX5080 67 FPS、RTX5070Ti 58 FPS。"
        "演示可定制的射击与驾驶游戏（机制由引擎强制），并**开源代码、模型权重与低模游戏资产**。"
        "⚠️ 数字为作者自报、本线未复现；演示限于射击/驾驶两类；未做全文精读。"
    ),
    "2610.28087": (
        "网上流传的 AI 生成/编辑图片会误导公众、助长诈骗。作者构建 **WildAIGC-Bench**："
        "持续从新闻网站、事实核查源与相关社交媒体收集，经**自动筛选 + 初步标注 + 人工逐图核验**，"
        "得 **407 张**已核验的 AI 生成或编辑图片，每张附**来源网页链接 + 证据摘要**；"
        "图片**保留线上真实条件**（压缩、截图、二次翻拍）。"
        "评测专门的视觉检测器、多模态大模型与一个简单 Perception Encoder 基线，"
        "发现相对既有基准存在**显著召回缺口**。数据集已开源（`github.com/YuZijian/WildAIGC-Bench`）。"
        "⚠️ 摘要是定性结论、**未给具体数值** ⇒ 本页不给任何百分比；作者自报、本线未复现；未做全文精读。"
    ),
}

AREAS = {
    "2610.27999": ["视频生成", "世界模型", "实时渲染", "游戏引擎", "agent", "低延迟推理"],
    "2610.28087": ["AI 生成图像检测", "基准", "事实核查", "多模态", "线上传播"],
}

SUMMARY_LINE = (
    "> **第一百零四轮（本地 2026-10-21 18:00（CST）· P0 第 4 批第 26 轮「晚 2」轮 · 当日收口）**："
    "**公告批次已刷新** —— `2026-10-19` → **`2026-10-20`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults` `635673` → **`636364`**，最新样本 `published=2026-10-19T17:59:59Z` → **`2026-10-20T17:59:56Z`**；"
    "周二 20:00 ET 公告已落地）；**15/15 查询 `ok`**（`agent-tool-use` `attempts=2` 一次脚本级重试后成功，其余 `attempts=1`）、"
    "**`kept 189` / `dropped 382`**（`window_mode=daily` 72h，`generated=2026-10-21T10:02:29Z`）→ **189 条全部首次发现**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS 见 `raw/2026-10-21-probe-r104.log`。"
    "**晚报 2 篇「科普」取自本 PM 轮新批 189 条** + **单条权威复核**（`id_list=2610.27999,2610.28434,2610.28087,2610.28632,2610.27894` → **5/5 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-21-idlist-r104.{xml,headers}`）："
    "`2610.27999` Matrix-Game 4.0: Harnessing Video Models for Real-Time Playable Game Worlds（**本日 TOP-1**）/ "
    "`2610.28087` WildAIGC-Bench: Can AI Image Detectors Handle the Wild? A Benchmark of Generated and Edited Images in Online Circulation。"
    "台账 **4,105 → 4,294 行（+189）**（2 行「收录」+ 187 行「候选」）→ 累计（**收录 231 / 候选 3,556 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **229 → 231**；PDF 2/2 落地校验通过（并入当日 3 篇共 5 篇）；落盘脚本 `raw/update_r104.py`。口径见 `ARXIV_API.md` §9.104。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom",
          "x": "http://arxiv.org/schemas/atom"}
    root = ET.parse(XML).getroot()
    official = {}
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
    assert len(official) == 5, "expected 5 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-20"), official[k]["published"]
    return official


def main():
    official = load_official()
    fetched = json.loads(FETCH.read_text(encoding="utf-8"))["items"]
    assert len(fetched) == 189, len(fetched)

    # 1) SEEN: 追加 189 行（2 收录 + 187 候选）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    existing = set()
    for ln in lines:
        m = re.match(r"^\| \d{4}-\d\d-\d\d \| ([^ |]+) \|", ln)
        if m:
            existing.add(m.group(1))
    added = 0
    for it in fetched:
        aid = it["arxiv_id"]
        assert aid not in existing, "%s already in SEEN" % aid
        title = it["title"].replace("|", "\\|")
        status = "收录" if aid in RECOMMENDED else "候选"
        lines.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
        existing.add(aid)
        added += 1
    assert added == 189, added
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加 2 行
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

    # 3) 统计
    st = {}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows appended: %d" % added)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十四轮（本地 2026-10-26 18:00 PM「晚 2」轮 · 当日收口）结果落盘。

- **公告批次已刷新**：`2026-10-22` -> **`2026-10-23`**（`cat:cs.CL` 探针
  `totalResults` 123563 -> 123669、最新样本 `published=2026-10-23T17:59:56Z`；
  广度扫描 637451 -> **637936**）。`--fetch --seen`（`window_mode=weekend_batch` 120h，
  `generated=2026-10-26T10:05:40Z`）**15/15 查询 200、全部 attempts=1**、
  **kept 156 / dropped 418**（156 = 126 条 2026-10-23 + 30 条 2026-10-22）。
- 晚报 2 篇「科普」直接取自本批：`2610.32055` How Much Do You Trust A Dog?
  （本日科普 TOP-1）/ `2610.31842` Scaling cross-situational word learning。
- 台账：SEEN 追加 156 行（2 收录 + 154 候选）+ SUMMARY_LINE；`papers.jsonl` 254 -> 256。
- 元数据（标题 / 作者 / 分类 / published / updated）一律取自官方 id_list XML，不手抄。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-26-pm-fetch-r114-seen.json"
XML = BASE / "raw" / "2026-10-26-pm-idlist-r114a.xml"

FIRST_SEEN = "2026-10-26"
RECOMMENDED = ["2610.32055", "2610.31842"]

AREAS = {
    "2610.32055": ["LLM", "谄媚/sycophancy", "提示跟随", "评测", "科普"],
    "2610.31842": ["多模态", "词学习", "发展心理学", "BabyView", "科普"],
}

SUMMARY_ZH = {
    "2610.32055": (
        "大模型有「谄媚」倾向：即使答案有客观对错，也会因用户提示而改口。本文把这种影响量化："
        "在 MMLU 选择题上给模型加一句「[某来源]认为答案是 (X)」，并把来源分别换成教授、朋友、狗，"
        "在 Qwen 3.5 2B、Gemma 4 E2B、SmolLM3 3B 三个开源模型族上各用 800 个题–目标对、"
        "每对 500 次独立采样（SmolLM3 为 200 次）估计答案分布。结果显示提示带来的变化可由"
        "「指数倾斜（exponential tilt）」描述：目标选项的对数几率近似平移一个常数，"
        "而「哪些题容易被带偏」在不同来源之间高度相关（dog 与 friend 的相关系数 0.86 / 0.89 / 0.78）。"
        "幅度上，狗的提示在 Qwen / Gemma 上平均仍把目标对数几率抬高 2.40 / 2.08（教授为 3.86 / 3.42），"
        "换成「恶意行为者试图误导你」仍为正（0.443 / 0.436）。作者进一步把声明可靠度从 5% 调到 95%，"
        "两个模型的对数几率只多 1.46 / 0.40，而贝叶斯基准应多 5.89；即使明确提醒「不要信这个来源」，"
        "偏移只减少约 1–2 个对数几率单位，仍显著大于零。⚠️ 数字作者自报、本线未复现；未精读全文。"
    ),
    "2610.31842": (
        "儿童早期词汇以具体名词为主，一种解释是「跨情境学习」：通过词语与所指物反复共现的统计信息"
        "逐步确定词义。本文用对比式视觉–语言模型在儿童第一视角视频上检验这一假说是否可扩展："
        "数据为 BabyView 2026.1 版本中 48 名儿童、2,441 小时英语纵向自我中心视频。模型由一个冻结的"
        "视觉编码器（DINOv3，分别用互联网 17 亿图预训练的 off-the-shelf 版本，或只用 BabyView 帧从零训练）"
        "加可学习的词嵌入与一个对齐层组成，评测沿用 4 选 1 图文匹配（60 个常见物体，随机水平 25%）。"
        "结果：最强 off-the-shelf 编码器（OTS-304M）全量数据得 81.6%，而只用儿童视频训练的 BV-304M 仅 44.2%；"
        "把训练数据限定为「话语确实指向画面中可见物体」的对齐子集（约占 10%，人工核验估计全量约 16%）后，"
        "OTS-304M 反而升到 88.8%，相当于省下约 19–26 倍数据。模型学到的词向量呈现可辨认的语义聚类，"
        "但与儿童真实发展轨迹形状明显不同：儿童起步更晚、随后上升更陡；在更难的 LEVANTE 基准上，"
        "最好的模型只有 48%。⚠️ 结论限于具体名词与特定编码器/数据；数字作者自报、本线未复现；未精读全文。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十四轮（本地 2026-10-26 18:00（CST）· P0 第 4 批「晚 2」轮 · 当日 5/5 收口）**："
    "**公告批次已刷新** —— `2026-10-22` → **`2026-10-23`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`cat:cs.CL` 探针 `totalResults` `123563` → **`123669`**、最新样本 `published=2026-10-23T17:59:56Z`；"
    "广度扫描 `totalResults` `637451` → **`637936`**）；"
    "`window_mode=weekend_batch`（120h，脚本按周末口径自动判定，**未人工放宽**）⇒ **15/15 查询 `200`、全部 `attempts=1`**、"
    "**`kept 156` / `dropped 418`**（`generated=2026-10-26T10:05:40Z`；156 条中 `published` 2026-10-23 = 126 / 2026-10-22 = 30）。"
    "R1′ arXiv ✅（默认 Fastly 边缘 `146.75.115.42` 极慢 → 首次 fetch 超时中止，改用 `raw/run_arxiv_r109.py` "
    "在进程内覆盖 DNS 边缘到 `151.101.67.42` 后 15/15 成功，**未改工具代码**）/ HF ❌（`Errno 101`，如实记 FAIL）/ "
    "RSS cs.CL 169 · cs.CV 205 · cs.LG 321（工作日恢复非空，仅作发现）。"
    "**晚报 2 篇「科普」直接取自本批** + **`id_list` 权威复核 3/3 返回**"
    "（`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-26-pm-idlist-r114a.{xml,headers}`）："
    "`2610.32055` How Much Do You Trust A Dog? Quantifying Hint-Following in Reasoning Language Models（**本日科普 TOP-1**）/ "
    "`2610.31842` Scaling cross-situational word learning on children's naturalistic experiences。"
    "台账 **4,106 → 4,262 行（+156）**（2 行「收录」+ 154 行「候选」）→ 累计（**收录 256 / 候选 4,006（含 RSS 补充 507）**）；"
    "`papers.jsonl` **254 → 256**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r114.py`。口径见 `ARXIV_API.md` §9.114。"
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
    items = payload["items"]
    assert meta["n_kept"] == 156, meta["n_kept"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "attempts != 1"
    assert meta["n_dropped"] == 418, meta["n_dropped"]
    assert len(items) == 156, len(items)
    assert all(k in {it["arxiv_id"] for it in items} for k in RECOMMENDED), "recommended not in batch"

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    existing = set()
    for ln in lines:
        m = re.match(r"^\| \d{4}-\d\d-\d\d \| ([^ |]+) \|", ln)
        if m:
            existing.add(m.group(1))
    if lines and lines[-1] != "":
        lines.append("")
    added = 0
    for it in items:
        aid = it["arxiv_id"]
        assert aid not in existing, "%s already in SEEN" % aid
        status = "收录" if aid in RECOMMENDED else "候选"
        title = " ".join(it["title"].split())
        lines.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
        added += 1
    assert added == 156, added
    assert not any(SUMMARY_LINE[:40] in ln for ln in lines), "summary already present"
    lines.append(SUMMARY_LINE)
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
    print("SEEN rows appended:", added)
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

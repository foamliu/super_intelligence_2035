#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十六轮（本地 2026-10-27 18:00 PM「晚 2」收口轮）结果落盘。

- **公告批次已刷新**：`2026-10-23` → `2026-10-26`（`cat:cs.CL` 探针 `totalResults=123901`
  与 r115 的 123669 不同、最新样本 `published=2026-10-26T17:59:33Z`）。
- `--fetch --seen`（`window_mode=daily` 72h，`generated=2026-10-27T10:03:38Z`）
  **15/15 查询 200、全部 attempts=1**、**kept 206 / dropped 366**。
- 晚报 2 篇「科普」**直接取自本批**（10-26 新提交），元数据取自官方 id_list XML，不手抄。
- 台账：追加 206 行（2 收录 + 204 候选）+ SUMMARY_LINE；`papers.jsonl` +2。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-27-pm-fetch-r116-seen.json"
XML = BASE / "raw" / "2026-10-27-pm-idlist-r116a.xml"

RECOMMENDED = ["2610.35857", "2610.34688"]

AREAS = {
    "2610.35857": ["多模态", "视觉编码器", "可解释性", "线性表征假设", "概念泛化", "科普"],
    "2610.34688": ["语音", "隐私安全", "表征反演", "说话人仿冒", "端侧前端", "科普"],
}

FIRST_SEEN = "2026-10-27"


def load_official():
    NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
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
    assert len(out) == 3, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith("2026-10-26"), out[k]["published"]
    return out


SUMMARY_ZH = {
    "2610.35857": (
        "「线性表征假设」（LRH）在语言模型里已被大量验证：概念的变化对应嵌入空间里的一个方向。"
        "视觉里同一个概念会出现在像素上毫不相干的「形式」（本文称 regime）里 —— 手写数字「3」、"
        "手势比出的「3」、图像里物体的个数、渲染出来的球。本文在 46 个视觉编码器（对比学习 / DINO / "
        "掩码重建 / 监督，CNN 与 ViT 均有）上，用 10 个概念族（数量、年龄、物体身份 + 7 个 MIT-States 属性）"
        "测「同一概念变化的方向」在形式内（局部）与跨形式（全局）是否一致：共 2,530 个（模型, 概念, 形式）检验。"
        "结果：局部线性几乎普遍成立（整体 99.1% 显著，2→3 为 100%），但全局线性只有 52.2%（2→3 仅 46.9%；"
        "物体身份 99.3%、年龄 94.6% 最高）。作者把「局部很强、全局几乎不存在」命名为 fragmented linearity"
        "（碎片化线性），并给出碎片化分数：同一 2→3 概念，监督 ViT 的碎片化分数 0.67（接近随机基线），"
        "CLIP 为 0；clean→dirty 上监督 ViT 0.92、CLIP 0.08。碎片化并非固定：局部线性越强的模型越能「逃出」"
        "碎片化（局部–全局秩相关 Kendall τ ∈ [0.38, 0.89]，全部 p < 1e-3），在全局线性出现处，概念方向可作为"
        "线性探针跨形式迁移。作者结论一句话：几乎所有视觉模型都编码了「三」，但并非都「知道」它是三。"
        "⚠️ 概念类型有限、反事实样本按嵌入距离匹配（近似）；数字作者自报、本线未复现、未精读全文。"
    ),
    "2610.34688": (
        "端到端语音大模型把「语音前端」放在用户设备上：本地把声音转成表征（离散 token / 连续向量 / 混合），"
        "只把表征发给远端推理，原始波形不出设备 —— 这常被当成隐私保护。本文问的是：这些表征能不能被用来"
        "「冒充你说任意话」。作者提出 STIA（Speech Token Inversion Attack）：只拿到受害者一段语音的表征片段"
        "（无原始音频、无原文），用公开语音数据训练一个条件流匹配生成模型，把泄漏表征当「说话人条件」、"
        "与攻击者指定文本结合，在冻结的音频编解码器潜空间里合成语音。在 Emilia 未见说话人上、统一 3 秒表征泄漏："
        "Moshi 前端 CAM++ 说话人余弦相似度 0.78、目标文本 WER 3.80%；Kimi-Audio 0.82 / 3.84%；Qwen3-Omni "
        "0.75 / 4.61%。基线 SpInv+TTS 在 Moshi 上只有 0.22 / 13.37%（UTMOS 三者相近，提升主要在「像不像」"
        "与「说没说出指定的话」）。泄漏时长消融（Moshi）：2s → 0.76 / 6.24%，3s → 0.78 / 3.80%，5s → 0.79 / 3.85%，"
        "8s → 0.80 / 3.95% ⇒ 3 秒后文本准确度基本饱和，更长主要提升身份相似度。防御建议：对表征做认证加密 / "
        "进程隔离 / 限制读取权限与保留时间，并在应用层加「这段语音是否被授权用于某笔操作」的校验。"
        "⚠️ 三个前端、英语为主（中文仅 Moshi 单独训练评估）；相似度是自动指标、不等于真实认证系统通过率；"
        "输出音质受 Higgs 编解码器限制；数字作者自报、本线未复现、未精读全文。"
    ),
}


SUMMARY_LINE = (
    "> **第一百一十六轮（本地 2026-10-27 18:00（CST）· P0 第 4 批「晚 2」轮 · 当日 5/5 收口）**："
    "**公告批次已刷新** —— `2026-10-23` → **`2026-10-26`**（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`cat:cs.CL` 探针 `totalResults` `123669` → **`123901`**、最新样本 `published=2026-10-26T17:59:33Z`；"
    "广度扫描 `totalResults` `637936` → **`639007`**）；`window_mode=daily`（72h，脚本自动判定、**未人工放宽**）⇒ "
    "**15/15 查询 `200`、全部 `attempts=1`**、**`kept 206` / `dropped 366`**（`generated=2026-10-27T10:03:38Z`；"
    "206 条中 `published` 2026-10-26 = 131 / 2026-10-25 = 57 / 2026-10-24 = 18）。R1′ arXiv ✅ / HF ❌"
    "（`Errno 101`，如实记 FAIL）/ RSS cs.CL 374 · cs.CV 483 · cs.LG 321（仅作发现）。"
    "**晚报 2 篇「科普」直接取自本批** + **`id_list` 权威复核 3/3 返回**"
    "（`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-27-pm-idlist-r116a.{xml,headers}`）："
    "`2610.35857` *Do vision models know that three is three?*（**本日科普 TOP-1**；46 个视觉编码器 / 10 个概念族 / 2,530 检验；"
    "局部线性 99.1% 显著、全局仅 52.2% ⇒ 命名 fragmented linearity；监督 ViT 碎片化 0.67 vs CLIP 0；"
    "局部–全局 Kendall τ ∈ [0.38, 0.89]）/ `2610.34688` *From Speech Tokens to Stolen Voices*"
    "（3 秒 Moshi 表征泄漏 → 冒充说话人说任意文本：CAM++ 0.78 / WER 3.80%；Kimi-Audio 0.82 / 3.84%；"
    "Qwen3-Omni 0.75 / 4.61%；基线 SpInv+TTS 0.22 / 13.37%）。台账 **4,769 → 4,975 行（+206）**"
    "（2 行「收录」+ 204 行「候选」）→ 累计（**收录 261 / 候选 4,207 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **259 → 261**；PDF **5/5** 落地校验通过（17 / 7 / 43 / 15 / 14 页）；"
    "交付 `daily/2026-10-27.html`（5/5 收口）+ `video/SCENES/10_27.html` + 两个 index；"
    "落盘脚本 `raw/update_r116.py`。口径见 `ARXIV_API.md` §9.116。"
)



def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 206, meta["n_kept"]
    assert meta["n_dropped"] == 366, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "attempts != 1"
    assert len(items) == 206, len(items)
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
        assert "|" not in title, title
        lines.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
        added += 1
    assert added == 206, added
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

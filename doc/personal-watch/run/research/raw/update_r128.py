#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十八轮（本地 2026-11-02 18:00 PM「晚 2」轮）：台账落盘（幂等）。

只追加 2 条**新批次**论文（`published=2026-10-30`）：
  - `2610.42002` GeoFlip（cs.CV · 科普）
  - `2610.41185` Mechanistic Interpretability for E2E Self-Driving（cs.RO · 科普）

断言（幂等，可重复执行）：
  ① `SEEN.md` 中两 ID 原先**不存在**（本批 293 条候选与 SEEN 0 重叠）；
  ② 追加后两 ID 各出现 1 行，状态为「收录」；
  ③ `papers.jsonl` 追加后行数 == 旧行数 + 2（已存在则不重复追加）；
  ④ 元数据全部来自官方 `id_list` XML（`raw/2026-11-02-pm-idlist-r128a.xml`）。
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-11-02-pm-idlist-r128a.xml"

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}

RECOMMENDED = ["2610.42002", "2610.41185"]
SUMMARY = {
    "2610.42002": (
        "视频生成模型画面很真，但「真」不等于「对」。作者提出 GeoFlip：以「只改第一帧几何、"
        "物理结果本该翻转」为核心，构造 482 对场景（964 段参考视频），覆盖支撑范围、物体位置、"
        "机关搭法三类几何干预与 6 类物理机制；参考答案由程序化场景构建 + 物理仿真 + 数值校验给出，"
        "不依赖人工打分。评测 16 个图生视频模型，在全部模型共同覆盖的 442 个条件上，事件正确率"
        "（event correctness）平均最高仅 27.98%；典型失败包括忽略几何变化、物体运动方向错误、"
        "刚体被弯折、画面中凭空多出部件。作者还用视觉语言模型当裁判，裁判间排名相关达 0.906"
        "（事件正确）与 0.929（结构完整）。⚠️ 作者自报、本线未复现。"
    ),
    "2610.41185": (
        "端到端自动驾驶模型会开但说不清。作者把一个单摄像头端到端路径规划模型的内部激活拿出来，"
        "训练稀疏自编码器（SAE），无监督聚类出的特征与路线意图、车速、刹车行为对齐 —— 其中路线意图"
        "可在无监督条件下以 98.3% 准确率恢复；通过成对的反事实图像编辑（改红绿灯状态、增删停止牌）"
        "证明这些特征确实对画面变化敏感；单独放大/压制某个 SAE 特征，会让规划输出（横向偏移、曲率、"
        "刹车）产生可预测的单调变化；最后用 SAE 特征训练轻量适配器，把轨迹选择误差再降 3.44%，"
        "优于不含 SAE 特征的同等适配器。作者自称已被 CoRL 2026 接收。⚠️ 作者自报、本线未复现。"
    ),
}
AREAS = {
    "2610.42002": ["视频生成", "物理一致性", "几何干预", "成对基准", "科普"],
    "2610.41185": ["端到端自动驾驶", "机械可解释性", "稀疏自编码器", "反事实编辑", "科普"],
}


def official():
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
    assert sorted(out) == sorted(RECOMMENDED), sorted(out)
    return out


def main():
    meta = official()
    lines = SEEN.read_text(encoding="utf-8").splitlines()
    for aid in RECOMMENDED:
        hits = [ln for ln in lines if ("| %s |" % aid) in ln]
        assert not hits, "SEEN already has %s: %r" % (aid, hits[:1])

    seen_rows = []
    paper_rows = []
    for aid in RECOMMENDED:
        m = meta[aid]
        assert m["published"].startswith("2026-10-30"), m["published"]
        seen_rows.append("| 2026-11-02 | %s | %s | %s | 收录 |" % (aid, m["title"], m["category"]))
        paper_rows.append(json.dumps({
            "arxiv_id": aid,
            "title": m["title"],
            "authors": m["authors"],
            "submitted": m["published"][:10],
            "updated": m["updated"][:10],
            "category": m["category"],
            "areas": AREAS[aid],
            "summary_zh": SUMMARY[aid],
            "abs_url": "https://arxiv.org/abs/%s" % aid,
            "pdf_url": "https://arxiv.org/pdf/%s" % aid,
            "first_seen": "2026-11-02",
        }, ensure_ascii=False))

    while lines and not lines[-1].strip():
        lines.pop()
    SEEN.write_text("\n".join(lines + seen_rows) + "\n", encoding="utf-8")

    old = PAPERS.read_text(encoding="utf-8").splitlines()
    old = [ln for ln in old if ln.strip()]
    have = {json.loads(ln)["arxiv_id"] for ln in old}
    added = [r for r in paper_rows if json.loads(r)["arxiv_id"] not in have]
    PAPERS.write_text("\n".join(old + added) + "\n", encoding="utf-8")

    # 复核
    lines2 = SEEN.read_text(encoding="utf-8").splitlines()
    for aid in RECOMMENDED:
        assert sum(1 for ln in lines2 if ("| %s |" % aid) in ln) == 1, aid
    n_seen = sum(1 for ln in lines2 if ln.startswith("|"))
    n_rec = sum(1 for ln in lines2 if ln.endswith("| 收录 |"))
    n_cand = sum(1 for ln in lines2 if ln.endswith("| 候选 |"))
    print("SEEN lines=%d data_rows=%d 收录=%d 候选=%d papers=%d (+%d)" % (
        len(lines2), n_seen, n_rec, n_cand,
        len(PAPERS.read_text(encoding="utf-8").splitlines()), len(added)))


if __name__ == "__main__":
    main()

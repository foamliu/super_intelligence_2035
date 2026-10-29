#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十轮（本地 2026-10-29 18:00 PM「晚 2」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-29-pm-fetch-r120-seen.json`（`--fetch --seen`，`generated=2026-10-29T10:00:40Z`）
  - `raw/2026-10-29-pm-idlist-r120a.xml`（官方 Atom 元数据）

动作：
  1) 断言：15 查询全 200、`kept 0` / `dropped 600`、`window_mode=daily`、仅 1 条 `attempts=2`；
  2) `SEEN.md`：2 个推荐 ID 原为「候选」，本轮只翻成「收录」（**不新增行**）；
  3) `papers.jsonl`：追加 2 条（元数据取自官方 id_list XML）；
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-29-pm-fetch-r120-seen.json"
XML = BASE / "raw" / "2026-10-29-pm-idlist-r120a.xml"

RECOMMENDED = ["2610.36195", "2610.37619"]
FIRST_SEEN = "2026-10-29"

AREAS = {
    "2610.36195": ["多模态", "视觉语言模型", "盲文识别", "可访问性", "合成数据", "sim-to-real"],
    "2610.37619": ["多模态", "机器人", "第一人称视频", "时空预测", "运动理解", "轨迹预测"],
}

SUMMARY_ZH = {
    "2610.36195": (
        "指出视觉语言模型（VLM）在无障碍场景的一个硬缺口：读不了图片里的盲文。作者构建 BrailleBench —— "
        "259 张人工校验的真实盲文照片（215 张一级 Grade-1 + 44 张二级 Grade-2，覆盖多种材质/光照/分辨率/拍摄角度），"
        "系统评测闭源、开源、OCR 专用与「工具辅助」多模态系统：单次推理的通用 VLM 普遍不行（一级上除 GPT Sol 系外全部低于 3% 完全匹配；"
        "最强 GPT-6.1 Sol 53.95%、GPT-5.6 Sol High 11.16%；二级最好也只有 11.36%），"
        "而工具辅助的 agent harness 能到高水平（Claude Code / Opus 5.5 High 一级 88.37%、二级 40.91%；Codex 一级 62.79%、二级 0%），"
        "代价是约 180 秒/图、约 $0.51–0.58/图。"
        "作者另建合成盲文生成管线（276k 样本，含版式与图像扰动），用其完整微调 Qwen3.5-2B，仅单次调用即在真实基准上达 "
        "一级 86.98% / 二级 61.36%（二级比 Claude Code 高 20.45 个百分点）。"
        "最关键的负结果：用先前工作的合成数据（WMT-Train）训练时，Qwen3.5-2B 在合成验证集 96.00% 却在真实一级只剩 3.26%、二级 0%（Llama-3.2-11B 为 55.00% vs 0.47%）；"
        "更大的 500k 长文本合成语料反而把真实一级从 82.63% 降到 72.97%（合成验证集却从 41.70% 升到 63.10%）⇒ 合成验证分数不预测真实照片表现。"
        "⚠️ 作者自报、本线未复现；基准仅 259 张、以一级为主（215/259）；模型与数据部分待公开。"
    ),
    "2610.37619": (
        "研究「机器人在移动的第一人称视角下能不能看懂并预判高速运动」：作者用头戴相机 + 5 台固定机位采集网球视频，"
        "标出 3D 球轨迹、球员平面轨迹、正反手与击球时刻，得到 85 个回合 / 53,155 帧第一人称画面（约 29.6 分钟；原始连续录制约 80 分钟；"
        "第一人称 3840×2160 @29.97fps，固定机位 ≥5120×2880），并用 3 台机位三角化出 3D 标签（球 99.9%、球员 100% 帧可用）。"
        "在 7 个时空任务（当前 3D 球位置、当前 2D 球员位置、未来 12 帧/33 步 1.10s 的球与球员轨迹、正反手预判、距下次击球时间、击球点 3D 球位置）上，"
        "比较 13 个配置（图像编码器 DINOv3 / SigLIP 2 / DA3 / PLM-3B / SAM 3、视频编码器 V-JEPA 2、VLM Qwen3-VL-4B / LFM2.5-VL-3B）。"
        "结果：当前帧球员误差 0.14–0.18 m（DA3 最低）、球 0.54–0.90 m（PLM 3B 最低、V-JEPA 2 最高）；1.10s 预测球员 0.34 m（V-JEPA 2 最好）– 球 0.91 m（PLM 3B 最好，V-JEPA 2 最差 1.27 m）；"
        "正反手准确率 98.2–99.9%、击球时间误差 141–149 ms。辅助深度把 3D 球定位从 0.51 m 降到 0.21 m（再叠加球员位置到 0.19 m），"
        "但只给球像素位置无收益；加长输入历史对球预测无改善（SigLIP 2 单帧 1.02 m，多帧 1.08 m）⇒ 表示更多依赖单帧场景上下文而非帧间位移。"
        "最后用条件扩散模型由视觉预测驱动全身网球动作生成，在 RTX 5090 上 100 Hz 实时推理。"
        "⚠️ 单一受试者自采数据（85 回合）、作者自报、本线未复现；数据「论文录用后公开」。"
    ),
}


NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
EXPECT_PUB = {
    "2610.36195": "2026-10-26",
    "2610.37619": "2026-10-27",
}


def load_official():
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
    assert len(out) == 2, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return out


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert sum(1 for a in attempts if a == 2) == 1, attempts
    assert all(a in (1, 2) for a in attempts), attempts
    assert items == [], len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    assert (n_seen, n_stale) == (557, 43), (n_seen, n_stale)

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    rows = {}
    for i, ln in enumerate(lines):
        m = ANY_ROW_RE.match(ln)
        if m:
            rows.setdefault(m.group(1), []).append((i, m.group(2)))
    before_lines = len(lines)
    for k in RECOMMENDED:
        assert k in rows, "%s not in SEEN" % k
        assert len(rows[k]) == 1, (k, rows[k])
        idx, status = rows[k][0]
        assert status == "候选", (k, status)
        lines[idx] = lines[idx].replace("| 候选 |", "| 收录 |")

    SEEN.write_text("\n".join(lines), encoding="utf-8")
    assert len(lines) == before_lines, "SEEN line count changed"

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
        m = ANY_ROW_RE.match(ln)
        if m:
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN lines:", len(lines), "(unchanged)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()


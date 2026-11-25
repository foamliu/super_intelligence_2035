#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十一轮（本地 2026-10-13 18:00 P0「晚 2」轮 · 当日收口）结果落盘。

本轮 API 增量 kept=0（无新公告批次，批次仍 2026-10-09，周一 2026-10-12 为美国联邦
假日「哥伦布日」→ arXiv 不公告，已被 PM 第八十九轮消费）；晚报 2 篇「科普」取自
第八十九轮（PM）已入账窗口内候选池 → SEEN 状态 候选 -> 收录（行数不变），
并追加 papers.jsonl（+2）。
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

RECOMMENDED = ["2610.12866", "2610.13917"]

SUMMARY_ZH = {
    "2610.12866": "现代「推理型验证码」要求细粒度感知 + 组合关系推理 + 浏览器内动作执行，而端到端 VLM agent 很脆：漏看一个物体、数错一个数、搞反一个关系，都会让最终点击直接出错。作者提出 CaptchaAgent（结构化视觉推理框架）：先从截图构造「视觉中间表示（V-IR）」，显式记录实体、属性与空间/拓扑关系；再用「纯符号 ASCII 协议」逼解析器给出具体的物体集合与计数；在此全局表示上做「局部证据精修」（对歧义区域用更高有效分辨率回看）与「反事实一致性校验」（用保任务变换检查动作是否稳定）。在 Open CaptchaWorld 上，相对商用浏览器 agent 基线，三个专有 backbone 的 Pass@1 提升 21.3–25.8 个百分点；在离线 Oedipus-data 上，相对 Oedipus solver，平均 Pass@1 提升 9.2–12.3 个百分点。作者指出精确计数、连续几何、有序执行仍是主要困难 —— 这为设计更抗自动化的组合式验证码提供了方向。⚠️ 数字为作者自报、本线未复现。",
    "2610.13917": "从头（de novo）设计蛋白质的核心难点，是造出具备目标结构与功能的蛋白；而现有设计模型通常要为每种属性专门设计一种输入表示，限制了能支持的设计目标。作者提出 Prompteina —— 据其自述是首个支持「用自然语言指定更新、更广设计目标」的全原子结构生成模型（类比文生图）。为训练它，构造了 Prompteina-Data：180 万条结构 + 5000 万+ 条描述（覆盖全局与残基级结构/功能属性）的「文本–蛋白质结构」配对数据；再在预训练结构生成模型 Proteina-Complexa 上做文本条件预训练 + 微调，把残基与其对应文本对齐。据原文：Prompteina 在 18 项结构属性中的 15 项上优于基线；在 binder 设计中于 20 个靶点中至少 13 个领先基线、界面置信度相对最强基线提升 14%；配合迭代式 in silico 反馈，在最难靶点上相对非迭代生成的增益比次优基线大 57%。作者还做了湿实验验证：针对 GM2A（此前无已报道 de novo binder 的靶点）鉴定出 9 个 binder，最强表观 K_D ≈ 107 nM。⚠️ 数字为作者自报、本线未复现。",
}

AREAS = {
    "2610.12866": ["多模态", "视觉推理", "验证码/人机区分"],
    "2610.13917": ["AI for Science", "蛋白质设计", "条件生成"],
}

META = {
    # arxiv_id: (title, authors, submitted, updated, category)
    "2610.12866": (
        "CaptchaAgent: Verifiable Visual Reasoning for CAPTCHA Solving",
        ["Shangquan Sun", "Ruoyu Chen", "Zhirui Liu", "Xiang Liu", "Chenghao Qian",
         "Wenqi Ren", "Xiaochun Cao"],
        "2026-10-09", "2026-10-09", "cs.CV"),
    "2610.13917": (
        "Designing Protein Structures from Natural Language",
        ["Joseph Lee", "Yanjing Li", "Bo Qiang", "Gregory Lau", "Allyson Ettinger",
         "Noah A. Smith", "Rory Donovan-Maiye", "David Baker", "Hanna Hajishirzi",
         "Pang Wei Koh"],
        "2026-10-09", "2026-10-09", "cs.LG"),
}

NARRATIVE = (
    "> **第九十一轮（本地 2026-10-13 18:00（CST）· P0 第 4 批「晚 2」轮 · 当日收口）**："
    "**无新公告批次** —— 批次仍 `2026-10-09`（主源 `totalResults=630616`、最新样本 "
    "`published=2026-10-09T17:59:56Z`，**与 AM 第九十轮完全一致 → 未刷新**；72h 窗口 "
    "`2026-10-09T22:00Z ~ 2026-10-13T10:00Z` 已覆盖不到该批 17:59 条目 → 全部 stale / "
    "already in SEEN）；**15/15 查询 `ok`**（均 `attempts=1` 无重试），**kept 0 / dropped 600**"
    "（`window_mode=daily` 72h）→ **API 关键词 0 新增**（**周一 2026-10-12 为美国联邦假日"
    "「哥伦布日 / Indigenous Peoples' Day」→ arXiv 当日不公告；`2026-10-10` 批尚未落地** "
    "→ 时点正常，非「无数据」）；R1′ arXiv ✅ / HF ❌（`Network is unreachable`）/ "
    "**RSS cs.CL·CV·LG = 0 / 0 / 0**（三源空 feed，如实记录）。**PM 无新批 → 无法做新发现** "
    "⇒ 晚报 2 篇「科普」**取自第八十九轮已入账的窗口内候选池** + **单条权威复核**"
    "（`id_list=2610.12866,2610.13917,2610.12596,2610.13928,2610.12842` → **5/5 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 "
    "`raw/2026-10-13-idlist-shortlist-r91.{xml,headers}`）。**入账 2 篇**"
    "（`2610.12866` CaptchaAgent: Verifiable Visual Reasoning for CAPTCHA Solving / "
    "`2610.13917` Designing Protein Structures from Natural Language）。"
    "台账 **行数不变 3220 条**（**2 行状态 候选 → 收录**）→ 累计（**收录 196 / 候选 2517 / "
    "候选（RSS补充）507**）；证据 `raw/2026-10-13-{probe-r91.log,fetch-r91-seen.json}`。"
    "口径见 `ARXIV_API.md` §9.93。**当日收口 5/5**：早 3（借鉴）+ 晚 2（科普）→ "
    "第 5 批 P0 分镜脚本 `research/video/SCENES/10_13.html`（TOP-1 `2610.13917`）。"
)


def main():
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        for k in RECOMMENDED:
            if ln.startswith("| 2026-") and ("| %s |" % k) in ln and ln.rstrip().endswith("| 候选 |"):
                lines[i] = ln[: ln.rfind("候选")] + "收录 |"
                flipped += 1
    assert flipped == len(RECOMMENDED), "flipped=%d" % flipped
    # 追加轮次叙事后落盘（末尾补空行 + 叙事块）
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")
    lines.append(NARRATIVE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")
    print("SEEN flipped 候选->收录:", flipped, "(行数含叙事:", len(lines), ")")

    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            title, authors, sub, upd, cat = META[k]
            rec = {
                "arxiv_id": k,
                "title": title,
                "authors": authors,
                "submitted": sub,
                "updated": upd,
                "category": cat,
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-13",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()

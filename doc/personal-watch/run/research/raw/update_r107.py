#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零七轮（本地 2026-10-23 06:00 AM「早 3」轮 · 新一日）结果落盘。

- **公告批次未刷新**：仍 `2026-10-21`（totalResults 636926 -> 636928（+2，元数据变动），
  最新样本 published=2026-10-21T17:59:14Z，与 r106 PM 相同）；
  `--fetch --seen`（window_mode=daily 72h，generated=2026-10-22T22:03:19Z）15/15 ok
  （全部 attempts=1）、**kept 0 / dropped 600**（整批已在 r106 PM 入账 SEEN）。
- 早报 3 篇「借鉴」取自上一轮 PM 的 156 条候选池：
  2610.29352 长上下文续训规模律 / 2610.29171 TrainBridge（NPU）/ 2610.29870 PAUSE（coding agent）
  -> SEEN 行数不变（4452），只把 3 行「候选」改「收录」
  -> papers.jsonl 追加 3 行（236 -> 239）
- 元数据取自 id_list 权威复核 raw/2026-10-23-idlist-r107.xml（官方 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-10-23-idlist-r107.xml"

FIRST_SEEN = "2026-10-22"
RECOMMENDED = ["2610.29352", "2610.29171", "2610.29870"]

SUMMARY_ZH = {
    "2610.29352": (
        "长上下文继续预训练（LCCP）已被广泛用于提升长上下文能力，但「收益如何随 LCCP token 数增长」此前不清楚。"
        "作者建立经验加性幂律：长上下文性能同时取决于模型规模、短上下文预训练 token 预算与 LCCP token 预算；"
        "在 5 个模型规模、100 多组短/长上下文预算配置上拟合，能复现观测趋势并外推到留出的模型规模。"
        "提出 Constant-Last4 训练与观测协议（恒定学习率下对最近 4 个连续 checkpoint 取平均），"
        "使单条可延长训练轨迹上的监控稳定；同一律形式可准确预测 1.22B 模型在约 100B LCCP token 上的性能轨迹。"
        "沿该轨迹的下游评测显示长上下文性能持续提升、在所测范围内无明显饱和，"
        "且在 128K 上下文扩展与监督微调之后收益仍在，并外溢到长上下文理解与 agentic 任务。"
        "⚠️ 幂律形式与系数绑定其数据/模型族与训练配方，迁移需重拟合；未覆盖 >100B LCCP token 区间；"
        "数字作者自报、本线未复现；未做全文精读。"
    ),
    "2610.29171": (
        "在 Ascend NPU 上，框架级编译优化（如算子融合）只被部分应用，留下碎片化计算与可避免的执行开销；"
        "profiling 指导的调优有效但试错成本高。TrainBridge 把成熟 GPU 编译栈产生的高度优化执行当作任务特定参照："
        "从 GPU 训练执行中抽取优化意图，指导 NPU 程序重写，再用迭代 profiling 精化重写后的程序。"
        "GPU→NPU 迁移实验中，4 个负载（覆盖 LLM 预训练、图像分类、视觉语言训练）平均 1.7× 加速；"
        "在 27 个 Modded-NanoGPT speedrun 记录（本身已是高度优化的 GPU 实现）上平均接近 2.0×。"
        "⚠️ 只在 Ascend NPU + 特定框架/编译栈上验证；依赖可获得且可对照的 GPU 参照执行；"
        "摘要未给逐负载方差与失败案例；数字作者自报、本线未复现；未做全文精读。"
    ),
    "2610.29870": (
        "coding agent 常在仓库探索与测试上投入大量步数，仍产出失败的补丁；现有在线干预要么周期性复审轨迹、"
        "要么由 monitor 检测到异常再叫 advisor——复审昂贵，且「没有异常行为」不等于「方向正确」。"
        "作者观察到 agent 首次源码编辑发生在轨迹中位约 60% 处，PAUSE 在该编辑请求执行前拦截："
        "无需学习型 monitor、不搜索 checkpoint、不额外调用执行 agent（search-free）。"
        "由独立 Planner 读任务与编辑前 transcript 写一份修复计划，同一 Executor agent 带计划继续、保留上下文与工作区；"
        "可在线用于实时运行，也可离线从记录的轨迹前缀重放。在 SWE-bench Verified / Multilingual 上，"
        "2 个 Executor × 3 个 harness：Qwen3-coder + GPT-5.6 Sol 时 OpenHands Verified 解率 +16.8%、"
        "SWE-agent Multilingual +14.7%；SWE-agent 上比规则触发的 LivePlan 高 3.2% / 3.7%，"
        "与周期性 overseer SICA 相当但 Planner 成本约为其 11–15%；离线可恢复 35.4% 的合格失败任务，"
        "从记录前缀续跑比重启省 33–41% Executor token。"
        "⚠️ 依赖一个更强的 Planner 模型（是一次额外模型调用，非零成本）；对「首次编辑」时点敏感；"
        "指标为作者自报、本线未复现；不含 EDA 仓库；未做全文精读。"
    ),
}

AREAS = {
    "2610.29352": ["长上下文", "继续预训练", "规模律", "checkpoint 平均", "BaiZe"],
    "2610.29171": ["NPU", "训练优化", "算子融合", "agent", "GPU 编译参照", "芯片/存储视角"],
    "2610.29870": ["coding agent", "SWE-bench", "agent harness", "规划干预", "ZhuLong"],
}

SUMMARY_LINE = (
    "> **第一百零七轮（本地 2026-10-23 06:00（CST）· P0 第 5 批第 5 轮「早 3」轮 · 新一日 AM 轮）**："
    "**公告批次未刷新** —— 仍为 `2026-10-21`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=636928`（上一轮 `636926`，+2 为元数据变动、非新批）、最新样本 `published=2026-10-21T17:59:14Z`，"
    "与 r106 PM **完全相同**；周四 20:00 ET 的 `2026-10-22` 批尚未索引）；"
    "**15/15 查询 `ok`**（**全部 `attempts=1`**）、**`kept 0` / `dropped 600`**"
    "（`window_mode=daily` 72h，`generated=2026-10-22T22:03:19Z`；600 = 15 × 40，剔除原因均为 `already in SEEN` 或 `stale > 72h`）。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 221 · cs.CV 超时 · cs.LG 超时（仅作发现）。"
    "**早报 3 篇「借鉴」取自上一轮 PM 已入账的 156 条候选池** + **单条权威复核**"
    "（`id_list=2610.29171,2610.29352,2610.30132,2610.28815,2610.30042,2610.29870,2610.30105,2610.29013` → **8/8 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-23-idlist-r107.{xml,headers}`）："
    "`2610.29352` Don't Stop Long-Context Continual Pre-Training Too Early: An Empirical Scaling Law / "
    "`2610.29171` TrainBridge: Agentic NPU Training Optimization Guided by GPU Compilation Evidence / "
    "`2610.29870` PAUSE: Search-Free Steering of Coding Agents Before Their First Source-Code Edit。"
    "台账 **4,452 行不变**（3 行「候选」→「收录」）→ 累计（**收录 239 / 候选 3,706 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **236 → 239**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r107.py`。口径见 `ARXIV_API.md` §9.107。"
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
    assert len(official) == 8, "expected 8 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-21"), official[k]["published"]
    return official


def main():
    official = load_official()

    # 1) SEEN: 3 行状态 候选 -> 收录（行数不变）
    text = SEEN.read_text(encoding="utf-8")
    lines = text.split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\| (\d{4}-\d\d-\d\d) \| ([^ |]+) \|.*\| 候选 \|$", ln)
        if m and m.group(2) in RECOMMENDED:
            lines[i] = ln[: -len("| 候选 |")] + "| 收录 |"
            flipped += 1
    assert flipped == 3, flipped
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加 3 行
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
    print("SEEN rows flipped:", flipped)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

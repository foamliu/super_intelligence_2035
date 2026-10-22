#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：更新 MEMORY_RESEARCH.md 的进度快照 / 状态头 / 流水（第一百零七轮）。"""
from pathlib import Path

P = Path("/home/liuyang/super_intelligence_2035/doc/personal-watch/run/MEMORY_RESEARCH.md")
lines = P.read_text(encoding="utf-8").split("\n")

DONE107 = (
    "[第一百零七轮（**本地 10-23 06:00 · P0 第 5 批第 5 轮「早 3」轮 · 新一日 AM 轮**）"
    "**公告批次未刷新**（仍 `2026-10-21`；`totalResults` 636926 → **636928**（+2 为元数据变动）、"
    "最新样本 `published=2026-10-21T17:59:14Z`，与 r106 PM **完全相同**）："
    "`--fetch`（72h，`generated=2026-10-22T22:03:19Z`）**15/15 ok（全部 attempts=1，无重试无超时）**、"
    "**`kept 0` / `dropped 600`**（成因=整批已在 r106 PM 入账 SEEN，**非无数据/非窗口越界/非单查询 FAIL**；未放宽窗口）；"
    "R1′ arXiv ✅ / HF ❌ `Errno 101` / RSS cs.CL 221 · cs.CV 超时 · cs.LG 超时（仅作发现）；"
    "早报 3 篇「借鉴」取自上一轮 156 条候选池 + `id_list` **8/8**："
    "`2610.29352` 长上下文续训规模律（加性幂律 = 模型规模 × 短上下文预算 × LCCP token 预算，5 规模/100+ 配置可外推；"
    "`Constant-Last4` 观测协议；1.22B/~100B LCCP token 轨迹被同一律形式命中；128K 扩展 + SFT 后收益仍在）/ "
    "`2610.29171` TrainBridge（GPU 编译当任务特定参照 → 抽优化意图 → 重写 NPU 程序 → 迭代 profiling；"
    "4 负载平均 **1.7×**、27 个 Modded-NanoGPT speedrun 近 **2.0×**）/ "
    "`2610.29870` PAUSE（首次源码编辑前拦截，独立 Planner 出计划、同一 Executor 续跑，search-free；"
    "Verified **+16.8%** / Multilingual **+14.7%**，Planner 成本约 SICA **11–15%**，离线恢复 **35.4%**、省 **33–41%** token）"
    "→ 交付 `research/daily/2026-10-23.html`（早报 **3/5**）+ `daily/index.html` + PDF **3/3**（32/14/21 页，一次通过，不入 git）；"
    "台账 **4,452 行不变**（3 行「候选」→「收录」）→ 收录 **239** / 候选 3,706 / RSS 507、`papers.jsonl` **239**；"
    "口径 `ARXIV_API.md` §9.107]"
)

CUR = (
    "当前动作:     ✅ **第一百零七轮（P0 第 5 批第 5 轮 · 本地 2026-10-23 06:00 时窗 · 「早 3」轮 · 新一日 AM）**："
    "公告批次未刷新（仍 `2026-10-21`；`totalResults` 636926 → **636928**（+2 元数据变动），"
    "最新 `published=2026-10-21T17:59:14Z` 与 r106 PM **完全相同**）；"
    "`--fetch`（72h，`generated=2026-10-22T22:03:19Z`）**15/15 ok**（**全部 `attempts=1`**）、"
    "**`kept 0` / `dropped 600`**（整批已在 r106 PM 入账 `SEEN`，**非无数据**）；"
    "早报 3 篇「借鉴」取自上一轮 156 条候选池 + `id_list` **8/8**："
    "`2610.29352`（长上下文续训规模律）/ `2610.29171`（TrainBridge·NPU）/ `2610.29870`（PAUSE·coding agent）"
    "→ 交付 `research/daily/2026-10-23.html` **早报 3/5**（自包含，22,591 字符 / 29,515 B，标签平衡校验通过）+ "
    "`daily/index.html`（倒序新增 1 行 + footer 前插）+ PDF **3/3**；"
    "台账 4,452 行不变（收录 **239** / 候选 3,706 / RSS 507）、`papers.jsonl` **239**；口径 `ARXIV_API.md` §9.107"
)

NEXT = (
    "下一步:       ① **P0 第 5 批 · 第 6 轮 = 本地 2026-10-23 18:00（PM「晚 2」轮 · 当日收口）**："
    "复验批次（**预期刷新到 `2026-10-22`**，周四 20:00 ET 公告届时已过）→ 补 2 篇「科普」收口 **5/5** → "
    "追加 `## 晚报变更说明（AM → PM）`（说明早报 3 篇批次归属 `2026-10-21` 与是否被替换）→ 分镜 `video/SCENES/10_23.html` + "
    "日报邮件 + 心跳 + `git pull --rebase --autostash` / commit / push；② 若 PM 仍无新批，沿用 §9.105 先例**不放宽窗口**、如实记 `kept 0`。"
)

NEW = (
    "本轮新增:      **0 条新采集（收录 0 + 候选 0；台账行数不变）**（**本地 2026-10-23 06:00 时窗 · P0「早 3」轮**；"
    "`--fetch`（72h）**15/15 ok**（全部 `attempts=1`）、**`kept 0` / `dropped 600`**；批次仍 `2026-10-21`、"
    "`totalResults` 636926 → **636928**（+2 元数据变动）；HF FAIL、RSS 221/超时/超时 如实记录）"
    "→ **收录 3**（`2610.29352` 长上下文续训规模律 / `2610.29171` TrainBridge / `2610.29870` PAUSE，"
    "均取自上一轮 PM 候选池；3 行「候选」→「收录」，行数不变）"
)

LASTWIN = (
    "- **上次采集窗口**：`2026-10-21`（**第一百零七轮 · P0 第 5 批第 5 轮「早 3」轮 · 本地 2026-10-23 06:00 时窗**；"
    "**公告批次未刷新**（`totalResults` 636926 → **636928**（+2 元数据变动）、最新样本 `published=2026-10-21T17:59:14Z` 与 r106 PM 相同）；"
    "`--fetch`（72h，`generated=2026-10-22T22:03:19Z`）**15/15 ok**（全部 `attempts=1`）、**`kept 0` / `dropped 600`**（整批已在 SEEN）；"
    "早报 3 篇取自上一轮候选池）"
)

TOTAL = (
    "- **累计收录**：`239` 篇（另候选 **3706** 篇，另 **RSS 补充候选 507**；仅存 `SEEN.md` 防重；"
    "**第一百零七轮：收录 3 / 候选 0**（4,452 行不变）；**第一百零六轮：收录 2 / 候选 156**（4,294 → 4,452）；"
    "**第一百零五轮：收录 3 / 候选 0**（行数不变 4,294）；**第一百零四轮：收录 2 / 候选 187**（4,105 → 4,294）；"
    "**第一百零三轮：收录 3 / 候选 0**（行数不变 4,105））"
)

FLOW = (
    "- **2026-10-23（本地 06:00 时窗）** —— **第一百零七轮（P0 第 5 批第 5 轮「早 3」· 新一日 AM）→ 公告批次未刷新（仍 `2026-10-21`）"
    "+ `kept 0` 因整批已入 SEEN + 早报 3 篇「借鉴」取自上一轮候选池**：R1′ arXiv ✅ `totalResults=636928`（+2 元数据变动）/ "
    "HF ❌ `Errno 101` / RSS cs.CL 221 · cs.CV·cs.LG 超时（仅发现）；72h `--fetch` **15/15 ok**（全 `attempts=1`）、"
    "**`kept 0` / `dropped 600`**；`id_list` **8/8** 复核 → 入账 `2610.29352` / `2610.29171` / `2610.29870`；"
    "PDF **3/3**（32/14/21 页，一次通过）；台账 **4,452 行不变**（收录 **239** / 候选 3,706 / RSS 507）、`papers.jsonl` **239**；"
    "交付 `daily/2026-10-23.html`（早报 3/5）+ `daily/index.html`；口径 §9.107。"
)

# 1) 已完成：前插本轮
for i, ln in enumerate(lines):
    if ln.startswith("已完成:"):
        assert "[[第一百零六轮" in ln, ln[:60]
        lines[i] = ln.replace("已完成:       [[第一百零六轮", "已完成:       [" + DONE107 + "；[[第一百零六轮", 1)
        break
else:
    raise SystemExit("no 已完成 line")

# 2) 当前动作 / 下一步 / 本轮新增
repl = {"当前动作:": CUR, "下一步:": NEXT, "本轮新增:": NEW}
seen = set()
for i, ln in enumerate(lines):
    for k, v in repl.items():
        if ln.startswith(k):
            lines[i] = v
            seen.add(k)
assert seen == set(repl), seen

# 3) 状态头：上次采集窗口 / 累计收录
seen = set()
for i, ln in enumerate(lines):
    if ln.startswith("- **上次采集窗口**"):
        lines[i] = LASTWIN
        seen.add("win")
    elif ln.startswith("- **累计收录**"):
        lines[i] = TOTAL
        seen.add("total")
assert seen == {"win", "total"}, seen

# 4) 流水：插在标题下方
for i, ln in enumerate(lines):
    if ln.startswith("## 2. 流水"):
        lines.insert(i + 2, FLOW)
        break
else:
    raise SystemExit("no 流水 header")

P.write_text("\n".join(lines), encoding="utf-8")
print("ok; lines =", len(lines))

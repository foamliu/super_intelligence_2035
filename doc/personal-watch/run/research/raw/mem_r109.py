#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百零九轮：更新 MEMORY_RESEARCH.md 快照 + 流水，并把 r108 原文滚动归档。"""
from pathlib import Path

P = Path("/home/liuyang/super_intelligence_2035/doc/personal-watch/run/MEMORY_RESEARCH.md")
ARCH = Path("/home/liuyang/super_intelligence_2035/doc/personal-watch/run/daily-memories-research/2026-10-23.md")

DONE = """已完成:       [[第一百零九轮（**本地 10-24 06:00 · P0 第 5 批第 7 轮「早 3」轮 · 新一日 AM 轮**）**公告批次未刷新**（仍 `2026-10-22`；`totalResults=637451` **与 r108 PM 完全相同**、最新样本 `published=2026-10-22T17:59:53Z`（`2610.31671`，cs.CV）；周五 20:00 ET 批未索引 / 周末不公告）：`--fetch --seen`（72h，`generated=2026-10-23T22:08:15Z`）**15/15 ok（全部 attempts=1）**、**`kept 0` / `dropped 600`**（成因=整批已在 r108 PM 入账 SEEN，**非无数据/非窗口越界/非单查询 FAIL**；未放宽窗口）；R1′ arXiv ✅ / HF ❌ `Errno 101` / RSS cs.CL **183** · cs.CV **192** · cs.LG 超时（仅作发现）；🔧 **DNS 边缘故障已兜底**：`export.arxiv.org`→`146.75.115.42` **12s 超时**、同域 `151.101.67.42` <0.8s → 新增 `raw/run_arxiv_r109.py`（仅进程内覆盖 `getaddrinfo`，TLS/SNI 不变、**工具代码未改**）；早报 3 篇「借鉴」取自上一轮 158 条候选池 + `id_list` 权威复核（两批 6+7 → 去重 **11 唯一全返回**）：`2610.30042` **HGM-Dual**（谱系感知上下文 + 错误条件化双路子代；case accuracy 相对最强基线 **+14.45%**、评测预算 **2×–4× 更少**；Samsung Research America）/ `2610.30132` **LongZero**（零数据长上下文 RL：自写「问题+答案+证据」再展开成长多文档上下文，多跳推理 + 多轮检索合练、GRPO；2 LLM / 5 基准优于外部语料合成基线；清华）/ `2610.29013` **Target Regeneration Shrinks the Gains of Draft-Training Objectives**（投机解码**评测口径**：target 重写回答后蒸馏增益收缩、门控几乎归零；对数据顺序/位置权重/验证器/温度/初始化/学习率/监督长度稳健；结论=在「target 重生成基线」上跨长度测；高丽大学 + 延世大学未来校区）→ 交付 `research/daily/2026-10-24.html`（早报 **3/5**：hero + 取数说明 + 3 卡片 + 附录 A/B/C/D + footer；**31,190 B**、`div` 71/71 · `table` 3/3 · `tr` 32/32 · `td` 182/182 配平、零 `<script>`）+ `daily/index.html`（新增 2026-10-24 行）+ PDF **3/3 通过**（16 / 17 / 19 页；511,421 / 574,366 / 543,617 B；均 `attempt=1`）+ **日报邮件 06:13:06 ✅ SENT OK**（3 附件 / 1.55 MB，未分包）；台账 **4,612 行不变**（3 行「候选」→「收录」）→ 收录 **244** / 候选 3,861 / RSS 507、`papers.jsonl` **241 → 244**；口径 `ARXIV_API.md` §9.109]；[[第一百零八轮（**本地 10-23 18:00 · 「晚 2」轮 · 当日收口**）批次刷新 `2026-10-21`→`2026-10-22`、`kept 160`、收录 `2610.31651` BrickWright（TOP-1）+ `2610.30769` 羊群效应、日报收口 5/5 + 分镜 `10_23` + 邮件分包 2 封 → **原文已归档** `daily-memories-research/2026-10-23.md`「归档 · MEMORY 滚动（2026-10-24）」]]"""

CUR = """当前动作:     ✅ **第一百零九轮（P0 第 5 批第 7 轮 · 本地 2026-10-24 06:00 时窗 · 「早 3」轮 · 新一日 AM）**：公告批次**未刷新**（`2026-10-22`、`totalResults=637451` 与 r108 PM 相同）⇒ `--fetch --seen` **15/15 ok（全部 `attempts=1`）**、**`kept 0` / `dropped 600`**（如实记录：整批已入 SEEN）；3 篇「借鉴」取自上一轮 158 条候选池 + `id_list` **11 唯一全返回**；交付 `daily/2026-10-24.html`（3/5）+ `daily/index.html` + PDF 3/3（16/17/19 页）+ 日报邮件 `SENT OK 06:13:06`（3 附件 / 1.55 MB）；台账 4,612 行不变（收录 **244**）、`papers.jsonl` **244**；口径 `ARXIV_API.md` §9.109"""

NEXT = """下一步:       ① **P0 第 5 批 · 第 8 轮 = 本地 2026-10-24 18:00（PM「晚 2」轮 · 当日收口）**：复验批次（**预期刷新到 `2026-10-23`**，周五 20:00 ET 公告届时已过）→ 若刷新则 2 篇「科普」**直接取自新批**（否则沿用 §9.100/§9.103/§9.105 先例**不放宽窗口**、如实记 `kept 0`），补 PDF 2 篇 → `daily/2026-10-24.html` 收口 **5/5**（+ 附录 A′/B′/C′/D′ + `## 晚报变更说明（AM → PM）`，**早报 3 篇不回改**）+ 选 **TOP-1** 出 `video/SCENES/10_24.html`（5 镜 · 120s · 口播 350–450 字）+ `SCENES/index.html`；② 日报邮件：当日 5 篇 PDF 若 >20MB 则**分包**（沿用 r108 先例）；③ `git pull --rebase --autostash` → commit → push 照常；④ 记忆若再超 32KB，继续按 §3 滚动归档"""

NEW = """本轮新增:      **0 条新采集（收录 3 / 候选 0；台账 4,612 行不变）**（本地 2026-10-24 06:00 时窗 · 「早 3」轮；`--fetch --seen`（72h）**15/15 ok**、**`kept 0` / `dropped 600`**；3 篇取自上一轮候选池、`id_list` 11 唯一全返回；RSS cs.CL 183 / cs.CV 192 / cs.LG 超时；HF `Errno 101` FAIL；**工具链**：DNS 边缘 `146.75.115.42` 不可达 → `raw/run_arxiv_r109.py` 运行期覆盖到 `151.101.67.42`）"""

ENTRY = """- **2026-10-24（本地 06:00 时窗）** —— **第一百零九轮（P0 第 5 批第 7 轮「早 3」· 新一日 AM）→ 公告批次未刷新（仍 `2026-10-22`，`totalResults=637451` 与 r108 PM 相同）+ `kept 0` 因整批已入 SEEN + 早报 3 篇取自上一轮 158 条候选池**：R1′ arXiv ✅ / HF ❌ `Errno 101` / RSS cs.CL 183 · cs.CV 192 · cs.LG 超时（仅发现）；🔧 **DNS 边缘故障**：`export.arxiv.org`→`146.75.115.42` 12s 超时、同域 `151.101.67.42` <0.8s ⇒ 新增 `raw/run_arxiv_r109.py`（进程内覆盖 `getaddrinfo`、TLS/SNI 不变、工具代码未改；首跑 `--fetch` 卡死 → 方括号防自杀 `pkill -f` 清场后成功）；`id_list` 两批 6+7 → **11 唯一全返回** → 收录 `2610.30042` **HGM-Dual**（谱系感知上下文 + 错误条件化双路子代；**+14.45%** case accuracy、评测预算 **2×–4× 更少**）/ `2610.30132` **LongZero**（零数据长上下文 RL：自写「问题+答案+证据」再展开 ↔ 多跳推理 + 多轮检索，GRPO；2 LLM / 5 基准）/ `2610.29013` **Target Regeneration**（投机解码评测口径：target 重写后蒸馏增益收缩、门控几乎归零）；交付 `daily/2026-10-24.html`（**3/5**，31,190 B，标签全配平）+ `daily/index.html` + PDF **3/3**（16/17/19 页）+ 邮件 **`SENT OK 06:13:06`**（3 附件 / 1.55 MB）；台账 4,612 行不变（收录 244 / 候选 3,861 / RSS 507）、`papers.jsonl` **244**；口径 `ARXIV_API.md` §9.109。⏭️ **下轮（18:00 PM）**：补 2 篇「科普」收口 5/5 + `video/SCENES/10_24.html`（TOP-1）+ 当日邮件（>20MB 则分包）。"""


def main():
    lines = P.read_text(encoding="utf-8").split("\n")
    old = lines[13:17]
    assert old[0].startswith("已完成:"), old[0][:20]
    assert old[1].startswith("当前动作:"), old[1][:20]
    assert old[2].startswith("下一步:"), old[2][:20]
    assert old[3].startswith("本轮新增:"), old[3][:20]

    hdr = "## 归档 · MEMORY 滚动（2026-10-24 第一百零九轮唤醒时执行）"
    s = ARCH.read_text(encoding="utf-8")
    if hdr not in s:
        s = s.rstrip("\n") + "\n\n" + hdr + "\n\n```\n" + "\n".join(old) + "\n```\n"
        ARCH.write_text(s, encoding="utf-8")
        print("archived to", ARCH.name, "bytes added", len("\n".join(old)))

    lines[13:17] = [DONE, CUR, NEXT, NEW]
    idx = max(i for i, l in enumerate(lines) if l.startswith("## 2. 流水"))
    lines.insert(idx + 1, ENTRY)
    out = "\n".join(lines)
    assert out.count("WAITING: 1") == 1
    P.write_text(out, encoding="utf-8")
    print("MEMORY bytes", len(out.encode()), "lines", out.count("\n") + 1)


if __name__ == "__main__":
    main()

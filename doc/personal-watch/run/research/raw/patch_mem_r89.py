#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第八十九轮：就地修订 MEMORY_RESEARCH.md 的 当前动作 / 下一步 / 本轮新增 / ERROR_COUNT。"""
import io, sys

P = "MEMORY_RESEARCH.md"
s = io.open(P, encoding="utf-8").read()

CUR = (
"当前动作:     第八十九轮（P0 第 4 批第 12 轮 · **本地 2026-10-12 18:00 时窗 · 「晚 2」轮 · 当日收口 + 第 5 批 P0**）："
"`--probe`（R1′，`generated=2026-10-12T10:00:58Z`，**无重试**）+ `--fetch`（`generated=2026-10-12T10:00:57Z`，"
"`window_mode=weekend_batch` 120h，**15/15 ok attempts=1 无重试**，**kept 169 / dropped 410**）—— "
"✅ **公告批次已刷新 `2026-10-08` → `2026-10-09`**（主源 `totalResults 630048 → 630616`（+568）、最新样本 "
"`published=2026-10-09T17:59:56Z`）—— ⚠️ **与 AM 第八十八轮「PM 大概率仍无新批」预期相反（如实记录）**；"
"R1′ arXiv ✅ / HF ❌（`Network is unreachable`）/ **RSS cs.CL/CV/LG = 172 / 0 / 413**（cs.CV 空 feed，如实记录）；"
"**PM 有真实新批** → 晚报 2 篇「科普」**取自本 PM 轮新发现** + **单条权威复核**"
"（`id_list=2610.13948,2610.13860,2610.13925,2610.13940,2610.12571` → **5/5**；均 `HTTP 200` + "
"`application/atom+xml; charset=utf-8` + 有 `published`/`comment`；证据 `raw/2026-10-12-idlist-shortlist-r89.{xml,headers}`）→ "
"**产出 P0 交付①** `research/daily/2026-10-12.html`（**自包含单文件**，收口 **晚报 5/5** = 早 3「借鉴」+ 晚 2「科普」："
"**`2610.13948` Can Language Models Play the Wikipedia Game?**（维基百科游戏当信息检索任务：5 语言维基页面图 + 5 学术引文图"
"（OpenAlex + 抓取），对比人类 / TF-IDF / 句向量 / LLM → **无一模型显著超人类**、排名随语言 / 主题漂移；"
"`comment` 64 pages/17 figs/10 tabs → cs.AI 次 cs.IR）/ **`2610.13860` Make It Flow: Animating Water in 3D Gaussian "
"Splatting Scenes**（静态 3DGS 水动起来：2D 光流 → 一致 3D 欧拉运动场 → cinemagraph 启发变形高斯，无缝循环 + 实时自由视角；"
"`comment` 含 youtu.be/qf04D73kgrc → cs.CV 次 cs.GR）；页头「早报 3/5」→「**晚报 5/5**」+ PM 轮取数说明 + 附录 A′（PM 轮 I→V）+ "
"附录 C 更新 + 新增 `## 晚报变更说明（AM → PM）`（锚点 `#pm-change`））+ 更新 `research/daily/index.html`"
"（2026-10-12 行 → **晚报 5/5**）；**产出 P0 交付②（第 5 批）** `research/video/SCENES/10_12.html` 分镜脚本"
"（**自包含单文件**，TOP-1 = **`2610.13948`**：固定五段 9 镜，口播 **≈426 字**，含英文原题 + abs 链接 + 免责 + 合规红线自检）+ "
"`research/video/SCENES/index.html`（新增 10_12 行）；落盘 日报 `research/2026-10-12.md`（第八十九轮）/ "
"INDEX(🗓89 + 累计 191/3029) / SEEN(**3,051 → 3,220 行**，**收录 +2 / 候选 +167** → 收录 **191 / 候选 3029**) / "
"papers.jsonl(**+2 → 191 行**，脚本 `raw/update_r89.py`) / ARXIV_API(**§9.91**) / 心跳")

NXT = (
"下一步:       ① **P0 第 4 批**：下轮 = 本地 **2026-10-13 06:00**（新一日「早 3」轮）→ ① 复验批次"
"（`2026-10-09` 批已被 PM 消费；AM 轮预计见 `2026-10-10/12` 批陆续公告）；② 若刷新则走标准 `--fetch` 增量取数，"
"否则继续走 **RSS 发现 + API `id_list` 复核**；③ 日报进度回到 **3/5**（新一日 AM）；④ 常态采集按 SOP 增量"
"（先读 SEEN.md 去重、定窗口）；⑤ **第 5 批 P0**：从当日 5 篇挑 TOP-1 → `research/video/SCENES/10_13.html` 分镜脚本；"
"⑥ 可考虑按 `RESEARCH_MAIL_SPEC.md` 起草 ≤3 封作者邮件（**前 3 封需运维确认后发送**）；⑦ **视频 V3（生成）待用户确认运行机工具链后再动**；"
"⑧ **邮件职能待用户批准后才可启动**（现仅登记）；⑨ ✅ `MEMORY_RESEARCH.md` 保持 **≤32KB**（按 §3 滚动）；"
"⑩ ⚠️ **采集命令统一在 `run/` 目录执行**：`python3 research/arxiv_fetch.py --fetch --seen research/SEEN.md`")

NEW = (
"本轮新增:     169 条采集（**本地 2026-10-12 18:00 时窗 · P0「晚 2」轮 · 周一**；"
"**PM 公告批次已刷新 `2026-10-08` → `2026-10-09`**，API 关键词 `kept 169 / dropped 410`（15/15 ok attempts=1），"
"RSS cs.CL/CV/LG = 172/0/413）→ **收录 2（晚报 2 篇「科普」）+ 候选 167**；晚报 2 篇**取自本 PM 轮新批**"
"（`2610.13948` Wikipedia Game / `2610.13860` Make It Flow），经**单条权威复核（`id_list` 5/5）**后由 SEEN「候选」→「收录」"
"（**收录 189 → 191**）；证据 `raw/2026-10-12-{probe-r89.log,fetch-r89-seen.json}` + "
"`raw/2026-10-12-idlist-shortlist-r89.{xml,headers}` + `raw/2026-10-12-candlist-r89.txt`")

def replace_block(text, start_marker, end_marker, new_block):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[:i] + new_block + text[j:]

s = replace_block(s, "当前动作:", "\n下一步:", CUR)
s = replace_block(s, "下一步:", "\n本轮新增:", NXT)
s = replace_block(s, "本轮新增:", "\n阻塞:", NEW)

# ERROR_COUNT 行尾补记
k = s.index("ERROR_COUNT:")
eol = s.index("\n", k)
add = "；**第八十九轮 `--probe`/`--fetch` 均 `attempts=1` 无重试**（PM 公告批次刷新；cs.CV 空 feed 属正常）"
s = s[:eol] + add + s[eol:]

io.open(P, "w", encoding="utf-8").write(s)
print("OK; bytes=", len(s.encode("utf-8")))

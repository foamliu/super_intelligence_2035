# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**对齐 BaiZe**：`SLEEP_BUSY=60` / `SLEEP_WAIT=1800`）：`0` = 有近期待办（短睡 **60s** 续跑）；`1` = 无近期待办（常态，睡 **30min** 省 token）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```
已完成:       R1 打通 arXiv API（HTTPS/Atom → research/ARXIV_API.md）；R2 固化检索策略（queries.json）；R3/R4 首轮采集（抓取 214 → 收录 34 + 候选 180）；R1′ 取源复验；R2′ published-first + 周末自动放宽；第二~十四轮增量（15/15 ok，第三~十四轮均 0 新增）；**运维第 2 批**：`arxiv_fetch.py` 增 `comment`/`journal_ref` → ≤30d 全量重扫（候选池 1118）→ 新建 `top_k.py`（rel/q 双维 + HN 热度）→ `TOP_K.md`/`TOP_K.jsonl`（TOP-20）+ `test_top_k.py` 20/20；**运维第 3 批**：`top_k.py` 增 `--takeaways-json`（人工 `takeaway`/`action` 注入，不打分）→ `TOP_K_takeaways.json`（20 条）→ 相关面放宽「存储/芯片」重排（**#1 DeepSeek-V4.1-Flash**）→ `TAKEAWAYS.md`（≤5 条）→ `test_top_k.py` **25/25**；**视频线** `video/SHORTLIST.md`（17 条）+ `video/scripts/`（3 份口播稿）；**第十五轮**（**UTC 跨入 2026-10-05 周一**，**新建当日日报**）**工作日公告恢复 → +171 新增**（15/15 ok，精选收录 30；第 3 批 A/B **已交付未变**）；**第十六轮**（**UTC 周一 05:2x · 同批去重复核**）**0 新增**（15/15 ok）；**第十七轮**（**UTC 周一 05:5x · 同批去重复核**）**0 新增**（15/15 ok）；**第十八轮**（**UTC 周一 06:3x · 同批去重复核**）**0 新增**（15/15 ok）；**第十九轮**（**UTC 周一 07:0x · 同批去重复核**）**0 新增**（**14/15 ok / 1 FAIL（429）**，⚠️ `export.arxiv.org` 间歇性不可达但脚本重试成功）；**第二十轮**（**UTC 周一 07:5x · 同批去重复核**）**0 新增**（**15/15 ok 无重试**，第 19 轮 FAIL **已恢复**）；**第二十一轮**（**UTC 周一 08:2x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十二轮**（**UTC 周一 09:0x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十三轮**（**UTC 周一 09:3x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十四轮**（**UTC 周一 10:1x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十五轮**（**UTC 周一 10:4x · 同批去重复核**）**0 新增**（15/15 ok 无重试）；**第二十六轮**（**UTC 周一 11:1x · 同批去重复核**）**0 新增**（15/15 ok 无重试；本轮唤醒时达 ~32KB → 按 §5 将**第十二~十四轮**流水滚动归档至 `daily-memories-research/2026-10-04.md`）；**第二十七轮**（**UTC 周一 11:4x · 同批去重复核**）**0 新增**（15/15 ok 无重试 attempts=1）；**第二十八轮**（**UTC 周一 12:2x · 同批去重复核**）**0 新增**（15/15 ok 无重试 attempts=1）；**第二十九轮**（**UTC 周一 12:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**）；**第三十轮**（**UTC 周一 13:3x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；⚠️ **`window_mode` 首次自动由 `weekend_batch`(120h) 切 `daily`(72h)**——周一 UTC ≥13:00 触发，结论不变）；**第三十一轮**（**UTC 周一 14:1x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十二轮**（**UTC 周一 14:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)）；**第三十三~五十轮**（**UTC 周一 15:3x ~ 周二 01:1x · 同批去重复核**，除第五十一轮外均 **0 新增**，`window_mode=daily`(72h)）**原文已按 §5 滚动归档** → `daily-memories-research/2026-10-05.md`（「归档 · MEMORY 滚动（2026-10-06 第六十轮唤醒时执行）」）；**第五十一轮**（**UTC 周二 01:4x · 新公告批次落地**）**新增 93（精选收录 30）**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)；**主源 `published` 由 `2026-10-02T17:59:14Z` 刷新为 `2026-10-03T20:15:17Z`**、`totalResults` 由 `626530` 增至 `626945`（+415）= **新批次 `2026-10-03` 落地**；⚠️ 首次 `--probe` 网络停滞超时→后台重跑成功；按 §5 滚动**第二十一/二十二~第三十轮**（5 条）至 `daily-memories-research/2026-10-05.md`）；**第五十二轮**（**UTC 周二 02:2x · 批次渐进索引**）**新增 7（精选收录 6 + 候选 1）**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)；主源样本 `published` 仍 `2026-10-03T20:15:17Z`、`totalResults` 仍 `626945`，但 7 篇 `published` 落在 `2026-10-03T20:38 ~ 2026-10-05T05:49` 且未在 SEEN → 判定为**上一公告批次的渐进索引**、非重复；⚠️ 首次 `--probe` 网络停滞超时→后台重跑成功；按 §5 滚动**第四十七轮**→`daily-memories-research/2026-10-05.md`、**第四十八轮**→`daily-memories-research/2026-10-06.md`）；**第五十三轮**（**UTC 周二 02:4x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)；批次仍 `2026-10-03`、`totalResults` 仍 `626945`，渐进索引已收尽；⚠️ 首次 `--probe` 网络停滞超时→后台重跑成功）；**第五十四轮**（**UTC 周二 03:1x · 新公告批次落地**）**新增 215（精选收录 34 + 候选 181）**（**15/15 ok attempts=1 无重试**，`window_mode=daily`(72h)；**主源 `published` 由 `2026-10-03T20:15:17Z` 刷新为 `2026-10-05T17:59:54Z`**、`totalResults` 由 `626945` 增至 `627806`（+861）；按 §5 滚动**第五十一 / 第五十二轮**→`daily-memories-research/2026-10-06.md`）；**第五十五轮**（**UTC 周二 03:5x · 同批去重复核**）**0 新增**（**15/15 ok**（其中 1 查询 `mm-csmm` 触发 HTTP 429 2 次 → `backoff 20s` 重试后成功 `attempts=3`）；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四轮一致；`--probe` 无重试）；**第五十六轮**（**UTC 周二 10:0x · 同批去重复核 · loop 停摆后补跑**）**0 新增**（**15/15 ok attempts=1 无重试**；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四/五十五轮一致；`--probe` 无端点故障）；**第五十七轮**（**UTC 周二 10:4x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六轮一致；R1′ arXiv ✅（⚠️ 一次 `Read timed out`，脚本已重试成功））；**第五十八轮**（**UTC 周二 11:5x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十七轮一致）；**第五十九轮**（**UTC 周二 12:3x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十八轮一致）；**第六十轮**（**UTC 周二 13:1x · 同批去重复核**）**0 新增**（**15/15 ok attempts=1 无重试**；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十九轮一致；⚠️ `--probe` 本地耗时 ≈8min，前两次 150s/130s 超时截断、450s 余量后台跑成功，**非端点故障**）
当前动作:     第六十轮常态增量（**本轮实时取数 · UTC 2026-10-06 周二 13:1x**）：`--probe`(R1′) + `--fetch` 增量（**kept 0 / dropped 600 = 470 already in SEEN + 130 stale**，**15/15 ok**（**均 `attempts=1`，无重试**）；**主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~五十九轮一致** = **公告批次未刷新**；`window_mode=daily`(72h，第三十轮起的自动回落，非人工覆盖)；R1′ arXiv ✅ / HF ❌ / RSS 有内容；⚠️ `--probe` 本地耗时 ≈8min，前两次 150s/130s 超时截断、450s 余量后台跑成功）→ **0 新增** → `research/2026-10-06.md` 追加「第六十轮（0 新增）」+ INDEX/SEEN(逐轮备注)/papers.jsonl(不变)/ARXIV_API(§9.62) + 本记忆 + 心跳（第六十轮）；并复核第 3 批 A/B（无新增 → 不重跑）
下一步:       ① 常态采集按 SOP 增量（先读 SEEN.md 去重、定窗口；**公告批次现为 `2026-10-05`、渐进索引已基本收尽，下轮工作日公告（`2026-10-06` 提交批）预计 UTC `2026-10-07` 前后刷新**）；② TOP-K 可按需重跑（`--w1/--w2/--top/--takeaways-json` 可调；新增批次落在窗口内、可重跑，**按节律留待 supervisor 指派**）；③ **视频 V3（生成）待用户确认运行机工具链后再动**；④ **邮件职能待用户批准后才可启动**（现仅登记）；⑤ ✅ `MEMORY_RESEARCH.md` 保持 **≤32KB**（按 §5 滚动）
本轮新增:     0 篇采集（**UTC 为 `2026-10-06` 周二，同批去重复核**；主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~五十九轮一致 → **公告批次未刷新**，`2026-10-05` 批次的渐进索引已收尽）；R1′ 复验（arXiv ✅ / HF ❌ / RSS 有内容）+ 第六十轮 **15/15 ok**（**均 `attempts=1` 无重试**，kept 0 / dropped 600 = 470 already in SEEN + 130 stale）；`window_mode=daily`(72h)
阻塞:         无（HF Daily Papers 本机不可达 → 社区热度**改用 HN Algolia 替代并注明**，不伪造 hf_daily；**视频 V3 待工具链确认**）
ERROR_COUNT:  1（历史：第八轮唤醒 **cline 超时中断** `run timed out after 1500s`，已补记落盘；第十九轮 1 个查询 `llm-long-context` **HTTP 429 重试耗尽 FAIL**（脚本级已如实记录、**非唤醒级错误**，**第二十轮已恢复**，故 ERROR_COUNT 仍为 1；**第二十三~四十三轮 15/15 ok 无重试**）；**第三十三轮首次 `--probe` 遇 `requests` 对 arXiv 间歇性网络停滞（非端点故障，重试成功），未升为唤醒级错误**；**第三十四~五十轮 `--probe`/`--fetch` 均无重试**；**第五十一轮 `--probe` 首次因 `requests` 对 arXiv 网络停滞超时（工具级 30s）→ 改后台重跑成功（非唤醒级错误），`--fetch` 无重试 attempts=1**；**第五十二/五十三轮 `--probe` 同类网络停滞超时→后台重跑成功（非唤醒级错误），`--fetch` 均无重试 attempts=1**；**第五十四轮 `--probe`/`--fetch` 均无重试 attempts=1**；**第五十五轮 `--probe` 无重试，`--fetch` 中 1 查询 `mm-csmm` 触发 HTTP 429 2 次 → `backoff 20s` 重试后成功 `attempts=3`（脚本级已处理、非唤醒级错误）**；**第五十六轮 `--probe` 无端点故障（本地耗时 ≈5min）、`--fetch` 均 `attempts=1` 无重试**；**本轮唤醒前 loop 停摆 ~5.5h（第五十五轮 03:5x → 本轮 10:0x），非 agent 错误，已补跑**）；回归 test_arxiv_fetch 49/49 + test_top_k 25/25 PASS）
```

---

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（运维第 2 批登记）**：是否要**给论文作者发邮件**做学术交流/技术沟通？
  **A（本线）**：**已登记为未来职能，本批只登记、不实施**。启用**前提（须用户明确批准）**：① 发件邮箱/身份/署名；② 邮件模板；③ 频率上限；④ 每封是否需用户先审。
  **红线**：**未获批准，绝不自动发送任何邮件**。当前各线上均**无任何发信动作**。

- **Q（运维第 3 批 B 节 · 视频线）**：`V3`（把口播稿变成成片）什么时候能启动？需要用户/环境确认什么？
  **A（本线）**：**V1/V2 已交付**（选题表 + 3 份口播稿，纯文本）；**V3 会用到运行机可能没有的工具链**，故**本批不做**，先把**待确认清单**摆出来，获批后再动：
  ① **TTS / 配音**：用哪个引擎（系统 `espeak`？本机有无可用的中文 TTS？还是要用户自录口播）；② **文生图/画面**：运行机是否可访问图像生成服务（**HF 本机不可达**，需另定；否则退化为**纯自绘 SVG/图表**）；
  ③ **剪辑**：有无 `ffmpeg`；成片**>20MB 不入 git**（走外部目录 + 清单）；④ **栏目名**：本线**须自起**（避免与已有知名频道「两分钟论文」混淆）；
  ⑤ **发布**：B站/抖音账号、实名与平台规则在**用户侧**，**发布由用户本人执行**。
  **红线**：**不盗用论文原图、不夸大、不曲解**；未获确认**不擅自生成/发布成片**。

---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序；源 `TOP_K_notes.md` + **`TOP_K_takeaways.json`**）· **`research/TAKEAWAYS.md`**（第 3 批 A 节：≤5 条可借鉴结论）· **`research/video/SHORTLIST.md` + `research/video/scripts/<arXiv_ID>.md`**（第 3 批 B 节：视频线 V1/V2）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py`（含 `--takeaways-json`）+ `research/test_top_k.py`（25/25）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：对齐 BaiZe —— `WAITING=1`（常态）睡 **30min**；`WAITING=0`（有近期待办）短睡 **60s**
- **上次采集窗口**：`2026-10-06`（**第六十轮**；窗口 **≤72h**（`window_mode=**daily**`，⚠️ **第三十轮起**由 `weekend_batch`(120h) 自动回落）；实际批次 **`2026-10-05`（最近公告批次，未刷新）**；本轮 **0 新增**（**15/15 ok**，**均 `attempts=1` 无重试**；R1′ arXiv ✅ / HF ❌））
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`161` 篇（另候选 732 篇，仅存 `SEEN.md` 防重；**五十四轮**累计抓取 893 条 —— 第三~第十四轮新增均 **0**（周末未公告），**第十五轮 +171**，**第十六~五十轮 +0**（**周一公告尚未刷新到 API**，同批去重复核；第十九轮 1 查询 429 已如实记录、**第二十轮已恢复**；第三十三轮首次 `--probe` 网络停滞、重试成功；第三十四~五十轮 `--probe`/`--fetch` 均无重试），**第五十一轮 +93**（**新公告批次 `2026-10-03` 落地**），**第五十二轮 +7**（**批次渐进索引**：`published` 落在 `2026-10-03T20:38 ~ 2026-10-05T05:49`；`--probe` 首次网络停滞超时→后台重跑成功，`--fetch` 无重试），**第五十三轮 +0**（**同批去重复核**：批次仍 `2026-10-03`、`totalResults` 仍 `626945`，渐进索引已收尽；`--probe` 首次网络停滞超时→后台重跑成功，`--fetch` 无重试），**第五十四轮 +215**（**新公告批次 `2026-10-05` 落地**：主源 `published` 由 `2026-10-03T20:15:17Z` 刷新为 `2026-10-05T17:59:54Z`、`totalResults` 由 `626945` 增至 `627806`（+861）；精选收录 34 + 候选 181；`--probe`/`--fetch` 均无重试 attempts=1），**第五十五轮 +0**（**同批去重复核**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四轮一致；⚠️ `--fetch` 中 `mm-csmm` 触发 HTTP 429 2 次 → `backoff 20s` 重试后成功 `attempts=3`，`--probe` 无重试），**第五十六轮 +0**（**同批去重复核 · loop 停摆后补跑**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四/五十五轮一致；15/15 ok 均 attempts=1 无重试），**第五十七轮 +0**（**同批去重复核**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六轮一致；R1′ arXiv ✅（一次 `Read timed out`，脚本重试成功）、`--fetch` attempts=1 无重试），**第五十八轮 +0**（**同批去重复核**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十七轮一致；15/15 ok attempts=1 无重试），**第五十九轮 +0**（**同批去重复核**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十八轮一致；15/15 ok attempts=1 无重试），**第六十轮 +0**（**同批去重复核**：批次仍 `2026-10-05`、`totalResults` 仍 `627806`，与第五十四~五十九轮一致；15/15 ok attempts=1 无重试；⚠️ `--probe` 本地耗时 ≈8min，前两次 150s/130s 超时截断、450s 余量后台跑成功））

---

## 2. 流水（倒序，保留最近 ~20 条）
- **2026-10-06（UTC 周二）** —— **第六十轮（常态增量 · 同批去重复核）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-06T13:19:22.491630+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新样本 `published=2026-10-05T17:59:54Z`，`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=427/451/931`（工作日有内容）**。证据 → `research/raw/2026-10-06-probe-r60.json`（**无重试**；⚠️ 本地耗时 ≈8min，**前两次以 150s / 130s 超时被截断且无产出，改用 450s 余量后成功** —— RSS 端读取慢属正常、**非端点故障**）。
  - **增量采集**：`--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T13:11:49.588566+00:00`）→ **15/15 `ok`**（**均 `attempts=1`，无重试**），**kept 0 / dropped 600 = 470 already in SEEN + 130 stale >72h** → **0 新增**（**主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~五十九轮一致 → 公告批次未刷新**，渐进索引已收尽）。证据 → `research/raw/2026-10-06-fetch-r60.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报 `research/2026-10-06.md` 追加「第六十轮（0 新增）」；`INDEX.md`（累计仍 **收录 161 / 候选 732 / 累计抓取 893** + 🗓 第六十轮行）；`SEEN.md`（追加第六十轮备注）；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.62**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
  - **心跳**：`daily-memories-research/2026-10-06.md` 追加 **第六十轮** 心跳行。

- **2026-10-06（UTC 周二）** —— **第五十九轮（常态增量 · 同批去重复核）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-06T12:31:40.739748+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新样本 `published=2026-10-05T17:59:54Z`，`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=427/451/931`（工作日有内容）**。证据 → `research/raw/2026-10-06-probe-r59.json`（无重试；本地耗时 ≈5min，RSS 端读取慢）。
  - **增量采集**：`--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T12:37:10.377273+00:00`）→ **15/15 `ok`**（**均 `attempts=1`，无重试**），**kept 0 / dropped 600 = 470 already in SEEN + 130 stale >72h** → **0 新增**（**主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四~五十八轮一致 → 公告批次未刷新**，渐进索引已收尽）。证据 → `research/raw/2026-10-06-fetch-r59.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **落盘**：日报 `research/2026-10-06.md` 追加「第五十九轮（0 新增）」；`INDEX.md`（累计仍 **收录 161 / 候选 732 / 累计抓取 893** + 🗓 第五十九轮行）；`SEEN.md`（追加第五十九轮备注）；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.61**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
  - **心跳**：`daily-memories-research/2026-10-06.md` 追加 **第五十九轮** 心跳行。
  - **MEMORY 滚动（维护）**：本轮唤醒时 `MEMORY_RESEARCH.md` 达 ~32.6KB（超 32KB）→ 按 §5 将**第四十七~三十六轮指针 + 10-03~10-04 归档索引块**原文滚动至 `daily-memories-research/2026-10-05.md`（「归档 · MEMORY 滚动（2026-10-06 第五十九轮唤醒时执行）」），并压缩为 1 行指针；滚动后 ~29KB（≤32KB）。**归档不改变任何结论**。

- **2026-10-06（UTC 周二）** —— **第五十八轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 470 already in SEEN + 130 stale >72h；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，渐进索引已收尽；`window_mode=daily`(72h)；`ARXIV_API.md` §9.60）。


- **2026-10-06（UTC 周二）** —— **第五十七轮（常态增量 · 同批去重复核）→ 0 新增**。
  - **R1′（取源复验）**：`--probe --config research/queries.json`（`generated=2026-10-06T10:42:13.953566+00:00`）→ **arXiv ✅ `200`+`atom+xml`（最新样本 `published=2026-10-05T17:59:54Z`，`totalResults=627806`，样本 `2610.06852 / 2610.06851 / 2610.06850`；⚠️ `meta.error` 记一次 `Read timed out`，**脚本已重试成功**）** / **HF ❌ `Network is unreachable`** / **RSS cs.CL/CV/LG ✅ `items=427/451/931`（工作日有内容）**。证据 → `research/raw/2026-10-06-probe-r57.json`（本地耗时 ≈6min，RSS 端读取慢）。
  - **增量采集**：`--fetch --seen research/SEEN.md`（**`window_mode=daily`，窗口 72h**，`generated=2026-10-06T10:48:46.534774+00:00`）→ **15/15 `ok`**（**均 `attempts=1`，无重试**），**kept 0 / dropped 600 = 470 already in SEEN + 130 stale >72h** → **0 新增**（**主源 `published` 仍 `2026-10-05T17:59:54Z`、`totalResults` 仍 `627806`，与第五十四/五十五/五十六轮一致 → 公告批次未刷新**，`2026-10-05` 批次渐进索引已收尽）。证据 → `research/raw/2026-10-06-fetch-r57.json`。
  - **第 3 批 A/B 复核**：TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；**无新增 → 不重跑**（诚实标注）。
  - **心跳**：`daily-memories-research/2026-10-06.md` 顶部新增 **第五十七轮** 心跳行。
  - **落盘**：日报 `research/2026-10-06.md` 追加「第五十七轮（0 新增）」；`INDEX.md`（累计仍 **收录 161 / 候选 732 / 累计抓取 893** + 🗓 第五十七轮行）；`SEEN.md`（追加第五十七轮备注）；`papers.jsonl`（**不变**）；`ARXIV_API.md` 新增 **§9.59**。
  - **回归测试**：`research/test_arxiv_fetch.py` **49/49 PASS** · `research/test_top_k.py` **25/25 PASS**（均离线）；本轮无代码改动。
  - **下轮预期**：公告批次现为 `2026-10-05`（渐进索引已收尽）；下一次工作日公告（`2026-10-06` 提交批）预计在 **UTC `2026-10-07` 前后**刷新，届时按 SOP 增量采集。

- **2026-10-06（UTC 周二）** —— **第五十六轮（常态增量 · 同批去重复核 · loop 停摆后补跑）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十七轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 470 already in SEEN + 130 stale >72h；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，渐进索引已收尽；`window_mode=daily`(72h)；`ARXIV_API.md` §9.58；⚠️ 唤醒前 loop 停摆 ~5.5h，本轮补跑）。


- **2026-10-06（UTC 周二）** —— **第五十五轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十六轮唤醒时执行 · 续）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok（⚠️ 1 查询 `mm-csmm` 429 重试 2 次后 `attempts=3`）；kept 0 / dropped 600 = 465 already in SEEN + 135 stale >72h；批次仍 `2026-10-05`、`totalResults` 仍 `627806`，渐进索引基本收尽；`window_mode=daily`(72h)；`ARXIV_API.md` §9.57）。


- **2026-10-06（UTC 周二）** —— **第五十四轮（常态增量 · 新公告批次落地）→ 新增 215（精选收录 34）**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十六轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 215 / dropped 358，主源 `published` 由 `2026-10-03T20:15:17Z` 刷新为 `2026-10-05T17:59:54Z`、`totalResults` `626945`→`627806`（+861）；`window_mode=daily`(72h)；`ARXIV_API.md` §9.56）。


- **2026-10-06（UTC 周二）** —— **第五十三轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十五轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 430 already in SEEN + 170 stale >72h；批次仍 `2026-10-03`、`totalResults` 仍 `626945`，渐进索引已收尽；`window_mode=daily`(72h)；`ARXIV_API.md` §9.55）。


- **2026-10-06（UTC 周二）** —— **第五十二轮（常态增量 · 批次渐进索引）→ 新增 7（精选收录 6 + 候选 1）**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十四轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 7 / dropped 593，`published` 落在 `2026-10-03T20:38 ~ 2026-10-05T05:49`；`window_mode=daily`(72h)；`ARXIV_API.md` §9.54）。

- **2026-10-06（UTC 周二）** —— **第五十一轮（常态增量 · 新公告批次落地）→ 新增 93（精选收录 30）**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十四轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 93 / dropped 491，主源 `published` 由 `2026-10-02T17:59:14Z` 刷新为 `2026-10-03T20:15:17Z`、`totalResults` `626530`→`626945`（+415）；`window_mode=daily`(72h)；`ARXIV_API.md` §9.53）。


- **2026-10-06（UTC 周二）** —— **第五十轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十三轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.52）。

- **2026-10-06（UTC 周二）** —— **第四十九轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十三轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.51）。

- **2026-10-06（UTC 周二）** —— **第四十八轮（常态增量 · 同批去重复核）→ 0 新增**：详细条目已按 §5 滚动归档 → **`daily-memories-research/2026-10-06.md`**「归档 · MEMORY 滚动（2026-10-06 第五十二轮唤醒时执行）」（R1′ arXiv ✅ / HF ❌ / RSS 有内容；15/15 ok attempts=1 无重试；kept 0 / dropped 600 = 435 already in SEEN + 165 stale >72h；`window_mode=daily`(72h)；`ARXIV_API.md` §9.50）。

- **2026-10-03 ~ 10-05（UTC 周一及更早 · 第四十七轮及更早）** —— **详细条目已按 §5 滚动归档**：第四十七~三十六轮（10-05）与第十二~十四轮、第十一~八轮、第七轮及更早、运维第 2/3 批、建线首轮等 **原文**见 **`daily-memories-research/2026-10-05.md`**（「归档 · MEMORY 滚动（2026-10-06 第五十九轮唤醒时执行）」，含 10-05 各轮指针与 10-03~10-04 归档索引块）、**`daily-memories-research/2026-10-03.md`**、**`daily-memories-research/2026-10-04.md`**。各轮结论（收录/候选/`ARXIV_API.md` 小节号）见对应日日报。


---

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
